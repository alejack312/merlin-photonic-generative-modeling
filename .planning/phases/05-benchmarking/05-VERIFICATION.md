---
phase: 05-benchmarking
verified: 2026-07-28T22:30:13Z
status: passed
score: 6/6 must-haves verified
---

# Phase 5: Benchmarking Verification Report

**Phase Goal:** The model's performance is honestly quantified and situated against a reference point, not presented as a bare "it trained."
**Verified:** 2026-07-28T22:30:13Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Held-out MMD² for trained generator reported as mean±std over repeated latent draws (BMK-01) | VERIFIED | `results/phase5_benchmark_metrics.csv` row `trained`: mmd_mean=0.01251, mmd_std=0.000269, n_draws=20, sigma=0.1. Re-ran `benchmark.py` live — produced mmd=0.0125±0.0003 for trained, consistent within noise. |
| 2 | MMD² bracketed by untrained baseline and real-train-vs-real-test floor | VERIFIED | CSV has `untrained` row (mmd_mean=0.0360) and `floor` row (mmd_mean=0.01137, std=0, n_draws=1) — floor < trained < untrained, correct ordering. |
| 3 | Ring/gap metrics re-measured and reported alongside MMD, carrying forward Phase 4's "not met" framing | VERIFIED | CSV `trained` row has ring_mass_mean=0.6833, gap_mass_mean=0.0514. `phase5_summary.md` explicitly states "this is 'an improvement, still not two distinct rings,' not a fully successful generative result." |
| 4 | Training cost (wall-clock, param count) measured, not estimated | VERIFIED | `results/phase5_training_cost.csv`: wall_clock_seconds=425.93 (real float from `time.time()` diff in `benchmark_timing.py`), param_count=220 (via `sum(p.numel() for p in generator.parameters())`). |
| 5 | BMK-02 comparison vs MerLin QGAN reproduction (paper #16) documented, fallback path explicitly flagged | VERIFIED | `phase5_summary.md` line 33: **"Fallback path used — no matched numeric comparison was computed."** — explicit, bolded, unambiguous. |
| 6 | `phase5_summary.md` citation-ready, real numbers, headline results up top | VERIFIED | Headline table at top of file cites all 7 numbers, each traceable to the two CSVs. No "TBD" or invented values found. |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `benchmark.py` | Held-out MMD² (trained/untrained/floor) + ring/gap, mean±std over draws | VERIFIED | Exists, 117 lines, no stub patterns, imports real infra (`generator.data`, `generator.mmd`, `generator.naturally_ordered_generator`, `generator.noise`, `generator.visualize`). Re-executed successfully (exit 0), reproduced trained MMD≈0.0125 matching CSV within stochastic tolerance. |
| `benchmark_timing.py` | Timed fresh retrain, wall-clock + param count, ring/gap sanity check | VERIFIED | Exists, 118 lines. Logic matches CSV contents exactly: `time.time()` wraps the epoch loop, `param_count = sum(p.numel()...)`, writes to `results/phase5_training_cost.csv`. Scratch checkpoint `results/phase5_timed_checkpoint.pt` exists (7217 bytes, dated 2026-07-29), confirming the script was actually run (not just written). Not re-run live (7 min cost); logic/output cross-checked instead per verification-budget guidance. |
| `results/phase5_benchmark_metrics.csv` | trained/untrained MMD² mean±std, floor MMD², ring/gap mean±std | VERIFIED | 3 data rows + header exactly as specified. All numeric, no placeholders. Reproduced live via re-run (then restored to committed version with `git checkout`). |
| `results/phase5_training_cost.csv` | wall_clock_seconds, param_count, epochs, batch_size, final ring/gap | VERIFIED | 1 data row, all real numbers: wall_clock_seconds=425.93, param_count=220, epochs=300, batch_size=32. |
| `results/phase5_summary.md` | Citation-ready BMK-01 + BMK-02 write-up | VERIFIED | 49 lines, headline table first, every number traces to the two CSVs (cross-checked value-by-value), "fallback" appears explicitly in bold in the BMK-02 section. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `benchmark.py` | `results/phase4_natural_checkpoint.pt` | `build_naturally_ordered_generator().load_state_dict(torch.load(...))` | WIRED | Line 63: `trained.load_state_dict(torch.load(CKPT, map_location="cpu"))`, `CKPT = "results/phase4_natural_checkpoint.pt"`. File exists (7299 bytes). |
| `benchmark.py` | `generator/naturally_ordered_generator.py` | `from generator.naturally_ordered_generator import ...` | WIRED | Line 16-19, import present and used for both trained/untrained generator construction. |
| `results/phase5_summary.md` | `phase5_benchmark_metrics.csv` + `phase5_training_cost.csv` | numbers cited match CSV values | WIRED | Cross-checked: 0.0125±0.0003, 0.0360±0.0048, 0.0114, 0.6833±0.0073, 0.0514±0.0035, 425.93s, 220 params — all match CSV values exactly (rounded to 4 decimals in prose). |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| BMK-01 (held-out MMD² benchmark, mean±std, bracketed) | SATISFIED | None |
| BMK-02 (comparison vs paper #16 QGAN reproduction, fallback explicitly flagged) | SATISFIED | None |

### Anti-Patterns Found

None. No TODO/FIXME/placeholder patterns found in `benchmark.py`, `benchmark_timing.py`, or `results/phase5_summary.md`. No empty returns or stub handlers.

### Human Verification Required

None — this phase's deliverables are numeric artifacts and a documentation write-up, fully verifiable structurally and by direct script re-execution.

### Gaps Summary

No gaps found. All must-haves verified against the actual codebase, not just SUMMARY.md's claims:

- Re-ran `benchmark.py` live (not from memory of SUMMARY claims) — reproduced trained MMD²≈0.0125±0.0003, matching the committed CSV within expected stochastic tolerance (untrained baseline is random-init so it varies run-to-run by design; trained is a fixed checkpoint so its MMD² is stable across runs). Restored the CSV to its git-committed state afterward with `git checkout` since the re-run was for verification only.
- `benchmark_timing.py` was not re-run live (costs ~7 min per SUMMARY.md), but its logic was read line-by-line and matches `phase5_training_cost.csv`'s contents exactly; the scratch checkpoint `results/phase5_timed_checkpoint.pt` on disk (dated 2026-07-29) is independent evidence the script actually executed rather than the CSV being hand-written.
- `pytest` run live: 48 passed, 0 failed (94s), confirming no regression from this phase (which touched no files under `generator/`).
- BMK-02 fallback flag is explicit and bolded in `phase5_summary.md`: "**Fallback path used — no matched numeric comparison was computed.**"
- Phase 4's GEN-07-not-met framing is carried forward honestly throughout `phase5_summary.md`, not implied away.

---

*Verified: 2026-07-28T22:30:13Z*
*Verifier: Claude (gsd-verifier)*
