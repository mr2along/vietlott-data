"""Select exponential-decay half-life using validation only; keep holdout locked."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from machine_learning.decay_validation import evaluate_half_life

DATA_PATH = Path("data/power655.jsonl")
OUTPUT_PATH = Path("artifacts/backtest_v2/decay_validation.json")
CANDIDATES = (30, 60, 90, 120, 180, 270, 365, 540, 730)

def main():
    print("DECAY_VALIDATION_START", flush=True)
    rows = []
    for line in DATA_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if len(row.get("result", [])) == 7:
            rows.append({"date": pd.to_datetime(row["date"]).date(), "result": row["result"][:6]})
    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    n = len(df)
    validation_start = int(n * 0.70)
    test_start = int(n * 0.85)
    validation_dates = df.iloc[validation_start:test_start]["date"].tolist()
    test_dates = df.iloc[test_start:]["date"].tolist()
    candidates = [evaluate_half_life(df, validation_dates, h).__dict__ for h in CANDIDATES]
    selected = max(candidates, key=lambda r: (r["avg_hits"], -r["half_life_days"]))
    selected_half_life = int(selected["half_life_days"])
    locked_test = evaluate_half_life(df, test_dates, selected_half_life).__dict__
    payload = {
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
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    assert len(candidates) == 9
    assert payload["test_rows_reserved"] > 0
    assert selected_half_life in CANDIDATES
    assert payload["locked_holdout"]["used_for_selection"] is False
    print(json.dumps(payload, indent=2), flush=True)
    print("DECAY_VALIDATION_COMPLETE", flush=True)

if __name__ == "__main__":
    main()
