#!/usr/bin/env python3
"""RH spectral instability detector for Li/Keiper coefficients.

This is a numerical witness tool, not an RH proof.

Given a suspected zero rho = a + ib, it computes the mpmath prototype for the
maximal downward impact

    D_n(rho) = 4 * (cosh(n * L) - 1)
    L = -log(|(rho - 1) / rho|)

For production certificates, use an interval/Arb implementation. This script is
intended for quick CI smoke tests, tables, and witness exploration.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import mpmath as mp


def rho_damage(a: str, b: str, n_max: int = 50, dps: int = 80) -> list[dict[str, str | int]]:
    mp.mp.dps = dps
    rho = mp.mpc(mp.mpf(a), mp.mpf(b))
    r = abs((rho - 1) / rho)
    L = -mp.log(r)

    rows: list[dict[str, str | int]] = []
    for n in range(1, n_max + 1):
        Dn = 4 * (mp.cosh(n * L) - 1)
        rows.append(
            {
                "n": n,
                "a": mp.nstr(mp.mpf(a), dps),
                "b": mp.nstr(mp.mpf(b), dps),
                "r": mp.nstr(r, dps),
                "L": mp.nstr(L, dps),
                "D_n": mp.nstr(Dn, dps),
            }
        )
    return rows


def print_report(rows: list[dict[str, str | int]]) -> None:
    if not rows:
        return
    first = rows[0]
    print("=" * 70)
    print(f"rho = {first['a']} + {first['b']}i")
    print("=" * 70)
    print(f"r = {mp.nstr(mp.mpf(str(first['r'])), 20)}")
    print(f"L = {mp.nstr(mp.mpf(str(first['L'])), 20)}")
    print("-" * 70)
    for row in rows:
        print(f"n={int(row['n']):3d}   D_n={mp.nstr(mp.mpf(str(row['D_n'])), 12)}")


def write_csv(rows: list[dict[str, str | int]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["n", "a", "b", "r", "L", "D_n"])
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows: list[dict[str, str | int]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "kind": "li_keiper_instability_detector",
        "warning": "mpmath prototype; use Arb intervals for production certificates",
        "rows": rows,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", required=True, help="real part of suspected zero")
    parser.add_argument("--b", required=True, help="imaginary part of suspected zero")
    parser.add_argument("--n-max", type=int, default=50)
    parser.add_argument("--dps", type=int, default=80)
    parser.add_argument("--csv", type=Path)
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()

    rows = rho_damage(args.a, args.b, args.n_max, args.dps)
    print_report(rows)
    if args.csv:
        write_csv(rows, args.csv)
    if args.json:
        write_json(rows, args.json)


if __name__ == "__main__":
    main()

