#!/usr/bin/env python3
"""
Landauer Bootstrap — GUM-compliant uncertainty pipeline.

Type-A: moving-block bootstrap (preserves serial correlation)
Type-B: calibration/timing/gain systematics from typeB.json
Combined: quadrature (GUM)

Input:  CSV with columns t_s, V, I, T, cycle  (or energy column directly)
Output: energy-per-erasure.json + cycle-energy.csv
"""
from __future__ import annotations
import argparse, csv, json, math, sys
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--trace",       required=True)
    p.add_argument("--typeb",       default="",      help="typeB.json path")
    p.add_argument("--block-size",  type=int, default=50)
    p.add_argument("--n-boot",      type=int, default=2000)
    p.add_argument("--alpha",       type=float, default=0.05)
    p.add_argument("--kT",          type=float, default=4.1e-21)
    p.add_argument("--out",         default="artifacts/energy_per_erasure.json")
    p.add_argument("--cycle-out",   default="artifacts/cycle_energy.csv")
    return p.parse_args()


# ── Data loading ──────────────────────────────────────────────────────────

def load_trace(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def compute_energy_per_cycle(rows: list[dict]) -> list[float]:
    """
    If 'cycle' column exists: integrate P=V*I per cycle via trapezoid.
    If only 'energy' column: use directly.
    """
    fields = list(rows[0].keys()) if rows else []

    if "energy" in fields:
        return [float(r["energy"]) for r in rows if float(r["energy"]) > 0]

    if "V" in fields and "I" in fields and "t_s" in fields:
        # group by cycle
        cycles: dict[str, list] = {}
        for r in rows:
            cid = r.get("cycle", "0")
            cycles.setdefault(cid, []).append(r)
        energies = []
        for cid, group in sorted(cycles.items()):
            ts = [float(r["t_s"]) for r in group]
            ps = [float(r["V"]) * float(r["I"]) for r in group]
            # trapezoid
            e = sum(0.5 * (ps[i] + ps[i+1]) * (ts[i+1] - ts[i])
                    for i in range(len(ts)-1))
            if e > 0:
                energies.append(e)
        return energies

    raise ValueError(f"cannot compute energy from columns: {fields}")


# ── Moving-block bootstrap ────────────────────────────────────────────────

def mbb_bootstrap(data: list[float], block: int, n_boot: int,
                  seed: int = 42) -> list[float]:
    """Moving-block bootstrap preserving serial correlation."""
    import random
    rng   = random.Random(seed)
    n     = len(data)
    means = []
    for _ in range(n_boot):
        sample = []
        while len(sample) < n:
            start = rng.randint(0, n - block)
            sample.extend(data[start:start + block])
        sample = sample[:n]
        means.append(sum(sample) / n)
    return means


def t_quantile(df: int, alpha: float) -> float:
    """Student-t quantile via Wilson-Hilferty approximation."""
    # good enough for df > 5; use scipy if available
    try:
        from scipy.stats import t
        return float(t.ppf(1 - alpha / 2, df=max(df, 1)))
    except ImportError:
        # fallback: normal approximation
        return 1.96 if alpha == 0.05 else 2.576


# ── Type-B propagation ────────────────────────────────────────────────────

def typeb_sigma(mu: float, typeb_path: str) -> float:
    """σ_B = |μ| · sqrt(Σ rel²) from typeB.json."""
    if not typeb_path or not Path(typeb_path).exists():
        return 0.0
    tb   = json.loads(Path(typeb_path).read_text())
    keys = ["volt_gain_rel", "curr_gain_rel", "timing_rel"]
    rel2 = sum(tb.get(k, 0.0)**2 for k in keys)
    return abs(mu) * math.sqrt(rel2)


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> int:
    args    = parse_args()
    path    = Path(args.trace)
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        return 1

    rows     = load_trace(path)
    energies = compute_energy_per_cycle(rows)
    if len(energies) < 2:
        print("error: need ≥ 2 energy values", file=sys.stderr)
        return 1

    n   = len(energies)
    mu  = sum(energies) / n

    # Type-A: moving-block bootstrap
    boot   = mbb_bootstrap(energies, args.block_size, args.n_boot)
    sigma_A = (sum((b - sum(boot)/len(boot))**2 for b in boot) / (len(boot)-1)) ** 0.5
    tq      = t_quantile(n - 1, args.alpha)

    # Type-B
    sigma_B = typeb_sigma(mu, args.typeb)

    # Combined (GUM quadrature)
    sigma_tot = math.sqrt(sigma_A**2 + sigma_B**2)
    U         = tq * sigma_tot   # expanded uncertainty

    kT_ln2    = args.kT * math.log(2)
    ratio     = mu / kT_ln2
    compliant = (mu - U) >= kT_ln2

    result = {
        "card":   "landauer-bootstrap",
        "status": "PASS" if compliant else ("WARN" if mu >= kT_ln2 else "FAIL"),
        "n_cycles":   n,
        "block_size": args.block_size,
        "n_boot":     args.n_boot,
        "kT":         args.kT,
        "kT_ln2":     kT_ln2,
        "estimate": {
            "mean_J":  mu,
            "sigma_A": sigma_A,
            "sigma_B": sigma_B,
            "sigma_combined": sigma_tot,
            "U_expanded":     U,
            "coverage_factor_k": tq,
            "ci95": [mu - U, mu + U],
        },
        "landauer_ratio": {
            "mean":  ratio,
            "lo":    (mu - U) / kT_ln2,
            "hi":    (mu + U) / kT_ln2,
        },
        "protocol_efficiency_eta": kT_ln2 / mu if mu > 0 else 0.0,
        "checks": {
            "mean_above_bound":     mu >= kT_ln2,
            "interval_above_bound": compliant,
        },
        "interpretation": (
            f"E/kT·ln2 = {ratio:.3f} ± {U/kT_ln2:.3f} — "
            + ("fully compliant" if compliant
               else "mean compliant, interval overlaps" if mu >= kT_ln2
               else "below Landauer bound")
        ),
    }

    # cycle-energy CSV
    Path(args.cycle_out).parent.mkdir(parents=True, exist_ok=True)
    with Path(args.cycle_out).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cycle", "energy_J", "ratio_kT_ln2"])
        for i, e in enumerate(energies):
            w.writerow([i+1, e, e/kT_ln2])

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2))
    print(json.dumps({k: result[k] for k in
          ("card", "status", "landauer_ratio",
           "protocol_efficiency_eta", "interpretation")}, indent=2))
    return 0 if result["status"] in ("PASS", "WARN") else 1


if __name__ == "__main__":
    sys.exit(main())
