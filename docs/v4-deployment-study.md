# v4 deployment/compiler slice

This additive slice implements the Phase 27 logical/compiler and ideal-instrument boundary. It does not select D1 and does not claim a general noisy or full-Fock deployment model.

The compiler accepts finite weight-1 and weight-2 IQP generators. For a pair angle t it records the identity

exp(i t ZiZj) = exp(-i t) exp(i t Zi) exp(i t Zj) CP(4t).

The logical-1 optical phase is recorded as PS(-2t). Pair angles use the 63-key catalog 0.1*j, j=0..62, with circular-nearest lookup. The wrapped CP key and the lifted compensation angle are separate fields; winding is never discarded.

compose_instruments applies local unnormalized maps directly to density-matrix blocks and normalizes once at the end. It returns normalized probabilities plus model success. It never constructs a 4^n square superoperator. Unsupported weights/topologies fail before execution.

reconstruct_cp_map runs the 16 product-input / 9 Pauli-setting / 4-outcome tomography contract and retains zero outcomes and global-success metadata. The ideal bare CP map has an exact Kraus reference; when Perceval is installed, its v1.2 catalog circuit is probed and the status is recorded. A failed optional backend is INCONCLUSIVE, not a substituted physical PASS. Physicality checks are Choi positivity, E_dagger(I) <= I, and Hermiticity preservation. Fidelity is the success-weighted Haar definition from the binding plan.

The full-Fock adapter is intentionally scoped to the existing n=2/3 single-CP diagnostic at ideal source/loss settings. Nonzero g2 or loss returns INCONCLUSIVE because D1 has not selected a joint source model. The erasure helper is explicitly synthetic and conditional on gate success; it adds a FAILURE category and does not claim to recover collision/multiphoton failed-gate outputs. Throughput exposes fixed-photon eta^n and the separate heralded-CZ resource formula.

Run the bounded smoke with:

    venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py
    venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_deploy.py

The smoke writes results/v4_tcdp/deploy/validation_manifest.json. It is a validation manifest, not a production map sweep.
