import FormalField.Numeric.IntervalRecord

namespace FormalField.Verified

open FormalField.Numeric

structure ArtifactManifest where
  artifactId : String
  sourcePath : String
  createdAt : String

structure CertifiedWitness where
  status : WitnessStatus
  interval : IntervalRecord
  manifest : ArtifactManifest
  notes : List String

structure GeneratedTable where
  tableId : String
  rowCount : Nat
  manifest : ArtifactManifest
  witnessCount : Nat

end FormalField.Verified
