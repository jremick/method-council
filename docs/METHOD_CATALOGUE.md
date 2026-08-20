# Method catalogue review

## Outcome

The catalogue now has eleven preview methods. The original eight cover evidence,
assumptions, explanation, challenge, uncertainty, monitoring, choice, and
prospective failure. Three additions close the clearest gaps:

1. **Causal Factors Analysis** for explaining why an observed problem happened.
2. **Outside View / Reference Class Check** for comparing forecasts with what
   happened in similar completed cases.
3. **Outside-In Context Scan** for finding material external forces before the
   question becomes too narrowly framed.

The three additions have source-backed contracts and clear contraindications,
but they are still unevaluated. They should remain preview-only until they beat
a matched no-method baseline and receive independent fidelity and practitioner
review. A pre-mortem is still better tested first as a profile made from methods
already in the catalogue.

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
| **Causal Factors Analysis** | Retrospective cause | It traces an observed outcome through timeline, causal links, contributing conditions, failed controls, and corrective actions. |
| **Outside View / Reference Class Check** | Base-rate check | It compares a plan or estimate with actual outcomes in defensible comparable cases and refuses false precision when the data are weak. |
| **Outside-In Context Scan** | Context framing | It looks for material external forces early, then tests their impact and evidence instead of returning a generic trend list. |

The intelligence-analysis methods are adapted from the CIA's public
[*Tradecraft Primer*](https://www.cia.gov/resources/csi/static/955180a45afe3f5013772c313b16face/Tradecraft-Primer-apr09.pdf)
and use the public [ICD 203 analytic standards](https://www.odni.gov/files/documents/ICD/ICD-203.pdf)
as a quality anchor. The decision, failure, and causal methods are adapted from
public NASA guidance. The outside-view method uses public Homes England
reference-class guidance. These sources establish a serious basis for the
procedures; they do not prove that Method Council's AI adaptations are faithful
or useful.

## Why the three additions were selected

### 1. Explaining an event after it happened

Competing Hypotheses helps decide which explanation best fits the evidence.
Failure Modes looks forward at how a system could fail. Neither provides a
full retrospective chain from event timeline, through contributing conditions
and failed controls, to corrective action.

**Added as preview:** **Causal Factors Analysis** allows multiple causes,
distinguishes direct causes from contributing conditions, links each causal
claim to evidence, and stops when the data runs out. NASA's current
[software process-assessment guidance](https://swehb.nasa.gov/spaces/SWEHBVD/pages/102695538/SWE-204%2B-%2BProcess%2BAssessments)
describes timelines, causal maps, root and contributing factors, corrective
actions, and follow-up checks. The Method Council version is a general preview
adaptation, not a safety investigation or certification artifact.

### 2. Using base rates instead of only an inside view

Alternative Futures explores plausible paths, but it does not compare a
forecast with the observed outcomes of similar past cases. That leaves a gap
for cost, schedule, adoption, delivery, and reliability estimates.

**Added as preview:** the **Outside View / Reference Class Check** defines a
comparable class, shows the actual outcome range, explains how similar the
current case is, and remains `INCOMPLETE` when reliable comparators are
unavailable. UK government
[reference-class guidance](https://www.gov.uk/government/publications/optimism-bias-and-contingency-at-homes-england/optimism-bias-and-contingency-at-homes-england-accessible-version)
uses completed comparable projects to counter optimism bias and explicitly
depends on suitable historical data. The method should not invent a base rate
or turn a small, biased sample into false precision.

### 3. Checking the wider context before analysis narrows

The current set can begin with the question as framed and still miss external
forces that sit outside the immediate evidence bundle.

**Added as preview:** the **Outside-In Context Scan** adapts the CIA primer's
Outside-In Thinking to identify external forces, factors, and trends early. Its
main risk in an AI workflow is producing a generic checklist. It should remain
preview-only unless evaluation shows that it finds material, evidenced factors
that the baseline misses.

## Remaining gaps

- calibrated probabilistic work where trustworthy priors and outcome feedback
  exist;
- human and organisational perspectives that cannot be simulated by merely
  assigning another prompt to the same model;
- specialised safety, security, legal, medical, and regulated methods whose
  use requires domain authority; and
- proof that the router chooses the right methods and that multi-method profiles
  add enough value to justify their extra cost.

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

## Admission and retention test

A candidate enters the preview catalogue only after it has:

1. a reputable public source and a traceable adaptation record;
2. a clear job that is not already covered by another method or profile;
3. a bounded result contract, evidence rules, contraindications, and honest
   `INCOMPLETE` behavior.

It should not be promoted or kept indefinitely without:

1. independent source-fidelity review;
2. representative, edge, and adversarial cases;
3. blinded comparison with a no-method baseline and the nearest existing
   method or profile; and
4. independent practitioner review of usefulness and likely misuse.

The [confidence plan](../evals/CONFIDENCE_PLAN.md) describes the wider evaluation
program. New-method admission should use the same frozen rubrics, retained
failures, and independence rules.
