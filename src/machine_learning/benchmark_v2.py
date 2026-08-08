"""Benchmark entrypoint for corrected Power 6/55 Backtest V2.

This module deliberately provides the common benchmark contract without
silently changing existing strategy implementations. Concrete adapters should
construct each strategy from six-main-number-only history and call
``predict(target_date)`` 30 times per target draw.
"""
from __future__ import annotations

from dataclasses import asdict
from .backtest_v2 import PrizeConfig, BacktestSummary
from .backtest_v2_walkforward import walk_forward


DEFAULT_PRIZES = PrizeConfig(
    jackpot1=30_000_000_000,
    jackpot2=3_000_000_000,
    first=40_000_000,
    second=500_000,
    third=50_000,
    ticket_price=10_000,
    tickets_per_draw=30,
)


def benchmark_strategy(name, rows, strategy_factory, seed=0):
    """Run one strategy with the agreed minimum-prize configuration."""
    summary = walk_forward(
        name=name,
        rows=rows,
        strategy_factory=strategy_factory,
        tickets_per_draw=DEFAULT_PRIZES.tickets_per_draw,
        seed=seed,
        prizes=DEFAULT_PRIZES,
    )
    return asdict(summary)
