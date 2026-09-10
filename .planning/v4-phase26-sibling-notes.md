# Phase 26 sibling inventory notes

Status: inventory boundary implemented; replay execution and scientific interpretation remain open.

Observed on 2026-09-06:

- Sibling checkout `C:\Users\cuqui\iqp-mmd-barren-plateau` is at `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`, with no Git status changes observed before inventory.
- Both packages are present: `src/iqp_bp` and `src/iqp_mmd`.
- The read-only scan recorded 81 source files, 30 configuration files, and 1,314 result/data/checkpoint artifacts, with hashes for each recorded artifact.
- The source environment records Python and installed package versions. JAX/PennyLane and other sibling dependencies remain provenance observations; they are not imported by `merlin_iqp.classical` and no dependency was added here.
- The sibling has no top-level `data/` directory in this checkout. This is an absence observation only. Configured paths and result metadata are retained individually; missing inputs become `blocked` rather than a generated substitute.

Disposition semantics:

- `exact_reproduction`: source configuration and local evidence are sufficient for a later source-faithful replay; `execution_state` remains `not_run` until that replay is actually run.
- `adapted_reproduction`: a named field changes and the changed field is recorded.
- `reference_only`: source study is retained for provenance but its backend/scale or capability is outside this bounded implementation.
- `blocked`: a required input or capability is absent; no replacement is claimed.

The manifests are deliberately not a scientific certification. They do not establish that a result aggregate is correct, that a checkpoint/data split is complete, or that a high-weight/large-n source row can be deployed through the current photonic compiler. Those are later gates.
