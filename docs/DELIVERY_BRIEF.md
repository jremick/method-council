# Delivery brief

## Value

- **User:** builders, researchers, operators, and reviewers using Codex for
  consequential but human-owned analysis and decisions.
- **Problem:** ordinary multi-agent councils often substitute persona variety
  and fluent consensus for method fidelity, evidence traceability, and honest
  uncertainty.
- **Value hypothesis:** a small set of source-backed method passes, surrounded
  by deterministic contracts, produces a more inspectable and useful decision
  artifact than persona roleplay or unstructured model debate.
- **Measurable outcome for this phase:** a private local repository with frozen
  contracts, source-backed method foundations, a deterministic core, a Codex
  skill foundation, negative fixtures, and a coherent design system.
- **Source of truth:** repository schemas, method records, tests, and evidence
  artifacts—not planning prose or model claims.

## Risk and gates

Risk tier: **Tier 3** because the design covers AI subagents, untrusted input,
provider adapters, CI/supply-chain configuration, and a future public surface.

Required before the next phase:

- Value, architecture, trust boundary, and status contracts are explicit.
- Method/source claims are reviewable and bounded.
- Deterministic validators and negative tests cover high-risk boundaries.
- The Codex path has a bounded, inspectable interaction contract.
- Dependency and workflow changes are reviewable and locked.
- No remote repository, provider call, release, or public write occurs.

## Non-goals

- No hosted service, dashboard, user accounts, or remote telemetry.
- No public release or GitHub settings mutation.
- No claim that a method, provider, UX, or release is independently validated.
- No generated bitmap hero in this phase.
- No provider adapter beyond foundation contracts and the Codex-first surface.

## Stop conditions

Stop and request a scope delta if implementation requires a new authentication
path, external provider billing, public/external writes, material dependencies,
schema redesign after lane work starts, or copying non-original source/assets.

## Revert path

This phase is local and version controlled. Revert individual commits or delete
the unpushed local repository after review. No external system rollback is
required because external writes are out of scope.
