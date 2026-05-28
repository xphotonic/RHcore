import Mathlib.Data.Complex.Basic
import RhCore.Li.AnomalyRadar
import RhCore.RH.Main

/-!
# Checkable RH Gate

This file states the RH-facing hypothesis in a form Lean can verify once the
analytic bridge proofs are supplied. It avoids asserting RH directly.

The structure is:

1. an off-line zero has a certified Li/Keiper damage profile;
2. the damage eventually overwhelms the available lower margin;
3. certified nonnegativity of Li coefficients blocks such a zero;
4. therefore all nontrivial zeros lie on the critical line.
-/

noncomputable section

namespace RhCore.RH.Checkable

open RhCore.Li.AnomalyRadar

/-- Predicate for a nontrivial zero that is not on the critical line. -/
def OffCriticalZero (s : ℂ) : Prop :=
  IsNontrivialZero s ∧ ¬ OnCriticalLine s

/-- A margin model for the non-suspect contribution to Li coefficients. -/
structure LiMargin where
  othersLower : ℕ → ℝ

/-- A checkable certificate that a candidate zero creates a radar anomaly. -/
structure DamageCertificate (s : ℂ) where
  offLine : OffCriticalZero s
  penalty : PenaltyBound
  margin : LiMargin
  index : ℕ
  anomaly : anomalyFlag margin.othersLower penalty index

/-- The analytic bridge: every off-critical zero generates a checkable damage
    certificate. This is the first real proof target. -/
def EveryOffLineZeroHasDamage : Prop :=
  ∀ s : ℂ, OffCriticalZero s → Nonempty (DamageCertificate s)

/-- Certified Li safety: no generated damage certificate is allowed. This is
    the second proof target, coming from uniform Li positivity/lower bounds. -/
def LiSafetyBlocksDamage : Prop :=
  ∀ s : ℂ, ¬ Nonempty (DamageCertificate s)

/-- The checkable gate: if every off-line zero creates damage, and certified Li
    safety blocks all damage, then there are no off-critical zeros. -/
theorem no_offline_zeros_of_damage_block
    (hDamage : EveryOffLineZeroHasDamage)
    (hBlock : LiSafetyBlocksDamage) :
    ∀ s : ℂ, IsNontrivialZero s → OnCriticalLine s := by
  intro s hs
  by_contra hnot
  have hoff : OffCriticalZero s := ⟨hs, hnot⟩
  exact hBlock s (hDamage s hoff)

/-- Final project RH statement from the checkable damage gate. -/
theorem rh_of_checkable_li_gate
    (hDamage : EveryOffLineZeroHasDamage)
    (hBlock : LiSafetyBlocksDamage) :
    RiemannHypothesisStatement := by
  exact no_offline_zeros_of_damage_block hDamage hBlock

end RhCore.RH.Checkable
