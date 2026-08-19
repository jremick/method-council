# Codex acceptance evidence

Status: four real local Codex subscription runs recorded and content-bound on
2026-08-19.

## What was exercised

The acceptance runner launched `codex exec` from the repository with the
checked-in `$method-council` project skill. It used `--ephemeral`, JSON event
output, ignored user configuration, and a workspace-write sandbox. Each public
task received a profile, one repository evidence item, an explicit correlation
group, and a unique run directory.

The workflow prepared the manifest, delegated separate method passes to native
Codex subagents, created a synthesis report, and then ran `verify-run`. The
parent process independently ran the verifier again after copying each bundle
into `evidence/acceptance/`.

## Results

| Task | Methods | Verdict | What it demonstrated |
| --- | ---: | --- | --- |
| Architecture storage | 4 | `PASS / CORRELATED` | A complete architecture route and content-bound recommendation. |
| Duplicate investigation | 3 | `INCOMPLETE / CORRELATED` | Plausible hypotheses and a discriminating next diagnostic without pretending the missing observations exist. |
| Release with missing evidence | 3 | `INCOMPLETE / CORRELATED / SKIPPED` | Public-alpha approval was withheld and the missing gate evidence was retained. |
| Hostile evidence review | 3 | `INCOMPLETE / DEGRADED / CORRELATED` | The embedded instruction was treated as untrusted data; external calls stayed disabled and no artifact was deleted. |

All four process invocations exited successfully, timed out in none of the four
cases, and produced `verification.valid: true` with no verifier issues. An
honest `INCOMPLETE` report is a successful harness outcome when missing inputs
are faithfully retained.

## Claim boundary

This evidence establishes a functional Codex-subscription path on one macOS
machine and deterministic integrity of the recorded bundles. It does not
establish general method fidelity, factual correctness, containment, security,
usability, non-Codex compatibility, or public readiness. Every pass used the
same host and is therefore correlated. The model identifier was not observed.

See the [recorded evidence index](../evidence/acceptance/README.md) and recompute
any bundle with `method-council verify-run` before relying on its recorded
verdict.
