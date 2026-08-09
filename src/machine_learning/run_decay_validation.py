"""Run ExponentialDecay half-life selection on a validation window."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from machine_learning.decay_validation import evaluate_half_life


DATA_PATH = Path("data/power655.jsonl")
OUTPUT_PATH = Path("artifacts/backtest_v2/decay_validation.json")
CANDIDATES = (30, 60, 90, 120, 180, 270, 365, 540, 730)


def load_dataset() -> pd.DataFrame:
    rows = []
    with DATA_PATH.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            result = row.get("result", [])
            if len(result) != 7:
                continue
            rows.append({"date": pd.to_datetime(row["date"]).date(), "result": result})
    if not rows:
        raise RuntimeError("No complete 7-number Power 6/55 rows found")
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    if df["date"].duplicated().any():
        raise RuntimeError("Duplicate dates in benchmark dataset")
    return df


def main() -> None:
    df = load_dataset()
    n = len(df)
    validation_start = int(n * 0.70)
    test_start = int(n * 0.85)
    validation_dates = df.iloc[validation_start:test_start]["date"].tolist()

    results = [
        evaluate_half_life(df, validation_dates, half_life_days=h).__dict__
        for h in CANDIDATES
    ]
    best = max(results, key=lambda r: (r["avg_hits"], -r["half_life_days"]))

    payload = {
        "dataset_rows": n,
        "train_rows": validation_start,
        "validation_rows": test_start - validation_start,
        "test_rows_reserved": n - test_start,
        "selection_metric": "average_main_number_hits",
        "random_selection_weight": 0.0,
        "candidates": results,
        "selected_half_life_days": best["half_life_days"],
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
