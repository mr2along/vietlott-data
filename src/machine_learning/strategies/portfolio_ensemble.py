"""Deterministic 30-ticket portfolio built from ensemble number scores."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .rank_ensemble import RankEnsembleStrategy


class PortfolioEnsembleStrategy(RankEnsembleStrategy):
    """Generate a diversified ticket portfolio from ensemble scores.

    The first call for a target date builds exactly ``tickets_per_draw``
    distinct six-number tickets. Later calls return the next ticket so the
    existing backtest loop can evaluate the full portfolio without changing
    its interface.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        time_predict: int = 1,
        weights: dict[str, float] | None = None,
        tickets_per_draw: int = 30,
        candidate_pool_size: int = 24,
        usage_penalty: float = 0.35,
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

        self.tickets_per_draw = int(tickets_per_draw)
        self.candidate_pool_size = int(candidate_pool_size)
        self.usage_penalty = float(usage_penalty)
        self._portfolio_cache: dict[date, list[list[int]]] = {}
        self._next_index: dict[date, int] = {}

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
                ranked = sorted(
                    available,
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
            if ticket in seen:
                # Deterministic repair: rotate one candidate from the pool.
                for replacement in pool:
                    if replacement in ticket:
                        continue
                    repaired = list(ticket[:-1]) + [replacement]
                    repaired_tuple = tuple(sorted(set(repaired)))
                    if len(repaired_tuple) == self.number_predict and repaired_tuple not in seen:
                        ticket = repaired_tuple
                        break

            seen.add(ticket)
            tickets.append(list(ticket))
            for number in ticket:
                usage[number] += 1

        if len(tickets) != len(seen):
            raise RuntimeError("failed to build distinct portfolio")
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
