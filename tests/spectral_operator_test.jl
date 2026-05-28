#!/usr/bin/env julia

using LinearAlgebra
using Printf

function parse_arg(prefix::String, default::String)
    for arg in ARGS
        if startswith(arg, prefix)
            return split(arg, "=", limit = 2)[2]
        end
    end
    return default
end

function bool_json(value::Bool)
    return value ? "true" : "false"
end

out_path = parse_arg("--out", "operator_eigs.json")

A = Symmetric([
    2.0 -1.0  0.0  0.0;
   -1.0  2.0 -1.0  0.0;
    0.0 -1.0  2.0 -1.0;
    0.0  0.0 -1.0  2.0;
])

eigs = eigvals(A)
sorted_ok = issorted(eigs)
finite_ok = all(isfinite, eigs)
nonnegative_ok = minimum(eigs) >= -1e-12
gap = length(eigs) > 1 ? eigs[2] - eigs[1] : 0.0
status = sorted_ok && finite_ok && nonnegative_ok && gap > 0 ? "PASS" : "FAIL"

open(out_path, "w") do io
    eig_text = join([@sprintf("%.12f", value) for value in eigs], ", ")
    write(
        io,
        "{\n" *
        "  \"layer\": \"L1\",\n" *
        "  \"status\": \"$status\",\n" *
        "  \"matrix_size\": $(size(A, 1)),\n" *
        "  \"spectral_gap\": $(@sprintf("%.12f", gap)),\n" *
        "  \"checks\": {\n" *
        "    \"finite\": $(bool_json(finite_ok)),\n" *
        "    \"sorted\": $(bool_json(sorted_ok)),\n" *
        "    \"nonnegative_ground\": $(bool_json(nonnegative_ok))\n" *
        "  },\n" *
        "  \"eigenvalues\": [$eig_text]\n" *
        "}\n",
    )
end

if status != "PASS"
    println(stderr, "L1 spectral operator test failed")
    exit(1)
end
