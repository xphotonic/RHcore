import FormalField.Core.StructuralRecords
import FormalField.Core.ProcessValidity
import FormalField.Core.GateCostReadout
import FormalField.Core.MonotoneFieldPower

noncomputable section

namespace FormalField.Core

def StableState (sys : TransformationSystem) (c : sys.State) : Prop :=
  ∀ ⦃d⦄, sys.step c d → d = c

def ResidualZero (P : FormalProcess) (c : P.C) : Prop :=
  P.r c = 0

def NonzeroResidual (P : FormalProcess) (c : P.C) : Prop :=
  P.r c ≠ 0

def NoStableNonzeroResidual (sys : TransformationSystem) (P : FormalProcess) : Prop :=
  ∀ c, NonzeroResidual P c → ¬ StableState sys c

def StableImpliesResidualZero (sys : TransformationSystem) (P : FormalProcess) : Prop :=
  ∀ c, StableState sys c → ResidualZero P c

theorem no_stable_nonzero_to_stable_zero
    (sys : TransformationSystem) (P : FormalProcess) (c : P.C) :
    NoStableNonzeroResidual sys P →
      StableState sys c →
      ResidualZero P c := by
  intro hnostable hstable
  by_cases hres : P.r c = 0
  · exact hres
  · exfalso
    exact (hnostable c hres) hstable

theorem stable_zero_to_no_stable_nonzero
    (sys : TransformationSystem) (P : FormalProcess) (c : P.C) :
    StableImpliesResidualZero sys P →
      NonzeroResidual P c →
      ¬ StableState sys c := by
  intro hstablezero hnonzero hstable
  exact hnonzero (hstablezero c hstable)

structure NoStableResidualSystem where
  sys : TransformationSystem
  P : FormalProcess
  noStable : NoStableNonzeroResidual sys P

theorem stable_state_residual_zero (S : NoStableResidualSystem) (c : S.P.C) :
    StableState S.sys c → ResidualZero S.P c := by
  exact no_stable_nonzero_to_stable_zero S.sys S.P c S.noStable

theorem zero_cost_residual_zero_bridge (P : FormalProcess) (c : P.C) :
    P.strict_zero_cost_validity →
      P.Q c = 0 →
      ResidualZero P c := by
  intro hvalid hzero
  exact hvalid c hzero

end FormalField.Core
