# Phase 19 Plan 02 (VERIFY-02): independent Yao.jl build of this repo's
# qubit-side IQP circuit, diffed against Python's exact_qubit_iqp_distribution
# reference (results/julia_reference/qubit_n2.csv, qubit_n3.csv).
#
# Circuit (matches iqp_photonic_encoding.py::exact_qubit_iqp_distribution):
#   |+>^n = H^n |0>^n -> per-qubit diagonal Z-phase layer (weight-1 thetas)
#   -> H^n conjugation -> |amplitude|^2
#
# This is an INDEPENDENT build from Yao.jl's own qubit-gate API, not a
# mechanical port -- it uses Yao's Rz/H/put/chain primitives directly rather
# than replaying Perceval's circuit structure.
#
# Run with: julia --project=julia julia/verify_qubit_iqp.jl

using Yao
using DelimitedFiles

println("Julia: ", VERSION)
println("Yao: ", pkgversion(Yao))

# ---------------------------------------------------------------------------
# Task 1: phase-convention derivation (19-RESEARCH.md Pitfall 2)
# ---------------------------------------------------------------------------
#
# This repo's weight-1 generator gate (iqp_photonic_encoding.py,
# exact_qubit_iqp_distribution):
#   WP(theta, 0) = diag(exp(i*theta), exp(-i*theta))     [bit=0 -> +theta, bit=1 -> -theta]
#
# Yao's built-in Rz(phi) gate:
#   Rz(phi) = diag(exp(-i*phi/2), exp(i*phi/2))
#
# Setting phi = -2*theta:
#   Rz(-2*theta) = diag(exp(-i*(-2*theta)/2), exp(i*(-2*theta)/2))
#                = diag(exp(i*theta), exp(-i*theta))
#                = WP(theta, 0)                                    QED, entry-for-entry.
#
# So put(k => Rz(-2*thetas[k])) reproduces this repo's own weight-1 phase
# gate exactly (not up to global phase), applied at the same circuit
# position (between two Hadamard layers).

"""
    build_qubit_iqp_circuit(n, thetas)

Independent Yao.jl build of this repo's qubit-side IQP circuit:
zero_state(n) -> H^n -> per-qubit Rz(-2*thetas[k]) -> H^n. Returns the
resulting Yao register.
"""
function build_qubit_iqp_circuit(n, thetas)
    had_layer = chain(n, [put(k => H) for k in 1:n]...)
    phase_layer = chain(n, [put(k => Rz(-2 * thetas[k])) for k in 1:n]...)
    circuit = chain(n, had_layer, phase_layer, had_layer)
    return zero_state(n) |> circuit
end

# --- Numerical confirmation at n=1 ---
# Closed form (derived directly from exact_qubit_iqp_distribution's own math,
# see 19-RESEARCH.md): P(bit=0)=cos(theta)^2, P(bit=1)=sin(theta)^2.
theta_test = 0.3
reg1 = build_qubit_iqp_circuit(1, [theta_test])
p1 = probs(reg1)
expected_p0 = cos(theta_test)^2
expected_p1 = sin(theta_test)^2
println("n=1 phase-convention check: p=", p1, " expected=(", expected_p0, ", ", expected_p1, ")")
@assert isapprox(p1[1], expected_p0; atol=1e-10)
@assert isapprox(p1[2], expected_p1; atol=1e-10)
println("PASS: n=1 phase-convention check (Rz(-2*theta) == WP(theta,0))")

# ---------------------------------------------------------------------------
# Task 1: bit-ordering confirmation (19-RESEARCH.md Pitfall 1) -- empirical,
# not assumed from hello_yao.jl's comment or any documentation.
# ---------------------------------------------------------------------------
#
# Build an asymmetric n=2 circuit (distinct thetas per qubit). This circuit
# has no entangling gate, so each qubit's marginal is independently known in
# closed form: P(qubit_m = 0) = cos(thetas[m])^2 (the same single-qubit math
# as above, applied independently per qubit -- H^n conjugation of a purely
# per-qubit-diagonal phase layer factors into independent per-qubit
# Hadamards). This lets us empirically determine which probs() vector
# positions correspond to which physical qubit's bit=0/1, by testing two
# candidate orderings against this known ground truth.

thetas_asym = [0.3, 1.1]
reg2_probe = build_qubit_iqp_circuit(2, thetas_asym)
p2_probe = probs(reg2_probe)
println("n=2 asymmetric-theta probs vector (1-based Yao index): ", p2_probe)

# Candidate A: qubit m contributes bit (i0 >> (m-1)) & 1 of the 0-based index
# (little-endian, qubit 1 = least-significant bit -- hello_yao.jl's documented
# convention).
bit_A(i0, m, n) = (i0 >> (m - 1)) & 1
# Candidate B: qubit m contributes bit (i0 >> (n-m)) & 1 (big-endian, qubit 1
# = most-significant bit).
bit_B(i0, m, n) = (i0 >> (n - m)) & 1

function marginal_p0(p, m, n, bitfn)
    return sum(p[i0 + 1] for i0 in 0:(length(p) - 1) if bitfn(i0, m, n) == 0)
end

expected_q1_p0 = cos(thetas_asym[1])^2  # Yao qubit 1 (this repo's qubit 0)
expected_q2_p0 = cos(thetas_asym[2])^2  # Yao qubit 2 (this repo's qubit 1)

marg_A_q1 = marginal_p0(p2_probe, 1, 2, bit_A)
marg_A_q2 = marginal_p0(p2_probe, 2, 2, bit_A)
marg_B_q1 = marginal_p0(p2_probe, 1, 2, bit_B)
marg_B_q2 = marginal_p0(p2_probe, 2, 2, bit_B)

println("Expected marginals: P(q1=0)=", expected_q1_p0, " P(q2=0)=", expected_q2_p0)
println("Candidate A (qubit m = LSB): P(q1=0)=", marg_A_q1, " P(q2=0)=", marg_A_q2)
println("Candidate B (qubit m = MSB): P(q1=0)=", marg_B_q1, " P(q2=0)=", marg_B_q2)

candidate_A_matches = isapprox(marg_A_q1, expected_q1_p0; atol=1e-9) &&
                       isapprox(marg_A_q2, expected_q2_p0; atol=1e-9)
candidate_B_matches = isapprox(marg_B_q1, expected_q1_p0; atol=1e-9) &&
                       isapprox(marg_B_q2, expected_q2_p0; atol=1e-9)

@assert candidate_A_matches != candidate_B_matches "Ambiguous bit-ordering result -- both or neither candidate matched the known marginals"
@assert candidate_A_matches "Yao's bit-ordering did not match the documented little-endian (qubit m = LSB) convention -- re-derive before proceeding"

const BIT_FN = bit_A  # confirmed empirically above, not assumed

println("PASS: n=2 bit-ordering check (qubit m = LSB of Yao's 0-based probs() index, confirmed empirically against known per-qubit marginals)")

# ---------------------------------------------------------------------------
# probs_to_bitstring_dict: convert Yao's probs() vector into this repo's own
# bitstring convention (qubit 0 = leftmost character, matching
# exact_qubit_iqp_distribution's own docstring), using the
# empirically-confirmed bit-ordering fact above.
# ---------------------------------------------------------------------------

"""
    probs_to_bitstring_dict(reg, n)

Convert a Yao register's probs() vector into a Dict{String,Float64} keyed
by this repo's own bitstring convention (qubit 0 = leftmost character),
using the empirically-confirmed bit-ordering (BIT_FN) above.
"""
function probs_to_bitstring_dict(reg, n)
    p = probs(reg)
    d = Dict{String,Float64}()
    for idx in 1:length(p)
        i0 = idx - 1  # 0-based Yao index
        bits = join(string(BIT_FN(i0, m, n)) for m in 1:n)
        d[bits] = get(d, bits, 0.0) + p[idx]
    end
    return d
end

# Sanity: n=2 dict should still sum to 1.
d2_sanity = probs_to_bitstring_dict(reg2_probe, 2)
@assert isapprox(sum(values(d2_sanity)), 1.0; atol=1e-9)
println("n=2 bitstring dict (sanity, keyed by this repo's own convention): ", d2_sanity)
