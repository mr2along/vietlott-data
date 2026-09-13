from pathlib import Path
import subprocess


def main() -> None:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    ref = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    path = Path(__file__).with_name("run_backtest_v2.py")
    text = path.read_text(encoding="utf-8")

    has_complete_row_validation = (
        "len(row[\"result\"]) != 7" in text
        or "len(result) != 7" in text
        or "len(result)!=7" in text
    )
    has_benchmark_path = "artifacts/backtest_v2/power655_benchmark.jsonl" in text
    has_main_numbers = "result[:6]" in text
    has_legacy_raw_error = "Invalid Power 6/55 row:" in text

    print(f"BACKTEST_V2_COMMIT={sha}")
    print(f"BACKTEST_V2_BRANCH={ref}")
    print(f"RUNNER_FILE={path}")
    print(f"COMPLETE_7_NUMBER_VALIDATION={has_complete_row_validation}")
    print(f"BENCHMARK_DATASET_PATH={has_benchmark_path}")
    print(f"MAIN_NUMBERS_NORMALIZATION={has_main_numbers}")
    print(f"LEGACY_RAW_DATA_ERROR={has_legacy_raw_error}")

    if not has_complete_row_validation:
        raise SystemExit("Runner identity check failed: complete 7-number validation missing")
    if not has_benchmark_path:
        raise SystemExit("Runner identity check failed: normalized benchmark path missing")
    if not has_main_numbers:
        raise SystemExit("Runner identity check failed: main-number slicing missing")
    if has_legacy_raw_error:
        raise SystemExit("Runner identity check failed: legacy raw-data error still present")


if __name__ == "__main__":
    main()
