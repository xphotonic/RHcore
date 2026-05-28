import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Tactic

/-!
# Heat Trace Closure Gate

This file formalizes the algebraic part of the certified heat-trace workflow:
from a heat-trace upper bound and a counting inequality, one gets the computable
lower bound used by the CI sweep.

The analytic burden is outside this file: proving the heat-trace upper bound,
the Weyl tail, and the spectral counting hypothesis belongs to the
numeric/analytic certification layer.
-/

noncomputable section

namespace RhCore.HeatTraceClosure

/-- The Markov/Chebyshev heat-trace conversion used by the certified numeric
    pipeline. Here `nMass` is the positive real mass corresponding to the
    counted eigenvalue index. -/
theorem lambda_lower_from_heat_trace
    {t nMass TrUp lambda : ℝ}
    (ht : 0 < t)
    (hn : 0 < nMass)
    (hTr : 0 < TrUp)
    (hcount : nMass * Real.exp (-t * lambda) ≤ TrUp) :
    -(Real.log (TrUp / nMass)) / t ≤ lambda := by
  have hExpLe : Real.exp (-t * lambda) ≤ TrUp / nMass := by
    rw [le_div_iff₀ hn]
    simpa [mul_comm] using hcount
  have hRatioPos : 0 < TrUp / nMass := div_pos hTr hn
  have hLogLe : -t * lambda ≤ Real.log (TrUp / nMass) := by
    rw [← Real.log_exp (-t * lambda)]
    exact Real.log_le_log (Real.exp_pos _) hExpLe
  have hDiv : (-t * lambda) / t ≤ Real.log (TrUp / nMass) / t :=
    (div_le_div_iff_of_pos_right ht).2 hLogLe
  have hEq : (-(t * lambda)) / t = -lambda := by
    field_simp [ne_of_gt ht]
    ring
  have hNeg : -lambda ≤ Real.log (TrUp / nMass) / t := by
    simpa [neg_mul, hEq] using hDiv
  have hFlip := neg_le_neg hNeg
  simpa [neg_div] using hFlip

/-- A named readout matching the CI formula. -/
def heatTraceLowerBound (t nMass TrUp : ℝ) : ℝ :=
  -(Real.log (TrUp / nMass)) / t

theorem heatTraceLowerBound_sound
    {t nMass TrUp lambda : ℝ}
    (ht : 0 < t)
    (hn : 0 < nMass)
    (hTr : 0 < TrUp)
    (hcount : nMass * Real.exp (-t * lambda) ≤ TrUp) :
    heatTraceLowerBound t nMass TrUp ≤ lambda := by
  exact lambda_lower_from_heat_trace ht hn hTr hcount

end RhCore.HeatTraceClosure
