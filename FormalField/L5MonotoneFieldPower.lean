import FormalField.Core.MonotoneFieldPower

namespace FormalField

open FormalField.Core

theorem monotone_field_power_law (sys : TransformationSystem)
    (P E : sys.State → ℝ)
    (hP : MonotonePower sys P)
    (hE : NonincreasingError sys E)
    {a b c : sys.State}
    (hab : sys.step a b) (hbc : sys.step b c) :
    P a ≤ P c ∧ E c ≤ E a := by
  exact ⟨two_step_power sys P hP hab hbc, two_step_error sys E hE hab hbc⟩

end FormalField
