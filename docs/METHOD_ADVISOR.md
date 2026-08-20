# Automatic method advisor plan

## Goal

Make automatic selection the normal starting point: analyse the user's question,
challenge, problem, or goal; recommend the smallest useful council; explain the
choice; and let the user accept or override it.

The advisor is not implemented as a trusted selector yet. Today the skill asks
the model to propose a route and deterministic code checks whether that route is
allowed. The validator does not know whether the methods are a good fit for the
task. This plan keeps that distinction visible until selection evals pass.

## User experience

Default:

```text
Methods: auto
```

The advisor shows a short preview:

```text
Activity: decide
Rigor: standard
Signals: contested meaning; affected stakeholders; value conflict
Council: concept-clarification, value-sensitive-inquiry,
         reflective-equilibrium, devils-advocacy
Why: one sentence per method
Limits: stakeholder interviews are missing; same-model passes are correlated
```

The user can instead name an exact route or include/exclude methods. An override
changes the recommendation, not the safety or contract rules: unknown methods,
unsupported rigor, conflicts, missing dependencies, disabled preview policy, and
required challenge coverage still fail closed.

## Selection signals

The first component should turn the request into a small structured record, not
hidden reasoning or a free-form score:

- desired activity and output;
- stakes, reversibility, urgency, and requested rigor;
- evidence availability, source dependence, and material gaps;
- causal, forecast, option-choice, or failure-risk focus;
- vague or contested terms;
- source interpretation or historical context;
- duties, principles, fairness, rights, or value conflict;
- direct and indirect stakeholder effects and missing participation;
- external-context sensitivity;
- explicit user includes, excludes, and exact selections.

Store a question digest and normalized signals by default, not the raw prompt.
Each signal should have a short reason code and confidence state such as
`present`, `absent`, or `uncertain`; it should not expose chain-of-thought.

## Family mapping

| Signal | Family to consider |
| --- | --- |
| Evidence quality, causes, alternatives, forecasts, risk | Analytical |
| Ambiguous concepts, passages, meaning, context | Interpretive |
| Principles, duties, fairness, rights, value conflict | Normative |
| Consequences, action, criteria, practical difference | Pragmatic |
| Affected people, distribution, participation, missing voices | Participatory |

Families narrow the search. Method-level rules then check applicability,
contraindications, prerequisites, activity, rigor, complements, conflicts, and
challenge coverage. Family diversity is useful only when the task signals call
for it; the advisor must not select one method from every family by default.

## Proposed architecture

1. **Signal proposal:** a model produces a schema-bound task-signal record.
2. **Deterministic mapping:** code maps signals to eligible methods and reason
   codes. Hard contraindications and missing prerequisites remove or downgrade
   candidates.
3. **Coverage solver:** select the smallest set that covers material signals,
   fits the rigor count, and contains a challenge method when required.
4. **Route validation:** the existing deterministic validator checks catalogue
   and execution constraints.
5. **Preview and override:** show the route, evidence needs, limitations, model
   assignments, and correlation before execution.
6. **Outcome logging:** retain only bounded selection metadata, user overrides,
   route validity, and later usefulness labels.

The advisor should return a set of acceptable routes when several are defensible,
not manufacture a false single optimum. When a missing fact would materially
change the family or method choice, it should ask one concise question.

## Failure behaviour

- Unclear activity or decision boundary: ask one question or remain `INCOMPLETE`.
- Missing method prerequisite: explain the gap and offer an eligible alternative;
  never pretend the evidence exists.
- No council adds value: recommend a direct answer instead of forcing methods.
- Invalid user override: reject it with reason codes; do not silently substitute.
- Preview method not allowed by policy: omit it and show the loss of coverage.
- Too many candidate methods: prefer the smallest coverage-preserving set.
- Same-model execution: retain `CORRELATED`, even with diverse families.

## Threats and misuse to test

- prompt injection inside the question or source material tries to choose methods,
  call providers, change persistence, or bypass the validator;
- keyword stuffing causes a family to be selected without material task fit;
- the advisor over-selects methods, increasing cost without useful coverage;
- preview methods are used silently;
- normative output launders model preference as moral authority;
- participatory output invents stakeholder views or consent;
- model/version drift changes routes without a catalogue change; and
- a user override is treated as permission for external calls or side effects.

## Delivery phases

### Phase 0 — catalogue structure

Complete in source: one required primary family per method, five family values,
new interpretive/normative/pragmatic/participatory methods, and documented limits.

### Phase 1 — advisory contract

Add versioned schemas for `selection-signals` and `route-advice`, plus a read-only
`method-council advise` command. It proposes and validates a route but launches
nothing. Add exact user include/exclude/selection fields and stable reason codes.

### Phase 2 — deterministic policy

Implement family and method mapping rules, contraindication handling, prerequisite
checks, parsimony, and alternative-route output. Freeze representative, edge, and
adversarial fixtures before tuning thresholds.

### Phase 3 — default skill workflow

Make `auto` the skill default only after the offline selector clears its held-out
gate. Keep a visible route preview and exact user override. Do not enable external
providers or side effects through selection.

### Phase 4 — measured ranking

Consider learned ranking only after enough reviewed usage evidence exists. Keep
deterministic eligibility and safety gates outside the model. Version the ranking
policy and preserve a rules-only fallback.

## Selection evaluation

Build a frozen corpus covering every activity and family, mixed-family questions,
simple cases that need no council, contraindications, missing evidence, and the
threats above. Independent reviewers should label **acceptable method sets** and
unacceptable selections rather than one exact answer.

Compare:

1. generic model choice;
2. current profile/activity heuristic;
3. rules-only advisor;
4. model signals plus deterministic advisor; and
5. expert manual selection.

Measure family recall, critical method omissions, contraindication violations,
prerequisite coverage, route validity, parsimony, selection stability, useful
route preference, user override rate, cost, and downstream decision-value delta.
Evaluate the advisor and the methods separately: a good route cannot rescue a
weak method, and a good method does not prove it was selected well.

Freeze thresholds before a held-out run. A default advisor should require zero
critical safety/contraindication violations, high acceptable-set coverage,
materially better parsimony than generic selection, stable reason codes, and no
downstream regression against manual routes. Final thresholds must be set from
the calibration distribution, not chosen after inspecting held-out results.

## Non-goals

The advisor does not score truth, certify method fidelity, replace domain or
stakeholder judgment, prove provider independence, authorise external calls, or
take the consequential action produced by a council.
