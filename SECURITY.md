# Security policy

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/jremick/method-council/security/advisories/new).
Do not post suspected vulnerabilities in public issues, discussions, logs, or
example artifacts. No response or remediation time is guaranteed during alpha.

## Supported versions

| Version | Security fixes |
| --- | --- |
| `0.1.x` alpha | Best effort |
| Earlier snapshots | Not supported |

## Security boundaries

The project treats the following as untrusted data:

- user prompts and supplied context;
- repository and retrieved source content;
- model and provider output;
- adapter-supplied status or availability claims;
- caller-supplied evidence and release flags.

Deterministic validation is intended to control route limits, schema and semantic
validity, evidence binding, primary status, and release eligibility. External
provider calls, tool side effects, and raw-prompt persistence are deny-by-default.

## Useful report contents

A useful report should include:

- affected version, commit, or component;
- observed behavior and security impact;
- minimal reproduction steps using non-sensitive fixtures;
- whether provider calls, tools, credentials, or persisted artifacts are involved;
- suggested remediation, if known.

Do not include real secrets, private prompts, personal data, or exploit material
beyond what is necessary for private reproduction.

See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for the evolving trust and abuse
model. Its presence does not imply an external security audit.
