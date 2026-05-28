import Mathlib.Data.Complex.Basic

/-!
# Carrier

H(t) is currently a placeholder: H(t) = 1 + it.

The correct carrier is H(t) = ξ(1/2 + it), derived in TransformChain.lean
via: Gaussian → Fourier → Poisson → Mellin → ξ.

Replacement is gated on Mathlib.NumberTheory.ZetaFunction availability.
-/

noncomputable section
open Complex

namespace RhCore.Core

/-- Placeholder carrier. Replace with ξ(1/2 + it) from TransformChain. -/
def H (t : ℝ) : ℂ :=
  (1 : ℂ) + (t : ℂ) * Complex.I

def amplitudeSq (t : ℝ) : ℝ :=
  Complex.normSq (H t)

end RhCore.Core
