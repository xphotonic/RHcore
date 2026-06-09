import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Topology.Basic

/-!
# Minimal Riemann Operator Interface

This is a reviewable interface, not a proof of the Hilbert--Polya program.
It packages the assumptions that later spectral lemmas may use: a Hilbert
carrier, a domain, a linear operator, symmetry on the domain, a self-adjointness
gate, and a hook for spectral transforms.
-/

noncomputable section

namespace RhCore.Spectral

universe u

/-- Minimal operator package for RH-style spectral experiments. -/
structure RiemannOperator where
  H : Type u
  [normedAddCommGroup : NormedAddCommGroup H]
  [innerProductSpace : InnerProductSpace ℂ H]
  [completeSpace : CompleteSpace H]
  D : Set H
  T : H →ₗ[ℂ] H
  ip : H → H → ℂ
  dom_dense : Dense D
  symmetric :
    ∀ {x y : H}, x ∈ D → y ∈ D →
      ip (T x) y = ip x (T y)
  selfAdjointReady : Prop
  spectral_map : (ℂ → ℂ) → Prop

namespace RiemannOperator

variable (R : RiemannOperator)

theorem symmetric_on_domain
    {x y : R.H} (hx : x ∈ R.D) (hy : y ∈ R.D) :
    R.ip (R.T x) y = R.ip x (R.T y) :=
  R.symmetric hx hy

/-- The self-adjointness gate is deliberately explicit: models must supply it. -/
def HasSelfAdjointGate : Prop :=
  R.selfAdjointReady

/-- A transform is accepted by the model exactly when its spectral hook accepts it. -/
def SupportsTransform (φ : ℂ → ℂ) : Prop :=
  R.spectral_map φ

theorem supportsTransform_iff (φ : ℂ → ℂ) :
    R.SupportsTransform φ ↔ R.spectral_map φ := by
  rfl

end RiemannOperator

end RhCore.Spectral
