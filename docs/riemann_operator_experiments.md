# RiemannOperator Experiments

This file records the executable status of the three proposed smoke tests.

## Commands

```bash
python tools/riemann_operator_experiments.py run_heat \
  --json outputs/riemann_operator_run_heat.json \
  --csv outputs/riemann_operator_run_heat.csv \
  --strict

python tools/riemann_operator_experiments.py run_parity \
  --json outputs/riemann_operator_run_parity.json \
  --csv outputs/riemann_operator_run_parity.csv \
  --strict

python tools/riemann_operator_experiments.py run_trace \
  --json outputs/riemann_operator_run_trace.json \
  --csv outputs/riemann_operator_run_trace.csv \
  --strict

python tools/riemann_operator_experiments.py run_all \
  --json outputs/riemann_operator_experiments.json \
  --csv outputs/riemann_operator_experiments.csv \
  --strict
```

## Interpretation

- `run_heat` tracks the heat-filter displacement, spacing coefficient of
  variation, and a local Weyl-style count error.
- `run_parity` splits the deterministic smoke spectrum into even and odd
  sectors and compares spacing statistics against the full spectrum.
- `run_trace` compares a Gaussian trace statistic on the heat-filtered spectrum
  with a zero-like statistic.

## Formal hooks

- Lean file:
  `RhCore/Spectral/RiemannOperatorExperiments.lean`.
- CI file:
  `.github/workflows/riemann_operator_experiments.yml`.

The current script uses a deterministic model spectrum. The next integration
step is replacing `model_spectrum` with the real RiemannOperator eigenvalue API
once it is stable.

