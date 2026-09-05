# Validate photonic research contracts before a sweep
Date: 2026-09-05 · Scope: project · Recurs when: composing noisy post-selected photonic gates into a scalable model

## Context & constraints
- A prior review disposition claimed closure without testing the revised source/angle/NAT contracts together.
- Single-gate fidelity, numerical repeatability and a green historical suite do not establish multi-gate physical equivalence.
- Owner retains source-model, optimizer and initialization choices.

## Approach
1. Trace source preparation, optical evolution and acceptance as separate stages.
2. Probe signs, wrapping and rounding on the smallest asymmetric ideal circuit.
3. Test joint source/loss settings and spectator acceptance, not just each noise axis separately.
4. Compare raw-trained, ideal-compiled and noisy-compiled distributions separately.
5. Recompute counts from axes/parameter dimensions; inspect the actual vendored API and deterministic initialization.

## Decision rules
- If g2>0, do not extend the fixed-n eta^n theorem without a source-sector calculation.
- If success is state-dependent, require Choi CP and E_dagger(I)<=I; product-input trace tests are insufficient.
- If composing post-selected maps, prove the supported projection/topology contract or label the calculation a surrogate.
- If pair angles are quantized, preserve the CP winding in local corrections and verify the optimizer can change keys.
- If a metric is constant over the target support, label it a control; do not require it to detect arbitrary perturbations.
- If exact initialization/updates ignore seeds, record n_unique rather than claim independent repetitions.

## Mistakes avoided
- Treating a repeated-rail projection counterexample as proof that a restricted one-pass chain fails.
- Treating a small-n discrepancy as an error bar for every size and nonlinear metric.
- Replacing missing owner design decisions with agent-authored approval.

## Verification
- `venv/Scripts/python.exe docs/audits/2026-09-05-v4-plan-probes.py` records executable controls/counterexamples in JSON.
- Correct signs agree to 3.75e-16; old signs produce TVD .442651; g2/loss invalidates eta-only scaling.
- Existing suite: 507 passed; this does not validate the unimplemented v4 model.

## Next time
- Do: inspect actual source APIs, joint noise assumptions and reference definitions before allocating a sweep budget.
- Don't: accept “every finding dispositioned” as evidence that revised contracts are mutually consistent.
