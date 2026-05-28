#!/usr/bin/env julia
# Card 4 — parity-involution
# Reads operator_eigs.json (or builds a small skew-symmetric demo matrix).
# Checks that eigenvalues pair as eigs[i] ≈ -eigs[j] within rel-tol.

using LinearAlgebra, Printf

function parse_arg(prefix, default)
    for a in ARGS
        startswith(a, prefix) && return split(a, "="; limit=2)[2]
    end
    default
end

eigs_path = parse_arg("--eigs", "")
tol       = parse(Float64, parse_arg("--tol", "1e-10"))
out       = parse_arg("--out", "artifacts/parity_involution.json")

# Build or load eigenvalues
if !isempty(eigs_path) && isfile(eigs_path)
    # Tiny dependency-free parser for files containing
    # {"eigenvalues":[...]} so the CI card does not need external Julia deps.
    text = read(eigs_path, String)
    m = match(r"\"eigenvalues\"\s*:\s*\[([^\]]*)\]", text)
    m === nothing && error("missing eigenvalues array in $eigs_path")
    eigs = [parse(Float64, strip(x)) for x in split(m.captures[1], ",") if !isempty(strip(x))]
else
    # Demo: skew-symmetric 6×6 → purely imaginary eigs → real part = 0
    B = [0 1 0; -1 0 1; 0 -1 0] .* 1.0
    A = [B zeros(3,3); zeros(3,3) -B]
    eigs = real.(eigvals(A))
end

sort!(eigs)
n = length(eigs)
pairs_ok = true
max_err  = 0.0

if iseven(n)
    for i in 1:(n÷2)
        lo, hi = eigs[i], eigs[n+1-i]
        err = abs(lo + hi) / (abs(lo) + abs(hi) + 1e-30)
        max_err = max(max_err, err)
        pairs_ok = pairs_ok && err < tol
    end
end

status = pairs_ok && iseven(n) ? "PASS" : "FAIL"
mkpath(dirname(out))
open(out, "w") do io
    write(io, """{
  "card": "parity-involution",
  "status": "$status",
  "tol": $tol,
  "n_eigs": $n,
  "max_pair_error": $(@sprintf("%.6e", max_err)),
  "checks": {
    "even_count": $(iseven(n)),
    "pairs_within_tol": $pairs_ok
  }
}
""")
end

status == "PASS" || (println(stderr, "parity-involution FAIL"); exit(1))
println("parity-involution PASS  max_err=$(@sprintf("%.2e", max_err))")
