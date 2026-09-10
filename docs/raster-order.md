# Raster order, radius order, and what was actually changed

Updated 2026-09-10. This note concerns the historical v1 462-outcome model. The new v4 IQP codec is separate. Earlier explanatory text asserted unverified smoothness of adjacent Fock-state indices; that assertion is withdrawn. The [earlier account](https://github.com/alejack312/merlin-photonic-generative-modeling/blob/41c0d1b/docs/raster-order.md) remains available for provenance.

## Mapping outcomes to a picture

A discrete photonic outcome does not intrinsically carry an x,y coordinate. The pipeline assigns each outcome to a grid center. The historical raster construction fixes one coordinate and sweeps the other before moving to the next column. Radius sorting instead orders centers by distance from the grid center.

A thin annulus occupies short separated intervals under a column-wise scan and a more compact range under radius ordering. Finite bins and empirical target occupancy can leave gaps; radius ordering does not guarantee exactly two contiguous bands. Equal radii also do not imply angular proximity, so this mapping cannot by itself enforce uniformity around a ring.

## Permutation invariance versus changing the model

For a permutation matrix P, replacing `(p,q,K)` by `(Pp,Pq,PKP^T)` leaves `(p-q)^T K (p-q)` unchanged. A consistent relabeling therefore cannot improve the loss.

Changing which optical outcome is assigned to each *fixed* geometric center can change the induced spatial model while holding the target geometry fixed. That can alter training. It does not prove that neighboring occupation-state indices respond similarly to parameter changes. Fock states have no universal physically preferred linear ordering, and center-of-mass ordering is a modeling choice rather than a smoothness theorem.

## What the historical comparison establishes

The observed visual/metric change is specific to the chosen mapping, grid, bandwidth, initialization, and training run. The old 400-bin and later 462-bin settings changed more than an index label, so their difference is not a controlled isolation of radius ordering. Claims that the circuit's “natural smoothness” caused improvement require a matched ablation and a parameter-response diagnostic; neither follows from plotting smoother bands.

The v1 fit limitation remains reported in the [README](../README.md). This note supplies no new experiment or causal conclusion.

## V4 boundary

V4 uses an explicit `2^n` row-major, MSB-first bit codec. Spatial distance and Hamming distance induce different kernels on that codec. Changing the bit-to-center mapping generally changes their relationship and must be recorded in the dataset identity. V4 neither adopts the v1 462-outcome ansatz nor establishes that radius sorting resolves its fit limitations. See [MMD loss](mmd-loss.md) and [v4 rings](v4-rings-study.md).
