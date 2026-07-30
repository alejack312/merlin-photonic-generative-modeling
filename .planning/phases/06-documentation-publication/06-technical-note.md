# Technical note to Vincent Espitalier

Draft, LinkedIn-message style.

---

Hey Vincent, following up on the MMD-based generative modeling work I mentioned. I built a photonic version in MerLin: same closed-form MMD² approach from my earlier gate-model (IQP) project, this time training a linear-optical circuit end-to-end on a two-ring toy dataset instead of bitstrings. The held-out MMD² comes out close to the real-data floor, and a fix to how the circuit's raw outputs map onto 2D space measurably improved the ring structure, though it's not fully clean yet. Wrote it up here: https://github.com/alejack312/merlin-photonic-generative-modeling

---

## Phase 7 addendum (2026-07-30)

Follow-up work testing the two open questions the v1.0 self-audit flagged about the ring-structure fix mentioned above — I don't take a result at face value without checking why it happened, so I ran two direct tests rather than leaving the mechanism as an assumption:

- **Neighbor-locality test** (Jacobian-based): does reordering the circuit's raw outputs actually make list-neighboring output bins move together when the circuit's parameters are perturbed — the property the fix's benefit was assumed to depend on?
- **Sigma re-sweep**: does the reported improvement depend on a stale, never-re-tuned kernel bandwidth rather than the reordering itself?

**What I found:**
- The assumed mechanism isn't confirmed. Adjacent bins do show a small, statistically detectable tendency to share sensitivity structure (p=0.0084), but the effect is roughly 10x too small to count as practically meaningful. I can't currently explain *why* the reordering fix works — only that it does, numerically.
- The improvement isn't a stale-bandwidth artifact — re-tuning at the correct grid width picks the same kernel bandwidth already in use. But it's also not a clean win: ring concentration improved at 4 of 5 tested bandwidths, while the amount of mass leaking into the gap between the rings got worse at every single one.

Full detail: `results/phase7_neighbor_locality_summary.md`, `results/phase7_sigma_resweep_summary.md`, `.planning/phases/07-mechanism-validation/`.

**Candidate revision**, folding this in honestly without overclaiming (swap in for the last sentence above, or send as a natural follow-up once Vincent responds):

> ...though it's not fully clean yet — mass concentration on the rings improved, but more mass also leaks into the gap between them, and I haven't pinned down the mechanism behind the improvement despite testing it directly (ruled out a stale-kernel-bandwidth explanation, but a Jacobian-based locality test didn't confirm the effect I assumed was driving it).

Owner call: whether to fold this into the first message, hold it for a natural follow-up, or leave the original short version as-is — it doesn't technically overclaim (`"though it's not fully clean yet"` already hedges), so this addendum is additional honesty rather than a correction of something false.

---

Ready to send via: LinkedIn message. **Note:** the original draft above predates Phase 7 — decide whether to send as-is or fold in the candidate revision before sending.
