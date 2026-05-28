import RhCore.Core.Carrier
import Mathlib.Analysis.Calculus.Deriv.Basic
import Mathlib.Analysis.Complex.Basic

noncomputable section

namespace RhCore.Core

def theta' (t : ℝ) : ℝ :=
  Complex.im ((deriv H t) / (H t))

end RhCore.Core
