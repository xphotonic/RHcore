#!/usr/bin/env python3
"""Lightweight orchestration for reproducible compute bundles."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import os
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: list[str], check: bool = True) -> int:
    print("+", " ".join(cmd))
    proc = subprocess.run(cmd)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def utc_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def write_checksums(out_dir: Path) -> None:
    lines: list[str] = []
    for path in sorted(out_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name == "checksums.txt":
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    (out_dir / "checksums.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_run(args: argparse.Namespace) -> int:
    run_id = args.run_id or utc_run_id()
    out_dir = Path(args.out_root) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    zero_table = out_dir / "ZERO_TABLE.csv"
    manifest = out_dir / "RH_STATE.json"

    run(
        [
            "python",
            "-m",
            "src.compute",
            "--out",
            str(zero_table),
            "--n",
            str(args.n),
            "--seed",
            str(args.seed),
        ]
    )
    run(
        [
            "python",
            "-m",
            "src.compute",
            "--manifest",
            str(manifest),
            "--emit-manifest",
            "--run-id",
            run_id,
            "--lock-file",
            args.lock_file,
            "--input-s3",
            args.input_s3,
            "--input-sha256",
            args.input_sha256,
            "--instance-type",
            args.instance_type,
        ]
        + (["--spot"] if args.spot else [])
    )

    write_checksums(out_dir)
    print(f"run complete: {out_dir}")
    return 0


def cmd_attest(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    checksums = out_dir / "checksums.txt"
    if not checksums.exists():
        raise SystemExit(f"missing checksums file: {checksums}")

    cosign = shutil.which("cosign")
    if cosign is None:
        print("cosign not found; skipping attest")
        return 0

    bundle = out_dir / "bundle.attestation"
    sig = out_dir / "signature.sig"
    run(["cosign", "sign-blob", "--yes", "--bundle", str(bundle), str(checksums)])
    # preserve a small pointer file for tooling that expects signature.sig
    sig.write_text("use bundle.attestation", encoding="utf-8")
    print(f"attested: {bundle}")
    return 0


def cmd_push(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    if not out_dir.exists():
        raise SystemExit(f"missing out dir: {out_dir}")
    target = f"s3://{args.bucket}/{args.project}/{out_dir.name}/"
    run(["aws", "s3", "cp", str(out_dir), target, "--recursive"])
    print(f"uploaded: {target}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    out_dir = Path(args.out_dir)
    checksums = out_dir / "checksums.txt"
    bundle = out_dir / "bundle.attestation"
    if not checksums.exists():
        raise SystemExit(f"missing checksums file: {checksums}")

    cosign = shutil.which("cosign")
    if cosign is None:
        print("cosign not found; skipping verify")
        return 0
    if not bundle.exists():
        raise SystemExit(f"missing bundle: {bundle}")

    cmd = ["cosign", "verify-blob", "--bundle", str(bundle), str(checksums)]
    repo = os.environ.get("GITHUB_REPOSITORY")
    if repo:
        cmd.extend(
            [
                "--certificate-identity-regexp",
                f"https://github.com/{repo}/.*",
                "--certificate-oidc-issuer",
                "https://token.actions.githubusercontent.com",
            ]
        )
    run(cmd)
    print("verify: OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run")
    p_run.add_argument("--run-id")
    p_run.add_argument("--out-root", default="out")
    p_run.add_argument("--n", type=int, default=10)
    p_run.add_argument("--seed", type=int, default=42)
    p_run.add_argument("--lock-file", default="env.lock")
    p_run.add_argument("--input-s3", default="s3://data/zeros/v1")
    p_run.add_argument("--input-sha256", default="unknown")
    p_run.add_argument("--instance-type", default="ml.t3.medium")
    p_run.add_argument("--spot", action="store_true")
    p_run.set_defaults(func=cmd_run)

    p_attest = sub.add_parser("attest")
    p_attest.add_argument("--out-dir", required=True)
    p_attest.set_defaults(func=cmd_attest)

    p_push = sub.add_parser("push")
    p_push.add_argument("--out-dir", required=True)
    p_push.add_argument("--bucket", required=True)
    p_push.add_argument("--project", default="myproj")
    p_push.set_defaults(func=cmd_push)

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--out-dir", required=True)
    p_verify.set_defaults(func=cmd_verify)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
