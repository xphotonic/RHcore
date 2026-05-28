import RhCore.Core.Carrier
import Mathlib.Tactic

noncomputable section

namespace RhCore.Core

lemma amplitudeSq_even (t : ℝ) :
    amplitudeSq (-t) = amplitudeSq t := by
  unfold amplitudeSq H
  simp [Complex.normSq]


end RhCore.Core
