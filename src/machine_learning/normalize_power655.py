"""Validate and normalize Power 6/55 data for the ROI benchmark.

The raw dataset is never modified. Complete 7-number draws are copied to a
benchmark JSONL; incomplete 6-number draws are quarantined and excluded from
both target draws and model history.
"""
from __future__ import annotations

import json
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "data" / "power655.jsonl"
    artifact_dir = root / "artifacts" / "backtest_v2"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    benchmark = artifact_dir / "power655_benchmark.jsonl"
    quarantine = artifact_dir / "power655_incomplete.jsonl"
    report_path = artifact_dir / "data_validation.json"

    valid: list[dict] = []
    incomplete: list[dict] = []
    errors: list[dict] = []
    ids: set[str] = set()
    dates: set[str] = set()

    with source.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                result = [int(x) for x in row["result"]]
                date = str(row["date"])
                ident = str(row["id"])
            except Exception as exc:
                errors.append({"line": line_no, "error": f"parse: {exc}"})
                continue

            if ident in ids:
                errors.append({"line": line_no, "id": ident, "error": "duplicate_id"})
            ids.add(ident)
            if date in dates:
                errors.append({"line": line_no, "date": date, "error": "duplicate_date"})
            dates.add(date)

            if len(result) == 6:
                incomplete.append({**row, "source_line": line_no,
                                   "quarantine_reason": "incomplete_result_missing_special_number"})
                continue
            if len(result) != 7:
                errors.append({"line": line_no, "id": ident, "error": "result_length_not_6_or_7"})
                continue

            main_numbers = result[:6]
            special = result[6]
            if len(set(main_numbers)) != 6:
                errors.append({"line": line_no, "id": ident, "error": "duplicate_main_number"})
                continue
            if any(n < 1 or n > 55 for n in result):
                errors.append({"line": line_no, "id": ident, "error": "number_out_of_range"})
                continue
            if special in main_numbers:
                errors.append({"line": line_no, "id": ident, "error": "special_repeats_main_number"})
                continue
            valid.append(row)

    benchmark.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in valid), encoding="utf-8")
    quarantine.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in incomplete), encoding="utf-8")

    report = {
        "source": str(source),
        "raw_rows": len(valid) + len(incomplete),
        "benchmark_rows": len(valid),
        "six_number_rows": len(incomplete),
        "seven_number_rows": len(valid),
        "quarantined_rows": len(incomplete),
        "validation_errors": errors,
        "quarantine": str(quarantine),
        "benchmark": str(benchmark),
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if errors or len(incomplete) != 1 or len(valid) != 1381:
        raise SystemExit("Power 6/55 normalization gate failed")


if __name__ == "__main__":
    main()
