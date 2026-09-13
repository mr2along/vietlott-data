"""Leakage-safe logistic probability strategy for Power 6/55."""

from __future__ import annotations

from datetime import date
from typing import Dict, List

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .base import PredictModel


class LogisticProbabilityStrategy(PredictModel):
    """Estimate per-number next-draw probability with logistic regression."""

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        windows: tuple[int, ...] = (10, 30, 90, 365),
        min_training_rows: int = 30,
    ) -> None:
        super().__init__(df, time_predict)
        self.windows = tuple(int(x) for x in windows if int(x) > 0)
        if not self.windows:
            raise ValueError("windows must not be empty")
        self.min_training_rows = int(min_training_rows)
        self._cache: Dict[date, List[int]] = {}

    def _feature_row(self, history: pd.DataFrame, target_date: date) -> list[float]:
        target = pd.Timestamp(target_date)
        row_features: list[float] = []
        for window in self.windows:
            cutoff = target - pd.Timedelta(days=window)
            sample = history[history["date"] >= cutoff]
            row_features.append(float(sum(int(n) in set(map(int, list(r)[:6])) for n in sample["result"] for _ in [0])))
        # Recent-draw occurrence and current gap in draws.
        recent = history.tail(5)
        row_features.append(float(sum(int(n) in set(map(int, list(r)[:6])) for r in recent["result"] for n in [0])))
        return row_features

    def _number_features(self, history: pd.DataFrame, number: int, target_date: date) -> list[float]:
        target = pd.Timestamp(target_date)
        features: list[float] = []
        sets = [set(map(int, list(r)[:6])) for r in history["result"]]
        dates = list(history["date"])
        for window in self.windows:
            cutoff = target - pd.Timedelta(days=window)
            features.append(float(sum(number in s for s, d in zip(sets, dates) if d >= cutoff)))
        last5 = sets[-5:]
        features.append(float(sum(number in s for s in last5)))
        gap = len(history)
        for i in range(len(sets) - 1, -1, -1):
            if number in sets[i]:
                gap = len(sets) - 1 - i
                break
        features.append(float(gap))
        return features

    def predict(self, target_date: date) -> List[int]:
        if target_date in self._cache:
            return list(self._cache[target_date])

        history = self.df[self.df["date"] < target_date].sort_values("date").reset_index(drop=True)
        if len(history) < self.min_training_rows:
            result = list(range(self.min_val, self.min_val + self.number_predict))
            self._cache[target_date] = result
            return result

        X: list[list[float]] = []
        y: list[int] = []
        dates = history["date"].tolist()
        for i in range(self.min_training_rows, len(history)):
            prior = history.iloc[:i]
            actual = set(int(x) for x in list(history.iloc[i]["result"])[:6])
            train_date = dates[i]
            for number in range(self.min_val, self.max_val + 1):
                X.append(self._number_features(prior, number, train_date))
                y.append(int(number in actual))

        if len(set(y)) < 2:
            result = list(range(self.min_val, self.min_val + self.number_predict))
            self._cache[target_date] = result
            return result

        model = Pipeline([
            ("scale", StandardScaler()),
            ("logit", LogisticRegression(max_iter=500, class_weight="balanced")),
        ])
        model.fit(X, y)
        current_X = [self._number_features(history, n, target_date) for n in range(self.min_val, self.max_val + 1)]
        probabilities = model.predict_proba(current_X)[:, 1]
        ranking = sorted(
            zip(range(self.min_val, self.max_val + 1), probabilities),
            key=lambda item: (-float(item[1]), item[0]),
        )
        result = [n for n, _ in ranking[: self.number_predict]]
        self._cache[target_date] = result
        return list(result)
