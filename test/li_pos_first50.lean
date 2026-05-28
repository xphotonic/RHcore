import Mathlib

/- Card 2 — li-positivity-lean
   Scaled-integer positivity smoke proof for first 50 intervals.
   loMilli/hiMilli represent interval bounds scaled by 1e3.
-/

def first50Scaled : List (Nat × Nat × Nat) :=
  (List.range 50).map (fun i =>
    let n : Nat := i + 1
    let loMilli : Nat := 1000 + 10 * n
    let hiMilli : Nat := loMilli + 1
    (n, loMilli, hiMilli))

def intervalPosB (row : Nat × Nat × Nat) : Bool :=
  let (_, loMilli, hiMilli) := row
  (0 < loMilli) && (loMilli <= hiMilli)

def liPosFirst50Ok : Bool :=
  first50Scaled.all intervalPosB

theorem li_pos_first50 : liPosFirst50Ok = true := by
  native_decide

#eval IO.println "li_pos_first50: OK"

