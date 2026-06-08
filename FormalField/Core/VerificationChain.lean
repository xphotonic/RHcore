namespace FormalField.Core

structure VerificationChain where
  carrierDefined : Prop
  metricDefined : Prop
  targetDefined : Prop
  representationDefined : Prop
  residualDefined : Prop
  gateDefined : Prop
  costNonnegative : Prop
  thresholdDecidable : Prop
  readoutAdmissible : Prop

def verification_complete (V : VerificationChain) : Prop :=
  V.carrierDefined ∧
    V.metricDefined ∧
    V.targetDefined ∧
    V.representationDefined ∧
    V.residualDefined ∧
    V.gateDefined ∧
    V.costNonnegative ∧
    V.thresholdDecidable ∧
    V.readoutAdmissible

end FormalField.Core
