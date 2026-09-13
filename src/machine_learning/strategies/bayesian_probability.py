"""Bayesian-smoothed probability strategy for Power 6/55."""

from __future__ import annotations

import math
from datetime import date
from typing import Dict, List

import pandas as pd

from .base import PredictModel


class BayesianProbabilityStrategy(PredictModel):
    """Rank main numbers by a recency-weighted Beta posterior mean.

    The prior mean is the uniform Power 6/55 inclusion probability (6/55).
    Only draws strictly before the target date are used.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        prior_strength: float = 20.0,
        half_life_days: float | None = 180.0,
    ) -> None:
        super().__init__(df, time_predict)
        if prior_strength <= 0:
            raise ValueError("prior_strength must be > 0")
        if half_life_days is not None and half_life_days <= 0:
            raise ValueError("half_life_days must be > 0 or None")
        self.prior_strength = float(prior_strength)
        self.half_life_days = half_life_days
        self._cache: Dict[date, List[int]] = {}

    def predict(self, target_date: date) -> List[int]:
        target = pd.Timestamp(target_date)
        if target_date in self._cache:
            return list(self._cache[target_date])

        history = self.df[self.df["date"] < target_date]
        p0 = self.number_predict / (self.max_val - self.min_val + 1)
        alpha0 = self.prior_strength * p0
        beta0 = self.prior_strength * (1.0 - p0)
        hits = {n: 0.0 for n in range(self.min_val, self.max_val + 1)}
        trials = 0.0

        for _, row in history.iterrows():
            d = pd.Timestamp(row["date"])
            age_days = max(0.0, (target - d).total_seconds() / 86400.0)
            if self.half_life_days is None:
                weight = 1.0
            else:
                weight = math.exp(-math.log(2.0) * age_days / self.half_life_days)
            trials += weight
            for n in set(int(x) for x in list(row["result"])[: self.number_predict]):
                if self.min_val <= n <= self.max_val:
                    hits[n] += weight

        posterior = {
            n: (alpha0 + hits[n]) / (alpha0 + beta0 + trials)
            for n in range(self.min_val, self.max_val + 1)
        }
        result = sorted(posterior, key=lambda n: (-posterior[n], n))[: self.number_predict]
        self._cache[target_date] = result
        return list(result)
