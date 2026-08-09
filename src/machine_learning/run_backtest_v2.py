from __future__ import annotations
import json
import os
import random
from pathlib import Path
import numpy as np
import pandas as pd
from .backtest_v2 import PrizeConfig
from .backtest_v2_walkforward import walk_forward
from .strategies import (
    BayesianNumberScoreStrategy,
    ExponentialDecayStrategy,
    LogisticProbabilityStrategy,
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
            if len(result) != 7:
                raise ValueError(f"Normalized benchmark contains non-complete row: {row}")
            row["result"] = result
            row["special"] = result[6]
            row["main_numbers"] = result[:6]
            rows.append(row)
    return rows


def factory(cls, **kwargs):
    def build(df, target_date):
        return cls(df, time_predict=1, **kwargs)

    return build


def validate_prediction(name: str, prediction: list[int]) -> None:
    if len(prediction) != 6:
        raise ValueError(f"{name} returned {len(prediction)} numbers; expected exactly 6: {prediction}")
    if len(set(prediction)) != 6:
        raise ValueError(f"{name} returned duplicate numbers: {prediction}")
    if any(n < 1 or n > 55 for n in prediction):
        raise ValueError(f"{name} returned out-of-range numbers: {prediction}")


def main():
    root = Path(__file__).resolve().parents[2]
    data_path = Path(
        os.environ.get(
            "POWER655_BENCHMARK_PATH",
            root / "artifacts/backtest_v2/power655_benchmark.jsonl",
        )
    )
    rows = load_rows(data_path)
    if len(rows) != 1381:
        raise ValueError(f"Expected 1381 normalized draws, got {len(rows)}")

    factories = {
        "Random": factory(RandomModel),
        "Pattern": factory(PatternStrategy, lookback_days=180, pattern_weight=0.6),
        "PairFrequency": factory(PairFrequencyStrategy, lookback_days=365),
        "Markov": factory(MarkovChainStrategy, lookback_days=365, smoothing=0.5),
        "Bayesian": factory(
            BayesianNumberScoreStrategy,
            lookback_days=365,
            prior_strength=20.0,
            recency_half_life_days=180.0,
        ),
        "ExponentialDecay": factory(
            ExponentialDecayStrategy,
            half_life_days=90,
            hot=True,
            selection_weight=0.8,
        ),
        "LogisticProbability": factory(
            LogisticProbabilityStrategy,
            lookback_draws=180,
            windows=(10, 30, 90),
            C=0.25,
            random_state=42,
        ),
    }

    summaries = []
    details_by_strategy = {}
    for name, make_strategy in factories.items():
        seed = 20260809
        random.seed(seed)
        np.random.seed(seed)
        summary, details = walk_forward(
            name=name,
            rows=rows,
            strategy_factory=make_strategy,
            tickets_per_draw=PRIZES.tickets_per_draw,
            seed=seed,
            prizes=PRIZES,
            min_history=1,
        )
        summaries.append(summary.__dict__)
        draw_gains = [d["gain_vnd"] for d in details]
        draw_costs = [d["cost_vnd"] for d in details]
        for d in details:
            if "predictions" in d:
                for prediction in d["predictions"]:
                    validate_prediction(name, prediction)
        details_by_strategy[name] = {
            "draw_gains_vnd": draw_gains,
            "draw_costs_vnd": draw_costs,
            "dates": [d["date"] for d in details],
        }

    out = Path("artifacts/backtest_v2")
    out.mkdir(parents=True, exist_ok=True)
    (out / "backtest_summary.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out / "backtest_per_draw.json").write_text(
        json.dumps(details_by_strategy, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(pd.DataFrame(summaries).to_string(index=False))
    print("\nPrize configuration:")
    print(PRIZES)
    print(f"\nBenchmarked strategies: {', '.join(factories)}")
    print(f"\nSaved {out / 'backtest_summary.json'} and {out / 'backtest_per_draw.json'}")


if __name__ == "__main__":
    main()
