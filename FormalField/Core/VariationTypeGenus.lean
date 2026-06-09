import FormalField.Core.StructuralRecords
import FormalField.Core.MetricCompanion
import FormalField.Core.ObserverDimensionSpace

namespace FormalField.Core

universe u v w

structure VariationTypeGenusSystem where
  Object : Type u
  TypeLabel : Type v
  GenusLabel : Type w
  typeOf : Object → TypeLabel
  genusOf : TypeLabel → GenusLabel
  internallyCoherent : Object → Object → Prop
  externallySeparated : Object → Object → Prop

def SameType (S : VariationTypeGenusSystem) (a b : S.Object) : Prop :=
  S.typeOf a = S.typeOf b

def SameGenus (S : VariationTypeGenusSystem) (a b : S.Object) : Prop :=
  S.genusOf (S.typeOf a) = S.genusOf (S.typeOf b)

def TypeRevealed (S : VariationTypeGenusSystem) (a b : S.Object) : Prop :=
  S.internallyCoherent a b ∧ SameType S a b

def TypeSeparated (S : VariationTypeGenusSystem) (a b : S.Object) : Prop :=
  S.externallySeparated a b ∧ ¬ SameType S a b

theorem same_type_refl (S : VariationTypeGenusSystem) (a : S.Object) :
    SameType S a a := by
  rfl

theorem same_type_symm (S : VariationTypeGenusSystem) {a b : S.Object} :
    SameType S a b → SameType S b a := by
  intro h
  exact h.symm

theorem same_type_trans (S : VariationTypeGenusSystem) {a b c : S.Object} :
    SameType S a b → SameType S b c → SameType S a c := by
  intro hab hbc
  exact hab.trans hbc

theorem same_type_implies_same_genus (S : VariationTypeGenusSystem) {a b : S.Object} :
    SameType S a b → SameGenus S a b := by
  intro h
  rw [SameGenus, h]

theorem type_revealed_same_type (S : VariationTypeGenusSystem) {a b : S.Object} :
    TypeRevealed S a b → SameType S a b := by
  intro h
  exact h.2

theorem type_revealed_coherent (S : VariationTypeGenusSystem) {a b : S.Object} :
    TypeRevealed S a b → S.internallyCoherent a b := by
  intro h
  exact h.1

theorem type_separated_not_same_type (S : VariationTypeGenusSystem) {a b : S.Object} :
    TypeSeparated S a b → ¬ SameType S a b := by
  intro h
  exact h.2

theorem type_separated_external (S : VariationTypeGenusSystem) {a b : S.Object} :
    TypeSeparated S a b → S.externallySeparated a b := by
  intro h
  exact h.1

def GenusInvariant (S : VariationTypeGenusSystem) (a b : S.Object) : Prop :=
  SameGenus S a b

theorem same_genus_refl (S : VariationTypeGenusSystem) (a : S.Object) :
    SameGenus S a a := by
  rfl

theorem same_genus_symm (S : VariationTypeGenusSystem) {a b : S.Object} :
    SameGenus S a b → SameGenus S b a := by
  intro h
  exact h.symm

theorem same_genus_trans (S : VariationTypeGenusSystem) {a b c : S.Object} :
    SameGenus S a b → SameGenus S b c → SameGenus S a c := by
  intro hab hbc
  exact hab.trans hbc

theorem genus_invariant_of_same_type (S : VariationTypeGenusSystem) {a b : S.Object} :
    SameType S a b → GenusInvariant S a b := by
  exact same_type_implies_same_genus S

structure ClosedTypeGenusSystem where
  S : VariationTypeGenusSystem
  type_reveal_rule : ∀ {a b}, TypeRevealed S a b → SameType S a b
  genus_rule : ∀ {a b}, SameType S a b → SameGenus S a b

theorem closed_type_reveals_type (X : ClosedTypeGenusSystem) {a b : X.S.Object} :
    TypeRevealed X.S a b → SameType X.S a b := by
  exact X.type_reveal_rule

theorem closed_same_type_same_genus (X : ClosedTypeGenusSystem) {a b : X.S.Object} :
    SameType X.S a b → SameGenus X.S a b := by
  exact X.genus_rule

theorem closed_type_reveals_genus (X : ClosedTypeGenusSystem) {a b : X.S.Object} :
    TypeRevealed X.S a b → SameGenus X.S a b := by
  intro h
  exact X.genus_rule (X.type_reveal_rule h)

end FormalField.Core
