from __future__ import annotations

import json
import math
import random
from pathlib import Path

TICKET_PRICE = 10_000
TICKETS_PER_DRAW = 30
SEED = 20260809


def prize(matches: int, special_hit: bool) -> int:
    if matches == 6:
        return 30_000_000_000
    if matches == 5 and special_hit:
        return 3_000_000_000
    if matches == 5:
        return 40_000_000
    if matches == 4:
        return 500_000
    if matches == 3:
        return 50_000
    return 0


def load_targets() -> list[tuple[set[int], int]]:
    path = Path("artifacts/backtest_v2/power655_benchmark.jsonl")
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows) != 1381 or not all(len(r["result"]) == 7 for r in rows):
        raise ValueError("Benchmark must contain exactly 1381 complete 7-number rows")
    return [(set(r["result"][:6]), int(r["result"][6])) for r in rows[1:]]


def main() -> None:
    targets = load_targets()
    rng = random.Random(SEED)
    match_counts = {i: 0 for i in range(7)}
    special_hits = 0
    gain = 0
    winning_tickets = 0
    for target, special in targets:
        for _ in range(TICKETS_PER_DRAW):
            ticket = set(rng.sample(range(1, 56), 6))
            matches = len(ticket & target)
            is_special = special in ticket
            match_counts[matches] += 1
            special_hits += int(is_special)
            p = prize(matches, is_special)
            gain += p
            winning_tickets += int(p > 0)

    tickets = len(targets) * TICKETS_PER_DRAW
    cost = tickets * TICKET_PRICE
    theoretical = {
        str(k): math.comb(6, k) * math.comb(49, 6 - k) / math.comb(55, 6)
        for k in range(7)
    }
    observed = {str(k): v / tickets for k, v in match_counts.items()}
    report = {
        "seed": SEED,
        "draws": len(targets),
        "tickets": tickets,
        "tickets_per_draw": TICKETS_PER_DRAW,
        "cost_vnd": cost,
        "gain_vnd": gain,
        "net_profit_vnd": gain - cost,
        "roi_percent": (gain - cost) / cost * 100.0,
        "winning_tickets": winning_tickets,
        "special_hits": special_hits,
        "match_counts": match_counts,
        "observed_match_probability": observed,
        "theoretical_match_probability": theoretical,
        "audit": {
            "uses_main_six_only_for_target": True,
            "uses_special_only_for_prize": True,
            "target_draw_excluded_from_history": True,
        },
    }
    out = Path("artifacts/backtest_v2")
    out.mkdir(parents=True, exist_ok=True)
    (out / "random_audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
