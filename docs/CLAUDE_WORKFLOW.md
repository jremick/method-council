# Claude workflow

## Claude Code

Install the CLI and personal skill:

```bash
python3 scripts/install.py --claude-code
method-council validate
```

Invoke `/method-council` in Claude Code. Run the task from the project that owns
the question, evidence, and resulting `runs/` directory.

Claude Code can apply the same method definitions and deterministic contracts as
Codex. The skill surface and portable CLI are installation-tested. A complete
Claude-hosted semantic acceptance suite has not yet run, so do not describe this
path as equivalent to the recorded Codex evidence.

The `adapters/claude/adapter.yaml` file is a separate automation contract. Its
launch and collection stages remain disabled. Using the skill interactively in
Claude Code does not enable that provider adapter.

## Claude and Cowork

Generate an account-upload skill:

```bash
python3 scripts/package_skill.py
```

Upload `dist/method-council-skill.zip` from Customize > Skills. The package
contains the method guides needed for a bounded instruction-only fallback.

Managed sessions do not inherit a local `~/.claude/skills` directory. They also
cannot assume that the `method-council` command is installed. When the CLI is
unavailable, the skill must:

- use only the bundled selected method guides;
- keep facts, assumptions, unknowns, and disagreements separate;
- return `INCOMPLETE`;
- state that deterministic validation did not run;
- recommend a local CLI verification as the next step.

## Multi-model use

Do not make an external provider call because an adapter file or executable is
present. The user must authorise the call, the current host must support it, and
the run must record the assigned and observed execution metadata.

Different models can reveal different blind spots. Shared evidence, framing, or
coordination still correlates their results, so model agreement is not
independent proof.
