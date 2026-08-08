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

from dataclasses import dataclass, asdict
from typing import Iterable, Sequence


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
    first_prize_hits: int
    second_prize_hits: int
    third_prize_hits: int
    zero_match: int
    one_match: int
    two_match: int
    three_match: int
    four_match: int
    five_main_only: int
    five_plus_special: int
    six_main: int


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
    ticket_set = set(int(x) for x in ticket)
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
    """Aggregate tickets, exact prize distribution, and ROI statistics."""
    prizes = prizes or PrizeConfig()
    total_draws = 0
    total_tickets = 0
    gain = 0
    match_sum = 0
    p3 = p4 = p5 = p6 = 0
    jp1 = jp2 = first = second = third = 0
    exact = {i: 0 for i in range(7)}
    five_plus_special = 0
    five_main_only = 0

    for result, tickets in zip(results, tickets_by_draw):
        total_draws += 1
        for ticket in tickets:
            evaluated = evaluate_ticket(ticket, result, prizes)
            total_tickets += 1
            gain += evaluated.prize
            match_sum += evaluated.main_matches
            exact[evaluated.main_matches] += 1
            p3 += evaluated.main_matches >= 3
            p4 += evaluated.main_matches >= 4
            p5 += evaluated.main_matches >= 5
            p6 += evaluated.main_matches == 6

            if evaluated.main_matches == 6:
                jp1 += 1
            elif evaluated.main_matches == 5 and evaluated.special_match:
                jp2 += 1
                five_plus_special += 1
            elif evaluated.main_matches == 5:
                first += 1
                five_main_only += 1
            elif evaluated.main_matches == 4:
                second += 1
            elif evaluated.main_matches == 3:
                third += 1

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
        first_prize_hits=first,
        second_prize_hits=second,
        third_prize_hits=third,
        zero_match=exact[0],
        one_match=exact[1],
        two_match=exact[2],
        three_match=exact[3],
        four_match=exact[4],
        five_main_only=five_main_only,
        five_plus_special=five_plus_special,
        six_main=exact[6],
    )


def expected_random_average_matches() -> float:
    """Expected number of main-number matches for a random 6/55 ticket."""
    return 36 / 55


def summary_dict(summary: BacktestSummary) -> dict:
    """Return a JSON-friendly summary."""
    return asdict(summary)
