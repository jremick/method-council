# Routing activities and rigor

Read this reference only when selecting or explaining a route.

## Activities

Choose the activity by the result the user needs, not by keywords alone.

| Activity | Intended result | Useful method contributions |
|---|---|---|
| `analyse` | Explain what the evidence supports | frame the question, assess evidence, test assumptions and alternatives |
| `investigate` | Identify the next discriminating inquiry | competing hypotheses, causal factors, evidence gaps, diagnostic tests and collection priorities |
| `decide` | Choose among explicit alternatives | criteria, trade-offs, pre-mortem, risk and reversibility |
| `forecast` | State plausible futures and observable indicators | outside view, alternative futures, signposts and change conditions |
| `architect` | Shape a system under constraints | requirements, trade studies, failure modes and verification boundaries |
| `review` | Challenge an existing artifact or claim | standards-based checks, adversarial review, counterevidence and residual risk |

If a request spans activities, choose the one that owns the final deliverable.
Use methods from another activity only when the catalog says they fit.

## Method families

Use families to decide which parts of the catalogue deserve attention. Do not
select one method from every family automatically.

| Family | Consider it when the task involves | Current methods |
|---|---|---|
| `analytical` | evidence, causes, alternatives, forecasts, uncertainty, or risk | evidence-quality, key-assumptions, competing-hypotheses, devils-advocacy, alternative-futures, indicators-signposts, failure-modes, causal-factors, outside-view, outside-in |
| `interpretive` | ambiguous concepts, passages, meaning, or historical context | concept-clarification, contextual-interpretation |
| `normative` | duties, principles, fairness, rights, or value conflict | reflective-equilibrium |
| `pragmatic` | practical consequences, action, criteria, or option choice | pragmatic-clarification, systems-trade-study |
| `participatory` | affected people, distribution, participation, or missing voices | value-sensitive-inquiry |

Before proposing a method, check its `use_when`, `avoid_when`, prerequisites,
activity, rigor, complements, and claim limits. A missing prerequisite is a gap
to report, not evidence to invent. In particular, generated personas are not
stakeholder evidence and model coherence is not moral authority.

If the user names an exact method set, use it as the requested route only after
validation. If the user gives include/exclude preferences, apply them before
proposing the smallest remaining route. Ask one concise question when an unknown
would materially change the family or method choice.

## Rigor

Rigor changes the workflow, not merely response length.

| Rigor | Route | Required shape |
|---|---:|---|
| `rapid` | 1–2 methods | complementary methods and one challenge check |
| `standard` | 3–4 methods | separate passes, comparison/challenge, full ledger |
| `intensive` | 4–6 methods | explicit alternatives, dedicated challenge/verifier, checkpoint |

Prefer `standard` when the user asks for Method Council without another signal.
Downgrade only when the question is clearly bounded and reversible. Escalate to
`intensive` when consequences, uncertainty, contested evidence, or adversarial
conditions justify the additional work. If the user explicitly chooses a rigor,
honor it unless a safety or contract boundary requires clarification.

## Route explanation

For each selected method, state:

- the method ID and version;
- what uncertainty or failure mode it is meant to expose;
- why it complements the other selected methods;
- the evidence or prerequisite it needs;
- its relevant limitation.

Keep the preview compact. Example shape:

```text
Activity: architect
Rigor: standard
Methods: <id> — <reason>; <id> — <reason>; <challenge-id> — <reason>
Host: Codex subscription
Correlation: same-host passes; CORRELATED
External provider calls: none
Raw prompt persistence: off
```

For a multi-model route, replace the host and correlation lines with the exact
per-method assignments. State that external calls are authorised and supported;
do not imply availability from a preview adapter or installed executable.

Do not claim the route is optimal or the methods are official unless the
canonical source record supports that exact statement.
