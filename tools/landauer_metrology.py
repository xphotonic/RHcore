#!/usr/bin/env python3
"""
Landauer Metrology — NIST-style uncertainty budget for bit erasure tests.

Implements:
  1. Point estimate: E_mean vs kT·ln2
  2. Type A uncertainty: statistical (std error of mean)
  3. Type B uncertainty: systematic sources (calibration, bath coupling, control noise)
  4. Combined uncertainty: u_c = sqrt(u_A² + u_B²)
  5. Coverage interval: [E_mean - k·u_c, E_mean + k·u_c]  (k=2, ~95%)
  6. Landauer ratio: E_mean / (kT·ln2) with uncertainty
  7. Dimensionless invariant: Ω = E·τ / (kT·ln2·τ_min)  [ResearchGate benchmark]
  8. Double-well protocol: work/heat decomposition from trajectory data
  9. Protocol efficiency: η = kT·ln2 / E_mean  (1.0 = ideal Landauer)

References:
  arXiv:1503.06537  — optical trap double-well erasure
  arXiv:2102.09925  — underdamped oscillator, ~1% uncertainty
  ResearchGate:400901723 — dimensionless invariant benchmark
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path
from typing import NamedTuple


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--trace",       required=True, help="CSV with energy column")
    p.add_argument("--energy-col",  default="energy")
    p.add_argument("--work-col",    default="",    help="Optional work column for W/Q decomposition")
    p.add_argument("--time-col",    default="",    help="Optional time column for duration τ")
    p.add_argument("--kT",          type=float, default=4.1e-21,
                   help="Thermal energy kT in Joules (room temp default)")
    p.add_argument("--tau-min",     type=float, default=0.0,
                   help="Minimum protocol duration τ_min for dimensionless invariant")
    p.add_argument("--u-cal",       type=float, default=0.02)
    p.add_argument("--u-bath",      type=float, default=0.01)
    p.add_argument("--u-control",   type=float, default=0.01)
    p.add_argument("--coverage",    type=float, default=2.0)
    p.add_argument("--out",         default="artifacts/landauer_budget.json")
    return p.parse_args()


class UncertaintyBudget(NamedTuple):
    n:            int
    mean:         float
    std:          float
    u_A:          float
    u_B_cal:      float
    u_B_bath:     float
    u_B_control:  float
    u_B:          float
    u_c:          float
    U:            float
    lo:           float
    hi:           float


def compute_budget(energies: list[float],
                   u_cal: float, u_bath: float, u_control: float,
                   k: float) -> UncertaintyBudget:
    n    = len(energies)
    mean = sum(energies) / n
    var  = sum((e - mean) ** 2 for e in energies) / max(n - 1, 1)
    std  = math.sqrt(var)
    u_A  = std / math.sqrt(n)
    u_B_cal     = u_cal     * mean
    u_B_bath    = u_bath    * mean
    u_B_control = u_control * mean
    u_B  = math.sqrt(u_B_cal**2 + u_B_bath**2 + u_B_control**2)
    u_c  = math.sqrt(u_A**2 + u_B**2)
    U    = k * u_c
    return UncertaintyBudget(
        n=n, mean=mean, std=std,
        u_A=u_A, u_B_cal=u_B_cal, u_B_bath=u_B_bath, u_B_control=u_B_control,
        u_B=u_B, u_c=u_c, U=U, lo=mean - U, hi=mean + U,
    )


def double_well_decompose(energies: list[float],
                          works: list[float]) -> dict:
    """
    W/Q decomposition for double-well protocol (arXiv:1503.06537).
    First law: Q = W - ΔE  (heat dissipated = work done - internal energy change)
    For a full erasure cycle: ΔE ≈ 0, so Q ≈ W.
    """
    if not works or len(works) != len(energies):
        return {"available": False}
    W_mean = sum(works) / len(works)
    Q_mean = sum(energies) / len(energies)
    delta  = W_mean - Q_mean   # ΔE = W - Q
    return {
        "available":    True,
        "W_mean":       W_mean,
        "Q_mean":       Q_mean,
        "delta_E_mean": delta,
        "first_law_residual": abs(delta) / max(abs(W_mean), 1e-40),
    }


def dimensionless_invariant(E_mean: float, tau: float,
                             kT: float, tau_min: float) -> dict:
    """
    Ω = (E / kT·ln2) · (τ / τ_min)
    Benchmark from ResearchGate:400901723.
    Ω = 1 is the ideal reversible limit.
    Ω > 1 means excess dissipation or excess time.
    """
    if tau <= 0 or tau_min <= 0:
        return {"available": False, "reason": "tau or tau_min not provided"}
    kT_ln2 = kT * math.log(2)
    omega  = (E_mean / kT_ln2) * (tau / tau_min)
    return {
        "available":  True,
        "omega":      omega,
        "tau":        tau,
        "tau_min":    tau_min,
        "interpretation": (
            "at reversible limit" if abs(omega - 1.0) < 0.05
            else "above reversible limit" if omega > 1.0
            else "below reversible limit (check calibration)"
        ),
    }


def load_trace(path: Path, energy_col: str,
               work_col: str, time_col: str):
    energies, works, times = [], [], []
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []

        # resolve column names
        e_col = energy_col if energy_col in fields else next(
            (c for c in fields if c.lower() in
             ("energy", "heat", "q", "work", "e", "w", "value")), None)
        w_col = work_col if work_col in fields else next(
            (c for c in fields if c.lower() in ("work", "w")), None)
        t_col = time_col if time_col in fields else next(
            (c for c in fields if c.lower() in ("time", "t", "tau")), None)

        if e_col is None:
            return None, None, None, "no energy column found"

        for row in reader:
            try:
                v = float(row[e_col])
                if math.isfinite(v) and v > 0:
                    energies.append(v)
                    if w_col and w_col in row:
                        works.append(float(row[w_col]))
                    if t_col and t_col in row:
                        times.append(float(row[t_col]))
            except (ValueError, KeyError):
                continue

    return energies, works, times, None


def main() -> int:
    args = parse_args()
    path = Path(args.trace)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    energies, works, times, err = load_trace(
        path, args.energy_col, args.work_col, args.time_col)
    if err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    if not energies or len(energies) < 2:
        print("error: need at least 2 energy measurements", file=sys.stderr)
        return 1

    kT_ln2 = args.kT * math.log(2)
    budget  = compute_budget(energies, args.u_cal, args.u_bath,
                             args.u_control, args.coverage)

    ratio    = budget.mean / kT_ln2
    ratio_lo = budget.lo   / kT_ln2
    ratio_hi = budget.hi   / kT_ln2
    eta      = kT_ln2 / budget.mean   # protocol efficiency (1.0 = ideal)

    compliant = budget.lo >= kT_ln2
    mean_ok   = budget.mean >= kT_ln2

    # optional extensions
    tau     = (max(times) - min(times)) if times else 0.0
    dw      = double_well_decompose(energies, works)
    inv     = dimensionless_invariant(budget.mean, tau, args.kT, args.tau_min)

    result = {
        "card":    "landauer-metrology",
        "status":  "PASS" if compliant else ("WARN" if mean_ok else "FAIL"),
        "kT":      args.kT,
        "kT_ln2":  kT_ln2,
        "n":       budget.n,
        "estimate": {"mean": budget.mean, "std": budget.std},
        "uncertainty_budget": {
            "u_A_statistical":   budget.u_A,
            "u_B_calibration":   budget.u_B_cal,
            "u_B_bath_coupling": budget.u_B_bath,
            "u_B_control_noise": budget.u_B_control,
            "u_B_combined":      budget.u_B,
            "u_c_combined":      budget.u_c,
            "coverage_factor_k": args.coverage,
            "U_expanded":        budget.U,
        },
        "coverage_interval": {
            "lo": budget.lo, "hi": budget.hi,
            "level": f"~{int(95 if args.coverage == 2.0 else 68)}%",
        },
        "landauer_ratio": {"mean": ratio, "lo": ratio_lo, "hi": ratio_hi},
        "protocol_efficiency_eta": eta,
        "double_well_decomposition": dw,
        "dimensionless_invariant":   inv,
        "checks": {
            "mean_above_bound":     mean_ok,
            "interval_above_bound": compliant,
        },
        "interpretation": (
            f"E/kT\u00b7ln2 = {ratio:.3f} [{ratio_lo:.3f}, {ratio_hi:.3f}]"
            f"  \u03b7 = {eta:.3f}"
            + (" \u2014 fully compliant" if compliant
               else " \u2014 mean compliant, interval overlaps bound" if mean_ok
               else " \u2014 below Landauer bound")
        ),
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in
          ("card", "status", "landauer_ratio",
           "protocol_efficiency_eta", "interpretation")}, indent=2))
    return 0 if result["status"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
