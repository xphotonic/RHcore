import FormalField.Core.ObserverDimensionSpace

namespace FormalField

open FormalField.Core

theorem observer_dimension_space_law (X : SpaceSystem) :
    SameDimension X.S X.observer X.carrier := by
  exact space_has_same_dimension X

theorem readout_dimension_gate_law (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) :
    DimensionMismatch S o c → ¬ ObserverReadoutAllowed S o c := by
  exact readout_blocked_by_mismatch S o c

end FormalField
