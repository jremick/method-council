#!/usr/bin/env python3
"""Install the Method Council CLI and skill for supported local AI tools."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class InstallError(RuntimeError):
    """Raised when an installation step cannot complete safely."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _replace_directory(source: Path, target: Path, *, force: bool) -> None:
    if target.exists() or target.is_symlink():
        if not force:
            raise InstallError(f"skill already exists; rerun with --force to replace it: {target}")
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="method-council-install-", dir=target.parent) as temp:
        staged = Path(temp) / target.name
        shutil.copytree(source, staged)
        staged.replace(target)


def _install_cli(root: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        raise InstallError("uv is required; install it from https://docs.astral.sh/uv/")
    result = subprocess.run(
        [uv, "tool", "install", "--force", str(root)],
        check=False,
        text=True,
    )
    if result.returncode:
        raise InstallError("uv could not install the method-council command")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install Method Council for Codex, Claude Code, or both."
    )
    parser.add_argument("--codex", action="store_true", help="install the user Codex skill")
    parser.add_argument(
        "--claude-code", action="store_true", help="install the personal Claude Code skill"
    )
    parser.add_argument("--no-cli", action="store_true", help="do not install the CLI")
    parser.add_argument("--force", action="store_true", help="replace an existing skill copy")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _repo_root()
    source = root / "skill" / "method-council"
    targets: list[tuple[str, Path]] = []
    selected = args.codex or args.claude_code
    if args.codex or not selected:
        targets.append(("Codex", Path.home() / ".agents" / "skills" / "method-council"))
    if args.claude_code or not selected:
        targets.append(("Claude Code", Path.home() / ".claude" / "skills" / "method-council"))

    try:
        if not args.no_cli:
            _install_cli(root)
        for label, target in targets:
            _replace_directory(source, target, force=args.force)
            print(f"Installed {label} skill: {target}")
    except (InstallError, OSError) as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1

    if not args.no_cli:
        print("Installed CLI: method-council")
    return 0


if __name__ == "__main__":
    sys.exit(main())
