import Mathlib.Data.Real.Basic
import RhCore.Li.Interval
import RhCore.Li.Rows
import RhCore.Li.LiRows

/-!
# Certified — Proof-Carrying Li Interval Bounds

Every `CertifiedBound` bundles:
  - the interval (mid, rad) as exact rationals
  - metadata (name, checksum, source)
  - a proof term `pf : liInInterval n mid rad`

No external leancert dependency — the proof object IS the certificate.
Serialization is handled by the CI layer (gate_simulator + validate_li_artifact).
-/

namespace RhCore.Li

-- ════════════════════════════════════════════
-- § 1  Certificate metadata
-- ════════════════════════════════════════════

/-- Auditable metadata attached to every certified bound. -/
structure CertMeta where
  name           : String
  zeros_checksum : String := ""
  payload        : Array (String × String) := #[]
deriving Repr, Inhabited

-- ════════════════════════════════════════════
-- § 2  Core certificate structure
-- ════════════════════════════════════════════

/-- A machine-checkable interval claim bundled with its Lean proof. -/
structure CertifiedBound where
  n    : Nat
  mid  : ℝ
  rad  : ℝ
  meta : CertMeta
  pf   : liInInterval n mid rad

-- ════════════════════════════════════════════
-- § 3  Proof construction helpers
-- ════════════════════════════════════════════

/-- Turn lower/upper side conditions into interval membership. -/
theorem intervalOfBounds
    {n : Nat} {mid rad : ℝ}
    (hL : mid - rad ≤ liTrue n)
    (hU : liTrue n ≤ mid + rad) :
    liInInterval n mid rad :=
  ⟨hL, hU⟩

/-- Interval membership implies positivity when lower bound > 0. -/
theorem liPositive_of_interval
    {n : Nat} {mid rad : ℝ}
    (hpos : 0 < mid - rad)
    (hmem : liInInterval n mid rad) :
    0 < liTrue n := by
  unfold liInInterval inInterval at hmem
  exact lt_of_lt_of_le hpos hmem.1

-- ════════════════════════════════════════════
-- § 5  Public certification API
-- ════════════════════════════════════════════

/-- Certify a generated row when the caller supplies the interval proof.
    CI should generate these proof terms from the audited numeric artifact. -/
def certifyRow
    (n : Nat)
    (hL : liMid n - liRad n ≤ liTrue n)
    (hU : liTrue n ≤ liMid n + liRad n)
    (checksum : String := "") : CertifiedBound :=
  { n    := n
    mid  := liMid n
    rad  := liRad n
    meta := { name           := s!"li_row_{n}"
              zeros_checksum := checksum
              payload        := #[] }
    pf   := intervalOfBounds hL hU }

/-- Certify an arbitrary interval when the caller supplies the proofs directly. -/
def certifyCustom
    (n : Nat) (mid rad : ℝ)
    (hL : mid - rad ≤ liTrue n)
    (hU : liTrue n ≤ mid + rad)
    (name : String := s!"li_custom_{n}") : CertifiedBound :=
  { n    := n
    mid  := mid
    rad  := rad
    meta := { name := name }
    pf   := intervalOfBounds hL hU }

-- ════════════════════════════════════════════
-- § 6  Positivity certificates for all rows
-- ════════════════════════════════════════════

/-- A row certifies positivity if its lower bound is strictly positive. -/
def rowCertifiesPositive (row : LiRow) : Prop :=
  0 < (row.mid : ℝ) - row.rad

/-- All generated rows certify positivity (decidable check). -/
noncomputable def allRowsPositive : Bool :=
  generatedRows.all (fun row => row.mid - row.rad > 0)

/-- If allRowsPositive = true and bounds hold, then liTrue n > 0 for all table rows. -/
theorem liTrue_pos_of_row
    (n : Nat) (row : LiRow)
    (hrow : rowFor? n = some row)
    (hpos : 0 < (row.mid : ℝ) - row.rad)
    (hL : liMid n - liRad n ≤ liTrue n) :
    0 < liTrue n := by
  have hmid : liMid n = row.mid := by simp [liMid, hrow]
  have hrad : liRad n = row.rad := by simp [liRad, hrow]
  rw [hmid, hrad] at hL
  exact lt_of_lt_of_le hpos hL

end RhCore.Li
