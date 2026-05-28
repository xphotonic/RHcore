# Formal Gap Map (RhCore -> Mathlib)

This file maps the RH-spectral program in `RhCore` to currently available
mathlib components and identifies what is still missing for merge-grade
formalization work.

## Status labels

- `available`: core theorem/structure exists in mathlib and can be reused.
- `wrapper-needed`: theorem exists but needs project-local API glue.
- `missing`: no direct mathlib theorem for the needed step yet.

## Current dependency map

### 0) Carrier / gate / cost algebra

- Target: reusable kernel behind the uploaded FFG/Q1/u-d/120-degree documents:
  nonnegative residual cost, zero-cost closure, and 120-degree no-leakage
  readout.
- Source:
  - `RhCore/Core/CarrierGateCost.lean`
- Status: `available`.
- Notes: this layer is fully closed in Lean with no `sorry` or `axiom`. It is
  domain-neutral and should be imported by RH, chemistry, and u/d
  specializations instead of duplicating the algebra.

### A) Zeta / L-series foundation

- Target: formal RH statement + completed zeta functional equation.
- Source:
  - `Mathlib/NumberTheory/LSeries/RiemannZeta.lean`
  - `Mathlib/NumberTheory/LSeries/DirichletContinuation.lean`
- Status: `available`.
- Notes: RH exists as a formal proposition in mathlib; use this as the canonical endpoint.

### B) Dirichlet / Euler-product side

- Target: arithmetic-function side (`Λ`, `ζ`, nonvanishing regions) for prime-side formulas.
- Source:
  - `Mathlib/NumberTheory/LSeries/Dirichlet.lean`
  - `Mathlib/NumberTheory/ArithmeticFunction/VonMangoldt.lean`
  - `Mathlib/NumberTheory/LSeries/Nonvanishing.lean`
- Status: `available`.
- Notes: enough infrastructure to formalize safe regions and explicit algebraic identities.

### C) Spectral linear algebra layer

- Target: finite-dimensional spectral sanity lemmas (eigen/spectrum/radius bounds).
- Source:
  - `Mathlib/LinearAlgebra/Eigenspace/*.lean`
  - `Mathlib/LinearAlgebra/Matrix/Gershgorin.lean`
  - `Mathlib/Analysis/InnerProductSpace/Rayleigh.lean`
- Status: `available` + `wrapper-needed`.
- Notes: great base for matrix/operator approximations and coercivity witnesses.

### D) RH reduction gates in RhCore

- Target: conditional theorem shape `Assumptions -> CriticalGate -> RH`.
- Source:
  - `RhCore/Final.lean`
  - `RhCore/Test/ClosureStub.lean`
- Status: `wrapper-needed`.
- Notes: convert project axioms into modular theorem files with stable import boundaries.

### E) Global coercive spectral gap on phase field

- Target: prove global lower bound (`lambda > 0`) for the projected phase operator.
- Source: no direct one-shot theorem in current mathlib.
- Status: `missing`.
- Notes: this is the real open gate; everything else should be organized around isolating this step.

### F) Explicit spectral growth constant

- Target: a theorem of the form `lambda_n >= c * n * log n` with explicit `c`
  and uniform remainder control.
- Source:
  - `RhCore/Core/SpectralGrowthConstant.lean`
  - heat-trace certificate tooling outside Lean.
- Status: `missing` for the closed universal theorem; `wrapper-needed` for
  conditional theorem packaging.
- Notes: current status is a candidate constant generation mechanism, not a
  finalized constant theorem. The missing gates are:
  1. a self-adjoint/operator object whose eigenvalues are the declared
     `lambda_n`;
  2. a closed coercive lower-growth estimate;
  3. proof that `c` is uniform under truncation, discretization, RH assumptions,
     and basis/kernel choices.

### G) Li/Keiper anomaly radar

- Target: use a suspected off-critical-line zero to quantify spectral damage in
  Li/Keiper coefficients.
- Source:
  - `RhCore/Li/AnomalyRadar.lean`
  - Arb/Julia interval tooling for `D_n(rho)`.
- Status: `available` as a conditional detector; not an RH proof.
- Notes: the Lean layer records the response law
  `lowerAfterPenalty = othersLower - D_n`. The numeric layer certifies the
  penalty `D_n`. A negative radar readout is an anomaly flag, not a theorem
  proving RH or disproving it.

### H) Checkable RH gate

- Target: a mechanically verifiable route from Li/Keiper anomaly detection to
  the project RH statement.
- Source:
  - `RhCore/RH/CheckableHypothesis.lean`
- Status: `wrapper-needed`.
- Notes: the gate is split into two independently checkable hypotheses:
  1. `EveryOffLineZeroHasDamage`: every off-critical zero produces a certified
     Li/Keiper damage certificate;
  2. `LiSafetyBlocksDamage`: certified Li lower bounds block all such damage.
  Lean already proves that these two hypotheses imply
  `RiemannHypothesisStatement`.

### I) Li/Keiper zero-sum bridge

- Target: formalize
  `lambda_n = sum_rho (1 - (1 - 1/rho)^n)` from Hadamard factorization of xi.
- Source:
  - `RhCore/Li/ZeroSum.lean`
- Status: `wrapper-needed` for the finite algebraic layer; `missing` for the
  infinite analytic bridge.
- Notes: Lean currently closes the finite algebraic scaffold and records
  `LiZeroSumBridge` as the exact future proof target. The missing analytic
  inputs are Hadamard factorization for xi, coefficient extraction at `s=1`,
  and convergence/termwise-operation estimates.

### J) Selberg zeta closure side channel

- Target: formalize the geometric chain
  `primitive closed orbit -> length -> phase accumulation -> spectral zero`.
- Source:
  - `RhCore/Core/SelbergClosure.lean`
- Status: `available` for the algebraic critical-line/eigenvalue readout;
  `missing` for the full Selberg trace/product analytic bridge.
- Notes: Lean currently proves the closed algebraic facts
  `Re(1/2 + ir) = 1/2`, `lambda = 1/4 + r^2 >= 1/4`, and symmetry under
  `r -> -r`. The actual Selberg trace formula and product-zero equivalence are
  represented as explicit bridge predicates, not assumed as axioms.

### K) Heat trace / Weyl spectral lower-bound gate

- Target: convert certified heat-trace upper bounds into explicit lower bounds
  for eigenvalues via the formula
  `lambda_n >= -log(TrUp(t) / n) / t`.
- Source:
  - `RhCore/Core/HeatTraceClosure.lean`
  - `docs/heat_trace_weyl_concentration.md`
- Status: `available` for the algebraic Markov/Chebyshev conversion;
  `missing` for the external analytic heat-trace theorem and Weyl-tail
  certificate.
- Notes: the Lean theorem
  `RhCore.HeatTraceClosure.lambda_lower_from_heat_trace` proves the exact
  conversion from `n * exp (-t * lambda) <= TrUp` to the lower-bound readout.
  Recent Neumann heat-trace bounds and Gaussian concentration results should be
  consumed as explicit certificates with constants and provenance, not silently
  promoted to Lean assumptions.

### L) RiemannOperator heat/parity/trace experiments

- Target: executable smoke tests for heat-kernel regularisation, parity
  involution splitting, and trace-to-zeros comparison.
- Source:
  - `tools/riemann_operator_experiments.py`
  - `RhCore/Spectral/RiemannOperatorExperiments.lean`
  - `.github/workflows/riemann_operator_experiments.yml`
  - `docs/riemann_operator_experiments.md`
- Status: `available` as deterministic smoke harness; `bridge-needed` for the
  real RiemannOperator eigenvalue API and analytic error estimates.
- Notes: the current implementation checks wiring, statistics, and artifact
  structure. It is not a proof of the analytic heat regularisation lemma.

## Merge strategy for large formalization

1. Keep upstream-friendly PR slices.
2. Land infrastructure before claims.
3. Separate numerics from core theorems.
4. Use stable naming and avoid local ad-hoc notation in shared modules.

## Recommended PR slicing

1. `PR-1`: API wrappers and import cleanup.
2. `PR-2`: operator/coercivity helper lemmas in finite-dimensional approximations.
3. `PR-3`: conditional reduction theorem skeleton with explicit assumptions.
4. `PR-4`: optional numerical certificate interface (separate from theorem kernel).

## CI gates for contribution readiness

- `lake update`
- `python tools/check_lean_dependency_health.py`
- `lake build`
- `lake env lean test/li_pos_first50.lean`
- `lake env lean --run test/closure_stub.lean`

If any gate fails, do not open a structural PR.
