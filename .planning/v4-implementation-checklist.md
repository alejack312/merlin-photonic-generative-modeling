# v4.0 implementation checklist

This is the execution checklist for the revision-4 canonical plan and the additive-pipelines design. A requirement is `PASS` only when its named evidence exists and the applicable tests/checks pass. Missing inputs, unsupported capabilities, and owner-gated decisions remain `FAIL` or `INCONCLUSIVE`; they are never represented as zero-valued results.

| Phase | Requirements | Concrete acceptance evidence |
|---|---|---|
| 26 — shared core, classical trainer, inventory | TRAIN-01..04, ADD-01, MOD-01..04, REPRO-01..02 | `src/merlin_iqp/classical/` imports without Perceval/JAX; weighted-target, spatial/Walsh/Hamming, gradient, optimizer-resume tests; `PROVENANCE.md`; `sibling_inventory.json`, source hashes/config manifests, and compatibility schema; legacy test suite and import/CLI checks unchanged |
| 27 — compilation and physical gates | CHAN-01..04; compiler portions of DEPLOY-01..04 | independent ideal qubit/photonic fixtures pass; supported capability manifest and unsupported-case failures; source-once/projection diagnostics; Choi positivity, `E†(I) <= I`, Hermiticity, held-out reconstruction, success-weighted Haar fidelity; signed/lifted angle fixtures; representative map timing before cache build |
| 28 — rings and deployment | RING-01..04, DEPLOY-01..05, REFRAME-03 | exact 400-point/320–80 ring artifact and codec hashes; classical-only `train_rings.py` smoke/main outputs; frozen qubit/ideal-photonic comparison; density-map memory/timing evidence; n=2/3 full-Fock conditional TVD plus absolute acceptance; topology/projection manifest; erasure categories and throughput artifacts |
| 29 — source reproduction and owner controls | REPRO-03..05, NULL-03..09 | faithful `training_smoke` replay; bandwidth/AC replay and retraining ledgers; every Gaussian-related source row dispositioned as exact/adapted/reference-only/blocked; owner-authored null fixture and hypothesis record; ideal control point passes in every cell and a deliberate control mutation fails |
| 30 — matched benchmark and qualified extension | SWEEP-01..05, COMPARE-01..04 | frozen design/schema manifests; ring/sibling arms share G/theta/data/Hamming kernel; raw/compiled/noisy vectors and metrics remain distinct; exact vs sampled budgets and paired seeds recorded; reproducible CSV/NPZ/JSON plus regenerated figures; unsupported/missing arms explicit |
| 31 — noise-aware training | NAT-01..03 | D2-approved optimizer moves pair keys or validated continuous angles; same-parameter ideal and equal-budget continued-ideal controls; n=4 end-to-end run; n=4/6/8 table or prescribed attempted/stopped record; timing and stop-rule evidence in `.planning/PROJECT.md` |
| 32 — synthesis and review | WRITE-07..09, REVIEW-02 | owner explanation transcript before interpretive prose; three workstream reports plus `docs/tcdp-study.md`; mirrors contain artifact-linked verified claims only; Fable/Opus and Codex review dispositions; former optional communication gate retired by owner on 2026-09-08 |

## Universal gates

- Preserve existing pipelines, historical result hashes, and unrelated worktree changes; verify with `git diff`, legacy imports/CLIs, and the full test suite.
- Record commit, sibling source, environment, data/checkpoint, implementation, and cache hashes in manifests; reject stale or duplicate artifacts.
- Keep raw trained, ideal compiled, and noisy compiled distributions separate; no per-gate normalization and no unsupported full-Fock extrapolation.
- Run `venv/Scripts/python.exe -m pytest -q` and any configured checks at integration milestones. Record each failed or unavailable criterion with its measured evidence and status.
