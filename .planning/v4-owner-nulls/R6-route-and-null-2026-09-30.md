OWNER RECORD (R6, 2026-09-30). Owner decisions in the owner's words; assistant notes labeled.
ROUTE: graph route (outcome-dependent measurement angle in the logical M1 incidence-graph
model). State injection not chosen for R6.
Owner ordering of criteria: (3) matches Kashefi's group, then (1) can explain unaided,
then (2) photonic fluency. Both routes satisfy (3) on the evidence checked; the tie was
broken by (1): "I could understand the graph route. it's more in line with what I have
learned throughout my masters. I don't fully understand photonic quantum computing yet."
Assistant notes (evidence, not owner claims): graph route matches Danos-Kashefi-
Panangaden (Measurement Calculus) and the masterclass slides p9, p12; FQC25 slides p41-44
present state injection as an adaptivity tool for a photonic QML classifier, not for
dual-rail IQP generation. SI on dual-rail IQP would be a new model with an undesigned
step. Owner recollection, UNVERIFIED and in no source: Kashefi said to Hela Mhiri
something like "it would be interesting to see how adaptivity applies to this" (about
arXiv 2604.14323, which contains no MBQC/adaptivity content; grep of the PDF found none).
Lab focus is unverified.
MODEL (owner answers): the outcome s1 selects which table is built:
table = make\_table(theta0) if s1 == 0 else make\_table(theta1)
q[x] = sum over s of P(s) \* table\_s[x]     (example q("000") = 0.5*0.4 + 0.5*0.2 = 0.30)
Graph-route policy family from masterclass p12: M^{(-1)^s a + t\*pi} (s flips the sign of
the angle, t adds pi). Risk noted by assistant: this mechanism may reproduce M1's
correction (relabeling) rather than change the distribution; the R6 null and controls
must distinguish the two.
MATCHED CONTROLS (owner): A adaptive (theta0, theta1, policy); B open-loop with matched
parameter count; D classical mixture with matched branch weights and parameters.
Explanations to rule out: more parameters (match count), and mixing (control D).
REFUTATION (owner): "Adaptivity is useful only if, on held-out data, A is better [closer
to the target on held-out data] than B by more than [fit-to-fit spread]. If instead they
are about the same or B is better, we report no benefit." Held-out metrics per R3:
coverage main, precision beside it. Independent fits per model, 95% bootstrap interval.
No meaningful-gap threshold. A vs D attributes any win to branch correlation.
R6 NULL (owner): with theta1 = theta0 the policy ignores s1 and A builds the same table as
B for every outcome, so its distribution is q\_theta0. Held-out score(A) - score(B) = 0
within 1e-9 (same tolerance as R2 null 1). If it is not, it is a bug in the adaptive
path, not a finding; no R6 result from that code is trusted. This is a deterministic
identity check, not a comparison against fit-to-fit spread.
HYPOTHESIS (owner, confirmed 2026-09-30). Owner's sentence, verbatim: "outcome-dependent
angles help on the rings target because the measure optimally in the equatorial basis."
Assistant's reading, confirmed by the owner ("yes, that's what I meant"): after each
outcome the adaptive model can pick the best angle in the X-Y plane for that branch;
a single fixed angle cannot be best for both branches, so A fits the rings target better
than B. In code: B uses angle = theta; A uses angle = theta0 if s1 == 0 else theta1.
Falsified by the owner's refutation rule above (A - B within fit-to-fit spread, or B better).
Left open by the owner: why this should hold on rings specifically. The hypothesis is
registered as general, with rings as the first test target. Not exploratory.
DEPENDENCIES/OPEN: R5, R3, relevant R1 noise contract; charge photons per graph state,
feed-forward rounds, delays and losses (D1 physical contract still open). Policy must
use only earlier outcomes.

R6 null #2 (owner, 2026-09-30). Prediction: in the M1 incidence-graph model, any
causal graph-route policy (a later ancilla's angle depends only on EARLIER outcomes)
gives x-distribution q\_A(x) = 2^-M \* sum over s of q\_{theta(s)}(x), a uniform classical
mixture of ordinary IQP tables. Branch weights are P(s) = 2^-M whatever the angles are
(from p(s,y) = 2^-M q\_theta(y XOR G^T s) in docs/v4-mbqc-adaptivity-plan.md section 2).
So control D (classical mixture with the same weights) equals model A exactly for this
policy class: score(A) - score(D) = 0 within 1e-9. This is a derivation, not yet tested.
GATE-02 label: exact-reference check of the same construction (the mixture is built from
the same q\_theta family). It confirms the collapse claim for commuting diagonal
M1 gates. It does not show adaptivity is absent from non-commuting models such as SI.
Owner sketch of the branch sum (verbatim, passes the toy checks):
q = {}
for i in range(len(p\_branch)):
for x in tables[i]:
q[x] = q.get(x, 0.0) + p\_branch[i] \* tables[i][x]
return q

R6 disposition (owner decision, 2026-09-30). Reason in the owner's words: "the graph
route doesn't benefit from adaptivity because the graph route with IQP circuits doesn't
benefit from adaptivity." Evidence: R6 null #2 fixture (commit 86955ff) confirmed that
causal graph-route policies on commuting IQP M1 give an exact uniform mixture of IQP
tables (gap 1.1e-16), so model A equals control D by construction. Disposition:
  - ADAPT-01..03 on the graph route: answered NEGATIVELY for commuting IQP M1, scoped to
    the tested fixtures plus the derivation below. Not a claim about non-commuting
    models.
  - A/B/D training sweeps: NOT RUN (A equals D by construction; no budget spent).
  - Adaptive SI (or non-commuting graph gates) for IQP-style generative modeling:
    DEFERRED to a separate future milestone, not part of v4. Open design items:
    (1) how count-and-reinject acts on a dual-rail qubit; (2) definition of control D for
    SI (branch tables must come from the non-adaptive family); (3) whether the trainable
    layer can do the branch sum (MerLin 0.4.0 has no feed-forward mention; Perceval
    1.2.4 has FFConfigurator, scope vs. SI reinjection unverified).
Owner's takeaway sentence for the portfolio/case-study reader: I tested whether adding outcome-dependent measurements to IQP circuits helps. Because s is a fair coin that only picks which IQP table to use, the adaptive model is just a mixture of ordinary IQP circuits, so it can do nothing a classical mixture of IQP circuits couldn't. I did not test SI circuits and circuits whose gates don't commute.
Unverified owner recollection (not a source): Kashefi's remark to Hela Mhiri about
adaptivity. PQCNN (arXiv 2504.20989) is a classification paper; its advantage wording in
the abstract summary (vs other QNN proposals) differs from FQC25 slide p44 (vs classical
CNNs); unresolved.
