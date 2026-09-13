"""Rank-consensus ensemble for Power 6/55 candidate selection."""

from __future__ import annotations

from datetime import date
from typing import Dict, List

import pandas as pd

from .base import PredictModel
from .bayesian_probability import BayesianProbabilityStrategy
from .exponential_decay import ExponentialDecayStrategy
from .logistic_probability import LogisticProbabilityStrategy


class RankEnsembleStrategy(PredictModel):
    """Combine several deterministic selectors with weighted Borda scoring.

    Each component contributes points only to its six selected main numbers.
    The special number is never passed to the components as a feature.  The
    ensemble is a consensus benchmark, not a claim that lottery outcomes are
    predictable.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        weights: dict[str, float] | None = None,
    ) -> None:
        super().__init__(df, time_predict)
        self.weights = weights or {
            "Bayesian": 0.35,
            "ExponentialDecay": 0.35,
            "LogisticProbability": 0.30,
        }
        if any(float(v) < 0 for v in self.weights.values()):
            raise ValueError("ensemble weights must be non-negative")
        if sum(float(v) for v in self.weights.values()) <= 0:
            raise ValueError("at least one ensemble weight must be positive")

        self._cache: Dict[date, List[int]] = {}
        self._bayesian = BayesianProbabilityStrategy(
            df, time_predict=1, prior_strength=20.0, half_life_days=180.0
        )
        self._decay = ExponentialDecayStrategy(
            df, time_predict=1, half_life_days=730, hot=True, selection_weight=1.0
        )
        self._logistic = LogisticProbabilityStrategy(df, time_predict=1)

    def _components(self):
        return [
            ("Bayesian", self.weights.get("Bayesian", 0.0), self._bayesian),
            ("ExponentialDecay", self.weights.get("ExponentialDecay", 0.0), self._decay),
            ("LogisticProbability", self.weights.get("LogisticProbability", 0.0), self._logistic),
        ]

    def predict(self, target_date: date) -> List[int]:
        if target_date in self._cache:
            return list(self._cache[target_date])

        scores = {n: 0.0 for n in range(self.min_val, self.max_val + 1)}
        for _, weight, model in self._components():
            if weight <= 0:
                continue
            selected = [int(n) for n in model.predict(target_date)]
            for rank, number in enumerate(selected):
                if self.min_val <= number <= self.max_val:
                    scores[number] += float(weight) * (self.number_predict - rank)

        result = sorted(scores, key=lambda n: (-scores[n], n))[: self.number_predict]
        self._cache[target_date] = result
        return list(result)
