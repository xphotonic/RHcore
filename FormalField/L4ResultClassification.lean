import FormalField.Core.ResultClassification

noncomputable section

namespace FormalField

open FormalField.Core

theorem result_classification_law (P : FormalProcess) (c : P.C) :
    classifiesAs P c ResultStatus.closed ∨
      classifiesAs P c ResultStatus.accumulation ∨
      classifiesAs P c ResultStatus.rejected := by
  exact classification_exhaustive P c

end FormalField
