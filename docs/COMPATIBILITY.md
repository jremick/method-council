# Compatibility

Compatibility is reported per host path. An adapter file or executable on
`PATH` is not functional evidence.

| Host | Surface | Current evidence | External calls by default | Status |
| --- | --- | --- | --- | --- |
| Codex | Repo-local skill, CLI core, native subagents | Four ChatGPT-authenticated public-safe runs; content-bound bundles; model ID unobserved | No additional provider calls | Locally exercised preview |
| Claude Code | Disabled adapter compiler input | Contract and official-source review only; no install, auth, or task run | Disabled | Unverified preview |
| Gemini CLI | Disabled adapter compiler input | Contract and official-source review only; no install, auth, or task run | Disabled | Unverified preview |
| OpenCode | None | No adapter or functional evidence | Not applicable | Planned, unsupported |

The canonical method, profile, run, method-result, report, provider-status, and
verdict contracts remain host-neutral. Host adapters must preserve those
contracts and add explicit authentication, launch, collection, timeout,
cancellation, error-normalization, and model-observation evidence before their
compatibility claim can advance.

Codex remains `preview` because four local runs cannot establish general
method quality, usability, or version-wide compatibility. Claude and Gemini
launch/collect capabilities remain disabled until their provider-specific
integration and adversarial tests exist.
