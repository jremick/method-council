# Canonical contracts

Version: 0.1.0

## Status

Primary status precedence is:

```text
FAIL > ERROR > INCOMPLETE > PASS
```

- `PASS`: every applicable hard gate is complete and passing.
- `FAIL`: a hard gate has a proven failure.
- `ERROR`: required execution or parsing failed without a stronger failure.
- `INCOMPLETE`: evidence or required work is missing, unavailable, stale, or
  indeterminate without a stronger failure/error.

Side conditions are `DEGRADED`, `CORRELATED`, and `SKIPPED`. They are preserved
in metadata and never upgrade the primary status.

## Rigor and route limits

| Rigor | Method count | Required shape |
|---|---:|---|
| Rapid | 1–2 | complementary methods and one challenge check |
| Standard | 3–4 | separate passes, comparison/challenge, full ledger |
| Intensive | 4–6 | explicit alternatives, dedicated challenge/verifier, checkpoint |

The model may propose a route. Code validates known IDs, catalog status,
activity fit, count, uniqueness, prerequisites, incompatibilities, and required
challenge coverage before any method pass starts.

Each method declares machine-readable `capabilities` and any
`requires_methods`. Profiles that set `challenge_required: true` must include a
method with the `challenge` capability. Human/data prerequisites remain visible
in the route explanation; only method dependencies and declared capabilities
can be enforced without interpreting the task context.

## Findings

Every finding is exactly one of:

- `fact` — directly supported observation or source statement.
- `inference` — conclusion drawn from facts; the connection is explicit.
- `assumption` — unverified condition required by the reasoning.
- `unknown` — information not currently established.

Evidence references are identifiers bound to the run manifest, not free-form
URLs inserted only at synthesis time.

## Correlation and diversity

Method diversity, model diversity, provider diversity, and source diversity are
separate fields. Multiple passes on one host/model are labelled correlated and
must not be described as independent corroboration.

## Persistence

Raw prompts and full context are not persisted by default. An explicit local
recording mode may store bounded inputs and artifacts after redaction. Hidden
chain-of-thought is never requested or stored.

## Host execution

Every run records the adapter, provider state, requested and observed model,
whether another provider was called, and a correlation group. Requested and
observed model identifiers remain `null` when the runner cannot independently
observe them. Multi-method runs on one Codex host require a non-null correlation
group, and every grouped result must carry `CORRELATED`.

Authentication evidence, process timing, and raw-stream persistence state are
recorded separately from method conclusions. A version response or login state
does not by itself prove successful submission, valid collection, or method
quality.

## Run verification

`verify-run` treats `run.json`, every method result, and `report.json` as
untrusted input. It:

1. revalidates the catalog and route;
2. re-reads repository-relative evidence and recomputes its digest;
3. requires exact, unique selected-method coverage;
4. validates method version, rigor, execution, findings, and evidence bindings;
5. recomputes each result digest, the ordered ledger, primary status, and side
   conditions;
6. checks that every report finding reference resolves exactly once; and
7. emits a schema-valid verdict with the recomputed report digest.

Bundle validity and the primary outcome are separate. A well-formed,
content-bound `FAIL`, `ERROR`, or `INCOMPLETE` run is valid evidence. A claimed
`PASS` that cannot be reproduced is invalid.

## Release eligibility

`verify-release` separately reports content consistency and release eligibility.
Content-bound files can establish that bytes and caller-declared check statuses
agree, but cannot establish who produced them or whether a named gate actually
ran. The `local-alpha` gate is registered to a fixed producer, exact check set,
raw observation format, and repository HEAD. Its verifier re-runs the checks
before deriving PASS. Every other otherwise-PASS gate remains `INCOMPLETE` and
`release_eligible` remains false until it receives an equivalent verifier.

Caller- or model-supplied pass flags are untrusted. Eligibility, if a later
verifier can derive it, still does not authorise a tag, release, remote push,
settings change, or visibility change.

The local-alpha record is an unsigned local execution record. It is not a
GitHub-hosted receipt, cryptographic provenance, or evidence that live
repository settings match source. Hosted CI and GitHub configuration therefore
remain separate release readbacks.

## Acceptance evidence

`verify-acceptance` binds a recorded run to an immutable source commit and tree,
the expected public task/profile, a tracked-file manifest, the allowlisted model
artifacts and their digests, source-mutation state, bounded lifecycle events,
process outcome, and the independently recomputed run verdict. It rejects
missing or swapped artifacts, symlinked paths, source mutations, malformed or
truncated lifecycle evidence, nonzero exits, timeouts, and disagreement between
stored and recomputed verdicts.

The current `unsigned-local-recorder` attestation establishes internal
consistency only. It is not a cryptographic signature, an independent provider
receipt, or proof of filesystem or network containment.
