"""Leakage-safe half-life validation for ExponentialDecayStrategy."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Sequence
import pandas as pd
from machine_learning.strategies.exponential_decay import ExponentialDecayStrategy

@dataclass(frozen=True)
class DecayValidationResult:
    half_life_days: int
    draws: int
    total_hits: int
    avg_hits: float

def evaluate_half_life(df: pd.DataFrame, validation_dates: Iterable, half_life_days: int) -> DecayValidationResult:
    dates = list(validation_dates)
    strategy = ExponentialDecayStrategy(df, half_life_days=half_life_days, selection_weight=1.0)
    hits = 0
    for target in dates:
        row = df[df["date"] == target]
        if row.empty: continue
        hits += len(set(strategy.predict(target)) & {int(x) for x in list(row.iloc[0]["result"])[:6]})
    return DecayValidationResult(half_life_days, len(dates), hits, hits/len(dates) if dates else 0.0)

def select_half_life(df: pd.DataFrame, validation_dates: Sequence, candidates=(30,60,90,120,180,270,365,540,730)) -> DecayValidationResult:
    return max((evaluate_half_life(df, validation_dates, h) for h in candidates), key=lambda r:(r.avg_hits,-r.half_life_days))
