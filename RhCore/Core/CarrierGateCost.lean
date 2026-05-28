import Mathlib.Tactic

/-!
# Carrier Gate Cost Core

This file closes the reusable mathematical kernel that appears across the
uploaded FFG/Q1/u-d/120-degree documents:

* residuals are measured by a nonnegative quadratic cost;
* closure is exactly zero residual;
* the angular gate has center `120`;
* with a nonzero scale, angular readout `120` is equivalent to zero residual;
* monotone/nonnegative return functionals can be represented as squared
  leakage coordinates.

These lemmas are intentionally domain-neutral. RH, chemistry, and u/d modules
should import this layer rather than restating the same algebra.
-/

noncomputable section

namespace RhCore.CarrierGateCost

/-- A one-dimensional residual coordinate. -/
structure Residual where
  value : ℝ

/-- Quadratic residual cost. -/
def residualCost (r : Residual) : ℝ :=
  r.value ^ 2

theorem residualCost_nonneg (r : Residual) :
    0 ≤ residualCost r := by
  unfold residualCost
  exact sq_nonneg r.value

theorem residualCost_eq_zero_iff (r : Residual) :
    residualCost r = 0 ↔ r.value = 0 := by
  unfold residualCost
  constructor
  · intro h
    exact pow_eq_zero h
  · intro h
    simp [h]

/-- Angular readout centered at 120 degrees. -/
def angularReadout (scale : ℝ) (r : Residual) : ℝ :=
  120 + scale * r.value

theorem angularReadout_center_iff
    {scale : ℝ} (hscale : scale ≠ 0) (r : Residual) :
    angularReadout scale r = 120 ↔ r.value = 0 := by
  unfold angularReadout
  constructor
  · intro h
    have hmul : scale * r.value = 0 := by linarith
    exact (mul_eq_zero.mp hmul).resolve_left hscale
  · intro h
    simp [h]

/-- Leakage coordinate used by the 120-degree horizon notes. -/
def leakage (load escape : ℝ) : ℝ :=
  load - escape

/-- Return functional for leakage. -/
def returnFunctional (load escape : ℝ) : ℝ :=
  leakage load escape ^ 2

theorem returnFunctional_nonneg (load escape : ℝ) :
    0 ≤ returnFunctional load escape := by
  unfold returnFunctional
  exact sq_nonneg (leakage load escape)

theorem returnFunctional_eq_zero_iff (load escape : ℝ) :
    returnFunctional load escape = 0 ↔ load = escape := by
  unfold returnFunctional leakage
  constructor
  · intro h
    have hdiff : load - escape = 0 := pow_eq_zero h
    linarith
  · intro h
    simp [leakage, h]

/-- The 120-degree horizon is the zero-leakage locus. -/
theorem horizon120_iff_balanced (load escape : ℝ) :
    angularReadout 4 { value := leakage load escape } = 120 ↔ load = escape := by
  unfold leakage
  change angularReadout 4 { value := load - escape } = 120 ↔ load = escape
  rw [angularReadout_center_iff (by norm_num : (4 : ℝ) ≠ 0)]
  change load - escape = 0 ↔ load = escape
  constructor <;> intro h <;> linarith

end RhCore.CarrierGateCost
