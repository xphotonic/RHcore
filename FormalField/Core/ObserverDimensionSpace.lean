import FormalField.Core.StructuralRecords
import FormalField.Core.VerificationPipeline
import FormalField.Core.FieldPassageFlow

namespace FormalField.Core

universe u v w

structure ObserverDimensionSystem where
  Carrier : Type u
  Observer : Type v
  Dimension : Type w
  metricReadable : Carrier → Prop
  measuredDim : Observer → Carrier → Dimension
  readoutDim : Observer → Carrier → Dimension

def SameDimension (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) : Prop :=
  S.measuredDim o c = S.readoutDim o c

def DimensionVerified (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) : Prop :=
  S.metricReadable c ∧ SameDimension S o c

def DimensionMismatch (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) : Prop :=
  S.measuredDim o c ≠ S.readoutDim o c

theorem dimension_verified_readable (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) :
    DimensionVerified S o c → S.metricReadable c := by
  intro h
  exact h.1

theorem dimension_verified_same_dimension (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) :
    DimensionVerified S o c → SameDimension S o c := by
  intro h
  exact h.2

theorem dimension_mismatch_not_verified (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) :
    DimensionMismatch S o c → ¬ DimensionVerified S o c := by
  intro hmismatch hverified
  exact hmismatch hverified.2

theorem same_dimension_not_mismatch (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) :
    SameDimension S o c → ¬ DimensionMismatch S o c := by
  intro hsame hmismatch
  exact hmismatch hsame

structure SpaceSystem where
  S : ObserverDimensionSystem
  observer : S.Observer
  carrier : S.Carrier
  dim_verified : DimensionVerified S observer carrier

theorem space_has_metric_readable_carrier (X : SpaceSystem) :
    X.S.metricReadable X.carrier := by
  exact X.dim_verified.1

theorem space_has_same_dimension (X : SpaceSystem) :
    SameDimension X.S X.observer X.carrier := by
  exact X.dim_verified.2

def ObserverReadoutAllowed (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) : Prop :=
  DimensionVerified S o c

theorem readout_allowed_implies_same_dimension (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) :
    ObserverReadoutAllowed S o c → SameDimension S o c := by
  intro h
  exact h.2

theorem readout_blocked_by_mismatch (S : ObserverDimensionSystem) (o : S.Observer) (c : S.Carrier) :
    DimensionMismatch S o c → ¬ ObserverReadoutAllowed S o c := by
  exact dimension_mismatch_not_verified S o c

end FormalField.Core
