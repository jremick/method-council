# GitHub settings posture

Repository: `jremick/method-council`

Target: **Stage 2 public alpha**. GitHub settings are part of the release gate
and must be read back live. This document records the intended posture; it is
not evidence that a setting is active.

## Public metadata

| Setting | Alpha posture |
| --- | --- |
| Description | `Structured methods, separate analysis passes, and one traceable report.` |
| Default branch | `main` |
| Homepage | Blank until a maintained project site exists |
| Topics | `codex`, `ai-agents`, `structured-analysis`, `decision-support`, `methodology`, `python` |
| Issues | On, with bounded bug and feature-request forms |
| Discussions | Off; no monitored community forum exists |
| Wiki | Off; canonical documentation stays in the repository |
| Projects | Off until a maintained public roadmap exists |
| Packages | No package-registry publication in alpha |
| Releases | Source-only `v0.1.0-alpha.1` prerelease |
| Social preview | Prepared in `assets/exported/social-preview.png`; upload and rendered state verified separately |

Avoid terms such as `intelligence-grade`, `official`, `audited`,
`production-ready`, or `decision quality improvement` unless later evidence
directly supports them.

## Security and branch controls

The alpha target is:

- secret scanning and push protection enabled where GitHub exposes them;
- private vulnerability reporting enabled;
- Dependabot alerts and security updates enabled;
- weekly Dependabot version updates for `uv` and GitHub Actions;
- CodeQL default setup for Python, including remote and local threat models,
  where the repository/account exposes default setup;
- `main` protected by the observed hosted CI check in strict mode;
- conversation resolution required before merge;
- force pushes and branch deletion disabled;
- administrator bypass retained for the single-maintainer alpha;
- merge commits disabled, squash and rebase merging enabled; and
- head branches deleted after merge.

The selected administrator policy is an explicit availability tradeoff for a
personal repository. It is not equivalent to independent review or a ruleset
with no bypass.

## Required live readback

Before and after the visibility change and prerelease publication, read back:

- owner/name, default branch, visibility, description, topics, and homepage;
- license detection and the complete tracked-file surface;
- latest default-branch CI result and the exact required check context;
- branch protection or ruleset behavior;
- secret scanning, push protection, Dependabot, and CodeQL state;
- private vulnerability reporting state;
- issues, discussions, wiki, projects, packages, and releases state;
- anonymous clone and README access; and
- prerelease tag, target commit, source archives, and published notes.

Do not describe the committed social-preview image as applied unless GitHub's
live rendered setting is separately verified. Do not infer a required check
context from workflow source; read it from a successful hosted check run.

## Support posture

- Use Issues for reproducible bugs and bounded feature requests.
- Use GitHub private vulnerability reporting for suspected vulnerabilities.
- Do not promise response times, consulting, compatibility, or roadmap dates.
- Keep Discussions off until the maintainer commits to monitoring it.

## Claim boundary

Public alpha means the source and bounded Codex path are inspectable. It does
not mean the methods improve decisions, that non-Codex adapters work, that the
acceptance runner is an operating-system sandbox, or that a stable API exists.
The next confidence program is specified in
[`evals/CONFIDENCE_PLAN.md`](../evals/CONFIDENCE_PLAN.md).
