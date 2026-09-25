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
import random
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
        max_pair_reuse: int | None = None,
        decay_half_life_days: int = 730,
        consensus_discount: float = 0.25,
        anchor_ticket_count: int = 0,
    ) -> None:
        super().__init__(
            df,
            time_predict=time_predict,
            weights=weights,
            decay_half_life_days=decay_half_life_days,
            consensus_discount=consensus_discount,
        )
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
        if max_pair_reuse is not None and int(max_pair_reuse) < 1:
            raise ValueError("max_pair_reuse must be >= 1 or None")

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
        self.max_pair_reuse = (
            int(max_pair_reuse) if max_pair_reuse is not None else None
        )
        if not 0 <= int(anchor_ticket_count) <= int(tickets_per_draw):
            raise ValueError("anchor_ticket_count must be between 0 and tickets_per_draw")
        self.anchor_ticket_count = int(anchor_ticket_count)

        self._candidate_cache: dict[date, tuple[list[int], list[int], list[int]]] = {}
        self._portfolio_cache: dict[date, list[list[int]]] = {}
        self._next_index: dict[date, int] = {}

    def _scores(self, target_date: date) -> dict[int, float]:
        """Return candidate scores with diminishing returns for repeated evidence."""
        if self.ensemble_score_mode == "top6":
            return super()._scores(target_date)

        contributions: dict[int, list[float]] = {
            n: [] for n in range(self.min_val, self.max_val + 1)
        }
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
                contributions[number].append(
                    float(weight) * (total_numbers - rank)
                )
        return self._aggregate_contributions(contributions)

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

    def _reservoir_sets(self, target_date: date) -> dict[str, set[int]]:
        """Build independent candidate reservoirs without using the target draw."""
        history = self.df[self.df["date"] < target_date].sort_values("date")
        if history.empty:
            return {}

        reservoirs: dict[str, set[int]] = {}
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

        reservoirs["recent"] = {
            n for n, _ in sorted(
                recent_counts.items(), key=lambda item: (-item[1], item[0])
            )[:12]
        }
        reservoirs["long_frequency"] = {
            n for n, _ in sorted(
                long_counts.items(), key=lambda item: (-item[1], item[0])
            )[:15]
        }

        latest_numbers = set(
            int(n) for n in list(history.iloc[-1]["result"])[: self.number_predict]
        )
        reservoirs["repeat"] = set(latest_numbers)
        if len(history) >= 2:
            reservoirs["repeat"] |= {
                int(n) for n in list(history.iloc[-2]["result"])[: self.number_predict]
            }

        exploded = history.copy()
        exploded["result"] = exploded["result"].apply(
            lambda x: list(x)[: self.number_predict]
        )
        exploded = exploded.explode("result")
        last_seen: dict[int, date] = {}
        if not exploded.empty:
            last_seen = exploded.groupby("result")["date"].max().to_dict()

        gaps = {
            n: float("inf")
            if n not in last_seen
            else float((target_date - last_seen[n]).days)
            for n in all_numbers
        }
        reservoirs["overdue"] = set(
            sorted(all_numbers, key=lambda n: (-gaps[n], n))[:12]
        )

        for name, weight, model in self._components():
            if weight <= 0:
                continue
            if hasattr(model, "score_numbers"):
                raw = model.score_numbers(target_date)
                ranked = sorted(
                    all_numbers,
                    key=lambda n: (-float(raw.get(n, 0.0)), n),
                )
                reservoirs[f"model:{name}"] = set(ranked[:12])

        return reservoirs

    def _coverage_rank(self, target_date: date, excluded: set[int]) -> list[int]:
        """Rank reservoir candidates outside the protected core."""
        reservoirs = self._reservoir_sets(target_date)
        if not reservoirs:
            return []

        scores = self._scores(target_date)
        normalized = self._normalize(scores)
        pool = [n for n in range(self.min_val, self.max_val + 1) if n not in excluded]
        model_keys = [k for k in reservoirs if k.startswith("model:")]
        history_keys = [k for k in reservoirs if not k.startswith("model:")]

        model_strength_by_number: dict[int, list[float]] = {
            number: [] for number in pool
        }
        for _, weight, model in self._components():
            if weight <= 0 or not hasattr(model, "score_numbers"):
                continue
            raw = model.score_numbers(target_date)
            ranked = sorted(
                range(self.min_val, self.max_val + 1),
                key=lambda number: (-float(raw.get(number, 0.0)), number),
            )
            denom = max(self.max_val - self.min_val, 1)
            for rank_index, number in enumerate(ranked):
                if number in model_strength_by_number:
                    model_strength_by_number[number].append(
                        (self.max_val - self.min_val - rank_index) / denom
                    )

        model_specificity_by_number: dict[int, float] = {}
        for number, strengths in model_strength_by_number.items():
            model_specificity_by_number[number] = (
                max(strengths) - sum(strengths) / len(strengths)
                if strengths
                else 0.0
            )

        def key(n: int) -> tuple[float, float, float, int]:
            model_breadth = (
                sum(n in reservoirs[k] for k in model_keys) / max(len(model_keys), 1)
            )
            history_breadth = (
                sum(n in reservoirs[k] for k in history_keys) / max(len(history_keys), 1)
            )
            model_specificity = model_specificity_by_number.get(n, 0.0)
            utility = (
                0.52 * normalized.get(n, 0.0)
                + 0.25 * model_specificity
                + 0.08 * model_breadth
                + 0.15 * history_breadth
            )
            return (
                -utility,
                -model_specificity,
                -scores.get(n, 0.0),
                n,
            )

        return sorted(pool, key=key)

    def _candidate_pool(self, target_date: date) -> tuple[list[int], list[int], list[int]]:
        if target_date in self._candidate_cache:
            return self._candidate_cache[target_date]

        scores = self._scores(target_date)
        ordered = sorted(scores, key=lambda n: (-scores[n], n))
        core_size = self.candidate_pool_size - self.coverage_rescue_size
        core = ordered[:core_size]
        core_set = set(core)

        # The core is protected. Reservoir/disagreement candidates can only
        # occupy the satellite slots left after the core is fixed.
        rescue_ranked = self._coverage_rank(target_date, core_set)
        rescue: list[int] = []
        if self.coverage_rescue_size > 0:
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

    def _build_hard_cap_portfolio(
        self,
        pool: list[int],
        normalized: dict[int, float],
    ) -> list[list[int]]:
        """Build a quota-safe portfolio by selecting whole feasible tickets.

        Whole-combination search avoids the dead-end behavior of greedy
        number-by-number construction. Quotas remain exact, while the
        objective preserves score strength, balances exposure, penalizes
        repeated pairs, and respects historical/shape exclusions.
        """
        total_slots = self.tickets_per_draw * self.number_predict
        pool_size = len(pool)
        base_quota, remainder = divmod(total_slots, pool_size)
        cap = self.max_number_usage
        if cap is None:
            raise RuntimeError("hard-cap portfolio requires max_number_usage")
        if base_quota > cap or (base_quota == cap and remainder > 0):
            raise RuntimeError(
                "max_number_usage does not provide enough per-number capacity"
            )

        ordered = sorted(pool, key=lambda n: (-normalized.get(n, 0.0), n))
        quota = {
            number: base_quota + (1 if index < remainder else 0)
            for index, number in enumerate(ordered)
        }

        # When a shape constraint is active, exact quota construction can be
        # solved directly with a small balanced block design. This avoids the
        # combinatorial dead-end caused by mixing shape filtering with greedy
        # quota consumption. The 30-ticket/24-candidate production-compatible
        # case uses 24 cyclic base blocks (replication 6 each) plus six
        # staggered blocks (+1/+2 replication), yielding the required 7/8
        # appearances while keeping the score-ranked top half on the extra slots.
        if self.max_consecutive_run is not None and self.tickets_per_draw == 30 and len(pool) == 24:
            doubled_positions = {0, 1, 4, 5, 8, 9, 12, 13, 16, 17, 20, 21}
            single_positions = set(range(24)) - doubled_positions
            rng_seed = sum((index + 1) * number for index, number in enumerate(ordered))
            for attempt in range(512):
                rng = random.Random(rng_seed + attempt)
                position_order = [None] * 24
                top = ordered[:12]
                bottom = ordered[12:]
                rng.shuffle(top)
                rng.shuffle(bottom)
                for pos, number in zip(sorted(doubled_positions), top):
                    position_order[pos] = number
                for pos, number in zip(sorted(single_positions), bottom):
                    position_order[pos] = number

                pattern = tuple(sorted(rng.sample(range(24), self.number_predict)))
                base_blocks = [
                    tuple(sorted(position_order[(start + offset) % 24] for offset in pattern))
                    for start in range(24)
                ]
                extra_starts = (0, 4, 8, 12, 16, 20)
                extra_blocks = [
                    tuple(sorted(position_order[(start + offset) % 24] for offset in range(6)))
                    for start in extra_starts
                ]
                candidate_blocks = base_blocks + extra_blocks

                if len(set(candidate_blocks)) != 30:
                    continue
                if any(not self._valid_shape(block) for block in candidate_blocks):
                    continue
                observed = Counter(number for block in candidate_blocks for number in block)
                expected = {
                    number: quota[number]
                    for number in pool
                }
                if observed == expected:
                    return [list(block) for block in candidate_blocks]

        exposure = {number: 0 for number in pool}
        pair_usage: dict[tuple[int, int], int] = {}
        tickets: list[list[int]] = []
        seen: set[tuple[int, ...]] = set()

        for _ticket_idx in range(self.tickets_per_draw):
            future_tickets = self.tickets_per_draw - len(tickets) - 1
            available = [
                number
                for number in pool
                if exposure[number] < quota[number]
            ]
            if len(available) < self.number_predict:
                raise RuntimeError(
                    "failed to construct quota-safe portfolio: insufficient candidates"
                )

            if future_tickets > 0:
                future_capacity = sum(
                    min(quota[number] - exposure[number], future_tickets)
                    for number in pool
                )
            else:
                future_capacity = 0

            best_ticket: tuple[int, ...] | None = None
            best_utility = float("-inf")

            for combo in combinations(available, self.number_predict):
                if combo in seen or combo in self.excluded_sets:
                    continue
                if not self._valid_shape(combo):
                    continue

                if future_tickets > 0:
                    # Selecting a number reduces its future-ticket capacity by
                    # one only when its remaining quota is <= future_tickets.
                    consumed_future_capacity = sum(
                        (quota[number] - exposure[number]) <= future_tickets
                        for number in combo
                    )
                    if future_capacity - consumed_future_capacity < (
                        future_tickets * self.number_predict
                    ):
                        continue

                score_sum = sum(normalized.get(number, 0.0) for number in combo)
                balance_sum = sum(
                    (quota[number] - exposure[number]) / max(quota[number], 1)
                    for number in combo
                )
                repeated_pairs = sum(
                    pair_usage.get(pair, 0)
                    for pair in combinations(combo, 2)
                )
                utility = (
                    score_sum
                    + 0.15 * balance_sum
                    - 0.02 * self.pair_reuse_penalty * repeated_pairs
                )
                tie_break = tuple(combo)
                if utility > best_utility or (
                    utility == best_utility
                    and (best_ticket is None or tie_break < best_ticket)
                ):
                    best_utility = utility
                    best_ticket = combo

            if best_ticket is None:
                raise RuntimeError(
                    "failed to construct quota-safe portfolio ticket"
                )

            seen.add(best_ticket)
            tickets.append(list(best_ticket))
            for number in best_ticket:
                exposure[number] += 1
            for pair in combinations(best_ticket, 2):
                pair_usage[pair] = pair_usage.get(pair, 0) + 1

        if len(tickets) != self.tickets_per_draw or len(seen) != self.tickets_per_draw:
            raise RuntimeError("failed to build requested distinct portfolio")
        if any(exposure[number] != quota[number] for number in pool):
            raise RuntimeError("hard-cap portfolio did not consume all candidate quotas")
        if max(exposure.values(), default=0) > cap:
            raise RuntimeError("hard-cap portfolio exceeded max_number_usage")

        return tickets

    def _anchor_tickets(self, target_date: date, pool: list[int]) -> list[tuple[int, ...]]:
        """Select diverse model-led anchor tickets before portfolio diversification."""
        if self.anchor_ticket_count <= 0:
            return []

        pool_set = set(pool)
        scores = self._scores(target_date)
        ranked_scores = sorted(scores, key=lambda n: (-scores[n], n))
        sources: list[list[int]] = [ranked_scores]

        for _, weight, model in self._components():
            if weight <= 0 or not hasattr(model, "predict"):
                continue
            sources.append([int(n) for n in model.predict(target_date)])

        try:
            sources.append(self._coverage_rank(target_date, set()))
        except Exception:
            pass

        anchors: list[tuple[int, ...]] = []
        pair_usage: Counter = Counter()

        for source in sources:
            values: list[int] = []
            for number in source:
                number = int(number)
                if number in pool_set and number not in values:
                    values.append(number)
                if len(values) == self.number_predict:
                    break
            if len(values) != self.number_predict:
                continue

            ticket = tuple(sorted(values))
            if ticket in self.excluded_sets or ticket in anchors:
                continue

            if self.max_pair_reuse is not None and anchors:
                if any(
                    pair_usage[pair] + 1 > self.max_pair_reuse
                    for pair in combinations(ticket, 2)
                ):
                    continue

            anchors.append(ticket)
            for pair in combinations(ticket, 2):
                pair_usage[pair] += 1

            if len(anchors) >= self.anchor_ticket_count:
                break

        return anchors

    def _build_portfolio(self, target_date: date) -> list[list[int]]:
        scores = self._scores(target_date)
        pool, _, _ = self._candidate_pool(target_date)
        normalized = self._normalize(scores)

        # Hard-cap mode is used for regression/compatibility callers. Solve it
        # with explicit quotas so finite capacity cannot dead-end the greedy
        # score-first constructor.
        if self.max_number_usage is not None:
            return self._build_hard_cap_portfolio(pool, normalized)

        # Production default: 30 candidates x 30 tickets. A cyclic balanced
        # block design gives every candidate exactly six appearances while
        # spreading pair reuse and avoiding the repeated five-block pattern that
        # previously concentrated the strongest candidates together. We retain
        # score information in candidate-pool selection and in the phase/order:
        # the first block contains the highest-ranked candidates.
        if (
            self.max_pair_reuse is not None
            and self.tickets_per_draw == 30
            and len(pool) == 30
            and self.anchor_ticket_count == 0
        ):
            pair_cap = self.max_pair_reuse
            rng_seed = sum((index + 1) * number for index, number in enumerate(pool))
            for attempt in range(2048):
                rng = random.Random(rng_seed + attempt)
                positions = list(range(30))
                rng.shuffle(positions)

                # Put the highest-ranked candidates in the first six positions
                # so the first emitted ticket remains score-led.
                position_order = [None] * 30
                for pos, number in zip(range(6), pool[:6]):
                    position_order[pos] = number
                remainder_numbers = list(pool[6:])
                rng.shuffle(remainder_numbers)
                free_positions = positions
                cursor = 0
                for pos in free_positions:
                    if position_order[pos] is None:
                        position_order[pos] = remainder_numbers[cursor]
                        cursor += 1

                pattern = tuple(sorted(rng.sample(range(30), 6)))
                blocks = [
                    tuple(sorted(position_order[(start + offset) % 30] for offset in pattern))
                    for start in range(30)
                ]
                if len(set(blocks)) != 30:
                    continue
                if any(not self._valid_shape(block) for block in blocks):
                    continue
                if any(block in self.excluded_sets for block in blocks):
                    continue

                pair_usage = Counter(
                    pair
                    for block in blocks
                    for pair in combinations(block, 2)
                )
                if max(pair_usage.values(), default=0) > pair_cap:
                    continue

                exposure = Counter(number for block in blocks for number in block)
                if any(exposure[number] != 6 for number in pool):
                    continue

                return [list(block) for block in blocks]

            raise RuntimeError(
                "unable to construct balanced 30-ticket portfolio within pair/shape constraints"
            )

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
        anchor_tickets = self._anchor_tickets(target_date, pool)
        tickets: list[list[int]] = [list(ticket) for ticket in anchor_tickets]
        seen: set[tuple[int, ...]] = set(anchor_tickets)
        for ticket in anchor_tickets:
            for number in ticket:
                exposure[number] += 1
            for pair in combinations(ticket, 2):
                pair_usage[pair] = pair_usage.get(pair, 0) + 1

        if self.max_number_usage is not None and any(
            exposure[number] > self.max_number_usage for number in pool
        ):
            raise RuntimeError("anchor tickets exceed max_number_usage")

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

        def feasible_candidates(chosen: list[int], _ticket_idx: int) -> list[int]:
            candidates = []
            for number in pool:
                if number in chosen:
                    continue
                if (
                    self.max_number_usage is not None
                    and exposure[number] >= self.max_number_usage
                ):
                    continue
                if (
                    self.max_pair_reuse is not None
                    and any(
                        pair_usage.get(tuple(sorted((number, other))), 0)
                        >= self.max_pair_reuse
                        for other in chosen
                    )
                ):
                    continue
                trial = tuple(sorted(chosen + [number]))
                if len(trial) == self.number_predict and not self._valid_shape(trial):
                    continue
                candidates.append(number)
            return candidates

        for ticket_idx in range(len(tickets), self.tickets_per_draw):
            chosen: list[int] = []
            for _slot in range(self.number_predict):
                candidates = feasible_candidates(chosen, ticket_idx)
                if not candidates:
                    # Pair reuse is a diversity constraint, not a correctness
                    # constraint. Near the end of a portfolio there can be no
                    # candidate left under a strict pair ceiling; relax only
                    # the ceiling for this slot rather than failing the forecast.
                    candidates = [
                        number for number in pool
                        if number not in chosen
                        and (
                            len(chosen) + 1 < self.number_predict
                            or self._valid_shape(
                                tuple(sorted(chosen + [number]))
                            )
                        )
                    ]
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

        # Repair any pair-cap violations introduced by the final fallback.
        # A pair limit is a portfolio-diversity constraint, so repair is done
        # after ticket generation while preserving ticket validity, exclusions,
        # and number-cap constraints.
        pair_cap = self.max_pair_reuse
        if pair_cap is not None:
            for _pass in range(len(tickets) * 3):
                pair_usage = Counter(
                    pair
                    for ticket in tickets
                    for pair in combinations(tuple(ticket), 2)
                )
                violating = sorted(
                    (pair, count)
                    for pair, count in pair_usage.items()
                    if count > pair_cap
                )
                if not violating:
                    break

                repaired_any = False
                seen_current = {tuple(ticket) for ticket in tickets}
                for over_pair, _count in violating:
                    for ticket_index, ticket_list in enumerate(tickets):
                        if ticket_index < len(anchor_tickets):
                            continue
                        ticket = tuple(sorted(ticket_list))
                        if not set(over_pair).issubset(ticket):
                            continue

                        # Prefer replacing the weaker endpoint, then fall back
                        # to either endpoint if the first choice is infeasible.
                        endpoints = sorted(
                            over_pair,
                            key=lambda n: (
                                normalized.get(n, 0.0),
                                -exposure.get(n, 0),
                                n,
                            ),
                        )
                        replacements = sorted(
                            (n for n in pool if n not in ticket),
                            key=lambda n: (
                                -normalized.get(n, 0.0),
                                -(
                                    target_exposure[n] - exposure.get(n, 0)
                                    if target_exposure.get(n, 0)
                                    else 0.0
                                ),
                                n,
                            ),
                        )

                        for old_number in endpoints:
                            for replacement in replacements:
                                if (
                                    self.max_number_usage is not None
                                    and exposure.get(replacement, 0)
                                    >= self.max_number_usage
                                ):
                                    continue

                                candidate_values = [
                                    replacement if n == old_number else n
                                    for n in ticket
                                ]
                                if len(set(candidate_values)) != self.number_predict:
                                    continue
                                candidate = tuple(sorted(candidate_values))
                                if (
                                    candidate in seen_current
                                    and candidate != ticket
                                ):
                                    continue
                                if candidate in self.excluded_sets:
                                    continue
                                if not self._valid_shape(candidate):
                                    continue

                                old_pairs = list(combinations(ticket, 2))
                                new_pairs = list(combinations(candidate, 2))
                                local_removed = Counter(old_pairs)
                                local_added = Counter(new_pairs)
                                violates = False
                                for pair, added in local_added.items():
                                    resulting = (
                                        pair_usage.get(pair, 0)
                                        - local_removed.get(pair, 0)
                                        + added
                                    )
                                    if resulting > pair_cap:
                                        violates = True
                                        break
                                if violates:
                                    continue

                                # Apply the replacement atomically.
                                for pair in old_pairs:
                                    pair_usage[pair] -= 1
                                    if pair_usage[pair] <= 0:
                                        del pair_usage[pair]
                                for pair in new_pairs:
                                    pair_usage[pair] += 1

                                exposure[old_number] -= 1
                                exposure[replacement] = exposure.get(replacement, 0) + 1
                                tickets[ticket_index] = list(candidate)
                                seen_current.discard(ticket)
                                seen_current.add(candidate)
                                repaired_any = True
                                break
                            if repaired_any:
                                break
                        if repaired_any:
                            break
                    if repaired_any:
                        break

                if not repaired_any:
                    raise RuntimeError(
                        "unable to repair portfolio repeated-pair violations"
                    )
            else:
                raise RuntimeError("pair-reuse repair exceeded iteration limit")

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
