# Method catalogue review

## Outcome

The current eight methods are a good alpha set. Together they cover evidence,
assumptions, explanation, challenge, uncertainty, monitoring, choice, and
failure. They are not a complete set for every kind of analysis.

The next catalogue wave should test two new methods first:

1. **Causal Factors Analysis** for explaining why an observed problem happened.
2. **Outside View / Reference Class Check** for comparing forecasts with what
   happened in similar real cases.

An **Outside-In Context Scan** is also worth prototyping. A pre-mortem is better
tested first as a short profile made from methods already in the catalogue.

No candidate should enter the public catalogue only because it is well known.
It should add a distinct result, have a reputable public source, work within a
bounded AI task, state when it should not be used, and beat a matched no-method
baseline in evaluation.

## Why the current methods were selected

| Method | Place in the set | Why it stays |
| --- | --- | --- |
| **Evidence Quality Review** | Input check | Weak, stale, duplicated, or dependent sources can undermine every later method. This check makes that visible before synthesis. |
| **Key Assumptions Check** | Reasoning check | Many conclusions rest on premises that are not stated as evidence. This method exposes the load-bearing ones and defines change conditions. |
| **Competing Hypotheses Analysis** | Explanation | It compares explanations against the same evidence and pays attention to disconfirming information, which helps reduce premature closure. |
| **Devil's Advocacy** | Challenge | It tests a leading judgment with the strongest credible contrary case. This is different from listing weak pros and cons. |
| **Alternative Futures Analysis** | Uncertainty | It handles situations where one forecast would be misleading by exploring several plausible futures and robust actions. |
| **Indicators and Signposts** | Monitoring | It turns a judgment into observable signals and a reason to revisit the work instead of leaving the report static. |
| **Systems Trade Study** | Choice | It makes criteria, constraints, uncertainty, and reversals visible when options must be compared. |
| **Failure Modes Review** | Prospective risk | It works from system elements to possible failures, effects, controls, and follow-up checks before failure occurs. |

The intelligence-analysis methods are adapted from the CIA's public
[*Tradecraft Primer*](https://www.cia.gov/resources/csi/static/955180a45afe3f5013772c313b16face/Tradecraft-Primer-apr09.pdf)
and use the public [ICD 203 analytic standards](https://www.odni.gov/files/documents/ICD/ICD-203.pdf)
as a quality anchor. The decision and failure methods are adapted from public
NASA guidance. These sources establish a serious basis for the procedures;
they do not prove that Method Council's AI adaptations are faithful or useful.

## Coverage gaps

### 1. Explaining an event after it happened

Competing Hypotheses helps decide which explanation best fits the evidence.
Failure Modes looks forward at how a system could fail. Neither provides a
full retrospective chain from event timeline, through contributing conditions
and failed controls, to corrective action.

**Recommendation:** prototype **Causal Factors Analysis**. It should allow
multiple causes, distinguish direct causes from contributing conditions, link
each causal claim to evidence, and stop when the data runs out. NASA's current
[software process-assessment guidance](https://swehb.nasa.gov/spaces/SWEHBVD/pages/102695538/SWE-204%2B-%2BProcess%2BAssessments)
describes timelines, causal maps, root and contributing factors, corrective
actions, and follow-up checks. A general Method Council version would still be
a preview adaptation, not a safety investigation or certification artifact.

### 2. Using base rates instead of only an inside view

Alternative Futures explores plausible paths, but it does not compare a
forecast with the observed outcomes of similar past cases. That leaves a gap
for cost, schedule, adoption, delivery, and reliability estimates.

**Recommendation:** prototype an **Outside View / Reference Class Check**. It
should define a comparable class, show the actual outcome distribution, explain
how similar the current case is, and remain `INCOMPLETE` when reliable
comparators are unavailable. UK government
[reference-class guidance](https://www.gov.uk/government/publications/optimism-bias-and-contingency-at-homes-england/optimism-bias-and-contingency-at-homes-england-accessible-version)
uses completed comparable projects to counter optimism bias and explicitly
depends on suitable historical data. The method should not invent a base rate
or turn a small, biased sample into false precision.

### 3. Checking the wider context before analysis narrows

The current set can begin with the question as framed and still miss external
forces that sit outside the immediate evidence bundle.

**Recommendation:** prototype an **Outside-In Context Scan** after the first two
candidates. The CIA primer describes Outside-In Thinking as a way to identify
external forces, factors, and trends early in a project. Its main risk in an AI
workflow is producing a generic checklist. It should enter the catalogue only
if evaluation shows that it finds material, evidenced factors that the baseline
misses.

## Useful ideas that should not become new methods yet

- **Pre-mortem / What-if analysis:** high practical value, but much of its work
  can be composed from Failure Modes, Alternative Futures, Devil's Advocacy,
  and Indicators and Signposts. Test a short `pre-mortem` profile before adding
  another overlapping method.
- **Value of Information:** NASA decision analysis already asks whether reducing
  uncertainty could change the ranking of options. First extend or profile the
  Systems Trade Study; split out a new method only if the result is clearer and
  measurably more useful.
- **Team A/Team B and Red Team:** these approaches need genuinely distinct
  expertise, evidence, or actor knowledge. Several agents using the same model
  are correlated and should not be presented as independent teams.
- **Brainstorming:** useful inside other methods, but idea generation alone does
  not produce a decision-ready analysis.
- **SWOT and PESTLE:** familiar names do not guarantee useful analysis. A sourced
  Outside-In method offers a clearer procedure and a testable output.
- **Bayesian or probabilistic methods:** potentially valuable, but they need
  trustworthy priors, likelihoods, and calibration controls. Adding them before
  those inputs can be verified would invite false precision.

## Admission test for a new method

A candidate moves into the preview catalogue only after it has:

1. a public primary source and an independent source-fidelity review;
2. a clear job that is not already covered by another method or profile;
3. a bounded result contract, evidence rules, contraindications, and honest
   `INCOMPLETE` behavior;
4. representative, edge, and adversarial cases;
5. blinded comparison with a no-method baseline and the nearest existing
   method; and
6. an independent practitioner review of usefulness and likely misuse.

The [confidence plan](../evals/CONFIDENCE_PLAN.md) describes the wider evaluation
program. New-method admission should use the same frozen rubrics, retained
failures, and independence rules.
