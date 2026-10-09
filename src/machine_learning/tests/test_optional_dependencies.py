"""Regression tests for keeping the data-validation path lightweight."""

import subprocess
import sys


def test_power655_normalizer_import_does_not_load_optional_ml_stack() -> None:
    """Importing the stdlib-only normalizer must not import backtest or NumPy."""
    probe = """
import sys
import src.machine_learning.normalize_power655
assert "src.machine_learning.backtest" not in sys.modules
assert "numpy" not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_lazy_package_keeps_legacy_public_exports() -> None:
    """Lazy loading must not remove previously documented package exports."""
    probe = """
import src.machine_learning as ml
expected = {
    "PredictModel", "RandomModel", "NotRepeatStrategy", "FrequencyStrategy",
    "HotNumbersStrategy", "ColdNumbersStrategy", "PatternStrategy",
    "LongAbsenceStrategy", "ExponentialDecayStrategy", "PairFrequencyStrategy",
    "MarkovChainStrategy", "StrategyBacktester", "ParameterTuner",
    "StrategyComparator", "BacktestResult",
}
assert set(ml.__all__) == expected
assert "numpy" not in __import__("sys").modules
"""
    result = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
