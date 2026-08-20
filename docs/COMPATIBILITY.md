# Compatibility

Compatibility is reported per host path. An adapter file or executable on
`PATH` is not functional evidence.

| Host | Surface | Current evidence | External calls by default | Status |
| --- | --- | --- | --- | --- |
| Codex | Personal or project skill, portable CLI, native subagents | Clean installed-runtime checks plus five commit-bound ChatGPT-authenticated runs; all recorded runs remain `INCOMPLETE / CORRELATED`, and the host envelope is unsigned | No additional provider calls | Hardened, locally exercised preview |
| Claude Code | Personal or project skill and portable CLI | Skill projection, install layout, packaged catalogue, and cross-project CLI behavior are checked; no Claude-hosted semantic acceptance run | No additional provider calls | Installable alpha; execution unverified |
| Claude / Cowork | Account-upload skill with read-only catalogue | Deterministic ZIP construction and contents are checked; no account upload or managed-session run | None | Instruction-only fallback; unverified |
| Claude automated adapter | Disabled adapter compiler input | Contract and official-source review only; no authenticated launch, collection, or task run | Disabled | Unverified preview |
| Gemini CLI | Disabled adapter compiler input | Contract and official-source review only; no install, auth, or task run | Disabled | Unverified preview |
| OpenCode | None | No adapter or functional evidence | Not applicable | Planned, unsupported |

The canonical method, profile, run, method-result, report, provider-status, and
verdict contracts remain host-neutral. Host adapters must preserve those
contracts and add explicit authentication, launch, collection, timeout,
cancellation, error-normalization, and model-observation evidence before their
compatibility claim can advance.

The Agent Skill surface is separate from an automated provider adapter. Claude
Code can follow the skill interactively while its launch/collect adapter remains
disabled. The run contract supports an optional per-method multi-model execution
plan. That makes assignments and correlation testable; it does not make the
disabled Claude or Gemini adapters functional. A current host must expose a
supported, authorised provider route and return the assigned execution metadata
before a non-default result can validate.

Codex remains `preview` because five local runs cannot establish general method
quality, usability, version-wide compatibility, operating-system containment,
or authentic execution without trusting the local recorder. The runner did not
independently observe requested or actual model identifiers. Claude skill
installation is not Claude execution evidence. Claude and Gemini launch/collect
capabilities remain disabled until their provider-specific integration and
adversarial tests exist.
