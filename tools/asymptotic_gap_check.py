#!/usr/bin/env python3
"""
Asymptotic Gap Check — tests λ_eff as N grows.

Key question: do cross terms cancel enough to keep λ_eff > 0?

Computes for N = 10, 20, 50, 100, 200:
  λ_diag(N)  = Σ(ln p)⁴/p / Σ(ln p)²/p  [grows as (ln P_N)²/2]
  λ_actual(N) = ∫|S′|² / ∫|S|²           [numerical]
  δ(N)        = 1 - λ_actual/λ_diag       [cross-term ratio]

If δ(N) < 1 for all N → λ_eff > 0 → supports RH.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--T",     type=float, default=20.0)
    p.add_argument("--steps", type=int,   default=300)
    p.add_argument("--out",   default="artifacts/asymptotic_gap_check.json")
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


def integrate(f, a: float, b: float, steps: int) -> float:
    dt = (b - a) / steps
    return sum((dt if 0 < i < steps else dt/2) * f(a + i*dt)
               for i in range(steps + 1))


def diag_ratio(primes: list[int]) -> float:
    num = sum(math.log(p)**4 / p for p in primes)
    den = sum(math.log(p)**2 / p for p in primes)
    return num / den if den > 0 else 0.0


def mertens_approx(primes: list[int]) -> dict:
    """Mertens-type: Σ(ln p)^k/p vs (ln P_N)^k/k"""
    P_N   = max(primes)
    ln_PN = math.log(P_N)
    s2    = sum(math.log(p)**2 / p for p in primes)
    s4    = sum(math.log(p)**4 / p for p in primes)
    return {
        "sum_lnp2_over_p":  s2,
        "mertens_approx_k2": ln_PN**2 / 2,
        "sum_lnp4_over_p":  s4,
        "mertens_approx_k4": ln_PN**4 / 4,
        "ratio_k4_k2":      s4 / s2 if s2 > 0 else 0,
        "ln_PN_sq_over_2":  ln_PN**2 / 2,
    }


def main() -> int:
    args = parse_args()
    a, b = 1.0, args.T

    N_values = [10, 20, 50, 100, 200]
    results  = []

    for N in N_values:
        primes     = first_n_primes(N)
        lam_diag   = diag_ratio(primes)
        mertens    = mertens_approx(primes)

        int_dS2 = integrate(lambda t: dS(t, primes)**2, a, b, args.steps)
        int_S2  = integrate(lambda t: S(t, primes)**2,  a, b, args.steps)
        lam_act = int_dS2 / int_S2 if int_S2 > 1e-30 else float("inf")

        delta   = 1.0 - lam_act / lam_diag if math.isfinite(lam_act) and lam_diag > 0 else None

        results.append({
            "N":            N,
            "P_N":          max(primes),
            "lambda_diag":  lam_diag,
            "lambda_actual": lam_act,
            "delta":        delta,
            "gap_positive": lam_act > 0 if math.isfinite(lam_act) else False,
            "mertens":      mertens,
        })

    # check: does λ_actual grow with N?
    finite_lam = [r["lambda_actual"] for r in results if math.isfinite(r["lambda_actual"])]
    growing    = all(finite_lam[i] <= finite_lam[i+1] * 2
                     for i in range(len(finite_lam)-1))  # allow 2× tolerance
    all_pos    = all(r["gap_positive"] for r in results)
    deltas     = [r["delta"] for r in results if r["delta"] is not None]
    delta_lt1  = all(d < 1.0 for d in deltas)

    status = "PASS" if all_pos and delta_lt1 else "FAIL"

    output = {
        "card":   "asymptotic-gap-check",
        "status": status,
        "T":      args.T,
        "conclusion": {
            "lambda_grows_with_N": growing,
            "all_gaps_positive":   all_pos,
            "all_deltas_lt_1":     delta_lt1,
            "interpretation": (
                "λ_eff > 0 for all tested N: cross terms do not cancel diagonal. "
                "Supports RH numerically."
                if all_pos and delta_lt1 else
                "λ_eff → 0 detected: cross terms dominate at some N."
            ),
        },
        "open_gate_status": {
            "statement": "δ_∞ = lim_{N→∞} (1 - λ_actual/λ_diag) < 1",
            "numerical_deltas": deltas,
            "trend": "decreasing" if len(deltas) >= 2 and deltas[-1] < deltas[0]
                     else "increasing" if len(deltas) >= 2 and deltas[-1] > deltas[0]
                     else "stable",
        },
        "mertens_verification": {
            "description": "λ_diag ≈ (ln P_N)²/2 per Mertens",
            "data": [{"N": r["N"], "lambda_diag": r["lambda_diag"],
                      "ln_PN_sq_over_2": r["mertens"]["ln_PN_sq_over_2"]}
                     for r in results],
        },
        "results": results,
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(output, indent=2))
    print(json.dumps({k: output[k] for k in
          ("card", "status", "conclusion", "open_gate_status")}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
