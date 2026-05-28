import Mathlib.Tactic

/-!
# u/d Carrier Confinement Core

This file formalizes the part of the u/d confinement note that is already
mathematically closed:

* the fixed two-state carrier `u/d`;
* the normalized charge coordinate sending `d` to `0` and `u` to `1`;
* mass as a nonnegative readout of confined quadratic energy;
* strict positive mass as a consequence of the positive-energy gate.

It deliberately does not formalize new particles, external carriers, or a
physical derivation of the curvature energy. Those remain model inputs.
-/

noncomputable section

namespace RhCore.Ud

/-- The fixed two-state `u/d` carrier. -/
inductive UdState where
  | d
  | u
  deriving DecidableEq, Repr

/-- Constants for the normalized charge coordinate. -/
structure ChargeScale where
  q0 : ℝ
  hq0 : 0 < q0

namespace ChargeScale

/-- Charge assignment: `d = -q0`, `u = 2q0`. -/
def charge (c : ChargeScale) : UdState → ℝ
  | UdState.d => -c.q0
  | UdState.u => 2 * c.q0

/-- Normalized coordinate `r(q) = (q + q0) / (3 q0)`. -/
def normalized (c : ChargeScale) (q : ℝ) : ℝ :=
  (q + c.q0) / (3 * c.q0)

lemma q0_ne_zero (c : ChargeScale) : c.q0 ≠ 0 :=
  ne_of_gt c.hq0

/-- The down carrier is the zero endpoint of the normalized coordinate. -/
@[simp] theorem normalized_d (c : ChargeScale) :
    c.normalized (c.charge UdState.d) = 0 := by
  unfold normalized charge
  field_simp [c.q0_ne_zero]

/-- The up carrier is the unit endpoint of the normalized coordinate. -/
@[simp] theorem normalized_u (c : ChargeScale) :
    c.normalized (c.charge UdState.u) = 1 := by
  unfold normalized charge
  field_simp [c.q0_ne_zero]
  ring

end ChargeScale

/-- Minimal closure gates used by the mass-readout theorem. -/
structure ConfinementGates where
  holonomyClosed : Prop
  angularQuantized : Prop
  noLeakage : Prop

/-- A quadratic field cost is nonnegative. -/
def quadraticCost (x : ℝ) : ℝ :=
  x ^ 2

@[simp] theorem quadraticCost_nonneg (x : ℝ) :
    0 ≤ quadraticCost x := by
  unfold quadraticCost
  exact sq_nonneg x

/-- Direction can change sign, but the quadratic directional readout cannot. -/
def directionalQuadraticReadout (alpha energy : ℝ) : ℝ :=
  alpha ^ 2 * energy

theorem directionalQuadraticReadout_nonneg
    (alpha energy : ℝ) (hE : 0 ≤ energy) :
    0 ≤ directionalQuadraticReadout alpha energy := by
  unfold directionalQuadraticReadout
  exact mul_nonneg (sq_nonneg alpha) hE

/-- In the closed model, mass is the confined curvature-energy readout. -/
def massReadout (confinedEnergy : ℝ) : ℝ :=
  confinedEnergy

@[simp] theorem massReadout_nonneg
    {confinedEnergy : ℝ} (hE : 0 ≤ confinedEnergy) :
    0 ≤ massReadout confinedEnergy := by
  simpa [massReadout] using hE

/-- Positive confined energy gives a positive mass readout. -/
theorem positiveMass_of_positiveConfinedEnergy
    {confinedEnergy : ℝ} (hE : 0 < confinedEnergy) :
    0 < massReadout confinedEnergy := by
  simpa [massReadout] using hE

/--
The formal closure theorem for the part of the u/d document that is currently
machine-checkable: once the structural gates hold and the confined energy is
positive, the mass readout is positive.
-/
theorem positiveMass_of_closedConfinement
    (gates : ConfinementGates)
    (_hHol : gates.holonomyClosed)
    (_hAng : gates.angularQuantized)
    (_hNoLeak : gates.noLeakage)
    {confinedEnergy : ℝ}
    (hE : 0 < confinedEnergy) :
    0 < massReadout confinedEnergy := by
  exact positiveMass_of_positiveConfinedEnergy hE

end RhCore.Ud
