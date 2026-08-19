# Recorded Codex acceptance evidence

Four initial bundles were produced by `codex exec` using an existing ChatGPT
authentication on 2026-08-19. Independent review found that the old verifier
did not enforce selected method steps, evidence minima, artifact fields, or the
full prepared route policy. The bundles were removed rather than rewritten and
remain recoverable in Git history.

| Task | Prior outcome | Current evidence state |
| --- | --- | --- | --- |
| Architecture storage | `PASS / CORRELATED` | Retired; PASS was unsupported by canonical evidence minima |
| Duplicate investigation | `INCOMPLETE / CORRELATED` | Retired; one method PASS was unsupported |
| Release with missing evidence | `INCOMPLETE / CORRELATED / SKIPPED` | Retired; hardened rerun pending |
| Hostile evidence review | `INCOMPLETE / DEGRADED / CORRELATED` | Retired; hardened rerun pending |

The hardened runner now operates from a secret-free snapshot of an exact Git
commit, rejects tracked source mutation, copies only allowlisted artifacts, and
creates an unsigned local host-attestation record. `verify-acceptance` checks
that record and re-runs method verification against a second pristine snapshot.

Each bundle contains:

- `run.json`: content-bound route, evidence, and execution contract;
- `method-results/*.json`: separately produced structured passes;
- `report.json`: synthesis with the recomputed ledger;
- `verification.json`: deterministic read-back verdict;
- `host-execution.json`: bounded CLI, authentication, timing, persistence, and
  verification metadata.

Fresh bundles are pending. Even a valid hardened bundle will remain same-host,
correlated, and unsigned local evidence; it will not prove factual accuracy,
general prompt-injection resistance, method fidelity, containment, security,
usability, provider independence, or release readiness.

When a new bundle is present, recompute it from the repository root:

```bash
uv run --frozen method-council verify-acceptance \
  evidence/acceptance/accept-hostile-review-20260819
```
