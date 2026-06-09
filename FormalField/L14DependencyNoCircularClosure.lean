import FormalField.Core.DependencyNoCircularClosure

namespace FormalField

open FormalField.Core

theorem no_circular_closure_law (S : DependencyClosureSystem) (π : S.ProofObject)
    (φ : S.Statement) :
    ClosedWithoutCircularity S π φ → ¬ CircularDependency S π φ := by
  exact closed_without_circularity_not_circular S π φ

theorem closed_dependency_not_circular_law (X : ClosedDependencySystem)
    (π : X.S.ProofObject) (φ : X.S.Statement) :
    ClosedWithoutCircularity X.S π φ → ¬ CircularDependency X.S π φ := by
  exact closed_dependency_not_circular X π φ

theorem closed_dependency_proves_law (X : ClosedDependencySystem) (π : X.S.ProofObject)
    (φ : X.S.Statement) :
    ClosedWithoutCircularity X.S π φ → X.S.proves π φ := by
  exact closed_dependency_proves X π φ

end FormalField
