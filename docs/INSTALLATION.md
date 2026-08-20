# Installation

Method Council uses the
[Agent Skills structure](https://learn.chatgpt.com/docs/build-skills) supported
by Codex and the
[skills structure documented for Claude Code](https://code.claude.com/docs/en/skills).
It has two parts:

1. The `method-council` command validates routes, run files, evidence links,
   statuses, and reports.
2. The skill tells an AI tool how to select and apply the methods.

Install both parts when the host supports local commands. A skill without the
CLI can still provide a limited instruction-only analysis, but it cannot produce
a deterministically verified run.

## Install for Codex and Claude Code

Requirements: Git and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/jremick/method-council.git
cd method-council
python3 scripts/install.py
method-council validate
```

This installs:

- the CLI as a user-level `uv` tool;
- the Codex skill at `~/.agents/skills/method-council`;
- the Claude Code skill at `~/.claude/skills/method-council`.

Install one skill only:

```bash
python3 scripts/install.py --codex
python3 scripts/install.py --claude-code
```

To replace an existing skill copy during an upgrade:

```bash
git pull --ff-only
python3 scripts/install.py --force
method-council validate
```

The installed CLI contains the canonical catalogue and schemas. Run it from the
project that contains your question and evidence. It writes `runs/` inside that
project rather than inside the Method Council installation.

## Use only in one project

A clone already contains project skills for both tools:

- `.agents/skills/method-council` for Codex;
- `.claude/skills/method-council` for Claude Code.

Install only the CLI, then open the clone in the chosen tool:

```bash
uv tool install --force .
method-council validate
```

If you do not want a personal skill, copy the applicable project skill
directory into your own repository instead.

## Claude and Cowork account skill

Build a deterministic upload ZIP:

```bash
python3 scripts/package_skill.py
```

Upload `dist/method-council-skill.zip` from Customize > Skills, following
[Anthropic's custom-skill upload flow](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
The ZIP contains the skill and a read-only copy of the method catalogue. It does
not contain the deterministic CLI or credentials.

If the managed environment can run the installed CLI, use the normal workflow.
Otherwise the skill uses instruction-only mode and must report `INCOMPLETE`. It
must not claim that route validation, evidence binding, aggregation, or report
verification ran.

## Other Agent Skills hosts

The skill uses the open Agent Skills folder structure. A compatible host can
import `skill/method-council`. Install the CLI separately and confirm
`method-council validate` before relying on deterministic checks.

Host discovery, command execution, subagent isolation, provider authentication,
and model observation vary. A successful skill import does not prove full host
compatibility.

## Uninstall

```bash
uv tool uninstall method-council
rm -rf ~/.agents/skills/method-council
rm -rf ~/.claude/skills/method-council
```

Review the paths before removal if you have edited either skill locally.
