# Wave 1 evaluation fixtures

Version: 0.1.0

## Purpose

The eight fixtures are public-safe, offline inputs for deterministic contract
tests. They do not call a provider, assert prose quality, or stand in for live
Codex acceptance runs. They test status precedence, side-condition retention,
route disposition, synthesis behavior, and explicit claim limits.

`tests/fixtures/inventory.json` is the canonical inventory. Each case provides:

- a bounded synthetic question and canonical method route;
- privacy settings that forbid raw-prompt persistence, hidden chain-of-thought
  requests, and external calls;
- observable gate statuses and reason codes;
- the expected primary status derived by
  `FAIL > ERROR > INCOMPLETE > PASS`;
- required information to preserve and claims that the report must not make.

## Corpus

| Fixture | Class | Expected | Contract under test |
|---|---|---:|---|
| `architecture-tradeoff` | representative | `PASS + CORRELATED` | Evidence-bound tradeoffs and same-host disclosure |
| `debugging-rca` | representative | `PASS + CORRELATED` | Fact/inference/unknown separation and falsifiable diagnostics |
| `release-decision-missing-evidence` | failure | `INCOMPLETE + SKIPPED` | Missing release evidence cannot become PASS |
| `adversarial-risk` | adversarial | `PASS + CORRELATED` | Trust boundaries, assumptions, controls, and residual risk |
| `hostile-prompt-injection` | adversarial | `PASS` | Untrusted directives do not alter policy or status authority |
| `provider-degraded-malformed` | failure | `ERROR + DEGRADED` | Malformed output cannot be simulated or aggregated |
| `split-conclusion` | representative | `PASS + CORRELATED` | Valid disagreement is preserved without voting theater |
| `unsupported-official-standard-claim` | failure | `FAIL + SKIPPED` | Unsupported provenance claims fail before routing |

## Offline checks

From the repository root:

```bash
python3 scripts/validate_fixtures.py
python3 scripts/tracked_file_hygiene.py
pytest tests/fixtures/test_evaluation_helpers.py
```

`validate_fixtures.py` uses only the Python standard library. It ensures that
the inventory exactly matches the eight JSON files, validates the bounded
contract, applies rigor method-count limits, and recomputes primary status from
the gate inputs.

`tracked_file_hygiene.py` asks Git only for the tracked-file inventory. It
scans local tracked text for narrow high-risk patterns and emits only paths and
category labels. It never prints matches. It is a release hygiene signal, not
a secret-scanning service or history audit.

## Evidence limits

Passing these checks proves only that the checked fixture envelopes are
internally consistent and that the narrow tracked-file scan found no matching
pattern. It does not prove:

- method fidelity or semantic output quality;
- resistance to all prompt-injection techniques;
- absence of secrets in Git history, untracked files, ignored files, binary
  files, provider logs, or other systems;
- provider availability, authentication, or functional task completion;
- release eligibility, usability, accessibility, or public readiness.

Public-alpha evidence still requires real Codex subscription runs, clean-clone
verification, content-bound release reports, independent acceptance, and live
GitHub security/settings readback.
