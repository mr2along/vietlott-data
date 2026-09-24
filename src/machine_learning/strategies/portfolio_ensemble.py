"""Score-first candidate selection and diversified portfolio construction for Power 6/55.

The implementation separates model ranking from portfolio coverage:
- top-ranked core candidates are protected;
- historical reservoirs add satellite candidates instead of replacing the core;
- portfolio exposure is score-weighted, not forced to be uniform;
- repeated pairs are penalized so 30 tickets cover the candidate pool more efficiently.

This module is a research component. Historical performance does not establish
future lottery predictability.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from itertools import combinations
from typing import Iterable

import pandas as pd

from .rank_ensemble import RankEnsembleStrategy


class PortfolioEnsembleStrategy(RankEnsembleStrategy):
    """Generate a deterministic score-first six-number portfolio."""

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        weights: dict[str, float] | None = None,
        tickets_per_draw: int = 30,
        candidate_pool_size: int = 24,
        usage_penalty: float = 0.35,
        max_number_usage: int | None = None,
        excluded_sets: set[tuple[int, ...]] | None = None,
        max_consecutive_run: int | None = None,
        coverage_rescue_size: int = 0,
        coverage_recent_draws: int = 20,
        coverage_long_draws: int = 180,
        coverage_repeat_weight: float = 0.20,
        ensemble_score_mode: str = "top6",
        exposure_power: float = 1.35,
        pair_reuse_penalty: float = 0.75,
    ) -> None:
        super().__init__(df, time_predict=time_predict, weights=weights)
        if tickets_per_draw <= 0:
            raise ValueError("tickets_per_draw must be > 0")
        if candidate_pool_size < self.number_predict:
            raise ValueError("candidate_pool_size must be at least 6")
        if candidate_pool_size > (self.max_val - self.min_val + 1):
            raise ValueError("candidate_pool_size exceeds number range")
        if usage_penalty < 0:
            raise ValueError("usage_penalty must be non-negative")
        if max_number_usage is not None:
            if max_number_usage < 1:
                raise ValueError("max_number_usage must be >= 1")
            capacity = int(max_number_usage) * int(candidate_pool_size)
            required = int(tickets_per_draw) * self.number_predict
            if capacity < required:
                raise ValueError(
                    "max_number_usage does not provide enough portfolio capacity"
                )
        if max_consecutive_run is not None and max_consecutive_run < 1:
            raise ValueError("max_consecutive_run must be >= 1")
        if not 0 <= coverage_rescue_size <= candidate_pool_size - self.number_predict:
            raise ValueError("coverage_rescue_size must leave room for six-number tickets")
        if coverage_recent_draws < 1 or coverage_long_draws < coverage_recent_draws:
            raise ValueError("coverage draw windows are invalid")
        if not 0 <= coverage_repeat_weight <= 1:
            raise ValueError("coverage_repeat_weight must be between 0 and 1")
        if ensemble_score_mode not in {"top6", "full_rank"}:
            raise ValueError("ensemble_score_mode must be 'top6' or 'full_rank'")
        if exposure_power <= 0:
            raise ValueError("exposure_power must be > 0")
        if pair_reuse_penalty < 0:
            raise ValueError("pair_reuse_penalty must be non-negative")

        self.tickets_per_draw = int(tickets_per_draw)
        self.candidate_pool_size = int(candidate_pool_size)
        self.usage_penalty = float(usage_penalty)
        self.max_number_usage = (
            int(max_number_usage) if max_number_usage is not None else None
        )
        self.excluded_sets = {
            tuple(sorted(int(n) for n in ticket))
            for ticket in (excluded_sets or set())
            if len(ticket) == self.number_predict
        }
        self.max_consecutive_run = (
            int(max_consecutive_run) if max_consecutive_run is not None else None
        )
        self.coverage_rescue_size = int(coverage_rescue_size)
        self.coverage_recent_draws = int(coverage_recent_draws)
        self.coverage_long_draws = int(coverage_long_draws)
        self.coverage_repeat_weight = float(coverage_repeat_weight)
        self.ensemble_score_mode = ensemble_score_mode
        self.exposure_power = float(exposure_power)
        self.pair_reuse_penalty = float(pair_reuse_penalty)

        self._candidate_cache: dict[date, tuple[list[int], list[int], list[int]]] = {}
        self._portfolio_cache: dict[date, list[list[int]]] = {}
        self._next_index: dict[date, int] = {}

    def _scores(self, target_date: date) -> dict[int, float]:
        """Return a full 1..55 score map, using weighted rank evidence."""
        if self.ensemble_score_mode == "top6":
            return super()._scores(target_date)

        scores = {n: 0.0 for n in range(self.min_val, self.max_val + 1)}
        total_numbers = self.max_val - self.min_val + 1
        for _, weight, model in self._components():
            if weight <= 0:
                continue
            if not hasattr(model, "score_numbers"):
                raise RuntimeError(
                    f"{model.__class__.__name__} does not expose full number scores"
                )
            raw_scores = model.score_numbers(target_date)
            ranked = sorted(
                range(self.min_val, self.max_val + 1),
                key=lambda n: (-float(raw_scores.get(n, 0.0)), n),
            )
            for rank, number in enumerate(ranked):
                scores[number] += float(weight) * (total_numbers - rank)
        return scores

    def _valid_shape(self, ticket: tuple[int, ...]) -> bool:
        if self.max_consecutive_run is None:
            return True
        run = best = 1
        for left, right in zip(ticket, ticket[1:]):
            if right == left + 1:
                run += 1
                best = max(best, run)
            else:
                run = 1
        return best <= self.max_consecutive_run

    @staticmethod
    def _normalize(scores: dict[int, float]) -> dict[int, float]:
        if not scores:
            return {}
        lo = min(scores.values())
        hi = max(scores.values())
        if hi == lo:
            return {n: 1.0 for n in scores}
        span = hi - lo
        return {n: (score - lo) / span for n, score in scores.items()}

    def _coverage_rank(self, target_date: date, excluded: set[int]) -> list[int]:
        """Rank historical reservoir candidates outside the protected core."""
        history = self.df[self.df["date"] < target_date].sort_values("date")
        if history.empty:
            return []

        recent = history.tail(self.coverage_recent_draws)
        long_window = history.tail(self.coverage_long_draws)
        recent_counts = Counter(
            int(n)
            for values in recent["result"].tolist()
            for n in list(values)[: self.number_predict]
        )
        long_counts = Counter(
            int(n)
            for values in long_window["result"].tolist()
            for n in list(values)[: self.number_predict]
        )

        all_numbers = list(range(self.min_val, self.max_val + 1))
        latest_numbers = set(int(n) for n in list(history.iloc[-1]["result"])[: self.number_predict])
        previous_numbers: set[int] = set()
        if len(history) >= 2:
            previous_numbers = set(
                int(n) for n in list(history.iloc[-2]["result"])[: self.number_predict]
            )

        last_seen: dict[int, date] = {}
        exploded = history.copy()
        exploded["result"] = exploded["result"].apply(lambda x: list(x)[: self.number_predict])
        exploded = exploded.explode("result")
        if not exploded.empty:
            last_seen = exploded.groupby("result")["date"].max().to_dict()

        gaps = {
            n: float("inf") if n not in last_seen else float((target_date - last_seen[n]).days)
            for n in all_numbers
        }
        finite_gaps = [value for value in gaps.values() if value != float("inf")]
        max_gap = max(finite_gaps, default=1.0)
        max_recent = max(recent_counts.values(), default=1)
        max_long = max(long_counts.values(), default=1)

        def key(n: int) -> tuple[float, float, int]:
            recent_norm = recent_counts.get(n, 0) / max_recent
            long_norm = long_counts.get(n, 0) / max_long
            repeat = 1.0 if n in latest_numbers else 0.5 if n in previous_numbers else 0.0
            gap_score = 1.0 if gaps[n] == float("inf") else gaps[n] / max_gap
            score = (
                0.38 * recent_norm
                + 0.27 * long_norm
                + self.coverage_repeat_weight * repeat
                + (0.35 - self.coverage_repeat_weight) * gap_score
            )
            return (-score, -gaps[n] if gaps[n] != float("inf") else float("-inf"), n)

        return sorted((n for n in all_numbers if n not in excluded), key=key)

    def _candidate_pool(self, target_date: date) -> tuple[list[int], list[int], list[int]]:
        if target_date in self._candidate_cache:
            return self._candidate_cache[target_date]

        scores = self._scores(target_date)
        ordered = sorted(scores, key=lambda n: (-scores[n], n))
        core_size = self.candidate_pool_size - self.coverage_rescue_size
        core = ordered[:core_size]
        core_set = set(core)

        # Reservoir candidates are selected only for the remaining satellite slots.
        rescue_ranked = self._coverage_rank(target_date, core_set)
        rescue: list[int] = []
        for number in rescue_ranked:
            rescue.append(number)
            if len(rescue) >= self.coverage_rescue_size:
                break

        if len(rescue) < self.coverage_rescue_size:
            for number in ordered:
                if number not in core_set and number not in rescue:
                    rescue.append(number)
                    if len(rescue) >= self.coverage_rescue_size:
                        break

        pool = core + rescue
        if len(pool) < self.candidate_pool_size:
            for number in ordered:
                if number not in pool:
                    pool.append(number)
                    if len(pool) >= self.candidate_pool_size:
                        break

        if len(pool) != self.candidate_pool_size:
            raise RuntimeError("failed to construct candidate pool")

        self._candidate_cache[target_date] = (pool, core, rescue)
        return pool, core, rescue

    def candidate_pool_details(self, target_date: date) -> dict[str, object]:
        pool, core, rescue = self._candidate_pool(target_date)
        return {
            "pool": list(pool),
            "core": list(core),
            "coverage_rescue": list(rescue),
            "candidate_selection_mode": "protected_core_plus_additive_reservoir",
        }

    def _build_portfolio(self, target_date: date) -> list[list[int]]:
        scores = self._scores(target_date)
        pool, _, _ = self._candidate_pool(target_date)
        normalized = self._normalize(scores)

        # Score-powered exposure targets: strong candidates can appear more
        # than six times; the target is a soft preference, not a hard quota.
        weights = {
            n: max(normalized.get(n, 0.0), 0.0) ** self.exposure_power + 1e-6
            for n in pool
        }
        weight_total = sum(weights.values())
        if weight_total <= 0:
            weights = {n: 1.0 for n in pool}
            weight_total = float(len(pool))
        total_slots = self.tickets_per_draw * self.number_predict
        target_exposure = {
            n: weights[n] / weight_total * total_slots for n in pool
        }

        exposure = {n: 0 for n in pool}
        pair_usage: dict[tuple[int, int], int] = {}
        tickets: list[list[int]] = []
        seen: set[tuple[int, ...]] = set()

        def utility(number: int, chosen: list[int], ticket_idx: int) -> float:
            score = normalized.get(number, 0.0)
            deficit = target_exposure[number] - exposure[number]
            target_term = 1.0 + (max(deficit, 0.0) / max(target_exposure[number], 1.0))
            overdue_bonus = 1.0
            if ticket_idx < 6 and target_exposure[number] >= 7:
                overdue_bonus += 0.03 * max(0.0, 6 - exposure[number])
            pair_count = sum(
                pair_usage.get(tuple(sorted((number, other))), 0)
                for other in chosen
            )
            pair_factor = 1.0 / (1.0 + self.pair_reuse_penalty * pair_count)
            return (
                score * (1.0 + self.usage_penalty * target_term) * overdue_bonus * pair_factor
            )

        def feasible_candidates(chosen: list[int], ticket_idx: int) -> list[int]:
            candidates = []
            for number in pool:
                if number in chosen:
                    continue
                if (
                    self.max_number_usage is not None
                    and exposure[number] >= self.max_number_usage
                ):
                    continue
                trial = tuple(sorted(chosen + [number]))
                if len(trial) == self.number_predict and not self._valid_shape(trial):
                    continue
                candidates.append(number)
            return candidates

        for ticket_idx in range(self.tickets_per_draw):
            chosen: list[int] = []
            for _slot in range(self.number_predict):
                candidates = feasible_candidates(chosen, ticket_idx)
                if not candidates:
                    raise RuntimeError("failed to find feasible portfolio candidate")

                # Deterministic tie-break rotates low-ranked numbers so equal
                # scores do not always favor the lowest numeric ID.
                ranked = sorted(
                    candidates,
                    key=lambda n: (
                        -utility(n, chosen, ticket_idx),
                        (n + ticket_idx + len(chosen)) % len(pool),
                        n,
                    ),
                )
                chosen.append(ranked[0])

            ticket = tuple(sorted(chosen))
            if ticket in seen or ticket in self.excluded_sets:
                # Repair from the weakest member while preserving shape/capacity.
                repair_ok = False
                weakest = sorted(
                    range(len(ticket)),
                    key=lambda i: (
                        normalized.get(ticket[i], 0.0),
                        ticket[i],
                    ),
                )
                replacements = sorted(
                    (n for n in pool if n not in ticket),
                    key=lambda n: (-normalized.get(n, 0.0), n),
                )
                for weakest_index in weakest:
                    for replacement in replacements:
                        if (
                            self.max_number_usage is not None
                            and exposure[replacement] >= self.max_number_usage
                        ):
                            continue
                        repaired = list(ticket)
                        repaired[weakest_index] = replacement
                        candidate = tuple(sorted(set(repaired)))
                        if (
                            len(candidate) == self.number_predict
                            and candidate not in seen
                            and candidate not in self.excluded_sets
                            and self._valid_shape(candidate)
                        ):
                            ticket = candidate
                            repair_ok = True
                            break
                    if repair_ok:
                        break

                if not repair_ok:
                    ranked_combos = sorted(
                        combinations(pool, self.number_predict),
                        key=lambda combo: (
                            -sum(normalized.get(n, 0.0) for n in combo),
                            combo,
                        ),
                    )
                    for combo in ranked_combos:
                        if combo in seen or combo in self.excluded_sets or not self._valid_shape(combo):
                            continue
                        if self.max_number_usage is not None and any(
                            exposure[n] >= self.max_number_usage for n in combo
                        ):
                            continue
                        ticket = combo
                        repair_ok = True
                        break

                if not repair_ok:
                    raise RuntimeError("failed to construct a distinct allowed portfolio ticket")

            seen.add(ticket)
            tickets.append(list(ticket))
            for number in ticket:
                exposure[number] += 1
            for i, left in enumerate(ticket):
                for right in ticket[i + 1 :]:
                    pair_usage[(left, right)] = pair_usage.get((left, right), 0) + 1

        if len(tickets) != self.tickets_per_draw or len(seen) != self.tickets_per_draw:
            raise RuntimeError("failed to build requested distinct portfolio")
        if self.max_number_usage is not None:
            assert max(exposure.values(), default=0) <= self.max_number_usage

        return tickets

    def predict(self, target_date: date) -> list[int]:
        if target_date not in self._portfolio_cache:
            self._portfolio_cache[target_date] = self._build_portfolio(target_date)
            self._next_index[target_date] = 0

        index = self._next_index[target_date]
        tickets = self._portfolio_cache[target_date]
        ticket = tickets[index % len(tickets)]
        self._next_index[target_date] = index + 1
        return list(ticket)
