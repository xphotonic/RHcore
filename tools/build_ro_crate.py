#!/usr/bin/env python3
"""
Build RO-Crate metadata with SLSA provenance and Sigstore attestation.

Produces:
  ro-crate-metadata.json  — RO-Crate 1.1 + WorkflowRun + instruments
  attestation.json        — SLSA Provenance v1 (in-toto Statement)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build RO-Crate + SLSA attestation.")
    p.add_argument("--artifact",    action="append", required=True, dest="artifacts")
    p.add_argument("--out",         required=True,  help="ro-crate-metadata.json path")
    p.add_argument("--attestation", default="",     help="attestation.json path")
    p.add_argument("--rekor-entry", default="",     help="Rekor UUID or URL")
    p.add_argument("--run-id",      default="",     help="CI run ID")
    p.add_argument("--run-url",     default="",     help="CI run URL")
    p.add_argument("--commit-sha",  default="",     help="Git commit SHA")
    p.add_argument("--builder-id",  default="",     help="SLSA builder ID")
    p.add_argument("--instruments", default="",     help="JSON string or path: [{id,type,serial}]")
    p.add_argument("--typeb",       default="",     help="typeB.json for measurement model")
    p.add_argument("--nb-params",   default="",     help="JSON string of notebook parameters")
    p.add_argument("--patch-rekor", default="",     help="cosign output file to extract Rekor UUID")
    p.add_argument("--provenance",   default="",     help="JSON string: {arb_numerics, zeros_wheel, li_script}")
    return p.parse_args()


def sha256_file(path: Path) -> str:
    d = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            d.update(chunk)
    return d.hexdigest()


def env_or(key: str, fallback: str) -> str:
    return os.environ.get(key, fallback)


def _find_first(obj, keys: set[str]):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in keys:
                return v
            nested = _find_first(v, keys)
            if nested is not None:
                return nested
    elif isinstance(obj, list):
        for item in obj:
            nested = _find_first(item, keys)
            if nested is not None:
                return nested
    return None


def parse_rekor_from_bundle(bundle_path: Path) -> str:
    """Best-effort Rekor locator extraction from a cosign bundle JSON file."""
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except Exception:
        return ""

    uuid = _find_first(payload, {"entryUUID", "uuid"})
    if isinstance(uuid, str) and uuid:
        return f"https://rekor.sigstore.dev/api/v1/log/entries/{uuid}"

    idx = _find_first(payload, {"logIndex"})
    if isinstance(idx, int):
        return f"https://rekor.sigstore.dev/api/v1/log/entries?logIndex={idx}"
    if isinstance(idx, str) and idx.isdigit():
        return f"https://rekor.sigstore.dev/api/v1/log/entries?logIndex={idx}"
    return ""


def build_file_entry(path: Path) -> dict:
    entry: dict = {
        "@id":         path.name,
        "@type":       "File",
        "name":        path.name,
        "contentSize": path.stat().st_size,
        "sha256":      sha256_file(path),
        "encodingFormat": (
            "application/json" if path.suffix == ".json" else
            "text/csv"         if path.suffix == ".csv"  else
            "application/octet-stream"
        ),
    }
    sig_path    = path.with_name(path.name + ".sig")
    cert_path   = path.with_name(path.name + ".pem")
    bundle_path = path.with_name(path.name + ".bundle.json")
    if sig_path.exists():
        entry["signed_by"] = "sigstore"
        entry["signature_file"] = sig_path.name
    if cert_path.exists():
        entry["certificate_file"] = cert_path.name
    if bundle_path.exists():
        entry["sigstore_bundle"] = bundle_path.name
        rekor_entry = parse_rekor_from_bundle(bundle_path)
        if rekor_entry:
            entry["rekor_entry"] = rekor_entry
    return entry


def parse_instruments(raw: str) -> list[dict]:
    if not raw:
        return []
    try:
        data = json.loads(Path(raw).read_text()) if Path(raw).exists() else json.loads(raw)
        result = []
        for inst in data:
            entry = {
                "@id":   f"#instrument-{inst.get('id', '?')}",
                "@type": "Instrument",
                "name":  inst.get("type", inst.get("id", "unknown")),
            }
            if "serial" in inst:
                entry["serialNumber"] = inst["serial"]
            result.append(entry)
        return result
    except Exception:
        return []


def parse_typeb(path: str) -> dict:
    if not path or not Path(path).exists():
        return {}
    tb = json.loads(Path(path).read_text())
    return {
        "@type":           "StructuredValue",
        "typeA_method":    "moving-block-bootstrap",
        "typeB_components": [k for k in tb if not k.startswith("_")],
    }


def extract_rekor_uuid(cosign_out: str) -> str:
    """Extract Rekor UUID from cosign output file."""
    if not cosign_out or not Path(cosign_out).exists():
        return ""
    txt = Path(cosign_out).read_text()
    m = re.search(r"UUID:\s*([0-9a-f\-]{36})", txt)
    if m:
        return f"https://rekor.sigstore.dev/api/v1/log/entries/{m.group(1)}"
    m = re.search(r"rekor\.sigstore\.dev/api/v1/log/entries/([0-9a-f]+)", txt)
    if m:
        return f"https://rekor.sigstore.dev/api/v1/log/entries/{m.group(1)}"
    m = re.search(r"log index:\s*([0-9]+)", txt, flags=re.IGNORECASE)
    if m:
        return f"https://rekor.sigstore.dev/api/v1/log/entries?logIndex={m.group(1)}"
    return ""


def infer_rekor_from_parts(parts: list[dict]) -> str:
    for part in parts:
        val = part.get("rekor_entry", "")
        if isinstance(val, str) and val:
            return val
    return ""


def build_ro_crate(parts: list[dict], args: argparse.Namespace, now: str) -> dict:
    run_id     = args.run_id     or env_or("GITHUB_RUN_ID", "local")
    run_url    = args.run_url    or env_or("GITHUB_RUN_URL", "")
    commit_sha = args.commit_sha or env_or("GITHUB_SHA", "unknown")
    repo       = env_or("GITHUB_REPOSITORY", "RhCore")
    rekor      = args.rekor_entry or extract_rekor_uuid(args.patch_rekor) or infer_rekor_from_parts(parts)

    if not run_url and env_or("GITHUB_SERVER_URL", ""):
        run_url = f"{env_or('GITHUB_SERVER_URL','')}/{repo}/actions/runs/{run_id}"

    instruments    = parse_instruments(args.instruments)
    meas_model     = parse_typeb(args.typeb)
    nb_params: dict = {}
    if args.nb_params:
        try:
            nb_params = json.loads(args.nb_params)
        except Exception:
            pass

    workflow_run: dict = {
        "@id":   "#workflow-run",
        "@type": "WorkflowRun",
        "name":  f"RhCore closure run {run_id}",
        "input": [{"@type": "File", "name": p["name"]} for p in parts],
    }
    if nb_params:
        workflow_run["parameter"] = [
            {"@type": "PropertyValue", "name": k, "value": str(v)}
            for k, v in nb_params.items()
        ]

    ci_job: dict = {
        "@id":             "#ci-job",
        "@type":           "SoftwareApplication",
        "name":            "GitHub Actions / CodeBuild",
        "softwareVersion": f"commit:{commit_sha}",
    }
    if run_url:
        ci_job["url"] = run_url

    sigstore_entry: dict = {
        "@id":   "#sigstore",
        "@type": "CreativeWork",
        "name":  "Sigstore attestation (Rekor)",
        "about": {"@id": "./"},
    }
    if rekor:
        sigstore_entry["identifier"] = f"rekor_entry:{rekor}"

    dataset: dict = {
        "@id":           "./",
        "@type":         "Dataset",
        "name":          f"RhCore Reference Closure — run {run_id}",
        "datePublished": now,
        "hasPart":       [{"@id": p["@id"]} for p in parts],
        "identifier":    f"run:{run_id}",
        "commit_sha":    commit_sha,
        "subjectOf":     {"@id": "#workflow-run"},
        "prov:wasGeneratedBy": {"@id": "#ci-job"},
    }
    if run_url:
        dataset["ci_run_url"] = run_url
    if rekor:
        dataset["rekor_entry"] = rekor
    if meas_model:
        dataset["measurementTechnique"] = meas_model
    if instruments:
        dataset["instrument"] = [{"@id": i["@id"]} for i in instruments]

    # Li-specific provenance
    if hasattr(args, 'provenance') and args.provenance:
        try:
            prov = json.loads(args.provenance)
            dataset["provenance"] = prov
        except Exception:
            pass

    att_obj = {
        "predicate_type": "https://slsa.dev/provenance/v1",
        "rekor_entry": rekor or "pending",
        "attestation_json": Path(args.attestation).name if args.attestation else "",
    }
    dataset["attestation"] = att_obj

    li_artifact = next((p for p in parts if p.get("name") == "li_n_intervals.csv"), None)
    if li_artifact:
        dataset["artifact"] = {
            "file": li_artifact.get("name", "li_n_intervals.csv"),
            "sha256": li_artifact.get("sha256", ""),
            "signed_by": li_artifact.get("signed_by", ""),
            "signature_file": li_artifact.get("signature_file", ""),
        }

    return {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": [
            {
                "@id":        "ro-crate-metadata.json",
                "@type":      "CreativeWork",
                "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
                "about":      {"@id": "./"},
            },
            dataset,
            workflow_run,
            ci_job,
            sigstore_entry,
            *instruments,
            *parts,
        ],
    }


def build_slsa_attestation(parts: list[dict], args: argparse.Namespace, now: str) -> dict:
    run_id     = args.run_id     or env_or("GITHUB_RUN_ID", "local")
    commit_sha = args.commit_sha or env_or("GITHUB_SHA", "unknown")
    repo       = env_or("GITHUB_REPOSITORY", "RhCore")
    ref        = env_or("GITHUB_REF", "refs/heads/main")
    builder_id = args.builder_id or f"https://github.com/{repo}/.github/workflows/layered_closure.yml"
    rekor      = args.rekor_entry or extract_rekor_uuid(args.patch_rekor)

    return {
        "_type":         "https://in-toto.io/Statement/v0.1",
        "subject":       [{"name": p["name"], "digest": {"sha256": p["sha256"]}} for p in parts],
        "predicateType": "https://slsa.dev/provenance/v1",
        "predicate": {
            "buildDefinition": {
                "buildType":          "https://slsa.dev/container-based-build/v0.1",
                "externalParameters": {"ref": ref, "repository": repo},
                "internalParameters": {},
                "resolvedDependencies": [
                    {"uri": f"git+https://github.com/{repo}",
                     "digest": {"gitCommit": commit_sha}}
                ],
            },
            "runDetails": {
                "builder":  {"id": builder_id},
                "metadata": {"invocationId": run_id, "startedOn": now, "finishedOn": now},
            },
            "rhcore_extension": {
                "rekor_entry":   rekor or "pending",
                "closure_chain": "zeros\u2192Li\u2192micro-closures\u2192validate\u2192freeze",
                "open_gate":     "\u2203 \u03bb > 0, globallyCoercive \u03bb",
            },
        },
    }


def main() -> int:
    args = parse_args()
    out  = Path(args.out)
    now  = datetime.now(timezone.utc).isoformat()

    parts: list[dict] = []
    for raw in args.artifacts:
        p = Path(raw)
        if not p.exists():
            print(f"warning: skipping missing artifact: {p}", file=sys.stderr)
            continue
        parts.append(build_file_entry(p))

    crate = build_ro_crate(parts, args, now)
    out.write_text(json.dumps(crate, indent=2), encoding="utf-8")
    print(f"wrote {out} ({len(parts)} artifacts)")

    if args.attestation:
        att_path = Path(args.attestation)
        att      = build_slsa_attestation(parts, args, now)
        att_path.write_text(json.dumps(att, indent=2), encoding="utf-8")
        print(f"wrote {att_path} (SLSA provenance)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
