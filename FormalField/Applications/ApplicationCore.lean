import FormalField.Core.TerminalStructuralClosure
import FormalField.Core.DependencyNoCircularClosure
import FormalField.Core.AssumptionConstraintClosure
import FormalField.Core.VerificationPipeline
import FormalField.Core.ResultClassification

namespace FormalField
namespace Applications

inductive ApplicationDomain where
  | rh
  | toe
  | rsa
  | physics
deriving DecidableEq, Repr

universe u

structure ApplicationSpec where
  Claim : Type u
  carrierReady : Claim → Prop
  metricReady : Claim → Prop
  residualReady : Claim → Prop
  gateReady : Claim → Prop
  costReady : Claim → Prop
  verificationReady : Claim → Prop
  nonCircularReady : Claim → Prop
  terminal : FormalField.Core.TerminalClosureSystem

def ApplicationStructurallyReady (A : ApplicationSpec) (c : A.Claim) : Prop :=
  A.carrierReady c ∧
    A.metricReady c ∧
    A.residualReady c ∧
    A.gateReady c ∧
    A.costReady c ∧
    A.verificationReady c ∧
    A.nonCircularReady c

def ApplicationPending (A : ApplicationSpec) (c : A.Claim) : Prop :=
  ¬ ApplicationStructurallyReady A c

theorem application_ready_carrier (A : ApplicationSpec) (c : A.Claim) :
    ApplicationStructurallyReady A c → A.carrierReady c := by
  intro h
  exact h.1

theorem application_ready_metric (A : ApplicationSpec) (c : A.Claim) :
    ApplicationStructurallyReady A c → A.metricReady c := by
  intro h
  exact h.2.1

theorem application_ready_residual (A : ApplicationSpec) (c : A.Claim) :
    ApplicationStructurallyReady A c → A.residualReady c := by
  intro h
  exact h.2.2.1

theorem application_ready_gate (A : ApplicationSpec) (c : A.Claim) :
    ApplicationStructurallyReady A c → A.gateReady c := by
  intro h
  exact h.2.2.2.1

theorem application_ready_cost (A : ApplicationSpec) (c : A.Claim) :
    ApplicationStructurallyReady A c → A.costReady c := by
  intro h
  exact h.2.2.2.2.1

theorem application_ready_verification (A : ApplicationSpec) (c : A.Claim) :
    ApplicationStructurallyReady A c → A.verificationReady c := by
  intro h
  exact h.2.2.2.2.2.1

theorem application_ready_nonCircular (A : ApplicationSpec) (c : A.Claim) :
    ApplicationStructurallyReady A c → A.nonCircularReady c := by
  intro h
  exact h.2.2.2.2.2.2

end Applications
end FormalField
