"""Deterministic portfolio built from ensemble number scores.

The optional usage cap turns the score-ranked portfolio into a coverage-aware
portfolio: high-scoring numbers remain preferred, but no candidate can consume
more than the configured share of the 30-ticket budget.
"""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from itertools import combinations

import pandas as pd

from .rank_ensemble import RankEnsembleStrategy


class PortfolioEnsembleStrategy(RankEnsembleStrategy):
    """Generate a score-driven six-number ticket portfolio.

    ``coverage_rescue_size`` optionally reserves part of the candidate pool
    for an independent historical-coverage tier instead of allowing the
    ensemble's zero-score numeric tie-break to decide every slot. This is a
    diversification guardrail, not evidence that rescued numbers are more
    likely to be drawn.
    """

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
        if max_consecutive_run is not None and max_consecutive_run < 1:
            raise ValueError("max_consecutive_run must be >= 1")
        if coverage_rescue_size < 0 or coverage_rescue_size > candidate_pool_size - self.number_predict:
            raise ValueError("coverage_rescue_size must leave room for six-number tickets")
        if coverage_recent_draws < 1 or coverage_long_draws < coverage_recent_draws:
            raise ValueError("coverage draw windows are invalid")
        if not 0 <= coverage_repeat_weight <= 1:
            raise ValueError("coverage_repeat_weight must be between 0 and 1")
        self.max_consecutive_run = (
            int(max_consecutive_run) if max_consecutive_run is not None else None
        )
        self.coverage_rescue_size = int(coverage_rescue_size)
        self.coverage_recent_draws = int(coverage_recent_draws)
        self.coverage_long_draws = int(coverage_long_draws)
        self.coverage_repeat_weight = float(coverage_repeat_weight)
        if ensemble_score_mode not in {"top6", "full_rank"}:
            raise ValueError("ensemble_score_mode must be 'top6' or 'full_rank'")
        self.ensemble_score_mode = ensemble_score_mode
        self._candidate_cache: dict[date, tuple[list[int], list[int], list[int]]] = {}
        self._portfolio_cache: dict[date, list[list[int]]] = {}
        self._next_index: dict[date, int] = {}

    def _scores(self, target_date: date) -> dict[int, float]:
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

    def _coverage_rank(self, target_date: date, excluded: set[int]) -> list[int]:
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
        latest_numbers = set(
            int(n) for n in list(history.iloc[-1]["result"])[: self.number_predict]
        )
        previous_numbers = set()
        if len(history) >= 2:
            previous_numbers = set(
                int(n)
                for n in list(history.iloc[-2]["result"])[: self.number_predict]
            )

        all_numbers = list(range(self.min_val, self.max_val + 1))
        max_recent = max(recent_counts.values(), default=1)
        max_long = max(long_counts.values(), default=1)

        def key(n: int) -> tuple[float, int]:
            recent_norm = recent_counts.get(n, 0) / max_recent
            long_norm = long_counts.get(n, 0) / max_long
            repeat = 1.0 if n in latest_numbers else 0.5 if n in previous_numbers else 0.0
            score = (
                (1.0 - self.coverage_repeat_weight) * 0.55 * recent_norm
                + (1.0 - self.coverage_repeat_weight) * 0.45 * long_norm
                + self.coverage_repeat_weight * repeat
            )
            return (-score, n)

        return sorted((n for n in all_numbers if n not in excluded), key=key)

    def _candidate_pool(self, target_date: date) -> tuple[list[int], list[int], list[int]]:
        if target_date in self._candidate_cache:
            return self._candidate_cache[target_date]

        scores = self._scores(target_date)
        ordered = sorted(scores, key=lambda n: (-scores[n], n))
        core_size = self.candidate_pool_size - self.coverage_rescue_size
        core = ordered[:core_size]
        excluded = set(core)
        rescue_ranked = self._coverage_rank(target_date, excluded)
        rescue = rescue_ranked[: self.coverage_rescue_size]
        pool = core + rescue

        if len(pool) < self.candidate_pool_size:
            remaining = [n for n in ordered if n not in pool]
            pool.extend(remaining[: self.candidate_pool_size - len(pool)])
        if len(pool) != self.candidate_pool_size:
            raise RuntimeError("failed to construct candidate pool")

        self._candidate_cache[target_date] = (pool, core, rescue)
        return pool, core, rescue

    def candidate_pool_details(self, target_date: date) -> dict[str, list[int]]:
        pool, core, rescue = self._candidate_pool(target_date)
        return {"pool": list(pool), "core": list(core), "coverage_rescue": list(rescue)}

    def _build_portfolio(self, target_date: date) -> list[list[int]]:
        scores = self._scores(target_date)
        pool, _, _ = self._candidate_pool(target_date)
        usage = {n: 0 for n in pool}
        tickets: list[list[int]] = []
        seen: set[tuple[int, ...]] = set()

        for ticket_idx in range(self.tickets_per_draw):
            available = list(pool)
            chosen: list[int] = []
            for slot in range(self.number_predict):
                slots_remaining_after_choice = (
                    self.tickets_per_draw - ticket_idx
                ) * self.number_predict - slot - 1
                candidates = [
                    n
                    for n in available
                    if self.max_number_usage is None
                    or usage[n] < self.max_number_usage
                ]
                required = self.number_predict - slot
                if len(candidates) < required:
                    raise RuntimeError(
                        "failed to preserve portfolio capacity while selecting a ticket"
                    )

                if self.max_number_usage is not None:
                    # Balance usage first, then use the ensemble score. This
                    # preserves the global usage cap by construction while
                    # still preferring stronger candidates among equally used
                    # numbers.
                    ranked = sorted(
                        candidates,
                        key=lambda n: (
                            usage[n],
                            -(scores[n] - self.usage_penalty * usage[n]),
                            (n + ticket_idx + slot) % self.candidate_pool_size,
                            n,
                        ),
                    )
                else:
                    ranked = sorted(
                        candidates,
                        key=lambda n: (
                            -(scores[n] - self.usage_penalty * usage[n]),
                            (n + ticket_idx + slot) % self.candidate_pool_size,
                            n,
                        ),
                    )
                choice = ranked[0]
                chosen.append(choice)
                available.remove(choice)

            ticket = tuple(sorted(chosen))
            if ticket in seen or ticket in self.excluded_sets or not self._valid_shape(ticket):
                # Deterministic repair: try one-number substitutions first so
                # the score profile remains close to the original selection.
                repair_candidates = sorted(
                    (n for n in pool if n not in ticket),
                    key=lambda n: (
                        -(scores[n] - self.usage_penalty * usage[n]),
                        n,
                    ),
                )
                repaired_ok = False
                for weakest_index in sorted(
                    range(len(ticket)),
                    key=lambda i: (
                        scores[ticket[i]] - self.usage_penalty * usage[ticket[i]],
                        -ticket[i],
                    ),
                ):
                    for replacement in repair_candidates:
                        if (
                            self.max_number_usage is not None
                            and usage[replacement] >= self.max_number_usage
                        ):
                            continue
                        repaired = list(ticket)
                        repaired[weakest_index] = replacement
                        repaired_tuple = tuple(sorted(set(repaired)))
                        if (
                            len(repaired_tuple) == self.number_predict
                            and repaired_tuple not in seen
                            and repaired_tuple not in self.excluded_sets
                            and self._valid_shape(repaired_tuple)
                        ):
                            ticket = repaired_tuple
                            repaired_ok = True
                            break
                    if repaired_ok:
                        break

                if not repaired_ok:
                    # The normal path should find a one-number repair. The
                    # exhaustive fallback guarantees exact-set exclusion when
                    # the candidate pool contains a feasible unseen ticket.
                    ranked_combos = sorted(
                        combinations(pool, self.number_predict),
                        key=lambda combo: (
                            -sum(
                                scores[n] - self.usage_penalty * usage[n]
                                for n in combo
                            ),
                            combo,
                        ),
                    )
                    for combo in ranked_combos:
                        key = tuple(sorted(combo))
                        if key in seen or key in self.excluded_sets or not self._valid_shape(key):
                            continue
                        if self.max_number_usage is not None and any(
                            usage[n] >= self.max_number_usage for n in key
                        ):
                            continue
                        ticket = key
                        repaired_ok = True
                        break

                if not repaired_ok:
                    raise RuntimeError(
                        "failed to construct an allowed portfolio ticket"
                    )

            if ticket in seen or ticket in self.excluded_sets:
                raise RuntimeError(
                    f"failed to create distinct portfolio ticket {ticket_idx + 1}"
                )

            seen.add(ticket)
            tickets.append(list(ticket))
            for number in ticket:
                usage[number] += 1

        if len(tickets) != self.tickets_per_draw or len(seen) != self.tickets_per_draw:
            raise RuntimeError("failed to build requested distinct portfolio")

        if self.max_number_usage is not None:
            assert max(usage.values(), default=0) <= self.max_number_usage

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
