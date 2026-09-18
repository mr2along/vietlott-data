"""Select exponential-decay half-life using validation only; keep holdout locked."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from machine_learning.decay_validation import evaluate_half_life

CANDIDATES = (30, 60, 90, 120, 180, 270, 365, 540, 730)
MIN_DATASET_ROWS = 100


def main() -> None:
    print("DECAY_VALIDATION_START", flush=True)
    root = Path(__file__).resolve().parents[2]
    data_path = root / "artifacts" / "backtest_v2" / "power655_benchmark.jsonl"
    output_path = root / "artifacts" / "backtest_v2" / "decay_validation.json"

    if not data_path.exists():
        raise FileNotFoundError(f"Normalized benchmark not found: {data_path}")

    rows = []
    for line in data_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if len(row.get("result", [])) != 7:
            raise ValueError("Normalized benchmark must contain only complete 7-number rows")
        rows.append(
            {
                "date": pd.to_datetime(row["date"]).date(),
                "result": [int(x) for x in row["result"][:6]],
            }
        )

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    n = len(df)
    if n < MIN_DATASET_ROWS:
        raise ValueError(f"Decay validation dataset too small: {n} < {MIN_DATASET_ROWS}")

    validation_start = int(n * 0.70)
    test_start = int(n * 0.85)
    validation_dates = df.iloc[validation_start:test_start]["date"].tolist()
    test_dates = df.iloc[test_start:]["date"].tolist()
    if not validation_dates or not test_dates:
        raise ValueError("Decay validation split produced an empty validation or holdout set")

    candidates = [evaluate_half_life(df, validation_dates, h).__dict__ for h in CANDIDATES]
    selected = max(candidates, key=lambda r: (r["avg_hits"], -r["half_life_days"]))
    selected_half_life = int(selected["half_life_days"])
    locked_test = evaluate_half_life(df, test_dates, selected_half_life).__dict__

    payload = {
        "dataset_source": str(data_path.relative_to(root)),
        "dataset_rows": n,
        "train_rows": validation_start,
        "validation_rows": test_start - validation_start,
        "test_rows_reserved": n - test_start,
        "selection_metric": "average_main_number_hits",
        "selection_source": "validation_only",
        "random_selection_weight": 0.0,
        "candidates": candidates,
        "selected_half_life_days": selected_half_life,
        "locked_holdout": {"used_for_selection": False, **locked_test},
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    assert len(candidates) == len(CANDIDATES)
    assert payload["test_rows_reserved"] > 0
    assert selected_half_life in CANDIDATES
    assert payload["locked_holdout"]["used_for_selection"] is False

    print(json.dumps(payload, indent=2), flush=True)
    print("DECAY_VALIDATION_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
