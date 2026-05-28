import Mathlib.Analysis.SpecialFunctions.Log.Basic
import RhCore.Li.Certified

/-!
# Li/Keiper Anomaly Radar

This file formalizes the safe role of the Li/Keiper off-line-zero calculation:
it is a numerical/spectral anomaly detector, not an RH proof.

A suspected zero off the critical line contributes a nonnegative penalty
`D_n`. If the rest of the Li contribution is bounded below by `othersLower`,
then the total lower bound after accounting for the suspect zero is

`othersLower - D_n`.

The CI/Arb layer computes interval-safe values of `D_n`; Lean records the
logical response law.
-/

noncomputable section

namespace RhCore.Li.AnomalyRadar

/-- Parameters attached to a suspected off-line zero packet. `L` is the
    interval-safe upper/readout for `|log |(rho - 1) / rho||`. -/
structure SuspectZero where
  label : String := ""
  L : ℝ
  hL : 0 ≤ L

/-- Penalty upper bound for one symmetric zero packet. In the analytic model
    this is `4 * (cosh (n * L) - 1)`. We keep it abstract here so the Arb
    certificate can supply a value with interval proof. -/
structure PenaltyBound where
  D : ℕ → ℝ
  nonneg : ∀ n : ℕ, 0 ≤ D n

/-- Lower bound after subtracting the certified suspect-zero penalty. -/
def lowerAfterPenalty
    (othersLower : ℕ → ℝ)
    (penalty : PenaltyBound)
    (n : ℕ) : ℝ :=
  othersLower n - penalty.D n

/-- The response law: if the non-suspect part is bounded below by
    `othersLower n` and the suspect packet can damage the coefficient by at
    most `D_n`, then the certified lower bound after the packet is
    `othersLower n - D_n`. -/
theorem li_lower_after_suspect
    (othersLower : ℕ → ℝ)
    (penalty : PenaltyBound)
    (n : ℕ) :
    lowerAfterPenalty othersLower penalty n =
      othersLower n - penalty.D n := by
  rfl

/-- A negative radar value is an anomaly flag. It is evidence for a mismatch
    between the input zero data and the expected spectral behavior, not a proof
    of RH or its negation. -/
def anomalyFlag
    (othersLower : ℕ → ℝ)
    (penalty : PenaltyBound)
    (n : ℕ) : Prop :=
  lowerAfterPenalty othersLower penalty n < 0

/-- Larger certified damage can only lower the radar readout. -/
theorem monotone_damage
    (othersLower : ℕ → ℝ)
    (p q : PenaltyBound)
    (n : ℕ)
    (h : p.D n ≤ q.D n) :
    lowerAfterPenalty othersLower q n ≤
      lowerAfterPenalty othersLower p n := by
  unfold lowerAfterPenalty
  linarith

end RhCore.Li.AnomalyRadar

