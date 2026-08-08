"""Run the corrected Power 6/55 benchmark and export an auditable report."""
from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import pandas as pd

from .backtest_v2 import PrizeConfig, summary_dict
from .backtest_v2_walkforward import walk_forward
from .strategies import MarkovChainStrategy, PairFrequencyStrategy, PatternStrategy, RandomModel

PRIZES = PrizeConfig(
    jackpot1=30_000_000_000, jackpot2=3_000_000_000, first=40_000_000,
    second=500_000, third=50_000, ticket_price=10_000, tickets_per_draw=30,
)
POWER_DRAW_WEEKDAYS = {1, 3, 5}


def load_rows(path: Path) -> list[dict]:
    rows: list[dict] = []
    skipped: list[tuple[str, str, str]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            draw_date = pd.to_datetime(row["date"]).date()
            result = [int(x) for x in row["result"]]
            if len(result) != 7:
                skipped.append((str(row.get("id", "")), str(draw_date), f"{len(result)} numbers"))
                continue
            if draw_date.weekday() not in POWER_DRAW_WEEKDAYS:
                skipped.append((str(row.get("id", "")), str(draw_date), "not a Power 6/55 draw weekday"))
                continue
            row["date"], row["result"] = draw_date, result
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
    output_dir = root / "artifacts" / "backtest_v2"
    output_dir.mkdir(parents=True, exist_ok=True)
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
            name=name, rows=rows, strategy_factory=make_strategy,
            tickets_per_draw=PRIZES.tickets_per_draw, seed=seed,
            prizes=PRIZES, min_history=1,
        )
        summaries.append(summary_dict(summary))

    report = pd.DataFrame(summaries)
    report.to_csv(output_dir / "strategy_summary.csv", index=False)
    report.to_csv(output_dir / "prize_audit.csv", index=False)
    with (output_dir / "strategy_summary.json").open("w", encoding="utf-8") as fh:
        json.dump(summaries, fh, ensure_ascii=False, indent=2)
    config = {
        "data_path": str(data_path.relative_to(root)),
        "valid_draws": len(rows),
        "tickets_per_draw": PRIZES.tickets_per_draw,
        "ticket_price": PRIZES.ticket_price,
        "prizes": {"jackpot1": PRIZES.jackpot1, "jackpot2": PRIZES.jackpot2,
                   "first": PRIZES.first, "second": PRIZES.second, "third": PRIZES.third},
        "seed": 20260809,
    }
    with (output_dir / "config.json").open("w", encoding="utf-8") as fh:
        json.dump(config, fh, ensure_ascii=False, indent=2)

    print(report.to_string(index=False))
    print("\nPrize configuration:")
    print(PRIZES)
    print(f"\nAudit artifacts written to: {output_dir}")


if __name__ == "__main__":
    main()
