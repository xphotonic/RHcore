import FormalField.Core.VariationTypeGenus

namespace FormalField

open FormalField.Core

theorem variation_type_law (X : ClosedTypeGenusSystem) {a b : X.S.Object} :
    TypeRevealed X.S a b → SameType X.S a b := by
  exact closed_type_reveals_type X

theorem type_genus_law (X : ClosedTypeGenusSystem) {a b : X.S.Object} :
    SameType X.S a b → SameGenus X.S a b := by
  exact closed_same_type_same_genus X

theorem revealed_type_genus_law (X : ClosedTypeGenusSystem) {a b : X.S.Object} :
    TypeRevealed X.S a b → SameGenus X.S a b := by
  exact closed_type_reveals_genus X

end FormalField
