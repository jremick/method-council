# Contributing

Method Council is currently a local private build. There is no public repository,
issue tracker, or contribution channel, and outside submissions are not yet being
accepted. This file records the contribution contract that should be activated
and verified before public alpha.

## Contribution principles

- Preserve the canonical method, schema, status, and evidence contracts.
- Prefer the smallest change that addresses a demonstrated need.
- Keep model judgment and deterministic enforcement separate.
- Do not simulate a failed provider or method pass and count it as successful.
- Do not request, expose, or persist hidden chain-of-thought.
- Do not add credentials, raw prompts, personal paths, private logs, or unrelated
  context to fixtures or commits.
- Keep provider-specific behavior in adapters. Do not redefine canonical method
  semantics for a host.
- Describe evidence limits honestly. Tests prove their checked contracts, not
  usability, accessibility conformance, method fidelity, or analytical truth.

## Method contributions

A method contribution must include:

1. A primary or authoritative source that supports the method's stated basis.
2. Clear `adapted from` language where the implementation is an adaptation.
3. Applicability, contraindications, prerequisites, and failure modes.
4. Rapid, standard, or intensive variants only where the procedure supports them.
5. A typed output contract and an example that contains no sensitive material.
6. Claim limits. Do not describe a method as official, certified, standard,
   de facto, or intelligence-grade unless the cited source supports that exact
   wording.

Do not copy protected source text, tables, templates, prompts, or visual assets.
Summarize the procedure in original language and preserve the citation.

## Development checks

The repository targets Python 3.12 and uses `uv`.

```bash
uv sync --frozen --all-groups
uv run --frozen method-council validate
uv run --frozen python scripts/sync_codex_skill.py check
uv run --frozen pytest -q
uv run --frozen ruff check .
uv run --frozen ruff format --check .
```

These are the canonical checks for the repository. Public contribution guidance
must not describe them as a passing clean-checkout path until release evidence
confirms that result.

## Change expectations

- Add tests for behavior and failure cases changed by the contribution.
- Use hostile and malformed fixtures for trust-boundary changes.
- Update source citations when a method claim changes.
- Update public documentation when a user-facing contract changes.
- Keep generated output linked to its canonical input and generator version.
- Explain any skipped validation and the practical risk in the pull request.

When a public remote exists, contribution mechanics, issue templates, review
expectations, and maintainer response boundaries will be added only for channels
that are actually enabled and monitored.
