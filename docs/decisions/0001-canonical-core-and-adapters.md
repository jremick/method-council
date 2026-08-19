# ADR 0001: Canonical core with host adapters

- **Status:** accepted for Wave 0/1
- **Date:** 2026-08-19

## Decision

Keep method semantics and run contracts host-neutral. Build Codex as the first
validated adapter and treat later providers as conformance surfaces.

The native Codex skill orchestrates semantic work. A small local Python core
validates definitions, routes, artifacts, status, and evidence.

## Consequences

- Codex subscription use does not require a separate provider API key.
- Host copies cannot redefine methods.
- Compatibility claims require host-specific real-run evidence.
- The first public alpha can ship without delaying on all providers.
- The project maintains both Markdown/YAML method sources and JSON evidence
  artifacts, with generation and parity checks where mirrors are necessary.
