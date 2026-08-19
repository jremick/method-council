# Codex workflow preview

Status: design contract; not yet a verified end-to-end user path.

## Intended first interaction

Method Council is being designed first for Codex users who are already signed in
through a ChatGPT subscription. The planned invocation is:

```text
$method-council <activity> --rigor <rapid|standard|intensive> "question"
```

The exact invocation, installation path, and output behavior remain provisional
until the Codex skill and deterministic core pass real clean-checkout task runs.
This document must not be used as evidence that the command currently works.

## Interaction sequence

### 1. Scope

The coordinator establishes:

- the question or decision;
- the decision owner and checkpoint;
- relevant constraints and non-goals;
- the permitted evidence boundary;
- whether external tools or providers are allowed.

Ambiguous scope should produce a bounded clarification or an explicit unknown,
not a broad autonomous search.

### 2. Select

The model proposes a small set of complementary methods based on the activity
and requested rigor. Deterministic code checks known IDs, catalog state, activity
fit, count, prerequisites, incompatibilities, and challenge coverage.

An invalid route stops before method execution.

### 3. Run separate passes

Each pass applies one named method and returns the method's typed artifact.
Codex subagents may provide bounded parallelism where their workstreams are
independent. Multiple passes on the same model or host are labelled correlated;
they are not described as independent corroboration.

### 4. Validate and challenge

Method output is untrusted until it passes structural and semantic checks.
Missing, malformed, simulated, or failed output remains `ERROR` or `INCOMPLETE`.
A challenge pass tests assumptions, alternatives, counterevidence, and the most
plausible material failure path.

### 5. Synthesize

Synthesis compares artifacts without confidence-weighted voting. It retains:

- areas of convergence;
- material disagreement;
- evidence that discriminates between alternatives;
- assumptions and unknowns;
- collection gaps and next checks.

### 6. Checkpoint

The run ends with a traceable report and an explicit human decision or next
action. Tool side effects are outside the default analysis route and require
their own authorization.

## Rigor levels

| Rigor | Route | Intended use |
| --- | --- | --- |
| Rapid | 1–2 complementary methods and one challenge check | Reversible, time-bounded questions |
| Standard | 3–4 separate passes, comparison/challenge, full ledger | Material technical or operating decisions |
| Intensive | 4–6 methods, explicit alternatives, dedicated challenge/verifier, checkpoint | High-consequence or highly uncertain analysis |

Rigor controls analytical work, not truth. A deeper route can still be wrong,
evidence-poor, or incomplete.

## Subscription and provider boundary

The default route is intended to use the active Codex session without a separate
provider API key. The interface should say `Host: Codex subscription` and
`External provider calls: none` when that is the observed route. It should not
translate subscription use into a fictional per-run `$0` cost claim.

Other providers are optional adapters. A binary on `PATH`, a version response,
or an adapter file does not prove authentication, availability, compatibility,
or successful execution. Those states require provider-specific probes and real
run evidence.

## Privacy and persistence

- Raw prompts and full context are not persisted by default.
- Hidden chain-of-thought is never requested or stored.
- Local recording, if later implemented, must be explicit and bounded.
- Secrets, unrelated repository data, and personal paths must be excluded from
  run artifacts.
- External calls and side effects are deny-by-default.

## Evidence needed before this becomes a quick start

- Clean-checkout installation and validation on the supported platform.
- At least four representative real Codex subscription runs.
- Negative coverage for malformed output, provider failure, prompt injection,
  unsupported source claims, and split conclusions.
- Content-bound run artifacts and deterministic status derivation.
- Independent review of method fidelity and the public user journey.
