import FormalField.Core.StructuralRecords
import FormalField.Core.VerificationPipeline
import FormalField.Core.ResultClassification
import FormalField.Core.OrderStatementClarification

namespace FormalField.Core

universe u v

structure AssumptionConstraintClosureSystem where
  Statement : Type u
  State : Type v
  assumed : Statement → Prop
  derivedFromCore : Statement → Prop
  constraintActive : Statement → State → Prop
  closureCondition : Statement → State → Prop

def Assumable (S : AssumptionConstraintClosureSystem) (φ : S.Statement) : Prop :=
  S.assumed φ

def Derivable (S : AssumptionConstraintClosureSystem) (φ : S.Statement) : Prop :=
  S.derivedFromCore φ

def Constrained (S : AssumptionConstraintClosureSystem) (φ : S.Statement) (s : S.State) : Prop :=
  S.constraintActive φ s

def ClosureReady (S : AssumptionConstraintClosureSystem) (φ : S.Statement) (s : S.State) : Prop :=
  S.derivedFromCore φ ∧ S.closureCondition φ s

def ClosedFromCore (S : AssumptionConstraintClosureSystem) (φ : S.Statement) (s : S.State) : Prop :=
  Derivable S φ ∧ ClosureReady S φ s

def AssumptionOnly (S : AssumptionConstraintClosureSystem) (φ : S.Statement) : Prop :=
  Assumable S φ ∧ ¬ Derivable S φ

theorem assumption_only_assumable (S : AssumptionConstraintClosureSystem) (φ : S.Statement) :
    AssumptionOnly S φ → Assumable S φ := by
  intro h
  exact h.1

theorem assumption_only_not_derivable (S : AssumptionConstraintClosureSystem) (φ : S.Statement) :
    AssumptionOnly S φ → ¬ Derivable S φ := by
  intro h
  exact h.2

theorem closed_from_core_derivable (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    ClosedFromCore S φ s → Derivable S φ := by
  intro h
  exact h.1

theorem closed_from_core_closure_ready (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    ClosedFromCore S φ s → ClosureReady S φ s := by
  intro h
  exact h.2

theorem closure_ready_derivable (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    ClosureReady S φ s → Derivable S φ := by
  intro h
  exact h.1

theorem closure_ready_condition (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    ClosureReady S φ s → S.closureCondition φ s := by
  intro h
  exact h.2

theorem assumption_only_not_closed_from_core (S : AssumptionConstraintClosureSystem)
    (φ : S.Statement) (s : S.State) :
    AssumptionOnly S φ → ¬ ClosedFromCore S φ s := by
  intro hAssumption hClosed
  exact hAssumption.2 hClosed.1

def ConstraintVerified (S : AssumptionConstraintClosureSystem) (φ : S.Statement) (s : S.State) :
    Prop :=
  Constrained S φ s ∧ S.closureCondition φ s

theorem constraint_verified_constrained (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    ConstraintVerified S φ s → Constrained S φ s := by
  intro h
  exact h.1

theorem constraint_verified_condition (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    ConstraintVerified S φ s → S.closureCondition φ s := by
  intro h
  exact h.2

theorem constraint_verified_closure_ready_of_derivable (S : AssumptionConstraintClosureSystem)
    (φ : S.Statement) (s : S.State) :
    Derivable S φ →
      ConstraintVerified S φ s →
        ClosureReady S φ s := by
  intro hDerivable hConstraint
  exact ⟨hDerivable, hConstraint.2⟩

theorem closed_from_core_of_derivable_and_constraint_verified
    (S : AssumptionConstraintClosureSystem) (φ : S.Statement) (s : S.State) :
    Derivable S φ →
      ConstraintVerified S φ s →
        ClosedFromCore S φ s := by
  intro hDerivable hConstraint
  exact ⟨hDerivable, ⟨hDerivable, hConstraint.2⟩⟩

structure ClosedConstraintSystem where
  S : AssumptionConstraintClosureSystem
  every_closed_derivable :
    ∀ {φ s}, ClosedFromCore S φ s → Derivable S φ

theorem closed_constraint_derivable (X : ClosedConstraintSystem) (φ : X.S.Statement)
    (s : X.S.State) :
    ClosedFromCore X.S φ s → Derivable X.S φ := by
  intro h
  exact X.every_closed_derivable h

theorem closed_constraint_not_assumption_only (X : ClosedConstraintSystem)
    (φ : X.S.Statement) (s : X.S.State) :
    ClosedFromCore X.S φ s → ¬ AssumptionOnly X.S φ := by
  intro hClosed hAssumption
  exact hAssumption.2 (X.every_closed_derivable hClosed)

end FormalField.Core
