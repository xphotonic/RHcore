import RhCore.Core.Transport
import RhCore.Core.SigFM
import RhCore.Core.ClosureOperator
import RhCore.Core.TransformChain
import RhCore.Core.EnergyCoercivity
import RhCore.Core.PrimeField
import RhCore.Core.CarrierGateCost
import RhCore.Core.HeatTraceClosure
import RhCore.Core.ExplicitFormula
import RhCore.Core.SelbergClosure
import RhCore.Core.SpectralGap
import RhCore.Core.ExplicitInequality
import RhCore.Core.AsymptoticGap
import RhCore.Core.SpectralGrowthConstant
import RhCore.Li
import RhCore.Spectral.RiemannOperatorExperiments
import RhCore.RH.Main
import RhCore.RH.CheckableHypothesis

noncomputable section

namespace RhCore.Core

lemma amplitudeSq_nonneg (t : ℝ) : 0 ≤ amplitudeSq t := by
  unfold amplitudeSq
  exact Complex.normSq_nonneg (H t)

/-!
## Closure Chain (partial)

Established:
  q_nonneg     : q β t ≥ 0  for β ≥ 0
  pIntegrand_nonneg : P integrand ≥ 0  for ε > 0

Open gate:
  nonCollapse  : q β t > 0  (requires H ≠ 0 and S, S' not simultaneously zero)
-/

/-- Structural closure: q ≥ 0 is established; strict positivity is the open gate -/
theorem carrier_nonneg (β : ℝ) (hβ : 0 ≤ β) (t : ℝ) :
    0 ≤ RhCore.SigFM.q β t :=
  RhCore.SigFM.q_nonneg β hβ t

end RhCore.Core
