#!/usr/bin/env python3
"""
Zenodo Adapter — converts experimental datasets into RhCore pipeline format.

Supported datasets:
  szilard    — Aggarwal et al. quantum-dot Szilard engine (DOI:10.5281/zenodo.14516010)
  ot_arhmm   — optical tweezer arHMM traces (DOI:10.5281/zenodo.13323961)
  cantilever — Bellon et al. underdamped erasure (DOI:10.5281/zenodo.13829200)

Input:
  - CSV directly
  - ZIP containing at least one CSV (largest CSV is selected by default)

Output:
  - <dataset>_trace.csv
  - <dataset>_landauer.json
  - <dataset>_provenance.json
  - <dataset>_checksums.txt
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, sys, zipfile
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", choices=["szilard", "ot_arhmm", "cantilever"],
                   required=True)
    p.add_argument("--input",   required=True, help="Path to downloaded CSV or ZIP")
    p.add_argument("--out-dir", default="repo/data/experimental")
    p.add_argument("--kT",      type=float, default=4.1e-21,
                   help="Thermal energy kT in Joules (default: room temp)")
    p.add_argument("--strict-landauer", action="store_true",
                   help="Fail (exit 1) when Landauer status is WARN")
    p.add_argument("--doi", default="", help="Dataset DOI for provenance")
    p.add_argument("--license", default="", help="Dataset license identifier (e.g., CC-BY-4.0)")
    p.add_argument("--record-url", default="", help="Zenodo record URL for provenance")
    return p.parse_args()


def sha256(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            d.update(chunk)
    return d.hexdigest()


# ── Dataset-specific parsers ──────────────────────────────────────────────

def _read_csv_rows(path: Path) -> list[dict]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path, "r") as zf:
            csv_members = [m for m in zf.infolist() if m.filename.lower().endswith(".csv")]
            if not csv_members:
                raise ValueError("zip input has no CSV files")
            # Prefer the largest CSV; these archives commonly include tiny helper files.
            csv_members.sort(key=lambda m: m.file_size, reverse=True)
            member = csv_members[0]
            with zf.open(member, "r") as raw:
                text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
                return list(csv.DictReader(text))

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def parse_szilard(path: Path) -> list[dict]:
    """
    Szilard engine: extract work extraction events as energy observations.
    Expected columns: time, work_extracted (or similar).
    Maps to: t = time, energy = |work| for Landauer check.
    """
    rows = []
    for i, row in enumerate(_read_csv_rows(path)):
        # try common column names
        t_col = next((k for k in row if k.lower() in
                     ("time", "t", "step", "index")), None)
        e_col = next((k for k in row if k.lower() in
                     ("work", "energy", "w", "e", "value")), None)
        if t_col and e_col:
            try:
                rows.append({
                    "index": i + 1,
                    "t":     float(row[t_col]),
                    "energy": abs(float(row[e_col])),
                })
            except ValueError:
                continue
    return rows


def parse_ot_arhmm(path: Path) -> list[dict]:
    """
    Optical tweezer: extract position traces as phase-like signal.
    Maps to: t = time, signal = position (proxy for S(t)).
    """
    rows = []
    for i, row in enumerate(_read_csv_rows(path)):
        t_col = next((k for k in row if k.lower() in
                     ("time", "t", "frame", "index")), None)
        x_col = next((k for k in row if k.lower() in
                     ("x", "position", "pos", "signal", "value")), None)
        if t_col and x_col:
            try:
                rows.append({
                    "index": i + 1,
                    "t":     float(row[t_col]),
                    "signal": float(row[x_col]),
                })
            except ValueError:
                continue
    return rows


def parse_cantilever(path: Path) -> list[dict]:
    """
    Cantilever erasure: position/velocity traces.
    Maps to: t = time, energy = 0.5*(v^2 + x^2) (normalized).
    """
    rows = []
    for i, row in enumerate(_read_csv_rows(path)):
        t_col = next((k for k in row if k.lower() in
                     ("time", "t")), None)
        x_col = next((k for k in row if k.lower() in
                     ("x", "position", "pos")), None)
        v_col = next((k for k in row if k.lower() in
                     ("v", "velocity", "vel")), None)
        if t_col and x_col:
            try:
                x = float(row[x_col])
                v = float(row[v_col]) if v_col else 0.0
                rows.append({
                    "index": i + 1,
                    "t":     float(row[t_col]),
                    "energy": 0.5 * (x**2 + v**2),
                })
            except ValueError:
                continue
    return rows


# ── Landauer check ────────────────────────────────────────────────────────

def landauer_check(rows: list[dict], kT: float) -> dict:
    """
    Verify E ≥ kT ln2 per bit erasure event.
    Counts events where energy < kT*ln2 (Landauer violations).
    """
    threshold = kT * math.log(2)
    energies  = [r["energy"] for r in rows if "energy" in r and r["energy"] > 0]
    if not energies:
        return {"status": "SKIP", "reason": "no energy column"}

    violations = sum(1 for e in energies if e < threshold)
    min_e      = min(energies)
    mean_e     = sum(energies) / len(energies)

    return {
        "card":           "landauer-gate",
        "status":         "PASS" if violations == 0 else "WARN",
        "kT":             kT,
        "threshold_kT_ln2": threshold,
        "n_events":       len(energies),
        "violations":     violations,
        "min_energy":     min_e,
        "mean_energy":    mean_e,
        "ratio_min_to_threshold": min_e / threshold,
        "interpretation": (
            "all events above Landauer bound"
            if violations == 0 else
            f"{violations} events below kT*ln2 — check units or normalization"
        ),
    }


# ── Main ──────────────────────────────────────────────────────────────────

def main() -> int:
    args     = parse_args()
    in_path  = Path(args.input)
    out_dir  = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        print(f"error: {in_path} not found", file=sys.stderr)
        return 1

    parsers = {
        "szilard":    parse_szilard,
        "ot_arhmm":   parse_ot_arhmm,
        "cantilever": parse_cantilever,
    }
    rows = parsers[args.dataset](in_path)

    if not rows:
        print("error: no rows parsed — check column names", file=sys.stderr)
        return 1

    # write energy_trace.csv
    trace_path = out_dir / f"{args.dataset}_trace.csv"
    with trace_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # Landauer check
    lc = landauer_check(rows, args.kT)
    lc_path = out_dir / f"{args.dataset}_landauer.json"
    lc_path.write_text(json.dumps(lc, indent=2))

    # provenance
    prov = {
        "dataset":    args.dataset,
        "source":     str(in_path),
        "sha256":     sha256(in_path),
        "doi":        args.doi,
        "license":    args.license,
        "record_url": args.record_url,
        "n_rows":     len(rows),
        "trace_out":  str(trace_path),
        "landauer":   lc,
    }
    prov_path = out_dir / f"{args.dataset}_provenance.json"
    prov_path.write_text(json.dumps(prov, indent=2))

    # checksums for CI/attestation workflows
    outputs = [trace_path, lc_path, prov_path]
    checksums_path = out_dir / f"{args.dataset}_checksums.txt"
    checksum_lines = [f"{sha256(p)}  {p.name}" for p in outputs]
    checksums_path.write_text("\n".join(checksum_lines) + "\n")

    print(json.dumps({
        "dataset":  args.dataset,
        "n_rows":   len(rows),
        "landauer": lc["status"],
        "outputs":  [str(trace_path), str(lc_path), str(prov_path), str(checksums_path)],
    }, indent=2))
    if args.strict_landauer and lc.get("status") == "WARN":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
