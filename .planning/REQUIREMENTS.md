# Requirements: MerLin Photonic Generative Modeling

**Defined:** 2026-07-19
**Core Value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.

## v1 Requirements

### Environment

- [x] **ENV-01**: MerLin installed in a version-compatible environment (Python 3.12 venv; `torch<2.13`, `perceval-quandela>=1.2.1`)
- [x] **ENV-02**: Quickstart classifier runs end-to-end locally, confirming gradients flow through the quantum layer

### Generator Architecture

- [x] **GEN-01**: Generator output-representation decided (full-distribution/histogram MMD matching, not single-point averaging or discrete sampling) — see [DESIGN_DECISIONS.md](../DESIGN_DECISIONS.md)
- [x] **GEN-02**: Latent noise sampled and encoded as `QuantumLayer` input each training step
- [x] **GEN-03**: Fixed set of K bin-centers defined, spanning the circles data's (x, y) region
- [x] **GEN-04**: Real-data histogram (`p_real`) precomputed once over the K bin-centers
- [x] **GEN-05**: Closed-form MMD² loss implemented between the model's probability-vector output (`q`) and `p_real`, using a kernel over bin-center coordinates
- [ ] **GEN-06**: Training loop runs end-to-end, producing a real (even if rough) MMD-decreasing run
- [ ] **GEN-07**: Generator's samples visibly approximate the two-ring circles shape

### Benchmark

- [ ] **BMK-01**: At least one benchmark/comparison metric reported (e.g. held-out MMD statistic)
- [ ] **BMK-02**: Qualitative or quantitative comparison noted against MerLin's photonic QGAN reproduction (paper #16, adversarial loss instead of MMD)

### Documentation & Deliverables

- [ ] **DOC-01**: README documenting problem, approach, and results (numbers/plots, not just prose)
- [ ] **DOC-02**: Public GitHub repo (github.com/alejack312) with working, runnable code
- [ ] **DOC-03**: Short technical note (3–5 sentences) ready to send to Vincent Espitalier
- [ ] **DOC-04**: Portfolio case study drafted (IQP-MMD case-study format)

## v2 Requirements

### Stretch Benchmark

- **BMK-03**: Exact replication of MerLin's photonic QGAN paper's MNIST-patch dataset/architecture, for a true apples-to-apples comparison (Aug 8 stretch target if time allows — not required for the core deliverable, which uses the circles dataset already in the quickstart)

## Out of Scope

| Feature | Reason |
|---------|--------|
| IQP gate-model circuit reproduction in MerLin | No established IQP→linear-optics reduction exists; a genuine research contribution, not an extension — parked to its own post-Sept-1 project ([Post_Sept1_IQP_Photonic_Plan.md](../Post_Sept1_IQP_Photonic_Plan.md)) |
| PennyLane independent contributions | Parked, sequenced after the IQP-photonic project wraps (decided 2026-07-19) |
| ket.jl / SDP self-study | Informal free-time research only, no artifact expected |
| Weighted-average → single continuous point output mapping | Collapses the circles' two-ring (multimodal) target into the empty gap between rings — a structural failure mode, not a fixable detail |
| Discrete `shots`-based sampling for the generator | Not differentiable through standard autograd without an additional estimator (REINFORCE/Gumbel-softmax); not worth the added complexity for this timeline |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ENV-01 | Phase 1 | Complete |
| ENV-02 | Phase 1 | Complete |
| GEN-01 | Phase 1 | Complete |
| GEN-02 | Phase 2 | Complete |
| GEN-03 | Phase 2 | Complete |
| GEN-04 | Phase 2 | Complete |
| GEN-05 | Phase 2 | Complete |
| GEN-06 | Phase 3 | Pending |
| GEN-07 | Phase 4 | Pending |
| BMK-01 | Phase 5 | Pending |
| BMK-02 | Phase 5 | Pending |
| DOC-01 | Phase 6 | Pending |
| DOC-02 | Phase 6 | Pending |
| DOC-03 | Phase 6 | Pending |
| DOC-04 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 15 total (7 complete: ENV-01, ENV-02, GEN-01 through GEN-05)
- Mapped to phases: 15/15 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-07-19*
*Last updated: 2026-07-19 after Phase 2 completion — GEN-02 through GEN-05 verified (24/24 tests passing)*
