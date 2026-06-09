import RhCore.Spectral.GeneratedEigs

/-!
# Bridge from Generated Eigen Rows to Li Positivity Gates

The current signed artifact contains generated rows for `n = 10, 11, 12`.
This module exposes those certified lower-endpoint positivity facts under
stable Li-facing names. A future `n = 1..50` artifact should extend this file
mechanically rather than weakening these statements.
-/

namespace RhCore.Li.GeneratedEigsBridge

open RhCore.Spectral.GeneratedEigs

/-- Current generated artifact has three certified rows. -/
def generatedRowCount : Nat :=
  rows.length

theorem generatedRowCount_eq : generatedRowCount = 3 := by
  native_decide

/-- Current signed generated row `n = 10` has positive lower endpoint. -/
theorem lowerPositive_n10 : (0 : ℝ) <
    ((7171472409516259 : ℚ) / 2500000000000000 : ℚ) -
    ((1 : ℚ) / 1000000000000 : ℚ) :=
  lowerPositive_10

/-- Current signed generated row `n = 11` has positive lower endpoint. -/
theorem lowerPositive_n11 : (0 : ℝ) <
    ((7805469288332911 : ℚ) / 2500000000000000 : ℚ) -
    ((1 : ℚ) / 1000000000000 : ℚ) :=
  lowerPositive_11

/-- Current signed generated row `n = 12` has positive lower endpoint. -/
theorem lowerPositive_n12 : (0 : ℝ) <
    ((1683647914993237 : ℚ) / 500000000000000 : ℚ) -
    ((1 : ℚ) / 1000000000000 : ℚ) :=
  lowerPositive_12

/-- Gate for the planned first-50 certificate: exact length plus positivity of
every generated lower endpoint. This is intentionally a proposition, not a
theorem, until the signed artifact actually contains 50 rows. -/
def First50CertificateReady : Prop :=
  rows.length = 50 ∧ ∀ row ∈ rows, 0 < lowerEndpoint row

end RhCore.Li.GeneratedEigsBridge

