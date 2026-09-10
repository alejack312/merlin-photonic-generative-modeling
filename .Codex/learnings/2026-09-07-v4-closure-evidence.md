# v4 closure requires evidence layers, not status labels
Date: 2026-09-07 · Scope: project · Recurs when: a computational milestone combines analytic references, direct physical simulation, bounded runs, and owner interpretation

## Context & constraints
- v4 has fixed-photon `g2=0` Perceval controls, analytic unnormalized CP maps, n=4 ring deployment, sibling replay, comparison artifacts, and NAT continuations.
- The binding plan forbids treating analytic-map self-consistency, unit tests, smoke runs, or checkpoint replay as broader physical/retraining evidence.
- Owner null predictions and explanatory prose must be prospective and owner-authored.

## Approach
1. Run direct source-once full-Fock controls and record conditional vectors, absolute accepted mass, projection mode, and hashes separately.
2. Compare final-only and intermediate projection directly; preserve a material discrepancy as a boundary, not as a hidden normalization choice.
3. Keep raw, compiled, deployed-map, and direct-photonic arms distinct; add provenance and exact output inventories before reuse.
4. Treat stop rules as executable budget contracts: record elapsed wall time and whether the stop condition actually triggered.
5. Classify every remaining row as PASS, FAIL, INCONCLUSIVE, NOT IMPLEMENTED, or BLOCKED with a concrete next action and dependency.

## Decision rules that generalize
- IF direct final-only agrees with an analytic map on tested fixtures but intermediate projection differs, THEN support only the tested final-only boundary; do not claim a general composition theorem.
- IF fixed-photon loss is uniform and conditioning is on accepted events, THEN report success/throughput separately from conditional quality.
- IF a sibling checkpoint is replayed, THEN label it replay/adapted replay unless the source training trajectory is rerun with exact inputs.
- IF n=4 is green before the two-day deadline, THEN do not launch a two-day wait; prove the n=8 time bound with machine-readable timing instead.
- IF the owner lacks the scientific foundation for a prospective null, THEN keep the row BLOCKED and schedule learning; never backdate an agent-written prediction.

## Mistakes avoided / dead ends
- Selecting final-only was not treated as proof that intermediate projection or arbitrary topologies compose identically.
- A bounded n=8 run without elapsed provenance was not treated as complete stop-rule evidence.
- Literature support was not substituted for the owner’s own prediction or explanation.

## Verification
- Full suite: `venv/Scripts/python.exe -m pytest -q` → `681 passed, 1 skipped` with writable `PCVL_PERSISTENT_PATH`.
- Explicit sibling integration → `21 passed`; sibling remained at `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336` and clean.
- Direct physical controls: n=2/n=3 PASS; shared final/intermediate conditional TVD `0.585411845271861`.
- Timed n=8 NAT report: `264.498991300003` seconds under `1200` seconds, both matched arms completed.
- Recursive v4 JSON validation: `191` files parsed with no nonfinite values.

## Next time (for a weaker model)
- Do: establish the evidence layers and closure checklist before changing scientific status.
- Don't: turn a passing control or a bounded artifact into a broader scientific claim.

## Changed files
- `.planning/v4-closure-checklist.md` — requirement-level remaining-work map.
- `scripts/v4_tcdp/run_nat.py` — machine-readable elapsed timing in matched reports.
