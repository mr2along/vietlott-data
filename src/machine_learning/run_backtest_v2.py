"""Run the corrected Power 6/55 benchmark and persist audit artifacts."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .backtest_v2 import PrizeConfig, evaluate_ticket, summarize
from .strategies import (
    BayesianProbabilityStrategy,
    ExponentialDecayStrategy,
    LogisticProbabilityStrategy,
    MarkovChainStrategy,
    PairFrequencyStrategy,
    PatternStrategy,
    RandomModel,
    UnseenSetGapStrategy,
)

PRIZES = PrizeConfig(
    jackpot1=30_000_000_000,
    jackpot2=3_000_000_000,
    first=40_000_000,
    second=500_000,
    third=50_000,
    ticket_price=10_000,
    tickets_per_draw=30,
)


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            result = [int(x) for x in row["result"]]
            if len(result) != 7:
                raise ValueError(f"Normalized benchmark contains non-complete row: {row}")
            rows.append({"id": row.get("id"), "date": pd.to_datetime(row["date"]).date(), "result": result})
    return rows


def factory(cls, **kwargs):
    def build(df, target_date):
        return cls(df, time_predict=1, **kwargs)
    return build


def run_strategy(name: str, rows: list[dict[str, Any]], make_strategy, seed: int, min_history: int):
    random.seed(seed)
    np.random.seed(seed)
    ordered = sorted(rows, key=lambda r: r["date"])
    results: list[list[int]] = []
    tickets_by_draw: list[list[list[int]]] = []
    per_draw: list[dict[str, Any]] = []

    for index in range(min_history, len(ordered)):
        target = ordered[index]
        history_df = pd.DataFrame(
            [{"date": r["date"], "result": list(r["result"][:6])} for r in ordered[:index]]
        )
        strategy = make_strategy(history_df, target["date"])
        tickets = [list(map(int, strategy.predict(target["date"]))) for _ in range(PRIZES.tickets_per_draw)]
        target_result = list(target["result"])
        results.append(target_result)
        tickets_by_draw.append(tickets)

        evaluations = [evaluate_ticket(ticket, target_result, PRIZES) for ticket in tickets]
        gain = sum(x.prize for x in evaluations)
        matches = [x.main_matches for x in evaluations]
        per_draw.append(
            {
                "strategy": name,
                "draw_index": index,
                "date": str(target["date"]),
                "draw_id": target.get("id"),
                "gain": gain,
                "cost": PRIZES.tickets_per_draw * PRIZES.ticket_price,
                "net_profit": gain - PRIZES.tickets_per_draw * PRIZES.ticket_price,
                "max_main_matches": max(matches),
                "average_main_matches": sum(matches) / len(matches),
                "winning_tickets": sum(x.prize > 0 for x in evaluations),
            }
        )

    return summarize(name, results, tickets_by_draw, PRIZES).__dict__, per_draw


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    benchmark_path = root / "artifacts" / "backtest_v2" / "power655_benchmark.jsonl"
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Benchmark dataset not found: {benchmark_path}")
    rows = load_rows(benchmark_path)

    factories = {
        "Random": factory(RandomModel),
        "Pattern": factory(PatternStrategy, lookback_days=180, pattern_weight=0.6),
        "PairFrequency": factory(PairFrequencyStrategy, lookback_days=365),
        "Markov": factory(MarkovChainStrategy, lookback_days=365, smoothing=0.5),
        "Bayesian": factory(BayesianProbabilityStrategy, prior_strength=20.0, half_life_days=180.0),
        "ExponentialDecay": factory(ExponentialDecayStrategy, half_life_days=730, hot=True, selection_weight=1.0),
        "LogisticProbability": factory(LogisticProbabilityStrategy),
        "UnseenSetGap": factory(UnseenSetGapStrategy, candidate_pool_size=18, max_attempts=200),
    }

    summaries: list[dict[str, Any]] = []
    all_per_draw: list[dict[str, Any]] = []
    for name, make_strategy in factories.items():
        summary, details = run_strategy(
            name, rows, make_strategy, seed=20260809,
            min_history=30 if name == "LogisticProbability" else 1,
        )
        summaries.append(summary)
        all_per_draw.extend(details)

    output_dir = root / "artifacts" / "backtest_v2"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "backtest_summary.json").write_text(json.dumps(summaries, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "backtest_per_draw.json").write_text(json.dumps(all_per_draw, indent=2, ensure_ascii=False), encoding="utf-8")

    print(pd.DataFrame(summaries).to_string(index=False))
    print("\nPrize configuration:")
    print(PRIZES)
    print(f"Wrote {output_dir / 'backtest_summary.json'}")
    print(f"Wrote {output_dir / 'backtest_per_draw.json'}")


if __name__ == "__main__":
    main()
