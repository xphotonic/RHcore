import FormalField.Core.StructuralRecords
import FormalField.Core.ProcessValidity
import FormalField.Core.VerificationChain

namespace FormalField

open FormalField.Core

theorem threshold_admissible_implies_gate (P : FormalProcess) (c : P.C)
    (h : P.threshold_admissible c) : P.G c := by
  exact h.1

theorem threshold_admissible_implies_cost_le (P : FormalProcess) (c : P.C)
    (h : P.threshold_admissible c) : P.Q c ≤ P.Θ := by
  exact h.2

theorem verification_complete_implies_carrierDefined (V : VerificationChain)
    (h : verification_complete V) : V.carrierDefined := by
  exact h.1

theorem verification_complete_implies_costNonnegative (V : VerificationChain)
    (h : verification_complete V) : V.costNonnegative := by
  exact h.2.2.2.2.2.2.1

end FormalField
