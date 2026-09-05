# v4.0 Plan: Train Classically, Deploy Photonically (TCDP)

**Status:** revision 2, 2026-09-03, after a Codex adversarial read (`.planning/research/v4-plan-codex-review.md`, disposition in `v4-plan-codex-review-disposition.md`). Not started.
**Executor:** Codex (gpt-5.5) for every task marked MECH; Sonnet for prose tasks; Fable or Opus for the two review gates. The owner runs every task marked OWNER personally.
**Rule of the milestone:** every measurement has a null result written as a failing test before the sweep runs (`CLAUDE.md`, "Null-result gate"). A sweep whose numbers match its null is a pipeline check, not a finding.
**Rule for the executor:** no tolerance, grid value, seed count, threshold, or formula in this document may be changed by the executor. A failing check is reported with the measured number. Anything this document does not specify is a stop-and-ask, not a judgment call.

---

## 0. The question, and why it is open

**Question.** An IQP Born machine is trained entirely classically (Van den Nest's cosine formula, the spring-semester `iqp-mmd-barren-plateau` methodology). The trained parameters are deployed on a photonic device: dual-rail photons, post-selected `CP(alpha)` gates for every ZZ term, realistic loss, partial distinguishability, and multi-photon emission. **How far is the device's post-selected output from the distribution the classical trainer thinks it deployed, as a function of gate count, system size, and the three noise parameters; what does a usable sample cost; and does training against the device's gate maps instead of the ideal gate close the gap?**

**Why it is open, stated at the strength the evidence supports.** In the four works reviewed for this plan and the 2026-09-03 literature searches (queries recorded in `docs/iqp-lit-scoping.md`'s addendum), no study deploys a classically trained IQP model through a photonic gate-noise model. Recio-Armengol, Ahmed, Bowles (arXiv:2503.02934) study qubit IQP deployment and do not study a photonic noise model. Raj, Mathur, Perdomo-Ortiz (arXiv:2608.31117, full text) evaluate the objective by state-vector simulation up to 30 qubits and define the coverage, fidelity, and forward-KL metrics used here. Salavrakos et al. (Quandela, arXiv:2405.02277) run a photonic Born machine on hardware with loss mitigation; whether its training route or circuit class overlaps this one is checked by a full read in Phase 32 before the write-up relies on it. The v3.1 closed forms settle the loss axis: conditioned on full detection the output is unchanged and throughput pays. The open axes are distinguishability and g2, which act inside the two-photon gates and are the parameters Quandela's roadmap tracks ("distinguishability 70% -> 99%").

**Verified facts this plan builds on (2026-09-03; do not re-derive):**

| Fact | Evidence |
|---|---|
| The sibling trainer's `theta` equals this repo's `thetas` / `pair_thetas` exactly, weight-1 and ZZ; scale 0.5 and 2 fail | Walsh-inverse of `iqp_expectation_exact` vs `exact_qubit_iqp_distribution`, n=3, error 0.0 |
| Sibling core (`iqp/expectation.py`, `mmd/{kernel,loss,gradients,mixture}.py`, `rng.py`) imports with numpy only | import scan; `mmd2_exact_small_n` ran in this venv |
| Perceval 1.2.4 `NoiseModel(indistinguishability, g2, transmittance)` acts on plain dual-rail `Processor`s | HOM dip 0.5 -> 0.25 -> 0 at V = 1, 0.5, 0 |
| **Direct reconstruction** of the post-selected CP gate as a trace-decreasing CP map from absolute Perceval probabilities (section 4.2) is exact: max error 5e-16 vs `(1/9) U rho U^dag` at alpha = pi/3 and pi; Choi min eigenvalue -2e-15 at V = 0.9; 2.3 s per gate | probe recorded in `.planning/research/v4-plan-codex-review-disposition.md` |
| Gate success probability is **input-dependent** under noise: 0.1111 to 0.1222 across 16 product inputs at V = 0.9. Per-gate renormalisation is therefore wrong; maps must be composed unnormalised and normalised once at the end | same probe |
| Perceval `ProcessTomography` on the bare catalog gate: average fidelity 1.0 ideal, 0.9707 at V = 0.9; the direct reconstruction's mean conditional fidelity at V = 0.9 is 0.9703 | probe |
| The PERM-adapted `_build_cp_insertion_core` gives fidelity 0.65 under tomography: reconstruct the **bare** catalog gate, never the adapted core | probe |
| Perceval dual-rail logical convention inside the bare gate: mode pattern (1,0) = logical 0, (0,1) = logical 1 | tomography fidelity 1.0 with the phase on the 11 state |
| Post-selected `probs()` under `NoiseModel` requires `min_detected_photons_filter(2)` | probe |
| Loss on a CP gate costs `eta` per data photon only (vacuum ancilla). Heralded CZ costs `eta^2` extra per gate. v3.1's `eta^(n+2k)` table is heralded-CZ only | `_build_cp_insertion_core` docstring; v3.1 hardness doc |
| Perceval SLOS is deterministic exact-arithmetic simulation: two reconstructions of the same key differ only by floating-point noise | probe fit residual 3e-16 |

**Hardware anchors** (cite, do not invent):

| Source | V | g2(0) | end-to-end transmission |
|---|---|---|---|
| Ascella, Maring et al. Nat. Photon. 2024, arXiv:2306.00874 (full text) | 0.930 (M_s 0.944 corrected) | 7.3e-3 | ~8% |
| Altair, Salavrakos et al. PRA 2025, arXiv:2405.02277 | 0.84 | 0.025 (purity) | loss ~0.96 |
| Quandela roadmap 2026-2033 | 70% -> 99% target | | |

---

## 1. Scope

### Must
- M1. Vendored classical trainer inside `merlin_iqp`, convention-tested against the repo's exact reference.
- M2. Gate-map deployment simulator: one directly reconstructed trace-decreasing map per CP gate, composed on an n-qubit density matrix, normalised once at the end; cross-checked against full-Fock Perceval at n = 2, 3 including the shared-qubit two-gate case.
- M3. The TCDP gap sweep on a 1D-chain IQP family at n in {4, 6, 8, 10}, noise grid anchored to Ascella and Altair, six exact metrics, every null written first, an ideal-map control point asserted in every cell.
- M4. Noise-aware classical training (NAT): train against the map-composed deployed distribution and measure whether the gap closes. Promoted to Must 2026-09-03 (owner decision). Stop rule in section 6.
- M5. Erasure-marked non-post-selected output (REFRAME-03).
- M6. Write-up, technical-findings mirror, README paragraph, owner checkpoints, two-stage review.

### Won't (write into `.planning/PROJECT.md` if tempted)
- A structured Fock-space simulator to n = 20. Not needed for this question.
- Any barren-plateau claim. The sibling project found init and n dominate; not re-litigated here.
- Graph-state / MBQC realization (audit direction 4). Separate milestone.
- Heralded CZ under distinguishability. CP(alpha) only.
- Recycling mitigation (Salavrakos). Different detector model and circuit class. Cite only.
- Analysis of the erasure-marked output. Audit direction 1, future milestone.
- New dependencies of any kind.

---

## 2. Repository layout the executor must produce

```
src/merlin_iqp/classical/            # M1, vendored from C:\Users\cuqui\iqp-mmd-barren-plateau\src\iqp_bp
    __init__.py
    PROVENANCE.md                    # sibling commit hash, copied files, removed jax/laplacian/polynomial paths
    expectation.py                   # iqp_phase, iqp_expectation, iqp_expectation_exact (verbatim)
    kernel.py                        # gaussian_* only
    mixture.py                       # DatasetParityCache, dataset_expectations_batch (verbatim)
    loss.py                          # mmd2, mmd2_exact_small_n (gaussian branch only)
    gradients.py                     # grad_expectation_analytic, grad_mmd2_analytic, estimate_gradient_variance; jax functions deleted
    rng.py                           # split_rng (verbatim)
    families.py                      # chain_1d (new), product_state, lattice (verbatim)
    initialization.py                # make_theta_with_metadata (verbatim)
    trainer.py                       # Trainer (verbatim)
    adapter.py                       # theta_to_repo, repo_to_theta (new)
    ising_chain.py                   # exact 1D Ising target (new, 3.3)
src/merlin_iqp/deploy/               # M2
    __init__.py
    gate_map.py                      # reconstruct_gate_map, GateMap, alpha_key, prep/read circuits
    density_matrix.py                # deploy_density_matrix
    fock_reference.py                # noisy_full_fock_distribution (n<=3 cross-check only)
    throughput.py                    # heralded_cz_throughput (overlay only)
    erasure.py                       # M5
    metrics.py                       # the six metrics, formulas in 5.4
tests/v4_tcdp/
    test_convention.py               # 3.4
    test_gate_map.py                 # 4.3
    test_density_matrix.py           # 4.4
    test_fock_crosscheck.py          # 4.5
    test_metrics.py                  # 5.4
    test_nulls_tcdp.py               # 5.2, owner-filled, red before the sweep
scripts/v4_tcdp/
    train_classical.py               # 5.3
    deploy_sweep.py                  # 5.5
    nat_train.py                     # 6
    tcdp_analysis.py                 # 5.6
results/v4_tcdp/
docs/tcdp-study.md
```

No file outside this list is modified except `docs/technical-findings.md`, `README.md`, `CLAUDE.md` (Repo state), `.planning/*`. `pyproject.toml` is not touched.

---

## 3. Phase 26 (MECH, Codex): vendor the classical trainer

### 3.1 Copy, strip, add `chain_1d`
1. Record `git -C C:\Users\cuqui\iqp-mmd-barren-plateau rev-parse HEAD` into `PROVENANCE.md`.
2. Copy the files listed in section 2 verbatim. Rewrite imports `iqp_bp.` -> `merlin_iqp.classical.`.
3. Delete from `gradients.py`: `grad_mmd2_autodiff_vector`, `grad_mmd2_autodiff`, `_jax_fixed_sample_value_and_grad`, every `import jax`. Delete `laplacian_*`, `polynomial_*`, `multi_scale_*` from `kernel.py` and their branches in `loss.py`, `gradients.py`.
4. Add to `families.py`:
   ```python
   def chain_1d(n: int, k: int) -> np.ndarray:
       """Rows 0..n-1: weight-1 generator on qubit r. Rows n..n+k-1: ZZ pairs (0,1),(1,2),...,(k-1,k).
       Requires 0 <= k <= n-1. Returns (n+k, n) uint8. Row order is part of the contract."""
   ```

### 3.2 `adapter.py`
```python
def theta_to_repo(G, theta) -> tuple[list[float], dict[tuple[int,int], float]]:
    """Weight-1 row on qubit r -> thetas[r]; weight-2 row on (i,j), i<j -> pair_thetas[(i,j)].
    Raises ValueError on any row of weight 0 or >= 3, on duplicate rows, or if any qubit lacks a weight-1 row."""
def repo_to_theta(n, thetas, pair_thetas) -> tuple[np.ndarray, np.ndarray]   # (G, theta) in chain_1d row order
```
No scaling, no sign change.

### 3.3 `ising_chain.py`
```python
def ising_chain_target(n: int) -> np.ndarray:
    """Exact 2^n vector, index = int(bitstring, 2) with qubit 0 the most significant bit.
    J = np.random.default_rng(4001).normal(size=19); use J[:n-1] (one common vector, prefixes per n).
    p(x) proportional to exp(sum_{i<n-1} J[i] * s_i * s_{i+1}), s_i = 1 - 2*x_i, beta = 1. Normalised by exact enumeration."""
def ising_chain_samples(n: int, m: int = 20000) -> np.ndarray:
    """(m, n) uint8 drawn by inverse CDF from ising_chain_target(n) with default_rng(4002).
    Used ONLY by the Monte-Carlo trainer at n in {16, 20}. Every metric and every exact-loss training run uses the vector."""
```

### 3.4 `tests/v4_tcdp/test_convention.py`
- `test_walsh_inverse_matches_exact_reference`: n in {2,3,4}, k in {0,1,n-1}, 5 draws: `p(x) = 2^-n sum_a <Z_a> (-1)^{a.x}` from `iqp_expectation_exact` vs `exact_qubit_iqp_distribution(n, *theta_to_repo(G, theta))`; max abs diff < 1e-12.
- `test_asymmetric_hand_fixture`: n = 3, thetas = (0.3, 0.0, 0.9), pair (0,2) theta 0.4. Expected probabilities are computed inside the test by an explicit 8-term amplitude sum written out by hand (not by calling either library), compared by named bitstring to both the Walsh reconstruction and `exact_qubit_iqp_distribution`. This is the test that catches a shared bit-order mistake.
- `test_scale_conventions_fail`: theta x 0.5 and theta x 2 exceed 1e-3.
- `test_no_jax_import`; `test_exact_loss_runs_n10` (< 60 s); `test_ising_target_normalised_and_prefix_consistent` (sum = 1; `J[:3]` identical between the n = 4 and n = 6 calls).

**Done when:** all green, full suite green, `PROVENANCE.md` present.

---

## 4. Phases 27-28 (MECH, Codex): gate maps and the deployment simulator

### 4.1 Design decision (recorded; not re-decided)
Full-Fock simulation of n qubits with k CP gates is infeasible past n ~ 5. Instead each gate is reconstructed once as a **trace-decreasing completely positive map** `Lambda_{alpha,V,g2}` on two qubits, and the n-qubit density matrix is evolved by composing these maps; the final state is normalised once, and its trace is the exact success probability of the composed post-selection. This is exact for post-selection applied at the end of the circuit, which is what the device does. The single approximation is that a photon's distinguishability is drawn independently in each gate it enters, whereas Perceval treats it as a property of the photon; 4.5 measures that error directly and the write-up carries it.

**Not** the earlier design: no per-gate renormalisation (success is input-dependent, 0.1111 to 0.1222 at V = 0.9), no chi-matrix Pauli-ordering inference. Perceval `ProcessTomography` is used only as an independent fidelity cross-check.

### 4.2 `gate_map.py`
```python
@dataclass(frozen=True)
class GateMap:
    alpha: float               # rounded key, in [0, 2pi)
    V: float
    g2: float
    superop: np.ndarray        # (16,16) complex; out_vec = superop @ rho.reshape(-1), ROW-MAJOR vec; trace-decreasing CP map
    choi_min_eig: float
    p_success_basis: np.ndarray  # (4,) success on the four computational inputs; reported only, never used for composition
    cond_fidelity_avg: float   # exact average fidelity of the normalised map vs diag(1,1,1,e^{i alpha}), from the Choi matrix
def reconstruct_gate_map(alpha: float, V: float, g2: float) -> GateMap
def alpha_key(alpha_raw: float) -> float:   # (round((alpha_raw mod 2pi) / 0.1) mod 63) * 0.1  -> exactly 63 keys
```
Construction, exactly as in the verified probe:
- Processor: `Processor("SLOS", 8, noise=NoiseModel(indistinguishability=V, g2=g2 or None))` (no `noise` argument when V = 1 and g2 = 0). Add `prep(ia)` on modes 0-1 and `prep(ib)` on modes 2-3; add the **bare** `PostProcessedControlledRotationsItem().build_circuit(n=2, alpha=float(alpha))` at mode 0; add `read(ra)` on 0-1 and `read(rb)` on 2-3; `add_herald(m, 0)` for m in 4..7; `set_postselection(PostSelect("[0,1]==1 & [2,3]==1"))`; `min_detected_photons_filter(2)`; input `BasicState([1,0,1,0])`.
- `prep(label)`: `"0"` identity; `"1"` `PERM([1,0])`; `"+"` `BS.H()` at 0; `"i"` `BS.H()` at 0 then `PS(pi/2)` at 1. `read(basis)`: `"Z"` identity; `"X"` `BS.H()` at 0; `"Y"` `PS(-pi/2)` at 1 then `BS.H()` at 0.
- Prep states and readout POVMs are **computed from the circuits' own unitaries** (`compute_unitary()`), never written by hand: `psi = U_prep[:, 0]`; `E_bit = R^dag |bit><bit| R`. Logical basis: mode pattern (1,0) = logical 0, (0,1) = logical 1.
- Absolute outcome probability = `results[state] * global_perf`. Linear inversion by least squares over 16 inputs x 9 readout pairs x observed outcomes; assert rank 256 and fit residual < 1e-12.
- Cache: `results/v4_tcdp/channels/{alpha:.1f}_{V}_{g2}.npz`. 63 x 18 = 1134 maps; measured 2.3 s each, about 45 minutes single-core. Loss (eta) is not a key: a lost data photon fails the pair post-selection, it does not change the conditional map.

### 4.3 `tests/v4_tcdp/test_gate_map.py`
- `test_ideal_map_exact`: V = 1, g2 = 0, alpha in {pi/6, pi/3, pi, 2.0}: `superop @ vec(rho)` equals `(1/sigma_max(alpha)^4) * U rho U^dag` to 1e-9 for 5 random pure rho (the trace is the closed-form success probability from `iqp_photonic`; the phase sits on the 11 state).
- `test_completely_positive`: every cached map has Choi min eigenvalue > -1e-9.
- `test_trace_non_increasing_all_units`: the map is Hermiticity-preserving on all 16 matrix units, and for the 16 product inputs the output trace is in (0, 1].
- `test_success_input_dependence_recorded`: at V = 0.9, alpha = pi/3, the basis successes differ by more than 1e-4 (documents why per-gate renormalisation would be wrong).
- `test_repeatable`: two reconstructions of the same key agree to 1e-13.
- `test_tomography_crosscheck`: `ProcessTomography(...).average_fidelity(U)` on the same bare gate agrees with `cond_fidelity_avg` within 5e-3 at (V, g2) in {(1, 0), (0.9, 0), (0.93, 0.007)}. The discrepancy is recorded, not hidden: Perceval's figure averages differently over an input-dependent success.
- `test_alpha_key`: 63 distinct keys over 10 000 random `alpha_raw` in [-10, 10]; `alpha_key(2*pi - 0.01) == 0.0`.
- `test_reconstruction_wall_clock`: writes seconds per map to `results/v4_tcdp/map_timing.json`, measured at the slowest condition (V = 0.84, g2 = 0.025). If 1134 x that exceeds 3 hours single-core, stop and report.

### 4.4 `density_matrix.py`
```python
def deploy_density_matrix(n, thetas, pair_thetas, gate_maps: dict[tuple[int,int], GateMap]) -> tuple[np.ndarray, float]:
    """Returns (probs over 2^n, p_success). rho = |+><+|^n as a (2,)*2n tensor; apply exp(i thetas[r] Z_r) exactly;
    for each (i,j) in pair_thetas IN ASCENDING ORDER OF (i,j): apply exp(i th Z_i) exp(i th Z_j) exactly then gate_maps[(i,j)]
    (raises unless gate_maps[(i,j)].alpha == alpha_key(4*th)); apply H^n; p_success = real trace;
    probs = diag / p_success. Two-qubit maps are applied by einsum on the tensor; a 4^n x 4^n matrix is never formed."""
```
Bit order: index = `int(bitstring, 2)`, qubit 0 most significant, matching `exact_qubit_iqp_distribution`. n <= 10; `test_peak_memory_n10` asserts peak RSS growth under 400 MB and records seconds per call at n = 8 into `results/v4_tcdp/deploy_timing.json`.

`tests/v4_tcdp/test_density_matrix.py`:
- `test_ideal_maps_reproduce_exact_reference`: n in {2,3,4}, k in {0,1,n-1}, ideal maps: probs vs `exact_qubit_iqp_distribution` < 1e-12 and `p_success` equals the product of `1/sigma_max^4` to 1e-9. (Phase 28 null.)
- `test_k0_ignores_maps`: n = 4, k = 0, noisy maps passed: probs unchanged, `p_success == 1`.
- `test_asymmetric_hand_fixture_deployed`: the n = 3 fixture of 3.4 through `deploy_density_matrix` with ideal maps, compared by named bitstring.
- `test_alpha_mismatch_raises`; `test_no_4n_matrix_allocated` (monkeypatch `np.zeros`/`np.empty` to fail on shape `(4**n, 4**n)` for n = 6).

### 4.5 `fock_reference.py` and `tests/v4_tcdp/test_fock_crosscheck.py` (the trust gate)
`noisy_full_fock_distribution(n, thetas, pair_thetas, V, g2) -> (probs, p_success)` for n <= 3. Layout: qubit q on modes (2q, 2q+1), Perceval dual-rail convention (logical 0 = photon in mode 2q). State prep `BS.H()` on each pair; diagonal layer `PS(2*theta)` on mode 2q+1 (equivalent to `exp(i theta Z)` up to global phase); for pair (i,j) with theta_ij: `PS(2*theta_ij)` on modes 2i+1 and 2j+1 then the bare CP gate with `alpha = 4*theta_ij` via `Processor.add({2i: 0, 2i+1: 1, 2j: 2, 2j+1: 3, a: 4, a+1: 5, a+2: 6, a+3: 7}, gate)` where `a = 2n + 4*g` for the g-th gate (g = 0, 1, ...); conjugation `BS.H()` on each pair; heralds `add_herald(m, 0)` on every ancilla mode; `set_postselection` requiring `[2q, 2q+1] == 1` for every q; `min_detected_photons_filter(n)`; `probs = results * global_perf` mapped to bitstrings by which mode of each pair holds the photon; `p_success = sum(probs)`; return normalised probs and `p_success`. **These tests choose theta_pair on the grid `alpha_key/4` so the reference's unrounded alpha equals the map's key.**

Tests (all compare `deploy_density_matrix` to this reference):
- `test_single_gate_n2`: pair (0,1); V in {1, 0.9, 0.7} x g2 in {0, 0.02}: TVD < 1e-9 **and** `p_success` agrees to 1e-9. (The composed trace equals the full-Fock success: this retires the "product of mean success" approximation.)
- `test_single_gate_n3_bystander_V_only` and `test_single_gate_n3_bystander_g2_only`: pair (1,2), bystander 0: TVD < 1e-9. If g2-only fails while V-only passes, multi-photon emission leaks into bystander modes: g2 becomes a "gate-local approximation" column with the measured n = 3 discrepancy as its error bar, V carries the headline, and the executor stops to report both numbers.
- `test_two_gates_shared_qubit_n3`: pairs (0,1), (1,2); (V, g2) in {(0.9, 0), (1, 0.02), (0.93, 0.007)}; theta_pair in {pi/12, 0.5}: record every TVD and success-probability discrepancy into `results/v4_tcdp/crosscheck_shared_qubit.json`. Pre-registered interpretation: max TVD < 0.01, reported as the error bar on every figure; 0.01 to 0.05, every figure additionally carries the full-Fock n = 3 points as an overlay and the write-up leads with the discrepancy; > 0.05, the method fails for this milestone and the executor stops.

### 4.6 `throughput.py`
```python
def heralded_cz_throughput(n, k, eta) -> float:   # 1 / (eta**(n+2*k) * (2/27)**k), v3.1's closed form, Fig 4 overlay only
```
CP-gate throughput is `1 / (eta**n * p_success)` with `p_success` the composed trace from `deploy_density_matrix`; no function multiplies per-gate means.

### 4.7 `erasure.py` (M5)
```python
def erasure_marked_distribution(q_conditional, n, eta, gates: list[tuple[int,int]]) -> tuple[dict[str,float], float]:
    """Keys are strings over {0,1,E}. A qubit that appears in any gate cannot be erased: loss there fails that gate's
    post-selection, and that mass is returned as `dropped`. A qubit in no gate is erased independently w.p. 1-eta.
    Exact per-pattern formula: for x with conditional prob q(x), every subset S of the free qubits gives
    pattern (x with S -> E) with mass q(x) * eta^(n_gate) * eta^(n_free - |S|) * (1-eta)^|S|, summed over x;
    dropped = 1 - eta^(n_gate)."""
```
Tests: exact per-pattern values against a hand-enumerated case for k = 0 (n = 2), one gate (n = 3, pair (0,1)), and the shared-qubit case (n = 3, pairs (0,1),(1,2): no free qubit); mass + dropped = 1 to 1e-12; eta = 1 reproduces `q_conditional`.

---

## 5. Phases 29-30: nulls, training, and the deployment gap sweep

### 5.1 Fixed experimental design

| Axis | Values | Reason |
|---|---|---|
| Circuit family | `chain_1d(n, k)` | gate count = k; nearest-neighbour connectivity |
| n (deployable) | 4, 6, 8, 10 | density-matrix budget |
| n (training only) | 16, 20 | shows the classical side scales; no deployment |
| k | 0 .. n-1 | k = 0 is the null; gap vs k is the primary curve |
| Target | `ising_chain_target(n)` (3.3); samples only for n in {16, 20} | structured low-order correlations |
| Kernel | Gaussian on Hamming distance; sigma = 0.5 * sqrt(n) (primary) and sigma = 1.0 (control) | Rudolph et al.: bandwidth in Theta(sqrt n) keeps the loss low-bodied |
| Loss | exact (`mmd2_exact_small_n`) for n <= 10; MC (`num_a_samples` 512, `num_z_samples` 2048) for n in {16, 20} | |
| Init | `data_dependent` (primary), `small_angle` std 0.1, `uniform` | sibling's three schemes |
| Optimizer | Adam, lr 0.05, 300 steps, checkpoint every 50 | sibling defaults |
| Seeds | 5 per cell, `derive_seed("tcdp", n, k, kernel, init, seed_idx)` via `trainability/rng.py` | |
| Map noise grid | V in {1.0, 0.99, 0.95, 0.93, 0.84, 0.70} x g2 in {0, 0.007, 0.025} = 18 points; (1.0, 0) is the **control point** and is asserted, not just recorded | Ascella, Altair, roadmap anchors |
| Loss (eta) | {1.0, 0.9, 0.5, 0.08}, post hoc, as throughput columns | eta does not change the conditional map |
| Gate angle | `alpha_key(4 * theta_pair_trained)`; `theta_eff = alpha_key / 4` is deployed; the ideal reference uses the trained theta | ARB-01 identity |

Cell counts: deployable circuits 4 + 6 + 8 + 10 = 28 (n, k) pairs; x 2 kernels x 3 inits x 5 seeds = **840 trained cells**; x 18 map points = **15 120 rows** in `deploy_sweep.csv`. Training-only cells: 2 n x 2 kernels x 3 inits x 5 seeds = 60; 900 trained files in total. Maps: 1134, precomputed by `deploy_sweep.py --build-maps` before any row is written.

### 5.2 `tests/v4_tcdp/test_nulls_tcdp.py` (OWNER; written red before `deploy_sweep.py` runs)
Owner-filled functions (Claude asks and points at rows; does not supply formulas):
- `owner_null_gap_k0(V, g2)`: predicted `tvd_ideal_deployed` at k = 0.
- `owner_null_gap_noiseless(k)`: predicted gap at the control point (1.0, 0) for any k.
- `owner_null_eta_effect(n, k, eta)`: predicted change in the conditional distribution from eta alone.
- `owner_null_throughput_cp(n, alphas, eta)` and `owner_null_throughput_hcz(n, k, eta)`: both closed forms.
- `owner_null_nat_ideal()`: what NAT does when every gate map is ideal (predicted before/after gap, and the relation between the NAT-trained and ideal-trained theta).
- `owner_hypothesis_gap_scaling(k, F)`: first-order hypothesis for TVD vs k; `xfail(strict=False)`.
Pipeline nulls (Codex may write these; they are checks, not findings):
- `test_control_point_every_cell`: at (V, g2) = (1.0, 0), for every trained cell, `tvd_ideal_deployed == 0` (1e-12), `mmd2_train_deployed == mmd2_train_ideal`, both KL columns equal, `coverage_deployed == coverage_ideal`, `fidelity_deployed == fidelity_ideal`, `marginal_err_*_deployed == *_ideal`, `mean_gate_fidelity == 1`, `p_success` equals the product of closed-form successes. Run inside `deploy_sweep.py` as an assertion on the control rows, and standalone on three cells.
- `test_control_point_can_fail`: perturb `q_dep` by 1e-3 on one entry; every equality above must fail.

### 5.3 `scripts/v4_tcdp/train_classical.py` (MECH)
Trains every cell; writes `results/v4_tcdp/trained/{n}_{k}_{kernel}_{init}_{seed}.npz` with `G, theta, loss_trajectory, metadata, q_ideal` (n <= 10). Deterministic: re-running produces byte-identical `theta`.

### 5.4 `metrics.py` (formulas are the contract; `test_metrics.py` checks each on a hand case)
All distributions are exact 2^n vectors. `p` = `ising_chain_target(n)`. `S = {x : p(x) > 1e-6}` (support set). `Q = 20000`.
- `tvd(a, b) = 0.5 * sum |a - b|`.
- `mmd2_train(q)`: computed **from the vectors**: `sum_a w_a (<Z_a>_p - <Z_a>_q)^2` with the training kernel's spectral weights (`spectral_weights_exact`) and Walsh transforms of `p` and `q`. The same number the exact trainer minimises.
- `kl_target(q) = sum_x p(x) log(p(x) / max(q(x), floor))`, reported at `floor = 1e-12` and `floor = 1e-9` as two columns.
- `coverage_pop(q) = (1/|S|) * sum_{x in S} (1 - (1 - q(x))^Q)`: expected fraction of the support seen in Q samples. Population analogue of Raj et al.'s sample coverage; there is no train/unseen split because the target is an exact vector, and this deviation is stated in the write-up.
- `fidelity_pop(q) = sum_{x in S} q(x)`: expected fraction of samples that are valid.
- `marginal_err_k(q, p)`: mean over all subsets T of size k (k = 1, 2) of `tvd(q_T, p_T)`.
Each metric is computed for `q_ideal(theta_trained)` and `q_dep(theta_eff)`; the ideal/deployed pair is the comparison, the absolute value is against the target. Also `tvd_rounding_only = tvd(q_ideal(theta_eff), q_ideal(theta_trained))`, so alpha rounding is separated from noise in every cell; a cell where `tvd_rounding_only > 0.1 * tvd_ideal_deployed` is flagged in a `rounding_flag` column.

### 5.5 `scripts/v4_tcdp/deploy_sweep.py` (MECH)
CSV columns, in this order: `n,k,kernel,init,seed,V,g2,alpha_trained_list,alpha_rounded_list,theta_eff_list,tvd_ideal_deployed,tvd_rounding_only,rounding_flag,mmd2_train_ideal,mmd2_train_deployed,kl12_target_ideal,kl12_target_deployed,kl9_target_ideal,kl9_target_deployed,coverage_ideal,coverage_deployed,fidelity_ideal,fidelity_deployed,marginal_err_k1_ideal,marginal_err_k1_deployed,marginal_err_k2_ideal,marginal_err_k2_deployed,mean_gate_fidelity,p_success,throughput_eta1.0,throughput_eta0.9,throughput_eta0.5,throughput_eta0.08`. List columns are `;`-joined floats. One row per (trained cell, V, g2). Erasure distributions are not in the CSV: `deploy_sweep.py --erasure` writes `results/v4_tcdp/erasure/{n}_{k}_{seed}_ascella.npz` for n <= 6, k in {0, 1, n-1}, primary kernel, data_dependent init, at the four eta values.

### 5.6 `scripts/v4_tcdp/tcdp_analysis.py` (MECH) and figures
Aggregation for every figure: primary kernel, `data_dependent` init, mean and std over the 5 seeds at fixed (n, k, V, g2). Other kernel/init combinations appear only in an appendix table with the same aggregation.
- Fig 1: `tvd_ideal_deployed` vs k, one panel per n, one line per V at g2 = 0; the control line (V = 1) is drawn and is zero.
- Fig 2: `tvd_ideal_deployed` vs `(1 - mean_gate_fidelity) * k`, all (n, k, V, g2), with the owner's hypothesis line and the (0, 0) control cluster.
- Fig 3: coverage and KL (floor 1e-12), ideal vs deployed, at the Ascella and Altair points, vs k, one panel per n.
- Fig 4: CP throughput `1/(eta^n p_success)` vs (n, k) at the four eta values, with `heralded_cz_throughput` overlaid.
- Table: the pre-registered headline numbers: at n = 10, k = 9, Ascella point, median over seeds of `tvd_ideal_deployed`, `coverage_deployed / coverage_ideal`, `kl12_target_deployed - kl12_target_ideal`. The two headline outcomes (pre-registered, descriptive, not tests): median TVD <= 0.02 reads "classically trained IQP survives Ascella-grade deployment through k = 9"; median TVD >= 0.1 reads "distinguishability is the deployment ceiling and the gate count where it bites is [first k with median TVD > 0.1]"; in between, the write-up reports the curve without a slogan.

### 5.7 What would make this a finding rather than a pipeline check
Only rows that differ from the nulls of 5.2: nonzero gap at k >= 1 under V < 1 or g2 > 0, its dependence on k and n, and whether the hypothesis line fits. The write-up states, per null, matched or not.

---

## 6. Phase 31 (M4): noise-aware classical training (NAT)
Design (fixed):
- Cells: n in {4, 6, 8}, k = n - 1, primary kernel, `data_dependent` init, the 5 Phase-30 seeds. Noise: Ascella (V = 0.93, g2 = 0.007). Maps: all 63 alphas at the Ascella point, precomputed (part of the 1134).
- Objective: `mmd2_train(q_dep(theta))` with `q_dep` from `deploy_density_matrix` using `theta_eff = alpha_key(4 theta_pair) / 4` inside; the weight-1 angles enter exactly.
- Warm start: theta from the corresponding Phase-30 ideal-trained cell. Adam, lr 0.02, 150 steps. Gradient: central finite differences, h = 1e-4, on the exact deployed vector (parameter-shift is not valid for a channel; the alpha rounding makes the objective piecewise, which is accepted and stated).
- Cost: (2m + 1) evaluations per step, m = n + k: 9, 13, 17 at n = 4, 6, 8; x 150 steps x 5 seeds = 29 250 evaluations; budget = that number x the per-call time in `results/v4_tcdp/deploy_timing.json`, recorded before the run.
- Report: for each seed, the six metrics of `q_dep(theta_NAT)` next to `q_dep(theta_ideal-trained)` and `q_ideal(theta_ideal-trained)`; the owner's `owner_null_nat_ideal` is run with ideal maps first (NAT on ideal maps must reproduce the ideal-trained gap, zero, and change theta by less than the optimizer's own step noise, quantified as the theta change from 150 further Adam steps on the ideal objective).
- **Stop rule:** one n = 8 run over 20 minutes, or two calendar days without a green n = 4 end-to-end run: record timing in `PROJECT.md`, ship NAT as "attempted, stopped" with the numbers obtained. The milestone still closes.

---

## 7. Phase 32: write-up, gates, review
1. **OWNER checkpoint before any prose:** (a) why theta needs no conversion; (b) why composing unnormalised maps and normalising once is exact for end-of-circuit post-selection, and why per-gate renormalisation is not; (c) why k = 0 is a null for distinguishability but not for loss; (d) what the shared-qubit approximation is, and the measured number; (e) CP vs heralded-CZ throughput under loss. Hedging stops the phase.
2. `docs/tcdp-study.md`: question, design table, per-null outcome, figures with the shared-qubit error bar, hardware anchors, "what this does/doesn't establish", literature table with read-depth labels.
3. Mirrors: `docs/technical-findings.md` v4.0 section, README paragraph, `CLAUDE.md` Repo state.
4. **REVIEW gate:** Fable or Opus, then Codex, prompt verbatim: "For each stated finding, write the null result and check whether the finding differs from it. Then check every number against `deploy_sweep.csv`." Dispositioned in `.planning/phases/32-*/32-REVIEW.md`.
5. Gibbs pass offered (questions only); journal entry in the owner's words.
6. Vincent note, owner's words; send/hold recorded.

---

## 8. Literature the write-up must engage (full reads; abstract-level claims are labelled until then)
- Recio-Armengol, Ahmed, Bowles, arXiv:2503.02934 (in `docs/papers/`; confirm what deployment they report before characterising it).
- Raj, Mathur, Perdomo-Ortiz, arXiv:2608.31117 (full text read 2026-09-03 for the metric definitions and the 30-qubit state-vector statement).
- Salavrakos et al., arXiv:2405.02277 (full read required before any sentence about its training route or circuit class).
- Xie, Notton, Senellart, arXiv:2605.11879 (full read before any implementation-level comparison).
- Maring et al., arXiv:2306.00874 (full text read 2026-09-03 for the Ascella numbers).

---

## 9. Forbidden moves (the executor stops and asks instead)
- Loosening any tolerance, seed count, grid value, threshold, aggregation, or formula in this document. A failing check is reported with the measured number. (v3.1's null test was widened from 0.35 to 0.5 by executor discretion with a wrong rationale; that is the failure this rule exists to prevent.)
- Changing any value in table 5.1 or section 6.
- Running `deploy_sweep.py` before `test_nulls_tcdp.py` exists with the k = 0, noiseless, and NAT-ideal nulls filled by the owner.
- Reconstructing the PERM-adapted core instead of the bare catalog gate; hand-writing prep states or POVMs instead of deriving them from `compute_unitary()`.
- Renormalising a gate map, or forming any 4^n x 4^n matrix.
- Adding jax, iqpopt, pennylane, torch-based training, or any dependency.
- Silently renormalising, flooring, or dropping any distribution mass without a named column reporting it.
- Reporting a metric not defined in 5.4, or a headline not pre-registered in 5.6.
- Writing any sentence containing "barren plateau" as a finding, or "nobody has" without the scope qualifier in section 0.
- Writing the owner's null formulas, checkpoint answers, journal entry, or Vincent note.

---

## 10. Finish criteria (checked mechanically, pasted into the phase summary)
1. `python -m pytest -q` green; `tests/v4_tcdp/` contains the six test files; the only permitted skips are NAT tests if NAT-03's stop rule fired.
2. `results/v4_tcdp/deploy_sweep.csv` has 15 120 rows with the 5.5 schema, or `missing_cells.md` names each missing row; `results/v4_tcdp/trained/` has 900 files.
3. `results/v4_tcdp/crosscheck_shared_qubit.json` exists and its numbers appear verbatim in `docs/tcdp-study.md`.
4. Every figure regenerates from `tcdp_analysis.py` with no manual edits; the control line in Fig 1 is zero.
5. Owner checkpoint transcript recorded; both reviews dispositioned; Vincent note drafted.

## 11. Model routing and sequencing
- Phases 26, 27, 28, 30 scripts, 31 scripts: Codex (`codex exec`), one phase per prompt, the relevant section of this file pasted verbatim plus the verified-facts table.
- Phase 29 and the owner items of Phase 32: owner.
- Phase 32 prose: Sonnet drafts, owner reads aloud before commit.
- Review gate: Fable or Opus, then Codex adversarial.
- Order: 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32. Phase 30 does not start until `crosscheck_shared_qubit.json` is on disk and the owner nulls are filled.
