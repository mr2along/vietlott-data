"""Exponential-decay frequency strategy."""
from __future__ import annotations
import math, random
from datetime import date
from typing import Dict, List
import numpy as np
import pandas as pd
from machine_learning.strategies.base import PredictModel

class ExponentialDecayStrategy(PredictModel):
    """Recency-weighted score over the six main Power 6/55 numbers."""
    def __init__(self, df: pd.DataFrame, time_predict: int = 1,
                 min_val: int = PredictModel.POWER_655_MIN_VAL,
                 max_val: int = PredictModel.POWER_655_MAX_VAL,
                 half_life_days: int = 90, hot: bool = True,
                 selection_weight: float = 0.8):
        super().__init__(df, time_predict, min_val, max_val)
        if half_life_days <= 0 or not 0 <= selection_weight <= 1:
            raise ValueError("invalid decay parameters")
        self.half_life_days, self.hot, self.selection_weight = half_life_days, hot, selection_weight
        self._decay_lambda = math.log(2) / half_life_days
        self.df_sorted = self.df.sort_values("date").reset_index(drop=True)
        self._score_cache: Dict[date, Dict[int, float]] = {}

    def _compute_scores(self, target_date: date) -> Dict[int, float]:
        past = self.df_sorted[self.df_sorted["date"] < target_date].copy()
        scores = {n: 0.0 for n in range(self.min_val, self.max_val + 1)}
        if past.empty: return scores
        past["_days_ago"] = past["date"].apply(lambda d: (target_date - d).days)
        past["_weight"] = np.exp(-self._decay_lambda * past["_days_ago"].to_numpy())
        x = past[["result", "_weight"]].copy()
        x["result"] = x["result"].apply(lambda xs: list(xs)[:6])
        x = x.explode("result").dropna(subset=["result"])
        x["result"] = x["result"].astype(int)
        for n, score in x.groupby("result")["_weight"].sum().items():
            if int(n) in scores: scores[int(n)] = float(score)
        return scores

    def predict(self, target_date: date) -> List[int]:
        if target_date not in self._score_cache:
            self._score_cache[target_date] = self._compute_scores(target_date)
        scores = self._score_cache[target_date]
        ordered = sorted(scores, key=lambda n: scores[n], reverse=self.hot)
        if self.selection_weight >= 1.0:
            return sorted(ordered[:self.number_predict])
        freq_count = int(self.number_predict * self.selection_weight)
        predicted = []
        pool = []
        max_score = scores[ordered[0]] if ordered else 1.0
        for n in ordered:
            s = scores[n]
            w = max(1, round(s * 10)) if self.hot else max(1, round((max_score - s + .1) * 10))
            pool.extend([n] * w)
        while len(predicted) < freq_count and pool:
            n = random.choice(pool)
            if n not in predicted: predicted.append(n)
            pool = [x for x in pool if x != n]
        available = [n for n in range(self.min_val, self.max_val + 1) if n not in predicted]
        predicted.extend(random.sample(available, self.number_predict - len(predicted)))
        return sorted(predicted)
