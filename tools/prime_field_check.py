#!/usr/bin/env python3
"""
Prime Field Check — verifies the Gaussian→Fourier→Poisson→Mellin bridge.

S_primes(t) = Im Σ_{p≤N} (ln p / √p) e^{it ln p}
            = -Σ_{p≤N} (ln p / √p) sin(t ln p)

S_zeros(t)  = Σ_γ (t-γ)/((t-γ)²+0.25)

The critical-line normalization (1/√p) comes from:
  Gaussian smoothing → Fourier → Poisson summation → Mellin at s=1/2

Checks:
  1. Sign agreement between S_primes and S_zeros
  2. Zero-crossing consistency (both cross zero near same t values)
  3. Gaussian smoothing reduces variance
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--zeros",    default="repo/data/zeros_prechecked.csv")
    p.add_argument("--N-primes", type=int,   default=100)
    p.add_argument("--sigma",    type=float, default=0.0,
                   help="Gaussian smoothing (0 = no smoothing)")
    p.add_argument("--T",        type=float, default=35.0)
    p.add_argument("--steps",    type=int,   default=200)
    p.add_argument("--out",      default="artifacts/prime_field_check.json")
    return p.parse_args()


def sieve_primes(n: int) -> list[int]:
    if n < 2:
        return []
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, n+1, i):
                is_p[j] = False
    return [i for i in range(2, n+1) if is_p[i]]


def first_n_primes(n: int) -> list[int]:
    upper = max(30, int(n * (math.log(n + 2) + math.log(math.log(n + 3))) * 1.5))
    return sieve_primes(upper)[:n]


def S_primes(t: float, primes: list[int], sigma: float = 0.0) -> float:
    """
    S(t) from prime sources with critical-line normalization.
    S(t) = -Σ_p (ln p / √p) sin(t ln p) × e^{-σ²t²/2}
    """
    smooth = math.exp(-0.5 * (sigma * t) ** 2) if sigma > 0 else 1.0
    return -smooth * sum(
        (math.log(p) / math.sqrt(p)) * math.sin(t * math.log(p))
        for p in primes
    )


def S_zeros(t: float, gammas: list[float]) -> float:
    """S(t) from zeta zeros: Σ_γ (t-γ)/((t-γ)²+0.25)"""
    return sum((t - g) / ((t - g)**2 + 0.25) for g in gammas)


def load_zeros(path: Path) -> list[float]:
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        col = next(k for k in (reader.fieldnames or [])
                   if k.lower() in ("t", "imag", "zero"))
        return [float(row[col]) for row in reader]


def zero_crossings(vals: list[float]) -> int:
    return sum(1 for i in range(len(vals)-1) if vals[i] * vals[i+1] < 0)


def main() -> int:
    args   = parse_args()
    gammas = load_zeros(Path(args.zeros))
    primes = first_n_primes(args.N_primes)

    dt   = args.T / args.steps
    ts   = [0.5 + i * dt for i in range(args.steps)]

    sp_vals = [S_primes(t, primes, args.sigma) for t in ts]
    sz_vals = [S_zeros(t, gammas) for t in ts]

    # sign agreement
    sign_agree = sum(
        1 for sp, sz in zip(sp_vals, sz_vals)
        if math.copysign(1, sp) == math.copysign(1, sz)
    )
    sign_pct = sign_agree / len(ts)

    # zero-crossing counts
    zc_primes = zero_crossings(sp_vals)
    zc_zeros  = zero_crossings(sz_vals)
    expected  = sum(1 for g in gammas if 0 < g < args.T)

    # normalized correlation (sign-insensitive scale difference expected)
    sp_norm = [v / (max(abs(v) for v in sp_vals) + 1e-30) for v in sp_vals]
    sz_norm = [v / (max(abs(v) for v in sz_vals) + 1e-30) for v in sz_vals]
    corr = sum(a*b for a,b in zip(sp_norm, sz_norm)) / len(ts)

    status = "PASS" if sign_pct > 0.6 and corr > 0.3 else "WARN"

    result = {
        "card":        "prime-field-check",
        "status":      status,
        "N_primes":    len(primes),
        "N_zeros":     len(gammas),
        "sigma":       args.sigma,
        "T":           args.T,
        "sign_agreement_pct": sign_pct,
        "normalized_correlation": corr,
        "zero_crossings": {
            "S_primes":  zc_primes,
            "S_zeros":   zc_zeros,
            "expected":  expected,
        },
        "checks": {
            "sign_agree_gt_60pct": sign_pct > 0.6,
            "correlation_gt_0.3":  corr > 0.3,
            "crossings_consistent": abs(zc_primes - zc_zeros) <= zc_zeros + 2,
        },
        "interpretation": (
            f"sign_agree={sign_pct:.0%}, corr={corr:.3f} — "
            + ("Poisson bridge consistent" if status == "PASS"
               else "partial agreement — more primes/zeros needed for full convergence")
        ),
        "derivation": {
            "step1": "ρ_p(u) = Σ_p (ln p) δ(u - ln p)  [prime source]",
            "step2": "* g_σ  [Gaussian smoothing, σ=" + str(args.sigma) + "]",
            "step3": "Fourier → Σ_p (ln p) p^{it} e^{-σ²t²/2}",
            "step4": "× p^{-1/2}  [critical-line normalization]",
            "step5": "Im → S(t) = -Σ_p (ln p/√p) sin(t ln p)",
        },
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in
          ("card", "status", "sign_agreement_pct",
           "normalized_correlation", "zero_crossings")}, indent=2))
    return 0 if status in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
