#!/usr/bin/env python3
"""Known-spectrum benchmark cards for heat-trace lower-bound smoke tests.

This is not an Arb certificate. It is a deterministic CI guard for indexing,
multiplicity, and the Markov heat-trace conversion before a heavier interval
pipeline is used.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


DEFAULT_T_VALUES = [0.005, 0.01, 0.02, 0.05, 0.1]
DEFAULT_N_VALUES = [1, 3, 8, 16, 32]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", default="outputs/spectral_benchmark_cards.json")
    parser.add_argument("--csv", default="outputs/spectral_benchmark_cards.csv")
    parser.add_argument("--max-n", type=int, default=40)
    parser.add_argument("--modes", type=int, default=220)
    parser.add_argument("--strict", action="store_true", help="Fail on any benchmark violation")
    return parser.parse_args()


def interval_dirichlet(modes: int, length: float = 1.0) -> list[float]:
    return [(math.pi * k / length) ** 2 for k in range(1, modes + 1)]


def interval_neumann(modes: int, length: float = 1.0) -> list[float]:
    return [(math.pi * k / length) ** 2 for k in range(0, modes)]


def circle_periodic(modes: int, length: float = 2.0 * math.pi) -> list[float]:
    eigs = [0.0]
    for k in range(1, modes + 1):
        lam = (2.0 * math.pi * k / length) ** 2
        eigs.extend([lam, lam])
    return sorted(eigs)


def rectangle_dirichlet(modes: int, a: float = 1.0, b: float = 1.5) -> list[float]:
    side = int(math.ceil(math.sqrt(modes * 3))) + 4
    eigs = []
    for m in range(1, side + 1):
        for n in range(1, side + 1):
            eigs.append((math.pi * m / a) ** 2 + (math.pi * n / b) ** 2)
    return sorted(eigs)[:modes]


def heat_trace(eigs: list[float], t: float) -> float:
    return sum(math.exp(-t * lam) for lam in eigs)


def heat_lower_bound(t: float, n_mass: float, tr_up: float) -> float:
    return -math.log(tr_up / n_mass) / t


def run_card(name: str, eigs: list[float], n_values: list[int], t_values: list[float]) -> list[dict[str, float | int | str]]:
    rows = []
    eigs = sorted(eigs)
    for n in n_values:
        if n < 1 or n > len(eigs):
            continue
        lam_n = eigs[n - 1]
        for t in t_values:
            tr = heat_trace(eigs, t)
            lower = heat_lower_bound(t, float(n), tr)
            margin = lam_n - lower
            rows.append(
                {
                    "family": name,
                    "n": n,
                    "t": t,
                    "lambda_n": lam_n,
                    "trace_upper_smoke": tr,
                    "lower_bound": lower,
                    "margin": margin,
                    "status": "PASS" if margin >= -1e-10 else "FAIL",
                }
            )
    return rows


def main() -> int:
    args = parse_args()
    if args.max_n < 1:
        raise ValueError("--max-n must be positive")
    modes = max(args.modes, args.max_n + 10)
    n_values = [n for n in DEFAULT_N_VALUES if n <= args.max_n]

    cards = {
        "interval_dirichlet_L1": interval_dirichlet(modes),
        "interval_neumann_L1": interval_neumann(modes),
        "circle_periodic_L2pi": circle_periodic(modes),
        "rectangle_dirichlet_1x1p5": rectangle_dirichlet(modes),
    }

    rows = []
    for name, eigs in cards.items():
        rows.extend(run_card(name, eigs, n_values, DEFAULT_T_VALUES))

    failures = [row for row in rows if row["status"] != "PASS"]
    report = {
        "status": "PASS" if not failures else "FAIL",
        "description": "Known-spectrum heat-trace lower-bound smoke tests",
        "rows": len(rows),
        "families": sorted(cards),
        "failures": failures,
    }

    json_path = Path(args.json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    csv_path = Path(args.csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = ["family", "n", "t", "lambda_n", "trace_upper_smoke", "lower_bound", "margin", "status"]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(json.dumps(report, indent=2))
    if args.strict and failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
