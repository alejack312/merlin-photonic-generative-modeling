# R1 first profile preflight (2026-10-02)

No profile-result table was produced: NULL 3 is NOT_REGISTERED. Owner clarification is pending.

| circuit | n | pilot seconds | density block bytes |
|---|---:|---:|---:|
| no_gate | 2 | 7.713176600 | 3600 |
| bystander | 3 | 0.182628600 | 1308736 |
| shared_gate | 3 | 1.337487100 | 7398400 |
| asymmetric_wrap | 3 | 0.178422700 | 1308736 |

Conservative projection for 32 cells plus threshold PNR companions: 112.940580002 seconds, within 75 focused minutes.

NULL 1, 2, and 4: PASS (14 tests passed). NULL 3: no owner definition found; not a numeric failure. No failed registered null.

Defined profile cells not run: 32. Undefined cells: 32. Exact enumeration: cells_not_run.csv. Undefined circuit/size combinations: no_gate n=3; bystander n=2; shared_gate n=2; asymmetric_wrap n=2. Synthetic no_gate n=3 pulse-oracle validation does not add a registered grid fixture.

Ignored-mass range for accepted profile rows: N/A (zero accepted rows). Pilot measurements are timing diagnostics only. Source and artifact hashes are frozen in manifest.json; do not overwrite this directory when the missing owner registration is supplied.

Focused-time estimate through local preflight commit: about 16 minutes of the 75-minute cap. No transit pause was observed during this preflight; the estimate does not charge the earlier session's transit time. The projected profile compute fits the cap; the stop is the missing owner NULL 3 registration.

Verification: source/artifact hashes match, all 64 possible cells are enumerated (32 defined/blocked, 32 undefined), and the NULL 4 insertion is verbatim with no other change to the owner document. No production code changed. Full-suite execution was not repeated for this documentation/measurement-only preflight; the 14 relevant production-path null checks passed. NULL 3 was not evaluated and no numeric null failed.
