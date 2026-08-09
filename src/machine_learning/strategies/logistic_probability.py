"""Walk-forward logistic probability strategy for Power 6/55."""

from __future__ import annotations

from datetime import date
import math
from typing import Dict, List

import pandas as pd

from .base import PredictModel

try:
    from sklearn.linear_model import LogisticRegression
except ImportError:  # pragma: no cover - environment dependent
    LogisticRegression = None


class LogisticProbabilityStrategy(PredictModel):
    """Estimate per-number next-draw probabilities with logistic regression."""

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        lookback_draws: int = 180,
        windows: tuple[int, ...] = (10, 30, 90),
        C: float = 0.25,
        random_state: int = 42,
    ) -> None:
        super().__init__(df, time_predict)
        self.lookback_draws = int(lookback_draws)
        self.windows = tuple(sorted(set(int(w) for w in windows if w > 0)))
        self.C = float(C)
        self.random_state = int(random_state)
        self._cache: Dict[str, List[float]] = {}

    @staticmethod
    def _draw_sets(hist: pd.DataFrame) -> list[set[int]]:
        return [set(int(x) for x in row["result"][:6]) for _, row in hist.iterrows()]

    def _features_for_number(self, draw_sets: list[set[int]], index: int, number: int) -> list[float]:
        prior = draw_sets[:index]
        if not prior:
            return [0.0] * (len(self.windows) + 2)

        feats: list[float] = []
        for w in self.windows:
            sample = prior[-w:]
            feats.append(sum(number in s for s in sample) / len(sample))

        ewma = 0.0
        decay = math.exp(-math.log(2.0) / 30.0)
        weight = 1.0
        total_weight = 0.0
        for s in reversed(prior):
            ewma += weight * (1.0 if number in s else 0.0)
            total_weight += weight
            weight *= decay
        feats.append(ewma / total_weight if total_weight else 0.0)

        gap = 0
        for s in reversed(prior):
            if number in s:
                break
            gap += 1
        feats.append(min(gap, 100) / 100.0)
        return feats

    def _fit_probabilities(self, target_date: date) -> list[float]:
        key = str(pd.Timestamp(target_date).date())
        if key in self._cache:
            return self._cache[key]
        if LogisticRegression is None:
            raise ImportError("scikit-learn is required for LogisticProbabilityStrategy")

        target = pd.Timestamp(target_date)
        dates = pd.to_datetime(self.df["date"])
        hist = self.df.loc[dates < target].copy().sort_values("date")
        hist["date"] = pd.to_datetime(hist["date"])
        if self.lookback_draws > 0:
            hist = hist.tail(self.lookback_draws)
        draw_sets = self._draw_sets(hist)

        X: list[list[float]] = []
        y: list[int] = []
        for i in range(1, len(draw_sets)):
            for number in range(self.min_val, self.max_val + 1):
                X.append(self._features_for_number(draw_sets, i, number))
                y.append(1 if number in draw_sets[i] else 0)

        if not X or len(set(y)) < 2:
            probs = [6.0 / 55.0] * 55
            self._cache[key] = probs
            return probs

        model = LogisticRegression(
            C=self.C,
            solver="liblinear",
            max_iter=300,
            random_state=self.random_state,
        )
        model.fit(X, y)

        probs: list[float] = []
        for number in range(self.min_val, self.max_val + 1):
            x = self._features_for_number(draw_sets, len(draw_sets), number)
            probs.append(float(model.predict_proba([x])[0, 1]))
        self._cache[key] = probs
        return probs

    def predict(self, target_date: date) -> list[int]:
        probs = self._fit_probabilities(target_date)
        ranked = sorted(
            range(self.min_val, self.max_val + 1),
            key=lambda n: (-probs[n - self.min_val], n),
        )
        return sorted(ranked[: self.number_predict])
