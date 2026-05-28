#!/usr/bin/env bash
set -euo pipefail

zeros_status_path=""
li_path=""
radius_threshold=""
out_path=""
trace_out_path=""

for arg in "$@"; do
  case "$arg" in
    --zeros-status=*)
      zeros_status_path="${arg#*=}"
      ;;
    --li=*)
      li_path="${arg#*=}"
      ;;
    --radius-threshold=*)
      radius_threshold="${arg#*=}"
      ;;
    --out=*)
      out_path="${arg#*=}"
      ;;
    --trace-out=*)
      trace_out_path="${arg#*=}"
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$zeros_status_path" || -z "$li_path" || -z "$radius_threshold" || -z "$out_path" ]]; then
  echo "Usage: $0 --zeros-status=zeta_status.json --li=li_n_intervals.csv --radius-threshold=1e-12 --out=closure_status.json [--trace-out=closure_trace.json]" >&2
  exit 2
fi

cmd=(
  python3 tools/validate_li_artifact.py
  --zeros-status="$zeros_status_path"
  --li="$li_path"
  --radius-threshold="$radius_threshold"
  --out="$out_path"
)

if [[ -n "$trace_out_path" ]]; then
  cmd+=(--trace-out="$trace_out_path")
fi

"${cmd[@]}"
