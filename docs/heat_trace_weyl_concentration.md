# Heat Trace, Weyl, and Concentration Closure Notes

This note records how recent heat-kernel and concentration inputs should enter
the RhCore verification stack without overstating them.

## Verified locally

- Lean algebraic gate:
  `RhCore.Core.HeatTraceClosure.lambda_lower_from_heat_trace`.
- It proves the exact conversion used by the numeric sweep:
  if `0 < t`, `0 < n`, `0 < TrUp`, and
  `n * exp (-t * lambda) <= TrUp`, then
  `-(log (TrUp / n)) / t <= lambda`.

## Analytic bridge needed

To use the gate for a concrete domain, the CI pipeline must supply:

- a certified heat-trace upper bound `TrUp(t)`;
- a counting inequality that yields
  `n * exp (-t * lambda_n) <= TrUp(t)`;
- explicit geometric constants such as dimension, volume, boundary term, and
  convexity/regularity assumptions;
- a Weyl-tail certificate, preferably with interval arithmetic.

## Current external anchors

- Frank and Larson, `arXiv:2601.07341`, gives all-time Neumann heat-trace
  bounds for convex domains capturing the first two short-time terms with
  simple geometric characteristics.
- Frank and Larson, `arXiv:2407.11808`, covers Dirichlet and Neumann Riesz
  means on Lipschitz domains and gives universal non-asymptotic convex-domain
  bounds for the corresponding spectral means.
- Koirala, `arXiv:2605.21193`, gives sharp Gaussian isoperimetry along Ricci
  flow for conjugate heat-kernel measures. This belongs to a concentration
  side channel, not directly to the finite eigenvalue lower-bound gate.

## Operator family routing

- Family A: Euclidean convex-domain Laplacians. Good first target for
  certified constants once the geometric inputs are fixed.
- Family B: Laplace-Beltrami operators. Keep as bridge-needed until curvature,
  volume, diameter, and heat-kernel hypotheses are explicit.
- Family C: known-spectrum cards. Use `tools/spectral_benchmark_cards.py` in CI
  to test indexing, multiplicity, and the heat-trace conversion before using
  Arb certificates.

## Safe integration policy

- Treat heat-trace bounds as input certificates, not as Lean-proved analytic
  theorems yet.
- Store the exact source theorem, constants, domain assumptions, and commit/SHA
  provenance next to generated numeric artifacts.
- Keep concentration estimates separate unless they produce a concrete
  inequality consumed by a named gate.
