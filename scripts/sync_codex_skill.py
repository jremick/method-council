#!/usr/bin/env python3
"""Synchronize the canonical skill into Codex and Claude Code project scopes."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Final, NamedTuple

GENERATOR_ID: Final = "method-council-agent-skill-sync"
GENERATOR_VERSION: Final = "0.2.0"
SOURCE_RELATIVE: Final = Path("skill/method-council")
METADATA_NAME: Final = ".projection.json"


class ProjectionTarget(NamedTuple):
    path: Path
    kind: str


TARGETS: Final = (
    ProjectionTarget(Path(".agents/skills/method-council"), "codex-skill-projection"),
    ProjectionTarget(Path(".claude/skills/method-council"), "claude-code-skill-projection"),
)
TARGET_RELATIVE: Final = TARGETS[0].path


class ProjectionError(RuntimeError):
    """Raised when the generated projection is unsafe or out of date."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _canonical_files(source: Path) -> dict[str, bytes]:
    if not source.is_dir() or source.is_symlink():
        raise ProjectionError(f"canonical skill source is not a directory: {SOURCE_RELATIVE}")

    files: dict[str, bytes] = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ProjectionError(
                f"canonical skill source contains a symbolic link: {path.relative_to(source)}"
            )
        if path.is_file():
            files[path.relative_to(source).as_posix()] = path.read_bytes()
    if "SKILL.md" not in files:
        raise ProjectionError("canonical skill source has no SKILL.md")
    return files


def _canonical_digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, content in sorted(files.items()):
        relative_bytes = relative.encode("utf-8")
        digest.update(len(relative_bytes).to_bytes(8, "big"))
        digest.update(relative_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def _metadata(files: dict[str, bytes], target: ProjectionTarget) -> bytes:
    document = {
        "schema_version": "0.1.0",
        "kind": target.kind,
        "source": SOURCE_RELATIVE.as_posix(),
        "target": target.path.as_posix(),
        "canonical_input_digest": _canonical_digest(files),
        "generator_id": GENERATOR_ID,
        "generator_version": GENERATOR_VERSION,
        "generated_files": sorted(files),
    }
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def expected_projection(root: Path, target: ProjectionTarget = TARGETS[0]) -> dict[str, bytes]:
    """Return the complete, content-bound projection for ``root``."""

    source = root / SOURCE_RELATIVE
    files = _canonical_files(source)
    return {**files, METADATA_NAME: _metadata(files, target)}


def _target_files(target: Path, target_relative: Path = TARGET_RELATIVE) -> dict[str, bytes]:
    if target.is_symlink():
        raise ProjectionError(f"projection target must not be a symbolic link: {target_relative}")
    if not target.exists():
        return {}
    if not target.is_dir():
        raise ProjectionError(f"projection target is not a directory: {target_relative}")

    files: dict[str, bytes] = {}
    for path in sorted(target.rglob("*")):
        if path.is_symlink():
            raise ProjectionError(
                f"projection contains a symbolic link: {path.relative_to(target)}"
            )
        if path.is_file():
            files[path.relative_to(target).as_posix()] = path.read_bytes()
    return files


def projection_issues(root: Path, target: ProjectionTarget = TARGETS[0]) -> list[str]:
    expected = expected_projection(root, target)
    actual = _target_files(root / target.path, target.path)
    issues: list[str] = []

    missing = sorted(set(expected) - set(actual))
    stale = sorted(set(actual) - set(expected))
    changed = sorted(path for path in set(expected) & set(actual) if expected[path] != actual[path])
    issues.extend(f"missing:{path}" for path in missing)
    issues.extend(f"stale:{path}" for path in stale)
    issues.extend(f"changed:{path}" for path in changed)
    return issues


def sync_projection(root: Path, projection: ProjectionTarget = TARGETS[0]) -> None:
    expected = expected_projection(root, projection)
    target = root / projection.path
    actual = _target_files(target, projection.path)
    target.mkdir(parents=True, exist_ok=True)

    for relative in sorted(set(actual) - set(expected), reverse=True):
        path = target / relative
        path.unlink()

    for directory in sorted(
        (path for path in target.rglob("*") if path.is_dir()),
        key=lambda path: len(path.parts),
        reverse=True,
    ):
        if not any(directory.iterdir()):
            directory.rmdir()

    for relative, content in sorted(expected.items()):
        path = target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() == content:
            continue
        temporary = path.with_name(f".{path.name}.tmp")
        temporary.write_bytes(content)
        temporary.replace(path)


def _all_issues(root: Path) -> list[str]:
    return [
        f"{target.path}:{issue}" for target in TARGETS for issue in projection_issues(root, target)
    ]


def sync_projections(root: Path) -> None:
    for target in TARGETS:
        sync_projection(root, target)


def _emit(mode: str, valid: bool, issues: list[str], root: Path) -> None:
    expected = expected_projection(root, TARGETS[0])
    metadata = json.loads(expected[METADATA_NAME])
    print(
        json.dumps(
            {
                "mode": mode,
                "valid": valid,
                "source": SOURCE_RELATIVE.as_posix(),
                "targets": [target.path.as_posix() for target in TARGETS],
                "canonical_input_digest": metadata["canonical_input_digest"],
                "generator_id": GENERATOR_ID,
                "generator_version": GENERATOR_VERSION,
                "issues": issues,
            },
            indent=2,
            sort_keys=True,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Synchronize or check repo-local Codex and Claude Code skill projections."
    )
    parser.add_argument("mode", choices=("sync", "check"))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = _repo_root()
    try:
        if args.mode == "sync":
            sync_projections(root)
        issues = _all_issues(root)
    except (OSError, ProjectionError, ValueError) as exc:
        print(json.dumps({"mode": args.mode, "valid": False, "error": str(exc)}, sort_keys=True))
        return 2

    _emit(args.mode, not issues, issues, root)
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
