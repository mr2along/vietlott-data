"""Backtest V2 for Power 6/55.

Separates the six main numbers from the special number and evaluates
30 independently generated tickets per historical draw.

Prize defaults use the minimum values requested for research:
- Jackpot 1: 30,000,000,000 VND (6 main numbers)
- Jackpot 2: 3,000,000,000 VND (5 main + special)
- First prize: 40,000,000 VND (5 main)
- Second prize: 500,000 VND (4 main)
- Third prize: 50,000 VND (3 main)

This module is deliberately independent of the legacy backtest revenue
logic so old results remain reproducible.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from itertools import combinations


@dataclass(frozen=True)
class PrizeConfig:
    jackpot1: int = 30_000_000_000
    jackpot2: int = 3_000_000_000
    first: int = 40_000_000
    second: int = 500_000
    third: int = 50_000
    ticket_price: int = 10_000
    tickets_per_draw: int = 30


@dataclass
class TicketResult:
    main_matches: int
    special_match: bool
    prize: int


@dataclass
class BacktestSummary:
    strategy: str
    draws: int
    tickets: int
    cost: int
    gain: int
    net_profit: int
    roi_pct: float
    average_main_matches: float
    p3_plus_pct: float
    p4_plus_pct: float
    p5_plus_pct: float
    p6_pct: float
    jackpot1_hits: int
    jackpot2_hits: int
    draws_with_p3_plus_pct: float
    duplicate_ticket_rate_pct: float
    average_unique_numbers_per_draw: float
    average_pairwise_overlap: float
    maximum_pair_reuse: int
    average_main_number_coverage_pct: float
    max_matches_stdev: float


def split_result(result: Sequence[int]) -> tuple[tuple[int, ...], int]:
    """Return (six main numbers, special number) from repository's 7-number result."""
    if len(result) != 7:
        raise ValueError(f"Power 6/55 result must contain 7 values, got {len(result)}")
    main = tuple(int(x) for x in result[:6])
    special = int(result[6])
    return main, special


def evaluate_ticket(ticket: Sequence[int], result: Sequence[int], prizes: PrizeConfig) -> TicketResult:
    """Evaluate one six-number ticket against a 6+1 Power 6/55 result."""
    if len(ticket) != 6:
        raise ValueError(f"Ticket must contain 6 values, got {len(ticket)}")
    main, special = split_result(result)
    ticket_set = {int(x) for x in ticket}
    main_matches = len(ticket_set.intersection(main))
    special_match = special in ticket_set

    if main_matches == 6:
        prize = prizes.jackpot1
    elif main_matches == 5 and special_match:
        prize = prizes.jackpot2
    elif main_matches == 5:
        prize = prizes.first
    elif main_matches == 4:
        prize = prizes.second
    elif main_matches == 3:
        prize = prizes.third
    else:
        prize = 0

    return TicketResult(main_matches, special_match, prize)


def summarize(
    strategy: str,
    results: Iterable[Sequence[int]],
    tickets_by_draw: Iterable[Iterable[Sequence[int]]],
    prizes: PrizeConfig | None = None,
) -> BacktestSummary:
    """Aggregate a strategy's walk-forward tickets and calculate ROI/statistics."""
    prizes = prizes or PrizeConfig()
    total_draws = 0
    total_tickets = 0
    gain = 0
    match_sum = 0
    p3 = p4 = p5 = p6 = 0
    jp1 = jp2 = 0
    p3_draws = duplicates = 0
    unique_numbers = overlap_sum = overlap_pairs = covered = 0
    max_pair_reuse = 0
    draw_max_matches: list[int] = []

    for result, tickets in zip(results, tickets_by_draw):
        tickets = [tuple(sorted(int(n) for n in ticket)) for ticket in tickets]
        total_draws += 1
        if tickets:
            p3_draws += max((len(set(t).intersection(result[:6])) for t in tickets), default=0) >= 3
            duplicates += len(tickets) - len(set(tickets))
            number_usage = Counter(n for t in tickets for n in t)
            unique_numbers += len(number_usage)
            pairs = Counter(pair for ticket in tickets for pair in combinations(ticket, 2))
            max_pair_reuse = max(max_pair_reuse, max(pairs.values(), default=0))
            overlaps = [len(set(a).intersection(b)) for i, a in enumerate(tickets) for b in tickets[i + 1 :]]
            overlap_sum += sum(overlaps)
            overlap_pairs += len(overlaps)
            covered += len({n for ticket in tickets for n in ticket}.intersection(result[:6])) / 6
            draw_max_matches.append(max(len(set(t).intersection(result[:6])) for t in tickets))
        for ticket in tickets:
            evaluated = evaluate_ticket(ticket, result, prizes)
            total_tickets += 1
            gain += evaluated.prize
            match_sum += evaluated.main_matches
            p3 += evaluated.main_matches >= 3
            p4 += evaluated.main_matches >= 4
            p5 += evaluated.main_matches >= 5
            p6 += evaluated.main_matches == 6
            jp1 += evaluated.main_matches == 6
            jp2 += evaluated.main_matches == 5 and evaluated.special_match

    cost = total_tickets * prizes.ticket_price
    net = gain - cost
    roi = (net / cost * 100.0) if cost else 0.0
    return BacktestSummary(
        strategy=strategy,
        draws=total_draws,
        tickets=total_tickets,
        cost=cost,
        gain=gain,
        net_profit=net,
        roi_pct=roi,
        average_main_matches=(match_sum / total_tickets) if total_tickets else 0.0,
        p3_plus_pct=(p3 / total_tickets * 100.0) if total_tickets else 0.0,
        p4_plus_pct=(p4 / total_tickets * 100.0) if total_tickets else 0.0,
        p5_plus_pct=(p5 / total_tickets * 100.0) if total_tickets else 0.0,
        p6_pct=(p6 / total_tickets * 100.0) if total_tickets else 0.0,
        jackpot1_hits=jp1,
        jackpot2_hits=jp2,
        draws_with_p3_plus_pct=(p3_draws / total_draws * 100.0) if total_draws else 0.0,
        duplicate_ticket_rate_pct=(duplicates / total_tickets * 100.0) if total_tickets else 0.0,
        average_unique_numbers_per_draw=(unique_numbers / total_draws) if total_draws else 0.0,
        average_pairwise_overlap=(overlap_sum / overlap_pairs) if overlap_pairs else 0.0,
        maximum_pair_reuse=max_pair_reuse,
        average_main_number_coverage_pct=(covered / total_draws * 100.0) if total_draws else 0.0,
        max_matches_stdev=(__import__("statistics").pstdev(draw_max_matches) if draw_max_matches else 0.0),
    )


def expected_random_average_matches() -> float:
    """Expected number of main-number matches for a random 6/55 ticket."""
    return 36 / 55


def summary_dict(summary: BacktestSummary) -> dict:
    """Return a JSON-friendly summary."""
    return asdict(summary)
