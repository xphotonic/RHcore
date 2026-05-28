#!/usr/bin/env python3
"""Card 5 — phase-seal
S(t) = sum_gamma (t-gamma)/((t-gamma)^2+0.25) has sign changes between zeros.
For N zeros in (0,T), S has between N and 2N-1 sign changes.
Seal check: crossings is in the valid range AND no extra equilibria exist
(S=0 and S'=0 simultaneously outside known zeros).
Success: N <= crossings <= 2*N and no extra equilibria found.
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--mesh",  type=int,   default=512)
    p.add_argument("--T",     type=float, default=35.0)
    p.add_argument("--tol",   type=float, default=1e-4)
    p.add_argument("--zeros", default="repo/data/zeros_prechecked.csv")
    p.add_argument("--out",   default="artifacts/phase_seal.json")
    return p.parse_args()


def load_zeros(path: Path) -> list[float]:
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        col = next(k for k in (reader.fieldnames or []) if k.lower() in ("t", "imag", "zero"))
        return [float(row[col]) for row in reader]


def S(t: float, gammas: list[float]) -> float:
    return sum((t - g) / ((t - g) ** 2 + 0.25) for g in gammas)


def dS(t: float, gammas: list[float]) -> float:
    return sum((0.25 - (t - g) ** 2) / ((t - g) ** 2 + 0.25) ** 2 for g in gammas)


def main() -> int:
    args     = parse_args()
    zeros    = load_zeros(Path(args.zeros))
    in_range = [g for g in zeros if 0 < g < args.T]
    N        = len(in_range)

    dt   = args.T / args.mesh
    ts   = [i * dt for i in range(args.mesh + 1)]
    vals = [S(t, zeros) for t in ts]

    crossings = sum(1 for i in range(len(vals) - 1) if vals[i] * vals[i + 1] < 0)

    # extra equilibria: S=0 and S'=0 simultaneously, not near a known zero
    extra = [
        round(ts[i], 4)
        for i in range(len(ts))
        if abs(vals[i]) < args.tol
        and abs(dS(ts[i], zeros)) < args.tol
        and all(abs(ts[i] - g) > 0.5 for g in zeros)
    ]

    range_ok = N <= crossings <= 2 * N
    extra_ok = len(extra) == 0
    status   = "PASS" if range_ok and extra_ok else "FAIL"

    result = {
        "card":     "phase-seal",
        "status":   status,
        "T":        args.T,
        "mesh":     args.mesh,
        "N_zeros":  N,
        "crossings": crossings,
        "valid_range": [N, 2 * N],
        "extra_equilibria": extra,
        "checks": {
            "crossings_in_range": range_ok,
            "no_extra_equilibria": extra_ok,
        },
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
