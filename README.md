# RhCore_fixed

Open this folder itself in VS Code.

Correct root:
- this folder contains `lakefile.lean`
- this folder contains `lean-toolchain`
- this folder contains the library folder `RhCore/`

Then run:

```bash
lake update
lake exe cache get
lake build
```

Lean dependency hygiene (recommended):

```bash
lake update
python tools/check_lean_dependency_health.py
lake build
```

Formalization governance docs:
- `FORMAL_GAP_MAP.md` (available vs missing mathlib pieces for RH-spectral path)
- `CONTRIBUTING_FORMALIZATION.md` (project contribution rules for Lean/mathlib-facing work)

After that, open:
`RhCore/Core/Final.lean`

AWS execution scaffolding for the reference closure pipeline lives under `aws/`.

Lean Li-interval scaffolding lives under `RhCore/Li/`, and `tools/generate_li_rows.py`
translates `data/li_n_intervals.csv` into `RhCore/Li/LiRows.lean`.

Li/Keiper instability detector:
```bash
python tools/li_keiper_instability_detector.py --a 0.6 --b 14.0 --n-max 30
python tools/li_keiper_instability_detector.py --a 0.6 --b 14.0 --n-max 50 \
  --csv outputs/li_keiper_damage.csv \
  --json outputs/li_keiper_damage.json
```
This is an `mpmath` prototype for witness exploration. Use Arb intervals for
production certificates. The Lean response-law layer is
`RhCore/Li/AnomalyRadar.lean`.

Reproducible AWS-oriented compute template lives in:
- `Makefile.repro`
- `tasks.py`
- `src/compute.py`
- `manifests/schema_rh_state.json`
- `.github/workflows/aws_repro_compute.yml`

Zenodo intake helpers for experimental traces:
- `tools/zenodo_adapter.py` (normalize CSV/ZIP into trace + Landauer + provenance)
- `tools/zenodo_intake.py` (download from Zenodo API by record URL/DOI, then run adapter)
- `repo/data/experimental/zenodo_sources.json` (batch source list)

Examples:
```bash
make experimental-intake-zenodo DATASET=szilard RECORD_URL=https://zenodo.org/records/14516010
make experimental-intake-all
```

Energy/work uncertainty workflow (Papermill + moving-block bootstrap):
- Notebook: `notebooks/landauer.ipynb`
- Sample trace: `traces/run1.csv`
- Type-B config: `inputs/typeB.json`
- Local run:
```bash
python -m pip install papermill numpy pandas scipy nbformat
python scripts/run_landauer_notebook.py --trace-path traces/run1.csv --block-size 5
```
- CI: `.github/workflows/energy_ci.yml` (uploads signed outputs).

Perovskite device provenance template:
- Schema: `data/perovskite/perovskite_devices_template.csv`
- README: `data/perovskite/README.md`
- Validator:
```bash
python tools/validate_perovskite_csv.py \
  --csv data/perovskite/perovskite_devices_template.csv \
  --out outputs/perovskite_devices_enriched.csv \
  --checksums outputs/perovskite_checksums.txt \
  --report outputs/perovskite_validation.json
```
