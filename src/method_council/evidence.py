"""Content digests and run-evidence binding checks."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from method_council.issues import Issue


def content_digest(content: bytes | str) -> str:
    data = content.encode("utf-8") if isinstance(content, str) else content
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def canonical_json_digest(value: Any) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return content_digest(encoded)


def verify_file_digest(path: Path, expected: str) -> bool:
    try:
        observed = file_digest(path)
    except OSError:
        return False
    return observed == expected


def validate_result_evidence(result: Mapping[str, Any], run: Mapping[str, Any]) -> list[Issue]:
    """Check that a method result refers only to evidence bound in its run."""

    issues: list[Issue] = []
    if result.get("run_id") != run.get("run_id"):
        issues.append(
            Issue(
                "evidence.run-mismatch",
                "method result run_id does not match run manifest",
                "/run_id",
            )
        )

    method_id = result.get("method_id")
    if method_id not in run.get("methods", []):
        issues.append(
            Issue(
                "evidence.method-unbound", "method result is not selected by the run", "/method_id"
            )
        )

    evidence_entries = run.get("evidence", [])
    evidence_ids = [entry.get("id") for entry in evidence_entries if isinstance(entry, Mapping)]
    duplicate_ids = sorted(
        {identifier for identifier in evidence_ids if evidence_ids.count(identifier) > 1}
    )
    for identifier in duplicate_ids:
        issues.append(
            Issue(
                "evidence.duplicate-id",
                f"run evidence id {identifier!r} is duplicated",
                "/evidence",
            )
        )
    known_ids = set(evidence_ids)

    for index, finding in enumerate(result.get("findings", [])):
        if not isinstance(finding, Mapping):
            continue
        finding_type = finding.get("type")
        references = list(finding.get("evidence_refs", []))
        counterreferences = list(finding.get("counterevidence_refs", []))
        if finding_type in {"fact", "inference"} and not references:
            issues.append(
                Issue(
                    "evidence.required",
                    f"{finding_type} findings require at least one bound evidence reference",
                    f"/findings/{index}/evidence_refs",
                )
            )
        for field, values in (
            ("evidence_refs", references),
            ("counterevidence_refs", counterreferences),
        ):
            for reference in values:
                if reference not in known_ids:
                    issues.append(
                        Issue(
                            "evidence.reference-unbound",
                            f"evidence reference {reference!r} is not bound in the run manifest",
                            f"/findings/{index}/{field}",
                        )
                    )
    return issues
