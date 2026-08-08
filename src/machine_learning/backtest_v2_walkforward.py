"""Leakage-safe walk-forward runner for Power 6/55 Backtest V2."""
from __future__ import annotations

import ast
import random
from dataclasses import dataclass
from typing import Any, Callable, Sequence

import pandas as pd

from .backtest_v2 import PrizeConfig, BacktestSummary, summarize


@dataclass(frozen=True)
class Draw:
    date: Any
    main: tuple[int, ...]
    special: int


def parse_draw(row: dict[str, Any]) -> Draw:
    value = row["result"]
    if isinstance(value, str):
        value = ast.literal_eval(value)
    values = tuple(int(x) for x in value)
    if len(values) != 7:
        raise ValueError(f"Power 6/55 draw must contain 7 numbers, got {len(values)}")
    return Draw(row["date"], values[:6], values[6])


def walk_forward(
    name: str,
    rows: Sequence[dict[str, Any]],
    strategy_factory: Callable[[pd.DataFrame, Any], Any],
    tickets_per_draw: int = 30,
    seed: int = 0,
    prizes: PrizeConfig | None = None,
    min_history: int = 1,
) -> BacktestSummary:
    """Generate tickets for each target draw from strictly prior main numbers.

    The strategy receives a pandas DataFrame containing only six main numbers.
    The target special number is retained only for prize evaluation.
    """
    prizes = prizes or PrizeConfig(tickets_per_draw=tickets_per_draw)
    draws = sorted((parse_draw(row) for row in rows), key=lambda d: d.date)
    random.seed(seed)

    evaluation_results: list[Sequence[int]] = []
    tickets_by_draw: list[list[Sequence[int]]] = []

    for index in range(min_history, len(draws)):
        target = draws[index]
        history_df = pd.DataFrame(
            [{"date": draw.date, "result": list(draw.main)} for draw in draws[:index]]
        )
        strategy = strategy_factory(history_df, target.date)
        tickets = [strategy.predict(target.date) for _ in range(tickets_per_draw)]
        evaluation_results.append(list(target.main) + [target.special])
        tickets_by_draw.append(tickets)

    return summarize(name, evaluation_results, tickets_by_draw, prizes)
