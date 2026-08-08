"""Leakage-safe walk-forward runner for Power 6/55 Backtest V2."""
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .backtest_v2 import PrizeConfig, BacktestSummary, summarize


@dataclass(frozen=True)
class Draw:
    date: Any
    main: tuple[int, ...]
    special: int


def parse_draw(row: dict[str, Any]) -> Draw:
    result = row["result"]
    if isinstance(result, str):
        import ast
        result = ast.literal_eval(result)
    values = tuple(int(x) for x in result)
    if len(values) != 7:
        raise ValueError(f"Expected 7 result numbers, got {len(values)}")
    return Draw(row["date"], values[:6], values[6])


def walk_forward(
    name: str,
    rows: Sequence[dict[str, Any]],
    strategy_factory: Callable[[Sequence[dict[str, Any]], Any], Any],
    tickets_per_draw: int = 30,
    seed: int = 0,
    prizes: PrizeConfig | None = None,
    min_history: int = 1,
) -> BacktestSummary:
    """Generate tickets for each target using strictly earlier draws only."""
    prizes = prizes or PrizeConfig(tickets_per_draw=tickets_per_draw)
    draws = [parse_draw(r) for r in rows]
    draws.sort(key=lambda d: d.date)
    random.seed(seed)

    evaluation_results: list[Sequence[int]] = []
    tickets_by_draw: list[list[Sequence[int]]] = []

    for i in range(min_history, len(draws)):
        target = draws[i]
        history = [{"date": d.date, "result": list(d.main)} for d in draws[:i]]
        strategy = strategy_factory(history, target.date)
        tickets = [strategy.predict(target.date) for _ in range(tickets_per_draw)]
        evaluation_results.append(list(target.main) + [target.special])
        tickets_by_draw.append(tickets)

    return summarize(name, evaluation_results, tickets_by_draw, prizes)
