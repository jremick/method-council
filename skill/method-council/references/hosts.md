# Host use and capability levels

Read this reference when the current host is not Codex, the deterministic CLI is
unavailable, or the user asks for multi-tool or multi-model execution.

## Codex

- Invoke the user skill as `$method-council`.
- The tested local path uses the installed `method-council` CLI and a ChatGPT
  subscription.
- Native subagents may run separate method passes. Same-host passes remain
  `CORRELATED`.

## Claude Code

- Invoke the personal or project skill as `/method-council`.
- Install the CLI locally before use. Run `method-council validate` from the
  project that contains the question and evidence.
- Claude Code can coordinate separate passes, but Method Council has not yet
  completed the same host-specific acceptance suite as Codex. State this limit.

## Claude and Cowork account skills

An uploaded skill ZIP can contain a read-only method catalogue but cannot assume
that the deterministic CLI is installed in the managed execution environment.

If `method-council validate` succeeds, use the normal verified workflow. If it
does not, the host may use instruction-only mode:

1. Read only the selected method definitions under
   `references/catalog/methods/` when that directory is present.
2. Apply each selected method in a separate pass and preserve facts,
   assumptions, unknowns, disagreement, and missing evidence.
3. Do not emit a deterministic `PASS` or claim that the route, result schema,
   evidence binding, aggregation, or report was verified.
4. Label the result `INCOMPLETE`, with `deterministic CLI unavailable` as a
   limitation and installation of the CLI as the next verification step.

Instruction-only mode is a useful analysis fallback. It is not equivalent to a
content-bound Method Council run.

## Other Agent Skills hosts

Use the same distinction:

- Skill plus installed CLI: normal workflow, subject to host-specific execution
  limits.
- Skill without CLI: instruction-only `INCOMPLETE` fallback when the bundled
  catalogue is available.
- No skill discovery or code execution: unsupported until a host adapter or
  manual integration is documented and tested.

An installed provider executable proves presence only. Never infer
authentication, model availability, submission, completion, or compatibility.
