"""Bounded local document loading helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

MAX_DOCUMENT_BYTES = 5 * 1024 * 1024


class DocumentError(ValueError):
    """Raised when a local structured document cannot be loaded safely."""


def load_document(path: Path) -> Any:
    """Load JSON or YAML from ``path`` without executing custom YAML objects."""

    try:
        size = path.stat().st_size
        if size > MAX_DOCUMENT_BYTES:
            raise DocumentError(
                f"structured document exceeds {MAX_DOCUMENT_BYTES} byte limit: {path}"
            )
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise DocumentError(f"could not read {path}: {exc}") from exc

    try:
        if path.suffix.lower() == ".json":
            return json.loads(text)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise DocumentError(f"could not parse {path}: {exc}") from exc

    raise DocumentError(f"unsupported structured document extension: {path.suffix}")


def repository_root(start: Path) -> Path:
    """Find the closest parent containing a complete Method Council catalogue."""

    candidate = start.resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if all(
            (
                (directory / "schemas" / "method.schema.json").is_file(),
                (directory / "methods").is_dir(),
                (directory / "profiles").is_dir(),
            )
        ):
            return directory
    raise DocumentError(f"could not locate repository root from {start}")


def packaged_catalog_root() -> Path:
    """Return the catalogue bundled in an installed Method Council package."""

    root = Path(__file__).resolve().parent / "_catalog"
    if all(
        (
            (root / "schemas" / "method.schema.json").is_file(),
            (root / "methods").is_dir(),
            (root / "profiles").is_dir(),
        )
    ):
        return root
    raise DocumentError("installed Method Council package has no bundled catalogue")


def catalog_root(start: Path | None = None) -> Path:
    """Prefer a nearby source checkout, then use the installed catalogue."""

    try:
        return repository_root(start or Path.cwd())
    except DocumentError:
        return packaged_catalog_root()


def workspace_root(start: Path | None = None) -> Path:
    """Find the current Git worktree root, or use the starting directory."""

    candidate = (start or Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / ".git").exists():
            return directory
    return candidate
