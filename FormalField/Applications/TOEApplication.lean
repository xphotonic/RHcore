import FormalField.Applications.ApplicationCore

namespace FormalField
namespace Applications

inductive TOEObligation where
  | stateSpace
  | localConsistency
  | symmetryDescent
  | observableReconstruction
  | causalDescent
  | globalCompatibility
deriving DecidableEq, Repr

structure TOEApplication where
  obligationReady : TOEObligation → Prop

def TOEStructuralReady (T : TOEApplication) : Prop :=
  T.obligationReady TOEObligation.stateSpace ∧
    T.obligationReady TOEObligation.localConsistency ∧
    T.obligationReady TOEObligation.symmetryDescent ∧
    T.obligationReady TOEObligation.observableReconstruction

def TOEGlobalReady (T : TOEApplication) : Prop :=
  T.obligationReady TOEObligation.causalDescent ∧
    T.obligationReady TOEObligation.globalCompatibility

theorem toe_structural_ready_stateSpace (T : TOEApplication) :
    TOEStructuralReady T → T.obligationReady TOEObligation.stateSpace := by
  intro h
  exact h.1

theorem toe_structural_ready_localConsistency (T : TOEApplication) :
    TOEStructuralReady T → T.obligationReady TOEObligation.localConsistency := by
  intro h
  exact h.2.1

theorem toe_structural_ready_symmetryDescent (T : TOEApplication) :
    TOEStructuralReady T → T.obligationReady TOEObligation.symmetryDescent := by
  intro h
  exact h.2.2.1

theorem toe_structural_ready_observableReconstruction (T : TOEApplication) :
    TOEStructuralReady T → T.obligationReady TOEObligation.observableReconstruction := by
  intro h
  exact h.2.2.2

theorem toe_global_ready_causalDescent (T : TOEApplication) :
    TOEGlobalReady T → T.obligationReady TOEObligation.causalDescent := by
  intro h
  exact h.1

theorem toe_global_ready_globalCompatibility (T : TOEApplication) :
    TOEGlobalReady T → T.obligationReady TOEObligation.globalCompatibility := by
  intro h
  exact h.2

-- The TOE application is reduced to state representation, symmetry descent,
-- observable reconstruction, causal descent, and global compatibility.

end Applications
end FormalField
