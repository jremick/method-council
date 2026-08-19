# GitHub settings plan

Status: plan only. No GitHub remote exists and no settings have been applied.

Repository creation, remote pushes, releases, and visibility changes require a
separate explicit approval and live readback.

## Recommended repository metadata

| Setting | Pre-public recommendation |
| --- | --- |
| Repository name | `method-council` |
| Description | `Structured methods, separate analysis passes, and one traceable report.` |
| Visibility | Private until the public-alpha gate passes and publication is approved |
| Homepage | Leave blank until a maintained docs or project site exists |
| Topics | `codex`, `ai-agents`, `structured-analysis`, `decision-support`, `methodology`, `python` |
| Issues | Enable when the private remote is created; use for concrete bugs and feature requests |
| Discussions | Off initially; no maintained community channel exists |
| Wiki | Off; canonical documentation remains in the repository |
| Projects | Off until a maintained public roadmap requires it |
| Releases | None during pre-public development |
| Social preview | Asset and upload deferred until the public surface and name are final |

Topics should be rechecked against the actual implementation at publication.
Avoid terms such as `intelligence-grade`, `official`, `audited`, or
`production-ready` unless later evidence directly supports them.

## Stage 1 — Pre-Public Candidate

Before any visibility change:

- create the repository as private;
- push only after tracked-file, history, secret, and personal-path inspection;
- keep the default branch aligned with the local repository;
- run CI and record the actual required job contexts;
- enable secret scanning and push protection where the account/repository tier
  exposes them;
- enable private vulnerability reporting and replace the placeholder language in
  `SECURITY.md` with the live private-reporting route;
- configure a ruleset or branch protection against the observed CI contexts;
- keep administrator bypass policy explicit;
- confirm Apache-2.0 detection matches `LICENSE`, `pyproject.toml`, and README;
- leave Discussions, Wiki, Projects, Packages, and Releases disabled unless a
  maintained purpose exists;
- confirm all README and documentation links resolve from GitHub.

Passing source checks locally is not evidence that these GitHub settings exist.

## Later public-alpha gate

Public visibility should be a final, separate action after release eligibility and
publication are both approved. Immediately before and after the change, read back:

- owner/name, default branch, visibility, description, topics, and homepage;
- license detection and the complete tracked-file surface;
- latest default-branch CI result and required ruleset/check contexts;
- secret scanning and push protection state;
- private vulnerability reporting state;
- issues, discussions, wiki, projects, packages, and releases state;
- custom social preview state, if an image has actually been uploaded;
- anonymous clone and README rendering from a non-authenticated surface.

Do not describe a committed preview image as an applied GitHub social preview.
Do not treat a commit hash as proof that rendered or live settings match source.

## Initial public support posture

For public alpha:

- Issues: on, with bounded bug and concrete feature-request guidance.
- Security: GitHub private vulnerability reporting, verified live.
- Discussions: off unless the maintainer commits to monitoring it.
- Wiki and Projects: off.
- Release: either no release with explicit source-only alpha language, or a
  clearly marked prerelease after release evidence passes.

The README, `CONTRIBUTING.md`, and `SECURITY.md` must be updated together when
these channels become real.
