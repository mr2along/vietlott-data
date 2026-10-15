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


def run_backtest(
    rows: list[dict[str, Any]],
    min_history: int | None = None,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    """Run expanding walk-forward predictions and calculate comparable ROI."""
    ordered = sorted(rows, key=lambda row: (row["date"], row["id"]))
    if min_history is None:
        min_history = max(100, int(len(ordered) * 0.10))
    if min_history < 1 or min_history >= len(ordered) - 1:
        raise ValueError(f"min_history must be in [1, {len(ordered) - 2}]")

    # The model stores the full timeline but filters strictly to date < target
    # inside score_positions; the explicit test guards against future leakage.
    model_df = pd.DataFrame(
        [{"date": row["date"], "result": row["result"][:6]} for row in ordered]
    )
    model = PositionWiseEnsembleStrategy(model_df)
    rng = random.Random(seed)

    eligible_rows = ordered[min_history:]
    actual_results: list[list[int]] = []
    position_tickets: list[list[list[int]]] = []
    random_tickets: list[list[list[int]]] = []
    per_draw: list[dict[str, Any]] = []

    for index in range(min_history, len(ordered)):
        target = ordered[index]
        prediction = model.predict(target["date"])
        if len(prediction) != 6 or prediction != sorted(set(prediction)):
            raise AssertionError(f"Invalid position-wise prediction for #{target['id']}: {prediction}")
        if any(number < 1 or number > 55 for number in prediction):
            raise AssertionError(f"Out-of-range prediction for #{target['id']}: {prediction}")

        random_ticket = sorted(rng.sample(range(1, 56), 6))
        actual_results.append(list(target["result"]))
        position_tickets.append([prediction])
        random_tickets.append([random_ticket])
        per_draw.append(
            {
                "draw_id": target["id"],
                "date": target["date"].isoformat(),
                "forecast": prediction,
                "random_baseline": random_ticket,
                "actual_main": sorted(target["result"][:6]),
                "special": target["result"][6],
            }
        )

    if len(per_draw) != len(eligible_rows):
        raise AssertionError("Backtest lost eligible draws")

    full = {
        "PositionWiseEnsemble": _summary("PositionWiseEnsemble", actual_results, position_tickets),
        "RandomOneTicket": _summary("RandomOneTicket", actual_results, random_tickets),
    }
    holdout_start = max(0, int(len(per_draw) * 0.85))
    holdout_results = actual_results[holdout_start:]
    holdout_position = position_tickets[holdout_start:]
    holdout_random = random_tickets[holdout_start:]
    tail_holdout = {
        "start_draw_id": per_draw[holdout_start]["draw_id"] if per_draw[holdout_start:] else None,
        "end_draw_id": per_draw[-1]["draw_id"] if per_draw else None,
        "PositionWiseEnsemble": _summary(
            "PositionWiseEnsemble", holdout_results, holdout_position
        ),
        "RandomOneTicket": _summary(
            "RandomOneTicket", holdout_results, holdout_random
        ),
    }

    return {
        "report_version": 1,
        "model": "PositionWiseEnsemble",
        "method": "Expanding walk-forward; each target sees only earlier draws; one ticket per draw",
        "dataset": {
            "draws_available": len(ordered),
            "first_draw_id": ordered[0]["id"],
            "last_draw_id": ordered[-1]["id"],
            "evaluation_draws": len(per_draw),
            "warmup_draws": min_history,
            "tickets_per_draw": 1,
            "ticket_price_vnd": 10_000,
            "seeded_random_baseline_seed": seed,
        },
        "full_walk_forward": full,
        "tail_holdout_last_15pct": tail_holdout,
        "per_draw": per_draw,
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render ROI and net return for the full walk-forward and tail holdout."""
    lines = [
        "# Position-wise Power 6/55 ROI Backtest",
        "",
        f"- Method: {report['method']}",
        f"- Available draws: {report['dataset']['draws_available']}",
        f"- Evaluation draws: {report['dataset']['evaluation_draws']}",
        f"- Warm-up draws: {report['dataset']['warmup_draws']}",
        "- Ticket budget: one ticket per evaluated draw for both strategies",
        "- Prize assumptions: same minimum prize schedule as Backtest V2",
        "",
        "## Full walk-forward",
        "",
        "| Strategy | Draws | Tickets | Cost (VND) | Prize gain (VND) | Net (VND) | ROI | Avg. main matches |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in report["full_walk_forward"].items():
        lines.append(
            f"| {name} | {row['draws']} | {row['tickets']} | {row['cost']:,} | "
            f"{row['gain']:,} | {row['net_profit']:,} | {row['roi_pct']:.2f}% | "
            f"{row['average_main_matches']:.4f} |"
        )

    lines += [
        "",
        "## Tail holdout (last 15% of eligible draws)",
        "",
        f"- Draw range: #{report['tail_holdout_last_15pct']['start_draw_id']} "
        f"to #{report['tail_holdout_last_15pct']['end_draw_id']}",
        "",
        "| Strategy | Draws | Tickets | Cost (VND) | Prize gain (VND) | Net (VND) | ROI | Avg. main matches |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("PositionWiseEnsemble", "RandomOneTicket"):
        row = report["tail_holdout_last_15pct"][name]
        lines.append(
            f"| {name} | {row['draws']} | {row['tickets']} | {row['cost']:,} | "
            f"{row['gain']:,} | {row['net_profit']:,} | {row['roi_pct']:.2f}% | "
            f"{row['average_main_matches']:.4f} |"
        )

    lines += [
        "",
        "## Interpretation",
        "",
        "ROI is net profit divided by ticket cost. A negative ROI means prizes did not cover ticket spend. "
        "The tail holdout is reported separately to reduce the risk of judging the model only by the full-history result. "
        "Lottery outcomes are random; historical performance does not guarantee future returns.",
        "",
    ]
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
