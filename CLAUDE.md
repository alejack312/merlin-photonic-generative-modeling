# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo state

As of 2026-08-24 the repo has shipped three milestones (v1.0 generator, v2.0 encoding design, v2.1 weight-2 implementation) plus v3.0 (IQP circuit study: trainability, hardness-under-loss, ARB-01, Julia cross-checks, write-up), and was repackaged into an installable `merlin_iqp` library (src-layout) with phase scripts moved to `scripts/`. Real commands:

- **Python env:** `venv/Scripts/python.exe` (Python 3.12; MerLin caps `python>=3.10,<=3.12`, `torch<2.13`).
- **Install (editable):** `venv/Scripts/python.exe -m pip install -e . --no-deps` — required once per venv for `import merlin_iqp` to resolve; `pytest.ini`'s `pythonpath = src` is a fallback for test runs without it.
- **Tests:** `venv/Scripts/python.exe -m pytest -q` — 296 tests (`testpaths = tests` per `pytest.ini`).
- **Library code:** `src/merlin_iqp/` — `encoding/` (shared IQP-to-photonic circuits), `generator/` (v1.0), `trainability/` (v3.0), `hardness/` (v3.0). No dependency on anything outside itself.
- **Study scripts:** `scripts/` — phase-tagged sweep/analysis/de-risking CLIs, not library code. Run from repo root, e.g. `python scripts/natural_order_train.py`.
- **Trainability study:** `scripts/gradient_variance_sweep.py` (raw sweep) → `scripts/trainability_analysis.py` / `scripts/trainability_analysis_1701.py` (curve-fit analysis).
- **Hardness-under-loss study:** `scripts/loss_sweep.py` (raw sweep) → `scripts/hardness_analysis.py` (TVD-vs-η/anticoncentration analysis).
- **ARB-01 (arbitrary-θ weight-2 gate):** `scripts/cp_alpha_sweep.py`.
- **Julia independent verifier:** `julia --project=julia julia/verify_qubit_iqp.jl` (and the other `julia/verify_*.jl` scripts) — Julia 1.10 LTS, Yao.jl, BosonSampling.jl.
- **Forge (ancilla mode-mapping bookkeeping check):** `forge/ancilla_mapping.frg`.
- **Results synthesis:** [docs/technical-findings.md](docs/technical-findings.md) is the canonical write-up; it links out to `docs/trainability-study.md`, `docs/hardness-under-loss-study.md`, `docs/iqp-photonic-encoding.md`, and `docs/julia-cross-check-study.md` for full detail.

**v3.1 Correction (2026-09-03 → shipped 2026-09-04):** an external audit found the v3.0 trainability and hardness-under-loss headline findings are pipeline artifacts with closed-form null results. Corrected additively across all affected documents; standing null-result gate added below. Full detail: `.planning/milestones/v3.1-{ROADMAP,REQUIREMENTS,MILESTONE-AUDIT}.md`. One item (NULL-01's mixed-scope self-explanation) remains open, tracked separately, not blocking.

**v3.2 Correction — Audit Response (opened 2026-09-05):** a second independent audit (GPT-6 Astra) found the v3.1 correction itself overreached in two places — an exact classical reference mistaken for a mechanism-removing control, and the `mixed` scope's "hardness candidate" framing never checked whether its one-fixed-pair entangling structure actually scales with `n` (it doesn't) — plus real code-level defects (a plateau classifier that labels increasing curves "plateau," among others). Requirements: `.planning/REQUIREMENTS.md`; context: `.planning/phases/25-v3-2-correction/25-CONTEXT.md`; audit: `docs/audits/2026-09-05-codebase-audit.md`. Conceptual corrections (CONCEPT-01..03) are owner-only; mechanical fixes (CORR-08..17) are Claude-executable and don't gate on the conceptual track.

Keep this section current at each new milestone — don't leave it stale.

## Why this project exists

This is a credential-building exercise ahead of conversations with Vincent Espitalier and a Spring 2027 Quandela placement — the deliverable is defensible fluency in MerLin (Quandela's photonic/CV QML framework), not just a working repo. **Deadline: September 1, 2026.** Full scope, milestones, and measurable deliverables are in [MerLin_SMART_Spec_Sept1.md](MerLin_SMART_Spec_Sept1.md) — read it before planning any work here.

The risk this file guards against: finishing with code the owner can't explain unaided, which is worse than not finishing. Speed on scaffolding/boilerplate is fine; speed on understanding is not.

## Offload freely (no gating needed)
- Environment setup, dependency/version conflicts
- Boilerplate: repo scaffolding, test harnesses, logging, file organization
- MerLin/PyTorch API syntax lookups
- Debugging stack traces and error messages
- Summarizing papers, doc lookups, git operations

## Do not shortcut — this is the owner's job, not Claude's
- Why a specific photonic encoding or circuit ansatz fits the chosen problem
- Interpreting benchmark/metric results — Claude may compute and plot them, but the owner writes the interpretation first, Claude checks it
- Core design decisions: architecture, loss function choice, training strategy
- Anything the owner will need to explain to Vincent or in an interview, unaided

## Attempt-first gating

Before implementing any new **conceptual** component (not boilerplate):
1. Explain the approach/relevant API well enough for the owner to attempt it themselves.
2. Ask the owner to sketch their approach or attempt the core logic first.
3. Only then write the full implementation — either after the owner's attempt, or if they explicitly say "just implement this, I've got the concept already."

Don't force this ritual once the owner has clearly signaled they don't need it for a given piece — but don't drop it by default either.

## Self-explanation checkpoints

After each SMART-spec milestone (Jul 18, Jul 25, Aug 8, Aug 15, Aug 22, Aug 29, Sep 1), don't move to the next one until the owner has explained back, in their own words, what was built and why it works. If they can't, say so directly — don't let it slide.

At each milestone, ask directly: "Can you explain how [specific piece] works right now, unaided?" Hedging is the signal to stop and actually build understanding before moving forward, not a cue to keep going.

## No silent unilateral design decisions

For any nontrivial architecture/design choice, state what tradeoff was considered and why this option was picked. The owner wants visibility into the decision, not just the resulting code.

## Null-result gate (added 2026-09-03)

Before any sweep, measurement, or benchmark phase runs, the owner writes the null result: the closed form the pipeline outputs if the circuit contributes nothing (a product distribution, a uniform distribution, pure post-selection, the metric's own floor). It goes in as a test against the data the sweep will produce, red first. A measurement that matches the null is a pipeline check, not a finding, and is written up as one. If no null can be stated, the measurement is not defined well enough to run yet. Reviewers must be handed the null-result question explicitly. Internal-consistency review did not catch the v3.0 artifacts. Derivation by experiment (guess, test against data, revise) counts; symbolic derivation is not required. Full note: `.claude/learnings/2026-09-03-null-result-gate-before-sweeps.md`.

## Jul 25 is not a formality

This is the historical stall point — the same pattern that killed a prior self-directed track (PennyLane) at the equivalent stage. If there's no working end-to-end run by then, say that plainly. Don't report partial progress as "on track" if it isn't.

## Push back

Be a direct, rigorous collaborator, not a yes-man. If the owner tries to skip understanding a core piece or asks Claude to just "handle" something that matters, name it explicitly rather than complying quietly.
