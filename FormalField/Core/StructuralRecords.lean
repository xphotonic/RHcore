namespace FormalField.Core

universe u v w

structure Carrier where
  C : Type u

structure Metric (R : Type u) where
  distance : R → R → ℝ

structure Target (C : Type u) (R : Type v) where
  map : C → R

structure Representation (C : Type u) (R : Type v) where
  map : C → R

structure Residual (C : Type u) (R : Type v) where
  map : C → R

structure Gate (C : Type u) where
  holds : C → Prop

structure Cost (C : Type u) where
  eval : C → ℝ

structure Threshold where
  value : ℝ

structure Readout (C : Type u) (O : Type v) where
  eval : C → O

structure FormalProcess where
  C : Type u
  R : Type v
  O : Type w
  instZeroR : Zero R
  τ : C → R
  ρ : C → R
  r : C → R
  G : C → Prop
  Q : C → ℝ
  Θ : ℝ
  ν : C → O

attribute [instance] FormalProcess.instZeroR

end FormalField.Core
