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

---

## Updated draft (2026-08-29) — reflects v3.0

The project grew well past the original v1.0 scope since the message above was drafted (a whole second milestone: trainability, hardness-under-loss, a tunable gate, independent Julia verification). Replaces the drafts above rather than extending them — send this one instead.

---

Hey Vincent, wanted to share what I built in MerLin. A photonic generator trained end-to-end with the same closed-form MMD² approach from my earlier gate-model project, this time on a two-ring toy dataset. Held-out MMD² landed close to the real-data floor, though the ring structure is not fully clean yet.

I extended it into a second study of the same circuit family. The trainability signature did not hold up across kernel bandwidths. The sampling-hardness argument only holds once you scope it to circuits with actual entanglement. I re-verified the whole thing independently in Julia, built from scratch rather than ported, and every check agreed.

Writeup: https://github.com/alejack312/merlin-photonic-generative-modeling

---

Superseded by the actual sent text below — the draft above is what was on record before sending, not what Vincent received.

---

## Actual message sent (2026-08-31)

Sent via LinkedIn message. This is the final text, verbatim, including the thesis-statement line folded into the second paragraph and the formal "Good afternoon Mr. Espitalier" opening (a register change from the earlier casual-LinkedIn-message drafts above).

---

Good afternoon Mr. Espitalier,

I hope this message finds you well. I wanted to share what I built in MerLin. It's a photonic generator trained end-to-end with the same closed-form MMD² approach from an earlier gate-model project of mine. This time trained on a two-ring toy dataset. Held-out MMD² landed close to the real-data floor, though the ring structure is not fully clean yet.

I extended it into a second study of the same circuit family. I wanted to see whether IQP circuits' trainability and hardness properties carry over to a discrete photonic construction of the same circuits. The trainability signature did not hold up across kernel bandwidths. The sampling-hardness argument only holds once you scope it to circuits with actual entanglement. I re-verified the whole thing independently in Julia, built from scratch rather than ported, and every check agreed.

Writeup: https://github.com/alejack312/merlin-photonic-generative-modeling


---

**Follow-up sent, same day (2026-08-31):** "Would genuinely welcome any critique." Thread closed for now.
