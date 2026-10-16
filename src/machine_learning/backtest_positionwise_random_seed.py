"""Multi-seed random-baseline validation for position-wise Power 6/55 models.

Each seeded baseline generates one fresh uniform 6-of-55 ticket for every
walk-forward target draw. All candidate models and random tickets are scored
against the same outcomes, one ticket per draw, using the same prize table.
Random-seed ROI distributions are descriptive empirical benchmarks, not proof
that any strategy has a predictive edge.
"""
from __future__ import annotations

import json
import random
from pathlib import Path
from statistics import mean, median
from typing import Any, Sequence

from .backtest_positionwise_roi import DEFAULT_DATA, load_rows, run_backtest
from .backtest_v2 import PrizeConfig, evaluate_ticket

OUTPUT_JSON = Path("artifacts/backtest_v2/positionwise_random_seed_validation.json")
OUTPUT_MD = Path("artifacts/backtest_v2/positionwise_random_seed_validation.md")
DEFAULT_SEED_START = 10_000
DEFAULT_SEED_COUNT = 500
DEFAULT_BLOCK_SIZE = 100
DEFAULT_ROLLING_SIZE = 200
DEFAULT_TRAILING_SIZES = (100, 200, 300, 500, 800)


def _percentile(values: Sequence[float], percentile: float) -> float:
    """Linearly interpolated percentile for a non-empty sequence."""
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * percentile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _make_scopes(
    draws: Sequence[dict[str, Any]],
    block_size: int,
    rolling_size: int,
    trailing_sizes: Sequence[int],
) -> list[dict[str, Any]]:
    """Create the same full, holdout, block, rolling and trailing draw scopes."""
    count = len(draws)
    holdout_start = max(0, int(count * 0.85))
    scopes: list[dict[str, Any]] = [
        {"family": "overall", "name": "full_walk_forward", "start": 0, "stop": count},
        {
            "family": "overall",
            "name": "tail_holdout_last_15pct",
            "start": holdout_start,
            "stop": count,
        },
    ]

    for number, start in enumerate(range(0, count, block_size), 1):
        scopes.append({
            "family": f"fixed_blocks_{block_size}",
            "name": f"block_{number:02d}",
            "start": start,
            "stop": min(start + block_size, count),
        })

    width = min(rolling_size, count)
    starts = list(range(0, count - width + 1, block_size))
    end_aligned = count - width
    if end_aligned not in starts:
        starts.append(end_aligned)
    for number, start in enumerate(sorted(set(starts)), 1):
        scopes.append({
            "family": f"rolling_{width}_step_{block_size}",
            "name": f"rolling_{number:02d}",
            "start": start,
            "stop": start + width,
        })

    for size in sorted(set(int(value) for value in trailing_sizes)):
        if size <= count:
            scopes.append({
                "family": "trailing_windows",
                "name": f"last_{size}",
                "start": count - size,
                "stop": count,
            })

    for scope in scopes:
        start, stop = scope["start"], scope["stop"]
        if stop <= start:
            raise ValueError(f"Empty scope: {scope['family']}/{scope['name']}")
        scope["draws"] = stop - start
        scope["start_draw_id"] = draws[start]["draw_id"]
        scope["end_draw_id"] = draws[stop - 1]["draw_id"]
        scope["start_date"] = draws[start]["date"]
        scope["end_date"] = draws[stop - 1]["date"]
    return scopes


def _ticket_outcome(ticket: Sequence[int], result: Sequence[int], prizes: PrizeConfig):
    item = evaluate_ticket(ticket, result, prizes)
    return (int(item.main_matches), bool(item.special_match), int(item.prize))


def _metrics(outcomes: Sequence[tuple[int, bool, int]]) -> dict[str, Any]:
    """ROI and match metrics derived from per-draw ticket outcomes."""
    draws = len(outcomes)
    gain = sum(item[2] for item in outcomes)
    cost = draws * PrizeConfig(ticket_price=10_000).ticket_price
    match_counts = [item[0] for item in outcomes]
    return {
        "draws": draws,
        "tickets": draws,
        "cost": cost,
        "gain": gain,
        "net_profit": gain - cost,
        "roi_pct": (gain - cost) / cost * 100.0 if cost else 0.0,
        "average_main_matches": mean(match_counts) if match_counts else 0.0,
        "p3_plus_pct": (sum(value >= 3 for value in match_counts) / draws * 100.0) if draws else 0.0,
        "p4_plus_pct": (sum(value >= 4 for value in match_counts) / draws * 100.0) if draws else 0.0,
        "p5_plus_pct": (sum(value >= 5 for value in match_counts) / draws * 100.0) if draws else 0.0,
        "p6_pct": (sum(value == 6 for value in match_counts) / draws * 100.0) if draws else 0.0,
    }


def _distribution(roi_values: Sequence[float]) -> dict[str, Any]:
    values = [float(value) for value in roi_values]
    if not values:
        raise ValueError("Cannot summarize an empty random ROI distribution")
    return {
        "seed_count": len(values),
        "mean_roi_pct": mean(values),
        "median_roi_pct": median(values),
        "p01_roi_pct": _percentile(values, 0.01),
        "p05_roi_pct": _percentile(values, 0.05),
        "p25_roi_pct": _percentile(values, 0.25),
        "p75_roi_pct": _percentile(values, 0.75),
        "p95_roi_pct": _percentile(values, 0.95),
        "p99_roi_pct": _percentile(values, 0.99),
        "best_roi_pct": max(values),
        "worst_roi_pct": min(values),
        "profitable_seed_count": sum(value > 0 for value in values),
        "profitable_seed_pct": sum(value > 0 for value in values) / len(values) * 100.0,
    }


def _compare_to_random(model_roi: float, random_rois: Sequence[float]) -> dict[str, Any]:
    count = len(random_rois)
    random_ge = sum(float(value) >= model_roi for value in random_rois)
    random_le = sum(float(value) <= model_roi for value in random_rois)
    return {
        "model_roi_pct": float(model_roi),
        "model_random_percentile_pct": random_le / count * 100.0 if count else 0.0,
        "random_seeds_roi_at_least_model": random_ge,
        "random_seeds_roi_at_least_model_pct": random_ge / count * 100.0 if count else 0.0,
        "empirical_one_sided_p_random_roi_ge_model": (random_ge + 1) / (count + 1) if count else 1.0,
        "random_roi_distribution": _distribution(random_rois),
    }


def run_random_seed_validation(
    rows: list[dict[str, Any]],
    min_history: int | None = None,
    seed_start: int = DEFAULT_SEED_START,
    seed_count: int = DEFAULT_SEED_COUNT,
    block_size: int = DEFAULT_BLOCK_SIZE,
    rolling_size: int = DEFAULT_ROLLING_SIZE,
    trailing_sizes: Sequence[int] = DEFAULT_TRAILING_SIZES,
) -> dict[str, Any]:
    """Compare model ROI to hundreds of seeded uniform tickets on identical draws."""
    if seed_count < 20:
        raise ValueError("seed_count must be >= 20 for a useful empirical baseline")
    if seed_start < 0:
        raise ValueError("seed_start must be >= 0")
    if block_size < 1 or rolling_size < 1:
        raise ValueError("block_size and rolling_size must be positive")
    if any(int(size) < 1 for size in trailing_sizes):
        raise ValueError("trailing window sizes must be positive")

    walk = run_backtest(rows, min_history=min_history, seed=655)
    draws = walk["per_draw"]
    if len(draws) < 2:
        raise ValueError("Need at least two eligible walk-forward draws")
    model_names = [name for name in walk["models_compared"] if name != "RandomOneTicket"]
    scopes = _make_scopes(draws, block_size, rolling_size, trailing_sizes)
    prizes = PrizeConfig(tickets_per_draw=1)
    actual_results = [
        [int(value) for value in draw["actual_main"]] + [int(draw["special"])]
        for draw in draws
    ]

    # Pre-score each deterministic model on each individual target draw.
    model_outcomes: dict[str, list[tuple[int, bool, int]]] = {}
    for name in model_names:
        model_outcomes[name] = [
            _ticket_outcome(draw["forecasts"][name], actual, prizes)
            for draw, actual in zip(draws, actual_results)
        ]

    random_rois_by_scope: dict[str, list[float]] = {
        f"{scope['family']}/{scope['name']}": [] for scope in scopes
    }
    for offset in range(seed_count):
        seed = seed_start + offset
        rng = random.Random(seed)
        outcomes = [
            _ticket_outcome(sorted(rng.sample(range(1, 56), 6)), actual, prizes)
            for actual in actual_results
        ]
        for scope in scopes:
            key = f"{scope['family']}/{scope['name']}"
            random_rois_by_scope[key].append(
                _metrics(outcomes[scope["start"]:scope["stop"]])["roi_pct"]
            )

    scope_reports: dict[str, Any] = {}
    for scope in scopes:
        key = f"{scope['family']}/{scope['name']}"
        start, stop = scope["start"], scope["stop"]
        random_rois = random_rois_by_scope[key]
        comparisons = {}
        for name in model_names:
            model_roi = _metrics(model_outcomes[name][start:stop])["roi_pct"]
            comparisons[name] = _compare_to_random(model_roi, random_rois)
        scope_reports[key] = {
            "family": scope["family"],
            "name": scope["name"],
            "draws": scope["draws"],
            "start_draw_id": scope["start_draw_id"],
            "end_draw_id": scope["end_draw_id"],
            "start_date": scope["start_date"],
            "end_date": scope["end_date"],
            "model_metrics": {
                name: _metrics(model_outcomes[name][start:stop]) for name in model_names
            },
            "random_seed_roi_distribution": _distribution(random_rois),
            "model_comparisons_vs_random": comparisons,
        }

    family_reports: dict[str, Any] = {}
    for family in sorted({scope["family"] for scope in scopes if scope["family"] != "overall"}):
        keys = [key for key, value in scope_reports.items() if value["family"] == family]
        model_family: dict[str, Any] = {}
        for name in model_names:
            model_rois = [scope_reports[key]["model_metrics"][name]["roi_pct"] for key in keys]
            percentiles = [
                scope_reports[key]["model_comparisons_vs_random"][name]["model_random_percentile_pct"]
                for key in keys
            ]
            median_random_rois = [
                scope_reports[key]["random_seed_roi_distribution"]["median_roi_pct"] for key in keys
            ]
            model_family[name] = {
                "window_count": len(keys),
                "mean_model_roi_pct": mean(model_rois) if model_rois else 0.0,
                "median_model_roi_pct": median(model_rois) if model_rois else 0.0,
                "best_model_roi_pct": max(model_rois) if model_rois else 0.0,
                "worst_model_roi_pct": min(model_rois) if model_rois else 0.0,
                "windows_model_roi_above_random_median": sum(
                    roi > random_median for roi, random_median in zip(model_rois, median_random_rois)
                ),
                "mean_model_random_percentile_pct": mean(percentiles) if percentiles else 0.0,
            }
        family_reports[family] = {
            "window_count": len(keys),
            "model_stability": model_family,
            "overlap_note": (
                "Fixed blocks are non-overlapping. Rolling and trailing windows overlap, "
                "so these windows are correlated and are descriptive rather than independent trials."
            ),
        }

    return {
        "report_version": 1,
        "analysis": "Multi-seed random baseline for position-wise Power 6/55 models",
        "method": (
            "Expanding walk-forward model predictions; each seeded baseline independently "
            "generates one uniformly sampled 6-of-55 ticket for every identical target draw. "
            "All strategies use the same outcomes, one ticket per draw and the same prize schedule."
        ),
        "random_seed_policy": {
            "seed_start_inclusive": seed_start,
            "seed_end_inclusive": seed_start + seed_count - 1,
            "seed_count": seed_count,
            "tickets_per_seed_per_draw": 1,
            "ticket_generation": "random.Random(seed).sample(range(1, 56), 6), sorted",
            "same_seed_ticket_stream_reused_across_scopes": True,
        },
        "dataset": {
            "draws_available": walk["dataset"]["draws_available"],
            "first_draw_id": walk["dataset"]["first_draw_id"],
            "last_draw_id": walk["dataset"]["last_draw_id"],
            "evaluation_draws": len(draws),
            "warmup_draws": walk["dataset"]["warmup_draws"],
            "ticket_price_vnd": prizes.ticket_price,
            "model_strategies_compared": model_names,
            "prize_schedule": {
                "jackpot1_vnd": prizes.jackpot1,
                "jackpot2_vnd": prizes.jackpot2,
                "first_vnd": prizes.first,
                "second_vnd": prizes.second,
                "third_vnd": prizes.third,
            },
        },
        "window_policy": {
            "fixed_blocks": f"Non-overlapping blocks of {block_size}, including any final partial block",
            "rolling_windows": f"Window size {min(rolling_size, len(draws))}, step {block_size}, includes end-aligned final window",
            "trailing_sizes_requested": sorted(set(int(value) for value in trailing_sizes)),
            "comparability": "Models and random baselines use exactly the same target draws within every scope.",
        },
        "scopes": scope_reports,
        "window_family_stability": family_reports,
        "interpretation": (
            "The empirical one-sided p-value is the fraction of random seeds with ROI at least "
            "as high as the model, with a +1 correction. It measures model performance relative "
            "to these simulated random tickets on this historical sequence; it is not a guarantee "
            "of future performance or a causal statistical proof. Jackpot prizes and overlapping "
            "windows make ROI distributions highly skewed."
        ),
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Position-wise Power 6/55 — Multi-seed Random Baseline",
        "",
        f"- Available draws: {report['dataset']['draws_available']}",
        f"- Walk-forward draws evaluated: {report['dataset']['evaluation_draws']}",
        f"- Warm-up draws: {report['dataset']['warmup_draws']}",
        f"- Random seeds: {report['random_seed_policy']['seed_start_inclusive']}–{report['random_seed_policy']['seed_end_inclusive']} ({report['random_seed_policy']['seed_count']} seeds)",
        "- Budget: one ticket per strategy per target draw; ticket price and prize schedule are equal",
        "- Every random seed generates a separate ticket for each evaluated draw; the same seed's ticket stream is reused across all windows",
        "",
        "## Full walk-forward — models versus random-seed distribution",
        "",
        "| Strategy | Model ROI | Random mean | Random median | Random P05 | Random P95 | Model percentile vs random | Random seeds >= model | Empirical p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    full = report["scopes"]["overall/full_walk_forward"]
    for name, comparison in full["model_comparisons_vs_random"].items():
        dist = comparison["random_roi_distribution"]
        lines.append(
            f"| {name} | {comparison['model_roi_pct']:.2f}% | "
            f"{dist['mean_roi_pct']:.2f}% | {dist['median_roi_pct']:.2f}% | "
            f"{dist['p05_roi_pct']:.2f}% | {dist['p95_roi_pct']:.2f}% | "
            f"{comparison['model_random_percentile_pct']:.1f}% | "
            f"{comparison['random_seeds_roi_at_least_model']}/{dist['seed_count']} | "
            f"{comparison['empirical_one_sided_p_random_roi_ge_model']:.4f} |"
        )

    lines.extend([
        "",
        "## Tail holdout — final 15% of eligible draws",
        "",
        "| Strategy | Model ROI | Random median | Random P05 | Random P95 | Model percentile vs random | Random seeds >= model | Empirical p |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    holdout = report["scopes"]["overall/tail_holdout_last_15pct"]
    for name, comparison in holdout["model_comparisons_vs_random"].items():
        dist = comparison["random_roi_distribution"]
        lines.append(
            f"| {name} | {comparison['model_roi_pct']:.2f}% | "
            f"{dist['median_roi_pct']:.2f}% | {dist['p05_roi_pct']:.2f}% | "
            f"{dist['p95_roi_pct']:.2f}% | "
            f"{comparison['model_random_percentile_pct']:.1f}% | "
            f"{comparison['random_seeds_roi_at_least_model']}/{dist['seed_count']} | "
            f"{comparison['empirical_one_sided_p_random_roi_ge_model']:.4f} |"
        )

    lines.extend([
        "",
        "## Stability across the same multi-window scopes",
        "",
        "| Window family | Strategy | Windows | Mean model ROI | Median model ROI | Windows above random median | Mean model percentile vs random |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    for family, family_report in report["window_family_stability"].items():
        for name, summary in family_report["model_stability"].items():
            lines.append(
                f"| {family} | {name} | {summary['window_count']} | "
                f"{summary['mean_model_roi_pct']:.2f}% | {summary['median_model_roi_pct']:.2f}% | "
                f"{summary['windows_model_roi_above_random_median']}/{summary['window_count']} | "
                f"{summary['mean_model_random_percentile_pct']:.1f}% |"
            )

    lines.extend([
        "",
        "## Window-by-window detail — polynomial, ensemble, and random distribution",
        "",
        "| Scope | Draws | Draw IDs | Polynomial ROI | Polynomial random percentile | Ensemble ROI | Ensemble random percentile | Random median ROI | Random P05–P95 |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ])
    for key, scope in report["scopes"].items():
        if scope["family"] == "overall":
            continue
        polynomial = scope["model_comparisons_vs_random"]["PositionWisePolynomial"]
        ensemble = scope["model_comparisons_vs_random"]["PositionWiseEnsemble"]
        dist = scope["random_seed_roi_distribution"]
        lines.append(
            f"| {key} | {scope['draws']} | #{scope['start_draw_id']}–#{scope['end_draw_id']} | "
            f"{polynomial['model_roi_pct']:.2f}% | {polynomial['model_random_percentile_pct']:.1f}% | "
            f"{ensemble['model_roi_pct']:.2f}% | {ensemble['model_random_percentile_pct']:.1f}% | "
            f"{dist['median_roi_pct']:.2f}% | {dist['p05_roi_pct']:.2f}% to {dist['p95_roi_pct']:.2f}% |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        report["interpretation"],
        "Higher model percentile means the model's historical ROI exceeded more simulated random-seed outcomes. "
        "Low empirical p alone does not establish a future predictive edge. Do not promote a model based on "
        "this report alone; evaluate calibration and a genuinely untouched prospective period.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    report = run_random_seed_validation(load_rows(DEFAULT_DATA))
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))
    print(f"POSITIONWISE_RANDOM_SEED_JSON={OUTPUT_JSON}")
    print(f"POSITIONWISE_RANDOM_SEED_MARKDOWN={OUTPUT_MD}")


if __name__ == "__main__":
    main()
