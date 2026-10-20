"""Polynomial-trend challenger for position-wise Power 6/55 forecasts.

Fits degree-2 trends to block-level frequencies for each sorted slot/number,
then blends the extrapolated scores with the theoretical order-statistic prior.
Every prediction filters history to draws strictly before its target date.
This is an experimental challenger, not a claim that lottery outcomes are predictable.
"""
from __future__ import annotations

import math
from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from .base import PredictModel


class PositionWisePolynomialStrategy(PredictModel):
    """Degree-2 block-frequency extrapolation for each sorted number position."""

    BLOCK_SIZE = 25
    MAX_BLOCKS = 12
    PRIOR_WEIGHT = 0.5

    def __init__(self, df: pd.DataFrame, time_predict: int = 1):
        super().__init__(df, time_predict)
        self._rows: list[dict[str, Any]] = []
        for _, row in df.iterrows():
            try:
                draw_date = pd.Timestamp(row["date"]).date()
                main = sorted(int(value) for value in list(row["result"])[:6])
            except (KeyError, TypeError, ValueError):
                continue
            if len(main) == 6 and len(set(main)) == 6 and all(1 <= n <= 55 for n in main):
                self._rows.append({"date": draw_date, "main": main})
        self._rows.sort(key=lambda item: item["date"])
        self._cache: dict[date, list[int]] = {}

    def _prior(self, position: int, candidates: range) -> np.ndarray:
        denominator = math.comb(55, 6)
        values = []
        for number in candidates:
            lower = math.comb(number - 1, position)
            upper = math.comb(55 - number, 5 - position)
            values.append((lower * upper) / denominator)
        prior = np.asarray(values, dtype=float)
        return prior / prior.sum()

    @staticmethod
    def _best_increasing_sequence(distributions: list[dict[int, float]]) -> list[int]:
        # Dynamic programming maximizes summed log scores while enforcing 6 unique
        # increasing numbers. Deterministic tie-breaking favors smaller numbers.
        states: dict[int, tuple[float, tuple[int, ...]]] = {}
        for position, distribution in enumerate(distributions):
            next_states: dict[int, tuple[float, tuple[int, ...]]] = {}
            for number in sorted(distribution):
                score = math.log(max(distribution[number], 1e-300))
                if position == 0:
                    next_states[number] = (score, (number,))
                    continue
                prior_states = [state for previous, state in states.items() if previous < number]
                if not prior_states:
                    continue
                best = min(prior_states, key=lambda state: (-state[0], state[1]))
                next_states[number] = (best[0] + score, best[1] + (number,))
            states = next_states
        if not states:
            raise RuntimeError("Polynomial model could not decode a valid ticket")
        return list(min(states.values(), key=lambda state: (-state[0], state[1]))[1])

    def predict(self, target_date: date) -> list[int]:
        target = pd.Timestamp(target_date).date()
        if target in self._cache:
            return list(self._cache[target])
        history = [row for row in self._rows if row["date"] < target]
        if len(history) < 3 * self.BLOCK_SIZE:
            # Insufficient blocks for a stable quadratic fit: return a valid
            # deterministic ticket from the theoretical order-statistic prior.
            prediction = [5, 14, 23, 33, 42, 51]
            self._cache[target] = prediction
            return list(prediction)

        history = history[-self.BLOCK_SIZE * self.MAX_BLOCKS:]
        blocks = [
            history[start:start + self.BLOCK_SIZE]
            for start in range(0, len(history), self.BLOCK_SIZE)
        ]
        distributions: list[dict[int, float]] = []
        x = np.arange(len(blocks), dtype=float)
        x_center = max(1.0, float(len(blocks) - 1))
        x_scaled = x / x_center
        target_x = float(len(blocks)) / x_center

        for position in range(6):
            candidates = range(position + 1, 56 - (5 - position))
            candidate_list = list(candidates)
            frequencies = np.zeros((len(blocks), len(candidate_list)), dtype=float)
            lookup = {number: index for index, number in enumerate(candidate_list)}
            for block_index, block in enumerate(blocks):
                for row in block:
                    number = row["main"][position]
                    if number in lookup:
                        frequencies[block_index, lookup[number]] += 1.0 / len(block)
            degree = min(2, len(blocks) - 1)
            design = np.vander(x_scaled, N=degree + 1, increasing=True)
            coefficients, *_ = np.linalg.lstsq(design, frequencies, rcond=None)
            target_design = np.asarray([target_x ** power for power in range(degree + 1)])
            extrapolated = target_design @ coefficients
            extrapolated = np.clip(extrapolated, 0.0, None)
            if float(extrapolated.sum()) <= 1e-12:
                trend = self._prior(position, candidates)
            else:
                trend = extrapolated / extrapolated.sum()
            prior = self._prior(position, candidates)
            scores = self.PRIOR_WEIGHT * prior + (1.0 - self.PRIOR_WEIGHT) * trend
            scores = scores / scores.sum()
            distributions.append({number: float(scores[index]) for index, number in enumerate(candidate_list)})

        prediction = self._best_increasing_sequence(distributions)
        self._cache[target] = prediction
        return list(prediction)
