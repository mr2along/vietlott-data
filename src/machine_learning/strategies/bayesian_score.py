"""Bayesian-smoothed number scoring strategy.

This strategy estimates the per-number appearance probability using a
Beta-Binomial posterior.  A neutral Beta prior shrinks noisy frequencies
toward the global expected rate (6/55), reducing overreaction to small
samples.  Recency weighting is applied to observations before updating the
posterior, but the model never uses future draws.
"""

from __future__ import annotations

from datetime import date
import math
import random

import pandas as pd

from .base import PredictModel


class BayesianNumberScoreStrategy(PredictModel):
    """Select numbers using Beta-Binomial posterior mean scores.

    Parameters
    ----------
    lookback_days:
        Historical window used before each prediction date.
    prior_strength:
        Effective prior sample size.  The prior mean is 6/55.
    recency_half_life_days:
        Exponential half-life for historical observations.  ``None`` means
        no recency weighting.
    temperature:
        Controls how strongly posterior scores are converted into sampling
        weights.  1.0 is linear weighting.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 6,
        lookback_days: int = 365,
        prior_strength: float = 20.0,
        recency_half_life_days: float | None = 180.0,
        temperature: float = 1.0,
    ) -> None:
        super().__init__(df, time_predict)
        self.lookback_days = int(lookback_days)
        self.prior_strength = float(prior_strength)
        self.recency_half_life_days = recency_half_life_days
        self.temperature = float(temperature)

    def predict(self, target_date: date) -> list[int]:
        hist = self.df[self.df["date"] < pd.Timestamp(target_date)]
        if self.lookback_days > 0:
            cutoff = pd.Timestamp(target_date) - pd.Timedelta(days=self.lookback_days)
            hist = hist[hist["date"] >= cutoff]

        prior_mean = 6.0 / 55.0
        alpha0 = self.prior_strength * prior_mean
        beta0 = self.prior_strength * (1.0 - prior_mean)
        scores = {n: alpha0 / (alpha0 + beta0) for n in range(1, 56)}
        weighted_hits = {n: 0.0 for n in range(1, 56)}
        weighted_trials = {n: 0.0 for n in range(1, 56)}

        target = pd.Timestamp(target_date)
        for _, row in hist.iterrows():
            age = max(0.0, (target - pd.Timestamp(row["date"])).total_seconds() / 86400.0)
            if self.recency_half_life_days and self.recency_half_life_days > 0:
                w = math.exp(-math.log(2.0) * age / self.recency_half_life_days)
            else:
                w = 1.0
            nums = set(int(x) for x in row["result"][:6])
            for n in range(1, 56):
                weighted_trials[n] += w
                if n in nums:
                    weighted_hits[n] += w

        for n in range(1, 56):
            alpha = alpha0 + weighted_hits[n]
            beta = beta0 + weighted_trials[n] - weighted_hits[n]
            scores[n] = alpha / (alpha + beta)

        power = 1.0 / max(self.temperature, 1e-9)
        weights = [max(scores[n], 1e-12) ** power for n in range(1, 56)]
        chosen = random.choices(range(1, 56), weights=weights, k=self.time_predict * 4)
        result: list[int] = []
        for n in chosen:
            if n not in result:
                result.append(n)
            if len(result) == self.time_predict:
                break
        if len(result) < self.time_predict:
            remaining = [n for n in range(1, 56) if n not in result]
            result.extend(random.sample(remaining, self.time_predict - len(result)))
        return sorted(result)
