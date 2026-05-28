import Mathlib.Data.Real.Basic

namespace RhCore.Li

/-- Abstract target value for the true Li coefficient.

This is intentionally opaque: numerical certification files must supply
interval proofs about it instead of using global bound axioms. -/
opaque liTrue : Nat → ℝ

/-- Midpoint-radius interval representation. -/
structure MidRad where
  mid : ℝ
  rad : ℝ
deriving Inhabited

/-- Interval membership for an arbitrary real value. -/
def inInterval (x : ℝ) (mr : MidRad) : Prop :=
  mr.mid - mr.rad ≤ x ∧ x ≤ mr.mid + mr.rad

/-- Interval membership for the true Li coefficient at index `n`. -/
def liInInterval (n : Nat) (mid rad : ℝ) : Prop :=
  inInterval (liTrue n) { mid := mid, rad := rad }

end RhCore.Li
