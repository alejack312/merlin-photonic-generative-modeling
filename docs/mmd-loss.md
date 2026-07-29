# Why the MMD loss differs between the IQP project and this project

Grounded by directly reading the prior project's source (`~/iqp-mmd-barren-plateau/src/iqp_bp/mmd/kernel.py`, `~/iqp-mmd-barren-plateau/src/iqp_mmd/metrics/mmd_eval.py`) alongside this repo's `generator/mmd.py` — not from memory of either project.

## What's identical

Both projects use the same core object: MMD²(p, q) = E[k(x,x')] + E[k(y,y')] − 2·E[k(x,y)], where k is a positive-definite kernel and x,x' ~ p, y,y' ~ q. Both use a Gaussian-shaped kernel with a bandwidth parameter σ. Both hit the same failure mode at the wrong bandwidth: loss decreases while the learned structure is still wrong. That's it — everything else differs.

## Difference 1: what a "point" is, and what "distance" means

**IQP project:** a point is a bitstring in `{+1,-1}^n` (n qubits). Distance is **Hamming distance** — how many bits differ. `kernel.py`'s `gaussian_kernel`:
```python
def gaussian_kernel(x, y, sigma):
    hamming = np.sum(x != y)
    return float(np.exp(-hamming / (2 * sigma**2)))
```

**This project:** a point is a location in continuous 2D space, represented by one of K bin-centers. Distance is **Euclidean distance**. `generator/mmd.py`'s `gaussian_kernel_matrix`:
```python
def gaussian_kernel_matrix(centers, sigma):
    return torch.exp(-torch.cdist(centers, centers)**2 / (2*sigma**2))
```

Same exponential-decay shape, completely different notion of "how far apart are these two things." Hamming distance is an integer in `{0, ..., n}` — a coarse, symmetric, combinatorial measure with no notion of direction or magnitude beyond bit-flip count. Euclidean distance is continuous and carries real geometric structure (angle, magnitude, triangle inequality in the usual sense).

## Difference 2: how MMD² actually gets computed — sampling vs. exact closed form

**IQP project:** MMD² is estimated from finite samples. `mmd_eval.py`'s `evaluate_mmd_loss` splits ground-truth and model samples into batches, calls `iqpopt.gen_qml.mmd_loss_samples`/`mmd_loss_iqp` on each split, and reports a **mean ± standard error over `n_repeats`** — this is a Monte Carlo estimate of MMD², with genuine sampling noise, which is why repeats and a standard error even exist as a concept there.

For the exact (not sampled) case, `kernel.py` also ships a **Fourier/Walsh spectral decomposition** (`spectral_weights_exact`, `gaussian_spectral_weights`) that computes MMD² analytically for kernels depending only on Hamming distance over the Boolean hypercube — but it's hard-capped: `if n > 20: raise ValueError(...too large to enumerate)`. The comment is the tell: for n qubits there are `2^n` possible bitstrings, so beyond ~20 qubits you literally cannot enumerate the outcome space, exact or otherwise — you're forced into sampling, and the elaborate Walsh-coefficient machinery exists specifically to get an exact answer *without* enumerating `2^n` states, by exploiting that a Hamming-distance kernel is invariant under a symmetry group of the hypercube.

**This project:** `mmd2` is an **exact closed form**, no sampling anywhere:
```python
def mmd2(p, q, kernel_matrix):
    return torch.clamp(p@kernel_matrix@p + q@kernel_matrix@q - 2*p@kernel_matrix@q, min=0)
```
`p` and `q` are full probability vectors over K=400 (or 462) bins — not samples drawn from a distribution, but the distribution itself, already known exactly (p_real from a histogram over real data, q from the circuit's own analytic forward pass). There is no sampling noise in this number at all; it's a deterministic function of the current parameters.

**Why the two projects made different choices here — this is the load-bearing reason, not incidental:** the IQP project's outcome space grows as `2^n` with qubit count — exponential, unbounded, and the entire research question (barren plateaus vs. system size) requires scaling `n` up, so an exact `2^n × 2^n` kernel matrix was never going to be tractable past a couple dozen qubits. Sampling (or the Walsh trick, which is really "exact but only because Hamming-kernels have exploitable symmetry") was a structural necessity forced by the problem itself.

This project deliberately avoided that problem at the design stage: K (the number of spatial bins) does **not** scale with circuit size — it's a fixed discretization choice (400, then 462) of a 2D square, chosen independently of `input_size`/`LATENT_DIM`. A 462×462 kernel matrix is trivial to hold in memory and compute exactly. The price paid for this convenience is discretization error (a continuous 2D plane approximated by finitely many bin-centers) instead of sampling error — a different kind of approximation, not a free lunch, just a cheaper one for this problem size.

## The shared throughline: bandwidth determines what the loss is blind to

This project's own sigma sweep found a non-monotonic result — `ring_mass = 0.459` at σ=0.02, peaking at `0.616` at σ=0.1, falling to `0.328` at σ=0.4 — meaning both too-small and too-large bandwidths produced worse structural matches even when the raw loss number looked reasonable. The IQP project has a documented version of the identical phenomenon, precisely characterized rather than just observed: the Gaussian kernel's bandwidth maps to a Walsh-order decay parameter `tau(sigma) = tanh(1/(4*sigma^2))`, and the kernel's spectral weight for order-`k` correlations scales as `tau^k`. Low `tau` (small sigma) means the loss is dominated by **low-order** structure (roughly: single-qubit/few-qubit marginals) and nearly blind to high-order correlations — so MMD² can be driven to ~0 while high-order structure is still completely wrong. That's the exact mechanism `docs/technical/bandwidth-marginals.md`'s "AC12 bandwidth sweep" was designed to characterize.

Different domain, same abstract lesson, now confirmed twice in two different projects: **the kernel bandwidth isn't a free tuning knob — it silently chooses which scale of structure the loss can see, and a "good" loss value at the wrong bandwidth actively hides the mismatch instead of catching it.**

---

## Feynman-technique explanation

**Plain version.** MMD asks one question: "if I grabbed two things at random — sometimes both from the real pile, sometimes both from the fake pile, sometimes one from each — how similar do they tend to be?" If real-vs-real similarity and fake-vs-fake similarity both look like real-vs-fake similarity, the two piles are indistinguishable, and MMD² is near zero. Both projects ask exactly this question. They disagree on two things: what "similar" means, and how you find out the answer.

**What "similar" means.** In the IQP project, each "thing" is a string of +1s and -1s (a measurement outcome from n qubits). "Similar" = count how many positions differ. Two strings that differ in 1 place out of 20 are very similar; differing in 15 out of 20 is very different. There's no geometry here — it's pure counting.

In this project, each "thing" is a point on a page (a 2D location). "Similar" = ordinary ruler distance. Two points an inch apart are similar; two points across the page are not. This is the geometry you already know from grade school.

Same shaped formula (`exp(-distance / bandwidth)` in both cases), completely different meaning of "distance," because the two projects generate fundamentally different kinds of stuff — bit patterns vs. locations in space.

**How you find out the answer.** In the IQP project, imagine the "pile" of all possible bit patterns is potentially enormous — for 20 qubits, over a million possible patterns; for 30 qubits, over a billion. You cannot physically go count every single one and compare it to every other one. So you do one of two things: (a) grab a random handful of samples from each pile and estimate the answer from that handful (like a political poll — you get an estimate plus a margin of error, which is exactly why their code reports a mean *and* a standard error over repeated draws), or (b) if the piles have a special hidden symmetry (which Hamming-distance similarity does, on bit-strings), use clever math to compute the *exact* answer without ever listing every single pattern — but this trick still breaks down once the pile gets too big (their code literally refuses above 20 qubits, because even the clever trick needs the full pile size as an input at some point).

In this project, the "pile" was never allowed to get that big in the first place. We deliberately chopped the page into a fixed number of squares (400, then 462) no matter how big or complicated the circuit gets — it's a design choice, not a law of nature. Because the pile size is small and fixed, we can just write down the *exact*, complete answer directly, every single time, with a formula — no polling, no sampling error, ever. It's less like a survey and more like a census where you already know every single resident by name.

**Why this matters beyond just "different math."** The IQP project *has* to fight exponential blowup because its whole point is studying what happens as you add more qubits — the size of the problem is the experiment. This project's whole point was building something that trains and visualizes cleanly on a laptop in an afternoon, so keeping the outcome space small and fixed was the right call — but it means every number reported here is exact and reproducible in a way the IQP project's numbers structurally cannot be (theirs always carry sampling noise, ours never do). Neither approach is "better" in the abstract; they're the correct tool for two different research questions.

**Where my understanding could still be wrong, stated honestly.** I read the IQP project's kernel and evaluator code directly this session, but I did not re-derive the Walsh/Fourier spectral math myself line-by-line — I'm taking the docstrings and the `bandwidth-marginals.md` note's stated purpose at face value rather than proving the Krawtchouk-polynomial machinery (`_krawtchouk`) is doing exactly what its docstring claims. If this comparison ever needs to hold up to someone who knows Fourier analysis on the Boolean hypercube well, that piece deserves a closer read before being asserted with full confidence.
