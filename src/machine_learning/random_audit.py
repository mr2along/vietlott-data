from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path

TICKET_PRICE = 10_000
MAIN_N = 55
PICK = 6
SPECIAL_PRIZE = 3_000_000_000
JACKPOT1_PRIZE = 30_000_000_000
FIRST_PRIZE = 40_000_000
SECOND_PRIZE = 500_000
THIRD_PRIZE = 50_000
DRAWS = 1380
TICKETS_PER_DRAW = 30
SEED = 20260809


def prize(main_matches: int, special: bool) -> int:
    if main_matches == 6:
        return JACKPOT1_PRIZE
    if main_matches == 5 and special:
        return SPECIAL_PRIZE
    if main_matches == 5:
        return FIRST_PRIZE
    if main_matches == 4:
        return SECOND_PRIZE
    if main_matches == 3:
        return THIRD_PRIZE
    return 0


def theoretical_probs() -> dict[str, float]:
    den = math.comb(55, 6)
    out = {}
    for k in range(7):
        out[str(k)] = math.comb(6, k) * math.comb(49, 6-k) / den
    return out


def main() -> None:
    path = Path("artifacts/backtest_v2/power655_benchmark.jsonl")
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    if len(rows) != 1381:
        raise AssertionError(f"expected 1381 rows, got {len(rows)}")

    rng = random.Random(SEED)
    match_counts = Counter()
    special_count = 0
    prize_counts = Counter()
    unique = 0
    total = 0
    gain = 0

    # Use the actual historical target draws, but generate every ticket uniformly.
    for row in rows[1:]:
        target = set(row["result"][:6])
        special = row["result"][6]
        tickets = []
        for _ in range(TICKETS_PER_DRAW):
            ticket = tuple(sorted(rng.sample(range(1, MAIN_N + 1), PICK)))
            tickets.append(ticket)
            total += 1
            unique += 1
            matches = len(set(ticket) & target)
            has_special = matches == 5 and special in ticket
            if has_special:
                special_count += 1
            match_counts[matches] += 1
            p = prize(matches, has_special)
            prize_counts[str(p)] += 1
            gain += p
        unique -= len(tickets) - len(set(tickets))

    cost = total * TICKET_PRICE
    net = gain - cost
    roi = net / cost * 100
    mean_matches = sum(k * v for k, v in match_counts.items()) / total
    expected_mean = PICK * PICK / MAIN_N

    report = {
        "seed": SEED,
        "draws_evaluated": len(rows) - 1,
        "tickets": total,
        "tickets_per_draw": TICKETS_PER_DRAW,
        "unique_tickets": unique,
        "duplicate_tickets": total - unique,
        "duplicate_rate": (total - unique) / total,
        "match_counts": {str(k): match_counts[k] for k in range(7)},
        "special_match_count": special_count,
        "prize_counts": dict(prize_counts),
        "gain": gain,
        "cost": cost,
        "net": net,
        "roi_percent": roi,
        "mean_main_matches": mean_matches,
        "theoretical_mean_main_matches": expected_mean,
        "theoretical_match_probabilities": theoretical_probs(),
    }
    out = Path("artifacts/backtest_v2/random_audit.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
