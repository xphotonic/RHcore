# AWS Reference Closure Path

This directory turns the current local `RhCore` closure pipeline into an AWS flow architecture.

## Pipeline

```
ZerosSanity → LiIntervals → MicroClosures → ValidateAndFreeze
```

## Stages

### Stage 1: ZerosSanity
`buildspec/zeros_sanity.yml`
- Downloads zeros CSV from S3
- Runs `tools/zeta_sanity.py`
- Uploads `zeta_status.json`

### Stage 2: LiIntervals
`buildspec/li_intervals.yml`
- Downloads `zeta_status.json`, extracts checksum
- Runs `ci/li_extend.jl` (Julia)
- Uploads `li_n_intervals.csv`

### Stage 3: MicroClosures (new)
`buildspec/micro_closures.yml`
- Runs all 8 spectral/phase/energy checks:
  - heat_kernel, phase_seal, li_positivity
  - poincare_witness, spectral_gap
  - explicit_inequality, asymptotic_gap
  - derivative_at_zeros
- Generates `cyber_riemann_artifact.json`
- Gates on PASS/WARN status
- Uploads all JSON artifacts

### Stage 4: ValidateAndFreeze
`buildspec/validate_and_freeze.yml`
- Validates Li artifact
- Builds RO-Crate
- Freezes bundle + SHA256

## Orchestration
`stepfunctions/reference_closure.asl.json`
- Step Functions state machine
- Sequential with error handling
- Input: `aws/config/reference_closure.example.json`

## S3 Layout
```
s3://bucket/
  input/zeros/zeros_prechecked.csv
  runs/<run-id>/
    zeta_status.json
    li_n_intervals.csv
    micro_closures/
      heat_kernel_check.json
      phase_seal.json
      poincare_witness.json
      spectral_gap_check.json
      explicit_inequality_check.json
      asymptotic_gap_check.json
      derivative_at_zeros.json
      cyber_riemann_artifact.json
    closure_status.json
    ro-crate-metadata.json
  releases/<run-id>/
    reference_closure_bundle.tar.gz
    reference_closure_bundle.sha256
```

## IAM Requirements
- CodeBuild role: `s3:GetObject`, `s3:PutObject` on artifact bucket
- Step Functions role: `codebuild:StartBuild`, `codebuild:BatchGetBuilds`


## Chosen Path

The path is:

`zeros -> li intervals -> validate -> freeze`

mapped onto AWS as:

- `S3`: source of truth and artifact store
- `CodeBuild`: execution layer for Python and Julia steps
- `Step Functions`: orchestration and gate sequencing
- `CloudWatch Logs`: execution trace and failure visibility

This keeps the current repo logic intact:

- `tools/zeta_sanity.py`
- `ci/li_extend.jl`
- `tools/validate_li_artifact.py`
- `tools/build_ro_crate.py`

## Bucket Layout

Use one artifact bucket with stable prefixes:

- `input/zeros/zeros_prechecked.csv`
- `runs/<run-id>/zeta_status.json`
- `runs/<run-id>/li_n_intervals.csv`
- `runs/<run-id>/closure_status.json`
- `runs/<run-id>/closure_trace.json`
- `runs/<run-id>/ro-crate-metadata.json`
- `releases/<run-id>/reference_closure_bundle.tar.gz`
- `releases/<run-id>/reference_closure_bundle.sha256`

## AWS Execution Model

### Stage 1: Zeros Sanity

CodeBuild runs:

```bash
python tools/zeta_sanity.py --zeros=repo/data/zeros_prechecked.csv > zeta_status.json
```

Then uploads:

- `zeta_status.json`
- the exact `zeros_prechecked.csv` snapshot used for the run

### Stage 2: Li Intervals

CodeBuild downloads `zeta_status.json`, extracts `zeros_checksum`, then runs:

```bash
julia --project=. ci/li_extend.jl --bits=512 --n_start=10 --n_end=20 --zeros-checksum=<checksum> --out=li_n_intervals.csv
```

Then uploads:

- `li_n_intervals.csv`

### Stage 3: Validate and Freeze

CodeBuild downloads:

- `zeros_prechecked.csv`
- `zeta_status.json`
- `li_n_intervals.csv`

Then runs:

```bash
python tools/validate_li_artifact.py \
  --zeros-status=zeta_status.json \
  --li=li_n_intervals.csv \
  --radius-threshold=1e-12 \
  --out=closure_status.json \
  --trace-out=closure_trace.json
```

and:

```bash
python tools/build_ro_crate.py \
  --artifact repo/data/zeros_prechecked.csv \
  --artifact zeta_status.json \
  --artifact li_n_intervals.csv \
  --artifact closure_status.json \
  --artifact closure_trace.json \
  --artifact OWNERS.md \
  --out ro-crate-metadata.json
```

Finally it freezes:

- `reference_closure_bundle.tar.gz`
- `reference_closure_bundle.sha256`

## Why This Path

This is the closest AWS mapping to the current repo:

- it preserves the existing closure machine
- it uses S3 as the data layer
- it treats Step Functions as flow control, not business logic
- it avoids premature migration to SageMaker before the closure artifacts are stable

## What Is Intentionally Not Done Here

- No AWS-native signing for the release tarball
- No SageMaker training or endpoints yet
- No Lambda rewrite of the existing scripts

Reason:

the current repo already has a stable artifact flow. The first AWS move should preserve it, not reshape it.

## Files in This Directory

- `config/reference_closure.example.json`
- `stepfunctions/reference_closure.asl.json`
- `buildspec/zeros_sanity.yml`
- `buildspec/li_intervals.yml`
- `buildspec/validate_and_freeze.yml`

## Next Safe Upgrade

Once this path is stable, the next upgrade is:

- SageMaker Processing for the Julia interval job, or
- an ML branch alongside closure artifacts, not inside them
