# Stretch Plan: IQP → Photonic Encoding Research Project
**Status:** Not started. Does not begin before **September 2, 2026** at the earliest, and only once [MerLin_SMART_Spec_Sept1.md](MerLin_SMART_Spec_Sept1.md) is actually complete (public repo, README, benchmark, note to Vincent, case study, all checked off).
**Relationship to other parked work (decided 2026-07-19):** This project runs **immediately after MerLin**, before PennyLane. PennyLane independent contributions are sequenced after this project wraps. ket.jl/SDP is informal free-time research only (no artifact), and runs ambiently rather than competing for a slot.

---

## Why this exists as its own doc

The MMD-generative MerLin project (the committed Sept 1 deliverable) reuses your IQP-MMD *loss function and eval methodology*, not the IQP *circuit* itself. This doc is for the harder, more interesting thing that got set aside during scoping: whether IQP's structure can be meaningfully realized as a photonic circuit at all, and whether it survives the translation.

## Research question

**Does an IQP-inspired photonic ansatz — built from linear-optical primitives (phase shifters, beamsplitters, Fock-space photon counting) instead of qubit gates — preserve the properties that make qubit-IQP interesting?**

Specifically:
- Trainability: does it exhibit the same (or different) barren-plateau behavior as qubit IQP, measured via gradient-variance scaling with system size?
- Hardness: does whatever sampling-complexity argument applies to qubit IQP survive the photonic translation, or does it degrade the way boson sampling's hardness argument degrades under photon loss/noise?

This is explicitly **not** a "port my old code" project: no established IQP→linear-optics reduction is known to exist. Phase 0 below exists to find out whether that's actually true before designing anything.

## Prerequisites (must be true before Phase 0 starts)
- MerLin project shipped per the SMART spec.
- Working fluency with Perceval's **low-level** circuit API: this project builds custom circuits from optical primitives, not MerLin's `QuantumLayer.simple()` wrapper. That fluency should already exist from the MerLin project, but confirm it covers manual circuit construction, not just the high-level interface.
- Your own IQP + barren-plateau notes/results compiled into one reference doc: you'll need to cite your own prior numbers as the qubit-side baseline for comparison.

## Phases (rough; expect this to get re-planned once Phase 0 lands)

**Phase 0 — Literature scoping.** Search for any existing IQP↔linear-optics or IQP↔continuous-variable constructions. Confirm the research question is actually open, or find out it's already been answered (in which case, adjust: reproduce-and-extend that instead of inventing from scratch). Time-box this: if nothing viable turns up in a defined window, this track isn't ready and shouldn't be forced.

**Phase 1 — Design the encoding.** On paper, before any code: define how IQP's commuting diagonal gates + Hadamard-basis conjugation map onto phase shifters, beamsplitters, and photon-number measurement. This is the actual novel contribution: don't skip to implementation before this is written down and you can defend it.

**Phase 2 — Minimal implementation.** Build the smallest instance of the mapped circuit in Perceval. Verify it reduces to known/classically-checkable IQP behavior in some limiting case (e.g., small enough to brute-force compare against a qubit IQP simulation).

**Phase 3 — Trainability/hardness study.** Measure gradient variance vs. system size (barren-plateau check) against your qubit-IQP baseline numbers. If pursuing the hardness angle, assess whether realistic photonic noise/loss breaks any hardness claim, the way it does for boson sampling.

**Phase 4 — Write-up.** Decide the target format once results exist: portfolio case study, a note to Vincent, or (if the result is genuinely novel) something aimed at a workshop/preprint. Don't decide this now: let what Phase 3 actually finds determine how big a claim is defensible.

## Finish criteria (modest, on purpose)
- A working small-scale photonic circuit built from the Phase 1 encoding, with Phase 2's sanity check passing.
- An honest empirical answer from Phase 3, including "it doesn't preserve X" as a valid, reportable outcome. This is a research project; a negative result you can explain is a real finish, a positive result you can't explain is not.
- A written explanation you could give unaided, same bar as the MerLin project.

## Sequencing (decided 2026-07-19)
Order is MerLin → this project → PennyLane. ket.jl/SDP is informal research with no artifact and runs in parallel without deadline pressure, so it doesn't affect this sequence. If this project runs long enough to threaten PennyLane indefinitely, that's worth an explicit re-check rather than letting PennyLane's already-long stall (since May) silently extend further.
