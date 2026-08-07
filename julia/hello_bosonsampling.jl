# Phase 14 hello-world: BosonSampling.jl linear-optics sanity check.
#
# Circuit: 50/50 beamsplitter (transmission amplitude t = 1/sqrt(2)) applied
# to Fock input |1,0>.
# Analytical result for a single photon on a 50/50 beamsplitter:
#   P(transmitted, i.e. output |1,0>) = |t|^2 = 0.5
#   P(reflected,   i.e. output |0,1>) = |r|^2 = 0.5
#
# This script asserts the simulated output against that hand-derived value —
# not just executing the circuit. Run with:
#   julia --project=julia julia/hello_bosonsampling.jl

using BosonSampling

println("Julia: ", VERSION)
println("BosonSampling: ", pkgversion(BosonSampling))

t = 1 / sqrt(2)                       # 50/50 beamsplitter, transmission amplitude
U = beam_splitter(t)                  # confirmed-from-source 2x2 unitary
interf = UserDefinedInterferometer(U)

input_state = Input{Bosonic}(ModeOccupation([1, 0]))  # |1,0>

out_transmitted = FockDetection(ModeOccupation([1, 0]))
ev_transmitted = Event(input_state, out_transmitted, interf)
p_transmitted = compute_probability!(ev_transmitted)

out_reflected = FockDetection(ModeOccupation([0, 1]))
ev_reflected = Event(input_state, out_reflected, interf)
p_reflected = compute_probability!(ev_reflected)

println("Beamsplitter |1,0> output probabilities: transmitted=$p_transmitted, reflected=$p_reflected")

@assert isapprox(p_transmitted, 0.5; atol=1e-10)
@assert isapprox(p_reflected, 0.5; atol=1e-10)

println("PASS: beamsplitter output probabilities match analytical (0.5, 0.5)")
