import FormalField.Core.ResultStatus
import FormalField.Core.GateCostReadout

noncomputable section

namespace FormalField.Core

def classifiesAs (P : FormalProcess) (c : P.C) : ResultStatus → Prop
  | ResultStatus.closed => admissible P c
  | ResultStatus.rejected => rejected_at P c
  | ResultStatus.accumulation => accumulation_at P c
  | ResultStatus.pending => False

theorem classified_closed_iff (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.closed ↔ admissible P c := by
  rfl

theorem classified_rejected_iff (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.rejected ↔ rejected_at P c := by
  rfl

theorem classified_accumulation_iff (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.accumulation ↔ accumulation_at P c := by
  rfl

theorem closed_not_rejected (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.closed → ¬ classifiesAs P c ResultStatus.rejected := by
  intro hclosed hrejected
  exact hrejected (admissible_gate P c hclosed)

theorem accumulation_not_closed (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.accumulation → ¬ classifiesAs P c ResultStatus.closed := by
  exact FormalField.Core.accumulation_not_closed P c

theorem rejected_not_closed (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.rejected → ¬ classifiesAs P c ResultStatus.closed := by
  exact rejected_not_admissible P c

theorem classification_exhaustive (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.closed ∨
      classifiesAs P c ResultStatus.accumulation ∨
      classifiesAs P c ResultStatus.rejected := by
  classical
  by_cases hG : P.G c
  · by_cases hQ : P.Q c ≤ P.Θ
    · left
      exact ⟨hG, hQ⟩
    · right
      left
      exact ⟨hG, hQ⟩
  · right
    right
    exact hG

end FormalField.Core
