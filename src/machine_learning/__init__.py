"""
Machine Learning module for Vietlott lottery prediction and analysis.

The module is optional and requires additional ML dependencies. Public symbols
are loaded lazily so data-validation tools under this package can run without
installing the optional ML extra.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    "PredictModel": ".strategies.base",
    "RandomModel": ".strategies.random_strategy",
    "NotRepeatStrategy": ".strategies.not_repeat",
    "FrequencyStrategy": ".strategies.frequency",
    "HotNumbersStrategy": ".strategies.frequency",
    "ColdNumbersStrategy": ".strategies.frequency",
    "PatternStrategy": ".strategies.pattern",
    "LongAbsenceStrategy": ".strategies.long_absence",
    "ExponentialDecayStrategy": ".strategies.exponential_decay",
    "PairFrequencyStrategy": ".strategies.pair_frequency",
    "MarkovChainStrategy": ".strategies.markov_chain",
    "StrategyBacktester": ".backtest",
    "ParameterTuner": ".backtest",
    "StrategyComparator": ".backtest",
    "BacktestResult": ".backtest",
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    """Load an exported ML symbol only when a caller requests it."""
    try:
        module_name = _EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None

    module = import_module(module_name, package=__name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
