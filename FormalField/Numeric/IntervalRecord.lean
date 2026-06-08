namespace FormalField.Numeric

structure IntervalRecord where
  mid : String
  rad : String
  precisionBits : Nat

inductive WitnessStatus where
  | «pass»
  | undefined
  | «fail»
  | witnessOnly

end FormalField.Numeric
