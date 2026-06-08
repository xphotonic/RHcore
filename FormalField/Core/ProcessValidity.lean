import FormalField.Core.StructuralRecords

namespace FormalField.Core

def FormalProcess.nonnegative_cost (P : FormalProcess) : Prop :=
  ∀ c, 0 ≤ P.Q c

def FormalProcess.strict_zero_cost_validity (P : FormalProcess) : Prop :=
  ∀ c, P.Q c = 0 → P.r c = 0

def FormalProcess.threshold_admissible (P : FormalProcess) (c : P.C) : Prop :=
  P.G c ∧ P.Q c ≤ P.Θ

def FormalProcess.valid_readout (P : FormalProcess) (c : P.C) : Prop :=
  P.threshold_admissible c

end FormalField.Core
