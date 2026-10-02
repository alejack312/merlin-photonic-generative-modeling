# R1 bucket 3 run accounting

32 defined cells run; 0 defined cells unrun. The other 32 circuit/size/profile/detector cells are undefined in the fixture registry and are enumerated in cells_not_defined.csv.

The e7a07e7 pilot was reused because all simulation/test code hashes matched. No timing pilot was rerun. Pilot projection including threshold PNR companions: 112.940580002 seconds. The accepted profile evaluations completed in 15.584709400 seconds; their already evaluated PNR rows served as threshold companions.

NULL 1-4 passed before acceptance: 17 existing tests passed, zero skipped, plus an explicit NULL 3 coincidence check through the same evaluator at V=.4. No null failed. NULL 4 is validated at c=n (complete pulse emissions); profile results retain the declared c=1 cutoff and report omitted source mass without renormalization.

Ignored mass range: 0 to 0.0002795752742321819. No row is flagged at the >=1e-3 threshold.

Full-suite verification: 875 passed, 1 skipped in 621.35 seconds (10:21), exit 0. Saved-table audit: PASS for 32 unique cells, normalized distributions, threshold coarse-graining, source/retained mass reconciliation, null-check binding, fixed-n baseline metadata, per-row Belenos loss/eta qualifications, extra-photon provenance, and source/artifact hashes. The NULL 3 owner insertion was also verified to be the only change to its document in commit 45a2ab9.

Focused-time estimate through final local commit: about 40 minutes of the 75-minute bucket cap, comprising the earlier approximately 16-minute preflight and this active continuation (07:57:50 UTC to approximately 08:22 UTC). Owner clarification wait and earlier transit time are excluded. No overrun. No interpretation or ranking is supplied.

No code changes. NULL 3 is restricted to the solvable beam-splitter case. Generic partial-V n=3 CP distributions are pipeline checks against NULL 1-4, not independently validated distributions. Acceptance definitions and latent true-n threshold conditioning are stated in manifest.json and each row. With-brightness acceptance remains N/A at unregistered source-emission boundaries, including all Belenos rows.

manifest.json is the immutable run manifest. verification.json binds the final verification/accounting files to that manifest; the prior preflight directory remains intact. Local commit only; no push.
