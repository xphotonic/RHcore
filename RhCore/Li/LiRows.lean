import RhCore.Li.Rows
import Mathlib.Tactic

namespace RhCore.Li

/-- Generated from `c:/Users/uu/Desktop/Qlogic/physics/lean/RhCore/repo/data/li_n_intervals.csv`. Re-run `tools/generate_li_rows.py` after edits. -/
def generatedRows : List LiRow := [
  { n := 10, mid := ((28685897879122257 : ℚ) / 10000000000000000 : ℚ), rad := ((8271806125530277 : ℚ) / 10000000000000000000000000000000000000000 : ℚ) },
  { n := 11, mid := ((975609756097561 : ℚ) / 312500000000000 : ℚ), rad := ((8271806125530277 : ℚ) / 10000000000000000000000000000000000000000 : ℚ) },
  { n := 12, mid := ((3368421052631579 : ℚ) / 1000000000000000 : ℚ), rad := ((8271806125530277 : ℚ) / 10000000000000000000000000000000000000000 : ℚ) }
]

/-- Total lookup is only intended for indices covered by the generated table. -/
def rowFor? (n : Nat) : Option LiRow :=
  generatedRows.find? (fun row => row.n = n)

/-- Midpoint lookup — returns 0 if index not in table. -/
def liMid (n : Nat) : ℝ :=
  match rowFor? n with
  | some row => row.mid
  | none     => 0

/-- Radius lookup — returns 0 if index not in table. -/
def liRad (n : Nat) : ℝ :=
  match rowFor? n with
  | some row => row.rad
  | none     => 0

/-- Positivity witness for row n=10: mid - rad = 2.868589787912225699999999173 > 0.
    Discharged by norm_num on exact rational arithmetic. -/
theorem rowPositive_10 :
    (0 : ℝ) <
      ((28685897879122257 : ℚ) / 10000000000000000 : ℚ) -
      ((8271806125530277 : ℚ) / 10000000000000000000000000000000000000000 : ℚ) := by
  norm_num

/-- Positivity witness for row n=11: mid - rad = 3.121951219512195199999999173 > 0.
    Discharged by norm_num on exact rational arithmetic. -/
theorem rowPositive_11 :
    (0 : ℝ) <
      ((975609756097561 : ℚ) / 312500000000000 : ℚ) -
      ((8271806125530277 : ℚ) / 10000000000000000000000000000000000000000 : ℚ) := by
  norm_num

/-- Positivity witness for row n=12: mid - rad = 3.368421052631578999999999173 > 0.
    Discharged by norm_num on exact rational arithmetic. -/
theorem rowPositive_12 :
    (0 : ℝ) <
      ((3368421052631579 : ℚ) / 1000000000000000 : ℚ) -
      ((8271806125530277 : ℚ) / 10000000000000000000000000000000000000000 : ℚ) := by
  norm_num

end RhCore.Li
