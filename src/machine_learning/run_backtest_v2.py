"""Run the corrected Power 6/55 benchmark.

Usage from repository root:
    python -m src.machine_learning.run_backtest_v2

Historical files in this repository contain both normal 7-number Power 6/55
rows (6 main numbers + special number) and legacy 6-number rows. Legacy rows
are retained as historical draws with no special number, rather than causing
the benchmark to abort.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

from .backtest_v2 import PrizeConfig
from .backtest_v2_walkforward import walk_forward
from .strategies import (
    MarkovChainStrategy,
    PairFrequencyStrategy,
    PatternStrategy,
    RandomModel,
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


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            row["date"] = pd.to_datetime(row["date"]).date()
            result = [int(x) for x in row["result"]]
            if len(result) not in (6, 7):
                raise ValueError(f"Invalid Power 6/55 row: {row}")
            row["result"] = result
            row["special"] = result[6] if len(result) == 7 else None
            row["main_numbers"] = result[:6]
            rows.append(row)
    return rows


def factory(cls, **kwargs):
    def build(df, target_date):
        return cls(df, time_predict=1, **kwargs)
    return build


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "data" / "power655.jsonl"
    rows = load_rows(data_path)

    factories = {
        "Random": factory(RandomModel),
        "Pattern": factory(PatternStrategy, lookback_days=180, pattern_weight=0.6),
        "PairFrequency": factory(PairFrequencyStrategy, lookback_days=365),
        "Markov": factory(MarkovChainStrategy, lookback_days=365, smoothing=0.5),
    }

    summaries = []
    for name, make_strategy in factories.items():
        seed = 20260809
        random.seed(seed)
        np.random.seed(seed)
        summary = walk_forward(
            name=name,
            rows=rows,
            strategy_factory=make_strategy,
            tickets_per_draw=PRIZES.tickets_per_draw,
            seed=seed,
            prizes=PRIZES,
            min_history=1,
        )
        summaries.append(summary.__dict__)

    report = pd.DataFrame(summaries)
    print(report.to_string(index=False))
    print("\nPrize configuration:")
    print(PRIZES)


if __name__ == "__main__":
    main()
