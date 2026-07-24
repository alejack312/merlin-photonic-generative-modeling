# Conceptual Notes & Clarifications

Explanatory notes for concepts that came up during development and are worth having in plain language — for explaining this project unaided to Vincent Espitalier, in interviews, or to a future version of the owner who has forgotten the details. Distinct from [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md), which logs *what was chosen and why*; this file explains *how the chosen thing actually works*, including misconceptions caught and corrected along the way.

---

## Phase 3's training loop is not "standard ML training" in two specific ways

Structurally, `train.py`'s loop is the same optimizer pattern as any PyTorch training run (`zero_grad()` / `backward()` / `step()`, matching `quickstart.py`). But two things about *what's* being trained are specific to this project:

1. **What's being trained isn't a neural network — it's the parameters of a photonic quantum circuit.** `ML.QuantumLayer.simple(input_size=10, output_size=400)` is a linear-optical circuit (phase shifters/beamsplitters); its trainable `thetas` are circuit parameters, not learned weight matrices. `torch.autograd` differentiates through MerLin's simulation of that circuit the same way it differentiates through any `nn.Module` — but the forward pass is a quantum-optics probability computation, not matrix multiplication through learned weights.

2. **There's no discriminator and no adversarial loss.** This isn't a GAN. Each step: draw a batch of latent `z`, get the circuit's output probability *distribution* (already normalized, 400-dim, one full distribution per `z` — not a discrete sample), average their MMD² distances to the fixed real-data histogram `p_real`, backprop that scalar. This is architecturally closer to a **Generative Moment Matching Network (GMMN)** — direct distribution matching via a fixed kernel statistic — than to a GAN's minimax game. No adversary to destabilize training, which is part of why full-distribution MMD matching was chosen over MerLin's own photonic QGAN reproduction for this project's generator (see DESIGN_DECISIONS.md, 2026-07-19 entry).

---

## `train_step`'s batch-averaging: what actually gets averaged, and why

This came up as a real self-explanation checkpoint gap during Phase 3 (documented in full, including the initial incorrect explanation, in [03-01-SUMMARY.md](.planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md)) — worth stating precisely here since the first-pass explanation was wrong in a way that's easy to slip back into.

**What `z` is:** `z` is the *latent noise input* — a random real-valued vector in ℝ¹⁰, sampled fresh every training step (`sample_latent`), fed into the photonic circuit as its encoding. **It is not a bitstring.** (Easy to confuse with the prior `iqp-mmd-barren-plateau` project, which computed MMD via Hamming-distance kernels over binary bitstrings — that machinery doesn't exist in this project. Here, `mmd2` compares two *continuous probability distributions* over K=400 real-valued 2D bin-centers, via a Gaussian kernel over Euclidean distance.)

**What happens per `z`:** The circuit runs its forward pass *analytically* (no `shots=`, no discrete sampling) and returns `q_i` — a full 400-entry probability distribution, the same kind of object `p_real` is. `mmd2(p_real, q_i, K)` is a distance *between two distributions*, not a sum over strings.

**What the batch does:** Each step draws 32 independent `z`'s, runs the circuit 32 times to get 32 different `q_i`'s (one full distribution per `z`), computes `mmd2(p_real, q_i, K)` for each, and averages those 32 *scalars* into one loss before `.backward()`.

**Why averaging helps — and what it is *not* doing:** There is only **one** shared parameter set, θ (the circuit's trainable phase-shifter values). All 32 `z`'s in a batch run through the *same* θ — the parameters don't vary across the batch, only the latent input does. Averaging is **not** "searching for which θ produced the closest q_i" (there's no set of different θ's to choose among). Because the gradient of a mean is the mean of gradients, averaging 32 per-sample losses before backprop gives a **less noisy estimate of which direction to push the single shared θ** — standard minibatch variance reduction, not model selection. The alternative that was explicitly rejected (DESIGN_DECISIONS.md, 2026-07-24) was averaging the 32 `q_i` vectors into one distribution *before* computing `mmd2` — a different, untested training objective.

**Empirical result:** this batch-averaging choice was validated in practice, not just plausible in theory — Phase 3's real 300-epoch run produced a statistically clean decreasing trend (slope < 0 at p≈1e-128, 62% relative drop from first-decile to last-decile mean loss). See [03-01-SUMMARY.md](.planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md) for the full verbatim `decreasing_trend_check` output.

---

*Notes started: 2026-07-24, during Phase 3 (End-to-End Training Run).*
