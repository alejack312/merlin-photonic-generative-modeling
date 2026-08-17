# Phase 19 Plan 05: VERIFY-04 -- independent BosonSampling.jl native-loss
# cross-check of Phase 18's photon-loss model (weight-1 and mixed scope,
# n=2, at eta in {0.99, 0.80, 0.05}).
#
# =============================================================================
# Task 1: native loss API investigation (installed v1.0.2 -- confirmed
# directly against the local depot source at
# ~/.julia/packages/BosonSampling/TEQXU/src/types/loss.jl, NOT GitHub main,
# NOT assumed from 19-RESEARCH.md's own explicitly-flagged unverified
# snippets)
# =============================================================================
#
# Confirmed API surface (read directly from the installed source before
# writing any comparison logic):
#
#   - `UniformLossInterferometer(η::Real, U_physical::Matrix) <: Interferometer`
#     exists and builds a virtual 2m x 2m interferometer: for every physical
#     mode i in 1:m, a loss beamsplitter connects physical mode i to its OWN
#     dedicated environment mode m+i, with transmission_amplitude=η, THEN
#     (matrix-multiplication order) the physical unitary U_physical is
#     folded in (`virtual_interferometer_uniform_loss`, loss.jl:9-36). Since
#     every one of these m loss beamsplitters uses the IDENTICAL η (a
#     genuinely "uniform" model) and each acts only on its own disjoint
#     (physical-mode-i, environment-mode-i) pair -- never mixing different
#     physical modes with each other the way U_physical does -- this loss
#     operation commutes with U_physical regardless of internal application
#     order. This matches this repo's own Python-side commutation argument
#     (hardness/loss_model.py's docstring, citing Park & Oh arXiv:2510.24137
#     Sec. II.B) for why front-loading LC before build_full_circuit is exact,
#     not a simplification -- so this script does not need to worry about
#     circuit-vs-loss ordering matching Python's literal front-loaded-LC
#     convention step-for-step; the RESULTING physical-mode marginal is the
#     same regardless.
#
#   - CONVENTION MISMATCH found and resolved (confirmed against source, not
#     assumed): `η` in `UniformLossInterferometer(η, U)` is a TRANSMISSION
#     AMPLITUDE, not a transmission probability -- confirmed from
#     circuit_elements.jl's `beam_splitter(transmission_amplitude)`, whose
#     own comment states "|t|^2 is the transmission probability", and
#     `UniformLossInterferometer` passes `η` straight through to
#     `beam_splitter_modes(transmission_amplitude = η, ...)` with no
#     squaring. This repo's Python-side `eta` (loss_model.py,
#     loss_model_weight2.py) is documented as a literal transmittance
#     PROBABILITY ("eta in [0.0, 1.0]: transmittance"). To make the two
#     eta's mean the SAME physical quantity, this script passes `sqrt(eta)`
#     as `UniformLossInterferometer`'s first argument. VERIFIED (not
#     assumed) by the n=1 sanity check below: p(survive) measured exactly
#     equal to eta_python (not sqrt(eta_python) or eta_python^2), confirming
#     eta_python = (transmission_amplitude)^2.
#
#   - REAL BUG FOUND in the installed v1.0.2 API, worked around (Rule 3 --
#     blocking, auto-fixed): constructing `Event(input, output,
#     uniform_loss_interferometer)` directly raises
#     `MethodError: no method matching LossParameters(::Type{UniformLossInterferometer})`
#     -- `Event`'s inner constructor dispatches on `LossParameters(typeof(interferometer))`
#     (events.jl) to decide input-padding behavior, but `UniformLossInterferometer`
#     never registered a `LossParameters` method for its own type (only
#     `RandomPhaseShifter`, `LosslessLoop`, `LossyBeamSplitter`, etc. have
#     one -- confirmed via the MethodError's own "Closest candidates" list).
#     This is a genuine gap in the installed package, verified live (not
#     inferred) via a standalone repro before writing this workaround.
#     WORKAROUND: wrap the interferometer's own `.U` field (BosonSampling's
#     own native `virtual_interferometer_uniform_loss`-computed 2m x 2m
#     unitary -- the exact quantity `UniformLossInterferometer` exists to
#     compute) in `UserDefinedInterferometer(li.U)` instead of passing `li`
#     directly to `Event`. `UserDefinedInterferometer` DOES have a
#     `LossParameters` method (confirmed working in Plans 19-02/19-03/19-04)
#     and, since compute_probability! only ever reads `ev.interferometer.U`
#     (scattering.jl:356), the numerical result is IDENTICAL either way --
#     this routes around a dispatch-registration gap, not around the loss
#     PHYSICS, which still comes entirely from BosonSampling's own native
#     `UniformLossInterferometer`/`virtual_interferometer_uniform_loss`
#     construction. This is still genuinely "using the native loss API", not
#     a hand-attenuation fallback.
#
#   - Doubled-mode marginalization (19-RESEARCH.md Pitfall 3 / Open Question
#     2): NOT delegated to `sort_by_lost_photons`/`lossless_part`/
#     `keep_lossless_part!` -- those operate on a `MultipleCounts`/Partition
#     sampling abstraction this script has no other reason to use, and their
#     semantics were flagged in 19-RESEARCH.md as unverified. Instead this
#     script does the marginalization BY HAND, directly and exactly: the
#     virtual 2m-mode interferometer is unitary, so the TOTAL photon number
#     across all 2m modes (physical + environment) is exactly conserved at
#     the input photon count N (N=2 for weight-1 n=2; N=4 for mixed n=2,
#     matching the n data photons + 2 ancilla photons the Python-side
#     `_build_weight2_processor_lossy` uses). This script enumerates EVERY
#     non-negative-integer composition of N across the 2m output modes --
#     C(N+2m-1, 2m-1) of them: 36 for weight-1 n=2 (N=2, 2m=8), 1365 for
#     mixed n=2 (N=4, 2m=12), both small, EXACT enumerations (not sampling)
#     -- calls `compute_probability!` once per full 2m-mode pattern, and
#     sums probabilities into a bucket keyed by the first-m (physical-mode)
#     sub-pattern. Summing an exact probability over every environment-mode
#     split consistent with a fixed physical outcome IS the marginal
#     distribution over physical outcomes, by the definition of
#     marginalization -- no additional library helper is needed for this.
#
# CONCLUSION: BosonSampling.jl's native `UniformLossInterferometer` loss
# model IS used (the strongly-preferred path per 19-RESEARCH.md's "Don't
# Hand-Roll" table), with one narrow, documented, verified workaround for a
# real dispatch gap in the installed v1.0.2 package -- this is NOT the
# hand-attenuation fallback CONTEXT.md names as the alternative for when no
# usable native API exists.
#
# Run: julia --project=julia julia/verify_loss_model.jl

using BosonSampling
using LinearAlgebra

println("Julia: ", VERSION)
println("BosonSampling: ", pkgversion(BosonSampling))

# =============================================================================
# Task 1: n=1 sanity check -- confirms the eta_python = (transmission
# amplitude)^2 convention and the UserDefinedInterferometer(li.U) workaround,
# against the known closed-form single-mode loss case (transmission
# probability = eta, loss probability = 1 - eta), BEFORE trusting the n=2
# weight-1/mixed comparison.
# =============================================================================

println("\n--- Task 1: n=1 native-loss sanity check ---")

function n1_survival_and_loss_prob(eta_python::Float64)
    U_physical = reshape(ComplexF64[1.0 + 0im], 1, 1)  # trivial 1-mode "circuit"
    t = sqrt(eta_python)
    li = UniformLossInterferometer(t, U_physical)
    interf = UserDefinedInterferometer(li.U)  # workaround for the LossParameters gap (see header)

    input_state = Input{Bosonic}(ModeOccupation([1, 0]))  # photon in physical mode, env empty

    ev_survive = Event(input_state, FockDetection(ModeOccupation([1, 0])), interf)
    p_survive = compute_probability!(ev_survive)

    ev_lost = Event(input_state, FockDetection(ModeOccupation([0, 1])), interf)
    p_lost = compute_probability!(ev_lost)

    return p_survive, p_lost
end

for eta_test in [0.99, 0.80, 0.05]
    p_s, p_l = n1_survival_and_loss_prob(eta_test)
    println("eta=$eta_test: p(survive)=$p_s (expect $eta_test), p(lost)=$p_l (expect $(1.0 - eta_test))")
    @assert isapprox(p_s, eta_test; atol=1e-10) "n=1 survival probability mismatch at eta=$eta_test"
    @assert isapprox(p_l, 1.0 - eta_test; atol=1e-10) "n=1 loss probability mismatch at eta=$eta_test"
    @assert isapprox(p_s + p_l, 1.0; atol=1e-10) "n=1 probabilities do not normalize at eta=$eta_test"
end

println("PASS: n=1 sanity check confirms eta_python = (transmission_amplitude)^2, and the native UniformLossInterferometer construction (wrapped via UserDefinedInterferometer to route around the installed-version LossParameters gap) reproduces the known closed-form single-mode loss case exactly.")

# =============================================================================
# Task 2: n=2 weight-1 and mixed loss cross-checks at 3 eta values.
# =============================================================================

println("\n--- Task 2: n=2 weight-1 and mixed loss cross-checks ---")

# --- General marginalization helper (native-loss doubled-mode -> physical
# marginal, done by hand per Task 1's investigation) -------------------------

"""All non-negative-integer vectors of length `num_modes` summing to `total`
-- an exact enumeration (not sampling), tractable at this plan's locked n=2
scale (36 patterns for weight-1, 1365 for mixed)."""
function enumerate_patterns(total::Int, num_modes::Int)
    if num_modes == 1
        return [[total]]
    end
    patterns = Vector{Vector{Int}}()
    for k in 0:total
        for rest in enumerate_patterns(total - k, num_modes - 1)
            push!(patterns, vcat([k], rest))
        end
    end
    return patterns
end

"""Computes the EXACT physical-mode marginal distribution (a Dict from
physical-mode pattern -> probability) for a physical circuit `U_physical`
(m x m) under BosonSampling.jl's native uniform loss model at eta_python,
starting from `input_physical` (length-m occupation vector). Sums
compute_probability! over every environment-mode split consistent with each
fixed physical outcome (Task 1's confirmed marginalization approach)."""
function compute_lossy_physical_marginal(U_physical::Matrix{ComplexF64}, input_physical::Vector{Int}, eta_python::Float64)
    m = size(U_physical, 1)
    @assert size(U_physical, 2) == m
    @assert length(input_physical) == m
    N = sum(input_physical)

    t = sqrt(eta_python)
    li = UniformLossInterferometer(t, U_physical)
    interf = UserDefinedInterferometer(li.U)  # LossParameters workaround, see header

    padded_input = vcat(input_physical, zeros(Int, m))
    input_state = Input{Bosonic}(ModeOccupation(padded_input))

    physical_totals = Dict{Vector{Int},Float64}()
    for pattern in enumerate_patterns(N, 2 * m)
        ev = Event(input_state, FockDetection(ModeOccupation(pattern)), interf)
        p = compute_probability!(ev)
        phys = pattern[1:m]
        physical_totals[phys] = get(physical_totals, phys, 0.0) + p
    end
    return physical_totals
end

# --- Weight-1 physical circuit (dual-rail, reusing Plan 19-03's verified
# H*phase_shift(pi-2*theta)*H construction -- weight-1 has no entangling
# gate, so only the per-qubit marginal needs to be correct; already proven
# to machine precision in Plan 19-03) ----------------------------------------

hadamard_block() = beam_splitter(1 / sqrt(2))

function weight1_qubit_pair_unitary(theta::Float64)
    H = hadamard_block()
    D = phase_shift(pi - 2 * theta)
    H * D * H
end

function weight1_physical_unitary(thetas::Vector{Float64})
    blocks = [ComplexF64.(weight1_qubit_pair_unitary(t)) for t in thetas]
    reduce((a, b) -> cat(a, b; dims=(1, 2)), blocks)
end

function try_decode_weight1(phys::Vector{Int}, n::Int)
    bits = Char[]
    for k in 1:n
        u = phys[2*k-1]
        l = phys[2*k]
        if u == 1 && l == 0
            push!(bits, '0')
        elseif u == 0 && l == 1
            push!(bits, '1')
        else
            return nothing
        end
    end
    return join(bits)
end

function classify_weight1(physical_totals::Dict{Vector{Int},Float64}, n::Int)
    dist = Dict{String,Float64}()
    residual = 0.0
    for (phys, p) in physical_totals
        bits = try_decode_weight1(phys, n)
        if bits === nothing
            residual += p
        else
            dist[bits] = get(dist, bits, 0.0) + p
        end
    end
    return dist, residual
end

# --- Mixed (weight-1 + weight-2) physical circuit (n=2, i=0, j=1 -- reusing
# Plan 19-04's independently-sourced Knill CZ construction (arXiv:quant-ph/
# 0110144 Eq. 11, transpose-fixed) verbatim, generalized from Plan 19-04's
# single-shared-theta `embed_correction6` to accept two independent
# per-qubit diagonal phases theta_A/theta_B = thetas[i]+pi/4, thetas[j]+pi/4
# -- matching Python's `_build_weight2_processor_lossy`'s
# `thetas_folded[i] += pi/4; thetas_folded[j] += pi/4` exactly, and using
# the SAME symmetric diag(e^{i*theta}, e^{-i*theta}) convention
# `build_diagonal_layer_circuit` uses (confirmed directly in
# iqp_photonic_encoding.py, not assumed) -- unlike weight-1's asymmetric
# phase_shift trick, this convention must be exact here because the CZ gate
# creates real interference/entanglement between the two qubit pairs, so
# only the per-qubit MARGINAL being right (as in weight-1) is not sufficient. --

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
# Same transpose-convention fix Plan 19-04 found and verified (Eq. 6 zero-leak
# diagnostic) -- reused verbatim, not re-derived.
V180 = collect(transpose(V180_paper))

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

function embed_diagonal6(theta_A::Float64, theta_B::Float64)
    U = zeros(ComplexF64, 6, 6)
    U[1, 1] = exp(im * theta_A)    # A0 (bit 0, qubit i) -- Zi eigenvalue +1
    U[2, 2] = exp(-im * theta_A)   # A1 (bit 1, qubit i) -- Zi eigenvalue -1
    U[3, 3] = exp(im * theta_B)    # B0 (bit 0, qubit j)
    U[4, 4] = exp(-im * theta_B)   # B1 (bit 1, qubit j)
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

"""Full n=2, i=0, j=1 mixed physical 6x6 unitary. thetas = [theta_i, theta_j]
(the externally-passed weight-1 angles for qubits i and j BEFORE the +pi/4
correction -- matches Python's `thetas` argument, not `thetas_folded`)."""
function mixed_physical_unitary(thetas::Vector{Float64})
    @assert length(thetas) == 2
    theta_A = thetas[1] + pi / 4
    theta_B = thetas[2] + pi / 4
    state_prep = embed_hadamard6()
    diagonal = embed_diagonal6(theta_A, theta_B)
    cz_embed = embed_cz6(V180)
    conjugation = embed_hadamard6()
    return conjugation * diagonal * cz_embed * state_prep
end

MIXED_VALID_PATTERNS = Dict(
    "00" => [1, 0, 1, 0],
    "01" => [1, 0, 0, 1],
    "10" => [0, 1, 1, 0],
    "11" => [0, 1, 0, 1],
)

function classify_mixed(physical_totals::Dict{Vector{Int},Float64})
    dist = Dict{String,Float64}()
    residual = 0.0
    herald_failure = 0.0
    for (phys, p) in physical_totals
        ancilla = phys[5:6]
        if ancilla != [1, 1]
            herald_failure += p
            continue
        end
        data = phys[1:4]
        matched = false
        for (bits, pat) in MIXED_VALID_PATTERNS
            if data == pat
                dist[bits] = get(dist, bits, 0.0) + p
                matched = true
                break
            end
        end
        if !matched
            residual += p
        end
    end
    herald_success = 1.0 - herald_failure
    if herald_success > 0
        dist = Dict(k => v / herald_success for (k, v) in dist)
        residual = residual / herald_success
    end
    return dist, residual, herald_failure
end

# --- Reference CSV reading + TVD (reimplemented, same formula as Plans
# 19-02/19-03/19-04) ----------------------------------------------------------

function read_reference_csv(path::String)
    dist = Dict{String,Float64}()
    header = Dict{String,String}()
    open(path, "r") do io
        for line in eachline(io)
            stripped = strip(line)
            isempty(stripped) && continue
            if startswith(stripped, "#")
                content = strip(stripped[2:end])
                for kv in split(content, " ")
                    if occursin("=", kv)
                        k, v = split(kv, "="; limit=2)
                        header[k] = v
                    end
                end
                continue
            end
            stripped == "bitstring,probability" && continue
            parts = split(stripped, ",")
            dist[String(parts[1])] = parse(Float64, parts[2])
        end
    end
    return dist, header
end

function total_variation_distance(dist_a::Dict{String,Float64}, dist_b::Dict{String,Float64})
    ks = union(keys(dist_a), keys(dist_b))
    s = 0.0
    for k in ks
        s += abs(get(dist_a, k, 0.0) - get(dist_b, k, 0.0))
    end
    return 0.5 * s
end

TVD_TOLERANCE = 1e-6

# --- Run weight-1 leg: n=2, thetas fixed from Plan 19-01's single draw
# (results/julia_reference/weight1_loss_n2_eta*.csv header) ------------------

WEIGHT1_THETAS = [1.4696702887560742, 0.5745464671322527]
WEIGHT1_ETA_FILES = Dict(
    0.99 => "results/julia_reference/weight1_loss_n2_eta099.csv",
    0.80 => "results/julia_reference/weight1_loss_n2_eta080.csv",
    0.05 => "results/julia_reference/weight1_loss_n2_eta005.csv",
)

println("\n--- Weight-1 leg (n=2, thetas=$WEIGHT1_THETAS) ---")

weight1_results = []
U_weight1 = weight1_physical_unitary(WEIGHT1_THETAS)
for eta_val in [0.99, 0.80, 0.05]
    physical_totals = compute_lossy_physical_marginal(U_weight1, [1, 0, 1, 0], eta_val)
    dist, residual = classify_weight1(physical_totals, 2)
    total = sum(values(dist)) + residual
    println("eta=$eta_val: sum(dist)+residual = $total (should be ~1.0)")
    @assert isapprox(total, 1.0; atol=1e-8) "eta=$eta_val weight-1 probabilities do not normalize (got $total)"

    ref_path = WEIGHT1_ETA_FILES[eta_val]
    ref_dist, ref_header = read_reference_csv(ref_path)
    tvd = total_variation_distance(dist, ref_dist)
    println("eta=$eta_val: TVD=$tvd (ref residual=$(get(ref_header, "residual", "?")), julia residual=$residual)")
    push!(weight1_results, (eta=eta_val, tvd=tvd, julia_dist=dist, julia_residual=residual, ref_dist=ref_dist, ref_header=ref_header))
end

# --- Run mixed leg: n=2, i=0, j=1, thetas fixed from Plan 19-01's single
# draw (results/julia_reference/mixed_loss_n2_eta*.csv header) --------------

MIXED_THETAS = [1.6612470810666293, 1.2467258944387942]
MIXED_ETA_FILES = Dict(
    0.99 => "results/julia_reference/mixed_loss_n2_eta099.csv",
    0.80 => "results/julia_reference/mixed_loss_n2_eta080.csv",
    0.05 => "results/julia_reference/mixed_loss_n2_eta005.csv",
)

println("\n--- Mixed leg (n=2, i=0, j=1, thetas=$MIXED_THETAS) ---")

mixed_results = []
U_mixed = mixed_physical_unitary(MIXED_THETAS)
for eta_val in [0.99, 0.80, 0.05]
    physical_totals = compute_lossy_physical_marginal(U_mixed, [1, 0, 1, 0, 1, 1], eta_val)
    dist, residual, herald_failure = classify_mixed(physical_totals)
    total = sum(values(dist)) + residual
    println("eta=$eta_val: sum(dist)+residual = $total (should be ~1.0), herald_failure_prob=$herald_failure")
    @assert isapprox(total, 1.0; atol=1e-8) "eta=$eta_val mixed probabilities do not normalize (got $total)"

    ref_path = MIXED_ETA_FILES[eta_val]
    ref_dist, ref_header = read_reference_csv(ref_path)
    tvd = total_variation_distance(dist, ref_dist)
    ref_herald_failure = haskey(ref_header, "herald_failure_prob") ? parse(Float64, ref_header["herald_failure_prob"]) : NaN
    herald_diff = abs(herald_failure - ref_herald_failure)
    println("eta=$eta_val: TVD=$tvd, herald_failure_prob (julia)=$herald_failure vs (python)=$ref_herald_failure, |diff|=$herald_diff")
    push!(mixed_results, (eta=eta_val, tvd=tvd, herald_failure=herald_failure, ref_herald_failure=ref_herald_failure, herald_diff=herald_diff, julia_dist=dist, julia_residual=residual, ref_dist=ref_dist, ref_header=ref_header))
end

# --- Verdict + results doc ---------------------------------------------------

weight1_pass = all(r.tvd <= TVD_TOLERANCE for r in weight1_results)
HERALD_TOLERANCE = 1e-4  # looser: this is a measured probability, not exact arithmetic (matches Plan 19-04's convention)
mixed_pass = all(r.tvd <= TVD_TOLERANCE && r.herald_diff <= HERALD_TOLERANCE for r in mixed_results)

println()
println("=" ^ 70)
if weight1_pass
    println("Weight-1 leg: PASS (all TVDs <= $TVD_TOLERANCE)")
else
    println("Weight-1 leg: DISAGREEMENT (see results/phase19_verify04_results.md)")
end
if mixed_pass
    println("Mixed leg: PASS (all TVDs <= $TVD_TOLERANCE, herald_failure_prob within $HERALD_TOLERANCE)")
else
    println("Mixed leg: DISAGREEMENT (see results/phase19_verify04_results.md)")
end
println("=" ^ 70)

verdict = weight1_pass && mixed_pass ? "GO" : (weight1_pass || mixed_pass ? "PARTIAL-GO (documented disagreement, see below)" : "NO-GO (documented disagreement, see below)")

open("results/phase19_verify04_results.md", "w") do io
    println(io, "# Phase 19 Plan 05: VERIFY-04 Results")
    println(io)
    println(io, "## Methodology")
    println(io)
    println(io, "### Native loss API investigation (Task 1)")
    println(io)
    println(io, "BosonSampling.jl's native `UniformLossInterferometer(η, U_physical)` loss")
    println(io, "API (confirmed against the ACTUAL installed v1.0.2 source at")
    println(io, "`~/.julia/packages/BosonSampling/TEQXU/src/types/loss.jl`, not GitHub main)")
    println(io, "IS used -- the strongly-preferred path per `19-RESEARCH.md`'s \"Don't Hand-Roll\"")
    println(io, "table -- with one narrow, verified workaround for a real dispatch gap in the")
    println(io, "installed package:")
    println(io)
    println(io, "- **Convention mismatch found and resolved:** `η` in `UniformLossInterferometer`")
    println(io, "  is a transmission AMPLITUDE (confirmed from `circuit_elements.jl`'s")
    println(io, "  `beam_splitter` comment: `|t|^2` is the transmission probability), while this")
    println(io, "  repo's Python-side `eta` is a transmission PROBABILITY. This script passes")
    println(io, "  `sqrt(eta)` to make the two `eta`'s mean the same physical quantity --")
    println(io, "  verified by the n=1 sanity check below.")
    println(io, "- **Real bug found in the installed package, worked around:**")
    println(io, "  `Event(input, output, uniform_loss_interferometer)` raises")
    println(io, "  `MethodError: no method matching LossParameters(::Type{UniformLossInterferometer})`")
    println(io, "  -- confirmed live via a standalone repro, not inferred. Worked around by")
    println(io, "  wrapping the interferometer's own native-computed `.U` field in")
    println(io, "  `UserDefinedInterferometer(li.U)` before constructing `Event`s --")
    println(io, "  `compute_probability!` only ever reads `ev.interferometer.U`, so the")
    println(io, "  numerical result is identical; only the dispatch path differs. The loss")
    println(io, "  PHYSICS still comes entirely from BosonSampling's own native")
    println(io, "  `UniformLossInterferometer`/`virtual_interferometer_uniform_loss`")
    println(io, "  construction -- this is not a hand-attenuation fallback.")
    println(io, "- **Doubled-mode marginalization:** done by hand (not via")
    println(io, "  `sort_by_lost_photons`/`lossless_part`, whose semantics were unverified per")
    println(io, "  `19-RESEARCH.md` Open Question 2): every non-negative-integer composition of")
    println(io, "  the conserved total photon count N across the 2m output modes is enumerated")
    println(io, "  exactly (36 patterns for weight-1 n=2, 1365 for mixed n=2), `compute_probability!`")
    println(io, "  is called once per full 2m-mode pattern, and probabilities are summed into a")
    println(io, "  bucket keyed by the physical-mode (first-m) sub-pattern -- an exact marginal,")
    println(io, "  not sampling or approximation.")
    println(io)
    println(io, "See `julia/verify_loss_model.jl`'s header comment for the full investigation")
    println(io, "detail and source citations.")
    println(io)
    println(io, "### n=1 sanity check")
    println(io)
    println(io, "Confirmed `eta_python = (transmission_amplitude)^2` and the")
    println(io, "`UserDefinedInterferometer(li.U)` workaround against the known closed-form")
    println(io, "single-mode loss case (p(survive)=eta, p(lost)=1-eta) at eta in {0.99, 0.80, 0.05},")
    println(io, "atol=1e-10, before trusting the n=2 comparison. PASS.")
    println(io)
    println(io, "### n=2 cross-checks")
    println(io)
    println(io, "Weight-1: an independently-built dual-rail circuit (reusing Plan 19-03's verified")
    println(io, "`H*phase_shift(pi-2*theta)*H` per-qubit construction, block-diagonal, no entangling")
    println(io, "gate) under native uniform loss, marginalized to a physical-mode distribution, diffed")
    println(io, "against `results/julia_reference/weight1_loss_n2_eta{099,080,005}.csv` (Plan 19-01's")
    println(io, "fixed single-draw thetas=$WEIGHT1_THETAS).")
    println(io)
    println(io, "Mixed: an independently-built n=2, i=0, j=1 weight-1+weight-2 circuit (reusing Plan")
    println(io, "19-04's verified Knill-CZ construction, arXiv:quant-ph/0110144 Eq. 11 transpose-fixed,")
    println(io, "generalized to two independent per-qubit diagonal phases theta_A/theta_B = thetas[i]+pi/4,")
    println(io, "thetas[j]+pi/4, matching `build_diagonal_layer_circuit`'s symmetric diag(e^{i*theta},")
    println(io, "e^{-i*theta}) convention exactly since the CZ gate creates real interference between the")
    println(io, "two qubit pairs) under native uniform loss (applied to all 2n+2=6 physical modes,")
    println(io, "including both ancilla modes -- matching Python's ancilla-inclusive HARD-07 model),")
    println(io, "herald accounting done by hand exactly as Plan 19-04 did (ancilla output pattern must be")
    println(io, "[1,1] or the outcome counts as herald failure), diffed against")
    println(io, "`results/julia_reference/mixed_loss_n2_eta{099,080,005}.csv` (Plan 19-01's fixed")
    println(io, "single-draw thetas=$MIXED_THETAS).")
    println(io)
    println(io, "## Results")
    println(io)
    println(io, "### Weight-1")
    println(io)
    println(io, "| eta | TVD | Tolerance | Status |")
    println(io, "|-----|-----|-----------|--------|")
    for r in weight1_results
        status = r.tvd <= TVD_TOLERANCE ? "PASS" : "FAIL"
        println(io, "| $(r.eta) | $(r.tvd) | <= $TVD_TOLERANCE | $status |")
    end
    println(io)
    println(io, "### Mixed")
    println(io)
    println(io, "| eta | TVD | herald_failure_prob (julia) | herald_failure_prob (python) | \\|diff\\| | Status |")
    println(io, "|-----|-----|------------------------------|-------------------------------|----------|--------|")
    for r in mixed_results
        status = (r.tvd <= TVD_TOLERANCE && r.herald_diff <= HERALD_TOLERANCE) ? "PASS" : "FAIL"
        println(io, "| $(r.eta) | $(r.tvd) | $(r.herald_failure) | $(r.ref_herald_failure) | $(r.herald_diff) | $status |")
    end
    println(io)
    println(io, "## Verdict")
    println(io)
    println(io, "**VERIFY-04: $verdict**")
    println(io)
    if weight1_pass && mixed_pass
        println(io, "BosonSampling.jl's independently-built weight-1 and mixed loss circuits, run")
        println(io, "through the native `UniformLossInterferometer` loss model (with the documented")
        println(io, "`LossParameters` dispatch workaround), reproduce the Python/Perceval `pcvl.LC`")
        println(io, "reference distributions within TVD <= $TVD_TOLERANCE at all 3 tested eta values")
        println(io, "for both scope, satisfying VERIFY-04 in full -- weight-1 and mixed, both scopes,")
        println(io, "using BosonSampling.jl's own native, structurally-different loss mechanism (a")
        println(io, "beamsplitter-to-environment-mode model) rather than a mechanism mirroring")
        println(io, "Perceval's `pcvl.LC` lossy-channel component.")
    else
        println(io, "One or more (eta, scope) combinations exceeded tolerance. See the per-eta table")
        println(io, "above for the measured TVD/herald-failure-probability values; this disagreement")
        println(io, "is reported honestly rather than forced to pass, per this project's established")
        println(io, "honesty norm (CONTEXT.md's disagreement-handling rule).")
    end
end

println("\nWrote results/phase19_verify04_results.md")
