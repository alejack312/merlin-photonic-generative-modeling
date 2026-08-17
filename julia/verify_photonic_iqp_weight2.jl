# Phase 19, Plan 04: VERIFY-03's weight-2 leg -- independent BosonSampling.jl
# cross-check of the locked-gate weight-2 photonic IQP distribution.
#
# ---------------------------------------------------------------------------
# LITERATURE SOURCE (Task 1) -- read directly, not extracted from Perceval
# ---------------------------------------------------------------------------
# E. Knill, "A Note on Linear Optics Gates by Post-Selection,"
# arXiv:quant-ph/0110144v2 (25 Oct 2001).
#
# Section III ("Conditional Phase Shifts") defines CS_theta: |ab> -> e^{i a b
# theta}|ab> on two "data" modes (a,b in {0,1} photons), realized with two
# ancilla ("helper") modes each prepared with exactly one photon, accepting
# only the output where exactly one photon survives in each ancilla mode
# (heralding, not post-selection on the data modes themselves). The paper
# states explicitly (Sec. III, first paragraph): "To realize the conditional
# sign flip between Q_{1,2} and Q_{3,4} [two dual-rail bosonic qubits], apply
# CS_180 degrees to modes 1 and 3" -- i.e. Knill's CS_theta only ever touches
# the logical-|1> rail of each dual-rail qubit; the logical-|0> rail is an
# untouched spectator. This is the exact mechanism this repo's own
# docs/iqp-photonic-encoding.md (Ingredient 2) describes for Perceval's
# heralded_cz, but sourced here independently from the original paper.
#
# Eq. 11 (p.5) gives the explicit closed-form solution for CS_180 (a CZ
# gate): a 4x4 REAL ORTHOGONAL matrix V_180, which the paper states "turns
# out to be unitary" -- meaning no additional ancilla modes beyond the two
# helper modes are needed (k=4 total modes: 2 data + 2 ancilla), matching
# Fig. 1's optical network (4 modes, 4 beamsplitters, 2 photon counters on
# the ancilla modes only). The paper reports success probability 2/27 for
# this matrix -- the SAME figure this repo independently measured directly
# from Perceval's `heralded_cz` catalog gate (heralded_cz_derisking.py,
# Phase 10), but V_180 below is transcribed from Knill's Eq. 11, never
# extracted from Perceval's own built circuit. This is what makes this an
# independent cross-check per 19-RESEARCH.md's explicitly flagged
# anti-pattern (extracting Perceval's `.compute_unitary()` and hardcoding
# the numbers would defeat the point).
#
# ---------------------------------------------------------------------------
# CONSTRUCTION (Task 2)
# ---------------------------------------------------------------------------
# This script builds the full n=2, weight-2-locked-gate photonic IQP circuit
# independently in BosonSampling.jl, using Knill's V_180 as the only
# ingredient sourced from outside this repo's own prior derivations:
#
#   6 modes, ordered [A0, A1, B0, B1, H1, H2]:
#     A0/A1 = qubit i's dual-rail pair (bit 0 -> A0 has the photon, bit 1 ->
#             A1 has the photon -- this script's own self-consistent
#             convention, chosen independently of Perceval's port labeling).
#     B0/B1 = qubit j's dual-rail pair, same convention.
#     H1/H2 = the two ancilla/herald modes from Knill's construction.
#
#   Stage 1 (state prep): a real Hadamard beamsplitter on (A0,A1) and
#   independently on (B0,B1), leaving H1/H2 untouched. This realizes H^{ox2}
#   on the two qubits (Perceval's HWP(pi/8) differs from a bare Hadamard only
#   by a global phase i per qubit -- unobservable in any measured
#   probability, confirmed already in docs/iqp-photonic-encoding.md's
#   Ingredient 1 -- so a bare real Hadamard is used directly here without
#   needing to reproduce Perceval's specific wave-plate parametrization).
#
#   Stage 2 (weight-1 correction, folded into the middle diagonal layer):
#   per the operator identity independently derived and already recorded in
#   this repo's docs/iqp-photonic-encoding.md (Ingredient 2, itself an
#   equation-level derivation, not a Perceval extraction):
#       exp(i*pi/4*Zi*Zj) = CZ . exp(i*pi/4*Zi) . exp(i*pi/4*Zj)   (up to
#       global phase), where Zi|bit=0> = +1, Zi|bit=0> = -1.
#   exp(i*pi/4*Zi) is realized as a per-mode phase: A0 (bit 0) gets
#   e^{+i*pi/4}, A1 (bit 1) gets e^{-i*pi/4}; same for B0/B1. thetas=[0,0]
#   externally (matching results/julia_reference/weight2_locked_n2.csv's
#   header), so this pi/4 correction is the ONLY diagonal-layer phase
#   present -- a pure weight-2 pair term at the locked angle pi/4.
#
#   Stage 3 (weight-2 gate): Knill's V_180 embedded into the 6-mode unitary,
#   acting on (A1, B1, H1, H2) -- the logical-|1> rails plus both ancillas
#   -- with A0/B0 left as untouched spectators (identity), matching Knill's
#   own Sec. III description of which modes CS_180 touches.
#
#   Stage 4 (conjugation/readout): the same Hadamard as Stage 1 (Hadamard is
#   self-inverse; this mirrors the qubit-side H-diagonal-H sandwich), then
#   photon-counting readout via BosonSampling.jl's Event/compute_probability!
#   (the same API already validated in julia/hello_bosonsampling.jl -- no
#   new, unverified BosonSampling.jl API surface is used in this script).
#
#   Herald accounting is done entirely by hand (BosonSampling.jl has no
#   Processor.add_herald equivalent, per 19-RESEARCH.md Open Question 3):
#   enumerate every way to distribute the 2 non-ancilla photons across the 4
#   data modes (10 combinations), call compute_probability! for each with
#   ancilla output fixed at [1,1], and classify each into either one of the
#   4 valid dual-rail bitstrings or "residual" (bunched/invalid data-mode
#   pattern despite herald success). herald_failure_prob = 1 - (sum over all
#   10 herald-success combinations). dist/residual are then renormalized by
#   dividing by (1 - herald_failure_prob), matching
#   photonic_weight2_iqp_distribution's own documented renormalization
#   contract (confirmed in julia/generate_reference.py's header comments,
#   19-01-SUMMARY.md).
#
# Order-of-application note: Stage 2 (correction) is applied AFTER Stage 3
# (CZ), i.e. composite = conjugation * correction * cz_embed * state_prep.
# Both correction and CZ are diagonal in the LOGICAL 2-qubit computational
# basis (Zi, Zj, and CZ=diag(1,1,1,-1) all commute), so the herald-
# conditioned logical action should not depend on this choice -- but the
# raw 6-mode matrix product is not literally diagonal-commuting at the full
# linear-optics level, so this is flagged explicitly as a design choice, not
# a proven irrelevant detail. If the measured TVD disagrees, swapping this
# order is the first thing to try (see results doc).
#
# Run: julia --project=julia julia/verify_photonic_iqp_weight2.jl

using BosonSampling
using LinearAlgebra

println("Julia: ", VERSION)
println("BosonSampling: ", pkgversion(BosonSampling))

# ---------------------------------------------------------------------------
# Task 1 artifact: Knill's CS_180 matrix, Eq. 11 of arXiv:quant-ph/0110144v2
# ---------------------------------------------------------------------------

function knill_cs180_matrix()
    s6 = sqrt(6.0)
    a = sqrt(3 + s6)
    b = sqrt(3 - s6)
    c = sqrt((3 + s6) / 2) / 3
    d = sqrt(1 / 6 - 1 / (3 * s6))
    V = [
        -1/3        -sqrt(2)/3   sqrt(2)/3    2/3;
         sqrt(2)/3  -1/3         -2/3         sqrt(2)/3;
        -a/3          b/3        -c            d;
        -b/3         -a/3        -d           -c
    ]
    return V
end

V180_paper = knill_cs180_matrix()

# NOTE on transpose convention (found during Task 2 debugging, documented
# honestly rather than silently absorbed): the paper defines its printed
# matrix via V_rs = u_sr (Sec. III, just before Eq. 9) -- i.e. Eq. 11's
# entries are the TRANSPOSE of the "output-row, input-column" convention
# BosonSampling.jl's UserDefinedInterferometer(U) expects (matching the
# convention already used successfully in julia/hello_bosonsampling.jl,
# where U's rows index output modes). Using Eq. 11's matrix AS PRINTED
# produced nonzero leakage into bunched outputs ((2,0)/(0,2) given a |1,1>
# input) that Knill's own Eq. 6 guarantees should be EXACTLY zero for a
# correctly-oriented V -- a clear, checkable tell (see results doc for the
# full diagnostic). Transposing resolves it: leakage drops to numerical
# zero (~1e-32) for all four of Eq. 6's zero-constraints, confirming this
# was a row/column convention mismatch, not a transcription error (the
# LaTeX source, fetched directly from arXiv's e-print endpoint, was
# checked character-for-character against Eq. 11 above and matches
# exactly). V180 (used from here on) is therefore V_180_paper transposed.
V180 = collect(transpose(V180_paper))

println()
println("=" ^ 70)
println("Task 1 sanity check: Knill Eq. 11 matrix, transcribed independently")
println("=" ^ 70)
println("V_180 as printed in the paper (Knill quant-ph/0110144, Eq. 11):")
display(V180_paper)
println()
println("V_180 as used here (transposed -- see note above):")
display(V180)
println()

unitarity_defect = maximum(abs.(V180' * V180 - I(4)))
println("Max |V'V - I| entry: ", unitarity_defect)
@assert isapprox(unitarity_defect, 0.0; atol=1e-9) "Transcribed Knill matrix is not unitary -- check Eq. 11 transcription"
println("PASS: transcribed matrix is unitary, as the paper claims (transpose of a unitary is unitary, so this holds either way).")

println()
println("Eq. 6 zero-leak diagnostic (standalone 4-mode gate, before 6-mode embedding):")
let
    diag_interf = UserDefinedInterferometer(ComplexF64.(V180))
    function diag_amp(inpat, outpat)
        ev = Event(Input{Bosonic}(ModeOccupation(inpat)), FockDetection(ModeOccupation(outpat)), diag_interf)
        return compute_probability!(ev)
    end
    leak_0110 = diag_amp([0, 1, 1, 1], [1, 0, 1, 1])
    leak_1001 = diag_amp([1, 0, 1, 1], [0, 1, 1, 1])
    leak_1120 = diag_amp([1, 1, 1, 1], [2, 0, 1, 1])
    leak_1102 = diag_amp([1, 1, 1, 1], [0, 2, 1, 1])
    println("  alpha_0110 (want 0): ", leak_0110)
    println("  alpha_1001 (want 0): ", leak_1001)
    println("  alpha_1120 (want 0): ", leak_1120)
    println("  alpha_1102 (want 0): ", leak_1102)
    @assert all(x -> isapprox(x, 0.0; atol=1e-9), [leak_0110, leak_1001, leak_1120, leak_1102]) "Eq. 6 zero-leak constraints not satisfied -- matrix orientation still wrong"
    println("PASS: all four Eq. 6 zero-leak constraints hold to numerical precision.")
end

# ---------------------------------------------------------------------------
# 6-mode embedding: [A0, A1, B0, B1, H1, H2]
# ---------------------------------------------------------------------------

function embed_hadamard6()
    Hd = (1 / sqrt(2)) .* [1.0 1.0; 1.0 -1.0]
    U = zeros(ComplexF64, 6, 6)
    U[1, 1] = Hd[1, 1]; U[1, 2] = Hd[1, 2]
    U[2, 1] = Hd[2, 1]; U[2, 2] = Hd[2, 2]
    U[3, 3] = Hd[1, 1]; U[3, 4] = Hd[1, 2]
    U[4, 3] = Hd[2, 1]; U[4, 4] = Hd[2, 2]
    U[5, 5] = 1.0
    U[6, 6] = 1.0
    return U
end

function embed_correction6(theta)
    U = zeros(ComplexF64, 6, 6)
    U[1, 1] = exp(im * theta)    # A0 (bit 0) -- Zi eigenvalue +1
    U[2, 2] = exp(-im * theta)   # A1 (bit 1) -- Zi eigenvalue -1
    U[3, 3] = exp(im * theta)    # B0 (bit 0)
    U[4, 4] = exp(-im * theta)   # B1 (bit 1)
    U[5, 5] = 1.0
    U[6, 6] = 1.0
    return U
end

function embed_cz6(V::Matrix{Float64})
    U = zeros(ComplexF64, 6, 6)
    U[1, 1] = 1.0   # A0 spectator (Knill: logical-|0> rail untouched)
    U[3, 3] = 1.0   # B0 spectator
    idx = [2, 4, 5, 6]   # A1, B1, H1, H2 <- Knill's modes 1, 2, 3, 4
    for (ki, gi) in enumerate(idx), (kj, gj) in enumerate(idx)
        U[gi, gj] = V[ki, kj]
    end
    return U
end

state_prep = embed_hadamard6()
correction = embed_correction6(pi / 4)
cz_embed = embed_cz6(V180)
conjugation = embed_hadamard6()

# Application order: state_prep first, then cz gate, then the pi/4
# correction, then conjugation (see header note on this choice).
FULL = conjugation * correction * cz_embed * state_prep

unitarity_defect_full = maximum(abs.(FULL' * FULL - I(6)))
println()
println("Composite 6-mode unitary max |U'U - I| entry: ", unitarity_defect_full)
@assert isapprox(unitarity_defect_full, 0.0; atol=1e-9) "Composite circuit matrix is not unitary"
println("PASS: composite 6-mode circuit matrix is unitary.")

# ---------------------------------------------------------------------------
# Task 2: run the circuit, herald by hand, compare against
# results/julia_reference/weight2_locked_n2.csv
# ---------------------------------------------------------------------------

interf = UserDefinedInterferometer(FULL)

# Input: bit=0 on both qubits (photon in A0, B0), ancilla prepared with one
# photon each in H1, H2 -- matches thetas=[0,0]'s all-zero-bitstring start,
# same as any standard IQP circuit's input convention.
input_state = Input{Bosonic}(ModeOccupation([1, 0, 1, 0, 1, 1]))

# All 10 ways to distribute the 2 non-ancilla photons across the 4 data
# modes, with the ancilla output fixed at exactly 1 photon each (the herald
# condition). The first 4 are the valid dual-rail bitstrings; the remaining
# 6 are bunched/invalid (residual).
valid_patterns = Dict(
    "00" => [1, 0, 1, 0],
    "01" => [1, 0, 0, 1],
    "10" => [0, 1, 1, 0],
    "11" => [0, 1, 0, 1],
)
bunched_patterns = [
    [2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 0, 0, 2],
    [1, 1, 0, 0], [0, 0, 1, 1],
]

function herald_success_prob(data_pattern)
    out = FockDetection(ModeOccupation(vcat(data_pattern, [1, 1])))
    ev = Event(input_state, out, interf)
    return compute_probability!(ev)
end

println()
println("=" ^ 70)
println("Task 2: full weight-2 locked-gate circuit, herald-by-hand")
println("=" ^ 70)

raw_valid = Dict{String,Float64}()
for (bitstring, pattern) in valid_patterns
    raw_valid[bitstring] = herald_success_prob(pattern)
    println("bitstring=$bitstring pattern=$pattern raw_prob=$(raw_valid[bitstring])")
end

raw_bunched_total = 0.0
global raw_bunched_total
for pattern in bunched_patterns
    global raw_bunched_total
    p = herald_success_prob(pattern)
    raw_bunched_total += p
    if p > 1e-12
        println("bunched pattern=$pattern raw_prob=$p")
    end
end

herald_success_total = sum(values(raw_valid)) + raw_bunched_total
herald_failure_prob = 1.0 - herald_success_total

println()
println("Sum of raw valid-pattern probabilities: ", sum(values(raw_valid)))
println("Sum of raw bunched (residual, pre-herald-renorm) probabilities: ", raw_bunched_total)
println("Total herald-success probability: ", herald_success_total)
println("Measured herald_failure_prob: ", herald_failure_prob)
println("Expected herald_failure_prob (1 - 2/27): ", 1.0 - 2.0 / 27.0)

# Renormalize by the herald-success total, matching
# photonic_weight2_iqp_distribution's own documented contract:
# sum(dist) + residual == 1.0 (verified in julia/generate_reference.py's
# header comments / 19-01-SUMMARY.md decision log).
julia_dist = Dict(k => v / herald_success_total for (k, v) in raw_valid)
julia_residual = raw_bunched_total / herald_success_total

println()
println("Renormalized Julia distribution (sum(dist)+residual should be 1.0):")
for k in sort(collect(keys(julia_dist)))
    println("  $k => $(julia_dist[k])")
end
println("  residual => $julia_residual")
println("  sum(dist)+residual = ", sum(values(julia_dist)) + julia_residual)

# ---------------------------------------------------------------------------
# Read the Python reference CSV and compute TVD (reimplementing the exact
# formula from iqp_photonic_encoding.py::total_variation_distance)
# ---------------------------------------------------------------------------

function read_reference_csv(path)
    dist = Dict{String,Float64}()
    header = Dict{String,String}()
    open(path, "r") do f
        for line in eachline(f)
            if startswith(line, "#")
                content = strip(line[2:end])
                for kv in split(content, " ")
                    if occursin("=", kv)
                        k, v = split(kv, "="; limit=2)
                        header[k] = v
                    end
                end
            elseif startswith(line, "bitstring")
                continue
            elseif !isempty(strip(line))
                parts = split(line, ",")
                bitstring = String(parts[1])
                prob = parse(Float64, parts[2])
                dist[bitstring] = prob
            end
        end
    end
    return dist, header
end

function total_variation_distance(a::Dict{String,Float64}, b::Dict{String,Float64})
    keys_union = union(keys(a), keys(b))
    total = 0.0
    for k in keys_union
        va = get(a, k, 0.0)
        vb = get(b, k, 0.0)
        total += abs(va - vb)
    end
    return 0.5 * total
end

ref_path = joinpath(@__DIR__, "..", "results", "julia_reference", "weight2_locked_n2.csv")
python_dist, python_header = read_reference_csv(ref_path)

println()
println("=" ^ 70)
println("Comparison against Python reference: ", ref_path)
println("=" ^ 70)
println("Python header: ", python_header)
println("Python distribution: ", python_dist)

tvd = total_variation_distance(julia_dist, python_dist)
println()
println("Measured TVD (Julia vs. Python): ", tvd)

python_herald_failure = haskey(python_header, "herald_failure_prob") ?
    parse(Float64, python_header["herald_failure_prob"]) : NaN
herald_failure_diff = abs(herald_failure_prob - python_herald_failure)
println("Python herald_failure_prob: ", python_herald_failure)
println("Julia herald_failure_prob: ", herald_failure_prob)
println("|difference|: ", herald_failure_diff)

TOL = 1e-6
tvd_pass = tvd <= TOL
herald_pass = herald_failure_diff <= 1e-4  # looser: this is a probability, not an exact-arithmetic quantity

println()
println("=" ^ 70)
if tvd_pass && herald_pass
    println("RESULT: GO -- TVD=$tvd <= $TOL, herald_failure_prob matches within tolerance.")
else
    println("RESULT: DISAGREEMENT -- TVD=$tvd (tol=$TOL), herald_failure diff=$herald_failure_diff")
    println("See results/phase19_verify03_weight2_results.md for the honest verdict and analysis.")
end
println("=" ^ 70)
