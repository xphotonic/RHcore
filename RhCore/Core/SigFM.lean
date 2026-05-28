import RhCore.Core.Carrier
import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.Analysis.Calculus.Deriv.Basic

/-!
# SigFM — Signal Functional Module

Defines S(t) as the phase observable derived from H(t),
and the carrier functional q(t) = |S|² + β|S'|².

This is the bridge between the analytic carrier (Carrier.lean)
and the RH reduction chain.
-/

noncomputable section

namespace RhCore.SigFM

open RhCore.Core

/-- Phase signal: imaginary part of logarithmic derivative of H -/
def S (t : ℝ) : ℝ :=
  Complex.im (deriv H t / H t)

/-- Carrier functional: q(t) = |S(t)|² + β·|S'(t)|² -/
def q (β : ℝ) (t : ℝ) : ℝ :=
  S t ^ 2 + β * (deriv S t) ^ 2

/-- q is nonneg for any β ≥ 0 -/
lemma q_nonneg (β : ℝ) (hβ : 0 ≤ β) (t : ℝ) : 0 ≤ q β t := by
  unfold q
  have h1 : 0 ≤ S t ^ 2 := sq_nonneg _
  have h2 : 0 ≤ β * (deriv S t) ^ 2 := mul_nonneg hβ (sq_nonneg _)
  linarith

/-- No-collapse condition: q > 0 iff S and S' are not simultaneously zero -/
def nonCollapse (β : ℝ) (t : ℝ) : Prop :=
  0 < q β t

/-- Accumulation functional P(T) = ∫₀ᵀ |S|²/(|S'| + ε) dt
    Defined as a pointwise integrand for now -/
def pIntegrand (ε : ℝ) (t : ℝ) : ℝ :=
  S t ^ 2 / (|deriv S t| + ε)

/-- pIntegrand is nonneg for ε > 0 -/
lemma pIntegrand_nonneg (ε : ℝ) (hε : 0 < ε) (t : ℝ) : 0 ≤ pIntegrand ε t := by
  unfold pIntegrand
  apply div_nonneg (sq_nonneg _)
  linarith [abs_nonneg (deriv S t)]

end RhCore.SigFM

end
