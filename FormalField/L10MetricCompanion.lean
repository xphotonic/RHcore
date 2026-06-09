import FormalField.Core.MetricCompanion

namespace FormalField

open FormalField.Core

theorem metric_companion_readout_law (S : ClosedCompanionSystem) (c : S.M.Carrier) :
    S.M.readout (S.M.companion c) = S.M.readout c := by
  exact closed_companion_preserves_readout S c

theorem metric_companion_generated_law (S : ClosedCompanionSystem) (c : S.M.Carrier) :
    CompanionGenerated S.M (S.M.companion c) := by
  exact closed_companion_generated S c

end FormalField
