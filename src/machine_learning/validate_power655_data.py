"""Validate and profile the raw Power 6/55 JSONL before backtesting."""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    path = root / "data" / "power655.jsonl"

    rows = []
    errors = []
    six_number = []
    seven_number = []
    seen_ids = Counter()
    seen_dates = Counter()

    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append({"line": line_no, "type": "invalid_json", "detail": str(exc)})
                continue

            required = {"date", "id", "result"}
            missing = sorted(required - row.keys())
            if missing:
                errors.append({"line": line_no, "type": "missing_fields", "detail": missing})
                continue

            try:
                d = date.fromisoformat(str(row["date"]))
            except ValueError:
                errors.append({"line": line_no, "type": "invalid_date", "detail": row.get("date")})
                continue

            values = row["result"]
            if not isinstance(values, list) or not all(isinstance(x, (int, float)) and int(x) == x for x in values):
                errors.append({"line": line_no, "id": row.get("id"), "type": "invalid_result_type"})
                continue
            values = [int(x) for x in values]

            seen_ids[str(row["id"])] += 1
            seen_dates[d] += 1
            rows.append((d, str(row["id"]), values, line_no))

            if len(values) == 6:
                six_number.append({"line": line_no, "id": str(row["id"]), "date": str(d), "result": values})
            elif len(values) == 7:
                seven_number.append({"line": line_no, "id": str(row["id"]), "date": str(d), "result": values})
            else:
                errors.append({"line": line_no, "id": str(row["id"]), "type": "wrong_result_length", "length": len(values), "result": values})
                continue

            main = values[:6]
            if len(set(main)) != 6:
                errors.append({"line": line_no, "id": str(row["id"]), "type": "duplicate_main_number", "result": values})
            if any(x < 1 or x > 55 for x in main):
                errors.append({"line": line_no, "id": str(row["id"]), "type": "main_out_of_range", "result": values})
            if values[0:6] != sorted(main):
                errors.append({"line": line_no, "id": str(row["id"]), "type": "main_not_sorted", "result": values})
            if len(values) == 7:
                special = values[6]
                if not 1 <= special <= 55:
                    errors.append({"line": line_no, "id": str(row["id"]), "type": "special_out_of_range", "result": values})
                if special in main:
                    errors.append({"line": line_no, "id": str(row["id"]), "type": "special_duplicates_main", "result": values})

    rows.sort(key=lambda x: x[0])
    for previous, current in zip(rows, rows[1:]):
        if current[0] < previous[0]:
            errors.append({"type": "date_order_error", "previous": str(previous[0]), "current": str(current[0])})

    duplicate_ids = {k: v for k, v in seen_ids.items() if v > 1}
    duplicate_dates = {str(k): v for k, v in seen_dates.items() if v > 1}

    report = {
        "file": str(path),
        "rows": len(rows),
        "six_number_rows": len(six_number),
        "seven_number_rows": len(seven_number),
        "duplicate_ids": duplicate_ids,
        "duplicate_dates": duplicate_dates,
        "validation_errors": errors,
        "six_number_examples": six_number[:25],
        "first_date": str(rows[0][0]) if rows else None,
        "last_date": str(rows[-1][0]) if rows else None,
    }

    out = root / "artifacts" / "backtest_v2"
    out.mkdir(parents=True, exist_ok=True)
    (out / "data_validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))

    # Six-number rows are a data-quality finding, not silently accepted as
    # complete 6+1 draws. They must be reviewed before an ROI benchmark.
    if errors or duplicate_ids or duplicate_dates:
        raise SystemExit("Power 6/55 data validation failed; inspect data_validation.json")
    if six_number:
        raise SystemExit("Power 6/55 data contains incomplete 6-number rows; normalize/quarantine before ROI benchmark")


if __name__ == "__main__":
    main()
