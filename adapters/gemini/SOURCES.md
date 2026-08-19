# Gemini CLI adapter sources

Accessed 2026-08-19. These primary sources support only the documented CLI
concepts recorded in `adapter.yaml`; they do not prove that this preview adapter
is authenticated or functionally compatible.

- [Gemini CLI reference](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/cli-reference.md) —
  version, non-interactive prompt, model, sandbox, approval, extension, and
  output-format flags.
- [Gemini CLI headless mode](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md) —
  JSON and streaming JSON envelopes, event types, model metadata, and basic
  process exit codes.
- [Gemini CLI troubleshooting](https://github.com/google-gemini/gemini-cli/blob/main/docs/resources/troubleshooting.md#exit-codes) —
  authentication, input, sandbox, configuration, and turn-limit exit codes.
- [Gemini CLI session management](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/session-management.md) —
  documents default local session persistence, which must be assessed before
  enabling this adapter under Method Council's no-raw-prompt default.

## Claim boundary

The candidate command is disabled. No live request, credential lookup, provider
SDK, or Gemini CLI installation check was used to create these files. Gemini
CLI documents automatic local session history, so raw-prompt non-persistence is
not yet proven and is an enablement blocker. A host wrapper also needs
version-specific tool-deny policy validation, authentication readback,
collection fixtures, cancellation tests, and adversarial validation.
