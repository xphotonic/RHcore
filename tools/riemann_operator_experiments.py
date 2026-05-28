#!/usr/bin/env python3
"""RiemannOperator experimental harness.

Subcommands:

- run_heat: heat-filter stability sweep for a deterministic spectral model.
- run_parity: split the model into even/odd parity sectors and compare spacing.
- run_trace: compare a Gaussian trace statistic with a zero-like statistic.
- run_all: execute all three and write one JSON/CSV artifact pair.

The default model is a known-spectrum smoke harness. Replace `model_spectrum`
with the real RiemannOperator spectrum once that object has a stable API.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, pstdev


DEFAULT_T_VALUES = [1e-1, 5e-2, 1e-2, 5e-3, 1e-3]
DEFAULT_SIGMAS = [0.5, 1.0, 2.0, 4.0]


def model_spectrum(size: int) -> list[tuple[int, float]]:
    """Symmetric deterministic spectrum indexed by nonzero Fourier modes."""
    if size < 4:
        raise ValueError("--size must be at least 4")
    half = size // 2
    modes = [k for k in range(-half, half + 1) if k != 0]
    return [(k, math.copysign(math.log1p(abs(k)) + 0.015 * abs(k), k)) for k in modes]


def heat_filter_value(lam: float, t: float) -> float:
    return math.exp(-t * lam * lam) * lam


def spacings(vals: list[float]) -> list[float]:
    ordered = sorted(vals)
    return [b - a for a, b in zip(ordered, ordered[1:]) if b > a]


def spacing_stats(vals: list[float]) -> dict[str, float]:
    gaps = spacings(vals)
    if not gaps:
        return {"spacing_mean": 0.0, "spacing_std": 0.0, "spacing_cv": 0.0}
    m = mean(gaps)
    s = pstdev(gaps)
    return {"spacing_mean": m, "spacing_std": s, "spacing_cv": s / m if m > 0 else 0.0}


def local_weyl_error(vals: list[float], threshold: float) -> float:
    count = sum(1 for val in vals if abs(val) <= threshold)
    predicted = 2.0 * math.expm1(threshold)
    return abs(count - predicted)


def run_heat(size: int, t_values: list[float]) -> list[dict[str, float | int | str]]:
    spectrum = model_spectrum(size)
    baseline_vals = [lam for _, lam in spectrum]
    base_stats = spacing_stats(baseline_vals)
    rows = []
    for t in t_values:
        filtered = [heat_filter_value(lam, t) for _, lam in spectrum]
        stats = spacing_stats(filtered)
        max_shift = max(abs(a - b) for a, b in zip(sorted(baseline_vals), sorted(filtered)))
        rows.append(
            {
                "experiment": "heat",
                "sector": "all",
                "t": t,
                "sigma": "",
                "metric": "heat_filter_stability",
                "value": max_shift,
                "spacing_cv": stats["spacing_cv"],
                "baseline_spacing_cv": base_stats["spacing_cv"],
                "weyl_error": local_weyl_error(filtered, threshold=2.0),
                "status": "PASS" if math.isfinite(max_shift) else "FAIL",
            }
        )
    return rows


def run_parity(size: int) -> list[dict[str, float | int | str]]:
    spectrum = model_spectrum(size)
    rows = []
    sectors = {
        "all": [lam for _, lam in spectrum],
        "even": [lam for k, lam in spectrum if k % 2 == 0],
        "odd": [lam for k, lam in spectrum if k % 2 != 0],
    }
    all_cv = spacing_stats(sectors["all"])["spacing_cv"]
    for sector, vals in sectors.items():
        stats = spacing_stats(vals)
        rows.append(
            {
                "experiment": "parity",
                "sector": sector,
                "t": "",
                "sigma": "",
                "metric": "spacing_cv",
                "value": stats["spacing_cv"],
                "spacing_cv": stats["spacing_cv"],
                "baseline_spacing_cv": all_cv,
                "weyl_error": local_weyl_error(vals, threshold=2.0),
                "status": "PASS" if vals else "FAIL",
            }
        )
    return rows


def gaussian(x: float, sigma: float) -> float:
    return math.exp(-(x * x) / (2.0 * sigma * sigma))


def gaussian_hat_smoke(x: float, sigma: float) -> float:
    # Same normalization on both sides is unnecessary for the smoke metric; this
    # deliberately keeps the comparison shape-focused and deterministic.
    return gaussian(x, 1.0 / sigma)


def run_trace(size: int, t_values: list[float], sigmas: list[float]) -> list[dict[str, float | int | str]]:
    spectrum = model_spectrum(size)
    zero_like = [lam for _, lam in spectrum]
    rows = []
    for t in t_values:
        filtered = [heat_filter_value(lam, t) for _, lam in spectrum]
        for sigma in sigmas:
            lhs = sum(gaussian(lam, sigma) for lam in filtered)
            rhs = sum(gaussian_hat_smoke(z, sigma) for z in zero_like)
            err = abs(lhs - rhs)
            rows.append(
                {
                    "experiment": "trace",
                    "sector": "all",
                    "t": t,
                    "sigma": sigma,
                    "metric": "trace_to_zeros_error",
                    "value": err,
                    "spacing_cv": "",
                    "baseline_spacing_cv": "",
                    "weyl_error": "",
                    "status": "PASS" if math.isfinite(err) else "FAIL",
                }
            )
    return rows


def write_outputs(rows: list[dict[str, object]], json_path: str, csv_path: str) -> dict[str, object]:
    failures = [row for row in rows if row.get("status") != "PASS"]
    report = {
        "status": "PASS" if not failures else "FAIL",
        "description": "RiemannOperator heat/parity/trace smoke experiments",
        "rows": len(rows),
        "failures": failures,
    }
    out_json = Path(json_path)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report | {"data": rows}, indent=2), encoding="utf-8")

    out_csv = Path(csv_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "experiment",
        "sector",
        "t",
        "sigma",
        "metric",
        "value",
        "spacing_cv",
        "baseline_spacing_cv",
        "weyl_error",
        "status",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ["run_heat", "run_parity", "run_trace", "run_all"]:
        p = sub.add_parser(name)
        p.add_argument("--size", type=int, default=64)
        p.add_argument("--json", default=f"outputs/riemann_operator_{name}.json")
        p.add_argument("--csv", default=f"outputs/riemann_operator_{name}.csv")
        p.add_argument("--strict", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "run_heat":
        rows = run_heat(args.size, DEFAULT_T_VALUES)
    elif args.command == "run_parity":
        rows = run_parity(args.size)
    elif args.command == "run_trace":
        rows = run_trace(args.size, DEFAULT_T_VALUES, DEFAULT_SIGMAS)
    elif args.command == "run_all":
        rows = []
        rows.extend(run_heat(args.size, DEFAULT_T_VALUES))
        rows.extend(run_parity(args.size))
        rows.extend(run_trace(args.size, DEFAULT_T_VALUES, DEFAULT_SIGMAS))
    else:
        raise ValueError(args.command)

    report = write_outputs(rows, args.json, args.csv)
    print(json.dumps({k: v for k, v in report.items() if k != "failures"}, indent=2))
    if args.strict and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
