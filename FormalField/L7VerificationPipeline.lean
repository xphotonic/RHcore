import FormalField.Core.VerificationPipeline

namespace FormalField

open FormalField.Core

theorem verification_pipeline_law (V : VerificationChain) :
    ClosedResultAllowed V → verification_complete V := by
  exact closed_requires_verification V

end FormalField
