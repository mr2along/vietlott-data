"""Walk-forward ROI backtest for the position-wise Power 6/55 model.

Every target prediction uses only draws strictly before the target. The
position-wise model is evaluated as one ticket per draw, alongside a seeded
one-ticket random baseline; this avoids pretending a single predicted set is
a 30-ticket portfolio. The final 15% of eligible draws is also reported
separately as a tail holdout.
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict
from datetime import date
from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from .backtest_v2 import PrizeConfig, summarize
from .strategies import PositionWiseEnsembleStrategy
from .strategies.positionwise_polynomial import PositionWisePolynomialStrategy

DEFAULT_DATA = Path("artifacts/backtest_v2/power655_benchmark.jsonl")
OUTPUT_JSON = Path("artifacts/backtest_v2/positionwise_roi_backtest.json")
OUTPUT_MD = Path("artifacts/backtest_v2/positionwise_roi_backtest.md")
DEFAULT_SEED = 655


def load_rows(path: Path = DEFAULT_DATA) -> list[dict[str, Any]]:
    """Load complete normalized 6+1 draws in chronological order."""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            raw = json.loads(line)
            result = [int(value) for value in raw["result"]]
            if len(result) != 7:
                continue
            main = result[:6]
            special = result[6]
            if len(set(main)) != 6 or not all(1 <= value <= 55 for value in main):
                raise ValueError(f"Invalid main numbers in draw {raw.get('id')}: {main}")
            if not 1 <= special <= 55 or special in main:
                raise ValueError(f"Invalid special number in draw {raw.get('id')}: {special}")
            rows.append(
                {
                    "id": str(raw.get("id", "")),
                    "date": pd.Timestamp(raw["date"]).date(),
                    "result": result,
                }
            )
    rows.sort(key=lambda row: (row["date"], row["id"]))
    if len(rows) < 100:
        raise ValueError(f"Need at least 100 complete draws; found {len(rows)}")
    if len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Duplicate draw IDs in normalized benchmark")
    return rows


def _summary(
    name: str,
    actual_results: Sequence[Sequence[int]],
    tickets: Sequence[Sequence[Sequence[int]]],
) -> dict[str, Any]:
    return asdict(
        summarize(
            name,
            actual_results,
            tickets,
            PrizeConfig(tickets_per_draw=1),
        )
    )


def _position_accuracy(
    draws: Sequence[dict[str, Any]],
    model_names: Sequence[str],
) -> dict[str, Any]:
    """Count exact slot hits using sorted actual numbers for every ticket model."""
    report: dict[str, Any] = {}
    for name in model_names:
        slot_hits = [0] * 6
        evaluated = [0] * 6
        all_six_exact = 0
        for draw in draws:
            actual = sorted(int(value) for value in draw["actual_main"])
            forecasts = draw.get("forecasts", {})
            predicted = forecasts.get(name)
            if not isinstance(predicted, list) or len(predicted) != 6:
                continue
            for index, (guess, truth) in enumerate(zip(predicted, actual)):
                evaluated[index] += 1
                if int(guess) == truth:
                    slot_hits[index] += 1
            if [int(value) for value in predicted] == actual:
                all_six_exact += 1
        report[name] = {
            "draws": min(evaluated) if evaluated else 0,
            "all_six_exact_draws": all_six_exact,
            "positions": [
                {
                    "position": index + 1,
                    "exact_hits": slot_hits[index],
                    "evaluated": evaluated[index],
                    "hit_rate_pct": (
                        100.0 * slot_hits[index] / evaluated[index]
                        if evaluated[index] else 0.0
                    ),
                }
                for index in range(6)
            ],
        }
    return report


def run_backtest(
    rows: list[dict[str, Any]],
    min_history: int | None = None,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Compare position-specific component models with a seeded random baseline.

    All strategies receive one ticket per evaluated draw, the same target draws,
    and the same prize configuration. Each target forecast only sees prior dates.
    """
    ordered = sorted(rows, key=lambda row: (row["date"], row["id"]))
    if min_history is None:
        min_history = max(100, int(len(ordered) * 0.10))
    if min_history < 1 or min_history >= len(ordered) - 1:
        raise ValueError(f"min_history must be in [1, {len(ordered) - 2}]")

    model_df = pd.DataFrame(
        [{"date": row["date"], "result": row["result"][:6]} for row in ordered]
    )
    model = PositionWiseEnsembleStrategy(model_df)
    polynomial_model = PositionWisePolynomialStrategy(model_df)
    rng = random.Random(seed)

    eligible_rows = ordered[min_history:]
    base_model_names = [
        "PositionWiseBayesian",
        "PositionWiseExponentialDecay",
        "PositionWiseRecent",
        "PositionWiseEnsemble",
        "PositionWisePolynomial",
    ]
    mirror_model_names = [f"{name}_Mirror56Minus" for name in base_model_names]
    model_names = base_model_names + mirror_model_names + ["RandomOneTicket"]
    tickets_by_model: dict[str, list[list[list[int]]]] = {
        name: [] for name in model_names
    }
    actual_results: list[list[int]] = []
    per_draw: list[dict[str, Any]] = []

    for index in range(min_history, len(ordered)):
        target = ordered[index]
        comparison = model.component_predictions(target["date"])
        forecasts: dict[str, list[int]] = {
            name: [int(value) for value in detail["predicted_numbers"]]
            for name, detail in comparison["components"].items()
        }
        forecasts["PositionWisePolynomial"] = polynomial_model.predict(target["date"])

        for name in base_model_names:
            prediction = forecasts.get(name)
            if (
                prediction is None
                or len(prediction) != 6
                or prediction != sorted(set(prediction))
                or any(number < 1 or number > 55 for number in prediction)
            ):
                raise AssertionError(
                    f"Invalid {name} prediction for #{target['id']}: {prediction}"
                )

        # Reflection of the valid 1..55 lottery range is 56 - n.
        # Literal 55 - n can produce 0 for n=55, which is not a valid ticket number.
        for name in base_model_names:
            forecasts[f"{name}_Mirror56Minus"] = sorted(56 - value for value in forecasts[name])
        random_ticket = sorted(rng.sample(range(1, 56), 6))
        forecasts["RandomOneTicket"] = random_ticket
        for name in mirror_model_names:
            prediction = forecasts[name]
            if len(prediction) != 6 or prediction != sorted(set(prediction)) or any(number < 1 or number > 55 for number in prediction):
                raise AssertionError(f"Invalid mirrored {name} prediction for #{target['id']}: {prediction}")
        actual_results.append(list(target["result"]))
        for name in model_names:
            tickets_by_model[name].append([forecasts[name]])

        actual_main = sorted(int(value) for value in target["result"][:6])
        per_draw.append(
            {
                "draw_id": target["id"],
                "date": target["date"].isoformat(),
                "forecasts": forecasts,
                "forecast": forecasts["PositionWiseEnsemble"],
                "random_baseline": random_ticket,
                "actual_main": actual_main,
                "special": target["result"][6],
            }
        )

    if len(per_draw) != len(eligible_rows):
        raise AssertionError("Backtest lost eligible draws")

    full = {
        name: _summary(name, actual_results, tickets_by_model[name])
        for name in model_names
    }
    holdout_start = max(0, int(len(per_draw) * 0.85))
    holdout_draws = per_draw[holdout_start:]
    holdout_results = actual_results[holdout_start:]
    tail_holdout = {
        "start_draw_id": holdout_draws[0]["draw_id"] if holdout_draws else None,
        "end_draw_id": holdout_draws[-1]["draw_id"] if holdout_draws else None,
    }
    tail_holdout.update({
        name: _summary(name, holdout_results, tickets_by_model[name][holdout_start:])
        for name in model_names
    })

    return {
        "report_version": 2,
        "model": "PositionWise model family with mirror-transform challenger",
        "mirror_transform": {
            "formula": "56 - n",
            "reason": "Preserves the valid lottery number domain 1..55; literal 55 - n would produce invalid number 0 when n=55",
            "note": "Mirrored tickets are a deterministic transform of the original forecast, not independently trained models",
        },
        "method": (
            "Expanding walk-forward; each target sees only earlier draws; polynomial model "
            "fits degree-2 trends to block-level slot frequencies and blends them with the "
            "theoretical prior; one ticket per model per draw; same seeded random baseline and prize schedule"
        ),
        "models_compared": model_names,
        "dataset": {
            "draws_available": len(ordered),
            "first_draw_id": ordered[0]["id"],
            "last_draw_id": ordered[-1]["id"],
            "evaluation_draws": len(per_draw),
            "warmup_draws": min_history,
            "tickets_per_model_per_draw": 1,
            "ticket_price_vnd": 10_000,
            "seeded_random_baseline_seed": seed,
        },
        "full_walk_forward": full,
        "position_accuracy_full_walk_forward": _position_accuracy(per_draw, model_names),
        "tail_holdout_last_15pct": tail_holdout,
        "position_accuracy_tail_holdout": _position_accuracy(holdout_draws, model_names),
        "per_draw": per_draw,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render ROI and exact-slot accuracy for full backtest and tail holdout."""
    lines = [
        "# Position-wise Power 6/55 Model-Family Backtest",
        "",
        f"- Method: {report['method']}",
        f"- Available draws: {report['dataset']['draws_available']}",
        f"- Evaluation draws: {report['dataset']['evaluation_draws']}",
        f"- Warm-up draws: {report['dataset']['warmup_draws']}",
        "- Budget: one ticket per model per evaluated draw, equal for all models",
        "- Mirror transform: 56 - n (valid reflection of numbers 1..55; literal 55 - n can create invalid 0)",
        "- Mirrored tickets are deterministic transforms of original predictions, not separately trained models",
        "- Prize assumptions: same prize schedule as Backtest V2",
        "",
        "## Full walk-forward — same budget",
        "",
        "| Strategy | Draws | Tickets | Cost (VND) | Prize gain (VND) | Net (VND) | ROI | Avg. main matches |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in report["models_compared"]:
        row = report["full_walk_forward"][name]
        lines.append(
            f"| {name} | {row['draws']} | {row['tickets']} | {row['cost']:,} | "
            f"{row['gain']:,} | {row['net_profit']:,} | {row['roi_pct']:.2f}% | "
            f"{row['average_main_matches']:.4f} |"
        )

    def append_position_table(title: str, metrics: dict[str, Any]) -> None:
        lines.extend([
            "",
            f"## {title} — exact position hits",
            "",
            "| Model | Position 1 | Position 2 | Position 3 | Position 4 | Position 5 | Position 6 | All-six exact draws |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for name in report["models_compared"]:
            item = metrics.get(name, {})
            rates = [
                float(slot.get("hit_rate_pct", 0.0))
                for slot in item.get("positions", [])
            ]
            rates += [0.0] * (6 - len(rates))
            lines.append(
                f"| {name} | " + " | ".join(f"{value:.2f}%" for value in rates[:6])
                + f" | {item.get('all_six_exact_draws', 0)} |"
            )

    append_position_table(
        "Full walk-forward",
        report["position_accuracy_full_walk_forward"],
    )

    tail = report["tail_holdout_last_15pct"]
    lines.extend([
        "",
        "## Tail holdout — last 15% of eligible draws",
        "",
        f"- Draw range: #{tail['start_draw_id']} to #{tail['end_draw_id']}",
        "",
        "| Strategy | Draws | Tickets | Cost (VND) | Prize gain (VND) | Net (VND) | ROI | Avg. main matches |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for name in report["models_compared"]:
        row = tail[name]
        lines.append(
            f"| {name} | {row['draws']} | {row['tickets']} | {row['cost']:,} | "
            f"{row['gain']:,} | {row['net_profit']:,} | {row['roi_pct']:.2f}% | "
            f"{row['average_main_matches']:.4f} |"
        )
    append_position_table("Tail holdout", report["position_accuracy_tail_holdout"])

    lines.extend([
        "",
        "## Interpretation",
        "",
        "ROI is net profit divided by ticket cost. Exact position hit means the forecasted number "
        "equals the actual number at the same rank after sorting the six main numbers. "
        "All models are evaluated on the same historical targets with one ticket each; the random "
        "baseline is seeded for reproducibility. A negative ROI means prizes did not cover ticket spend. "
        "Lottery outcomes are random; historical performance does not guarantee future returns.",
        "",
    ])
    return "\n".join(lines)

def main() -> None:
    report = run_backtest(load_rows())
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(report), encoding="utf-8")
    print(render_markdown(report))
    print(f"POSITIONWISE_ROI_JSON={OUTPUT_JSON}")
    print(f"POSITIONWISE_ROI_MARKDOWN={OUTPUT_MD}")


if __name__ == "__main__":
    main()
