# Compatibility

Compatibility is reported per host path. An adapter file or executable on
`PATH` is not functional evidence.

| Host | Surface | Current evidence | External calls by default | Status |
| --- | --- | --- | --- | --- |
| Codex | Repo-local skill, CLI core, native subagents | Five commit-bound ChatGPT-authenticated runs pass run and host-evidence verification; all are `INCOMPLETE / CORRELATED`, and the host envelope is unsigned | No additional provider calls | Hardened, locally exercised preview |
| Claude Code | Disabled adapter compiler input | Contract and official-source review only; no install, auth, or task run | Disabled | Unverified preview |
| Gemini CLI | Disabled adapter compiler input | Contract and official-source review only; no install, auth, or task run | Disabled | Unverified preview |
| OpenCode | None | No adapter or functional evidence | Not applicable | Planned, unsupported |

The canonical method, profile, run, method-result, report, provider-status, and
verdict contracts remain host-neutral. Host adapters must preserve those
contracts and add explicit authentication, launch, collection, timeout,
cancellation, error-normalization, and model-observation evidence before their
compatibility claim can advance.

The run contract now supports an optional per-method multi-model execution plan.
That makes assignments and correlation testable; it does not make the disabled
Claude or Gemini adapters functional. A current host must expose a supported,
authorised provider route and return the assigned execution metadata before a
non-Codex result can validate.

Codex remains `preview` because five local runs cannot establish general method
quality, usability, version-wide compatibility, operating-system containment,
or authentic execution without trusting the local recorder. The runner did not
independently observe requested or actual model identifiers. Claude and Gemini
launch/collect capabilities remain disabled until their provider-specific
integration and adversarial tests exist.
