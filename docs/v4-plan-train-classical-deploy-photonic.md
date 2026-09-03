# v4.0 Plan: Train Classically, Deploy Photonically (TCDP)

**Status:** draft for owner approval, 2026-09-03. Written by Fable 5.1 after the v3.1 audit. Not started.
**Executor:** Codex (gpt-5.5) for every task marked MECH; Sonnet for prose tasks; Fable or Opus for the two review gates. The owner runs every task marked OWNER personally.
**Rule of the milestone:** every measurement has a null result written as a failing test before the sweep runs (`CLAUDE.md`, "Null-result gate"). A sweep whose numbers match its null is a pipeline check, not a finding.

---

## 0. The question, and why it is open

**Question.** An IQP Born machine is trained entirely classically (Van den Nest's cosine formula, the spring-semester `iqp-mmd-barren-plateau` methodology). The trained parameters are deployed on a photonic device: dual-rail photons, post-selected `CP(alpha)` gates for every ZZ term, realistic loss, partial distinguishability, and multi-photon emission. **How far is the device's post-selected output from the distribution the classical trainer thinks it deployed, as a function of gate count, system size, and the three noise parameters, and what does a usable sample cost?**

**Why it is open.** Recio-Armengol et al. (arXiv:2503.02934) deploy on ideal qubits. Raj, Mathur, Perdomo-Ortiz (arXiv:2608.31117) study the objective on a state-vector simulator. Salavrakos et al. (Quandela, arXiv:2405.02277) train a photonic Born machine on-device with loss mitigation but do not use the classical-training route or IQP structure. Nobody has put a classically trained IQP model through a photonic noise model. The closed forms from v3.1 already settle the loss axis exactly (conditional output is unchanged, throughput pays). The open axes are distinguishability and g2, which act inside the two-photon gates and are the parameters Quandela's own roadmap tracks ("distinguishability 70% -> 99%").

**What v3.1 established that this plan builds on (verified, do not re-derive):**

| Fact | Where verified |
|---|---|
| The sibling trainer's `theta` equals this repo's `thetas` / `pair_thetas` exactly, weight-1 and ZZ, no scale or sign conversion | Fable 2026-09-03: Walsh-inverse of sibling `iqp_expectation_exact` vs `exact_qubit_iqp_distribution`, n=3, error 0.0; scale 0.5 and 2 fail |
| Sibling core (`iqp/expectation.py`, `mmd/{kernel,loss,gradients,mixture}.py`, `rng.py`) imports with numpy only, no jax, no iqpopt | import scan 2026-09-03; `mmd2_exact_small_n` ran in this repo's venv |
| Perceval 1.2.4 `NoiseModel(indistinguishability=, g2=, transmittance=)` acts on plain dual-rail `Processor`s (HOM dip 0.5 -> 0.25 -> 0 at V = 1, 0.5, 0) | probe 2026-09-03 |
| `ProcessTomography` on the bare catalog `PostProcessedControlledRotationsItem` gate returns average fidelity 1.0 vs `diag(1,1,1,e^{i alpha})` ideal, 0.9707 at V = 0.9, 0.9690 at V = 0.9, g2 = 0.02, eta = 0.9 | probe 2026-09-03 |
| The PERM-adapted core `_build_cp_insertion_core` gives fidelity 0.65 under the same tomography: tomography must be run on the **bare** catalog gate, not the repo's adapted core | probe 2026-09-03 |
| Post-selected `probs()` under `NoiseModel` requires `min_detected_photons_filter(2)` on the 2-qubit gate processor or raises | probe 2026-09-03 |
| Loss on a CP gate costs nothing beyond `eta` per data photon: ancilla are vacuum in and out. Heralded CZ costs `eta^2` extra per gate for its two ancilla photons. v3.1's throughput table (`eta^(n+2k)`) is for heralded CZ only | `_build_cp_insertion_core` docstring; v3.1 hardness doc |

**Hardware anchors for the noise grid** (cite, do not invent):

| Source | V (indistinguishability) | g2(0) | end-to-end transmission |
|---|---|---|---|
| Ascella, Maring et al. Nat. Photon. 2024, arXiv:2306.00874 | 0.930 (M_s 0.944 corrected) | 7.3e-3 | ~8% |
| Altair, Salavrakos et al. PRA 2025, arXiv:2405.02277 | 0.84 | 0.025 (purity) | loss ~0.96 |
| Quandela roadmap 2026-2033 (p. 200 of the PDF text) | 70% -> 99% target | | |

---

## 1. Scope

### Must
- M1. Vendored classical trainer inside `merlin_iqp`, convention-tested against the repo's exact reference.
- M2. A noisy-gate-channel deployment simulator (density matrix on qubits, one tomographed channel per CP gate), cross-checked against full-Fock Perceval at n = 2, 3, including the shared-qubit two-gate case.
- M3. The TCDP gap sweep on a 1D-chain IQP family at n in {4, 6, 8, 10}, deployment noise grid anchored to Ascella and Altair, six metrics, every null written first.
- M4. Write-up in `docs/tcdp-study.md`, technical-findings mirror, README paragraph, and the owner's self-explanation checkpoints.

### Should
- S1. Non-post-selected (erasure-marked) output distribution returned by the deployment simulator (closes v3.1 REFRAME-02 properly).
- S2. Noise-aware classical training: train against the channel-composed deployed distribution instead of the ideal one, at n <= 8, and measure whether the gap closes. Stop rule in section 6.

### Won't (write into `.planning/PROJECT.md` Next Milestone Goals if tempted)
- A structured Fock-space simulator to n = 20. The channel approach makes it unnecessary for this question.
- Any barren-plateau claim. The sibling project's own finding is that init and n dominate; this milestone does not re-litigate it.
- Graph-state / MBQC realization (audit direction 4). Separate milestone.
- Heralded CZ under distinguishability. CP(alpha) only; it is the tunable gate ARB-01 validated and the cheaper one under loss.
- Recycling mitigation (Salavrakos). Different detector model (threshold) and different circuit class. Cite, do not implement.
- New literature reads beyond the four named in section 8.

---

## 2. Repository layout the executor must produce

```
src/merlin_iqp/classical/            # M1, vendored from C:\Users\cuqui\iqp-mmd-barren-plateau\src\iqp_bp
    __init__.py
    PROVENANCE.md                    # commit hash of the sibling repo, list of copied files, list of removed jax paths
    expectation.py                   # iqp_phase, iqp_expectation, iqp_expectation_exact (verbatim)
    kernel.py                        # gaussian_* only; laplacian/polynomial removed
    mixture.py                       # DatasetParityCache, dataset_expectations_batch (verbatim)
    loss.py                          # mmd2, mmd2_exact_small_n (verbatim minus laplacian/polynomial branches)
    gradients.py                     # grad_expectation_analytic, grad_mmd2_analytic, estimate_gradient_variance; ALL jax functions deleted
    rng.py                           # split_rng (verbatim)
    families.py                      # chain_1d (new, see 3.1), product_state, lattice (verbatim)
    initialization.py                # make_theta_with_metadata (verbatim)
    trainer.py                       # Trainer (verbatim; loss_mode exact for n<=12)
    adapter.py                       # theta_to_repo, repo_to_theta (new, see 3.2)
src/merlin_iqp/deploy/               # M2
    __init__.py
    gate_channel.py                  # extract_gate_channel, GateChannel
    density_matrix.py                # deploy_density_matrix
    fock_reference.py                # noisy_full_fock_distribution (n<=3 cross-check only)
    throughput.py                    # success_probability
    erasure.py                       # S1
tests/v4_tcdp/
    test_convention.py               # 3.3
    test_gate_channel.py             # 4.2
    test_density_matrix.py           # 4.4
    test_fock_crosscheck.py          # 4.5
    test_nulls_tcdp.py               # 5.2, written BEFORE the sweep, red first
scripts/v4_tcdp/
    train_classical.py               # 5.3
    deploy_sweep.py                  # 5.4
    tcdp_analysis.py                 # 5.5
results/v4_tcdp/
docs/tcdp-study.md
```

No file outside this list is modified except: `docs/technical-findings.md`, `README.md`, `CLAUDE.md` (Repo state section), `.planning/*`, `pyproject.toml` (no new dependencies; if Codex believes one is needed it stops and asks).

---

## 3. Phase 1 (MECH, Codex): vendor the classical trainer

### 3.1 Copy, strip, add `chain_1d`
1. Record `git -C C:\Users\cuqui\iqp-mmd-barren-plateau rev-parse HEAD` into `PROVENANCE.md`.
2. Copy the files listed in section 2 verbatim. Rewrite imports `iqp_bp.` -> `merlin_iqp.classical.`.
3. Delete from `gradients.py`: `grad_mmd2_autodiff_vector`, `grad_mmd2_autodiff`, `_jax_fixed_sample_value_and_grad`, and any `import jax`. Delete `laplacian_*`, `polynomial_*`, `multi_scale_*` from `kernel.py` and their branches in `loss.py`, `gradients.py`. `python -c "import merlin_iqp.classical"` must succeed with jax absent.
4. Add to `families.py`:
   ```python
   def chain_1d(n: int, k: int) -> np.ndarray:
       """Weight-1 generator on every qubit, plus the first k nearest-neighbour ZZ pairs
       (0,1),(1,2),...,(k-1,k). Rows: n weight-1 rows first, then k weight-2 rows.
       Requires 0 <= k <= n-1. Returns (n+k, n) uint8."""
   ```
   Row order is fixed and documented because `adapter.py` depends on it.

### 3.2 `adapter.py`
```python
def theta_to_repo(G: np.ndarray, theta: np.ndarray) -> tuple[list[float], dict[tuple[int,int], float]]:
    """G rows of weight 1 -> thetas[k]; rows of weight 2 -> pair_thetas[(i,j)] with i<j.
    Raises ValueError on any row of weight 0 or >=3, on duplicate rows, or if a weight-1
    row is missing for any qubit (thetas[k] = 0.0 is NOT silently assumed)."""
def repo_to_theta(n, thetas, pair_thetas) -> tuple[np.ndarray, np.ndarray]:   # (G, theta), chain_1d row order
```
No angle scaling, no sign flip. The identity `theta_sibling == theta_repo` was verified (section 0); the test below re-verifies it in-repo.

### 3.3 `tests/v4_tcdp/test_convention.py` (acceptance for Phase 1)
- `test_walsh_inverse_matches_exact_reference`: for n in {2,3,4}, k in {0,1,n-1}, 5 random theta draws: reconstruct `p(x) = 2^-n sum_a <Z_a> (-1)^{a.x}` from `iqp_expectation_exact` over all `a`, compare to `exact_qubit_iqp_distribution(n, *theta_to_repo(G, theta))`; max abs diff < 1e-12.
- `test_scale_conventions_fail`: the same check with `theta*0.5` and `theta*2` must exceed 1e-3 (proves the test can fail).
- `test_no_jax_import`: `sys.modules` contains no `jax` after importing `merlin_iqp.classical`.
- `test_exact_loss_runs_n10`: `mmd2_exact_small_n` at n = 10, chain_1d k = 9, sigma = 1.0 returns a finite float in under 60 s.

**Done when:** `python -m pytest tests/v4_tcdp/test_convention.py -q` green, full suite still green, `PROVENANCE.md` present.

---

## 4. Phase 2 (MECH, Codex): the deployment simulator

### 4.1 Design decision (recorded here so it is not re-decided)
Two options were considered. (a) Full-Fock simulation of the whole n-qubit photonic circuit with k CP gates: 2n + 4k modes, n photons, `C(2n+4k+n-1, n)` Fock states, infeasible past n ~ 5 with k ~ 4. (b) Tomograph each noisy CP gate once as a 2-qubit channel, then compose channels on an n-qubit density matrix (4^n entries, fine to n = 10, 12 with care). Option (b) is chosen. Its one approximation is that a photon's distinguishability is drawn independently in each gate it enters, whereas Perceval's `NoiseModel` makes it a property of the photon. Task 4.5 measures that approximation directly at n = 3 and the write-up carries the measured number as the stated error bar. Nothing is assumed.

### 4.2 `gate_channel.py`
```python
@dataclass(frozen=True)
class GateChannel:
    alpha: float
    noise: dict            # {"indistinguishability": V, "g2": g2, "transmittance": eta} or {} for ideal
    chi: np.ndarray        # (16,16) complex, Perceval's Pauli-basis chi matrix
    superop: np.ndarray    # (16,16) complex, acts on vec(rho) column-stacked, TRACE-PRESERVING (renormalised)
    avg_fidelity: float    # vs diag(1,1,1,e^{i alpha})
    p_success: float       # post-selection success probability, mean over the 4 computational basis inputs

def extract_gate_channel(alpha: float, noise: pcvl.NoiseModel | None) -> GateChannel:
```
Implementation constraints:
- Build the processor exactly as in the 2026-09-03 probe: `Processor("SLOS", 8, noise=noise)`, `add(0, PostProcessedControlledRotationsItem().build_circuit(n=2, alpha=float(alpha)))`, `add_herald(m, 0)` for m in 4..7, `set_postselection(PostSelect("[0,1]==1 & [2,3]==1"))`. **Bare catalog gate, no PERM adapters.**
- `chi = ProcessTomography(proc).chi_matrix()`; `avg_fidelity = ProcessTomography(proc).average_fidelity(U)`.
- Convert chi to a superoperator with an explicit Pauli-basis convention test (4.3, `test_ideal_superop_equals_unitary`). If Perceval's Pauli ordering is undocumented, determine it empirically from the ideal gate and write the ordering into a module constant with the test as its proof.
- Renormalise the superoperator to trace-preserving (divide by the trace of the Choi state). **`p_success` comes from `probs()` only** (`min_detected_photons_filter(2)`, mean `global_perf` over the four basis inputs). Do not derive success probability from the chi matrix; Perceval may already normalise it and nothing in this plan depends on its trace.
- **The channel key is `(alpha, V, g2)`; eta is not part of it.** Loss before a CP gate only removes shots in which a data photon is missing; conditioned on both photons arriving, the gate is identical. Eta enters only through `throughput.py` and `erasure.py`. (Null check in 4.3: a channel extracted with `transmittance=0.9` must equal the eta = 1 channel to 1e-9.)
- **Alpha is rounded to the grid `round(alpha / 0.1) * 0.1` (63 values on [0, 2pi)) before any channel lookup or deployment**, and the rounded value is stored in the sweep CSV next to the trained one. This bounds the number of distinct channels at 63 alphas x 18 (V, g2) points = 1134 tomographies. Measured 2026-09-03 in this venv: one tomography takes 19.6 s ideal, 22.0 s at Ascella noise, so the full set is about 7 hours on one core; tomographies are independent and may be run in parallel processes, provided the cached result for a key is byte-identical regardless of which process produced it. The rounding error on the deployed distribution is measured once (ideal channels, rounded vs unrounded alpha, n = 4, k = 3) and reported.
- Cache channels on disk under `results/v4_tcdp/channels/{alpha_rounded:.1f}_{V}_{g2}.npz`.
- **Timing gate:** `test_tomography_wall_clock` records the seconds per tomography into `results/v4_tcdp/tomography_timing.json`. If 1134 x that number exceeds 10 hours single-core, Codex stops and reports; the owner then chooses between dropping the g2 = 0.025 row and dropping V = 0.99. Neither is chosen by the executor.
- **Fallback if 4.5's single-gate cross-check fails:** tomography under `NoiseModel` is then not trusted. Reconstruct the channel by direct simulation instead: run the bare gate processor on the 16 product inputs `{|0>,|1>,|+>,|+i>}^2` with readout in the Z basis and, via an added `BS()` / phase on each dual-rail pair before detection, in the X and Y bases; invert to the process matrix by standard linear inversion. Same tests apply. If that also fails the n = 2 cross-check, stop: the milestone's method has a problem the owner must see.

### 4.3 `tests/v4_tcdp/test_gate_channel.py`
- `test_ideal_superop_equals_unitary`: noise = None, alpha in {pi/6, pi/3, pi}: `superop` equals `conj(U) kron U` (column-stacking) to 1e-9. Phase must sit on `|11>`.
- `test_ideal_fidelity_one`: avg_fidelity == 1.0 within 1e-9; V = 1, g2 = 0, eta = 1 explicitly also gives 1.0.
- `test_V09_fidelity_matches_probe`: V = 0.9, alpha = pi/3: avg_fidelity within 1e-4 of 0.97073 (the probe value).
- `test_trace_preserving`: for every cached channel, applying `superop` to vec(I/4) returns trace 1.
- `test_p_success_closed_form`: at noise = None, `p_success == 1/sigma_max(alpha)^4` from `iqp_photonic`'s closed form within 1e-9.
- `test_eta_does_not_change_channel`: superoperator at `transmittance=0.9, V=0.9` equals the one at `V=0.9` alone to 1e-9.
- `test_tomography_wall_clock`: writes seconds-per-tomography to `results/v4_tcdp/tomography_timing.json`; asserts nothing, but Phase 3 reads it (5.1).

### 4.4 `density_matrix.py`
```python
def deploy_density_matrix(n, thetas, pair_thetas, channel_for_pair: dict[tuple[int,int], GateChannel],
                          qubit_order="msb_q0") -> np.ndarray:
    """Returns probs over 2^n bitstrings, bit order identical to exact_qubit_iqp_distribution.
    rho = |+><+|^n; apply exp(i thetas[k] Z_k) exactly; for each (i,j) in pair_thetas apply
    exp(i th Z_i) exp(i th Z_j) exactly then channel_for_pair[(i,j)].superop (alpha must equal 4*th
    or raise); apply H^n; return diag."""
```
Memory rule: n <= 10 in this milestone (4^10 * 16 B = 16 MB per copy). If n = 12 is attempted it must use the two-qubit-at-a-time einsum path and be timed first; Codex does not silently allocate 4^12 x several copies.

`tests/v4_tcdp/test_density_matrix.py`:
- `test_ideal_channels_reproduce_exact_reference`: n in {2,3,4}, k in {0,1,n-1}, ideal channels: max abs diff vs `exact_qubit_iqp_distribution` < 1e-12. (**This is Phase 2's null result.**)
- `test_k0_ignores_channels`: n = 4, k = 0, any noisy channel dict passed: output equals ideal. (A weight-1 circuit has no two-photon interference; distinguishability cannot act.)
- `test_alpha_theta_mismatch_raises`.

### 4.5 `fock_reference.py` and `tests/v4_tcdp/test_fock_crosscheck.py` (the trust gate for option (b))
`noisy_full_fock_distribution(n, thetas, pair_thetas, noise: NoiseModel) -> (dist, p_success)` for n <= 3 only: build the dual-rail circuit with `dual_rail.make_weight2_cp_circuit_and_input` (one pair) or a two-pair variant assembled through `Processor.add(mapping, ...)` following `_build_weight2_cp_processor_no_postselect`'s mapping pattern, attach `noise`, `min_detected_photons_filter(n)`, and do the manual per-pair post-selection and ancilla-vacuum filtering exactly as `photonic_cp_iqp_distribution` does. Tests:
- `test_single_gate_n2_matches_channel`: n = 2, pair (0,1), V in {1, 0.9, 0.7}, g2 in {0, 0.02}: TVD(channel-composed, full-Fock) < 1e-6.
- `test_single_gate_n3_bystander`: n = 3, pair (1,2), bystander qubit 0: same bound, run separately for V-only noise and for g2-only noise. **If the g2-only case fails while the V-only case passes**, multi-photon emission is leaking into bystander modes, which a per-gate channel cannot represent. Then: g2 is demoted from a headline axis to a "gate-local approximation" column, the write-up states the measured n = 3 discrepancy as its error bar, and the V axis carries the headline. The executor does not decide this; it reports both numbers and stops.
- `test_two_gates_shared_qubit_n3`: n = 3, pairs (0,1) and (1,2), V = 0.9: **record** TVD(channel-composed, full-Fock) into `results/v4_tcdp/crosscheck_shared_qubit.json`. Assert only that it is < 0.05. The measured value is reported in the write-up as the independent-gate approximation error; if it exceeds 0.01, section 5's sweep additionally runs the full-Fock reference at n = 3 for every noise point and plots both.

**Done when:** all three test files green; `results/v4_tcdp/crosscheck_shared_qubit.json` exists with a number in it.

### 4.6 `throughput.py`
```python
def success_probability(n, channels: list[GateChannel], eta: float) -> float:
    """eta**n * prod(c.p_success for c in channels). CP gates carry vacuum ancilla: NO eta**2 per gate.
    Document in the docstring that heralded_cz would add eta**2 per gate (v3.1 closed form)."""
```
Test: at eta = 1 and ideal channels equals the product of `1/sigma_max^4`; at k = 0 equals `eta**n`.

### 4.7 `erasure.py` (S1)
`erasure_marked_distribution(q_conditional, n, eta, gate_qubits: set[int]) -> dict[str, float]` over strings in `{0,1,E}^n`: each qubit outside `gate_qubits` is erased independently with probability `1 - eta`; any loss on a qubit inside `gate_qubits` fails that gate's post-selection and the shot is dropped (mass reported separately as `dropped`). Test: total mass + dropped == 1; at eta = 1 equals `q_conditional`. This is the honest form of v3.1's REFRAME-02 and is what direction 1 of the audit would consume later.

---

## 5. Phase 3: the TCDP gap sweep

### 5.1 Fixed experimental design (no free choices left to the executor)

| Axis | Values | Reason |
|---|---|---|
| Circuit family | `chain_1d(n, k)`: all weight-1 + first k NN ZZ pairs | KLM/CP gate count = k; matches nearest-neighbour hardware connectivity |
| n (deployment) | 4, 6, 8, 10 | density-matrix budget |
| n (training only) | 16, 20 | shows training scales; deployment there via loss closed form only |
| k | 0, 1, 2, ..., n-1 | k = 0 is the null; gap vs gate count is the primary curve |
| Target | 1D open Ising chain: `p(x) = exp(beta * sum_{i<n-1} J_i s_i s_{i+1}) / Z`, `s_i = 1 - 2 x_i`, beta = 1, `J_i ~ N(0,1)` drawn once from `np.random.default_rng(4001)`, Z by exact enumeration of all 2^n strings (n <= 20), 20 000 samples drawn by inverse-CDF from the exact vector with `default_rng(4002)`; the exact vector itself is the target for every exact metric | structured, low-order correlations, sibling-compatible; the exact vector removes sampling noise from every population metric |
| Kernel | Gaussian on Hamming distance, sigma = 0.5 * sqrt(n) (primary), sigma = 1.0 fixed (control) | Rudolph et al.: bandwidth in Theta(sqrt n) keeps the loss low-bodied |
| Loss | exact (`mmd2_exact_small_n`) for n <= 10; MC (`num_a_samples` 512, `num_z_samples` 2048) for n in {16, 20} | |
| Init | `data_dependent` (primary), `small_angle` std 0.1, `uniform` | sibling's three schemes |
| Optimizer | Adam, lr 0.05, 300 steps, checkpoint every 50 | sibling defaults |
| Seeds | 5 per cell, `derive_seed("tcdp", n, k, init, seed_idx)` via `trainability/rng.py` | |
| Deployment noise grid | V in {1.0, 0.99, 0.95, 0.93, 0.84, 0.70}; g2 in {0, 0.007, 0.025} (18 channel points); eta in {1.0, 0.9, 0.5, 0.08} applied post hoc through throughput and erasure only | Ascella, Altair, roadmap anchors; eta does not change the conditional gate (4.2) |
| Gate angle | alpha = 4 * theta_pair from the trained theta, rounded to the 0.1 rad grid (4.2); both values stored; rounding error on the deployed distribution measured once and reported | ARB-01 identity |

Channels are tomographed once per rounded `(alpha, V, g2)`, at most 1134 in total (about 7 single-core hours at the measured 20 s each), budgeted by Phase 2's timing gate before this phase starts. **No value in this table may be changed by the executor.** A cell that cannot be run goes into `missing_cells.md` with the reason; it is not replaced with a nearby value.

### 5.2 `tests/v4_tcdp/test_nulls_tcdp.py` (OWNER writes the formulas; written red BEFORE `deploy_sweep.py` runs)
The owner fills these; Claude may ask questions and point at rows, not supply formulas:
- `owner_null_gap_k0(V, g2)`: predicted TVD(ideal, deployed) at k = 0 for any V, g2.
- `owner_null_gap_noiseless(k)`: predicted gap at V = 1, g2 = 0 for any k.
- `owner_null_eta_effect(n, k, eta)`: predicted change in the conditional distribution from eta alone.
- `owner_null_throughput(n, k, alphas, eta)`: closed form.
- `owner_hypothesis_gap_scaling(k, F)`: the owner's *hypothesis* for TVD vs k given single-gate infidelity 1 - F (first-order guess is fine); marked `xfail(strict=False)` because it is a hypothesis, not a null.
Tests skip while a function returns `None`; NULL-02-style promotion after the sweep.

### 5.3 `scripts/v4_tcdp/train_classical.py` (MECH)
Trains every `(n, k, kernel, init, seed)` cell with `merlin_iqp.classical.Trainer`; writes `results/v4_tcdp/trained/{cell}.npz` containing `G`, `theta`, `loss_trajectory`, `metadata`. Also writes `q_ideal` (exact `exact_qubit_iqp_distribution` for n <= 10). Deterministic; re-running produces byte-identical `theta`.

### 5.4 `scripts/v4_tcdp/deploy_sweep.py` (MECH)
For every trained cell with n <= 10 and every noise point: `q_dep = deploy_density_matrix(...)`, `p_succ = success_probability(...)`. One CSV `results/v4_tcdp/deploy_sweep.csv` with columns:
`n,k,kernel,init,seed,V,g2,eta,tvd_ideal_deployed,mmd2_train_ideal,mmd2_train_deployed,kl_target_ideal,kl_target_deployed,coverage_ideal,coverage_deployed,fidelity_ideal,fidelity_deployed,marginal_err_k1_deployed,marginal_err_k2_deployed,p_success,mean_gate_fidelity`.
Metric definitions (exact, since all distributions are exact vectors):
- `tvd_ideal_deployed`: 1/2 sum |q_ideal - q_dep|.
- `mmd2_train_*`: `mmd2_exact_small_n` with the training kernel, target = exact Ising p.
- `kl_target_*`: sum p log(p/q), with q floored at 1e-12 (state the floor).
- `coverage_*`, `fidelity_*`: Raj et al. definitions with "valid" = strings in the target's support above 1e-6, computed from exact vectors, not samples (state that this is the population version of their sample metric).
- `marginal_err_k1/k2`: mean over subsets of size 1 / 2 of TVD between marginals (sibling `marginal_metrics.py`, vendored if needed).

### 5.5 `scripts/v4_tcdp/tcdp_analysis.py` (MECH) and figures
- Fig 1: TVD(ideal, deployed) vs k at each n, one line per V (g2 = 0, eta = 1).
- Fig 2: TVD vs (1 - mean_gate_fidelity) * k, all cells, with the owner's hypothesis line.
- Fig 3: coverage and forward-KL, ideal vs deployed, at Ascella and Altair points.
- Fig 4: throughput vs (n, k) at the four eta values, CP-gate cost, with the heralded-CZ curve from v3.1 overlaid for contrast.
- Table: per-n, per-noise-point summary, mean +- std over seeds.
Every number in `docs/tcdp-study.md` must trace to `deploy_sweep.csv` or a test (WRITE-06 convention).

### 5.6 What would make this a finding rather than a pipeline check
The sweep is a finding only where it differs from the nulls in 5.2: nonzero gap at k >= 1 under V < 1 or g2 > 0, and its dependence on k and n. If the gap at Ascella's point stays below 0.02 through k = n - 1 at n = 10, that is the headline ("classically trained IQP survives Ascella-grade deployment"); if it grows past 0.1 by k = 5, that is the headline ("distinguishability, not loss, is the deployment ceiling, and here is the gate count where it bites"). Either is publishable at the "note to Vincent / workshop poster" level. The write-up states which occurred.

---

## 6. Phase 4 (S2, stretch): noise-aware classical training
Train theta against `q_dep(theta)` instead of `q_ideal(theta)` at n in {4, 6, 8}, k = n - 1, Ascella noise. Gradient by central finite differences on `deploy_density_matrix` (h = 1e-4; parameter-shift is not valid for a channel). Metric: the deployed gap before vs after. **Stop rule:** if one training run at n = 8 exceeds 20 minutes, or if two full days pass without a green end-to-end run at n = 4, record the timing in `PROJECT.md` and stop. This is the SMART spec's stall pattern and the milestone ships without S2.

---

## 7. Phase 5: write-up, gates, review

1. **OWNER self-explanation checkpoint before writing** (CLAUDE.md rule): explain unaided (a) why theta needs no conversion between trainer and photonic circuit, (b) why option (b) in 4.1 is exact for one gate and approximate for two gates on a shared qubit, and what the measured error was, (c) why k = 0 is a null for distinguishability but not for loss, (d) what the throughput formula changes between CP and heralded CZ. Hedging is the stop signal.
2. `docs/tcdp-study.md`: question, design table (5.1), nulls and whether each matched, figures, the shared-qubit approximation number, hardware anchors with citations, "what this does/doesn't establish", literature table with read-depth labels.
3. Mirror in `docs/technical-findings.md` (new section, not a rewrite), README v4.0 paragraph, `CLAUDE.md` Repo state.
4. **REVIEW gate (Fable or Opus, then Codex adversarial):** prompt verbatim: "For each stated finding, write the null result and check whether the finding differs from it. Then check every number against `deploy_sweep.csv`." Findings dispositioned in `.planning/phases/25-tcdp/25-REVIEW.md`.
5. Gibbs pass offered to the owner (questions only), journal entry in the owner's words.
6. Vincent note (3-5 sentences, owner's words); send/hold recorded.

---

## 8. Literature the write-up must engage (full reads, not abstracts)
- Recio-Armengol, Ahmed, Bowles, arXiv:2503.02934 (already in `docs/papers/`).
- Raj, Mathur, Perdomo-Ortiz, arXiv:2608.31117 (metrics in 5.4 come from here).
- Salavrakos et al., arXiv:2405.02277 (Quandela; the on-device comparison point).
- Xie, Notton, Senellart, arXiv:2605.11879 (Quandela; dual-rail post-selection and trainability).
Optional context: Maring et al. arXiv:2306.00874 (Ascella numbers), Oh arXiv:2406.08086 (if S1's erasure output is analysed, which is out of scope here).

---

## 9. Forbidden moves (the executor stops and asks instead)
- **Loosening any tolerance, seed count, grid value, or threshold stated in this plan.** A failing tolerance is reported with the measured number, never adjusted to pass. (v3.1's null test was widened from 0.35 to 0.5 by executor discretion and the reason given was wrong; that is the failure this rule exists to prevent.)
- Changing any value in table 5.1.
- Running `deploy_sweep.py` before `test_nulls_tcdp.py` exists with at least the k = 0 and noiseless nulls filled by the owner.
- Tomographing the PERM-adapted core instead of the bare catalog gate.
- Passing a superoperator that is not trace-preserving into `deploy_density_matrix`.
- Adding jax, iqpopt, pennylane, torch-based training, or any new dependency.
- Silently renormalising, flooring, or dropping any distribution mass without a named column reporting it.
- Reporting a metric that was not defined in 5.4.
- Writing any sentence containing "barren plateau" as a finding.
- Writing the owner's checkpoint answers, journal entry, or Vincent note.

---

## 10. Finish criteria (checked mechanically at the end, pasted into the phase summary)
1. `python -m pytest -q` green; `tests/v4_tcdp/` contains the five test files and no skips remain except S2 if abandoned.
2. `results/v4_tcdp/deploy_sweep.csv` has every cell of 5.1 for n <= 10 (4 n-values x (n choose k as listed) x 3 inits x 5 seeds x 72 noise points) or a `missing_cells.md` explaining each gap.
3. `results/v4_tcdp/crosscheck_shared_qubit.json` exists and its number appears verbatim in `docs/tcdp-study.md`.
4. Every figure in `docs/tcdp-study.md` regenerates from `tcdp_analysis.py` with no manual edits.
5. Owner checkpoint transcript recorded; review file dispositioned; Vincent note drafted.

## 11. Model routing and sequencing
- Phase 1, 2, 3 code and scripts: Codex (`codex exec`), one phase per prompt, each prompt containing the relevant section of this file verbatim plus the two verified facts it depends on.
- Phase 3 nulls and Phase 5 items 1, 5, 6: owner.
- Phase 5 prose: Sonnet drafts, owner reads aloud before commit.
- Review gate: Fable or Opus, then Codex adversarial.
- Order: 1 -> 2 -> 5.2 (owner) -> 3 -> 4 (optional) -> 5. Nothing in 3 starts until 4.5's cross-check number is on disk.
