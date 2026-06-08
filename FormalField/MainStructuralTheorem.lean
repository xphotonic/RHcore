import FormalField.Core.CountingLift

noncomputable section

namespace FormalField

theorem metric_triadic_correction_main (R : FormalField.Core.CountingLift)
    (hA : (FormalField.Core.correctedLift R).A ≠ 0) :
    (FormalField.Core.correctedLift R).B = 2 * (FormalField.Core.correctedLift R).A ∧
    (FormalField.Core.correctedLift R).C = 3 * (FormalField.Core.correctedLift R).A ∧
    (FormalField.Core.correctedLift R).A / (FormalField.Core.correctedLift R).B = (1 : ℝ) / 2 ∧
    (FormalField.Core.correctedLift R).A / (FormalField.Core.correctedLift R).C = (1 : ℝ) / 3 ∧
    (FormalField.Core.correctedLift R).B / (FormalField.Core.correctedLift R).C = (2 : ℝ) / 3 := by
  have hk : FormalField.Core.k (FormalField.Core.CountingLift.toTriadicSpace R) ≠ 0 := by
    simpa [FormalField.Core.correctedLift_A] using hA
  refine ⟨(FormalField.Core.correctedLift_ratio_line R).1,
    (FormalField.Core.correctedLift_ratio_line R).2, ?_, ?_, ?_⟩
  · simpa [FormalField.Core.correctedLift, FormalField.Core.CountingLift.ofTriadicSpace] using
      (FormalField.Core.projTriadic_ratio_AB (FormalField.Core.CountingLift.toTriadicSpace R) hk)
  · simpa [FormalField.Core.correctedLift, FormalField.Core.CountingLift.ofTriadicSpace] using
      (FormalField.Core.projTriadic_ratio_AC (FormalField.Core.CountingLift.toTriadicSpace R) hk)
  · simpa [FormalField.Core.correctedLift, FormalField.Core.CountingLift.ofTriadicSpace] using
      (FormalField.Core.projTriadic_ratio_BC (FormalField.Core.CountingLift.toTriadicSpace R) hk)

end FormalField
