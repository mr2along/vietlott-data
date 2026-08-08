"""Run the corrected Power 6/55 benchmark.

Usage from repository root:
    python -m src.machine_learning.run_backtest_v2

The benchmark uses the repository's JSONL data, strips the special number
from strategy history, and scores it only against the target draw.
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

# Power 6/55 is drawn on Tuesday, Thursday and Saturday.  The repository
# contains one corrupted Mega 6/45 row dated Friday 2022-09-23 (id 00944)
# with only six numbers.  It must not enter a Power 6/55 backtest.
POWER_DRAW_WEEKDAYS = {1, 3, 5}  # Python: Tue, Thu, Sat


def load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    skipped: list[tuple[str, str, str]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            draw_date = pd.to_datetime(row["date"]).date()
            result = [int(x) for x in row["result"]]

            # Reject malformed/non-Power records instead of aborting an
            # otherwise valid historical dataset.  We log every skipped row
            # so data cleaning remains auditable.
            if len(result) != 7:
                skipped.append((str(row.get("id", "")), str(draw_date), f"{len(result)} numbers"))
                continue
            if draw_date.weekday() not in POWER_DRAW_WEEKDAYS:
                skipped.append((str(row.get("id", "")), str(draw_date), "not a Power 6/55 draw weekday"))
                continue

            row["date"] = draw_date
            row["result"] = result
            rows.append(row)

    if skipped:
        print(f"Skipped {len(skipped)} invalid/non-Power rows:")
        for item in skipped:
            print(f"  id={item[0]} date={item[1]} reason={item[2]}")
    return rows


def factory(cls, **kwargs):
    def build(df, target_date):
        return cls(df, time_predict=1, **kwargs)
    return build


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    data_path = root / "data" / "power655.jsonl"
    rows = load_rows(data_path)
    if not rows:
        raise RuntimeError(f"No valid Power 6/55 rows found in {data_path}")

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
