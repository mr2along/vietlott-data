from pathlib import Path
import subprocess


def main() -> None:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    ref = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    path = Path(__file__).with_name("run_backtest_v2.py")
    text = path.read_text(encoding="utf-8")
    has_six_or_seven_validation = "len(result) not in (6, 7)" in text
    has_main_numbers = "row[\"main_numbers\"] = result[:6]" in text
    has_legacy_error = 'raise ValueError(f"Invalid Power 6/55 row:' in text

    print(f"BACKTEST_V2_COMMIT={sha}")
    print(f"BACKTEST_V2_BRANCH={ref}")
    print(f"RUNNER_FILE={path}")
    print(f"SIX_OR_SEVEN_ROW_VALIDATION={has_six_or_seven_validation}")
    print(f"MAIN_NUMBERS_NORMALIZATION={has_main_numbers}")
    print(f"LEGACY_INVALID_ROW_ERROR={has_legacy_error}")

    if not has_six_or_seven_validation:
        raise SystemExit("Runner identity check failed: six/seven-number validation missing")
    if not has_main_numbers:
        raise SystemExit("Runner identity check failed: main-number normalization missing")
    if has_legacy_error:
        raise SystemExit("Runner identity check failed: legacy invalid-row exception still present")


if __name__ == "__main__":
    main()
