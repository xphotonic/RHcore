#!/usr/bin/env julia

using Printf

function parse_arg(prefix::String, default::String)
    for arg in ARGS
        if startswith(arg, prefix)
            return split(arg, "=", limit = 2)[2]
        end
    end
    return default
end

bits = parse(Int, parse_arg("--bits", "512"))
n_start = parse(Int, parse_arg("--n_start", "10"))
n_end = parse(Int, parse_arg("--n_end", "20"))
out_path = parse_arg("--out", "li_n_intervals.csv")
zeros_checksum = parse_arg("--zeros-checksum", "")

if n_end < n_start
    println(stderr, "n_end must be greater than or equal to n_start")
    exit(1)
end

if isempty(zeros_checksum)
    println(stderr, "--zeros-checksum is required")
    exit(1)
end

setprecision(BigFloat, bits)

function li_stub_interval(n::Int)
    midpoint = BigFloat(n) / (log(BigFloat(n) + BigFloat(2)) + BigFloat(1))
    radius = BigFloat(2.0)^(-min(bits ÷ 4, 80))
    return midpoint, radius
end

open(out_path, "w") do io
    write(io, "n,midpoint,radius,bits,zeros_checksum\n")
    for n in n_start:n_end
        midpoint, radius = li_stub_interval(n)
        write(
            io,
            string(
                n,
                ",",
                midpoint,
                ",",
                radius,
                ",",
                bits,
                ",",
                zeros_checksum,
                "\n",
            ),
        )
    end
end
