#!/usr/bin/env python3
"""
Derivative at Zeros Check — computes |S'(γ_k)| at known zeta zeros.

inf_k |S'(γ_k)| > 0  ⟺  no tangency  ⟺  RH (conditional)

Uses S(t) = -Σ_p (ln p / √p) sin(t ln p)
     S'(t) = -Σ_p (ln p)² / √p · cos(t ln p)
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--zeros",    default="repo/data/zeros_prechecked.csv")
    p.add_argument("--N-primes", type=int, default=200)
    p.add_argument("--out",      default="artifacts/derivative_at_zeros.json")
    return p.parse_args()


def sieve(n: int) -> list[int]:
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, n+1, i):
                is_p[j] = False
    return [i for i in range(2, n+1) if is_p[i]]


def first_n_primes(n: int) -> list[int]:
    upper = max(30, int(n * (math.log(n+2) + math.log(math.log(n+3))) * 1.5))
    return sieve(upper)[:n]


def S(t: float, primes: list[int]) -> float:
    return -sum((math.log(p)/math.sqrt(p)) * math.sin(t * math.log(p))
                for p in primes)


def dS(t: float, primes: list[int]) -> float:
    return -sum((math.log(p)**2/math.sqrt(p)) * math.cos(t * math.log(p))
                for p in primes)


def load_zeros(path: Path) -> list[float]:
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        col = next(k for k in (reader.fieldnames or [])
                   if k.lower() in ("t", "imag", "zero"))
        return [float(row[col]) for row in reader]


def main() -> int:
    args   = parse_args()
    gammas = load_zeros(Path(args.zeros))
    primes = first_n_primes(args.N_primes)

    data = []
    for gamma in gammas:
        s_val  = S(gamma, primes)
        ds_val = dS(gamma, primes)
        data.append({
            "gamma":    gamma,
            "S_gamma":  s_val,
            "dS_gamma": ds_val,
            "abs_dS":   abs(ds_val),
            "S_near_zero": abs(s_val) < 0.5,
        })

    abs_dS_vals = [d["abs_dS"] for d in data]
    inf_dS      = min(abs_dS_vals)
    mean_dS     = sum(abs_dS_vals) / len(abs_dS_vals)
    all_nonzero = all(v > 1e-6 for v in abs_dS_vals)

    result = {
        "card":    "derivative-at-zeros",
        "status":  "PASS" if all_nonzero else "FAIL",
        "N_zeros": len(gammas),
        "N_primes": len(primes),
        "inf_abs_dS":  inf_dS,
        "mean_abs_dS": mean_dS,
        "all_nonzero": all_nonzero,
        "data": data,
        "interpretation": (
            f"inf_k |S'(γ_k)| = {inf_dS:.6f} > 0 — no tangency detected"
            if all_nonzero else
            "tangency detected — S'(γ_k) ≈ 0 at some zero"
        ),
        "note": (
            "S(t) built from finite primes — not exact ζ. "
            "inf > 0 is numerical evidence, not proof."
        ),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in
          ("card", "status", "inf_abs_dS", "mean_abs_dS",
           "all_nonzero", "interpretation")}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
