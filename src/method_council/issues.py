"""Small, serialisable validation issue types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Issue:
    """A deterministic validation failure with a stable machine-readable code."""

    code: str
    message: str
    path: str = "$"

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message, "path": self.path}


def issue_dicts(issues: list[Issue]) -> list[dict[str, Any]]:
    return [issue.as_dict() for issue in issues]
