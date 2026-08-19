# Claude Code adapter sources

Accessed 2026-08-19. These primary sources support only the documented CLI
concepts recorded in `adapter.yaml`; they do not prove that this preview adapter
is authenticated or functionally compatible.

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-usage) —
  `--version`, print mode, JSON and streaming JSON output, JSON Schema structured
  output, model selection, maximum turns, tool restrictions, non-persistence,
  and permission modes.
- [Claude Code authentication commands](https://code.claude.com/docs/en/cli-usage#cli-commands) —
  documents `claude auth status`; the preview adapter deliberately does not run
  it or infer authentication from CLI presence.

## Claim boundary

The candidate command is disabled. No live request, credential lookup, provider
SDK, or Claude Code installation check was used to create these files. The host
wrapper still needs version-specific probes, authentication readback,
structured-output fixtures, cancellation tests, and adversarial validation.
