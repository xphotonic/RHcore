#!/usr/bin/env python3
"""Validate and enrich perovskite device CSV rows.

Standard-library only. Computes missing hysteresis indices, checks basic numeric
fields, and optionally emits checksums for referenced raw files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


REQUIRED_COLUMNS = [
    "device_id",
    "wafer_id",
    "cell_xy",
    "active_area_cm2",
    "stack_description",
    "substrate",
    "batch_date",
    "encapsulation",
    "precondition_protocol",
    "temperature_C",
    "humidity_RH_pct",
    "atm",
    "scan_speed_Vs",
    "scan_dir",
    "illumination_spectrum",
    "illumination_intensity_sun",
    "Voc_V",
    "Jsc_mAcm2",
    "FF_pct",
    "PCE_MPP_pct",
    "PCE_JV_fwd_pct",
    "PCE_JV_rev_pct",
    "hysteresis_index",
    "series_R_ohmcm2",
    "shunt_R_kohmcm2",
    "stabilization_time_s",
    "stability_protocol",
    "MPPT_window_s",
    "EQE_file",
    "JV_fwd_file",
    "JV_rev_file",
    "MPP_trace_file",
    "IV_raw_file",
    "notes",
    "operator",
    "analysis_script",
    "analysis_version",
    "doi_or_repo",
]

NUMERIC_COLUMNS = [
    "active_area_cm2",
    "temperature_C",
    "humidity_RH_pct",
    "scan_speed_Vs",
    "illumination_intensity_sun",
    "Voc_V",
    "Jsc_mAcm2",
    "FF_pct",
    "PCE_MPP_pct",
    "PCE_JV_fwd_pct",
    "PCE_JV_rev_pct",
    "series_R_ohmcm2",
    "shunt_R_kohmcm2",
    "stabilization_time_s",
    "MPPT_window_s",
]

FILE_COLUMNS = ["EQE_file", "JV_fwd_file", "JV_rev_file", "MPP_trace_file", "IV_raw_file"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="Input perovskite devices CSV")
    parser.add_argument("--out", help="Optional enriched CSV output")
    parser.add_argument("--checksums", help="Optional checksums.txt output")
    parser.add_argument("--report", help="Optional JSON validation report")
    parser.add_argument(
        "--strict-files",
        action="store_true",
        help="Fail if any referenced EQE/JV/MPP/IV raw file is missing",
    )
    return parser.parse_args()


def as_float(value: str, column: str, row_index: int) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"row {row_index}: {column} is not numeric: {value!r}") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"row {row_index}: {column} is not finite: {value!r}")
    return parsed


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def compute_hysteresis(fwd: float, rev: float) -> float:
    denom = max(fwd, rev)
    if denom <= 0:
        raise ValueError("PCE_JV_fwd_pct/PCE_JV_rev_pct must have positive max")
    return abs(fwd - rev) / denom


def main() -> int:
    args = parse_args()
    csv_path = Path(args.csv)
    base_dir = csv_path.parent
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        rows = list(reader)

    if fields != REQUIRED_COLUMNS:
        raise ValueError(f"schema mismatch: expected {REQUIRED_COLUMNS}, got {fields}")
    if not rows:
        raise ValueError("CSV has no device rows")

    seen_ids: set[str] = set()
    enriched: list[dict[str, str]] = []
    checksum_lines: list[str] = []
    missing_files: list[str] = []

    for idx, row in enumerate(rows, start=2):
        device_id = row["device_id"].strip()
        if not device_id:
            raise ValueError(f"row {idx}: missing device_id")
        if device_id in seen_ids:
            raise ValueError(f"row {idx}: duplicate device_id {device_id}")
        seen_ids.add(device_id)

        for column in NUMERIC_COLUMNS:
            as_float(row[column], column, idx)

        if row["scan_dir"] not in {"fwd", "rev", "both", "na"}:
            raise ValueError(f"row {idx}: scan_dir must be fwd/rev/both/na")

        fwd = as_float(row["PCE_JV_fwd_pct"], "PCE_JV_fwd_pct", idx)
        rev = as_float(row["PCE_JV_rev_pct"], "PCE_JV_rev_pct", idx)
        computed_hi = compute_hysteresis(fwd, rev)
        if row["hysteresis_index"].strip():
            given_hi = as_float(row["hysteresis_index"], "hysteresis_index", idx)
            if abs(given_hi - computed_hi) > 5e-4:
                raise ValueError(
                    f"row {idx}: hysteresis_index {given_hi} does not match computed {computed_hi}"
                )
        else:
            row["hysteresis_index"] = f"{computed_hi:.15g}"

        for column in FILE_COLUMNS:
            ref = row[column].strip()
            if not ref:
                continue
            path = base_dir / ref
            if path.exists():
                checksum_lines.append(f"{sha256_file(path)}  {ref}")
            else:
                missing_files.append(ref)

        enriched.append(row)

    missing_files = sorted(set(missing_files))
    if args.strict_files and missing_files:
        raise ValueError(f"missing referenced files: {missing_files}")

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerows(enriched)

    if args.checksums:
        checksums_path = Path(args.checksums)
        checksums_path.parent.mkdir(parents=True, exist_ok=True)
        checksums_path.write_text("\n".join(checksum_lines) + ("\n" if checksum_lines else ""), encoding="utf-8")

    report = {
        "status": "PASS",
        "rows": len(enriched),
        "device_ids": sorted(seen_ids),
        "checksummed_files": len(checksum_lines),
        "missing_referenced_files": missing_files,
    }
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
