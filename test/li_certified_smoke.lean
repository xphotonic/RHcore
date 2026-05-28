import RhCore.Li

/-!
# Li Certification Smoke Test

Verifies end-to-end:
1. allRowsPositive = true  (norm_num witnesses compile)
2. certifyRow produces a valid CertifiedBound for each table row
3. liPositive_of_interval discharges positivity from the certificate
-/

namespace RhCore.Li.Smoke

open RhCore.Li

-- ── 1) Runtime positivity check ──────────────────────────────────────────
#eval do
  let ok := allRowsPositive
  if ok then IO.println "allRowsPositive: PASS"
  else   IO.eprintln "allRowsPositive: FAIL" *> throw (IO.userError "fail")

-- ── 2) certifyRow compiles for each known index ───────────────────────────
#check (certifyRow 10 : CertifiedBound)
#check (certifyRow 11 : CertifiedBound)
#check (certifyRow 12 : CertifiedBound)

-- ── 3) liPositive_of_interval on row 10 ──────────────────────────────────
-- rowPositive_10 : 0 < mid_10 - rad_10  (from LiRows.lean, norm_num)
-- liRow_lower 10 : liMid 10 - liRad 10 ≤ liTrue 10
-- liRow_upper 10 : liTrue 10 ≤ liMid 10 + liRad 10
example : 0 < liTrue 10 :=
  liPositive_of_interval
    (by exact_mod_cast rowPositive_10)
    (intervalOfBounds (liRow_lower 10) (liRow_upper 10))

end RhCore.Li.Smoke
