# Changelog

All notable changes to Method Council will be recorded here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and versions use [Semantic Versioning](https://semver.org/) with explicit
prerelease labels.

## [Unreleased]

### Added

- Causal Factors Analysis, Outside View / Reference Class Check, and Outside-In
  Context Scan as source-backed, unevaluated preview methods.
- Three complementary profiles for causal investigation, outside-view
  forecasting, and context analysis.
- An optional per-method multi-model execution plan with deterministic coverage,
  target, correlation, and result-assignment checks.
- A council-in-practice diagram and multi-model guidance in the README and
  existing Codex skill.
- A complex council example and visible source-material inputs in the README
  diagrams.

### Changed

- The method evaluation report now lists catalogue methods without specimens as
  unevaluated instead of borrowing confidence or rejecting the expanded
  catalogue.
- The Codex adapter defaults to one GPT while allowing an explicit,
  user-authorised multi-model plan. Claude and Gemini execution remain disabled
  previews.
- The README opening and skill-first quick start use simpler, more direct
  language.

## [0.1.0-alpha.1] - 2026-08-20

### Added

- Eight source-backed analytical methods and six activity profiles.
- A deterministic CLI for catalog, route, result, run, acceptance, and release
  validation.
- A Codex-subscription-first skill and checked-in project projection.
- Five commit-bound Codex acceptance bundles with deterministic read-back.
- Disabled preview contracts for Claude Code and Gemini CLI.
- A recorded eight-method semantic screen and a staged usefulness-evaluation
  plan.
- A candidate-bound local-alpha release producer whose verifier independently
  reruns its registered checks.

### Known limitations

- Method usefulness and fidelity have not been independently validated.
- The recorded model runs are same-host, correlated, and unsigned local
  evidence; they are not execution authenticity or containment proof.
- Claude and Gemini execution is not implemented or verified.
- Schemas, CLI commands, methods, profiles, and adapters may change before beta.
- This GitHub prerelease is source-only; no package is published to PyPI.

[0.1.0-alpha.1]: https://github.com/jremick/method-council/releases/tag/v0.1.0-alpha.1
