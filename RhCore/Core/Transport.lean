import RhCore.Core.Readout
import RhCore.Core.Symmetry

noncomputable section

namespace RhCore.Core

def fTransport (t : ℝ) : ℝ :=
  amplitudeSq t

lemma fTransport_nonneg (t : ℝ) :
    0 ≤ fTransport t := by
  unfold fTransport
  exact Complex.normSq_nonneg (H t)

lemma fTransport_even (t : ℝ) :
    fTransport (-t) = fTransport t := by
  unfold fTransport
  simpa using amplitudeSq_even t

end RhCore.Core
