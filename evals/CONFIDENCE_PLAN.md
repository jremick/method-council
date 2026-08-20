# Method usage-confidence plan

## Decision target

The current evidence shows that Method Council can produce structurally valid,
recognizable artifacts while preserving missing evidence and correlation. It
does not show that applying a named method improves an analysis compared with a
well-formed generic prompt.

The next evaluation program will estimate incremental usefulness, method
fidelity, calibration, actionability, and failure-mode resistance without using
the implementation's own status flags as quality authority.

## Claims and gates

| Claim | Required evidence | Current state |
| --- | --- | --- |
| Structural implementation works | Content-bound deterministic verification | Established for eight recorded specimens |
| Outputs resemble the intended method | Blinded rubric review across varied cases | Correlated screen only |
| A method improves analysis | Matched no-method baseline and pairwise grading | Not measured |
| Improvement is repeatable | Multiple independent runs per condition | Not measured |
| Improvement generalizes | Held-out cases, domains, and model/provider paths | Not measured |

## Wave 4A — calibration set

Create three case types for every method:

1. **Representative:** a well-bounded task with adequate evidence.
2. **Edge:** a task near the method's contraindications or with ambiguous fit.
3. **Adversarial:** a task designed around a documented method failure mode.

This produces 24 case-method pairs. For each pair:

- generate a method-conditioned artifact and a matched generic-analysis
  baseline;
- run each condition three times with the same observable host configuration;
- hide condition labels, method names, file paths, and status fields from
  graders;
- randomize pair ordering; and
- retain prompts, harness version, duration, failures, and bounded execution
  metadata separately from the grading packet.

The baseline prompt must not expose the method steps or scoring rubric. Cases
and grading keys must not appear in the execution context before the run.

## Measures

Two independent reviewers should score each blinded pair on a 0–4 anchored
rubric:

- method fidelity;
- decision-relevant considerations surfaced;
- unsupported or misclassified claims;
- evidence and counterevidence discipline;
- calibration and claim limits;
- actionability and change conditions; and
- resistance to the case's named failure mode.

Also record pairwise preference (`method`, `baseline`, or `tie`), material
omissions, critical-error count, completion time, and artifact-review time.
Reviewers must provide short rationales. Differences greater than one scale
point receive adjudication rather than automatic averaging.

## Wave 4B — held-out gate

Use Wave 4A to debug cases, rubric anchors, and grader disagreement—not to set a
passing claim after inspecting favorable results. Freeze the harness, rubric,
grader instructions, failure taxonomy, and thresholds before evaluating unseen
held-out cases.

The held-out set should include at least two new cases per method, preserve the
same repeated-run design, and add a second supported model/provider path when
one has independently passed its adapter contract. Report distributions and
disagreements, not only averages.

Candidate public-beta gates, to be finalized before the held-out run, should
require:

- no critical unsupported claim or status laundering;
- no material regression from baseline in evidence discipline or calibration;
- a stable positive decision-value delta for each method, not only the suite
  average;
- acceptable reviewer agreement or documented adjudication; and
- reproducible results across repeated runs and at least two execution paths.

If a method does not improve its matched baseline, narrow its applicability,
revise its artifact contract, keep it preview-only, or remove it. Do not average
a weak method into a suite-level pass.

## Wave 4C — portfolio value and new-method admission

Method-level results do not show whether a full profile is worth its extra
steps. For each activity profile, compare four blinded conditions:

1. a matched generic-analysis baseline;
2. the best single applicable method;
3. the current profile; and
4. the current profile with one method removed.

Measure decision-relevant gain, material omissions, critical errors, review
time, execution time, and disagreement. The removal tests show whether a method
adds useful coverage or mainly repeats another pass. Also test whether the
router chooses a suitable method set for unseen questions; a useful method that
is consistently selected for the wrong task still lowers portfolio value.

Candidate methods follow a separate admission gate before joining the preview
catalogue. Each candidate needs a public primary source, independent fidelity
review, representative, edge, and adversarial cases, and a blinded comparison
with both the generic baseline and the nearest existing method or profile. It
must fail visibly when required evidence is unavailable. Familiarity, source
prestige, or one strong example is not sufficient.

The first recommended candidates are Causal Factors Analysis and an Outside
View / Reference Class Check. An Outside-In Context Scan should follow if it
can avoid generic checklist output. Test a pre-mortem first as a profile built
from existing methods rather than assuming it needs a separate contract. See
the [method catalogue review](../docs/METHOD_CATALOGUE.md) for the coverage
reasoning.

## Independence and governance

- At least one reviewer per method must be a practitioner independent of the
  implementation; two are preferred for consequential methods.
- Reviewers disclose conflicts and do not see implementation-authored semantic
  scores until their ratings are locked.
- Model graders may assist with triage but cannot replace practitioner review.
- The deterministic harness owns case identity, randomization, bindings,
  aggregation, and gate calculation.
- Every FAIL, ERROR, INCOMPLETE result, skipped run, and grader disagreement is
  retained.

## Alpha exit condition

The public alpha can invite inspection while this plan is incomplete, provided
the README and releases do not claim improved decision quality. Public beta
remains blocked until the held-out gate and independent review are complete.
