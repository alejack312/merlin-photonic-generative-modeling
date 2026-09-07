# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Repo state

As of 2026-09-07, branch `codex/v4-implementation` contains the additive v4.0 implementation through the milestone verification pass: bounded ring comparisons, source-smoke retraining evidence, matched NAT arms, fail-closed provenance, full raw-content identities, strict atomic continuation, complete ring artifact/summary reuse validation, paired NAT binding, fixed-photon n=2/n=3 Perceval controls, n=4 photonic ring smoke evaluation, and the n=4/6/8/10 resource pilot. The v4 evidence ledger is [.planning/v4-requirement-evidence.md](.planning/v4-requirement-evidence.md); broader multiphoton/full-Fock, n=6/n=8 photonic, complete sibling, NAT efficacy, and owner-authored interpretation requirements remain explicitly qualified.

As of 2026-08-24 the repo has shipped three milestones (v1.0 generator, v2.0 encoding design, v2.1 weight-2 implementation) plus v3.0 (IQP circuit study: trainability, hardness-under-loss, ARB-01, Julia cross-checks, write-up), and was repackaged into an installable `merlin_iqp` library (src-layout) with phase scripts moved to `scripts/`. Real commands:

- **Python env:** `venv/Scripts/python.exe` (Python 3.12; MerLin caps `python>=3.10,<=3.12`, `torch<2.13`).
- **Install (editable):** `venv/Scripts/python.exe -m pip install -e . --no-deps` — required once per venv for `import merlin_iqp` to resolve; `pytest.ini`'s `pythonpath = src` is a fallback for test runs without it.
- **Tests:** `venv/Scripts/python.exe -m pytest -q` — full-suite execution remains the required gate; v4 focused evidence is recorded in the ledger. (`testpaths = tests` per `pytest.ini`.)
- **Library code:** `src/merlin_iqp/` — `encoding/` (shared IQP-to-photonic circuits), `generator/` (v1.0), `trainability/` (v3.0), `hardness/` (v3.0), `classical/` (v4 NumPy trainer), `experiments/` (v4 rings and sibling inventory), and `deploy/` (v4 compiler/qualified CP-map boundary). No existing pipeline was migrated.
- **Study scripts:** `scripts/` — phase-tagged sweep/analysis/de-risking CLIs, not library code. Run from repo root, e.g. `python scripts/natural_order_train.py`.
- **Trainability study:** `scripts/gradient_variance_sweep.py` (raw sweep) → `scripts/trainability_analysis.py` / `scripts/trainability_analysis_1701.py` (curve-fit analysis).
- **Hardness-under-loss study:** `scripts/loss_sweep.py` (raw sweep) → `scripts/hardness_analysis.py` (TVD-vs-η/anticoncentration analysis).
- **ARB-01 (arbitrary-θ weight-2 gate):** `scripts/cp_alpha_sweep.py`.
- **v4 bounded CLIs:** `scripts/v4_tcdp/train_rings.py`, `scripts/v4_tcdp/inventory_sibling.py`, `scripts/v4_tcdp/retrain_sibling.py`, `scripts/v4_tcdp/run_nat.py`, and `scripts/v4_tcdp/compare_backends.py`. Results are isolated under `results/v4_tcdp/`; source retraining is an explicit sibling-root integration, not a default-suite dependency.
- **Julia independent verifier:** `julia --project=julia julia/verify_qubit_iqp.jl` (and the other `julia/verify_*.jl` scripts) — Julia 1.10 LTS, Yao.jl, BosonSampling.jl.
- **Forge (ancilla mode-mapping bookkeeping check):** `forge/ancilla_mapping.frg`.
- **Results synthesis:** [docs/technical-findings.md](docs/technical-findings.md) remains the legacy canonical write-up; v4 evidence is in [docs/v4-tcdp-study.md](docs/v4-tcdp-study.md), with [docs/v4-rings-study.md](docs/v4-rings-study.md), [docs/v4-sibling-reproduction.md](docs/v4-sibling-reproduction.md), and [docs/v4-backend-comparison.md](docs/v4-backend-comparison.md).

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

## Do not shortcut — this is the owner's job, not Codex's
- Why a specific photonic encoding or circuit ansatz fits the chosen problem
- Interpreting benchmark/metric results — Codex may compute and plot them, but the owner writes the interpretation first, Codex checks it
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

## Jul 25 is not a formality

This is the historical stall point — the same pattern that killed a prior self-directed track (PennyLane) at the equivalent stage. If there's no working end-to-end run by then, say that plainly. Don't report partial progress as "on track" if it isn't.

## Push back

Be a direct, rigorous collaborator, not a yes-man. If the owner tries to skip understanding a core piece or asks Codex to just "handle" something that matters, name it explicitly rather than complying quietly.
