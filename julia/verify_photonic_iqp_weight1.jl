# Phase 19 Plan 03: VERIFY-03 weight-1 leg.
#
# Independently builds the weight-1 photonic IQP circuit in BosonSampling.jl
# using a plain dual-rail (2-modes-per-qubit) encoding -- BosonSampling.jl has
# no polarization/PBS component, so dual rail is the natural, idiomatic
# Julia-side equivalent of Perceval's polarization encoding (iqp_photonic_
# encoding.py's HWP/WP/PBS pipeline), NOT a mechanical port of it. Then diffs
# the resulting distribution against Python's `photonic_iqp_distribution`
# reference (results/v3_julia_verify/julia_reference/weight1_n2.csv, weight1_n3.csv).
#
# Run with:
#   julia --project=julia julia/verify_photonic_iqp_weight1.jl
#
# --- Dual-rail encoding convention -----------------------------------------
#
# n qubits -> 2n total modes. Qubit k (1-indexed) occupies mode pair
# (2k-1, 2k):
#   bit=0 <=> mode (2k-1) [upper / first-of-pair] holds the photon
#   bit=1 <=> mode  2k    [lower / second-of-pair] holds the photon
# Input state (all qubits start at bit=0, matching Python's |H>=|0> starting
# point before the Hadamard-equivalent prep layer): [1,0,1,0,...,1,0].
#
# Per-qubit gate stack, built from BosonSampling.jl's own primitives
# (confirmed from ~/.julia/packages/BosonSampling/*/src/circuits/
# circuit_elements.jl source, not assumed):
#   1. Hadamard-equivalent (state prep):    beam_splitter(1/sqrt(2))
#      -- already proven correct against the analytic 0.5/0.5 split in
#         hello_bosonsampling.jl (Phase 14).
#   2. Z-phase layer (weight-1 generator):  phase_shift(phi) on the LOWER
#      (bit=1) rail only, embedded as the 2x2 block diag(1, exp(i*phi)) --
#      BosonSampling.jl's own `phase_shift(phase) = [[1 0]; [0 exp(phase*im)]]`
#      is the library's single-mode phase primitive.
#   3. Hadamard-equivalent (conjugation):   beam_splitter(1/sqrt(2)) again.
#
# --- Deriving phi(theta), not assuming it ----------------------------------
#
# Let H = beam_splitter(1/sqrt(2)) = (1/sqrt(2)) * [[1,-1],[1,1]] (confirmed
# from source: beam_splitter(t) = [[t,-r];[r,t]], r=sqrt(1-t^2), t=r=1/sqrt(2)
# here). Let D = diag(1, exp(i*phi)) (phase_shift(phi) embedded on the lower
# rail). The full per-qubit unitary is U = H*D*H (Hadamard, then phase, then
# Hadamard -- order doesn't matter here since both Hadamards are identical).
#
# Multiplying out U*[1,0]^T (input = bit 0, photon in the upper rail):
#   amplitude(upper) = (1 - exp(i*phi)) / 2   =>  P(upper) = sin^2(phi/2)
#   amplitude(lower) = (1 + exp(i*phi)) / 2   =>  P(lower) = cos^2(phi/2)
#
# We want P(bit=0) = P(upper) = cos(theta)^2 (Python's closed-form marginal,
# docs: `expected_single_qubit_probs`). Setting sin^2(phi/2) = cos(theta)^2 =
# sin^2(pi/2 - theta) gives:
#
#   phi(theta) = pi - 2*theta
#
# (mod 2*pi; any solution of sin(phi/2)=+-cos(theta) works, this is the
# simplest one). Confirmed numerically in Task 1 below at theta=0.3, and
# by hand-computing the resulting n=2 product-form probabilities against
# results/v3_julia_verify/julia_reference/weight1_n2.csv before writing this script (e.g.
# P("00") = cos(0.3)^2 * cos(1.1)^2 ~= 0.187691, matching the CSV's
# 0.1877808915423398 to 4 significant figures by hand).
#
# --- Bitstring convention ---------------------------------------------------
#
# Qubit 1 (first pair, modes 1-2) is the MOST SIGNIFICANT (leftmost) bitstring
# character -- same convention independently verified in Plan 19-02 for the
# qubit-side (Yao.jl) circuit, and matching Python's own
# `basic_state_to_bitstring`/qubit-index-0-is-leftmost convention.

using BosonSampling
using DelimitedFiles

println("Julia: ", VERSION)
println("BosonSampling: ", pkgversion(BosonSampling))

# --- Per-qubit gate primitives ----------------------------------------------

hadamard_block() = beam_splitter(1 / sqrt(2))

function phase_block(theta::Float64)
    phi = pi - 2 * theta
    phase_shift(phi)
end

"""Per-qubit-pair unitary: Hadamard -> Z-phase(theta) -> Hadamard, as a 2x2
block."""
function qubit_pair_unitary(theta::Float64)
    H = hadamard_block()
    D = phase_block(theta)
    H * D * H
end

"""Full n-qubit 2n x 2n unitary: block-diagonal direct sum of each qubit
pair's independently-derived 2x2 unitary -- the 'independent build from
primitives' composition CONTEXT.md requires."""
function full_unitary(thetas::Vector{Float64})
    blocks = [qubit_pair_unitary(theta) for theta in thetas]
    reduce((a, b) -> cat(a, b; dims=(1, 2)), blocks)
end

# --- Bitstring <-> Fock-state helpers ---------------------------------------

"""bit=0 -> (1,0) [upper occupied], bit=1 -> (0,1) [lower occupied]."""
bit_to_pair_occupation(bit::Int) = bit == 0 ? (1, 0) : (0, 1)

function bitstring_to_mode_occupation(bitstring::String)
    occ = Int[]
    for c in bitstring
        b = c == '0' ? 0 : 1
        (u, l) = bit_to_pair_occupation(b)
        push!(occ, u)
        push!(occ, l)
    end
    ModeOccupation(occ)
end

"""Qubit 1 = MSB (leftmost char) -- matches Plan 19-02 / Python convention."""
function int_to_bitstring(i::Int, n::Int)
    join([string((i >> (n - k)) & 1) for k in 1:n])
end

function all_zero_input(n::Int)
    occ = Int[]
    for k in 1:n
        push!(occ, 1)
        push!(occ, 0)
    end
    Input{Bosonic}(ModeOccupation(occ))
end

# =============================================================================
# Task 1: n=1 convention check against the known closed-form marginal.
# =============================================================================

println("\n--- Task 1: n=1 dual-rail weight-1 encoding convention check ---")

theta1 = 0.3
U1 = full_unitary([theta1])
interf1 = UserDefinedInterferometer(U1)
input1 = Input{Bosonic}(ModeOccupation([1, 0]))

ev_bit0 = Event(input1, FockDetection(ModeOccupation([1, 0])), interf1)
p_bit0 = compute_probability!(ev_bit0)

ev_bit1 = Event(input1, FockDetection(ModeOccupation([0, 1])), interf1)
p_bit1 = compute_probability!(ev_bit1)

expected_p0 = cos(theta1)^2
expected_p1 = sin(theta1)^2

println("theta=$theta1: p(bit=0)=$p_bit0 (expected cos^2(theta)=$expected_p0)")
println("theta=$theta1: p(bit=1)=$p_bit1 (expected sin^2(theta)=$expected_p1)")

@assert isapprox(p_bit0, expected_p0; atol=1e-10) "n=1 p(bit=0) mismatch"
@assert isapprox(p_bit1, expected_p1; atol=1e-10) "n=1 p(bit=1) mismatch"
@assert isapprox(p_bit0 + p_bit1, 1.0; atol=1e-10) "n=1 probabilities do not normalize"

println("PASS: n=1 dual-rail weight-1 encoding matches closed-form cos^2(theta)/sin^2(theta) marginal")

# =============================================================================
# Task 2: n=2/n=3 cross-check against the Python reference.
# =============================================================================

println("\n--- Task 2: n=2/n=3 cross-check against Python reference ---")

function compute_weight1_distribution(n::Int, thetas::Vector{Float64})
    @assert length(thetas) == n
    U = full_unitary(thetas)
    interf = UserDefinedInterferometer(U)
    input_state = all_zero_input(n)

    dist = Dict{String,Float64}()
    for i in 0:(2^n-1)
        bitstring = int_to_bitstring(i, n)
        out_occ = bitstring_to_mode_occupation(bitstring)
        ev = Event(input_state, FockDetection(out_occ), interf)
        p = compute_probability!(ev)
        dist[bitstring] = p
    end
    dist
end

function read_reference_csv(path::String)
    dist = Dict{String,Float64}()
    open(path) do io
        for line in eachline(io)
            stripped = strip(line)
            isempty(stripped) && continue
            startswith(stripped, "#") && continue
            stripped == "bitstring,probability" && continue
            parts = split(stripped, ",")
            dist[String(parts[1])] = parse(Float64, parts[2])
        end
    end
    dist
end

function total_variation_distance(dist_a::Dict{String,Float64}, dist_b::Dict{String,Float64})
    ks = union(keys(dist_a), keys(dist_b))
    s = 0.0
    for k in ks
        s += abs(get(dist_a, k, 0.0) - get(dist_b, k, 0.0))
    end
    0.5 * s
end

TVD_TOLERANCE = 1e-6

cases = [
    (n=2, thetas=[0.3, 1.1], ref_path="results/v3_julia_verify/julia_reference/weight1_n2.csv"),
    (n=3, thetas=[0.3, 1.1, 0.75], ref_path="results/v3_julia_verify/julia_reference/weight1_n3.csv"),
]

results = []
for c in cases
    dist = compute_weight1_distribution(c.n, c.thetas)
    total = sum(values(dist))
    @assert isapprox(total, 1.0; atol=1e-9) "n=$(c.n) Julia distribution does not normalize to 1 (got $total)"

    ref_dist = read_reference_csv(c.ref_path)
    tvd = total_variation_distance(dist, ref_dist)
    println("n=$(c.n) (thetas=$(c.thetas)): TVD=$tvd")
    push!(results, (n=c.n, thetas=c.thetas, tvd=tvd, julia_dist=dist, ref_dist=ref_dist, ref_path=c.ref_path))
end

all_pass = all(r.tvd <= TVD_TOLERANCE for r in results)

if all_pass
    for r in results
        @assert r.tvd <= TVD_TOLERANCE "n=$(r.n) TVD $(r.tvd) exceeds tolerance $TVD_TOLERANCE"
    end
    println("\nPASS: VERIFY-03 weight-1 leg -- BosonSampling.jl independently reproduces the Python reference within TVD <= $TVD_TOLERANCE at n=2 and n=3")
else
    println("\nDISAGREEMENT: one or more TVDs exceed $TVD_TOLERANCE -- see results/v3_julia_verify/phase19_verify03_weight1_results.md for details")
end

# --- Write results/v3_julia_verify/phase19_verify03_weight1_results.md ----------------------

verdict = all_pass ? "GO" : "PARTIAL-GO (documented disagreement, see below)"

open("results/v3_julia_verify/phase19_verify03_weight1_results.md", "w") do io
    println(io, "# Phase 19 Plan 03: VERIFY-03 Weight-1 Leg Results")
    println(io)
    println(io, "## Methodology")
    println(io)
    println(io, "An independent BosonSampling.jl dual-rail (2-modes-per-qubit) circuit for the")
    println(io, "weight-1 photonic IQP generator family was built from BosonSampling.jl's own")
    println(io, "primitives (`beam_splitter`, `phase_shift`, `UserDefinedInterferometer`) --")
    println(io, "not a port of Perceval's HWP/WP/PBS polarization circuit (`iqp_photonic_encoding.py`).")
    println(io)
    println(io, "Encoding: qubit k (1-indexed) occupies modes `(2k-1, 2k)`; bit=0 <=> upper mode")
    println(io, "occupied, bit=1 <=> lower mode occupied. Per-qubit gate stack: Hadamard-equivalent")
    println(io, "(`beam_splitter(1/sqrt(2))`) -> Z-phase (`phase_shift(pi - 2*theta)` on the lower")
    println(io, "rail) -> Hadamard-equivalent conjugation. The phase parameter `phi = pi - 2*theta`")
    println(io, "was algebraically derived (not assumed) from `H*D*H` acting on the bit=0 input,")
    println(io, "requiring `P(bit=0) = cos(theta)^2` to match Python's closed-form marginal -- see")
    println(io, "the header comment in `julia/verify_photonic_iqp_weight1.jl` for the full derivation.")
    println(io)
    println(io, "The n=1 convention check (Task 1) verifies this construction directly against the")
    println(io, "known closed-form single-qubit marginal `P(bit=0)=cos(theta)^2, P(bit=1)=sin(theta)^2`")
    println(io, "at theta=0.3, before trusting the full n=2/n=3 comparison.")
    println(io)
    println(io, "The n=2/n=3 distributions are computed by enumerating all `2^n` valid")
    println(io, "computational-basis outcomes (each qubit pair carries exactly 1 photon) via")
    println(io, "`compute_probability!` per outcome, and diffed by total variation distance against")
    println(io, "Python's `photonic_iqp_distribution` reference (`results/v3_julia_verify/julia_reference/weight1_n2.csv`,")
    println(io, "`weight1_n3.csv`, generated in Plan 19-01), using the identical theta values")
    println(io, "(`n=2: thetas=[0.3, 1.1]`, `n=3: thetas=[0.3, 1.1, 0.75]`).")
    println(io)
    println(io, "## Results")
    println(io)
    println(io, "| n | thetas | TVD | Tolerance | Status |")
    println(io, "|---|--------|-----|-----------|--------|")
    for r in results
        status = r.tvd <= TVD_TOLERANCE ? "PASS" : "FAIL"
        println(io, "| $(r.n) | $(r.thetas) | $(r.tvd) | <= $TVD_TOLERANCE | $status |")
    end
    println(io)
    println(io, "n=1 convention check: p(bit=0)=$p_bit0 (expected $expected_p0), ")
    println(io, "p(bit=1)=$p_bit1 (expected $expected_p1), both within atol=1e-10. PASS.")
    println(io)
    println(io, "## Verdict")
    println(io)
    println(io, "**VERIFY-03 weight-1 leg: $verdict**")
    println(io)
    if all_pass
        println(io, "BosonSampling.jl's independently-built dual-rail weight-1 circuit reproduces")
        println(io, "the Python/Perceval reference distribution within TVD <= $TVD_TOLERANCE at both")
        println(io, "n=2 and n=3, confirming cross-implementation agreement on the weight-1 photonic")
        println(io, "IQP distribution. This satisfies VERIFY-03's weight-1 leg independent of Plan")
        println(io, "19-04's weight-2 (Knill-CZ) leg.")
    else
        println(io, "One or more n values exceeded the TVD <= $TVD_TOLERANCE tolerance. See the")
        println(io, "per-n TVD values above; this disagreement is reported honestly rather than")
        println(io, "forced to pass, per this project's established honesty norm (CONTEXT.md's")
        println(io, "disagreement-handling rule).")
    end
end

println("\nWrote results/v3_julia_verify/phase19_verify03_weight1_results.md")

# CORR-11 (2026-09-05): the diagnostic report above and the results file
# are always written first, but a DISAGREEMENT/PARTIAL-GO here previously
# still reached normal script termination -- a command runner would see
# exit status 0 despite a failed comparison. Exit nonzero now so CI-style
# invocation can actually detect this.
if !all_pass
    exit(1)
end
