# Recorded Codex acceptance evidence

These four bundles were produced by `codex exec` using an existing ChatGPT
authentication on 2026-08-19. Each run used the checked-in project skill,
public synthetic task data, native Codex subagents, and the same-host
`CORRELATED` label. The runner did not persist its raw prompt or raw event
stream and did not request another provider.

| Bundle | Profile | Verified status | Side conditions |
| --- | --- | --- | --- |
| `accept-architecture-storage-20260819` | `standard-architecture` | `PASS` | `CORRELATED` |
| `accept-investigation-duplicates-20260819` | `standard-investigation` | `INCOMPLETE` | `CORRELATED` |
| `accept-release-missing-evidence-20260819` | `standard-decision` | `INCOMPLETE` | `CORRELATED`, `SKIPPED` |
| `accept-hostile-review-20260819` | `standard-review` | `INCOMPLETE` | `DEGRADED`, `CORRELATED` |

`INCOMPLETE` is a valid outcome. It means the selected method procedures
required evidence or a decision condition that the task did not provide. A
bundle is accepted only when `verification.json` has `valid: true`; validity
means that deterministic checks reproduced its status, side conditions,
method coverage, evidence references, file digests, ledger, and report digest.

Each bundle contains:

- `run.json`: content-bound route, evidence, and execution contract;
- `method-results/*.json`: separately produced structured passes;
- `report.json`: synthesis with the recomputed ledger;
- `verification.json`: deterministic read-back verdict;
- `host-execution.json`: bounded CLI, authentication, timing, persistence, and
  verification metadata.

The harness observed `codex-cli 0.147.0` and ChatGPT authentication. It did not
independently observe the requested or executed model, so both model fields are
`null`. These bundles do not prove factual accuracy, general prompt-injection
resistance, method fidelity, provider independence, security, usability, or
release readiness. The runner is a process wrapper and is not an operating-
system sandbox.

Recompute any bundle from the repository root:

```bash
uv run method-council verify-run \
  evidence/acceptance/accept-hostile-review-20260819
```
