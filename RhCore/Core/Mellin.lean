import Mathlib.Analysis.SpecialFunctions.Log.Basic
import Mathlib.MeasureTheory.Measure.Lebesgue.Basic
import Mathlib.MeasureTheory.Integral.Bochner

/-!
# Mellin Transform Interface

This file fixes the Mellin names used by the RH toolkit without pretending that
the hard substitution and differentiation lemmas are already formalized.

The currently proved lemmas are interface lemmas: downstream code can depend on
stable names, while future mathlib work can replace the `*Law` hypotheses with
analytic proofs from change of variables and dominated convergence.
-/

noncomputable section

open Complex MeasureTheory
open scoped Real

namespace RhCore.Core.Mellin

/-- Complex power kernel `x^(s-1)` on the positive real axis, zero off it. -/
def kernel (s : ℂ) (x : ℝ) : ℂ :=
  if 0 < x then Complex.exp ((s - 1) * (Real.log x : ℂ)) else 0

/-- Mellin transform over the positive real axis, represented as an integral on `ℝ`. -/
def mellin (f : ℝ → ℂ) (s : ℂ) : ℂ :=
  ∫ x : ℝ, kernel s x * f x

/-- Admissibility on a vertical strip. This starts with the integrability field
needed by every downstream Mellin identity; decay/regularity fields can be
added as the analytic proofs become concrete. -/
structure MellinAdmissible (f : ℝ → ℂ) (a b : ℝ) : Prop where
  int_ok :
    ∀ s : ℂ, a < s.re ∧ s.re < b →
      Integrable (fun x : ℝ => kernel s x * f x)

theorem integrable_of_admissible
    {f : ℝ → ℂ} {a b : ℝ} (hf : MellinAdmissible f a b)
    {s : ℂ} (hs : a < s.re ∧ s.re < b) :
    Integrable (fun x : ℝ => kernel s x * f x) :=
  hf.int_ok s hs

/-- Scaling law target for a fixed scale. Future analytic work should prove this
from substitution for admissible `f`; for now it is a precise gate. -/
def ScaleLaw (f : ℝ → ℂ) (α : ℝ) (s : ℂ) : Prop :=
  mellin (fun x => f (α * x)) s = Complex.exp (-(s * (Real.log α : ℂ))) * mellin f s

theorem mellin_scale_of_law
    {f : ℝ → ℂ} {α : ℝ} {s : ℂ}
    (h : ScaleLaw f α s) :
    mellin (fun x => f (α * x)) s =
      Complex.exp (-(s * (Real.log α : ℂ))) * mellin f s :=
  h

/-- Log-derivative law target: `M[x f'(x)](s) = -s M[f](s)`. -/
def DerivLogLaw (f f' : ℝ → ℂ) (s : ℂ) : Prop :=
  mellin (fun x => (x : ℂ) * f' x) s = -s * mellin f s

theorem mellin_deriv_log_of_law
    {f f' : ℝ → ℂ} {s : ℂ}
    (h : DerivLogLaw f f' s) :
    mellin (fun x => (x : ℂ) * f' x) s = -s * mellin f s :=
  h

/-- Multiplicative convolution placeholder. This is a named interface; the
measure-theoretic definition can be strengthened later. -/
def mulConv (f g : ℝ → ℂ) : ℝ → ℂ :=
  fun x => f x * g x

/-- Mellin-convolution law target for the current placeholder convolution. -/
def ConvLaw (f g : ℝ → ℂ) (s : ℂ) : Prop :=
  mellin (mulConv f g) s = mellin f s * mellin g s

theorem mellin_conv_of_law
    {f g : ℝ → ℂ} {s : ℂ}
    (h : ConvLaw f g s) :
    mellin (mulConv f g) s = mellin f s * mellin g s :=
  h

end RhCore.Core.Mellin
