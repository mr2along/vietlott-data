"""Unseen-combination strategy driven by overdue numbers.

The model targets *sets* that have not appeared before, rather than only
ranking individual numbers.  It combines draw-level absence (gap) with an
explicit exact-combination exclusion so that a predicted 6-number set is not
one of the historical 6-number sets seen before the target date.
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

    Numbers are ranked by draws since their most recent appearance.  A pool
    of the most overdue numbers is then used to generate a 6-number ticket.
    Historical exact 6-number combinations are rejected.

    This is deliberately a portfolio-style model: the individual number gap
    is only the building block; the final prediction is a *combination*.
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
        self.candidate_pool_size = min(candidate_pool_size, max_val - min_val + 1)
        self.max_attempts = max_attempts
        self._cache: dict[date, tuple[list[int], dict[int, float], set[tuple[int, ...]]]] = {}

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

        # Gap scoring is based only on the six main numbers; the 7th special
        # number must never influence which main numbers are considered overdue.
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
        return self._cache[target_date]

    @staticmethod
    def _weighted_sample(pool: list[int], scores: dict[int, float]) -> List[int]:
        available = pool[:]
        selected: list[int] = []
        # Convert the gap into a stable, bounded weight. Infinite gap gets max.
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

        for _ in range(self.max_attempts):
            ticket = tuple(self._weighted_sample(candidate_pool, gaps))
            if ticket not in seen_sets and len(ticket) == self.number_predict:
                return list(ticket)

        # Deterministic fallback: inspect combinations in ranked order and
        # choose the highest-gap unseen set.
        for ticket in combinations(candidate_pool, self.number_predict):
            key = tuple(sorted(ticket))
            if key not in seen_sets:
                return list(key)

        # Extremely defensive fallback for a saturated candidate pool.
        return sorted(candidate_pool[: self.number_predict])
