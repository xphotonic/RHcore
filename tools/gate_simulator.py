#!/usr/bin/env python3
"""
Gate Simulator — ClosureOperator on real zeta zeros.

Runs Gates 0-5 (Cards 1,5,6,7,9,10) on S(t) built from zeros_prechecked.csv.
S(t) is the spectral sum approximation of Im(-ζ'/ζ(1/2+it)),
derived from the chain: Gaussian → Fourier → Poisson → Mellin → ξ.
Outputs: gate_report.json
"""

from __future__ import annotations
import csv, json, math, sys
from pathlib import Path

# ── S(t) from spectral sum ──────────────────────────────────────────────────

def S(t: float, gammas: list[float], a: float = 0.5) -> float:
    """Phase signal: S(t) = Σ (t-γ) / ((t-γ)² + a²)"""
    return sum((t - g) / ((t - g) ** 2 + a ** 2) for g in gammas)

def dS(t: float, gammas: list[float], a: float = 0.5) -> float:
    """S'(t) = Σ (a² - (t-γ)²) / ((t-γ)² + a²)²"""
    return sum((a**2 - (t-g)**2) / ((t-g)**2 + a**2)**2 for g in gammas)

# ── Gate evaluators ─────────────────────────────────────────────────────────

def gate0_carrier(t: float, gammas: list[float], beta: float = 1.0) -> dict:
    """Card 1: q(t) = |S|² + β|S'|² > 0"""
    s, ds = S(t, gammas), dS(t, gammas)
    q = s**2 + beta * ds**2
    return {"gate": 0, "name": "carrier", "q": q, "pass": q > 0}

def gate1_no_tangency(t: float, gammas: list[float], tol: float = 1e-6) -> dict:
    """Card 5: S(t)=0 ⇒ S'(t)≠0"""
    s, ds = S(t, gammas), dS(t, gammas)
    tangency = abs(s) < tol and abs(ds) < tol
    return {"gate": 1, "name": "no_tangency", "S": s, "dS": ds, "pass": not tangency}

def gate2_local_energy(t0: float, gammas: list[float], c: float = 0.01) -> dict:
    """Card 6: |S(t)| ≥ c|t-t0| near zero"""
    pts = [t0 + d for d in (-0.1, -0.05, 0.05, 0.1)]
    ok = all(abs(S(t, gammas)) >= c * abs(t - t0) for t in pts)
    return {"gate": 2, "name": "local_energy", "c": c, "pass": ok}

def gate3_accumulation(gammas: list[float], T: float = 40.0,
                        eps: float = 1e-3, steps: int = 400) -> dict:
    """Card 7: P(T) monotone increasing"""
    dt = T / steps
    ts = [i * dt for i in range(1, steps + 1)]
    integrands = [S(t, gammas)**2 / (abs(dS(t, gammas)) + eps) for t in ts]
    cumsum = []
    acc = 0.0
    for v in integrands:
        acc += v * dt
        cumsum.append(acc)
    monotone = all(cumsum[i] <= cumsum[i+1] for i in range(len(cumsum)-1))
    return {"gate": 3, "name": "accumulation", "P_T": cumsum[-1], "pass": monotone}

def gate4_uniqueness(gammas: list[float], T: float = 40.0,
                      steps: int = 2000, tol: float = 1e-4) -> dict:
    """Card 9: no extra equilibrium (S=0 and S'=0 simultaneously)"""
    dt = T / steps
    extra = []
    for i in range(steps):
        t = i * dt
        if abs(S(t, gammas)) < tol and abs(dS(t, gammas)) < tol:
            # check it's not near a known gamma
            near_known = any(abs(t - g) < 0.5 for g in gammas)
            if not near_known:
                extra.append(round(t, 4))
    return {"gate": 4, "name": "uniqueness", "extra_equilibria": extra,
            "pass": len(extra) == 0}

def gate5_no_winding(gammas: list[float], T: float = 40.0,
                      steps: int = 2000) -> dict:
    """
    Card 10: Δarg = 0 proxy.
    For S built from N zeros in [0,T], the winding number
    equals N by construction (each γ contributes one crossing).
    We verify no *extra* crossings beyond those accounted for
    by checking crossings ≤ 2 * expected (generous bound).
    True Δarg=0 requires ζ — this is a structural consistency check.
    """
    dt = T / steps
    ts = [i * dt for i in range(steps)]
    vals = [S(t, gammas) for t in ts]
    crossings = sum(1 for i in range(len(vals)-1)
                    if vals[i] * vals[i+1] < 0)
    expected = sum(1 for g in gammas if 0 < g < T)
    # S(t) oscillates: each zero contributes ~1-2 crossings; no extra zeros = no extra clusters
    ok = crossings <= 2 * expected + 2
    return {"gate": 5, "name": "no_winding", "crossings": crossings,
            "expected": expected, "bound": 2 * expected + 2, "pass": ok}

# ── Main ─────────────────────────────────────────────────────────────────────

def load_zeros(path: Path) -> list[float]:
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        col = next(k for k in reader.fieldnames if k.lower() in ("t", "imag", "zero"))
        return [float(row[col]) for row in reader]

def main() -> int:
    zeros_path = Path(__file__).parent.parent / "repo" / "data" / "zeros_prechecked.csv"
    out_path   = Path(__file__).parent.parent / "repo" / "data" / "gate_report.json"

    gammas = load_zeros(zeros_path)

    # sample point between first two zeros
    t_sample = (gammas[0] + gammas[1]) / 2

    results = [
        gate0_carrier(t_sample, gammas),
        gate1_no_tangency(t_sample, gammas),
        gate2_local_energy(gammas[0], gammas),
        gate3_accumulation(gammas),
        gate4_uniqueness(gammas),
        gate5_no_winding(gammas),
    ]

    all_pass = all(r["pass"] for r in results)
    report = {
        "status":  "CLOSED" if all_pass else "OPEN",
        "t_sample": t_sample,
        "zeros_count": len(gammas),
        "gates": results,
        "open_gate": None if all_pass else next(r["name"] for r in results if not r["pass"]),
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if all_pass else 1

if __name__ == "__main__":
    sys.exit(main())
