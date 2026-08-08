from pathlib import Path
import subprocess


def main() -> None:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    ref = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    path = Path(__file__).with_name("run_backtest_v2.py")
    text = path.read_text(encoding="utf-8")
    print(f"BACKTEST_V2_COMMIT={sha}")
    print(f"BACKTEST_V2_BRANCH={ref}")
    print(f"RUNNER_FILE={path}")
    print(f"SKIP_INVALID_ROWS={'if len(result) != 7:' in text}")
    print(f"LEGACY_INVALID_ROW_ERROR={'raise ValueError(f\"Invalid Power 6/55 row:' in text}")
    if "if len(result) != 7:" not in text:
        raise SystemExit("Runner identity check failed: invalid-row skip logic missing")
    if 'raise ValueError(f"Invalid Power 6/55 row:' in text:
        raise SystemExit("Runner identity check failed: legacy invalid-row exception still present")


if __name__ == "__main__":
    main()
