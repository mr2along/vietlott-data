"""Validate and normalize Power 6/55 data for the benchmark."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

EXPECTED_HISTORICAL_INCOMPLETE_IDS = {"00944"}
MIN_BENCHMARK_ROWS = 100


def _canonical_date(value: object) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError("empty_date")
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError as exc:
        raise ValueError(f"invalid_date:{text}") from exc


def _sort_key(row: dict) -> tuple[str, int | str]:
    ident = str(row["id"]).strip()
    try:
        return str(row["date"]), int(ident)
    except ValueError:
        return str(row["date"]), ident


def _validate_row_shape(row: dict) -> tuple[str, str, list[int]]:
    if not isinstance(row, dict):
        raise ValueError("row_not_object")
    ident = str(row["id"]).strip()
    if not re.fullmatch(r"\d{5}", ident):
        raise ValueError(f"invalid_id:{ident}")
    canonical_date = _canonical_date(row["date"])
    result = [int(x) for x in row["result"]]
    return ident, canonical_date, result


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "data" / "power655.jsonl"
    out = root / "artifacts" / "backtest_v2"
    out.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        raise SystemExit(f"Power 6/55 raw data not found: {source}")

    valid: list[dict] = []
    incomplete: list[dict] = []
    errors: list[dict] = []
    ordering_anomalies: list[dict] = []
    ids: set[str] = set()
    dates: set[str] = set()
    previous_source_key = None

    for line_no, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            ident, canonical_date, result = _validate_row_shape(row)
            row = {**row, "id": ident, "date": canonical_date}
        except Exception as exc:
            errors.append({"line": line_no, "error": str(exc)})
            continue

        source_key = _sort_key(row)
        if previous_source_key is not None and source_key < previous_source_key:
            ordering_anomalies.append(
                {"line": line_no, "id": ident, "date": canonical_date, "previous": previous_source_key}
            )
        previous_source_key = source_key

        if ident in ids:
            errors.append({"line": line_no, "id": ident, "error": "duplicate_id"})
            continue
        if canonical_date in dates:
            errors.append({"line": line_no, "id": ident, "error": "duplicate_date"})
            continue
        ids.add(ident)
        dates.add(canonical_date)

        if len(result) == 6:
            if ident in EXPECTED_HISTORICAL_INCOMPLETE_IDS:
                incomplete.append({**row, "source_line": line_no, "quarantine_reason": "known_historical_incomplete"})
            else:
                errors.append({"line": line_no, "id": ident, "error": "unexpected_incomplete_row"})
            continue

        if (
            len(result) != 7
            or len(set(result[:6])) != 6
            or any(n < 1 or n > 55 for n in result)
            or result[6] in result[:6]
        ):
            errors.append({"line": line_no, "id": ident, "error": "invalid_result"})
            continue

        valid.append({**row, "result": result})

    valid.sort(key=_sort_key)
    incomplete.sort(key=_sort_key)

    all_ids = sorted(int(x) for x in ids)
    id_gaps = [f"{ident:05d}" for ident in range(all_ids[0], all_ids[-1] + 1) if ident not in set(all_ids)] if all_ids else []

    benchmark_text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in valid)
    incomplete_text = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in incomplete)
    (out / "power655_benchmark.jsonl").write_text(benchmark_text, encoding="utf-8")
    (out / "power655_incomplete.jsonl").write_text(incomplete_text, encoding="utf-8")

    report = {
        "raw_rows": len(valid) + len(incomplete) + len(errors),
        "parsed_rows": len(valid) + len(incomplete),
        "benchmark_rows": len(valid),
        "quarantined_rows": len(incomplete),
        "quarantined_ids": [r["id"] for r in incomplete],
        "validation_errors": errors,
        "source_ordering_anomalies": ordering_anomalies,
        "id_continuity_gaps": id_gaps,
        "benchmark_sorted": True,
        "main_numbers_only_for_prediction": True,
        "special_number_reserved_for_prize_evaluation": True,
        "expected_historical_incomplete_ids": sorted(EXPECTED_HISTORICAL_INCOMPLETE_IDS),
    }
    (out / "data_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if errors:
        raise SystemExit("Power 6/55 normalization gate failed: unexpected data validation errors")
    if id_gaps:
        preview = ", ".join(id_gaps[:12])
        suffix = " ..." if len(id_gaps) > 12 else ""
        raise SystemExit(
            f"Power 6/55 normalization gate failed: {len(id_gaps)} missing draw IDs: {preview}{suffix}"
        )
    if len(valid) < MIN_BENCHMARK_ROWS:
        raise SystemExit(
            f"Power 6/55 normalization gate failed: benchmark has only {len(valid)} rows; "
            f"minimum is {MIN_BENCHMARK_ROWS}"
        )


if __name__ == "__main__":
    main()
