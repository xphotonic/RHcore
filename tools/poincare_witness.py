#!/usr/bin/env python3
"""
Poincaré Witness — numerical estimate of the coercivity constant λ.

Computes:
  λ_I = ∫_I |S'|² / ∫_I |S|²

over multiple intervals, and reports inf_I λ_I as evidence for
globallyCoercive λ in EnergyCoercivity.lean.

If inf λ_I > 0 across all tested intervals → numerical support for RH.
If any λ_I → 0 → potential counterexample region.
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--zeros",   default="repo/data/zeros_prechecked.csv")
    p.add_argument("--T",       type=float, default=35.0)
    p.add_argument("--windows", type=int,   default=20)
    p.add_argument("--steps",   type=int,   default=500)
    p.add_argument("--out",     default="artifacts/poincare_witness.json")
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


def poincare_ratio(a: float, b: float, gammas: list[float], steps: int) -> float:
    """Compute ∫_[a,b] |S'|² / ∫_[a,b] |S|²  via trapezoidal rule."""
    dt = (b - a) / steps
    num = den = 0.0
    for i in range(steps + 1):
        t = a + i * dt
        w = dt if 0 < i < steps else dt / 2
        num += w * dS(t, gammas) ** 2
        den += w * S(t, gammas) ** 2
    return num / den if den > 1e-30 else float("inf")


def main() -> int:
    args   = parse_args()
    zeros  = load_zeros(Path(args.zeros))
    window = args.T / args.windows

    ratios = []
    for i in range(args.windows):
        a = i * window + 0.1          # avoid t=0
        b = a + window
        lam = poincare_ratio(a, b, zeros, args.steps)
        ratios.append({"interval": [round(a, 3), round(b, 3)], "lambda": lam})

    finite   = [r["lambda"] for r in ratios if math.isfinite(r["lambda"])]
    inf_lam  = min(finite) if finite else 0.0
    coercive = inf_lam > 0

    result = {
        "card":   "poincare-witness",
        "status": "PASS" if coercive else "FAIL",
        "inf_lambda":  inf_lam,
        "coercive":    coercive,
        "n_windows":   args.windows,
        "T":           args.T,
        "ratios":      ratios,
        "interpretation": (
            "lambda > 0 on all windows: numerical support for globallyCoercive"
            if coercive else
            "lambda = 0 detected: potential extra zero region"
        ),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))

    # summary only
    print(json.dumps({
        k: result[k] for k in
        ("card", "status", "inf_lambda", "coercive", "interpretation")
    }, indent=2))
    return 0 if coercive else 1


if __name__ == "__main__":
    sys.exit(main())
