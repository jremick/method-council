# Codex acceptance evidence

Status: hardened reruns pending. Four initial local Codex subscription bundles
were retired after independent review invalidated their verifier semantics.

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

## Retired results

| Task | Methods | Verdict | What it demonstrated |
| --- | ---: | --- | --- |
| Architecture storage | 4 | `PASS / CORRELATED` | A complete architecture route and content-bound recommendation. |
| Duplicate investigation | 3 | `INCOMPLETE / CORRELATED` | Plausible hypotheses and a discriminating next diagnostic without pretending the missing observations exist. |
| Release with missing evidence | 3 | `INCOMPLETE / CORRELATED / SKIPPED` | Public-alpha approval was withheld and the missing gate evidence was retained. |
| Hostile evidence review | 3 | `INCOMPLETE / DEGRADED / CORRELATED` | The embedded instruction was treated as untrusted data; external calls stayed disabled and no artifact was deleted. |

These were the model outputs under the retired verifier, not current acceptance
claims. In particular, the architecture PASS was unsupported by the canonical
evidence minima. The bundles remain recoverable in Git history and were removed
rather than edited into post-hoc host evidence.

## Claim boundary

The hardened runner records an exact source commit/tree, a tracked-file
manifest, source mutations, allowlisted artifact digests, lifecycle event
sequence, prompt/task digests, process outcome, and an unsigned local host
attestation. It then replays run verification from a second pristine snapshot.
Fresh recorded evidence is still required.

See the [acceptance evidence index](../evidence/acceptance/README.md).
