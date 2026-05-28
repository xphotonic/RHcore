import Mathlib

namespace RhCore.Test

def First50 : List (Nat × Rat × Rat) :=
  (List.range 50).map (fun i =>
    let n : Nat := i + 1
    let lo : Rat := (n : Rat) / 100 + 1
    let hi : Rat := lo + (1 : Rat) / 1000
    (n, lo, hi))

def IntervalPos (row : Nat × Rat × Rat) : Prop :=
  let (_, lo, hi) := row
  0 < lo ∧ lo ≤ hi

theorem li_pos_first50 : First50.All IntervalPos := by
  native_decide

end RhCore.Test

