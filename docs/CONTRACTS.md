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

## Release eligibility

Release eligibility is derived from content-bound evidence reports. Caller- or
model-supplied pass flags are untrusted. Eligibility does not authorise a tag,
release, remote push, settings change, or visibility change.
