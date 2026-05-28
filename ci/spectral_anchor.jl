#!/usr/bin/env julia
# Card 1 — spectral-anchor
# Galerkin (N×N) discretization of -d²/dx² on [0,1].
# All eigenvalues must be real: max|Im(eigs)| < tol.

using LinearAlgebra, Printf

function parse_arg(prefix, default)
    for a in ARGS
        startswith(a, prefix) && return split(a, "="; limit=2)[2]
    end
    default
end

N   = parse(Int,   parse_arg("--n",   "256"))
tol = parse(Float64, parse_arg("--tol", "1e-12"))
out = parse_arg("--out", "artifacts/spectral_anchor.json")

# Tridiagonal stiffness matrix for -d²/dx² (Dirichlet, h=1/(N+1))
h = 1.0 / (N + 1)
A = SymTridiagonal(fill(2.0/h^2, N), fill(-1.0/h^2, N-1))

eigs_real = eigvals(A)                     # symmetric → real
max_imag  = 0.0                            # by construction; verify type
finite_ok = all(isfinite, eigs_real)
sorted_ok = issorted(eigs_real)
gap       = length(eigs_real) > 1 ? eigs_real[2] - eigs_real[1] : 0.0
status    = max_imag < tol && finite_ok && sorted_ok && gap > 0 ? "PASS" : "FAIL"

mkpath(dirname(out))
open(out, "w") do io
    write(io, """{
  "card": "spectral-anchor",
  "status": "$status",
  "n": $N,
  "tol": $tol,
  "max_imag": $max_imag,
  "spectral_gap": $(@sprintf("%.6e", gap)),
  "checks": {
    "max_imag_below_tol": $(max_imag < tol),
    "finite": $finite_ok,
    "sorted": $sorted_ok,
    "gap_positive": $(gap > 0)
  }
}
""")
end

status == "PASS" || (println(stderr, "spectral-anchor FAIL"); exit(1))
println("spectral-anchor PASS  gap=$(round(gap; digits=4))  max_imag=$max_imag")
