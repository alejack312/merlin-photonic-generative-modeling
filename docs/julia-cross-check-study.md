# Independent Julia cross-check study (Phase 19)

The phase's canonical reference document: methodology, per-requirement
results, and honest scope statement for VERIFY-02/VERIFY-03/VERIFY-04.
Phase 20 (Technical Write-Up) treats this as supplementary evidence per
`ROADMAP.md` and can cite it directly rather than re-deriving any of it.

## Methodology

### Python-reference generation (Plan 19-01)

Every number Julia is diffed against in this phase comes from
`julia/generate_reference.py`, which calls this repo's already-tested
Python functions directly (`exact_qubit_iqp_distribution`,
`photonic_iqp_distribution`, `photonic_weight2_iqp_distribution`, and the
loss-model equivalents from `hardness/loss_model*.py`) and writes their
output to CSV under `results/julia_reference/`. No number in this document
was computed by hand or re-derived — every Julia script reads a CSV Plan
19-01 produced from a single, specific Python call.

For the loss-model cross-check (VERIFY-04), a **single fixed theta draw
per scope** was used (seed_base `190819`, deliberately distinct from Phase
18's own `180814`), not a pooled multi-draw mean — per `19-RESEARCH.md`
Pitfall 4, since the point is number-for-number agreement on one concrete
case, not a statistical claim. The literal theta values are recorded as
header comments in every loss-case reference CSV.

### Independent build, not a mechanical port

The single most load-bearing decision in this phase
(`19-CONTEXT.md`'s own framing): every Julia circuit was built from its
own library's native API and idioms — Yao.jl's `H`/`Rz`/`put`/`chain` for
the qubit-side circuit, BosonSampling.jl's `beam_splitter`/`phase_shift`/
`UserDefinedInterferometer` for the photonic-level circuits — never by
extracting a matrix or structure from Perceval's own circuit and replaying
it in Julia. This is what makes agreement meaningful: if a bug existed in
`iqp_photonic_encoding.py`'s math, a mechanical port would silently
reproduce it in both languages, while an independent build sourced from
first principles (phase-convention algebra, literature-sourced gate
matrices) would not.

Every phase-convention or bit-ordering translation between the two
languages' native conventions (Yao's `Rz` vs. this repo's `WP`;
BosonSampling's mode-orientation convention vs. Perceval's) was derived
algebraically first, then confirmed numerically against a known
closed-form case (typically n=1) before being trusted for the full n=2/n=3
comparison — never assumed from surface-level similarity.

### Tolerance

A single locked bar applies throughout: **TVD ≤ 1e-6**, the same bar used
for Phase 12's locked-gate cross-check. Both sides of every comparison in
this phase are exact, non-sampling computations of the same underlying
physics, so agreement at the level of floating-point noise (typically
1e-14 to 1e-17) is the expected, achievable outcome — not an approximate
or statistical match.

## VERIFY-02: Yao.jl qubit-side cross-check

**Plan:** 19-02. **Script:** `julia/verify_qubit_iqp.jl`. **Results:**
`results/phase19_verify02_results.md`.

An independently-built Yao.jl circuit (state prep → Hadamard layer →
diagonal weight-1 phase layer → Hadamard conjugation, using Yao's own `H`/
`Rz`/`chain`/`probs` primitives) reproduces
`iqp_photonic_encoding.py::exact_qubit_iqp_distribution`:

| n | thetas | TVD (Julia vs. Python) | Tolerance | Result |
|---|--------|------------------------:|-----------|--------|
| 2 | `[0.3, 1.1]` | `2.26e-17` | `1e-6` | PASS |
| 3 | `[0.3, 1.1, 0.75]` | `1.12e-16` | `1e-6` | PASS |

**Phase-convention finding:** this repo's `WP(theta,0) =
diag(e^{i*theta}, e^{-i*theta})` equals Yao's `Rz(-2*theta)` entry-for-
entry — derived algebraically, then confirmed numerically at n=1 against
the closed-form marginal `cos(theta)^2`/`sin(theta)^2` (atol=1e-10).

**Bit-ordering finding:** Yao's `probs()` vector uses qubit `m` = LSB of
the 0-based index for this circuit — confirmed empirically (not assumed
from a prior Phase-14 comment) via an asymmetric n=2 probe tested against
two named candidate orderings, with a hard assertion that exactly one
matches known per-qubit marginals.

**Verdict: GO.**

## VERIFY-03: BosonSampling.jl photonic-level cross-check

Split into a weight-1 leg (Plan 19-03) and a weight-2 leg (Plan 19-04),
per `19-CONTEXT.md`'s "independently gradeable" design — neither leg
blocks the other.

### Weight-1 leg (Plan 19-03)

**Script:** `julia/verify_photonic_iqp_weight1.jl`. **Results:**
`results/phase19_verify03_weight1_results.md`.

An independent BosonSampling.jl dual-rail (2-modes-per-qubit) circuit
(built from `beam_splitter`/`phase_shift`/`UserDefinedInterferometer`, not
a port of Perceval's HWP/WP/PBS polarization circuit) reproduces
`photonic_iqp_distribution`:

| n | thetas | TVD | Tolerance | Status |
|---|--------|-----|-----------|--------|
| 2 | `[0.3, 1.1]` | `2.36e-16` | `1e-6` | PASS |
| 3 | `[0.3, 1.1, 0.75]` | `3.04e-16` | `1e-6` | PASS |

The load-bearing derivation: `phase_shift(phi)` with `phi = pi - 2*theta`
reproduces this repo's `WP(theta,0)`-derived marginal — derived
algebraically from the `H*D*H` sandwich, not assumed to be the more
"obvious" `phi = 2*theta`, and confirmed both by hand against the n=2
reference CSV and by the script's own n=1 assertion (atol=1e-10).

**Verdict: GO.**

### Weight-2 leg (Plan 19-04)

**Script:** `julia/verify_photonic_iqp_weight2.jl`. **Results:**
`results/phase19_verify03_weight2_results.md`.

This was the phase's single highest-stall-risk piece per
`19-CONTEXT.md`'s own framing, and it reached a **real, full GO** — not a
partial-go or a documented stall. The Knill CZ gate's unitary was sourced
directly from arXiv:quant-ph/0110144 (Knill, 2001), Eq. 11's closed-form
4×4 matrix — fetched as both PDF and LaTeX e-print source, read directly,
never extracted from Perceval's own `heralded_cz` circuit. Built as a
6-mode dual-rail circuit (Hadamard state prep, a π/4 weight-1 correction
realizing the CZ-to-ZZ operator identity already derived in
`docs/iqp-photonic-encoding.md`'s Ingredient 2, the Knill gate embedded on
the logical-`|1⟩` rails + 2 ancillas, conjugation, hand-herald
post-selection).

| Quantity | Python | Julia | Difference |
|---|---|---|---|
| TVD (bitstring distribution) | — | `3.497e-15` | well below `1e-6` |
| `herald_failure_prob` | `25/27 = 0.9259259...` | `0.925925925925926` | `5.55e-16` |
| `residual` (bunching leak) | `0.0` | `~4.45e-32` | numerical zero |

**A real bug was found and fixed during execution**, not smoothed over:
the paper's matrix, used exactly as printed, leaked ~0.033 probability
into bunched outputs that Knill's own Eq. 6 proves must be exactly zero.
Diagnosed via a standalone 4-mode zero-leak check (not trial-and-error
against the full pipeline) as a row/column transpose convention mismatch
— the paper defines its matrix via `V_rs = u_sr`, differing from
`UserDefinedInterferometer`'s expected output-row/input-column
orientation. Using the matrix transposed dropped all four leak terms to
numerical zero (~1e-32); the fix and the zero-leak check are preserved as
a runnable assertion in the script, re-verified on every run. This is the
"obvious culprit" (mode/matrix orientation convention)
`19-CONTEXT.md`'s disagreement-handling protocol names as the first thing
to check, and it resolved within a single focused debugging pass, well
inside the phase's time-box.

Scope: covers only the n=2 locked-gate case (`i=0, j=1`, pair angle
`pi/4`), matching `19-CONTEXT.md`'s VERIFY-03 weight-2 scope — does not
extend to other `(i,j)` pairs, n=3, or non-locked pair angles (the catalog
gate `heralded_cz` only realizes the fixed `pi/4` angle in the first
place).

**Verdict: GO.**

## VERIFY-04: BosonSampling.jl loss-model cross-check

**Plan:** 19-05. **Script:** `julia/verify_loss_model.jl`. **Results:**
`results/phase19_verify04_results.md`.

BosonSampling.jl's **native** `UniformLossInterferometer(eta, U)` loss API
was used — confirmed against the actual installed v1.0.2 depot source
(`~/.julia/packages/BosonSampling/TEQXU/src/types/loss.jl`), not GitHub
`main` — the strongly-preferred independence path per `19-RESEARCH.md`'s
"Don't Hand-Roll" guidance. No fallback to hand-attenuation was needed.

**Two real findings during the native-API investigation**, both auto-fixed
and documented rather than silently absorbed:

1. **Convention mismatch:** BosonSampling's `eta` parameter is a
   transmission AMPLITUDE (`|t|^2` = transmission probability), while this
   repo's Python-side `eta` is a transmission PROBABILITY directly.
   Resolved by passing `sqrt(eta)`, verified via an n=1 closed-form sanity
   check (`p(survive)=eta, p(lost)=1-eta`, atol=1e-10) before trusting the
   n=2 comparison.
2. **Real bug in the installed package:** `Event()` cannot be constructed
   directly against a `UniformLossInterferometer` — it never registered a
   `LossParameters` dispatch method for its own type (confirmed live via a
   standalone repro). Worked around by wrapping the interferometer's own
   native-computed `.U` field in `UserDefinedInterferometer(li.U)` before
   building `Event`s — numerically identical, since `compute_probability!`
   only ever reads `.U`; the loss physics still comes entirely from
   BosonSampling's own native construction, not a hand-attenuation
   fallback.

Doubled-mode marginalization (the phase's flagged hardest open question)
was done by exact enumeration: since the virtual 2m-mode interferometer is
unitary, total photon count is exactly conserved, so every composition of
N photons across 2m modes was enumerated and summed into physical-mode
buckets — an exact marginal, not sampling or approximation.

Circuits reused Plan 19-03's verified weight-1 dual-rail construction and
Plan 19-04's verified Knill-CZ construction (generalized to two
independent per-qubit diagonal phases for the mixed case).

### Weight-1

| eta | TVD | Tolerance | Status |
|-----|-----|-----------|--------|
| 0.99 | `2.07e-16` | `1e-6` | PASS |
| 0.80 | `8.13e-18` | `1e-6` | PASS |
| 0.05 | `1.62e-18` | `1e-6` | PASS |

### Mixed (weight-1 + weight-2, n=2, i=0, j=1)

| eta | TVD | herald_failure_prob (Julia) | herald_failure_prob (Python) | \|diff\| | Status |
|-----|-----|------------------------------|-------------------------------|----------|--------|
| 0.99 | `1.75e-14` | `0.925933480` | `0.925933480` | `2.55e-15` | PASS |
| 0.80 | `7.81e-17` | `0.929837037` | `0.929837037` | `0.0` | PASS |
| 0.05 | `1.17e-19` | `0.999128704` | `0.999128704` | `0.0` | PASS |

Scope: n=2 only, 3 eta values spanning Phase 18's grid (matching
`19-CONTEXT.md`'s locked scope for this leg) — both weight-1 and mixed
scope reached, at full parity with what Phase 18 reported (including
herald-compounding behavior).

**Verdict: GO.**

## What this study does and does not establish

**Establishes:** numerical agreement, at the level of floating-point
noise, between two independently-built simulators (Perceval/Python and
Yao.jl or BosonSampling.jl/Julia) on this repo's exact and lossy IQP
distributions, at small n (n=2/n=3, single fixed test cases), covering
every math layer this project relies on — qubit-side IQP, photonic-level
weight-1 and weight-2 encoding, and photon-loss under both scopes. Where
loss is involved, agreement was reached using BosonSampling.jl's own
structurally-different native loss mechanism (a beamsplitter-to-
environment-mode model), not Perceval's `pcvl.LC` math replayed in Julia
— the strongest form of independence this phase's design allows for.

**Does not establish:** a formal proof of either implementation's
correctness, agreement at any n beyond what was tested, agreement for
weight-2 pairs other than `(i,j)=(0,1)` or for non-locked pair angles, or
anything about circuits/parameter regimes this project does not itself
use. This is a small-n numerical cross-check between two concrete
implementations, not an independent formal verification of the underlying
photonic quantum mechanics.

**No leg stalled or produced an unresolved disagreement.** All three
requirements' underlying plans (19-02 through 19-05) reached a real,
measured TVD comparison and a full GO verdict, including the phase's own
flagged highest-risk piece (the weight-2 Knill-CZ leg, Plan 19-04) — the
one real bug found along the way (a matrix transpose-convention mismatch)
was diagnosed and fixed within a single focused debugging pass, well
inside `19-CONTEXT.md`'s time-box, not left as a documented, unresolved
disagreement.

## Overall status

| Requirement | Scope | Verdict |
|---|---|---|
| VERIFY-02 | Yao.jl qubit-side, n=2/n=3 | **GO** |
| VERIFY-03 (weight-1) | BosonSampling.jl photonic, weight-1, n=2/n=3 | **GO** |
| VERIFY-03 (weight-2) | BosonSampling.jl photonic, weight-2 Knill-CZ, n=2 locked | **GO** |
| VERIFY-04 | BosonSampling.jl native loss, weight-1 + mixed, n=2, eta in {0.99, 0.80, 0.05} | **GO** |

All three of Phase 19's requirements (VERIFY-02, VERIFY-03, VERIFY-04) are
fully satisfied.
