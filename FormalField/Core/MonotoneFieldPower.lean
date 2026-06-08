namespace FormalField.Core

universe u

structure TransformationSystem where
  State : Type u
  step : State → State → Prop

def MonotonePower (sys : TransformationSystem) (P : sys.State → ℝ) : Prop :=
  ∀ {a b}, sys.step a b → P a ≤ P b

def NonincreasingError (sys : TransformationSystem) (E : sys.State → ℝ) : Prop :=
  ∀ {a b}, sys.step a b → E b ≤ E a

structure CorrectiveSystem where
  sys : TransformationSystem
  E : sys.State → ℝ
  error_nonincreasing : NonincreasingError sys E

structure PowerAccumulationSystem where
  sys : TransformationSystem
  P : sys.State → ℝ
  power_monotone : MonotonePower sys P

theorem monotone_power_step (sys : TransformationSystem) (P : sys.State → ℝ) :
    MonotonePower sys P → ∀ {a b}, sys.step a b → P a ≤ P b := by
  intro h a b hab
  exact h hab

theorem nonincreasing_error_step (sys : TransformationSystem) (E : sys.State → ℝ) :
    NonincreasingError sys E → ∀ {a b}, sys.step a b → E b ≤ E a := by
  intro h a b hab
  exact h hab

theorem two_step_power (sys : TransformationSystem) (P : sys.State → ℝ)
    (hmono : MonotonePower sys P)
    {a b c : sys.State}
    (hab : sys.step a b) (hbc : sys.step b c) :
    P a ≤ P c := by
  exact le_trans (hmono hab) (hmono hbc)

theorem two_step_error (sys : TransformationSystem) (E : sys.State → ℝ)
    (hmono : NonincreasingError sys E)
    {a b c : sys.State}
    (hab : sys.step a b) (hbc : sys.step b c) :
    E c ≤ E a := by
  exact le_trans (hmono hbc) (hmono hab)

end FormalField.Core
