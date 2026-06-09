import FormalField.Core.AssumptionConstraintClosure

namespace FormalField

open FormalField.Core

theorem assumption_is_not_closure_law (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    AssumptionOnly S φ → ¬ ClosedFromCore S φ s := by
  exact assumption_only_not_closed_from_core S φ s

theorem constraint_to_closure_law (S : AssumptionConstraintClosureSystem) (φ : S.Statement)
    (s : S.State) :
    Derivable S φ →
      ConstraintVerified S φ s →
        ClosedFromCore S φ s := by
  exact closed_from_core_of_derivable_and_constraint_verified S φ s

theorem closed_not_assumption_only_law (X : ClosedConstraintSystem) (φ : X.S.Statement)
    (s : X.S.State) :
    ClosedFromCore X.S φ s → ¬ AssumptionOnly X.S φ := by
  exact closed_constraint_not_assumption_only X φ s

end FormalField
