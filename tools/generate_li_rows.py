#!/usr/bin/env python3
"""Translate `data/li_n_intervals.csv` into a pure Lean module.

Emits:
  - generatedRows : List LiRow
  - rowFor?, liMid, liRad
  - rowPositive_{n} : native_decide witnesses (mid - rad > 0)
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RhCore/Li/LiRows.lean from CSV.")
    parser.add_argument("--csv", required=True, help="Path to li_n_intervals.csv")
    parser.add_argument("--out", required=True, help="Path to output LiRows.lean")
    return parser.parse_args()


def to_rational_term(value: str) -> str:
    numerator, denominator = Decimal(value).as_integer_ratio()
    return f"(({numerator} : \u211a) / {denominator} : \u211a)"


LEAN_HEADER = """\
import RhCore.Li.Rows

namespace RhCore.Li

/-- Generated from `{csv_posix}`. Re-run `tools/generate_li_rows.py` after edits. -/
def generatedRows : List LiRow := [
{body}
]

/-- Total lookup is only intended for indices covered by the generated table. -/
def rowFor? (n : Nat) : Option LiRow :=
  generatedRows.find? (fun row => row.n = n)

/-- Midpoint lookup \u2014 returns 0 if index not in table. -/
def liMid (n : Nat) : \u211d :=
  match rowFor? n with
  | some row => row.mid
  | none     => 0

/-- Radius lookup \u2014 returns 0 if index not in table. -/
def liRad (n : Nat) : \u211d :=
  match rowFor? n with
  | some row => row.rad
  | none     => 0

"""

POSITIVITY_WITNESS = """\
/-- Positivity witness for row n={n}: mid - rad = {diff} > 0.
    Discharged by norm_num on exact rational arithmetic. -/
lemma rowPositive_{n} : (0 : \u211d) < {mid} - {rad} := by norm_num

"""

LEAN_FOOTER = "end RhCore.Li\n"


def main() -> int:
    args     = parse_args()
    csv_path = Path(args.csv)
    out_path = Path(args.out)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows   = list(reader)

    fieldnames = reader.fieldnames or []
    mid_col = "midpoint" if "midpoint" in fieldnames else "mid"
    rad_col = "radius"   if "radius"   in fieldnames else "rad"
    if "n" not in fieldnames or mid_col not in fieldnames or rad_col not in fieldnames:
        raise ValueError(f"expected n + midpoint/radius columns, got {fieldnames}")

    rendered_rows     = []
    positivity_lemmas = []

    for row in rows:
        n       = int(row["n"])
        mid_str = row[mid_col]
        rad_str = row[rad_col]
        mid     = to_rational_term(mid_str)
        rad     = to_rational_term(rad_str)
        rendered_rows.append(f"  {{ n := {n}, mid := {mid}, rad := {rad} }}")

        # positivity witness: mid - rad > 0
        mid_d = Decimal(mid_str)
        rad_d = Decimal(rad_str)
        diff  = mid_d - rad_d
        if diff > 0:
            positivity_lemmas.append(
                POSITIVITY_WITNESS.format(n=n, mid=mid, rad=rad, diff=diff)
            )

    body    = ",\n".join(rendered_rows)
    content = (
        LEAN_HEADER.format(csv_posix=csv_path.as_posix(), body=body)
        + "".join(positivity_lemmas)
        + LEAN_FOOTER
    )
    out_path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
