"""Walk-forward validation utilities for ExponentialDecayStrategy.

Selects a decay half-life using only a validation window. The selected
parameter must then be frozen before the final out-of-sample test.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, Sequence

import pandas as pd

from machine_learning.strategies.exponential_decay import ExponentialDecayStrategy


@dataclass(frozen=True)
class DecayValidationResult:
    half_life_days: int
    draws: int
    total_hits: int
    avg_hits: float


def _main_numbers(value) -> set[int]:
    return {int(x) for x in list(value)[:6]}


def evaluate_half_life(
    df: pd.DataFrame,
    validation_dates: Iterable[date],
    half_life_days: int,
) -> DecayValidationResult:
    """Evaluate one half-life without looking beyond each target date."""
    dates = list(validation_dates)
    strategy = ExponentialDecayStrategy(
        df=df,
        time_predict=1,
        half_life_days=half_life_days,
        selection_weight=1.0,
    )
    total_hits = 0
    for target in dates:
        row = df[df["date"] == target]
        if row.empty:
            continue
        prediction = set(strategy.predict(target))
        actual = _main_numbers(row.iloc[0]["result"])
        total_hits += len(prediction & actual)
    draws = len(dates)
    return DecayValidationResult(
        half_life_days=half_life_days,
        draws=draws,
        total_hits=total_hits,
        avg_hits=(total_hits / draws) if draws else 0.0,
    )


def select_half_life(
    df: pd.DataFrame,
    validation_dates: Sequence[date],
    candidates: Sequence[int] = (30, 60, 90, 120, 180, 270, 365, 540, 730),
) -> DecayValidationResult:
    """Return the best half-life by validation average hits.

    This function deliberately does not inspect any dates after the supplied
    validation window. The caller must freeze the returned parameter before
    running the final OOS test.
    """
    results = [evaluate_half_life(df, validation_dates, h) for h in candidates]
    return max(results, key=lambda r: (r.avg_hits, -r.half_life_days))
