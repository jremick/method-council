# Recorded Codex acceptance evidence

Five hardened bundles were produced by `codex exec` using an existing ChatGPT
authentication on 2026-08-19 and 2026-08-20. The first four were executed from
source commit `7da73bbeef496cff9e31828e97a3fb400f44ead5` and source tree
`03af9cb01c76f454b7182e428b7de0d760051b50`. The forecast bundle was executed
from source commit `6f9d96f3a22a3f4b3217199d88a0bce17a6911f7` and source tree
`f9e6ce7f35c45b721264a83e27065bf128a78617`.

| Task | Current outcome | Recorded bundle |
| --- | --- | --- |
| Architecture storage | `INCOMPLETE / CORRELATED` | `accept-architecture-storage-20260819` |
| Duplicate investigation | `INCOMPLETE / CORRELATED` | `accept-investigation-duplicates-20260819` |
| Release with missing evidence | `INCOMPLETE / CORRELATED` | `accept-release-missing-evidence-20260819` |
| Hostile evidence review | `INCOMPLETE / CORRELATED` | `accept-hostile-review-20260819` |
| Provider-plugin forecast | `INCOMPLETE / CORRELATED` | `accept-forecast-plugin-ecosystem-20260820-v2` |

The hardened runner operates from a tracked-file snapshot of an exact Git
commit, rejects tracked-source mutation, copies only allowlisted artifacts, and
creates an unsigned local host-evidence record. `verify-acceptance` checks that
record and re-runs method verification against a second pristine snapshot.

Each bundle contains:

- `run.json`: content-bound route, evidence, and execution contract;
- `method-results/*.json`: separately produced structured passes;
- `report.json`: synthesis with the recomputed ledger;
- `verification.json`: deterministic read-back verdict;
- `host-execution.json`: bounded CLI, authentication, timing, persistence, and
  verification metadata;
- `acceptance-verdict.json`: recomputed binding between the host record, source
  snapshot, model artifacts, and run verdict.

Every recorded process exited successfully without timeout, all expected
lifecycle events were observed, no tracked-source mutation was recorded, and
both deterministic verifiers report no issues. Raw prompts and raw event streams
were not persisted. The model requested and observed fields are `null`.

The earlier pre-hardening bundles were removed rather than rewritten after
independent review found missing semantic gates; they remain recoverable in Git
history. The current bundles are still same-host, correlated, and
`unsigned-local-recorder` evidence. They do not prove factual accuracy, general
prompt-injection resistance, method fidelity, network denial, operating-system
containment, security, usability, provider independence, or release readiness.
The first four predate the runner's explicit `best-effort-unverified`
descendant-cleanup record. The forecast bundle exercises that record, but its
sampled process-table observation still makes no process-lifetime containment
claim.

Recompute a bundle from the repository root:

```bash
uv run --frozen method-council verify-acceptance \
  evidence/acceptance/accept-hostile-review-20260819
```
