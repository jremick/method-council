# Security policy

## Current reporting status

Method Council is a pre-public local build. No GitHub remote or public release
exists, so **no public vulnerability reporting channel is active** and no support
response time is promised.

Before public alpha, the maintainer intends to enable GitHub private vulnerability
reporting and verify the setting through a live readback. This file will then link
to the repository's private reporting form. Suspected vulnerabilities should not
be posted in public issues, discussions, logs, or example artifacts.

## Supported versions

There are no supported public versions yet. A supported-version table will be
added when the first public release or prerelease is created.

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

Once private reporting is active, a useful report should include:

- affected version, commit, or component;
- observed behavior and security impact;
- minimal reproduction steps using non-sensitive fixtures;
- whether provider calls, tools, credentials, or persisted artifacts are involved;
- suggested remediation, if known.

Do not include real secrets, private prompts, personal data, or exploit material
beyond what is necessary for private reproduction.

See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) for the evolving trust and abuse
model. Its presence does not imply an external security audit.
