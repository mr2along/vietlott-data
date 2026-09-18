"""Leakage-safe online logistic probability strategy for Power 6/55."""

from __future__ import annotations

from datetime import date
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier

from .base import PredictModel


class LogisticProbabilityStrategy(PredictModel):
    """Incremental walk-forward logistic model over six main numbers."""

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        windows: tuple[int, ...] = (10, 30, 90, 365),
        min_training_rows: int = 30,
        random_state: int = 20260809,
    ) -> None:
        super().__init__(df, time_predict)
        self.windows = tuple(int(x) for x in windows if int(x) > 0)
        if not self.windows:
            raise ValueError("windows must not be empty")
        self.min_training_rows = int(min_training_rows)
        if self.min_training_rows < 1:
            raise ValueError("min_training_rows must be >= 1")
        self.random_state = int(random_state)
        self._cache: Dict[date, List[int]] = {}
        self._model: SGDClassifier | None = None
        # Row i is a supervised example whose features use only rows < i.
        # Start at row 1 so the first eligible target can train on every
        # available historical label from rows 1..target_index-1.
        self._trained_until = 1
        self._last_target: pd.Timestamp | None = None
        self._prepare_matrix()

    def _prepare_matrix(self) -> None:
        history = self.df.sort_values("date").reset_index(drop=True).copy()
        history["date"] = pd.to_datetime(history["date"]).dt.normalize()
        self._history = history
        self._dates = history["date"].to_numpy(dtype="datetime64[ns]")
        n = len(history)
        width = self.max_val - self.min_val + 1
        occurrence = np.zeros((n, width), dtype=np.float32)
        for i, value in enumerate(history["result"].tolist()):
            for raw in list(value)[: self.number_predict]:
                number = int(raw)
                if self.min_val <= number <= self.max_val:
                    occurrence[i, number - self.min_val] = 1.0
        self._occurrence = occurrence
        self._prefix = np.vstack(
            [np.zeros((1, width), dtype=np.float32), np.cumsum(occurrence, axis=0, dtype=np.float32)]
        )
        last_seen = np.full(width, -1, dtype=np.int32)
        self._last_seen_before = np.empty((n, width), dtype=np.int32)
        for i in range(n):
            self._last_seen_before[i] = last_seen
            last_seen[occurrence[i] > 0] = i
        self._last_seen_after = last_seen

    def _feature_matrix(self, index: int) -> np.ndarray:
        width = self.max_val - self.min_val + 1
        if index <= 0:
            return np.zeros((width, len(self.windows) + 2), dtype=np.float64)
        target = self._dates[index] if index < len(self._dates) else self._dates[-1] + np.timedelta64(1, "D")
        blocks: list[np.ndarray] = []
        for window in self.windows:
            cutoff = target - np.timedelta64(window, "D")
            start = int(np.searchsorted(self._dates, cutoff, side="left"))
            counts = self._prefix[index] - self._prefix[start]
            blocks.append(counts / float(max(1, index - start)))
        last5_start = max(0, index - 5)
        last5 = self._prefix[index] - self._prefix[last5_start]
        blocks.append(last5 / float(max(1, index - last5_start)))
        last_seen = self._last_seen_before[index] if index < len(self._last_seen_before) else self._last_seen_after
        gaps = np.where(last_seen >= 0, index - last_seen, index)
        blocks.append(gaps.astype(np.float64) / float(max(1, index)))
        return np.column_stack(blocks).astype(np.float64)

    def _new_model(self) -> SGDClassifier:
        return SGDClassifier(
            loss="log_loss",
            penalty="l2",
            alpha=1e-4,
            learning_rate="optimal",
            class_weight={0: 55.0 / (2.0 * 49.0), 1: 55.0 / (2.0 * 6.0)},
            max_iter=1,
            tol=None,
            random_state=self.random_state,
            average=True,
        )

    def _reset_model(self) -> None:
        self._model = None
        self._trained_until = 1

    def _advance_training(self, target_index: int) -> None:
        target_index = min(target_index, len(self._history))
        if target_index < self._trained_until:
            self._reset_model()

        for i in range(self._trained_until, target_index):
            if i <= 0 or i >= len(self._history):
                continue
            X = self._feature_matrix(i)
            y = self._occurrence[i].astype(np.int8)
            if self._model is None:
                self._model = self._new_model()
                self._model.partial_fit(X, y, classes=np.array([0, 1], dtype=np.int8))
            else:
                self._model.partial_fit(X, y)
            self._trained_until = i + 1

    def predict(self, target_date: date) -> List[int]:
        key = pd.Timestamp(target_date).date()
        if key in self._cache:
            return list(self._cache[key])

        target = pd.Timestamp(target_date).normalize()
        if self._last_target is not None and target < self._last_target:
            self._reset_model()

        target_index = int(np.searchsorted(self._dates, target.to_datetime64(), side="left"))
        if target_index < self.min_training_rows:
            result = list(range(self.min_val, self.min_val + self.number_predict))
            self._cache[key] = result
            self._last_target = target
            return list(result)

        self._advance_training(target_index)
        if self._model is None:
            result = list(range(self.min_val, self.min_val + self.number_predict))
            self._cache[key] = result
            self._last_target = target
            return list(result)

        probabilities = self._model.predict_proba(self._feature_matrix(target_index))[:, 1]
        ranking = sorted(
            zip(range(self.min_val, self.max_val + 1), probabilities),
            key=lambda item: (-float(item[1]), item[0]),
        )
        result = [n for n, _ in ranking[: self.number_predict]]
        self._cache[key] = result
        self._last_target = target
        return list(result)
