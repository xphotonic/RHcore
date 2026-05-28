#!/usr/bin/env python3
"""Validate Li-interval artifacts using exactly four closure checks."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

REQUIRED_COLUMNS = ["n", "midpoint", "radius", "bits", "zeros_checksum"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Li interval artifacts.")
    parser.add_argument("--zeros-status", required=True, help="Path to zeta_status.json.")
    parser.add_argument("--li", required=True, help="Path to li_n_intervals.csv.")
    parser.add_argument(
        "--radius-threshold",
        required=True,
        type=float,
        help="Maximum allowed radius for closure.",
    )
    parser.add_argument("--out", required=True, help="Output JSON status path.")
    parser.add_argument(
        "--trace-out",
        help="Optional output path for the detailed closure gate trace JSON.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    args = parse_args()
    zeros_status_path = Path(args.zeros_status)
    li_path = Path(args.li)
    out_path = Path(args.out)
    trace_out_path = Path(args.trace_out) if args.trace_out else None

    result: dict[str, object] = {
        "layer": "closure",
        "status": "FAIL",
        "representation": {
            "zeros": "ordered_ordinates_with_checksum",
            "li": "midpoint_radius",
            "state": "json_pass_fail",
        },
        "sources": {
            "zeros_status": str(zeros_status_path),
            "li_csv": str(li_path),
        },
        "checks": {
            "checksum_match": False,
            "interval_containment": False,
            "radius_bound": False,
            "schema_correctness": False,
        },
    }
    trace: dict[str, object] = {
        "machine": "Reference Deck v2.1 Closed Engine",
        "status": "FAIL",
        "gates": [],
    }

    def record_gate(name: str, passed: bool, constraint: str, failure_reason: str | None = None) -> None:
        gates = trace["gates"]
        assert isinstance(gates, list)
        gates.append(
            {
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "constraint": constraint,
                "failure_reason": failure_reason,
            }
        )

    if not zeros_status_path.exists() or not li_path.exists():
        result["error"] = "missing required input artifact"
        out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        record_gate(
            "Gate 0 - Carrier / Source Admissibility",
            False,
            "zeros status and li artifact must both exist",
            "missing required input artifact",
        )
        trace["status"] = "FAIL"
        if trace_out_path:
            trace_out_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
        return 1

    try:
        zeros_status = load_json(zeros_status_path)
        zeros_status_ok = zeros_status.get("status") == "PASS"
        record_gate(
            "Gate 0 - Carrier / Source Admissibility",
            zeros_status_ok,
            "zeros source must already be admissible",
            None if zeros_status_ok else "zeros_status.json is not PASS",
        )
        expected_checksum = (
            zeros_status.get("summary", {}).get("zeros_checksum")  # type: ignore[union-attr]
        )
        if not isinstance(expected_checksum, str) or not expected_checksum:
            raise ValueError("zeros_status missing summary.zeros_checksum")

        with li_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            fieldnames = reader.fieldnames or []
            rows = list(reader)

        schema_correctness = fieldnames == REQUIRED_COLUMNS and bool(rows)
        result["checks"]["schema_correctness"] = schema_correctness  # type: ignore[index]
        record_gate(
            "Gate 1 - Schema Correctness",
            schema_correctness,
            "li artifact must use the single midpoint/radius schema",
            None if schema_correctness else f"expected columns {REQUIRED_COLUMNS}, got {fieldnames}",
        )

        checksum_match = False
        interval_containment = False
        radius_bound = False
        max_radius = None
        n_values: list[int] = []

        if schema_correctness:
            checksum_match = all(row["zeros_checksum"] == expected_checksum for row in rows)

            midpoint_values = []
            radius_values = []
            interval_ok = True
            radius_ok = True

            for row in rows:
                midpoint = float(row["midpoint"])
                radius = float(row["radius"])
                n_values.append(int(row["n"]))
                midpoint_values.append(midpoint)
                radius_values.append(radius)

                lower = midpoint - radius
                upper = midpoint + radius
                interval_ok = interval_ok and math.isfinite(midpoint) and math.isfinite(radius)
                interval_ok = interval_ok and radius >= 0.0 and lower <= midpoint <= upper
                radius_ok = radius_ok and radius <= args.radius_threshold

            interval_containment = interval_ok
            radius_bound = radius_ok
            max_radius = max(radius_values) if radius_values else None

        result["checks"]["checksum_match"] = checksum_match  # type: ignore[index]
        result["checks"]["interval_containment"] = interval_containment  # type: ignore[index]
        result["checks"]["radius_bound"] = radius_bound  # type: ignore[index]
        record_gate(
            "Gate 2 - Checksum Consistency",
            checksum_match,
            "every li row must be bound to the same zeros checksum",
            None if checksum_match else "li rows are not bound to the expected zeros checksum",
        )
        record_gate(
            "Gate 3 - Interval Containment",
            interval_containment,
            "midpoint +/- radius must form a valid finite interval",
            None if interval_containment else "at least one interval is non-finite or malformed",
        )
        record_gate(
            "Gate 4 - Radius Bound",
            radius_bound,
            "each radius must stay below the closure threshold",
            None if radius_bound else f"at least one radius exceeds {args.radius_threshold}",
        )
        status = all(bool(value) for value in result["checks"].values())  # type: ignore[union-attr]
        result["status"] = "PASS" if status else "FAIL"
        result["summary"] = {
            "zeros_checksum": expected_checksum,
            "radius_threshold": args.radius_threshold,
            "max_radius": max_radius,
            "row_count": len(rows),
            "n_start": min(n_values) if n_values else None,
            "n_end": max(n_values) if n_values else None,
        }
        record_gate(
            "Gate 5 - Final Closure Decision",
            status,
            "all prior gates must pass for closure to be frozen",
            None if status else "one or more prior gates failed",
        )
        trace["status"] = "PASS" if status else "FAIL"
    except Exception as exc:  # pragma: no cover - surfaced in status file
        result["error"] = str(exc)
        result["status"] = "FAIL"
        record_gate(
            "Gate X - Validation Exception",
            False,
            "validation must complete without runtime exceptions",
            str(exc),
        )
        trace["status"] = "FAIL"

    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if trace_out_path:
        trace["summary"] = {
            "closure_status": result["status"],
            "checks": result["checks"],
        }
        trace_out_path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
