# Traceable report anatomy

The Method Council report is a decision artifact, not a transcript of hidden
reasoning and not a vote among simulated experts. It should be useful to a human
who needs to act, inspect the basis, or decide what evidence to collect next.

## Required reading order

### 1. Result and checkpoint

- direct answer or decision-relevant result;
- recommended next action, if the activity supports one;
- named human checkpoint or unresolved decision;
- primary status and any side conditions.

### 2. Key judgments and evidence

Each judgment links to evidence identifiers bound to the run. Confidence language
describes the evidence and uncertainty; it is not a numerical vote tally.

Each finding is typed as one of:

- `fact` — directly supported observation or source statement;
- `inference` — conclusion drawn from facts with the connection made explicit;
- `assumption` — unverified condition required by the reasoning;
- `unknown` — information not currently established.

### 3. Alternatives, dissent, and counterevidence

Materially different conclusions remain visible. The report identifies the
evidence that supports or weakens each alternative and what could discriminate
between them.

### 4. Assumptions, unknowns, and gaps

The report gathers unverified dependencies and missing information in one place.
Unknowns are not silently converted to assumptions during synthesis.

### 5. Indicators and decision controls

Where the selected methods support them, the report includes indicators,
signposts, review dates, thresholds, or kill criteria. These are observable
decision controls, not generic recommendations.

### 6. Run ledger and limitations

The ledger records:

- method ID and version;
- coordinator host plus any per-method execution assignment, provider state,
  and observable model identifier;
- method, model, provider, and source diversity separately;
- correlation and degraded/skipped side conditions;
- artifact digests, validation reasons, and timestamps;
- explicit limitations and skipped checks.

## Status semantics

Primary status precedence is:

```text
FAIL > ERROR > INCOMPLETE > PASS
```

`DEGRADED`, `CORRELATED`, and `SKIPPED` are side conditions. They never upgrade
the primary status. A caller or model cannot declare its own report release
eligible; that state is derived from content-bound validation evidence.

## What the report does not prove

A complete report does not by itself prove:

- the conclusion is true;
- the selected methods were optimal;
- a method was applied with expert fidelity;
- same-model passes are independent;
- the output is unbiased;
- the interface is usable or accessible;
- a provider is generally available;
- the repository is ready for public release.

Those claims require their own evidence and review.

![Contract diagram of the Method Council report sections and their validation ledger](../assets/exported/report-cutaway.svg)
