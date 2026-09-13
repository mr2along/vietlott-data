"""Validate and normalize Power 6/55 data for the benchmark."""
from __future__ import annotations
import json
from pathlib import Path

def main() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "data" / "power655.jsonl"
    out = root / "artifacts" / "backtest_v2"
    out.mkdir(parents=True, exist_ok=True)
    valid, incomplete, errors = [], [], []
    ids, dates = set(), set()
    for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip(): continue
        try:
            row = json.loads(line); result = [int(x) for x in row["result"]]
            ident, d = str(row["id"]), str(row["date"])
        except Exception as exc:
            errors.append({"line": line_no, "error": str(exc)}); continue
        if ident in ids: errors.append({"line": line_no, "error": "duplicate_id"})
        ids.add(ident)
        if d in dates: errors.append({"line": line_no, "error": "duplicate_date"})
        dates.add(d)
        if len(result) == 6:
            incomplete.append({**row, "source_line": line_no}); continue
        if len(result) != 7 or len(set(result[:6])) != 6 or any(n < 1 or n > 55 for n in result) or result[6] in result[:6]:
            errors.append({"line": line_no, "id": ident, "error": "invalid_result"}); continue
        valid.append(row)
    (out / "power655_benchmark.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in valid), encoding="utf-8")
    (out / "power655_incomplete.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in incomplete), encoding="utf-8")
    report = {"raw_rows": len(valid)+len(incomplete), "benchmark_rows": len(valid), "quarantined_rows": len(incomplete), "validation_errors": errors}
    (out / "data_validation.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors or len(incomplete) != 1 or len(valid) != 1381: raise SystemExit("Power 6/55 normalization gate failed")
if __name__ == "__main__": main()
