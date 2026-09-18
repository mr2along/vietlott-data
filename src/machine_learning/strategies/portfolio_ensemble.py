"""Deterministic portfolio built from ensemble number scores.

The optional usage cap turns the score-ranked portfolio into a coverage-aware
portfolio: high-scoring numbers remain preferred, but no candidate can consume
more than the configured share of the 30-ticket budget.
"""

from __future__ import annotations

from datetime import date
from itertools import combinations

import pandas as pd

from .rank_ensemble import RankEnsembleStrategy


class PortfolioEnsembleStrategy(RankEnsembleStrategy):
    """Generate a score-driven six-number ticket portfolio.

    "max_number_usage" is disabled by default to preserve the historical V2
    benchmark behavior. Forecasting can enable it to reduce concentration and
    spread the fixed ticket budget across the candidate pool.
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
        self.max_consecutive_run = (
            int(max_consecutive_run) if max_consecutive_run is not None else None
        )
        self._portfolio_cache: dict[date, list[list[int]]] = {}
        self._next_index: dict[date, int] = {}

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

    def _build_portfolio(self, target_date: date) -> list[list[int]]:
        scores = self._scores(target_date)
        ordered = sorted(scores, key=lambda n: (-scores[n], n))
        pool = ordered[: self.candidate_pool_size]
        usage = {n: 0 for n in pool}
        tickets: list[list[int]] = []
        seen: set[tuple[int, ...]] = set()

        for ticket_idx in range(self.tickets_per_draw):
            available = list(pool)
            chosen: list[int] = []
            for slot in range(self.number_predict):
                under_cap = [
                    n
                    for n in available
                    if self.max_number_usage is None
                    or usage[n] < self.max_number_usage
                ]
                # Defensive fallback keeps the ticket valid if intermediate
                # constraints leave fewer than six under-cap candidates.
                candidates = (
                    under_cap
                    if len(under_cap) >= self.number_predict - slot
                    else available
                )
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
