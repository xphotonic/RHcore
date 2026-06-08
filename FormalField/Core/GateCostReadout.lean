import FormalField.Core.ProcessValidity
import FormalField.Core.VerificationChain

namespace FormalField.Core

def gate_passed (P : FormalProcess) (c : P.C) : Prop :=
  P.G c

def cost_bounded (P : FormalProcess) (c : P.C) : Prop :=
  P.Q c ≤ P.Θ

def admissible (P : FormalProcess) (c : P.C) : Prop :=
  P.threshold_admissible c

def closed_at (P : FormalProcess) (c : P.C) : Prop :=
  admissible P c

def rejected_at (P : FormalProcess) (c : P.C) : Prop :=
  ¬ P.G c

def accumulation_at (P : FormalProcess) (c : P.C) : Prop :=
  P.G c ∧ ¬ P.Q c ≤ P.Θ

theorem admissible_gate (P : FormalProcess) (c : P.C) :
    admissible P c → P.G c := by
  intro h
  exact h.1

theorem admissible_cost (P : FormalProcess) (c : P.C) :
    admissible P c → P.Q c ≤ P.Θ := by
  intro h
  exact h.2

theorem closed_implies_admissible (P : FormalProcess) (c : P.C) :
    closed_at P c → admissible P c := by
  intro h
  exact h

theorem rejected_not_admissible (P : FormalProcess) (c : P.C) :
    rejected_at P c → ¬ admissible P c := by
  intro hreject hadm
  exact hreject hadm.1

theorem accumulation_not_closed (P : FormalProcess) (c : P.C) :
    accumulation_at P c → ¬ closed_at P c := by
  intro hacc hclosed
  exact hacc.2 hclosed.2

theorem zero_cost_residual_zero (P : FormalProcess) (c : P.C) :
    P.strict_zero_cost_validity →
    P.Q c = 0 →
    P.r c = 0 := by
  intro hvalid hzero
  exact hvalid c hzero

end FormalField.Core
