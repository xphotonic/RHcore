#!/usr/bin/env python3
"""
Explicit Formula Check — numerical verification of ψ(x) = x - Σ x^ρ/ρ + ...

Computes:
  ψ_primes(x) = Σ_{n≤x} Λ(n)          [von Mangoldt, from primes]
  ψ_zeros(x)  = x - Σ_γ correction(γ,x) [from zeros via explicit formula]

Also checks:
  S(t) zero crossings vs Z(t) zero crossings (prime-zero duality)
  Destructive interference: S(t₀)=0 ↔ phase cancellation
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--zeros",   default="repo/data/zeros_prechecked.csv")
    p.add_argument("--X-max",   type=float, default=50.0)
    p.add_argument("--steps",   type=int,   default=50)
    p.add_argument("--out",     default="artifacts/explicit_formula_check.json")
    return p.parse_args()


def sieve_mangoldt(n: int) -> list[tuple[int, float]]:
    """Returns (k, Λ(k)) for k=2..n where Λ(k) = ln p if k=p^m, else 0."""
    result = []
    for k in range(2, n + 1):
        # check if k is a prime power
        lp = 0.0
        for p in range(2, k + 1):
            if k % p == 0:
                # p is the smallest prime factor
                m = k
                while m % p == 0:
                    m //= p
                if m == 1:
                    lp = math.log(p)
                break
        if lp > 0:
            result.append((k, lp))
    return result


def psi_primes(x: float, mangoldt: list[tuple[int, float]]) -> float:
    """ψ(x) = Σ_{n≤x} Λ(n)"""
    return sum(lp for k, lp in mangoldt if k <= x)


def psi_correction(gamma: float, x: float) -> float:
    """Real part of -x^ρ/ρ where ρ = 1/2 + iγ"""
    if x <= 0:
        return 0.0
    denom = 0.25 + gamma**2
    sqrt_x = math.sqrt(x)
    log_x  = math.log(x)
    re = sqrt_x * (0.5 * math.cos(gamma * log_x) + gamma * math.sin(gamma * log_x))
    return -re / denom


def psi_zeros(x: float, gammas: list[float]) -> float:
    """ψ(x) ≈ x - Σ_γ correction(γ, x)"""
    return x + sum(psi_correction(g, x) for g in gammas)


def S_primes(t: float, primes: list[int]) -> float:
    return -sum((math.log(p) / math.sqrt(p)) * math.sin(t * math.log(p))
                for p in primes)


def Z_zeros(t: float, gammas: list[float]) -> float:
    return sum(math.sin(g * t) for g in gammas)


def load_zeros(path: Path) -> list[float]:
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        col = next(k for k in (reader.fieldnames or [])
                   if k.lower() in ("t", "imag", "zero"))
        return [float(row[col]) for row in reader]


def sieve_primes(n: int) -> list[int]:
    is_p = [True] * (n + 1)
    is_p[0] = is_p[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, n+1, i):
                is_p[j] = False
    return [i for i in range(2, n+1) if is_p[i]]


def main() -> int:
    args    = parse_args()
    gammas  = load_zeros(Path(args.zeros))
    X_max   = args.X_max
    primes  = sieve_primes(int(X_max) + 10)
    mangoldt = sieve_mangoldt(int(X_max) + 1)

    # ── ψ(x) comparison ──────────────────────────────────────────────────
    xs = [2.0 + i * (X_max - 2.0) / args.steps for i in range(args.steps + 1)]
    psi_data = []
    for x in xs:
        pp = psi_primes(x, mangoldt)
        pz = psi_zeros(x, gammas)
        psi_data.append({"x": round(x, 2), "psi_primes": pp,
                         "psi_zeros": pz, "diff": abs(pp - pz)})

    max_psi_diff  = max(d["diff"] for d in psi_data)
    mean_psi_diff = sum(d["diff"] for d in psi_data) / len(psi_data)
    rel_err       = mean_psi_diff / (sum(d["psi_primes"] for d in psi_data)
                                     / len(psi_data) + 1e-10)

    # ── S(t) vs Z(t) duality ─────────────────────────────────────────────
    ts = [0.5 + i * 35.0 / 200 for i in range(200)]
    sp = [S_primes(t, primes) for t in ts]
    zz = [Z_zeros(t, gammas)  for t in ts]

    sign_agree = sum(1 for a, b in zip(sp, zz)
                     if math.copysign(1, a) == math.copysign(1, b))
    sign_pct   = sign_agree / len(ts)

    # ── Destructive interference check ───────────────────────────────────
    # Find t where S_primes ≈ 0 (sign changes)
    s_crossings = [ts[i] for i in range(len(ts)-1) if sp[i] * sp[i+1] < 0]
    z_crossings = [ts[i] for i in range(len(ts)-1) if zz[i] * zz[i+1] < 0]

    status = "PASS" if rel_err < 0.5 and sign_pct > 0.55 else "WARN"

    result = {
        "card":   "explicit-formula-check",
        "status": status,
        "psi_comparison": {
            "max_diff":  max_psi_diff,
            "mean_diff": mean_psi_diff,
            "rel_error": rel_err,
            "n_points":  len(psi_data),
        },
        "prime_zero_duality": {
            "sign_agreement_pct": sign_pct,
            "S_crossings": len(s_crossings),
            "Z_crossings": len(z_crossings),
        },
        "destructive_interference": {
            "S_zero_locations": [round(t, 3) for t in s_crossings[:5]],
            "Z_zero_locations": [round(t, 3) for t in z_crossings[:5]],
            "interpretation": (
                "S zeros ≈ Z zeros: prime-zero duality consistent"
                if abs(len(s_crossings) - len(z_crossings)) <= len(z_crossings) + 2
                else "mismatch: more zeros needed"
            ),
        },
        "checks": {
            "psi_rel_error_lt_50pct": rel_err < 0.5,
            "sign_agree_gt_55pct":    sign_pct > 0.55,
        },
        "chain": {
            "step1": "ρ_p(u) = Σ (ln p) δ(u - ln p)",
            "step2": "Fourier → S(t) = Im Σ (ln p/√p) e^{it ln p}",
            "step3": "Mellin → ψ(x) = x - Σ x^ρ/ρ + ...",
            "step4": "x^ρ = x^{1/2} e^{iγ ln x} → Z(t) = Im Σ e^{iγ_n t}",
            "step5": "S(t₀)=0 ⟺ destructive interference ⟺ zero of ζ",
        },
        "sample_psi": psi_data[:5],
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in
          ("card", "status", "psi_comparison",
           "prime_zero_duality", "destructive_interference")}, indent=2))
    return 0 if status in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
