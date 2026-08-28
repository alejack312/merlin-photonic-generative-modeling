# Contributing

This repo separates a reusable library (`src/merlin_iqp/`) from the phase-tagged experiment scripts (`scripts/`) that used it to produce this project's results. Contributions to the library are welcome; the scripts under `scripts/` are a provenance record of specific runs and are not expected to change except to fix a bug in the run they document.

## Setup

```bash
git clone https://github.com/alejack312/merlin-photonic-generative-modeling.git
cd merlin-photonic-generative-modeling
python -m venv venv
venv/Scripts/activate           # venv\Scripts\activate.bat on cmd.exe, source venv/bin/activate on Linux/macOS
pip install -r requirements.txt
pip install -e .
```

Python 3.10-3.12 (MerLin's own cap), `torch<2.13`.

## Before opening a PR

```bash
python -m pytest -q
```

All tests must pass. There is no separate lint/type-check step configured yet (see Open items below).

## Package layout

- `src/merlin_iqp/encoding/` — the shared IQP-to-photonic circuit encodings (polarization and dual-rail). Everything else in the package builds on this.
- `src/merlin_iqp/generator/` — the MMD-trained generative model (v1.0).
- `src/merlin_iqp/trainability/` — gradient-variance / barren-plateau study utilities (v3.0).
- `src/merlin_iqp/hardness/` — sampling-hardness-under-photon-loss study utilities (v3.0).
- `scripts/` — one-off, phase-tagged CLIs (sweeps, analysis, de-risking probes) that consume the library above, grouped into per-milestone subpackages (`v1_generator/`, `v2_encoding/`, `v3_trainability/`, `v3_hardness/`, `v3_arb_gate/`, `v3_forge_formal/`). New reusable logic belongs in `src/merlin_iqp/`, not here.
- `results/` — the raw output (CSVs, plots, checkpoints, summary docs) each script above produced, in the same per-milestone subfolders as `scripts/` plus `v3_julia_verify/` for the Julia cross-check outputs.
- `tests/` — mirrors `src/merlin_iqp/`'s subpackages (`generator/`, `encoding/`, `trainability/`, `hardness/`) for library tests, and `scripts/`'s own milestone subfolders (under `tests/scripts/`) for tests that exercise a script directly; a change to either needs a matching test in the corresponding subfolder.

Avoid adding a catch-all `utils` module — put a new helper in the subpackage that owns the concept it serves, or give it its own module if it doesn't fit any existing one.

## Conventions

- Every public function and module carries a docstring. Nested/local helper functions can skip one if the enclosing function's docstring already documents the contract.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#summary) (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- Non-obvious design or physics decisions are documented in-line (the "why", not the "what") and, for anything load-bearing, cross-referenced from [`DESIGN_DECISIONS.md`](DESIGN_DECISIONS.md).

## Open items

- No CI workflow yet — tests are run locally.
- No lint/type-check configuration yet.
- No PyPI release yet; install from source via `pip install -e .`.
