import FormalField.Applications.ApplicationCore

namespace FormalField
namespace Applications

inductive RSAObligation where
  | logCarrier
  | reciprocalManifold
  | orthogonalProjection
  | thetaMellinFilter
  | localLyapunovClosure
  | basinEntryComplexity
  | hardVerification
deriving DecidableEq, Repr

structure RSAApplication where
  obligationReady : RSAObligation → Prop

def RSALocalReady (R : RSAApplication) : Prop :=
  R.obligationReady RSAObligation.logCarrier ∧
    R.obligationReady RSAObligation.reciprocalManifold ∧
    R.obligationReady RSAObligation.orthogonalProjection ∧
    R.obligationReady RSAObligation.localLyapunovClosure ∧
    R.obligationReady RSAObligation.hardVerification

def RSAComplexityOpen (R : RSAApplication) : Prop :=
  ¬ R.obligationReady RSAObligation.basinEntryComplexity

theorem rsa_local_ready_logCarrier (R : RSAApplication) :
    RSALocalReady R → R.obligationReady RSAObligation.logCarrier := by
  intro h
  exact h.1

theorem rsa_local_ready_reciprocalManifold (R : RSAApplication) :
    RSALocalReady R → R.obligationReady RSAObligation.reciprocalManifold := by
  intro h
  exact h.2.1

theorem rsa_local_ready_orthogonalProjection (R : RSAApplication) :
    RSALocalReady R → R.obligationReady RSAObligation.orthogonalProjection := by
  intro h
  exact h.2.2.1

theorem rsa_local_ready_localLyapunovClosure (R : RSAApplication) :
    RSALocalReady R → R.obligationReady RSAObligation.localLyapunovClosure := by
  intro h
  exact h.2.2.2.1

theorem rsa_local_ready_hardVerification (R : RSAApplication) :
    RSALocalReady R → R.obligationReady RSAObligation.hardVerification := by
  intro h
  exact h.2.2.2.2

-- The RSA application is a conditional basin-entry framework; global
-- complexity remains open.

end Applications
end FormalField
