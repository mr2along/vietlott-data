"""Position-wise ensemble for ordered Power 6/55 main numbers.

Each slot is modeled only from the same sorted slot in historical draws. The
six marginal distributions are then decoded jointly into a strictly increasing
ticket. This is a descriptive statistical model, not evidence that lottery
outcomes are predictable.
"""

from __future__ import annotations

import math
from collections import Counter
from datetime import date
from typing import Any

import pandas as pd

from .base import PredictModel


class PositionWiseEnsembleStrategy(PredictModel):
    """Forecast each sorted position from that same position in prior draws.

    A per-position score blends long-run frequency, exponential decay, and
    recent-draw frequency. Each component is smoothed toward the exact
    order-statistic distribution implied by uniformly choosing six distinct
    values from the configured number range. A dynamic program selects the
    valid increasing sequence with the greatest sum of log marginal scores.
    """

    COMPONENT_WEIGHTS = {
        "long_term": 0.25,
        "exponential_decay": 0.50,
        "recent": 0.25,
    }

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        decay_half_life_days: float = 180.0,
        prior_strength: float = 30.0,
        recent_draws: int = 120,
    ) -> None:
        super().__init__(df, time_predict)
        if decay_half_life_days <= 0:
            raise ValueError("decay_half_life_days must be > 0")
        if prior_strength <= 0:
            raise ValueError("prior_strength must be > 0")
        if recent_draws < 1:
            raise ValueError("recent_draws must be >= 1")

        self.decay_half_life_days = float(decay_half_life_days)
        self.prior_strength = float(prior_strength)
        self.recent_draws = int(recent_draws)
        self._history_rows: list[dict[str, Any]] = []
        for _, row in df.iterrows():
            try:
                draw_date = pd.Timestamp(row["date"]).date()
                main = sorted(int(value) for value in list(row["result"])[: self.number_predict])
            except (KeyError, TypeError, ValueError):
                continue
            if (
                len(main) != self.number_predict
                or len(set(main)) != self.number_predict
                or any(value < self.min_val or value > self.max_val for value in main)
            ):
                continue
            self._history_rows.append({"date": draw_date, "main": main})
        self._history_rows.sort(key=lambda item: item["date"])
        self._score_cache: dict[date, list[dict[int, float]]] = {}
        self._prediction_cache: dict[date, list[int]] = {}

    def _position_candidates(self, position: int) -> range:
        """Return values feasible at this zero-based sorted position."""
        min_value = self.min_val + position
        max_value = self.max_val - (self.number_predict - 1 - position)
        return range(min_value, max_value + 1)

    def _theoretical_prior(self, position: int) -> dict[int, float]:
        """Order-statistic probabilities under a uniform six-of-N draw."""
        candidate_count = self.max_val - self.min_val + 1
        denominator = math.comb(candidate_count, self.number_predict)
        prior: dict[int, float] = {}
        for number in self._position_candidates(position):
            lower_choices = math.comb(number - self.min_val, position)
            upper_choices = math.comb(
                self.max_val - number,
                self.number_predict - 1 - position,
            )
            prior[number] = (lower_choices * upper_choices) / denominator
        return prior

    def _smoothed_distribution(
        self,
        counts: Counter[int] | dict[int, float],
        observed_mass: float,
        prior: dict[int, float],
    ) -> dict[int, float]:
        denominator = observed_mass + self.prior_strength
        if denominator <= 0:
            return dict(prior)
        return {
            number: (float(counts.get(number, 0.0)) + self.prior_strength * prior[number])
            / denominator
            for number in prior
        }

    def score_positions(self, target_date: date) -> list[dict[int, float]]:
        """Return a probability-like score distribution for each sorted slot."""
        target = pd.Timestamp(target_date).date()
        if target in self._score_cache:
            return [dict(scores) for scores in self._score_cache[target]]

        history = [row for row in self._history_rows if row["date"] < target]
        recent = history[-self.recent_draws :]
        decay_lambda = math.log(2.0) / self.decay_half_life_days
        weights = [
            math.exp(-decay_lambda * max(0, (target - row["date"]).days))
            for row in history
        ]
        weighted_mass = sum(weights)
        distributions: list[dict[int, float]] = []

        for position in range(self.number_predict):
            prior = self._theoretical_prior(position)
            long_counts: Counter[int] = Counter(row["main"][position] for row in history)
            recent_counts: Counter[int] = Counter(row["main"][position] for row in recent)
            decay_counts: Counter[int] = Counter()
            for row, weight in zip(history, weights):
                decay_counts[row["main"][position]] += weight

            long_term = self._smoothed_distribution(long_counts, float(len(history)), prior)
            decayed = self._smoothed_distribution(decay_counts, weighted_mass, prior)
            recent_distribution = self._smoothed_distribution(
                recent_counts, float(len(recent)), prior
            )
            scores = {
                number: (
                    self.COMPONENT_WEIGHTS["long_term"] * long_term[number]
                    + self.COMPONENT_WEIGHTS["exponential_decay"] * decayed[number]
                    + self.COMPONENT_WEIGHTS["recent"] * recent_distribution[number]
                )
                for number in prior
            }
            total = sum(scores.values())
            distributions.append({number: score / total for number, score in scores.items()})

        self._score_cache[target] = distributions
        return [dict(scores) for scores in distributions]

    @staticmethod
    def _prefer_path(
        left: tuple[float, tuple[int, ...]],
        right: tuple[float, tuple[int, ...]],
    ) -> tuple[float, tuple[int, ...]]:
        """Choose higher score, then lexicographically smaller path on ties."""
        if left[0] > right[0] + 1e-15:
            return left
        if right[0] > left[0] + 1e-15:
            return right
        return left if left[1] < right[1] else right

    def _best_increasing_sequence(self, distributions: list[dict[int, float]]) -> list[int]:
        """Maximize summed log scores while enforcing unique increasing values."""
        previous: dict[int, tuple[float, tuple[int, ...]]] = {}
        for position, scores in enumerate(distributions):
            current: dict[int, tuple[float, tuple[int, ...]]] = {}
            for number in sorted(scores):
                log_score = math.log(max(float(scores[number]), 1e-300))
                if position == 0:
                    current[number] = (log_score, (number,))
                    continue

                best_prior: tuple[float, tuple[int, ...]] | None = None
                for previous_number, path_score in previous.items():
                    if previous_number >= number:
                        continue
                    best_prior = (
                        path_score if best_prior is None
                        else self._prefer_path(best_prior, path_score)
                    )
                if best_prior is not None:
                    current[number] = (best_prior[0] + log_score, best_prior[1] + (number,))
            if not current:
                raise RuntimeError(
                    f"Unable to construct an increasing sequence at position {position + 1}"
                )
            previous = current

        best: tuple[float, tuple[int, ...]] | None = None
        for candidate in previous.values():
            best = candidate if best is None else self._prefer_path(best, candidate)
        if best is None or len(best[1]) != self.number_predict:
            raise RuntimeError("Position-wise decoder failed to produce six numbers")
        return list(best[1])

    def component_predictions(self, target_date: date) -> dict[str, Any]:
        """Forecast all six ordered slots with separate historical model components.

        The Bayesian component uses long-run slot counts with the theoretical
        order-statistic prior; the decay component uses exponentially weighted
        slot counts; the recent component uses the last N draws. Each component
        is decoded independently into a valid increasing six-number sequence.
        """
        target = pd.Timestamp(target_date).date()
        history = [row for row in self._history_rows if row["date"] < target]
        recent = history[-self.recent_draws :]
        decay_lambda = math.log(2.0) / self.decay_half_life_days
        weights = [
            math.exp(-decay_lambda * max(0, (target - row["date"]).days))
            for row in history
        ]
        weighted_mass = sum(weights)
        component_distributions: dict[str, list[dict[int, float]]] = {
            "PositionWiseBayesian": [],
            "PositionWiseExponentialDecay": [],
            "PositionWiseRecent": [],
        }

        for position in range(self.number_predict):
            prior = self._theoretical_prior(position)
            long_counts: Counter[int] = Counter(row["main"][position] for row in history)
            recent_counts: Counter[int] = Counter(row["main"][position] for row in recent)
            decay_counts: Counter[int] = Counter()
            for row, weight in zip(history, weights):
                decay_counts[row["main"][position]] += weight

            component_distributions["PositionWiseBayesian"].append(
                self._smoothed_distribution(long_counts, float(len(history)), prior)
            )
            component_distributions["PositionWiseExponentialDecay"].append(
                self._smoothed_distribution(decay_counts, weighted_mass, prior)
            )
            component_distributions["PositionWiseRecent"].append(
                self._smoothed_distribution(recent_counts, float(len(recent)), prior)
            )

        result: dict[str, Any] = {}
        for name, distributions in component_distributions.items():
            numbers = self._best_increasing_sequence(distributions)
            result[name] = {
                "predicted_numbers": numbers,
                "positions": [
                    {
                        "position": index + 1,
                        "selected_number": numbers[index],
                        "selected_score": round(float(distributions[index][numbers[index]]), 8),
                        "top_candidates": [
                            {"number": number, "score": round(float(distributions[index][number]), 8)}
                            for number in sorted(
                                distributions[index],
                                key=lambda value: (-distributions[index][value], value),
                            )[:5]
                        ],
                    }
                    for index in range(self.number_predict)
                ],
            }
        result["PositionWiseEnsemble"] = {
            "predicted_numbers": self.predict(target),
            "positions": self.position_details(target)["positions"],
        }
        return {
            "method": "Each component is fitted to the same sorted slot in historical draws; each ticket is decoded to six distinct ascending numbers.",
            "history_draws": len(history),
            "components": result,
        }

    def predict(self, target_date: date) -> list[int]:
        """Predict one number per historical sorted position."""
        target = pd.Timestamp(target_date).date()
        if target not in self._prediction_cache:
            self._prediction_cache[target] = self._best_increasing_sequence(
                self.score_positions(target)
            )
        return list(self._prediction_cache[target])

    def position_details(self, target_date: date) -> dict[str, Any]:
        """Return the final sequence plus ranked candidates for all six positions."""
        target = pd.Timestamp(target_date).date()
        prediction = self.predict(target)
        distributions = self.score_positions(target)
        history_count = sum(row["date"] < target for row in self._history_rows)
        positions: list[dict[str, Any]] = []

        for index, scores in enumerate(distributions):
            selected = prediction[index]
            ranked = sorted(scores, key=lambda number: (-scores[number], number))
            top = sorted(set(ranked[:5] + [selected]), key=lambda number: (-scores[number], number))
            positions.append(
                {
                    "position": index + 1,
                    "selected_number": selected,
                    "selected_score": round(float(scores[selected]), 8),
                    "history_draws": history_count,
                    "top_candidates": [
                        {"number": number, "score": round(float(scores[number]), 8)}
                        for number in top
                    ],
                }
            )

        return {
            "model": "PositionWiseEnsemble",
            "method": (
                "Each sorted position is scored only from the same position in prior draws; "
                "the six marginal scores are decoded jointly subject to strict ascending order."
            ),
            "history_draws": history_count,
            "decay_half_life_days": self.decay_half_life_days,
            "prior_strength": self.prior_strength,
            "recent_draws": self.recent_draws,
            "component_weights": dict(self.COMPONENT_WEIGHTS),
            "positions": positions,
            "predicted_numbers": prediction,
        }
