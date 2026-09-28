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
        decay_half_life_days: int = 730,
        consensus_discount: float = 0.25,
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
        if int(decay_half_life_days) <= 0:
            raise ValueError("decay_half_life_days must be > 0")
        if not 0.0 <= float(consensus_discount) <= 1.0:
            raise ValueError("consensus_discount must be between 0 and 1")
        self.decay_half_life_days = int(decay_half_life_days)
        self.consensus_discount = float(consensus_discount)

        self._cache: Dict[date, List[int]] = {}
        self._bayesian = BayesianProbabilityStrategy(
            df, time_predict=1, prior_strength=20.0, half_life_days=180.0
        )
        self._decay = ExponentialDecayStrategy(
            df, time_predict=1, half_life_days=self.decay_half_life_days, hot=True, selection_weight=1.0
        )
        self._logistic = LogisticProbabilityStrategy(df, time_predict=1)

    def _components(self):
        return [
            ("Bayesian", self.weights.get("Bayesian", 0.0), self._bayesian),
            ("ExponentialDecay", self.weights.get("ExponentialDecay", 0.0), self._decay),
            ("LogisticProbability", self.weights.get("LogisticProbability", 0.0), self._logistic),
        ]

    def _aggregate_contributions(
        self, contributions: dict[int, list[float]]
    ) -> dict[int, float]:
        """Aggregate correlated model evidence with diminishing consensus returns."""
        scores = {n: 0.0 for n in range(self.min_val, self.max_val + 1)}
        for number, values in contributions.items():
            if not values:
                continue
            ordered = sorted((float(value) for value in values), reverse=True)
            scores[number] = ordered[0] + self.consensus_discount * sum(ordered[1:])
        return scores

    def _scores(self, target_date: date) -> dict[int, float]:
        contributions: dict[int, list[float]] = {
            n: [] for n in range(self.min_val, self.max_val + 1)
        }
        for _, weight, model in self._components():
            if weight <= 0:
                continue
            selected = [int(n) for n in model.predict(target_date)]
            for rank, number in enumerate(selected):
                if self.min_val <= number <= self.max_val:
                    contributions[number].append(
                        float(weight) * (self.number_predict - rank)
                    )
        return self._aggregate_contributions(contributions)

    def predict(self, target_date: date) -> List[int]:
        if target_date in self._cache:
            return list(self._cache[target_date])

        scores = self._scores(target_date)
        result = sorted(scores, key=lambda n: (-scores[n], n))[: self.number_predict]
        self._cache[target_date] = result
        return list(result)
