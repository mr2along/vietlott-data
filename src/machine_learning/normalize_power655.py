"""Validate and normalize Power 6/55 data for the benchmark."""
from __future__ import annotations
import json
from pathlib import Path

def _sort_key(row: dict) -> tuple[str, int | str]:
    ident = str(row["id"]).strip()
    try:
        return str(row["date"]), int(ident)
    except ValueError:
        return str(row["date"]), ident

def main() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "data" / "power655.jsonl"
    out = root / "artifacts" / "backtest_v2"
    out.mkdir(parents=True, exist_ok=True)
    valid, incomplete, errors, ordering_anomalies = [], [], [], []
    ids, dates = set(), set()
    previous_source_key = None

    for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            result = [int(x) for x in row["result"]]
            ident, d = str(row["id"]), str(row["date"])
        except Exception as exc:
            errors.append({"line": line_no, "error": str(exc)})
            continue
        source_key = _sort_key(row)
        if previous_source_key is not None and source_key < previous_source_key:
            ordering_anomalies.append({"line": line_no, "id": ident, "date": d, "previous": previous_source_key})
        previous_source_key = source_key
        if ident in ids:
            errors.append({"line": line_no, "error": "duplicate_id"})
        ids.add(ident)
        if d in dates:
            errors.append({"line": line_no, "error": "duplicate_date"})
        dates.add(d)
        if len(result) == 6:
            incomplete.append({**row, "source_line": line_no})
            continue
        if len(result) != 7 or len(set(result[:6])) != 6 or any(n < 1 or n > 55 for n in result) or result[6] in result[:6]:
            errors.append({"line": line_no, "id": ident, "error": "invalid_result"})
            continue
        valid.append(row)

    valid.sort(key=_sort_key)
    (out / "power655_benchmark.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in valid), encoding="utf-8")
    (out / "power655_incomplete.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in incomplete), encoding="utf-8")
    report = {
        "raw_rows": len(valid) + len(incomplete),
        "benchmark_rows": len(valid),
        "quarantined_rows": len(incomplete),
        "validation_errors": errors,
        "source_ordering_anomalies": ordering_anomalies,
        "benchmark_sorted": True,
        "main_numbers_only_for_prediction": True,
        "special_number_reserved_for_prize_evaluation": True,
    }
    (out / "data_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors or len(incomplete) != 1 or len(valid) != 1381:
        raise SystemExit("Power 6/55 normalization gate failed")

if __name__ == "__main__":
    main()
