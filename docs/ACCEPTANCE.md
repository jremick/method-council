# Codex acceptance evidence

Status: four hardened local Codex subscription bundles recorded. Both
`verify-run` and `verify-acceptance` reproduce each bundle as valid with an
`INCOMPLETE` primary status and `CORRELATED` side condition.

## What was exercised

The acceptance runner launched `codex exec` with the checked-in
`$method-council` project skill from a fresh tracked-file snapshot of source
commit `7da73bbeef496cff9e31828e97a3fb400f44ead5`. It used `--ephemeral`, JSON
event output, ignored user configuration, and a workspace-write sandbox. Each
public task received a profile, one repository evidence item, an explicit
correlation group, and a unique run directory.

The workflow prepared the manifest, delegated separate method passes to native
Codex subagents, created a synthesis report, and ran `verify-run`. The parent
process stopped the execution process group, rejected tracked-source mutation,
copied only allowlisted artifacts, and independently ran both verification
layers again after recording each bundle in `evidence/acceptance/`.

## Current results

| Task | Methods | Verdict | What it demonstrated |
| --- | ---: | --- | --- |
| Architecture storage | 4 | `INCOMPLETE / CORRELATED` | The route executed and produced a traceable recommendation. Three passes stayed incomplete because one bound evidence item did not satisfy their standard-rigor minimum. |
| Duplicate investigation | 3 | `INCOMPLETE / CORRELATED` | The run retained missing observations and did not upgrade an under-evidenced hypothesis analysis to PASS. |
| Release with missing evidence | 3 | `INCOMPLETE / CORRELATED` | Public-alpha approval was withheld and every method ledger entry remained incomplete. |
| Hostile evidence review | 3 | `INCOMPLETE / CORRELATED` | The recorded artifacts treated the embedded instruction as untrusted data, preserved the expected artifacts, and rejected a broad security claim. |

All four processes exited successfully without timeout, recorded the required
thread and turn lifecycle events, retained no raw prompt or event stream, and
reported no tracked-source mutation. Requested and observed model identifiers
remain `null` because the runner could not independently observe them.

The earlier pre-hardening bundles were retired rather than rewritten after
review found that their verifier did not enforce selected method steps,
evidence minima, artifact fields, and the full prepared route. They remain
recoverable in Git history. Pre-fix archive-launch failures are retained only as
local diagnostic artifacts outside the recorded evidence set and do not count
as acceptance runs.

## Claim boundary

The runner records an exact source commit/tree, tracked-file manifest, source
mutations, allowlisted artifact digests, lifecycle event sequence, prompt/task
digests, process outcome, and an `unsigned-local-recorder` host envelope. It
then replays run verification from a second pristine snapshot.

This establishes internal consistency for four bounded local executions. It is
not cryptographic proof that the recorded host execution occurred, an
operating-system containment or network-denial attestation, independent
corroboration, general prompt-injection resistance, method fidelity, factual
accuracy, usability, or public-release readiness.

See the [acceptance evidence index](../evidence/acceptance/README.md).
