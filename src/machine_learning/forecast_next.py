"""Generate a forward Power 6/55 forecast from the latest available draw data.

This is a research/forecasting artifact. Lottery draws are random; the output
is a model-generated candidate set, not a claim that future results are
predictable.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from .strategies import (
    BayesianProbabilityStrategy,
    ExponentialDecayStrategy,
    LogisticProbabilityStrategy,
    PortfolioEnsembleStrategy,
    RankEnsembleStrategy,
)


DRAW_WEEKDAYS = {1, 3, 5}  # Tuesday, Thursday, Saturday


def next_draw_date(last_date: date) -> date:
    for offset in range(1, 8):
        candidate = last_date + timedelta(days=offset)
        if candidate.weekday() in DRAW_WEEKDAYS:
            return candidate
    raise RuntimeError("Unable to resolve next Power 6/55 draw date")


def load_complete_rows(path: Path) -> list[dict]:
    rows_by_id: dict[str, dict] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        result = [int(x) for x in row.get("result", [])]
        if len(result) != 7:
            continue
        main = result[:6]
        special = result[6]
        if len(set(main)) != 6 or not all(1 <= x <= 55 for x in main):
            continue
        if not 1 <= special <= 55 or special in main:
            continue
        draw_id = str(row.get("id", ""))
        if not draw_id.isdigit() or len(draw_id) != 5:
            continue
        normalized = {
            "id": draw_id,
            "date": pd.Timestamp(row["date"]).date(),
            "result": result,
        }
        rows_by_id[draw_id] = normalized

    rows = sorted(rows_by_id.values(), key=lambda r: (r["date"], r["id"]))
    if len(rows) < 100:
        raise RuntimeError(f"Need at least 100 complete Power 6/55 rows, got {len(rows)}")
    return rows


def portfolio_stats(portfolio: list[list[int]]) -> dict[str, object]:
    usage = Counter(n for ticket in portfolio for n in ticket)
    overlaps: list[int] = []
    for index, ticket in enumerate(portfolio):
        ticket_set = set(ticket)
        for other in portfolio[index + 1 :]:
            overlaps.append(len(ticket_set.intersection(other)))

    pair_count = len(overlaps)
    average_overlap = sum(overlaps) / pair_count if pair_count else 0.0
    histogram = {
        str(k): overlaps.count(k)
        for k in sorted(set(overlaps))
    }
    return {
        "unique_numbers_used": len(usage),
        "number_usage": dict(sorted(usage.items())),
        "max_number_usage": max(usage.values(), default=0),
        "min_number_usage": min(usage.values(), default=0),
        "average_pairwise_overlap": average_overlap,
        "pairwise_overlap_histogram": histogram,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data",
        default="data/power655.jsonl",
        help="Power 6/55 JSONL data path",
    )
    parser.add_argument(
        "--tickets",
        type=int,
        default=30,
        help="Number of PortfolioEnsemble tickets to emit",
    )
    parser.add_argument(
        "--max-number-usage",
        type=int,
        default=8,
        help="Maximum appearances of one candidate number across the portfolio",
    )
    args = parser.parse_args()

    if args.tickets < 1:
        raise ValueError("--tickets must be >= 1")
    if args.max_number_usage < 1:
        raise ValueError("--max-number-usage must be >= 1")

    rows = load_complete_rows(Path(args.data))
    last = rows[-1]
    target = next_draw_date(last["date"])
    df = pd.DataFrame(
        [{"date": r["date"], "result": r["result"][:6]} for r in rows]
    )

    models = {
        "Bayesian": BayesianProbabilityStrategy(
            df, time_predict=1, prior_strength=20.0, half_life_days=180.0
        ),
        "ExponentialDecay": ExponentialDecayStrategy(
            df, time_predict=1, half_life_days=730, hot=True, selection_weight=1.0
        ),
        "LogisticProbability": LogisticProbabilityStrategy(df, time_predict=1),
        "RankEnsemble": RankEnsembleStrategy(df, time_predict=1),
        "PortfolioEnsemble": PortfolioEnsembleStrategy(
            df,
            time_predict=1,
            tickets_per_draw=args.tickets,
            candidate_pool_size=24,
            usage_penalty=0.35,
            max_number_usage=args.max_number_usage,
        ),
    }

    predictions: dict[str, object] = {}
    for name in ("Bayesian", "ExponentialDecay", "LogisticProbability", "RankEnsemble"):
        predictions[name] = models[name].predict(target)

    portfolio_model = models["PortfolioEnsemble"]
    portfolio = [portfolio_model.predict(target) for _ in range(args.tickets)]
    predictions["PortfolioEnsemble"] = portfolio

    output = {
        "as_of_draw": {
            "id": last["id"],
            "date": last["date"].isoformat(),
            "main": last["result"][:6],
            "special": last["result"][6],
        },
        "target_draw_date": target.isoformat(),
        "target_draw_weekday": target.strftime("%A"),
        "dataset_rows": len(rows),
        "predictions": predictions,
        "portfolio_stats": portfolio_stats(portfolio),
        "method": {
            "main_numbers_only": True,
            "special_used_as_feature": False,
            "portfolio_tickets": args.tickets,
            "candidate_pool_size": 24,
            "max_number_usage": args.max_number_usage,
            "rank_ensemble_weights": {
                "Bayesian": 0.35,
                "ExponentialDecay": 0.35,
                "LogisticProbability": 0.30,
            },
        },
        "note": "Model forecast for research; historical backtest does not establish future lottery predictability.",
    }

    out_path = Path("artifacts/forecast/next_power655.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
