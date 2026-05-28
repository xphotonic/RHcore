import Mathlib.Data.Complex.Basic
import Mathlib.Algebra.BigOperators.Fin
import RhCore.Core.Zeta
import RhCore.Li.Interval

/-!
# Li/Keiper Zero-Sum Scaffold

This file records the Lean-facing shape of the classical zero-sum formula

`lambda_n = sum_rho (1 - (1 - 1/rho)^n)`.

The analytic content is intentionally isolated as a checkable bridge:
`LiZeroSumBridge`. Once Hadamard factorization, coefficient extraction, and
termwise convergence are formalized, that bridge can be supplied. Until then
the theorem below is a conditional packaging theorem, not a proof of Li's
criterion.
-/

noncomputable section

namespace RhCore.Li.ZeroSum

open Complex BigOperators

/-- Finite proxy for a multiset/list of nontrivial zeros counted with
    multiplicity. Infinite summability is a later analytic layer. -/
def zeroContribution (n : ℕ) (ρ : ℂ) : ℂ :=
  1 - (1 - 1 / ρ) ^ n

/-- Finite zero-sum approximation. -/
def finiteZeroSum (n : ℕ) (zeros : Finset ℂ) : ℂ :=
  ∑ ρ in zeros, zeroContribution n ρ

/-- The term for `n = 0` vanishes. This is the closed algebraic part of the
    coefficient formula. -/
@[simp] theorem zeroContribution_zero (ρ : ℂ) :
    zeroContribution 0 ρ = 0 := by
  simp [zeroContribution]

/-- If the zero list is empty, the finite zero sum is zero. -/
@[simp] theorem finiteZeroSum_empty (n : ℕ) :
    finiteZeroSum n (∅ : Finset ℂ) = 0 := by
  simp [finiteZeroSum]

/-- Abstract statement of the analytic bridge from Hadamard product and
    coefficient extraction to Li/Keiper zero sums. -/
def LiZeroSumBridge
    (lambda : ℕ → ℂ)
    (zeroSum : ℕ → ℂ) : Prop :=
  ∀ n : ℕ, 1 ≤ n → lambda n = zeroSum n

/-- Conditional Li/Keiper zero-sum theorem. The proof is immediate once the
    analytic bridge is supplied. -/
theorem li_keiper_zero_sum
    (lambda : ℕ → ℂ)
    (zeroSum : ℕ → ℂ)
    (hbridge : LiZeroSumBridge lambda zeroSum) :
    ∀ n : ℕ, 1 ≤ n → lambda n = zeroSum n := by
  exact hbridge

/-- Finite version useful for CI witnesses: if a finite zero list is the chosen
    approximation to the zero-sum layer, the Li coefficient model is exactly
    that finite sum. -/
theorem finite_li_model_eq_zero_sum
    (n : ℕ)
    (zeros : Finset ℂ)
    (lambdaFinite : ℕ → ℂ)
    (h : lambdaFinite n = finiteZeroSum n zeros) :
    lambdaFinite n = ∑ ρ in zeros, zeroContribution n ρ := by
  simpa [finiteZeroSum] using h

end RhCore.Li.ZeroSum

