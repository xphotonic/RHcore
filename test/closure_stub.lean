import Mathlib

/- Card 6 — proof-seal-smoke
   Minimal theorem that must compile and emit .olean.
   Provenance: if this builds, the Lean toolchain is intact. -/
theorem closure_stub : (1 : Nat) = 1 := by decide

def main (_args : List String) : IO UInt32 := do
  have _h : (1 : Nat) = 1 := closure_stub
  IO.println "closure_stub: OK"
  pure 0
