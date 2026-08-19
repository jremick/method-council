# Codex workflow

Status: hardened local preview; the initial run bundles were retired after
independent review found missing semantic gates, and commit-bound reruns are
pending.

## Intended first interaction

Method Council is designed first for Codex users who are already signed in
through a ChatGPT subscription. From the repository, install and validate the
locked environment:

```bash
uv sync --frozen --all-groups
uv run method-council validate
uv run python scripts/sync_codex_skill.py check
```

The checked-in project skill is available at `.agents/skills/method-council`.
Invoke it in a Codex task with a natural-language request such as:

```text
Use $method-council to review this release decision with standard rigor.
Keep missing evidence explicit and do not use external providers.
```

The current runner executes `codex exec` inside a fresh tracked-file snapshot of
an exact commit, rejects tracked source mutation, copies only expected run
artifacts, and independently re-verifies them against a second pristine
snapshot. This is still an unsigned local recorder, not an external attestation
or an operating-system containment proof.

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

## Recorded acceptance

The four initial subscription-backed runs covered architecture, investigation,
missing release evidence, and hostile embedded instructions. Independent review
showed that the old verifier trusted method PASS claims without enforcing each
method's selected steps, evidence minima, and artifact fields. Those bundles
were retired. The same cases must now pass `verify-acceptance` from the hardened
source commit before this section can claim recorded acceptance.

Still needed before public alpha:

- independent method-fidelity and user-journey review;
- live GitHub identity, settings, CI, and security read-back;
- provider-specific evidence before any non-Codex compatibility claim;
- a release decision derived from the complete candidate evidence set.

See [Codex acceptance evidence](ACCEPTANCE.md).
