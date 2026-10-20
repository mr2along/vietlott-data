"""P-DOS: philosophy-inspired, falsifiable Power 6/55 challenger.

The mapping is an engineering convention, not a claim that Eastern philosophy
predicts lottery draws. Yin-Yang features summarize parity/low-high balance;
I-Ching-inspired states discretize the previous draw and estimate transitions;
Wu-Xing-inspired groups use a fixed modulo-5 partition. Scores are blended with
the theoretical order-statistic prior and decoded to six increasing numbers.
Only draws strictly before the target date are used.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import date
from typing import Any

import pandas as pd

from .base import PredictModel


class PDOSStrategy(PredictModel):
    """Philosophy-inspired feature model; research-only until validated."""

    PRIOR_STRENGTH = 30.0
    TRANSITION_WEIGHT = 0.20
    ELEMENT_WEIGHT = 0.10
    STATE_COUNT = 8

    def __init__(self, df: pd.DataFrame, time_predict: int = 1):
        super().__init__(df, time_predict)
        self._rows: list[dict[str, Any]] = []
        for _, row in df.iterrows():
            try:
                draw_date = pd.Timestamp(row["date"]).date()
                main = sorted(int(v) for v in list(row["result"])[:6])
            except (KeyError, TypeError, ValueError):
                continue
            if len(main) == 6 and len(set(main)) == 6 and all(1 <= n <= 55 for n in main):
                self._rows.append({"date": draw_date, "main": main})
        self._rows.sort(key=lambda item: item["date"])
        self._cache: dict[date, list[int]] = {}

    @staticmethod
    def _state(numbers: list[int]) -> int:
        """Eight deterministic states from yin/yang balance and total."""
        odd = sum(n % 2 for n in numbers)
        high = sum(n >= 28 for n in numbers)
        total = sum(numbers)
        parity_bit = int(odd >= 3)
        high_bit = int(high >= 3)
        total_bit = int(total >= 168)
        return (parity_bit << 2) | (high_bit << 1) | total_bit

    @staticmethod
    def _element(number: int) -> int:
        """Fixed five-group partition; zero-based modulo is documented convention."""
        return (number - 1) % 5

    def _prior(self, position: int) -> dict[int, float]:
        denominator = math.comb(55, 6)
        low = position
        high = 5 - position
        candidates = range(position + 1, 56 - (5 - position))
        return {
            n: math.comb(n - 1, low) * math.comb(55 - n, high) / denominator
            for n in candidates
        }

    @staticmethod
    def _decode(distributions: list[dict[int, float]]) -> list[int]:
        states: dict[int, tuple[float, tuple[int, ...]]] = {}
        for pos, scores in enumerate(distributions):
            current: dict[int, tuple[float, tuple[int, ...]]] = {}
            for number, probability in scores.items():
                value = math.log(max(probability, 1e-300))
                if pos == 0:
                    current[number] = (value, (number,))
                    continue
                eligible = [v for n, v in states.items() if n < number]
                if eligible:
                    best = min(eligible, key=lambda v: (-v[0], v[1]))
                    current[number] = (best[0] + value, best[1] + (number,))
            states = current
        if not states:
            raise RuntimeError("P-DOS could not decode valid ticket")
        return list(min(states.values(), key=lambda v: (-v[0], v[1]))[1])

    def predict(self, target_date: date) -> list[int]:
        target = pd.Timestamp(target_date).date()
        if target in self._cache:
            return list(self._cache[target])
        history = [r for r in self._rows if r["date"] < target]
        if len(history) < 30:
            # The order-statistic prior is the only supported information at warm-up.
            result = [5, 14, 23, 33, 42, 51]
            self._cache[target] = result
            return list(result)

        prior_distributions = [self._prior(pos) for pos in range(6)]
        slot_counts = [Counter(row["main"][pos] for row in history) for pos in range(6)]
        previous_states = [self._state(row["main"]) for row in history]
        state_counts: dict[int, Counter[int]] = defaultdict(Counter)
        transitions: dict[int, Counter[int]] = defaultdict(Counter)
        for index, row in enumerate(history):
            state = previous_states[index]
            for number in row["main"]:
                state_counts[state][number] += 1
            if index:
                transitions[previous_states[index - 1]][state] += 1

        current_state = previous_states[-1]
        next_state_counts = transitions[current_state]
        state_total = sum(next_state_counts.values())
        next_state_prob = {
            state: (next_state_counts[state] + 1.0) / (state_total + self.STATE_COUNT)
            for state in range(self.STATE_COUNT)
        }
        # Expected next-state-conditioned number propensity, with Laplace smoothing.
        state_number_scores: Counter[int] = Counter()
        for state, state_probability in next_state_prob.items():
            total = sum(state_counts[state].values())
            for number in range(1, 56):
                state_number_scores[number] += state_probability * (
                    (state_counts[state][number] + 1.0) / (total + 55.0)
                )

        element_counts = Counter(self._element(n) for row in history for n in row["main"])
        element_total = sum(element_counts.values())
        element_prob = {
            element: (element_counts[element] + 1.0) / (element_total + 5.0)
            for element in range(5)
        }

        distributions: list[dict[int, float]] = []
        for position, prior in enumerate(prior_distributions):
            total = len(history)
            smoothed = {
                n: (slot_counts[position][n] + self.PRIOR_STRENGTH * prior[n])
                / (total + self.PRIOR_STRENGTH)
                for n in prior
            }
            raw = {}
            for n in prior:
                state_score = state_number_scores[n]
                element_score = element_prob[self._element(n)] * 55.0 / 6.0
                raw[n] = smoothed[n] * (
                    (1.0 - self.TRANSITION_WEIGHT - self.ELEMENT_WEIGHT)
                    + self.TRANSITION_WEIGHT * state_score * 55.0
                    + self.ELEMENT_WEIGHT * element_score
                )
            norm = sum(raw.values())
            distributions.append({n: score / norm for n, score in raw.items()})
        result = self._decode(distributions)
        self._cache[target] = result
        return list(result)
