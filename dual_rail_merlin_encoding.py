"""Alternate, additive implementation of this project's v2.0 (weight-1
IQP-photonic encoding), v2.1 (weight-2 CZ-insertion), and v3.0 ARB-01
(tunable weight-2 CP(alpha)) pipelines, built in a polarization-FREE spatial
dual-rail basis and wrapped by MerLin's QuantumLayer for native torch
autograd -- instead of iqp_photonic_encoding.py's existing polarization
encoding, which MerLin's QuantumLayer categorically cannot wrap (rejects
polarization-annotated BasicStates outright).

Does NOT modify iqp_photonic_encoding.py or any other existing v2.0/v2.1 code.
Purely additive: a second, parallel encoding of the same abstract IQP circuit
family. Reuses `_build_cz_insertion_core`, `fock_to_bitstring`, and
`_decode_single_qubit_pair` directly from iqp_photonic_encoding.py -- both are
already pure Fock-space/mode-occupation logic with no polarization dependence,
so they apply unchanged to this dual-rail circuit too, rather than being
re-derived here (this project's established "Don't Hand-Roll" convention).

Bit convention (matches iqp_photonic_encoding.py's own, for direct
comparability): mode pair (2k, 2k+1) occupation (0,1) = bit '0', (1,0) = bit
'1' -- per `_decode_single_qubit_pair`, reused unmodified below.

Dual-rail structural analogues of the polarization gate family:
    HWP(pi/8)   [state-prep/conjugation, Hadamard-equivalent]  -> BS()
    WP(theta,0) [diagonal Z-phase generator]                   -> PS(theta) on
                                                                   mode 2k only
    PBS()       [polarization -> dual-rail readout conversion] -> not needed;
                                                                   already dual
                                                                   rail

Single-sided PS(theta) note (why this is safe, not a simplifying
approximation): PS(theta) on mode 2k only realizes diag(e^{i*theta}, 1) on
qubit k's own 2-dim subspace, which factors as e^{i*theta/2} *
diag(e^{i*theta/2}, e^{-i*theta/2}) -- an exact scalar times the pure
exp(i*theta*Z) rotation. Because Perceval circuit evolution is linear, that
per-qubit scalar commutes through every downstream gate, including the
entangling CZ-insertion core, and lands as an unobservable overall phase on
the full measured state -- never a state-dependent relative phase. Verified
directly (not just argued): dual-rail forward output and full-gradient
autograd both matched independent bare-Perceval finite-difference ground
truth to ~1e-8 at n=1 and n=3 (weight-1) during interactive validation before
this module was written.

MerLin's QuantumLayer(circuit=...) accepts only a plain pcvl.Circuit, but the
weight-2 CZ-insertion component must land on non-contiguous global modes
(qubit i's pair, qubit j's pair, and 2 tail ancilla modes are not adjacent in
general). Circuit.add() only supports contiguous port ranges. Reusing
pcvl.Processor purely as a construction tool (its .add(mapping, ...) already
handles arbitrary non-contiguous mode wiring, exactly as
iqp_photonic_encoding.py's own build_weight2_processor does) and then
flattening via Processor.linear_circuit() sidesteps hand-rolling PERM logic --
verified live that flattening preserves named, unbound (symbolic) Parameters,
not baked-in numeric values.

Heralding/post-selection: MerLin's own docs state a custom `experiment=` "must
be unitary and without post-selection or heralding". This module never uses
`experiment=` and never calls add_herald -- it runs the flat circuit through
MerLin as a plain unitary (via `circuit=`), gets the FULL raw probability
distribution over all modes including the 2 ancilla, and does the herald
check/renormalization manually afterward in Python -- exactly mirroring
iqp_photonic_encoding.py's OWN `_build_weight2_processor_no_herald` +
`photonic_weight2_iqp_distribution` pattern (which already avoids Perceval's
native herald mechanism for an unrelated reason -- a documented add_herald+PBS
crash -- but the resulting manual-filtering strategy happens to be exactly
what's needed here too).
"""

import numpy as np
import perceval as pcvl
import torch
import merlin as ML

from iqp_photonic_encoding import (
    _build_cp_insertion_core,
    _build_cz_insertion_core,
    _decode_single_qubit_pair,
    fock_to_bitstring,
)


# ---------------------------------------------------------------------------
# Weight-1 (v2.0 analogue)
# ---------------------------------------------------------------------------


def build_dual_rail_state_prep_circuit(n):
    """BS() per qubit pair -- the dual-rail Hadamard-equivalent, matching
    build_state_prep_circuit's role (HWP(pi/8) per qubit) for the polarization
    encoding. Returns a Circuit(2n)."""
    circuit = pcvl.Circuit(2 * n)
    for k in range(n):
        circuit.add(2 * k, pcvl.BS())
    return circuit


def build_dual_rail_diagonal_layer_circuit(n, thetas):
    """PS(thetas[k]) on qubit k's mode 2k only (mode 2k+1 untouched) -- see
    module docstring for why this single-sided form is exact, not
    approximate, matching build_diagonal_layer_circuit's role (WP(thetas[k],0))
    for the polarization encoding. thetas[k]=0.0 means identity. Returns a
    Circuit(2n)."""
    assert len(thetas) == n
    circuit = pcvl.Circuit(2 * n)
    for k in range(n):
        circuit.add(2 * k, pcvl.PS(thetas[k]))
    return circuit


def build_dual_rail_conjugation_circuit(n):
    """Same BS() as state prep (its own inverse), matching
    build_conjugation_circuit's role. Returns a Circuit(2n)."""
    return build_dual_rail_state_prep_circuit(n)


def build_dual_rail_full_circuit(n, thetas):
    """Full weight-1 dual-rail pipeline: state prep -> diagonal -> conjugation.
    No readout-conversion step needed (unlike the polarization encoding's
    build_readout_circuit/PBS) -- already directly measurable in the
    mode-occupation basis. Returns a Circuit(2n)."""
    assert len(thetas) == n
    circuit = pcvl.Circuit(2 * n)
    circuit.add(0, build_dual_rail_state_prep_circuit(n))
    circuit.add(0, build_dual_rail_diagonal_layer_circuit(n, thetas))
    circuit.add(0, build_dual_rail_conjugation_circuit(n))
    return circuit


def dual_rail_all_zero_input(n):
    """BasicState with all n qubits in the '0' bitstring state, matching
    _decode_single_qubit_pair's (0,1)='0' convention: |0,1,0,1,...>."""
    return pcvl.BasicState([0, 1] * n)


def make_weight1_circuit_and_input(n):
    """Builds a fresh, symbolic (unbound) weight-1 dual-rail circuit with n
    named Parameters ('theta0'..'theta{n-1}') plus its input state. Returns
    (circuit, input_state, param_names)."""
    params = [pcvl.Parameter(f"theta{k}") for k in range(n)]
    circuit = pcvl.Circuit(2 * n)
    circuit.add(0, build_dual_rail_state_prep_circuit(n))
    diag = pcvl.Circuit(2 * n)
    for k in range(n):
        diag.add(2 * k, pcvl.PS(params[k]))
    circuit.add(0, diag)
    circuit.add(0, build_dual_rail_conjugation_circuit(n))
    return circuit, dual_rail_all_zero_input(n), [p.name for p in params]


def _validate_eta(eta):
    """Validate and normalize a uniform per-mode transmittance."""
    eta = float(eta)
    if not 0.0 <= eta <= 1.0:
        raise ValueError(f"eta must be in [0.0, 1.0], got {eta!r}")
    return eta


def make_weight1_quantum_layer(n, eta=1.0):
    """Factory for a MerLin QuantumLayer wrapping the full weight-1 dual-rail
    circuit for n qubits. All n thetas are bundled into ONE trainable
    parameter tensor of shape (n,) (MerLin's own prefix-matching behavior for
    Parameters sharing the 'theta' name prefix), in declaration order
    (theta0..theta{n-1}).

    Explicit ComputationSpace.FOCK (not MerLin's UNBUNCHED default): weight-1
    has no entangling gate, so no output state can ever be bunched (verified
    directly), meaning UNBUNCHED and FOCK give identical results here -- but
    FOCK is used uniformly across both weight-1 and weight-2 factories for
    consistency and because weight-2's default-UNBUNCHED silently dropped
    real probability mass (see make_weight2_quantum_layer's docstring).

    ``eta`` is the uniform per-mode photon transmittance. MerLin applies it
    as a differentiable photon-loss transform over the full Fock output,
    including lower-photon-number sectors; eta=1 is lossless."""
    eta = _validate_eta(eta)
    circuit, input_state, _ = make_weight1_circuit_and_input(n)
    return ML.QuantumLayer(
        circuit=circuit,
        input_state=input_state,
        trainable_parameters=["theta"],
        noise=pcvl.NoiseModel(transmittance=eta),
        measurement_strategy=ML.MeasurementStrategy.probs(
            computation_space=ML.ComputationSpace.FOCK
        ),
    )


def _bitstring_dist_from_layer_output(layer, out_flat, n):
    """Maps a MerLin QuantumLayer's flattened forward-pass output (indexed by
    layer.output_keys, plain mode-occupation tuples) into a
    {bitstring: probability} dict via fock_to_bitstring/_decode_single_qubit_pair
    (reused, unmodified, from iqp_photonic_encoding.py), plus the residual
    probability on out-of-subspace outcomes -- mirroring
    photonic_iqp_distribution's (dist, residual) return shape."""
    dist = {}
    residual = 0.0
    for key, val in zip(layer.output_keys, out_flat.tolist()):
        state = pcvl.BasicState(list(key))
        bits = fock_to_bitstring(state, n)
        if bits is None:
            residual += val
        else:
            dist[bits] = dist.get(bits, 0.0) + val
    return dist, residual


def dual_rail_photonic_iqp_distribution(n, thetas, eta=1.0):
    """Weight-1 dual-rail analogue of photonic_iqp_distribution: builds the
    dual-rail circuit for the given theta values, runs it through MerLin's
    QuantumLayer (native torch forward pass, not Perceval's own Analyzer),
    and returns (dist, residual) in the exact same shape as the polarization
    encoding's function -- {bitstring: probability}, residual float. Lost
    data photons produce invalid dual-rail pairs and are accumulated into
    residual rather than silently discarded."""
    assert len(thetas) == n
    layer = make_weight1_quantum_layer(n, eta=eta)
    with torch.no_grad():
        theta_tensor = dict(layer.named_parameters())["theta"]
        theta_tensor.copy_(torch.tensor(thetas, dtype=theta_tensor.dtype))
        out_flat = layer().flatten()
    return _bitstring_dist_from_layer_output(layer, out_flat, n)


# ---------------------------------------------------------------------------
# Weight-2 (v2.1 analogue)
# ---------------------------------------------------------------------------


def build_dual_rail_weight2_processor(n, i, j, thetas):
    """Full weight-2 dual-rail pipeline (v2.1 analogue of
    build_weight2_processor): state prep -> theta-folded diagonal layer ->
    CZ insertion (qubits i, j) -> conjugation. Reuses
    `_build_cz_insertion_core()` UNMODIFIED from iqp_photonic_encoding.py --
    it is already pure dual rail (no PBS inside it; the polarization
    encoding wraps it in PBS before/after, this module skips that wrap
    entirely since it starts and ends in dual rail already). No readout
    step needed (see build_dual_rail_full_circuit's docstring).

    Mode layout, identical in shape to build_weight2_processor: 2n+2 total
    modes. Modes 0..2n-1 are the normal per-qubit dual-rail pairs; modes
    2n, 2n+1 are the 2 tail ancilla modes _build_cz_insertion_core's local
    herald ports (4,5) need.

    Theta folding: additive +pi/4 on thetas[i]/thetas[j] only, identical
    convention to build_weight2_processor -- realizes the same
    exp(i*pi/4*Z_i*Z_j) = CZ . exp(i*pi/4*Z_i) . exp(i*pi/4*Z_j) operator
    identity documented in docs/iqp-photonic-encoding.md.

    Built via pcvl.Processor purely for its non-contiguous mode-mapping
    convenience (see module docstring), no heralds registered (this module
    never uses Processor.add_herald -- manual filtering happens in
    dual_rail_photonic_weight2_iqp_distribution instead). Returns
    (Processor(2n+2), herald_spec) -- herald_spec read from
    `_build_cz_insertion_core`'s own component (via HeraldedCzItem's
    build_experiment().in_heralds), NOT hardcoded, matching
    iqp_photonic_encoding.py's established pattern."""
    assert len(thetas) == n
    assert 0 <= i < n and 0 <= j < n and i != j

    thetas_folded = list(thetas)
    thetas_folded[i] += np.pi / 4
    thetas_folded[j] += np.pi / 4

    total_modes = 2 * n + 2
    proc = pcvl.Processor("SLOS", total_modes)

    proc.add(0, build_dual_rail_state_prep_circuit(n))
    proc.add(0, build_dual_rail_diagonal_layer_circuit(n, thetas_folded))

    cz_core = _build_cz_insertion_core()
    mapping = {
        2 * i: 0, 2 * i + 1: 1,
        2 * j: 2, 2 * j + 1: 3,
        2 * n: 4, 2 * n + 1: 5,
    }
    proc.add(mapping, cz_core)

    proc.add(0, build_dual_rail_conjugation_circuit(n))

    from perceval.components.core_catalog.heralded_cz import HeraldedCzItem
    herald_spec = HeraldedCzItem().build_experiment().in_heralds
    return proc, herald_spec


def dual_rail_weight2_input_state(n):
    """All-'0' data qubits ([0,1] per pair, matching dual_rail_all_zero_input)
    PLUS [1,1] ancilla -- heralded_cz's own native ancilla input convention
    (confirmed from heralded_cz_derisking.py: plain, unannotated 1-photon
    input on each herald mode; no polarization annotation needed here since
    this module never touches polarization at all)."""
    return pcvl.BasicState([0, 1] * n + [1, 1])


def make_weight2_circuit_and_input(n, i, j):
    """Symbolic (unbound) weight-2 dual-rail circuit for qubits i,j, flattened
    from a Processor via linear_circuit() (verified to preserve named,
    unbound Parameters, not bake in numeric values). Returns
    (flat_circuit, input_state, herald_spec)."""
    params = [pcvl.Parameter(f"theta{k}") for k in range(n)]
    assert 0 <= i < n and 0 <= j < n and i != j
    total_modes = 2 * n + 2
    proc = pcvl.Processor("SLOS", total_modes)
    proc.add(0, build_dual_rail_state_prep_circuit(n))

    # Additive +pi/4 fold on qubits i, j: NOT Perceval parameter arithmetic
    # (params[k] + np.pi/4) -- that creates a derived expression-Parameter
    # whose auto-generated name (e.g. "(theta0 + 0.785...)") MerLin's
    # trainable-parameter name-mapping cannot resolve back to the original
    # trainable tensor (confirmed live: KeyError inside
    # merlin.pcvl_pytorch.locirc_to_tensor). Instead, two separate PS gates
    # in sequence on the same mode: a trainable PS(theta_k) (kept as a bare,
    # unmodified pcvl.Parameter -- MerLin-compatible) followed by a fixed,
    # non-parameterized PS(pi/4) for k in {i, j} only. Phase shifters on the
    # same mode compose additively (PS(a) then PS(b) == PS(a+b)), so this is
    # physically identical to the numeric fold, not an approximation.
    diag = pcvl.Circuit(2 * n)
    for k in range(n):
        diag.add(2 * k, pcvl.PS(params[k]))
        if k in (i, j):
            diag.add(2 * k, pcvl.PS(np.pi / 4))
    proc.add(0, diag)

    cz_core = _build_cz_insertion_core()
    mapping = {
        2 * i: 0, 2 * i + 1: 1,
        2 * j: 2, 2 * j + 1: 3,
        2 * n: 4, 2 * n + 1: 5,
    }
    proc.add(mapping, cz_core)
    proc.add(0, build_dual_rail_conjugation_circuit(n))

    flat = proc.linear_circuit()

    from perceval.components.core_catalog.heralded_cz import HeraldedCzItem
    herald_spec = HeraldedCzItem().build_experiment().in_heralds

    return flat, dual_rail_weight2_input_state(n), herald_spec


def make_weight2_quantum_layer(n, i, j, eta=1.0):
    """Factory for a MerLin QuantumLayer wrapping the full weight-2 dual-rail
    circuit (qubits i, j coupled via the CZ-insertion core) for n qubits.
    Returns (layer, herald_spec).

    Explicit ComputationSpace.FOCK (not MerLin's UNBUNCHED default) is
    REQUIRED here, not just a style choice: heralded_cz's internal
    Hong-Ou-Mandel-type interference genuinely produces bunched
    intermediate/output configurations on the ancilla modes as part of its
    real physics. MerLin's default UNBUNCHED computation space silently
    drops all such states -- confirmed live: with the default, this
    function's herald_failure_prob came out as ~0.194 instead of the
    correct ~0.9259 (Phase 10's independently-established 2/27 success
    rate, reproduced exactly by bare Perceval on this identical circuit).
    FOCK fixes this by enumerating the true, unrestricted n+2-photon Fock
    space (792 states at n=3, vs UNBUNCHED's silently-wrong 56).

    ``eta`` is applied uniformly to every data and ancilla mode. Manual
    herald filtering must therefore happen after the layer forward pass so
    lost herald photons contribute to herald failure.
    """
    eta = _validate_eta(eta)
    circuit, input_state, herald_spec = make_weight2_circuit_and_input(n, i, j)
    layer = ML.QuantumLayer(
        circuit=circuit,
        input_state=input_state,
        trainable_parameters=["theta"],
        noise=pcvl.NoiseModel(transmittance=eta),
        measurement_strategy=ML.MeasurementStrategy.probs(
            computation_space=ML.ComputationSpace.FOCK
        ),
    )
    return layer, herald_spec


def dual_rail_photonic_weight2_iqp_distribution(n, i, j, thetas, eta=1.0):
    """Weight-2 dual-rail analogue of photonic_weight2_iqp_distribution:
    builds the dual-rail weight-2 circuit for the given theta values, runs it
    through MerLin's QuantumLayer, and manually filters/renormalizes on the
    2 tail ancilla modes matching herald_spec (see module docstring for why
    this sidesteps MerLin's "no heralding in experiment=" restriction).
    Returns (dist, residual, herald_failure_prob) -- identical 3-tuple shape
    to photonic_weight2_iqp_distribution. Photon loss is applied before this
    manual classification, so data loss becomes residual when the herald
    succeeds and ancilla loss compounds with the gate's intrinsic herald
    failure probability."""
    assert len(thetas) == n
    layer, herald_spec = make_weight2_quantum_layer(n, i, j, eta=eta)
    with torch.no_grad():
        theta_tensor = dict(layer.named_parameters())["theta"]
        theta_tensor.copy_(torch.tensor(thetas, dtype=theta_tensor.dtype))
        out_flat = layer().flatten()

    ancilla_a, ancilla_b = 2 * n, 2 * n + 1
    expected_a, expected_b = herald_spec[4], herald_spec[5]

    dist = {}
    residual = 0.0
    herald_failure_prob = 0.0
    for key, val in zip(layer.output_keys, out_flat.tolist()):
        if key[ancilla_a] != expected_a or key[ancilla_b] != expected_b:
            herald_failure_prob += val
            continue
        state = pcvl.BasicState(list(key))
        bits = fock_to_bitstring(state, n)
        if bits is None:
            residual += val
        else:
            dist[bits] = dist.get(bits, 0.0) + val

    herald_success_prob = 1.0 - herald_failure_prob
    if herald_success_prob > 0:
        dist = {k: v / herald_success_prob for k, v in dist.items()}
        residual = residual / herald_success_prob

    return dist, residual, herald_failure_prob


# ---------------------------------------------------------------------------
# ARB-01 tunable weight-2 CP(alpha) (v3.0 Phases 15-16 analogue)
# ---------------------------------------------------------------------------


def dual_rail_weight2_cp_input_state(n):
    """All-'0' data qubits ([0,1] per pair) PLUS [0,0,0,0] ancilla -- CP's
    post-selection-on-vacuum convention (NOT heralded_cz's [1,1] photon
    input), matching _weight2_cp_input_state's polarization-side logic but
    without any polarization annotation (a genuinely-vacuum mode needs
    none)."""
    return pcvl.BasicState([0, 1] * n + [0, 0, 0, 0])


def make_weight2_cp_circuit_and_input(n, i, j, alpha):
    """Symbolic (unbound in theta, fixed in alpha) weight-2 CP(alpha)
    dual-rail circuit for qubits i, j, flattened from a Processor via
    linear_circuit(). alpha is baked in as a plain float at construction
    time (matching _build_cp_insertion_core's own isinstance(float) contract
    -- it cannot be a late-bound pcvl.Parameter), exactly mirroring
    iqp_photonic_encoding.py's own convention of rebuilding the circuit per
    alpha value for a sweep, never optimizing alpha via gradient descent
    (ARB-04's success-probability-vs-alpha table is a sweep over discrete
    alpha values, not a differentiable alpha).

    Theta folding: +alpha/4 on thetas[i]/thetas[j] via a SEPARATE, fixed,
    non-parameterized PS(alpha/4) gate (not Perceval parameter arithmetic --
    see build_dual_rail_weight2_processor's docstring for why arithmetic on
    a pcvl.Parameter breaks MerLin's trainable-tensor name-mapping), per the
    ARB-01/ARB-02 identity exp(i*theta*Z_i*Z_j) = e^{-i*theta} * CP(4*theta)
    * exp(i*theta*Z_i) * exp(i*theta*Z_j), theta=alpha/4.

    Returns (flat_circuit, input_state, ancilla_spec)."""
    alpha = float(alpha)  # cast at every call site, matching this repo's established discipline
    theta_fold = alpha / 4.0

    assert 0 <= i < n and 0 <= j < n and i != j
    params = [pcvl.Parameter(f"theta{k}") for k in range(n)]

    total_modes = 2 * n + 4
    proc = pcvl.Processor("SLOS", total_modes)
    proc.add(0, build_dual_rail_state_prep_circuit(n))

    diag = pcvl.Circuit(2 * n)
    for k in range(n):
        diag.add(2 * k, pcvl.PS(params[k]))
        if k in (i, j):
            diag.add(2 * k, pcvl.PS(theta_fold))
    proc.add(0, diag)

    cp_core = _build_cp_insertion_core(alpha)
    mapping = {
        2 * i: 0, 2 * i + 1: 1,
        2 * j: 2, 2 * j + 1: 3,
        2 * n: 4, 2 * n + 1: 5,
        2 * n + 2: 6, 2 * n + 3: 7,
    }
    proc.add(mapping, cp_core)
    proc.add(0, build_dual_rail_conjugation_circuit(n))

    flat = proc.linear_circuit()

    from perceval.components.core_catalog.controlled_rotation_gates import (
        PostProcessedControlledRotationsItem,
    )
    ancilla_spec = PostProcessedControlledRotationsItem().build_experiment(
        n=2, alpha=alpha
    ).in_heralds
    assert ancilla_spec == {4: 0, 5: 0, 6: 0, 7: 0}, (
        f"PostProcessedControlledRotationsItem's ancilla layout changed: {ancilla_spec} "
        "-- this function hardcodes local ports 4-7, all expecting count 0"
    )

    return flat, dual_rail_weight2_cp_input_state(n), ancilla_spec


def make_weight2_cp_quantum_layer(n, i, j, alpha):
    """Factory for a MerLin QuantumLayer wrapping the full weight-2 CP(alpha)
    dual-rail circuit (qubits i, j) for n qubits, at a fixed alpha. Returns
    (layer, ancilla_spec).

    ComputationSpace.FOCK (not UNBUNCHED) for the same reason as
    make_weight2_quantum_layer: CP's post-selection mechanism, like
    heralded_cz's heralding, relies on genuine multi-photon interference
    that can populate bunched configurations -- confirmed necessary here too
    (see test_weight2_cp_requires_fock_not_unbunched)."""
    circuit, input_state, ancilla_spec = make_weight2_cp_circuit_and_input(n, i, j, alpha)
    layer = ML.QuantumLayer(
        circuit=circuit,
        input_state=input_state,
        trainable_parameters=["theta"],
        measurement_strategy=ML.MeasurementStrategy.probs(
            computation_space=ML.ComputationSpace.FOCK
        ),
    )
    return layer, ancilla_spec


def dual_rail_photonic_cp_iqp_distribution(n, i, j, thetas, alpha):
    """Weight-2 CP(alpha) dual-rail analogue of photonic_cp_iqp_distribution:
    builds the dual-rail CP(alpha) circuit for the given theta values, runs
    it through MerLin's QuantumLayer, and applies the SAME three-step manual
    filter as the polarization version (reused logic, not re-derived):
      1. any nonzero ancilla mode (2n..2n+3) -> postselect_failure_prob
      2. otherwise, qubit i's or j's own pair out-of-subspace ->
         ALSO postselect_failure_prob (CP's own post-selection condition
         covers both ancilla vacuum AND pair-i/pair-j validity together --
         folding this into residual instead reproduces the exact TVD~0.3-0.4
         bug iqp_photonic_encoding.py's own history already hit and fixed;
         see photonic_cp_iqp_distribution's docstring for the full account)
      3. otherwise, any other bystander qubit out-of-subspace -> residual;
         everything else -> dist

    Returns (dist, residual, postselect_failure_prob) -- identical 3-tuple
    shape to photonic_cp_iqp_distribution."""
    assert len(thetas) == n
    layer, ancilla_spec = make_weight2_cp_quantum_layer(n, i, j, alpha)
    with torch.no_grad():
        theta_tensor = dict(layer.named_parameters())["theta"]
        theta_tensor.copy_(torch.tensor(thetas, dtype=theta_tensor.dtype))
        out_flat = layer().flatten()

    ancilla_modes = [2 * n, 2 * n + 1, 2 * n + 2, 2 * n + 3]

    dist = {}
    residual = 0.0
    postselect_failure_prob = 0.0
    for key, val in zip(layer.output_keys, out_flat.tolist()):
        if any(key[m] != 0 for m in ancilla_modes):
            postselect_failure_prob += val
            continue

        state = pcvl.BasicState(list(key))
        bit_i = _decode_single_qubit_pair(state, i)
        bit_j = _decode_single_qubit_pair(state, j)
        if bit_i is None or bit_j is None:
            postselect_failure_prob += val
            continue

        bits = []
        bystander_invalid = False
        for k in range(n):
            if k == i:
                bits.append(bit_i)
            elif k == j:
                bits.append(bit_j)
            else:
                b = _decode_single_qubit_pair(state, k)
                if b is None:
                    bystander_invalid = True
                    break
                bits.append(b)

        if bystander_invalid:
            residual += val
        else:
            key_str = "".join(bits)
            dist[key_str] = dist.get(key_str, 0.0) + val

    postselect_success_prob = 1.0 - postselect_failure_prob
    if postselect_success_prob > 0:
        dist = {k: v / postselect_success_prob for k, v in dist.items()}
        residual = residual / postselect_success_prob

    return dist, residual, postselect_failure_prob
