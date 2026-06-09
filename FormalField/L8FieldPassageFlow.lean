import FormalField.Core.FieldPassageFlow

namespace FormalField

open FormalField.Core

theorem passage_flow_effect_law (S : PassageFlowSystem) :
    ∀ {a b}, S.F.passage a b → S.F.effect a b := by
  intro a b hab
  exact system_passage_implies_effect S hab

theorem effect_readout_law (P : FormalProcess) (c : P.C) :
    admissible P c → closed_at P c := by
  exact effect_closed_if_admissible P c

end FormalField
