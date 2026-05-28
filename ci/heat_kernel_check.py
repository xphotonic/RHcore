#!/usr/bin/env python3
"""Card 3 — heat-kernel-smooth
Verifies the theta symmetry identity: theta(t) = t^{-1/2} theta(1/t).
Checks max pointwise error over a grid of t values.
Success: max|theta(t) - t^{-0.5} * theta(1/t)| < tol
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--cutoff", type=float, default=50.0)
    p.add_argument("--tol",    type=float, default=1e-8)
    p.add_argument("--terms",  type=int,   default=200)
    p.add_argument("--steps",  type=int,   default=100)
    p.add_argument("--out",    default="artifacts/heat_kernel_check.json")
    return p.parse_args()


def theta(t: float, terms: int) -> float:
    """theta(t) = 1 + 2 * sum_{n>=1} exp(-pi*n^2*t)"""
    return 1.0 + 2.0 * sum(math.exp(-math.pi * n * n * t) for n in range(1, terms + 1))


def main() -> int:
    args = parse_args()

    # sample t in (0, 1] — symmetry: theta(t) = t^{-1/2} theta(1/t)
    t_vals = [0.01 + i * (1.0 - 0.01) / args.steps for i in range(args.steps + 1)]
    errors = []
    for t in t_vals:
        lhs = theta(t, args.terms)
        rhs = t ** (-0.5) * theta(1.0 / t, args.terms)
        errors.append(abs(lhs - rhs))

    max_err = max(errors)
    status  = "PASS" if max_err < args.tol else "FAIL"

    result = {
        "card":    "heat-kernel-smooth",
        "status":  status,
        "tol":     args.tol,
        "terms":   args.terms,
        "steps":   args.steps,
        "max_symmetry_error": max_err,
        "checks":  {"symmetry_below_tol": max_err < args.tol},
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
