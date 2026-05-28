import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Data.Real.Basic

/-!
# RiemannOperator Experiment Gates

Lean-facing names for the three computational experiments:

1. heat-kernel regularisation;
2. parity/involution splitting;
3. trace-to-zeros comparison.

The analytic estimates are kept as explicit hypotheses. This file closes the
checkable algebra around the readouts used by the CI smoke harness.
-/

noncomputable section

namespace RhCore.Spectral.RiemannOperatorExperiments

/-- Eigenvalue readout after the heat filter `H_t = exp (-t H^2) H`. -/
def heatFilteredEigenvalue (t lambda : ℝ) : ℝ :=
  Real.exp (-t * lambda ^ 2) * lambda

theorem heatFilteredEigenvalue_zero (lambda : ℝ) :
    heatFilteredEigenvalue 0 lambda = lambda := by
  simp [heatFilteredEigenvalue]

/-- Minimal abstract involution package for parity experiments. -/
structure Involution (V : Type u) where
  J : V → V
  involutive : ∀ x : V, J (J x) = x

/-- A point is even under `J`. -/
def EvenSector {V : Type u} (J : Involution V) (x : V) : Prop :=
  J.J x = x

/-- If `x` is even, applying the involution keeps it even. -/
theorem evenSector_stable {V : Type u} (J : Involution V) {x : V}
    (hx : EvenSector J x) :
    EvenSector J (J.J x) := by
  unfold EvenSector
  rw [J.involutive x, hx]

/-- Trace-to-zeros comparison is exposed as a certificate value. -/
structure TraceToZerosCertificate where
  traceStatistic : ℝ
  zeroStatistic : ℝ
  epsilon : ℝ
  epsilon_nonneg : 0 ≤ epsilon
  certified : |traceStatistic - zeroStatistic| ≤ epsilon

theorem trace_to_zeros_error_bound (cert : TraceToZerosCertificate) :
    |cert.traceStatistic - cert.zeroStatistic| ≤ cert.epsilon :=
  cert.certified

/-- Heat regularisation error gate: the future analytic proof should supply
    the estimate; Lean then exposes it under a stable theorem name. -/
def HeatRegularisedErrorGate
    (baseline regularised C t : ℝ) (alpha : ℕ) : Prop :=
  0 < C ∧ 0 < alpha ∧ |regularised - baseline| ≤ C * t ^ alpha

theorem heat_regularised_error_from_gate
    {baseline regularised C t : ℝ} {alpha : ℕ}
    (h : HeatRegularisedErrorGate baseline regularised C t alpha) :
    |regularised - baseline| ≤ C * t ^ alpha := by
  exact h.2.2

end RhCore.Spectral.RiemannOperatorExperiments
