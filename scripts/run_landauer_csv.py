#!/usr/bin/env python3
"""Generate Landauer CSV artifacts without notebook execution."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-path", default="traces/run1.csv")
    parser.add_argument("--block-size", type=int, default=5)
    parser.add_argument("--cycle-column", default="cycle")
    parser.add_argument("--typeb-json", default="inputs/typeB.json")
    parser.add_argument("--bootstrap-reps", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--outputs-dir", default="outputs")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def cycle_energies(rows: list[dict[str, str]], cycle_column: str) -> list[tuple[str, float]]:
    cycles: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        cycles.setdefault(row[cycle_column], []).append(row)

    out: list[tuple[str, float]] = []
    for cycle, group in sorted(cycles.items(), key=lambda item: float(item[0])):
        group = sorted(group, key=lambda row: float(row["t_s"]))
        energy = 0.0
        for left, right in zip(group, group[1:]):
            p0 = float(left["V"]) * float(left["I"])
            p1 = float(right["V"]) * float(right["I"])
            dt = float(right["t_s"]) - float(left["t_s"])
            energy += 0.5 * (p0 + p1) * dt
        if energy > 0:
            out.append((cycle, energy))
    return out


def bootstrap_means(values: list[float], block_size: int, reps: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    n = len(values)
    block_size = max(1, min(block_size, n))
    means = []
    for _ in range(reps):
        sample = []
        while len(sample) < n:
            start = rng.randint(0, n - block_size)
            sample.extend(values[start : start + block_size])
        sample = sample[:n]
        means.append(sum(sample) / n)
    return means


def sample_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = sum(values) / len(values)
    return math.sqrt(sum((x - mu) ** 2 for x in values) / (len(values) - 1))


def typeb_sigma(mu: float, path: Path) -> float:
    if not path.exists():
        return 0.0
    data = json.loads(path.read_text(encoding="utf-8"))
    rel2 = sum(float(data.get(key, 0.0)) ** 2 for key in ["volt_gain_rel", "curr_gain_rel", "timing_rel"])
    return abs(mu) * math.sqrt(rel2)


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    return ordered[lo] * (hi - pos) + ordered[hi] * (pos - lo)


def main() -> int:
    args = parse_args()
    trace_path = Path(args.trace_path)
    typeb_path = Path(args.typeb_json)
    out_dir = Path(args.outputs_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(trace_path)
    required = {"t_s", "V", "I", args.cycle_column}
    missing = required - set(rows[0].keys() if rows else [])
    if missing:
        raise SystemExit(f"missing required columns: {sorted(missing)}")

    cycle_rows = cycle_energies(rows, args.cycle_column)
    values = [energy for _, energy in cycle_rows]
    if len(values) < 2:
        raise SystemExit("need at least two positive cycle energies")

    mu = sum(values) / len(values)
    boot = bootstrap_means(values, args.block_size, args.bootstrap_reps, args.seed)
    sigma_a = sample_std(boot)
    sigma_b = typeb_sigma(mu, typeb_path)
    sigma_total = math.sqrt(sigma_a**2 + sigma_b**2)

    with (out_dir / "cycle-energy.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["cycle", "energy_J"])
        writer.writerows(cycle_rows)

    ci_a = (percentile(boot, 0.025), percentile(boot, 0.975))
    summary = {
        "stat": "mean_energy_J",
        "value": mu,
        "sigma_A": sigma_a,
        "sigma_B": sigma_b,
        "sigma_total": sigma_total,
        "ci95_A_low": ci_a[0],
        "ci95_A_high": ci_a[1],
        "ci95_B_low": mu - 1.96 * sigma_b,
        "ci95_B_high": mu + 1.96 * sigma_b,
        "ci95_total_low": mu - 1.96 * sigma_total,
        "ci95_total_high": mu + 1.96 * sigma_total,
        "cycles": len(values),
        "block_size": args.block_size,
        "bootstrap_reps": args.bootstrap_reps,
    }
    with (out_dir / "energy-per-erasure.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary))
        writer.writeheader()
        writer.writerow(summary)

    components = [
        ("Type-A bootstrap", sigma_a),
        ("Type-B systematic", sigma_b),
        ("Combined", sigma_total),
    ]
    with (out_dir / "uncertainty-components.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["component", "sigma_J"])
        writer.writerows(components)

    print(json.dumps({"status": "PASS", "cycles": len(values), "mean_energy_J": mu}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
