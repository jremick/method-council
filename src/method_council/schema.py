"""JSON Schema loading and validation."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from method_council.issues import Issue

SCHEMA_ALIASES = {
    "method": "method.schema.json",
    "profile": "profile.schema.json",
    "run": "run.schema.json",
    "method-result": "method-result.schema.json",
    "report": "report.schema.json",
    "provider-status": "provider-status.schema.json",
    "release-manifest": "release-manifest.schema.json",
    "run-verdict": "run-verdict.schema.json",
    "host-execution": "host-execution.schema.json",
    "acceptance-verdict": "acceptance-verdict.schema.json",
}

_RFC3339_ZONE = re.compile(r"(?:Z|[+-][0-9]{2}:[0-9]{2})$")


def _format_checker() -> FormatChecker:
    """Provide required checks even when jsonschema format extras are absent."""

    checker = FormatChecker()

    @checker.checks("date-time")
    def is_date_time(value: object) -> bool:
        if (
            not isinstance(value, str)
            or "T" not in value.upper()
            or not _RFC3339_ZONE.search(value)
        ):
            return False
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None

    @checker.checks("uri")
    def is_uri(value: object) -> bool:
        if not isinstance(value, str) or any(character.isspace() for character in value):
            return False
        try:
            parsed = urlsplit(value)
        except ValueError:
            return False
        return bool(parsed.scheme)

    return checker


def _pointer(parts: list[object]) -> str:
    if not parts:
        return "$"
    escaped = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(escaped)


class SchemaRegistry:
    """Load the repository's frozen schemas and validate with format checks."""

    def __init__(self, schema_dir: Path):
        self.schema_dir = schema_dir.resolve()
        self._schemas: dict[str, dict[str, Any]] = {}

    def names(self) -> tuple[str, ...]:
        return tuple(SCHEMA_ALIASES)

    def _filename(self, name: str) -> str:
        if name in SCHEMA_ALIASES:
            return SCHEMA_ALIASES[name]
        if name in SCHEMA_ALIASES.values():
            return name
        raise KeyError(f"unknown schema {name!r}; expected one of {', '.join(self.names())}")

    def load(self, name: str) -> dict[str, Any]:
        filename = self._filename(name)
        if filename not in self._schemas:
            path = self.schema_dir / filename
            with path.open(encoding="utf-8") as handle:
                schema = json.load(handle)
            if not isinstance(schema, dict):
                raise SchemaError(f"schema {path} is not an object")
            Draft202012Validator.check_schema(schema)
            self._schemas[filename] = schema
        return self._schemas[filename]

    def validate(self, instance: Any, name: str) -> list[Issue]:
        schema = self.load(name)
        validator = Draft202012Validator(schema, format_checker=_format_checker())
        errors = sorted(
            validator.iter_errors(instance),
            key=lambda error: (list(error.absolute_path), error.message),
        )
        return [
            Issue(
                code="schema.invalid",
                message=error.message,
                path=_pointer(list(error.absolute_path)),
            )
            for error in errors
        ]

    def validate_registry(self) -> list[Issue]:
        issues: list[Issue] = []
        for name in self.names():
            try:
                self.load(name)
            except (OSError, json.JSONDecodeError, SchemaError) as exc:
                issues.append(
                    Issue(
                        code="schema.definition-invalid",
                        message=f"{name}: {exc}",
                        path=str(self.schema_dir / SCHEMA_ALIASES[name]),
                    )
                )
        return issues
