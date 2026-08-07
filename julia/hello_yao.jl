# Phase 14 hello-world: Yao.jl qubit-circuit sanity check.
#
# Circuit: H on qubit 1, then CNOT(control=1, target=2), applied to |00>.
# Analytical result (Bell state (|00> + |11>)/sqrt(2)):
#   P(00) = 0.5, P(01) = 0.0, P(10) = 0.0, P(11) = 0.5
#
# This script asserts the simulated output against that hand-derived value —
# not just executing the circuit. Run with:
#   julia --project=julia julia/hello_yao.jl

using Yao

println("Julia: ", VERSION)
println("Yao: ", pkgversion(Yao))

bell_circuit = chain(2, put(1 => H), control(1, 2 => X))
reg = zero_state(2) |> bell_circuit

p = probs(reg)  # length-4 vector; Yao's bit-order convention observed below
println("Bell state probabilities (index order matches Yao's probs() convention): ", p)

# Yao's probs() indexes basis states 1..4 as |00>, |10>, |01>, |11| in
# little-endian bit order (qubit 1 = least significant bit). Bell state has
# equal amplitude only on |00> and |11>, so indices 1 and 4 hold 0.5 and
# indices 2 and 3 (the mixed-parity states) hold 0.0, regardless of bit-order
# convention -- confirmed by inspecting the printed vector above.
@assert isapprox(p[1], 0.5; atol=1e-10)
@assert isapprox(p[4], 0.5; atol=1e-10)
@assert isapprox(p[2], 0.0; atol=1e-10)
@assert isapprox(p[3], 0.0; atol=1e-10)

println("PASS: Bell state probabilities match analytical (0.5, 0.0, 0.0, 0.5)")
