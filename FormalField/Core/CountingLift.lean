import FormalField.Core.MetricTriadic

noncomputable section

namespace FormalField.Core

structure CountingLift where
  A : ℝ
  B : ℝ
  C : ℝ

def CountingLift.toTriadicSpace (R : CountingLift) : TriadicSpace :=
  ![R.A, R.B, R.C]

def CountingLift.ofTriadicSpace (R : TriadicSpace) : CountingLift where
  A := R 0
  B := R 1
  C := R 2

def correctedLift (R : CountingLift) : CountingLift :=
  CountingLift.ofTriadicSpace (projTriadic (CountingLift.toTriadicSpace R))

theorem correctedLift_A (R : CountingLift) :
    (correctedLift R).A = k (CountingLift.toTriadicSpace R) := by
  simp [correctedLift, CountingLift.ofTriadicSpace, CountingLift.toTriadicSpace, projTriadic, v]

theorem correctedLift_B (R : CountingLift) :
    (correctedLift R).B = 2 * k (CountingLift.toTriadicSpace R) := by
  simp [correctedLift, CountingLift.ofTriadicSpace, CountingLift.toTriadicSpace, projTriadic, v,
    mul_comm]

theorem correctedLift_C (R : CountingLift) :
    (correctedLift R).C = 3 * k (CountingLift.toTriadicSpace R) := by
  simp [correctedLift, CountingLift.ofTriadicSpace, CountingLift.toTriadicSpace, projTriadic, v,
    mul_comm]

theorem correctedLift_ratio_line (R : CountingLift) :
    (correctedLift R).B = 2 * (correctedLift R).A ∧
    (correctedLift R).C = 3 * (correctedLift R).A := by
  constructor
  · rw [correctedLift_A, correctedLift_B]
  · rw [correctedLift_A, correctedLift_C]

end FormalField.Core
