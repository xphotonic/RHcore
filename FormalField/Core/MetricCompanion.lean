import FormalField.Core.StructuralRecords
import FormalField.Core.ObserverDimensionSpace
import FormalField.Core.VerificationPipeline

namespace FormalField.Core

universe u v

structure MetricCompanionSystem where
  Carrier : Type u
  Readout : Type v
  companion : Carrier → Carrier
  readout : Carrier → Readout

def IsCompanion (M : MetricCompanionSystem) (c cStar : M.Carrier) : Prop :=
  M.companion c = cStar

def CompanionGenerated (M : MetricCompanionSystem) (cStar : M.Carrier) : Prop :=
  ∃ c, M.companion c = cStar

def ReadoutPreserved (M : MetricCompanionSystem) (c : M.Carrier) : Prop :=
  M.readout (M.companion c) = M.readout c

def CompanionReadoutPreserving (M : MetricCompanionSystem) : Prop :=
  ∀ c, ReadoutPreserved M c

theorem companion_is_generated (M : MetricCompanionSystem) (c : M.Carrier) :
    CompanionGenerated M (M.companion c) := by
  exact ⟨c, rfl⟩

theorem is_companion_refl_generated (M : MetricCompanionSystem) (c cStar : M.Carrier) :
    IsCompanion M c cStar → CompanionGenerated M cStar := by
  intro h
  exact ⟨c, h⟩

theorem readout_preserved_of_system (M : MetricCompanionSystem) (c : M.Carrier) :
    CompanionReadoutPreserving M → ReadoutPreserved M c := by
  intro h
  exact h c

theorem companion_readout_eq (M : MetricCompanionSystem) (c : M.Carrier) :
    CompanionReadoutPreserving M →
      M.readout (M.companion c) = M.readout c := by
  intro h
  exact h c

structure ClosedCompanionSystem where
  M : MetricCompanionSystem
  readout_preserving : CompanionReadoutPreserving M

theorem closed_companion_preserves_readout (S : ClosedCompanionSystem) (c : S.M.Carrier) :
    S.M.readout (S.M.companion c) = S.M.readout c := by
  exact S.readout_preserving c

theorem closed_companion_generated (S : ClosedCompanionSystem) (c : S.M.Carrier) :
    CompanionGenerated S.M (S.M.companion c) := by
  exact ⟨c, rfl⟩

def CompanionInvolutive (M : MetricCompanionSystem) : Prop :=
  ∀ c, M.companion (M.companion c) = c

theorem involutive_returns_original (M : MetricCompanionSystem) (c : M.Carrier) :
    CompanionInvolutive M →
      M.companion (M.companion c) = c := by
  intro h
  exact h c

end FormalField.Core
