import FormalField.Core.TerminalStructuralClosure

namespace FormalField

open FormalField.Core

theorem terminal_classification_law (S : TerminalClosureSystem) (x : S.Object) :
    TerminallyClassified S x := by
  exact terminally_classified S x

theorem terminal_exhaustive_law (S : TerminalClosureSystem) :
    TerminalExhaustive S := by
  exact terminal_exhaustive_of_classifier S

theorem final_core_terminal_classification_law (X : FinalFormalFieldCore) (x : X.terminal.Object) :
    TerminallyClassified X.terminal x := by
  exact final_core_terminally_classified X x

theorem final_core_classifier_sound_law (X : FinalFormalFieldCore) (x : X.terminal.Object) :
    HasTerminalStatus X.terminal x (X.terminal.classify x) := by
  exact final_core_classifier_sound X x

end FormalField
