import FormalField.Core.ResultStatus
import FormalField.Core.GateCostReadout

namespace FormalField

open FormalField.Core

theorem gate_cost_readout_law (P : FormalProcess) (c : P.C) :
    admissible P c → P.G c ∧ P.Q c ≤ P.Θ := by
  intro hadm
  exact ⟨admissible_gate P c hadm, admissible_cost P c hadm⟩

end FormalField
