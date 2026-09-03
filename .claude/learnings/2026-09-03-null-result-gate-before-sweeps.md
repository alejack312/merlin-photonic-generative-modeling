# Null-result gate before any sweep

**Problem type:** a measurement pipeline produces a clean, plausible curve (exponential decay, monotone convergence) that gets interpreted as a property of the system under study, when it is a property of the pipeline (loss normalization, post-selection, metric definition). Four reviewers (Sonnet, Opus, Sol, a systematic self-verification pass) checked internal consistency and missed it; the repo was internally consistent.

**Two concrete instances (v3.0, corrected in v3.1):**
- TRAIN: Gaussian kernel with sigma below grid bin spacing is the identity, so MMD² = L2 on a product distribution → gradient variance ∝ 2^-n with no circuit content.
- HARD: post-selecting on all photons arriving returns the lossless distribution, so `tvd_to_lossless = ½(1 − eta^(n+2))` and anticoncentration is invariant by construction.

**Rule:** before running any sweep or measurement phase, write the null result: the closed form the pipeline outputs if the object under study contributes nothing. Write it as a test against the data the sweep will produce (red/green, Willison §09). A measurement that matches the null is a pipeline check, not a finding. If no null can be written, that is itself a finding: the measurement is not yet defined well enough to run.

**Decision rules:**
- Loss/normalization is part of the pipeline. Ask "what does this loss do to a trivial model?" (a product distribution, a uniform distribution, a delta) before crediting the circuit.
- Any conditioning step (post-selection, heralding, filtering to a subspace) can make a preserved property tautological. Ask "what does conditioning alone guarantee?"
- Reviewers who share the author's frame will not catch this. The review prompt has to hand them the null-result question explicitly.
- The owner writes the null, not the agent: it is the one derivation that has to be the owner's, because it is the sentence they will be asked about. Derivation-by-experiment (guess, test against data, revise) is an acceptable substitute for symbolic derivation.

**Tells that the pipeline is what was measured:** theta-dependence of the reported quantity is ~1e-15 across random draws; the curve is fit by a two-parameter closed form to printed precision; the "finding" holds identically for a control that has no mechanism (weight-1 with no entangling gate).

**Verification:** `tests/v3_correction/test_null_results.py` — each null is a parametrized test over every shipped CSV row.

**Scope:** cross-project. Copy the rule, not the formulas.
