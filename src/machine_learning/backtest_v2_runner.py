"""Walk-forward runner for the Power 6/55 Backtest V2.

The runner intentionally feeds each strategy only the six main numbers from
historical results. It evaluates 30 independently generated tickets against
the next historical draw using :mod:`backtest_v2`.
"""
from __future__ import annotations

import random
from datetime import date
from typing import Any, Callable, Sequence

from .backtest_v2 import PrizeConfig, BacktestSummary, summarize


def _main_only_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    cleaned: list[dict[str, Any]] = []
    for row in rows:
        result = row["result"]
        if isinstance(result, str):
            result = [int(x) for x in result.strip("[]").split(",") if x.strip()]
        if len(result) != 7:
            continue
        cleaned.append({**row, "result": list(map(int, result[:6])), "special": int(result[6])})
    return cleaned


def run_strategy(
    name: str,
    strategy_factory: Callable[[Any], Any],
    df: Any,
    results: Sequence[Sequence[int]],
    tickets_per_draw: int = 30,
    seed: int = 0,
    prizes: PrizeConfig | None = None,
) -> BacktestSummary:
    """Run a strategy in walk-forward mode.

    ``strategy_factory`` receives the history dataframe available before the
    current target draw. ``predict()`` is called once per ticket, preserving
    the original strategy randomness while preventing future-data leakage.
    """
    prizes = prizes or PrizeConfig(tickets_per_draw=tickets_per_draw)
    random.seed(seed)
    tickets_by_draw: list[list[Sequence[int]]] = []
    evaluation_results: list[Sequence[int]] = []

    # This function is a reusable adapter. Concrete repository integrations
    # can supply a dataframe slice and factory while retaining the corrected
    # 6+1 evaluation logic.
    for i in range(1, len(results)):
        history = df.iloc[:i] if hasattr(df, "iloc") else df[:i]
        strategy = strategy_factory(history)
        draw_tickets = [strategy.predict(date.today()) for _ in range(tickets_per_draw)]
        tickets_by_draw.append(draw_tickets)
        evaluation_results.append(list(results[i]) + [0])

    return summarize(name, evaluation_results, tickets_by_draw, prizes)
