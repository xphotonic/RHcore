import FormalField.Core.StructuralRecords
import FormalField.Core.VerificationPipeline
import FormalField.Core.ResultClassification
import FormalField.Core.AssumptionConstraintClosure
import FormalField.Core.DependencyNoCircularClosure

namespace FormalField.Core

universe u

inductive TerminalStatus where
  | closedResult
  | accumulation
  | rejected
  | pendingIntegration
deriving DecidableEq

structure TerminalClosureSystem where
  Object : Type u
  closedResult : Object → Prop
  accumulation : Object → Prop
  rejected : Object → Prop
  pendingIntegration : Object → Prop
  classify : Object → TerminalStatus
  classify_sound :
    ∀ x,
      match classify x with
      | TerminalStatus.closedResult => closedResult x
      | TerminalStatus.accumulation => accumulation x
      | TerminalStatus.rejected => rejected x
      | TerminalStatus.pendingIntegration => pendingIntegration x

def HasTerminalStatus (S : TerminalClosureSystem) (x : S.Object) (status : TerminalStatus) : Prop :=
  match status with
  | TerminalStatus.closedResult => S.closedResult x
  | TerminalStatus.accumulation => S.accumulation x
  | TerminalStatus.rejected => S.rejected x
  | TerminalStatus.pendingIntegration => S.pendingIntegration x

def TerminallyClassified (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  ∃ status, HasTerminalStatus S x status

def IsClosedResult (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  HasTerminalStatus S x TerminalStatus.closedResult

def IsAccumulation (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  HasTerminalStatus S x TerminalStatus.accumulation

def IsRejected (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  HasTerminalStatus S x TerminalStatus.rejected

def IsPendingIntegration (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  HasTerminalStatus S x TerminalStatus.pendingIntegration

theorem classified_has_status (S : TerminalClosureSystem) (x : S.Object) :
    HasTerminalStatus S x (S.classify x) := by
  simpa [HasTerminalStatus] using S.classify_sound x

theorem terminally_classified (S : TerminalClosureSystem) (x : S.Object) :
    TerminallyClassified S x := by
  exact ⟨S.classify x, classified_has_status S x⟩

theorem closed_status_is_closed (S : TerminalClosureSystem) (x : S.Object) :
    IsClosedResult S x → S.closedResult x := by
  intro h
  exact h

theorem accumulation_status_is_accumulation (S : TerminalClosureSystem) (x : S.Object) :
    IsAccumulation S x → S.accumulation x := by
  intro h
  exact h

theorem rejected_status_is_rejected (S : TerminalClosureSystem) (x : S.Object) :
    IsRejected S x → S.rejected x := by
  intro h
  exact h

theorem pending_status_is_pending (S : TerminalClosureSystem) (x : S.Object) :
    IsPendingIntegration S x → S.pendingIntegration x := by
  intro h
  exact h

def TerminalExhaustive (S : TerminalClosureSystem) : Prop :=
  ∀ x, TerminallyClassified S x

theorem terminal_exhaustive_of_classifier (S : TerminalClosureSystem) :
    TerminalExhaustive S := by
  intro x
  exact terminally_classified S x

def ClosedOnly (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  S.classify x = TerminalStatus.closedResult

def AccumulationOnly (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  S.classify x = TerminalStatus.accumulation

def RejectedOnly (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  S.classify x = TerminalStatus.rejected

def PendingOnly (S : TerminalClosureSystem) (x : S.Object) : Prop :=
  S.classify x = TerminalStatus.pendingIntegration

theorem closed_only_sound (S : TerminalClosureSystem) (x : S.Object) :
    ClosedOnly S x → S.closedResult x := by
  intro h
  simpa [ClosedOnly, h] using S.classify_sound x

theorem accumulation_only_sound (S : TerminalClosureSystem) (x : S.Object) :
    AccumulationOnly S x → S.accumulation x := by
  intro h
  simpa [AccumulationOnly, h] using S.classify_sound x

theorem rejected_only_sound (S : TerminalClosureSystem) (x : S.Object) :
    RejectedOnly S x → S.rejected x := by
  intro h
  simpa [RejectedOnly, h] using S.classify_sound x

theorem pending_only_sound (S : TerminalClosureSystem) (x : S.Object) :
    PendingOnly S x → S.pendingIntegration x := by
  intro h
  simpa [PendingOnly, h] using S.classify_sound x

theorem closed_not_accumulation_status :
    TerminalStatus.closedResult ≠ TerminalStatus.accumulation := by
  intro h
  cases h

theorem closed_not_rejected_status :
    TerminalStatus.closedResult ≠ TerminalStatus.rejected := by
  intro h
  cases h

theorem closed_not_pending_status :
    TerminalStatus.closedResult ≠ TerminalStatus.pendingIntegration := by
  intro h
  cases h

theorem accumulation_not_rejected_status :
    TerminalStatus.accumulation ≠ TerminalStatus.rejected := by
  intro h
  cases h

theorem accumulation_not_pending_status :
    TerminalStatus.accumulation ≠ TerminalStatus.pendingIntegration := by
  intro h
  cases h

theorem rejected_not_pending_status :
    TerminalStatus.rejected ≠ TerminalStatus.pendingIntegration := by
  intro h
  cases h

structure FinalFormalFieldCore where
  terminal : TerminalClosureSystem
  exhaustive : TerminalExhaustive terminal

theorem final_core_terminally_classified (X : FinalFormalFieldCore) (x : X.terminal.Object) :
    TerminallyClassified X.terminal x := by
  exact X.exhaustive x

theorem final_core_classifier_sound (X : FinalFormalFieldCore) (x : X.terminal.Object) :
    HasTerminalStatus X.terminal x (X.terminal.classify x) := by
  exact classified_has_status X.terminal x

theorem final_core_exhaustive (X : FinalFormalFieldCore) :
    TerminalExhaustive X.terminal := by
  exact X.exhaustive

end FormalField.Core
