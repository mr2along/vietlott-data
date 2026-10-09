"""
Machine Learning module for Vietlott lottery prediction and analysis.

The normalization and data-validation tools use only the Python standard library.
Keep ML imports lazy so those tools can run in the base installation without
installing the optional machine-learning dependencies (numpy, pandas, etc.).
Install the optional dependencies with: pip install vietlott-data[ml]
"""

from importlib import import_module
from typing import Any

_STRATEGY_EXPORTS = {
    "RandomModel",
    "NotRepeatStrategy",
    "FrequencyStrategy",
    "HotNumbersStrategy",
    "ColdNumbersStrategy",
    "PatternStrategy",
    "LongAbsenceStrategy",
    "ExponentialDecayStrategy",
    "PairFrequencyStrategy",
    "MarkovChainStrategy",
}

_BACKTEST_EXPORTS = {
    "StrategyBacktester",
    "ParameterTuner",
    "StrategyComparator",
    "BacktestResult",
}

__all__ = [
    "PredictModel",
    "RandomModel",
    "NotRepeatStrategy",
    "FrequencyStrategy",
    "HotNumbersStrategy",
    "ColdNumbersStrategy",
    "PatternStrategy",
    "LongAbsenceStrategy",
    "ExponentialDecayStrategy",
    "PairFrequencyStrategy",
    "MarkovChainStrategy",
    "StrategyBacktester",
    "ParameterTuner",
    "StrategyComparator",
    "BacktestResult",
]


def __getattr__(name: str) -> Any:
    """Load ML classes on demand instead of importing optional dependencies eagerly."""
    if name == "PredictModel":
        module_name = ".strategies.base"
    elif name in _STRATEGY_EXPORTS:
        module_name = ".strategies"
    elif name in _BACKTEST_EXPORTS:
        module_name = ".backtest"
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
