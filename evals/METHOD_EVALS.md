# Method usefulness evaluation

Schema-valid artifacts are necessary but do not show that a method improves an
analysis. Method Council therefore separates three claims:

1. **Deterministic conformance** checks the selected steps, required artifact
   fields, evidence binding, status derivation, correlation labels, and bundle
   digests.
2. **Correlated semantic screening** looks for obvious method-fidelity,
   evidence-discipline, calibration, actionability, and known-failure-mode
   defects. The current screen is authored within the Codex development context
   and is neither independent nor calibrated.
3. **Usefulness validation** requires blinded comparison with a no-method
   baseline, repeated representative, edge, and adversarial cases, and review by
   at least one practitioner independent of the implementation. That gate is
   currently `INCOMPLETE` for every method.

This separation follows OpenAI's guidance to define the target behavior, use
realistic and edge cases, examine the full harness, and retain human expert
audit rather than treating a model grader as final authority:

- <https://openai.com/index/evals-drive-next-chapter-of-ai/>
- <https://openai.com/index/trustworthy-third-party-evaluations-foundations/>

## Current screening set

The inventory at `evals/methods/inventory.json` covers the original eight
catalog methods. Six use the hardened 2026-08-19 acceptance bundles.
Alternative Futures and Indicators/Signposts use the hardened forecast bundle
recorded on 2026-08-20. Each currently has one representative run only.

Causal Factors Analysis, Outside View, Outside-In Context Scan, Concept and
Meaning Clarification, Contextual Interpretation, Reflective Equilibrium,
Pragmatic Clarification, and Value-Sensitive Inquiry are listed as unevaluated
in the generated report. They have no specimen or semantic score yet. Adding a
source-backed method does not transfer confidence from another method.

Generate the content-derived report:

```bash
uv run --frozen python scripts/evaluate_methods.py
```

The command re-verifies every inventoried source bundle, rejects unknown or
unreviewed specimens, reports catalogue methods without specimens, checks
selected-step and artifact-field coverage, validates the bounded 0-4 review
records, and writes `evals/methods/screening-report.json`.

The screening threshold is a score of at least 3 on every dimension. It is an
uncalibrated defect-finding threshold, not a quality percentage. Meeting it can
only produce `MET` under `correlated_semantic_screen`; it cannot change a
method's usefulness status from `INCOMPLETE`.

## Next validation wave

For each of the original eight methods, add:

- one edge case and one adversarial case, for at least three recorded runs;
- a no-method baseline produced without exposing the method or scoring rubric;
- blinded pairwise ratings for decision-relevant delta, method fidelity,
  unsupported assertions, and omitted material considerations;
- at least one independent practitioner review with conflicts recorded; and
- regression thresholds derived from observed score distributions rather than
  chosen after seeing results.

Keep prompts, answers, rubrics, budgets, model state, and harness versions
separate enough to detect contamination and reward hacking. Do not convert a
same-model or same-host majority into independent corroboration.

For each of the eight unevaluated methods, first add one representative, one edge, and
one adversarial case plus a matched no-method baseline and nearest-method
comparison. They should not receive even an initial correlated screen until the
artifact checks pass and the grading packet is frozen.

Selection confidence is a separate claim. The future automatic advisor needs
its own frozen tasks, acceptable-route labels, contraindication tests, and
manual-selection baseline as described in
[the advisor plan](../docs/METHOD_ADVISOR.md).
