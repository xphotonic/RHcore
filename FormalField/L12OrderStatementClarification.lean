import FormalField.Core.OrderStatementClarification

namespace FormalField

open FormalField.Core

theorem order_statement_law (X : ClosedStatementSystem) (c : X.S.Carrier) :
    OrderedStatement X.S c (X.S.readout c) := by
  exact closed_ordered_statement_from_readout X c

theorem clarification_statement_law (X : ClosedStatementSystem) (c : X.S.Carrier) :
    ClarifiedStatement X.S c (X.S.readout c) := by
  exact closed_clarified_statement_from_readout X c

theorem clarification_implies_ordered_law (S : OrderedReadoutSystem) (c : S.Carrier) (y : S.Output) :
    ClarifiedStatement S c y → OrderedStatement S c y := by
  exact clarified_implies_ordered S c y

end FormalField
