"""Multi-window stability analysis for position-wise Power 6/55 forecasts.

Uses expanding walk-forward predictions from backtest_positionwise_roi.py, then
compares them over non-overlapping chronological blocks, overlapping rolling
windows, and several trailing windows. No window refits or looks ahead: the
underlying per-draw forecasts were produced using only draws before each target.
"""
from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median
from typing import Any, Sequence

from .backtest_positionwise_roi import DEFAULT_DATA, DEFAULT_SEED, _summary, load_rows, run_backtest

OUTPUT_JSON = Path("artifacts/backtest_v2/positionwise_multiwindow_backtest.json")
OUTPUT_MD = Path("artifacts/backtest_v2/positionwise_multiwindow_backtest.md")
BASE_MODELS = (
    "PositionWiseBayesian",
    "PositionWiseExponentialDecay",
    "PositionWiseRecent",
    "PositionWiseEnsemble",
)
DEFAULT_TRAILING_SIZES = (100, 200, 300, 500, 800)


def _score_window(draws: Sequence[dict[str, Any]], model_names: Sequence[str]) -> dict[str, Any]:
    actual_results = [
        [int(value) for value in draw["actual_main"]] + [int(draw["special"])]
        for draw in draws
    ]
    return {
        name: _summary(
            name,
            actual_results,
            [[draw["forecasts"][name]] for draw in draws],
        )
        for name in model_names
    }


def _make_window(
    family: str,
    name: str,
    start: int,
    stop: int,
    draws: Sequence[dict[str, Any]],
    model_names: Sequence[str],
) -> dict[str, Any]:
    chunk = draws[start:stop]
    if not chunk:
        raise ValueError(f"Empty window: {family}/{name}")
    return {
        "family": family,
        "name": name,
        "start_index": start,
        "stop_index_exclusive": stop,
        "draws": len(chunk),
        "start_draw_id": chunk[0]["draw_id"],
        "end_draw_id": chunk[-1]["draw_id"],
        "start_date": chunk[0]["date"],
        "end_date": chunk[-1]["date"],
        "metrics": _score_window(chunk, model_names),
    }


def _strategy_stability(windows: Sequence[dict[str, Any]], model_names: Sequence[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for model_name in model_names:
        rois = [float(window["metrics"][model_name]["roi_pct"]) for window in windows]
        gains = [int(window["metrics"][model_name]["gain"]) for window in windows]
        random_wins = sum(
            float(window["metrics"][model_name]["roi_pct"])
            > float(window["metrics"]["RandomOneTicket"]["roi_pct"])
            for window in windows
        )
        result[model_name] = {
            "window_count": len(windows),
            "mean_roi_pct": mean(rois) if rois else 0.0,
            "median_roi_pct": median(rois) if rois else 0.0,
            "best_roi_pct": max(rois) if rois else 0.0,
            "worst_roi_pct": min(rois) if rois else 0.0,
            "profitable_windows": sum(roi > 0 for roi in rois),
            "windows_beating_random": random_wins,
            "mean_prize_gain_vnd_per_window": mean(gains) if gains else 0.0,
        }
    return result


def _mirror_stability(
    windows: Sequence[dict[str, Any]],
    base_models: Sequence[str] = BASE_MODELS,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for base in base_models:
        mirror = f"{base}_Mirror56Minus"
        deltas = [
            float(window["metrics"][mirror]["roi_pct"])
            - float(window["metrics"][base]["roi_pct"])
            for window in windows
        ]
        random_deltas = [
            float(window["metrics"][mirror]["roi_pct"])
            - float(window["metrics"]["RandomOneTicket"]["roi_pct"])
            for window in windows
        ]
        result[base] = {
            "mirror_model": mirror,
            "window_count": len(windows),
            "mirror_beats_original_windows": sum(value > 0 for value in deltas),
            "ties_vs_original_windows": sum(value == 0 for value in deltas),
            "mirror_beats_random_windows": sum(value > 0 for value in random_deltas),
            "mean_roi_delta_vs_original_percentage_points": mean(deltas) if deltas else 0.0,
            "median_roi_delta_vs_original_percentage_points": median(deltas) if deltas else 0.0,
            "mean_roi_delta_vs_random_percentage_points": mean(random_deltas) if random_deltas else 0.0,
            "median_roi_delta_vs_random_percentage_points": median(random_deltas) if random_deltas else 0.0,
        }
    return result


def run_multiwindow_backtest(
    rows: list[dict[str, Any]],
    min_history: int | None = None,
    seed: int = DEFAULT_SEED,
    block_size: int = 100,
    rolling_size: int = 200,
    trailing_sizes: Sequence[int] = DEFAULT_TRAILING_SIZES,
) -> dict[str, Any]:
    """Produce chronological block, rolling, and trailing-window stability summaries."""
    if block_size < 1 or rolling_size < 1:
        raise ValueError("block_size and rolling_size must be positive")
    if any(size < 1 for size in trailing_sizes):
        raise ValueError("trailing window sizes must be positive")

    walk = run_backtest(rows, min_history=min_history, seed=seed)
    eligible = walk["per_draw"]
    model_names = walk["models_compared"]
    count = len(eligible)
    if count < 2:
        raise ValueError("Need at least two eligible prediction draws for multi-window analysis")

    families: dict[str, list[dict[str, Any]]] = {
        f"fixed_blocks_{block_size}": [],
        f"rolling_{min(rolling_size, count)}_step_{block_size}": [],
        "trailing_windows": [],
    }

    # Non-overlapping chronological blocks; keep the final partial block and
    # record its draw count explicitly instead of silently dropping data.
    block_family = f"fixed_blocks_{block_size}"
    for window_no, start in enumerate(range(0, count, block_size), 1):
        stop = min(start + block_size, count)
        families[block_family].append(
            _make_window(
                block_family, f"block_{window_no:02d}", start, stop, eligible, model_names
            )
        )

    # Overlapping rolling windows to reduce sensitivity to a single block
    # boundary. Include a final end-aligned window if stride does not land on it.
    width = min(rolling_size, count)
    rolling_family = f"rolling_{width}_step_{block_size}"
    starts = list(range(0, count - width + 1, block_size))
    final_start = count - width
    if final_start not in starts:
        starts.append(final_start)
    for window_no, start in enumerate(sorted(set(starts)), 1):
        families[rolling_family].append(
            _make_window(
                rolling_family,
                f"rolling_{window_no:02d}",
                start,
                start + width,
                eligible,
                model_names,
            )
        )

    # Several explicitly trailing horizons, each ending at the latest
    # evaluated draw. Oversized horizons are skipped (not silently clamped).
    for size in sorted(set(int(value) for value in trailing_sizes)):
        if size > count:
            continue
        families["trailing_windows"].append(
            _make_window(
                "trailing_windows",
                f"last_{size}",
                count - size,
                count,
                eligible,
                model_names,
            )
        )

    family_reports: dict[str, Any] = {}
    for family, windows in families.items():
        if not windows:
            continue
        family_reports[family] = {
            "window_count": len(windows),
            "windows": windows,
            "strategy_stability": _strategy_stability(windows, model_names),
            "mirror_stability": _mirror_stability(windows),
        }

    return {
        "report_version": 1,
        "analysis": "Position-wise Power 6/55 multi-window ROI stability",
        "source_method": walk["method"],
        "mirror_transform": walk["mirror_transform"],
        "dataset": walk["dataset"],
        "window_policy": {
            "fixed_blocks": f"Non-overlapping blocks of {block_size} evaluated draws; includes final partial block",
            "rolling_windows": f"Windows of {min(rolling_size, count)} evaluated draws with stride {block_size}; includes an end-aligned final window",
            "trailing_sizes_requested": sorted(set(int(value) for value in trailing_sizes)),
            "trailing_windows": "Each trailing window ends on the most recent evaluated draw",
            "comparability": "Every strategy in a given window is evaluated on the same actual draws, one ticket per draw, with the same prize configuration",
            "no_lookahead": "Per-draw forecasts were generated by expanding walk-forward evaluation and only use draws before each forecast target",
        },
        "families": family_reports,
        "interpretation_note": (
            "Window-level ROI is noisy and strongly affected by random lottery outcomes. "
            "A mirror win over an original model in a window is descriptive, not proof of predictive edge. "
            "Check consistency across disjoint blocks and compare against the seeded random baseline."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Position-wise Power 6/55 Multi-window Backtest",
        "",
        f"- Available draws: {report['dataset']['draws_available']}",
        f"- Walk-forward evaluation draws: {report['dataset']['evaluation_draws']}",
        f"- Warm-up draws: {report['dataset']['warmup_draws']}",
        f"- Transform: {report['mirror_transform']['formula']}",
        f"- Fixed blocks: {report['window_policy']['fixed_blocks']}",
        f"- Rolling windows: {report['window_policy']['rolling_windows']}",
        f"- Trailing windows requested: {', '.join(map(str, report['window_policy']['trailing_sizes_requested']))}",
        "- Baseline: same seeded random ticket for each evaluated draw; one ticket/model/draw",
        "",
        "## Window-by-window comparison: Ensemble and random baseline",
        "",
        "| Family | Window | Draws | Draw ID range | Date range | Ensemble ROI | Ensemble mirror ROI | Mirror delta pp | Random ROI | Mirror delta vs random pp |",
        "|---|---|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for family, family_data in report["families"].items():
        for window in family_data["windows"]:
            metrics = window["metrics"]
            base = float(metrics["PositionWiseEnsemble"]["roi_pct"])
            mirror = float(metrics["PositionWiseEnsemble_Mirror56Minus"]["roi_pct"])
            random_roi = float(metrics["RandomOneTicket"]["roi_pct"])
            lines.append(
                f"| {family} | {window['name']} | {window['draws']} | "
                f"#{window['start_draw_id']}–#{window['end_draw_id']} | "
                f"{window['start_date']}–{window['end_date']} | {base:.2f}% | "
                f"{mirror:.2f}% | {mirror - base:+.2f} | {random_roi:.2f}% | "
                f"{mirror - random_roi:+.2f} |"
            )

    lines.extend([
        "",
        "## Strategy ROI stability by window family",
        "",
        "| Family | Strategy | Windows | Mean ROI | Median ROI | Best ROI | Worst ROI | Profitable windows | Beats random |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for family, family_data in report["families"].items():
        for strategy, stats in family_data["strategy_stability"].items():
            lines.append(
                f"| {family} | {strategy} | {stats['window_count']} | "
                f"{stats['mean_roi_pct']:.2f}% | {stats['median_roi_pct']:.2f}% | "
                f"{stats['best_roi_pct']:.2f}% | {stats['worst_roi_pct']:.2f}% | "
                f"{stats['profitable_windows']} | {stats['windows_beating_random']} |"
            )

    lines.extend([
        "",
        "## Does the mirror beat its corresponding original?",
        "",
        "| Family | Original model | Windows | Mirror beats original | Mirror beats random | Mean ROI delta vs original | Median ROI delta vs original | Mean ROI delta vs random |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for family, family_data in report["families"].items():
        for base, stats in family_data["mirror_stability"].items():
            lines.append(
                f"| {family} | {base} | {stats['window_count']} | "
                f"{stats['mirror_beats_original_windows']}/{stats['window_count']} | "
                f"{stats['mirror_beats_random_windows']}/{stats['window_count']} | "
                f"{stats['mean_roi_delta_vs_original_percentage_points']:+.2f} pp | "
                f"{stats['median_roi_delta_vs_original_percentage_points']:+.2f} pp | "
                f"{stats['mean_roi_delta_vs_random_percentage_points']:+.2f} pp |"
            )

    lines.extend([
        "",
        "## Important interpretation",
        "",
        report["interpretation_note"],
        "ROI is net prize profit divided by ticket cost. ROI differences are percentage-point differences. "
        "Overlapping rolling/trailing windows are correlated and should not be treated as independent statistical trials. "
        "Historical lottery results do not guarantee future returns.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    report = run_multiwindow_backtest(load_rows(DEFAULT_DATA))
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))
    print(f"POSITIONWISE_MULTIWINDOW_JSON={OUTPUT_JSON}")
    print(f"POSITIONWISE_MULTIWINDOW_MARKDOWN={OUTPUT_MD}")


if __name__ == "__main__":
    main()
