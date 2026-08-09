"""
Exponential-decay frequency strategy.

Historical observations are weighted by an exponential half-life. For Power
6/55 the seventh value is the special number, so only the first six main
numbers are used for scoring.
"""

import math
import random
from datetime import date
from typing import Dict, List

import numpy as np
import pandas as pd

from machine_learning.strategies.base import PredictModel


class ExponentialDecayStrategy(PredictModel):
    """Select numbers using exponentially-decaying main-number frequency."""

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        min_val: int = PredictModel.POWER_655_MIN_VAL,
        max_val: int = PredictModel.POWER_655_MAX_VAL,
        half_life_days: int = 90,
        hot: bool = True,
        selection_weight: float = 0.8,
    ):
        super().__init__(df, time_predict, min_val, max_val)
        self.half_life_days = half_life_days
        self.hot = hot
        self.selection_weight = selection_weight
        self._decay_lambda = math.log(2) / half_life_days
        self.df_sorted = self.df.sort_values("date").reset_index(drop=True)
        self._score_cache: Dict[date, Dict[int, float]] = {}

    def _compute_scores(self, target_date: date) -> Dict[int, float]:
        past = self.df_sorted[self.df_sorted["date"] < target_date].copy()
        scores: Dict[int, float] = {n: 0.0 for n in range(self.min_val, self.max_val + 1)}
        if past.empty:
            return scores

        past["_days_ago"] = past["date"].apply(lambda d: (target_date - d).days)
        past["_weight"] = np.exp(-self._decay_lambda * past["_days_ago"].to_numpy())

        exploded = past[["result", "_weight"]].copy()
        exploded["result"] = exploded["result"].apply(lambda xs: list(xs)[:6])
        exploded = exploded.explode("result").dropna(subset=["result"])
        exploded["result"] = exploded["result"].astype(int)
        grouped = exploded.groupby("result")["_weight"].sum()

        for num, score in grouped.items():
            if num in scores:
                scores[num] = float(score)
        return scores

    def predict(self, target_date: date) -> List[int]:
        if target_date not in self._score_cache:
            self._score_cache[target_date] = self._compute_scores(target_date)
        scores = self._score_cache[target_date]

        sorted_nums = sorted(scores.keys(), key=lambda n: (scores[n], -n), reverse=self.hot)

        # selection_weight=1.0 is the deterministic pure-decay mode used for
        # validation. The production/backtest default remains stochastic.
        if self.selection_weight >= 1.0:
            return sorted_nums[: self.number_predict]

        max_score = scores[sorted_nums[0]] if sorted_nums else 1.0
        weighted_pool: List[int] = []
        for num in sorted_nums:
            s = scores[num]
            w = max(1, round(s * 10)) if self.hot else max(1, round((max_score - s + 0.1) * 10))
            weighted_pool.extend([num] * w)

        freq_count = int(self.number_predict * self.selection_weight)
        random_count = self.number_predict - freq_count
        predicted: List[int] = []
        pool = weighted_pool[:]
        while len(predicted) < freq_count and pool:
            chosen = random.choice(pool)
            if chosen not in predicted:
                predicted.append(chosen)
            pool = [n for n in pool if n != chosen]

        available = [n for n in range(self.min_val, self.max_val + 1) if n not in predicted]
        predicted.extend(random.sample(available, min(random_count, len(available))))
        if len(predicted) < self.number_predict:
            predicted.extend(n for n in available if n not in predicted)
        return sorted(predicted[: self.number_predict])
