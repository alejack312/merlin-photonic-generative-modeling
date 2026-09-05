# v4.0 plan: Codex adversarial review, disposition (2026-09-03)

Review: `v4-plan-codex-review.md` (verbatim Codex output, `codex exec -s read-only`, prompt asked for null results per metric, silent-failure paths, underspecified steps, tolerances, literature strength, feasibility). Plan revised to revision 2 in `docs/v4-plan-train-classical-deploy-photonic.md`.

| # | Finding (severity) | Verdict | Action in plan rev 2 |
|---|---|---|---|
| A1 | Only TVD has a null; other metrics' nulls are equalities (BLOCKER) | Accepted | `test_control_point_every_cell` asserts every ideal/deployed pair equal at (V,g2)=(1,0) in every cell, plus a perturbation test that must fail; 5.4 states which metrics are pairs vs absolute |
| A2-A4 | Figures 1-3 lack an ideal-channel control | Accepted | Control point (1.0, 0) is asserted, drawn on Fig 1, and the (0,0) cluster is drawn on Fig 2 |
| A5 | Heralded-CZ overlay has no null | Accepted | `owner_null_throughput_hcz` and `owner_null_throughput_cp` both required |
| A6 | NAT has no null (BLOCKER) | Accepted | `owner_null_nat_ideal`; NAT on ideal maps must reproduce the ideal-trained result within quantified optimizer noise; metrics named |
| B1 | Scalar Choi renormalisation is not trace-preserving; success is input-dependent (BLOCKER) | Accepted and verified: success 0.1111-0.1222 across inputs at V=0.9 | Method changed: gates are reconstructed as trace-decreasing CP maps, composed unnormalised, normalised once; p_success = composed trace, cross-checked against full-Fock success at n=2,3 |
| B2 | Chi Pauli ordering unverifiable from a diagonal gate | Resolved by construction | No chi matrix is used; prep states and POVMs come from `compute_unitary()`; Perceval tomography is a fidelity cross-check only |
| B3 | Trace test on one input only | Accepted | Trace and Hermiticity tested on all 16 matrix units and 16 product inputs; CP via Choi eigenvalues |
| B4 | Rounded alpha vs `alpha == 4*theta` contradiction (BLOCKER) | Accepted | `theta_eff = alpha_key/4` is deployed; ideal reference uses trained theta; `tvd_rounding_only` column per cell with a flag rule |
| B5 | Shared bit-order mistake could pass | Accepted | Hand-computed asymmetric n=3 fixture compared by named bitstring in both convention and deployment tests |
| B6 | Product of mean gate successes is not the composed success | Accepted | Removed; success is the composed trace, tested against full Fock |
| B7 | Coverage/fidelity underspecified | Accepted | Population formulas written into 5.4 with S, Q, and the stated deviation from Raj et al. |
| B8 | Shared-qubit check too narrow | Accepted | V-only, g2-only, mixed, two alphas; pre-registered bands <0.01 / 0.01-0.05 / >0.05 |
| B9 | Erasure conservation test is vacuous | Accepted | Exact per-pattern formula and hand-enumerated tests including the shared-qubit case |
| C1-C2 | CSV schema ambiguous | Accepted | Exact column list; eta as throughput columns; erasure to npz; 15 120 rows |
| C3 | Aggregation undefined | Accepted | Primary kernel, data_dependent init, mean +- std over 5 seeds; appendix for the rest |
| C4 | Ising target ambiguous | Accepted | One length-19 J vector, prefixes; samples only for MC training at n=16,20 |
| C5 | Two-pair Fock mapping unspecified | Accepted | Exact mode map and post-selection written into 4.5 |
| C6 | NAT design unspecified | Accepted | Section 6 fixed: warm start, Adam lr 0.02, 150 steps, 5 seeds, precomputed maps, cost formula |
| D1 | 1e-9 on reconstructed channels unjustified | Accepted with evidence | SLOS is deterministic exact simulation (residual 3e-16 measured); `test_repeatable` at 1e-13 documents it |
| D2 | Shared-qubit thresholds unjustified | Accepted | Bands pre-registered with interpretation |
| D3 | KL floor / support threshold sensitivity | Accepted | KL at two floors as two columns |
| D4 | Headline cutoffs invite cherry-picking | Accepted | Aggregation fixed first; headline pre-registered on one cell (n=10, k=9, Ascella, median over seeds); descriptive, not a test |
| D5 | Rounding error has no threshold | Accepted | Per-cell `rounding_flag` at 10% of the noise gap |
| E1-E5 | Literature claims stronger than abstracts (one BLOCKER) | Accepted | "Nobody has" replaced with scoped statement; Recio-Armengol and Salavrakos sentences weakened; full reads required before the write-up relies on them; Raj and Maring full texts were read 2026-09-03 |
| F1 | 64 alpha bins not 63 | Accepted | `alpha_key` reduces mod 2pi and wraps: exactly 63 keys, tested |
| F2 | Row count wrong | Accepted | 840 trained cells x 18 = 15 120 rows; 900 trained files |
| F3 | Timing must use slowest condition | Accepted | Timing gate measured at (0.84, 0.025); direct reconstruction is 2.3 s, budget ~45 min |
| F4 | Memory bound unstated | Accepted | einsum on the (2,)*2n tensor; 4^n x 4^n forbidden and tested; peak RSS asserted at n=10 |
| F5 | NAT cost unbudgeted | Accepted | 29 250 evaluations; per-call time measured in Phase 28 |

Verified by probe before accepting B1/B2/B6: direct linear-inversion reconstruction of the bare CP gate from absolute Perceval probabilities (16 product inputs x 9 readout pairs, prep/readout unitaries from `compute_unitary()`) reproduces `(1/9) U rho U^dag` to 5e-16 at alpha = pi/3 and pi, is completely positive to 2e-15 at V = 0.9, takes 2.3 s per gate, and gives mean conditional fidelity 0.9703 at V = 0.9 vs Perceval tomography's 0.9707.
