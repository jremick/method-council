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
    """Find the closest parent containing the canonical ``schemas`` directory."""

    candidate = start.resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        if (directory / "schemas").is_dir():
            return directory
    raise DocumentError(f"could not locate repository root from {start}")
