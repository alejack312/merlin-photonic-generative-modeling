# Qubit-side IQP baseline: structure, hardness, and trainability

Compiled from the sibling `iqp-mmd-barren-plateau` project's own docs and vault notes — not re-derived from a fresh literature pass:
- `C:\Users\cuqui\iqp-mmd-barren-plateau\docs\technical\iqp-classical-sampling.md` (circuit structure, classical-training trick)
- `C:\Users\cuqui\iqp-mmd-barren-plateau\iqp-mmd-barren-plateau-vault\Theory\Barren Plateaus.md` (barren-plateau definition and framing)
- `C:\Users\cuqui\iqp-mmd-barren-plateau\iqp-mmd-barren-plateau-vault\Report\Final Findings - IQP MMD Barren Plateaus.md` (empirical resolution)

This is the qubit-side reference Phase 9 compares its photonic (Fock-space) encoding design against — what does IQP look like, and is it trainable, before any translation happens.

## IQP Circuit Structure & Hardness

- **Circuit recipe.** Every qubit starts in the `|+⟩` state (Hadamard on `|0⟩`). A middle layer of gates diagonal in the Z-basis is applied — in the reference implementation, `MultiRZ(2θⱼ, wires=gⱼ)` for each generator `gⱼ`. Hadamards are applied again and the circuit is measured in the computational basis — equivalently, measurement lands in the Hadamard-conjugate (X) basis relative to the diagonal gate layer.
- **"Instantaneous" means no fixed gate order.** Every gate in the middle layer is diagonal in the same basis, so they all commute pairwise. There is no operator-ordering to track — this is where the "I" in IQP comes from, and it is the structural property the classical-training trick below depends on.
- **The classical-training trick (Van den Nest's cosine formula).** Any Z-word expectation value under the circuit has a closed form:

  ```
  ⟨Z_a⟩ = E_{z ~ Uniform({0,1}^n)} [ cos(Φ(θ, z, a)) ]
  Φ(θ, z, a) = Σ_j (a·g_j mod 2) · 2θ_j · (-1)^(z·g_j)
  ```

  This turns "compute an expectation value" into averaging a cosine over randomly sampled classical bitstrings `z` — plain integer/float arithmetic, no `2^n`-dimensional state vector, no matrix exponentiation. Commutativity of the gate layer is exactly what makes this closed form exist: because there's no ordering ambiguity, the output distribution has tractable Fourier/Walsh structure over Z-word expectations.
- **Training is classically tractable; sampling is believed hard.** The cosine-formula trick only ever produces expectation values, never full samples. Actually drawing a bitstring from the circuit's real output distribution still requires running the quantum circuit (or a full state-vector simulator) — believed classically hard, which is the entire basis for a quantum-advantage claim here. Training and sampling are different computational tasks with very different classical tractability, and it's easy to conflate them.
- **Same structural skeleton Douce et al. ports to CV.** The H-diagonal-gates-H sandwich (`|+⟩` prep → commuting diagonal layer → Hadamard-conjugate measurement) is exactly the DV starting point `docs/iqp-lit-scoping.md` describes Douce et al. (2017) building its continuous-quadrature analogue from — see that doc for how each ingredient gets swapped for a CV counterpart, and why that swap still isn't a Fock-space/photon-number construction.

## Barren-Plateau Trainability

- **Formal definition.** A barren plateau is the regime where the loss-gradient variance decays exponentially in qubit count: `Var_{θ~D}[∂_θᵢ L] = O(2^{-αn})` for some `α > 0`. When this holds, distinguishing a useful descent direction from noise requires an exponential number of measurement shots, and training does not scale.
- **The open question this baseline investigated.** Standard results for generic random circuits (unitary 2-designs) say barren plateaus are the rule as circuit depth/qubit count grow. IQP is *not* a 2-design — its gate set is far more structured (all diagonal, all commuting). Does that structure protect trainability, or is exponential gradient decay unavoidable regardless?
- **Average-case framing matters.** Barren-plateau results are statements about the *average* gradient over the parameter landscape, not pointwise guarantees (Larocca et al. 2024) — so "trainable valleys" can exist even where the ensemble average looks flat. This is why initialization scheme (e.g. small-angle, θ near 0) is a live variable rather than a footnote.
- **Empirical resolution: structure alone does not predict plateaus.** A purely structural predicate (`bounded_degree AND high_overlap`) had 0% recall against observed plateaus — structure alone told you almost nothing. The rule that actually worked combines initialization, system size, and one structural escape hatch:

  ```
  plateau if small_angle
  or plateau if uniform and n >= 6 and not complete_graph_like
  ```

  Scored against 283 training + holdout rows: 97.9% accuracy, 100% precision, 97.5% recall (0 false positives, 6 false negatives, all in an unresolved `uniform × n=4` corner). The `not complete_graph_like` clause is load-bearing — removing it reintroduces false positives on complete-graph structures.
- **Anti-concentration alone is an insufficient success criterion.** A learned distribution can pass a naive anti-concentration check and still have small MMD loss while being far more concentrated than its target — every exact-`n=9` sweep found the learned distribution smoother/more concentrated than target regardless of bandwidth. Marginal-agreement diagnostics (does the learned distribution match the target's actual correlational structure) are the more informative check than anti-concentration in isolation.

## Why This Matters for Phase 9

Phase 9's photonic (Fock-space) encoding design has two qubit-side properties to keep in view as targets, not just one. The structural-hardness argument above depends on a specific circuit skeleton — commuting diagonal gates conjugated by a fixed basis change — so preserving (or knowingly trading off) that skeleton in a photonic mapping is what would keep the hardness claim intact. Separately, and only weakly correlated with structure, trainability in the qubit case turned out to hinge on initialization and system size, with structure acting as a narrow escape hatch rather than a guarantee either way. A DV/Fock-space encoding that faithfully preserves IQP's commuting-gate structure is not thereby guaranteed to inherit favorable trainability — that would need to be checked on its own terms, not assumed from the structural analogy alone.
