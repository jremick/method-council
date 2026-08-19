# ADR 0003: Content-bound run verification

Status: accepted for Wave 2  
Date: 2026-08-19

## Decision

A complete run is a directory containing one run manifest, exactly one checked
result for every selected method, one traceable report, and one deterministic
verdict. `verify-run` re-reads those artifacts, validates every schema and
evidence reference, recomputes result and report digests, checks exact method
coverage, derives status and side conditions, and compares the report ledger to
the recomputed ledger.

Method results record observable execution metadata. Results sharing a non-null
correlation group must carry `CORRELATED`; a report may not describe those
passes as independent evidence. Missing or malformed artifacts cannot be
replaced by coordinator prose or a caller-supplied `PASS`.

## Consequences

- The model remains responsible for method application and synthesis.
- Code owns completeness, binding, digest, status, and correlation gates.
- A valid `PASS` verdict proves contract integrity only. It does not prove
  factual accuracy, methodology fidelity, independence, or decision quality.
- The verifier is a recorder and gate, not an operating-system sandbox.
