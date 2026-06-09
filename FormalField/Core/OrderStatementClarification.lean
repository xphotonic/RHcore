import FormalField.Core.StructuralRecords
import FormalField.Core.VerificationPipeline
import FormalField.Core.ObserverDimensionSpace
import FormalField.Core.VariationTypeGenus

namespace FormalField.Core

universe u v

structure OrderedReadoutSystem where
  Carrier : Type u
  Output : Type v
  leq : Carrier → Carrier → Prop
  readout : Carrier → Output

def OrderReflexive (S : OrderedReadoutSystem) : Prop :=
  ∀ a, S.leq a a

def OrderTransitive (S : OrderedReadoutSystem) : Prop :=
  ∀ {a b c}, S.leq a b → S.leq b c → S.leq a c

def OrderAntisymmetric (S : OrderedReadoutSystem) : Prop :=
  ∀ {a b}, S.leq a b → S.leq b a → a = b

def OrderValid (S : OrderedReadoutSystem) : Prop :=
  OrderReflexive S ∧ OrderTransitive S ∧ OrderAntisymmetric S

def StatementFrom (S : OrderedReadoutSystem) (c : S.Carrier) (y : S.Output) : Prop :=
  S.readout c = y

def OrderedStatement (S : OrderedReadoutSystem) (c : S.Carrier) (y : S.Output) : Prop :=
  OrderValid S ∧ StatementFrom S c y

def ClarifiedStatement (S : OrderedReadoutSystem) (c : S.Carrier) (y : S.Output) : Prop :=
  OrderValid S ∧ StatementFrom S c y

theorem order_valid_reflexive (S : OrderedReadoutSystem) :
    OrderValid S → OrderReflexive S := by
  intro h
  exact h.1

theorem order_valid_transitive (S : OrderedReadoutSystem) :
    OrderValid S → OrderTransitive S := by
  intro h
  exact h.2.1

theorem order_valid_antisymmetric (S : OrderedReadoutSystem) :
    OrderValid S → OrderAntisymmetric S := by
  intro h
  exact h.2.2

theorem ordered_statement_has_order (S : OrderedReadoutSystem) (c : S.Carrier) (y : S.Output) :
    OrderedStatement S c y → OrderValid S := by
  intro h
  exact h.1

theorem ordered_statement_has_statement (S : OrderedReadoutSystem) (c : S.Carrier)
    (y : S.Output) :
    OrderedStatement S c y → StatementFrom S c y := by
  intro h
  exact h.2

theorem clarified_statement_has_order (S : OrderedReadoutSystem) (c : S.Carrier)
    (y : S.Output) :
    ClarifiedStatement S c y → OrderValid S := by
  intro h
  exact h.1

theorem clarified_statement_has_statement (S : OrderedReadoutSystem) (c : S.Carrier)
    (y : S.Output) :
    ClarifiedStatement S c y → StatementFrom S c y := by
  intro h
  exact h.2

theorem clarified_implies_ordered (S : OrderedReadoutSystem) (c : S.Carrier) (y : S.Output) :
    ClarifiedStatement S c y → OrderedStatement S c y := by
  intro h
  exact h

structure ClosedStatementSystem where
  S : OrderedReadoutSystem
  order_valid : OrderValid S

theorem closed_statement_order_valid (X : ClosedStatementSystem) :
    OrderValid X.S := by
  exact X.order_valid

theorem closed_statement_from_readout (X : ClosedStatementSystem) (c : X.S.Carrier) :
    StatementFrom X.S c (X.S.readout c) := by
  rfl

theorem closed_ordered_statement_from_readout (X : ClosedStatementSystem) (c : X.S.Carrier) :
    OrderedStatement X.S c (X.S.readout c) := by
  exact ⟨X.order_valid, rfl⟩

theorem closed_clarified_statement_from_readout (X : ClosedStatementSystem) (c : X.S.Carrier) :
    ClarifiedStatement X.S c (X.S.readout c) := by
  exact ⟨X.order_valid, rfl⟩

end FormalField.Core
