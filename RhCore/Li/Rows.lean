import Mathlib.Data.Real.Basic
import RhCore.Li.Interval

namespace RhCore.Li

/-- A generated row from `li_n_intervals.csv`. -/
structure LiRow where
  n : Nat
  mid : ℝ
  rad : ℝ
deriving Inhabited

end RhCore.Li
