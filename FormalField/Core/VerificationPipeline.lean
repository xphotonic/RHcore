import FormalField.Core.VerificationChain
import FormalField.Core.GateCostReadout
import FormalField.Core.ResultClassification
import FormalField.Core.NoStableResidual

namespace FormalField.Core

def PipelineVerified (V : VerificationChain) : Prop :=
  verification_complete V

def ClosedResultAllowed (V : VerificationChain) : Prop :=
  verification_complete V

def ClosedResultBlocked (V : VerificationChain) : Prop :=
  ¬ verification_complete V

theorem verified_allows_closed (V : VerificationChain) :
    verification_complete V → ClosedResultAllowed V := by
  intro h
  exact h

theorem blocked_if_not_verified (V : VerificationChain) :
    ¬ verification_complete V → ClosedResultBlocked V := by
  intro h
  exact h

theorem closed_requires_verification (V : VerificationChain) :
    ClosedResultAllowed V → verification_complete V := by
  intro h
  exact h

theorem complete_has_carrier (V : VerificationChain) :
    verification_complete V → V.carrierDefined := by
  intro h
  exact h.1

theorem complete_has_metric (V : VerificationChain) :
    verification_complete V → V.metricDefined := by
  intro h
  exact h.2.1

theorem complete_has_target (V : VerificationChain) :
    verification_complete V → V.targetDefined := by
  intro h
  exact h.2.2.1

theorem complete_has_representation (V : VerificationChain) :
    verification_complete V → V.representationDefined := by
  intro h
  exact h.2.2.2.1

theorem complete_has_residual (V : VerificationChain) :
    verification_complete V → V.residualDefined := by
  intro h
  exact h.2.2.2.2.1

theorem complete_has_gate (V : VerificationChain) :
    verification_complete V → V.gateDefined := by
  intro h
  exact h.2.2.2.2.2.1

theorem complete_has_cost_nonnegative (V : VerificationChain) :
    verification_complete V → V.costNonnegative := by
  intro h
  exact h.2.2.2.2.2.2.1

theorem complete_has_threshold (V : VerificationChain) :
    verification_complete V → V.thresholdDecidable := by
  intro h
  exact h.2.2.2.2.2.2.2.1

theorem complete_has_readout (V : VerificationChain) :
    verification_complete V → V.readoutAdmissible := by
  intro h
  exact h.2.2.2.2.2.2.2.2

end FormalField.Core
