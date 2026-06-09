import FormalField.Core.StructuralRecords
import FormalField.Core.GateCostReadout
import FormalField.Core.ResultClassification
import FormalField.Core.VerificationPipeline
import FormalField.Core.MonotoneFieldPower
import FormalField.Core.NoStableResidual

namespace FormalField.Core

universe u

structure FieldSystem where
  State : Type u
  passage : State → State → Prop
  flow : State → State → Prop
  effect : State → State → Prop

def PassagePreservesCarrier (F : FieldSystem) : Prop :=
  ∀ {a b}, F.passage a b → F.flow a b ∨ a = b

def PassageProducesFlow (F : FieldSystem) : Prop :=
  ∀ {a b}, F.passage a b → F.flow a b

def FlowProducesEffect (F : FieldSystem) : Prop :=
  ∀ {a b}, F.flow a b → F.effect a b

def FlowPreservesState (F : FieldSystem) : Prop :=
  ∀ {a b}, F.flow a b → True

structure PassageFlowSystem where
  F : FieldSystem
  passage_to_flow : PassageProducesFlow F
  flow_to_effect : FlowProducesEffect F

theorem passage_implies_flow (F : FieldSystem) :
    PassageProducesFlow F → ∀ {a b}, F.passage a b → F.flow a b := by
  intro h a b hab
  exact h hab

theorem flow_implies_effect (F : FieldSystem) :
    FlowProducesEffect F → ∀ {a b}, F.flow a b → F.effect a b := by
  intro h a b hab
  exact h hab

theorem passage_implies_effect (F : FieldSystem) :
    PassageProducesFlow F →
      FlowProducesEffect F →
      ∀ {a b}, F.passage a b → F.effect a b := by
  intro hpass hflow a b hab
  exact hflow (hpass hab)

theorem system_passage_implies_flow (S : PassageFlowSystem) :
    ∀ {a b}, S.F.passage a b → S.F.flow a b := by
  intro a b hab
  exact S.passage_to_flow hab

theorem system_passage_implies_effect (S : PassageFlowSystem) :
    ∀ {a b}, S.F.passage a b → S.F.effect a b := by
  intro a b hab
  exact S.flow_to_effect (S.passage_to_flow hab)

theorem effect_closed_if_admissible (P : FormalProcess) (c : P.C) :
    admissible P c → closed_at P c := by
  intro h
  exact h

theorem effect_accumulation_if_gate_without_cost (P : FormalProcess) (c : P.C) :
    accumulation_at P c → ¬ closed_at P c := by
  exact accumulation_not_closed P c

theorem effect_rejected_if_gate_failed (P : FormalProcess) (c : P.C) :
    rejected_at P c → ¬ admissible P c := by
  exact rejected_not_admissible P c

end FormalField.Core
