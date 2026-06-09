import FormalField.Core.StructuralRecords
import FormalField.Core.VerificationPipeline
import FormalField.Core.ResultClassification
import FormalField.Core.AssumptionConstraintClosure

namespace FormalField.Core

universe u v

structure DependencyClosureSystem where
  Statement : Type u
  ProofObject : Type v
  proves : ProofObject → Statement → Prop
  dependsOn : ProofObject → Statement → Prop
  equivalentTo : Statement → Statement → Prop

def SelfDependency (S : DependencyClosureSystem) (π : S.ProofObject) (φ : S.Statement) : Prop :=
  S.dependsOn π φ

def HiddenEquivalentDependency (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) : Prop :=
  ∃ ψ, S.equivalentTo ψ φ ∧ S.dependsOn π ψ

def CircularDependency (S : DependencyClosureSystem) (π : S.ProofObject) (φ : S.Statement) :
    Prop :=
  SelfDependency S π φ ∨ HiddenEquivalentDependency S π φ

def NoSelfDependency (S : DependencyClosureSystem) (π : S.ProofObject) (φ : S.Statement) : Prop :=
  ¬ SelfDependency S π φ

def NoHiddenEquivalentDependency (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) : Prop :=
  ¬ HiddenEquivalentDependency S π φ

def NonCircularProof (S : DependencyClosureSystem) (π : S.ProofObject) (φ : S.Statement) : Prop :=
  S.proves π φ ∧ NoSelfDependency S π φ ∧ NoHiddenEquivalentDependency S π φ

def ClosedWithoutCircularity (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) : Prop :=
  NonCircularProof S π φ

def RejectedCircularProof (S : DependencyClosureSystem) (π : S.ProofObject) (φ : S.Statement) :
    Prop :=
  CircularDependency S π φ

theorem non_circular_proves (S : DependencyClosureSystem) (π : S.ProofObject) (φ : S.Statement) :
    NonCircularProof S π φ → S.proves π φ := by
  intro h
  exact h.1

theorem non_circular_no_self (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    NonCircularProof S π φ → NoSelfDependency S π φ := by
  intro h
  exact h.2.1

theorem non_circular_no_hidden (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    NonCircularProof S π φ → NoHiddenEquivalentDependency S π φ := by
  intro h
  exact h.2.2

theorem closed_without_circularity_proves (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    ClosedWithoutCircularity S π φ → S.proves π φ := by
  exact non_circular_proves S π φ

theorem closed_without_circularity_no_self (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    ClosedWithoutCircularity S π φ → NoSelfDependency S π φ := by
  exact non_circular_no_self S π φ

theorem closed_without_circularity_no_hidden (S : DependencyClosureSystem)
    (π : S.ProofObject) (φ : S.Statement) :
    ClosedWithoutCircularity S π φ → NoHiddenEquivalentDependency S π φ := by
  exact non_circular_no_hidden S π φ

theorem self_dependency_is_circular (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    SelfDependency S π φ → CircularDependency S π φ := by
  intro h
  exact Or.inl h

theorem hidden_dependency_is_circular (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    HiddenEquivalentDependency S π φ → CircularDependency S π φ := by
  intro h
  exact Or.inr h

theorem rejected_circular_is_circular (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    RejectedCircularProof S π φ → CircularDependency S π φ := by
  intro h
  exact h

theorem non_circular_not_circular (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    NonCircularProof S π φ → ¬ CircularDependency S π φ := by
  intro hNon hCircular
  cases hCircular with
  | inl hSelf =>
      exact hNon.2.1 hSelf
  | inr hHidden =>
      exact hNon.2.2 hHidden

theorem closed_without_circularity_not_circular (S : DependencyClosureSystem)
    (π : S.ProofObject) (φ : S.Statement) :
    ClosedWithoutCircularity S π φ → ¬ CircularDependency S π φ := by
  exact non_circular_not_circular S π φ

structure ClosedDependencySystem where
  S : DependencyClosureSystem
  closure_requires_non_circular :
    ∀ {π φ}, ClosedWithoutCircularity S π φ → NonCircularProof S π φ

theorem closed_dependency_non_circular (X : ClosedDependencySystem) (π : X.S.ProofObject)
    (φ : X.S.Statement) :
    ClosedWithoutCircularity X.S π φ → NonCircularProof X.S π φ := by
  intro h
  exact X.closure_requires_non_circular h

theorem closed_dependency_not_circular (X : ClosedDependencySystem) (π : X.S.ProofObject)
    (φ : X.S.Statement) :
    ClosedWithoutCircularity X.S π φ → ¬ CircularDependency X.S π φ := by
  intro h
  exact non_circular_not_circular X.S π φ (X.closure_requires_non_circular h)

theorem closed_dependency_proves (X : ClosedDependencySystem) (π : X.S.ProofObject)
    (φ : X.S.Statement) :
    ClosedWithoutCircularity X.S π φ → X.S.proves π φ := by
  intro h
  exact (X.closure_requires_non_circular h).1

end FormalField.Core
