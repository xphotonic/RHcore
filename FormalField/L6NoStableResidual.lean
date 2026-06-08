import FormalField.Core.NoStableResidual

noncomputable section

namespace FormalField

open FormalField.Core

theorem no_stable_residual_law (S : NoStableResidualSystem) (c : S.P.C) :
    StableState S.sys c → ResidualZero S.P c := by
  exact stable_state_residual_zero S c

end FormalField
