"""Unseen-combination strategy driven by overdue numbers.

The model targets *sets* that have not appeared before, rather than only
ranking individual numbers. It combines draw-level absence (gap) with an
explicit exact-combination exclusion and avoids duplicate tickets within the
same target-draw portfolio.
"""

from __future__ import annotations

import math
import random
from datetime import date
from itertools import combinations
from typing import List

import pandas as pd

from machine_learning.strategies.base import PredictModel


class UnseenSetGapStrategy(PredictModel):
    """Predict previously unseen 6-number sets built from overdue numbers.

    Numbers are ranked by days since their most recent appearance. A pool of
    the most overdue numbers is then used to generate tickets. Historical
    exact 6-number combinations are rejected, and repeated tickets are avoided
    when ``predict()`` is called multiple times for one target draw.

    This is deliberately a portfolio-style model: individual number gap is
    the building block, while the final prediction is a 6-number combination.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        min_val: int = PredictModel.POWER_655_MIN_VAL,
        max_val: int = PredictModel.POWER_655_MAX_VAL,
        candidate_pool_size: int = 18,
        max_attempts: int = 200,
    ):
        super().__init__(df, time_predict, min_val, max_val)
        if candidate_pool_size < self.number_predict:
            raise ValueError("candidate_pool_size must be >= number_predict")
        if max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")
        self.candidate_pool_size = min(candidate_pool_size, max_val - min_val + 1)
        self.max_attempts = max_attempts
        self._cache: dict[date, tuple[list[int], dict[int, float], set[tuple[int, ...]]]] = {}
        self._issued: dict[date, set[tuple[int, ...]]] = {}

    def _prepare(self, target_date: date):
        if target_date in self._cache:
            return self._cache[target_date]

        past = self.df[self.df["date"] < target_date].sort_values("date")
        all_numbers = list(range(self.min_val, self.max_val + 1))

        seen_sets: set[tuple[int, ...]] = set()
        rows_for_gap: list[dict[str, object]] = []
        for row in past[["date", "result"]].itertuples(index=False):
            main = tuple(sorted(int(x) for x in list(row.result)[: self.number_predict]))
            if len(main) != self.number_predict or len(set(main)) != self.number_predict:
                continue
            seen_sets.add(main)
            rows_for_gap.append({"date": row.date, "result": list(main)})

        # Gap scoring uses only the six main numbers; the 7th special number
        # must never influence the overdue ranking.
        if rows_for_gap:
            gap_df = pd.DataFrame(rows_for_gap).explode("result")
            gap_df["result"] = gap_df["result"].astype(int)
            last_dates = gap_df.groupby("result")["date"].max().to_dict()
        else:
            last_dates = {}

        gaps: dict[int, float] = {}
        for n in all_numbers:
            d = last_dates.get(n)
            gaps[n] = float("inf") if d is None else float((target_date - d).days)

        ranked = sorted(all_numbers, key=lambda n: (-gaps[n], n))
        candidate_pool = ranked[: self.candidate_pool_size]
        self._cache[target_date] = (candidate_pool, gaps, seen_sets)
        self._issued.setdefault(target_date, set())
        return self._cache[target_date]

    @staticmethod
    def _weighted_sample(pool: list[int], scores: dict[int, float]) -> List[int]:
        available = pool[:]
        selected: list[int] = []
        finite = [v for v in scores.values() if math.isfinite(v)]
        cap = max(finite, default=1.0)
        for _ in range(min(6, len(available))):
            weights = [
                (cap + 1.0) if not math.isfinite(scores[n]) else (1.0 + max(scores[n], 0.0))
                for n in available
            ]
            chosen = random.choices(available, weights=weights, k=1)[0]
            selected.append(chosen)
            available.remove(chosen)
        return sorted(selected)

    def predict(self, target_date: date) -> List[int]:
        candidate_pool, gaps, seen_sets = self._prepare(target_date)
        issued = self._issued.setdefault(target_date, set())

        for _ in range(self.max_attempts):
            ticket = tuple(self._weighted_sample(candidate_pool, gaps))
            if (
                len(ticket) == self.number_predict
                and ticket not in seen_sets
                and ticket not in issued
            ):
                issued.add(ticket)
                return list(ticket)

        # Deterministic fallback: choose the highest-gap unseen ticket that has
        # not already been issued for this target draw.
        for ticket in combinations(candidate_pool, self.number_predict):
            key = tuple(sorted(ticket))
            if key not in seen_sets and key not in issued:
                issued.add(key)
                return list(key)

        # If the candidate pool becomes saturated, a previously unseen ticket
        # may not exist. Keep the API contract by returning the highest-gap
        # valid ticket; duplicates are allowed only in this pathological case.
        fallback = tuple(sorted(candidate_pool[: self.number_predict]))
        issued.add(fallback)
        return list(fallback)
