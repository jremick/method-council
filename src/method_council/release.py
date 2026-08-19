"""Fail-closed, content-bound public-alpha release verification."""

from __future__ import annotations

import json
import os
import stat
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from method_council.documents import MAX_DOCUMENT_BYTES, DocumentError
from method_council.evidence import content_digest
from method_council.issues import Issue
from method_council.release_checks import verify_registered_gate
from method_council.schema import SchemaRegistry
from method_council.status import PRIMARY_STATUSES, aggregate_status


def _read_regular_file(path: Path) -> bytes:
    """Read a bounded regular file without following a final symlink or device."""

    lexical = path if path.is_absolute() else Path.cwd() / path
    cursor = Path(lexical.anchor)
    for part in lexical.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise DocumentError(f"release input is a symlink: {path}")

    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise DocumentError(f"could not read {path}: {exc}") from exc

    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise DocumentError(f"release input is not a regular file: {path}")
        if metadata.st_size > MAX_DOCUMENT_BYTES:
            raise DocumentError(f"release input exceeds {MAX_DOCUMENT_BYTES} byte limit: {path}")
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            data = handle.read(MAX_DOCUMENT_BYTES + 1)
    except OSError as exc:
        raise DocumentError(f"could not read {path}: {exc}") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)

    if len(data) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"release input exceeds {MAX_DOCUMENT_BYTES} byte limit: {path}")
    return data


def _load_regular_document(path: Path, data: bytes | None = None) -> Any:
    raw = data if data is not None else _read_regular_file(path)
    try:
        text = raw.decode("utf-8")
        if path.suffix.lower() == ".json":
            return json.loads(text)
        if path.suffix.lower() in {".yaml", ".yml"}:
            return yaml.safe_load(text)
    except (UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise DocumentError(f"could not parse {path}: {exc}") from exc
    raise DocumentError(f"unsupported structured document extension: {path.suffix}")


def _resolve_local(root: Path, relative: object, *, field: str) -> tuple[Path | None, Issue | None]:
    if not isinstance(relative, str) or not relative:
        return None, Issue(
            "release.path-invalid", f"{field} must be a non-empty relative path", field
        )
    candidate = Path(relative)
    if candidate.is_absolute():
        return None, Issue("release.path-absolute", f"{field} must be relative", field)
    cursor = root
    for part in candidate.parts:
        cursor /= part
        if cursor.is_symlink():
            return None, Issue(
                "release.path-symlink",
                f"{field} must not contain symlinks",
                field,
            )
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None, Issue("release.path-escapes-root", f"{field} escapes the release root", field)
    return resolved, None


def _verify_binding(
    binding: object, *, root: Path, report_path: Path, check_path: str
) -> list[Issue]:
    if not isinstance(binding, Mapping):
        return [Issue("release.evidence-invalid", "evidence binding must be an object", check_path)]
    if set(binding) != {"path", "digest"}:
        return [
            Issue(
                "release.evidence-invalid",
                "evidence binding must contain exactly path and digest",
                check_path,
            )
        ]
    path, path_issue = _resolve_local(root, binding.get("path"), field=f"{check_path}/path")
    if path_issue:
        return [path_issue]
    assert path is not None
    if path == report_path:
        return [
            Issue("release.evidence-self-reference", "gate report cannot bind itself", check_path)
        ]
    if not path.exists():
        return [
            Issue("release.evidence-missing", f"bound evidence does not exist: {path}", check_path)
        ]
    expected = binding.get("digest")
    if not isinstance(expected, str) or not expected.startswith("sha256:"):
        return [Issue("release.evidence-digest-invalid", "invalid evidence digest", check_path)]
    try:
        observed = content_digest(_read_regular_file(path))
    except DocumentError as exc:
        return [Issue("release.evidence-read", str(exc), check_path)]
    if observed != expected:
        return [
            Issue(
                "release.evidence-digest-mismatch",
                f"bound evidence digest mismatch for {binding['path']}",
                check_path,
            )
        ]
    return []


def _verify_gate_report(
    document: object, *, expected_gate: str, root: Path, report_path: Path
) -> tuple[str, list[Issue]]:
    """Derive a gate status from content-bound checks, never a claimed top-level flag."""

    issues: list[Issue] = []
    if not isinstance(document, Mapping):
        return "ERROR", [Issue("release.gate-report-invalid", "gate report must be an object")]
    if document.get("schema_version") != "0.1.0":
        issues.append(
            Issue("release.gate-report-version", "gate report schema_version must be 0.1.0")
        )
    if document.get("gate") != expected_gate:
        issues.append(
            Issue(
                "release.gate-report-mismatch",
                f"gate report names {document.get('gate')!r}; expected {expected_gate!r}",
            )
        )
    checks = document.get("checks")
    if not isinstance(checks, list) or not checks:
        issues.append(
            Issue(
                "release.gate-checks-missing",
                "a top-level PASS is insufficient; gate report requires content-bound checks",
                "/checks",
            )
        )
        return "INCOMPLETE", issues

    check_ids: list[str] = []
    check_statuses: list[str] = []
    for index, check in enumerate(checks):
        path = f"/checks/{index}"
        if not isinstance(check, Mapping):
            issues.append(Issue("release.gate-check-invalid", "check must be an object", path))
            check_statuses.append("ERROR")
            continue
        identifier = check.get("id")
        if not isinstance(identifier, str) or not identifier:
            issues.append(
                Issue("release.gate-check-id", "check id must be non-empty", f"{path}/id")
            )
        else:
            check_ids.append(identifier)
        status = check.get("status")
        if status not in PRIMARY_STATUSES:
            issues.append(
                Issue(
                    "release.gate-check-status",
                    "check has an invalid primary status",
                    f"{path}/status",
                )
            )
            check_statuses.append("ERROR")
        else:
            check_statuses.append(str(status))
        bindings = check.get("evidence")
        if not isinstance(bindings, list) or not bindings:
            issues.append(
                Issue(
                    "release.gate-check-unbound",
                    "every gate check requires at least one content-bound evidence file",
                    f"{path}/evidence",
                )
            )
            check_statuses[-1] = aggregate_status((check_statuses[-1], "INCOMPLETE"))
            continue
        binding_issues: list[Issue] = []
        for binding_index, binding in enumerate(bindings):
            binding_issues.extend(
                _verify_binding(
                    binding,
                    root=root,
                    report_path=report_path,
                    check_path=f"{path}/evidence/{binding_index}",
                )
            )
        if binding_issues:
            issues.extend(binding_issues)
            check_statuses[-1] = aggregate_status((check_statuses[-1], "ERROR"))

    duplicate_ids = sorted(
        {identifier for identifier in check_ids if check_ids.count(identifier) > 1}
    )
    for identifier in duplicate_ids:
        issues.append(
            Issue(
                "release.gate-check-duplicate", f"duplicate gate check id {identifier!r}", "/checks"
            )
        )

    derived = aggregate_status(check_statuses)
    claimed = document.get("status")
    if claimed not in PRIMARY_STATUSES:
        issues.append(
            Issue("release.gate-claim-invalid", "gate report status claim is invalid", "/status")
        )
    elif claimed != derived:
        issues.append(
            Issue(
                "release.gate-claim-mismatch",
                f"claimed gate status {claimed} does not match derived status {derived}",
                "/status",
            )
        )
    return derived, issues


def verify_release_manifest(
    manifest_path: Path, *, root: Path, registry: SchemaRegistry | None = None
) -> dict[str, Any]:
    """Re-read every byte and derive eligibility from bound gate checks."""

    root = root.resolve()
    registry = registry or SchemaRegistry(root / "schemas")
    issues: list[Issue] = []
    try:
        manifest = _load_regular_document(manifest_path)
    except DocumentError as exc:
        return {
            "valid": False,
            "release_eligible": False,
            "status": "ERROR",
            "gate_statuses": {},
            "content_valid": False,
            "content_status": "ERROR",
            "content_gate_statuses": {},
            "issues": [Issue("release.manifest-parse", str(exc), str(manifest_path)).as_dict()],
        }
    issues.extend(registry.validate(manifest, "release-manifest"))
    if issues or not isinstance(manifest, Mapping):
        return {
            "valid": False,
            "release_eligible": False,
            "status": "ERROR",
            "gate_statuses": {},
            "content_valid": False,
            "content_status": "ERROR",
            "content_gate_statuses": {},
            "issues": [issue.as_dict() for issue in issues],
        }

    artifact_ids: list[str] = []
    artifact_paths: list[str] = []
    gate_artifact_statuses: dict[str, list[str]] = {}
    gate_artifact_content_statuses: dict[str, list[str]] = {}
    for index, artifact in enumerate(manifest["artifacts"]):
        artifact_ids.append(artifact["id"])
        artifact_paths.append(artifact["path"])
        gate = artifact["gate"]
        gate_artifact_statuses.setdefault(gate, [])
        gate_artifact_content_statuses.setdefault(gate, [])
        path, path_issue = _resolve_local(root, artifact["path"], field=f"/artifacts/{index}/path")
        if path_issue:
            issues.append(path_issue)
            gate_artifact_statuses[gate].append("ERROR")
            gate_artifact_content_statuses[gate].append("ERROR")
            continue
        assert path is not None
        if not path.exists():
            issues.append(
                Issue(
                    "release.artifact-missing",
                    f"release artifact does not exist: {path}",
                    f"/artifacts/{index}",
                )
            )
            gate_artifact_statuses[gate].append("INCOMPLETE")
            gate_artifact_content_statuses[gate].append("INCOMPLETE")
            continue
        try:
            report_bytes = _read_regular_file(path)
        except DocumentError as exc:
            issues.append(Issue("release.artifact-read", str(exc), f"/artifacts/{index}/path"))
            gate_artifact_statuses[gate].append("ERROR")
            gate_artifact_content_statuses[gate].append("ERROR")
            continue
        observed_digest = content_digest(report_bytes)
        if observed_digest != artifact["digest"]:
            issues.append(
                Issue(
                    "release.artifact-digest-mismatch",
                    f"artifact digest mismatch for {artifact['path']}",
                    f"/artifacts/{index}/digest",
                )
            )
            gate_artifact_statuses[gate].append("FAIL")
            gate_artifact_content_statuses[gate].append("FAIL")
            continue
        try:
            report = _load_regular_document(path, report_bytes)
        except DocumentError as exc:
            issues.append(Issue("release.gate-report-parse", str(exc), f"/artifacts/{index}/path"))
            gate_artifact_statuses[gate].append("ERROR")
            gate_artifact_content_statuses[gate].append("ERROR")
            continue
        status, report_issues = _verify_gate_report(
            report, expected_gate=gate, root=root, report_path=path
        )
        gate_artifact_content_statuses[gate].append(status)
        if status == "PASS":
            registered_status, registered_issues = verify_registered_gate(
                report,
                expected_gate=gate,
                root=root,
                read_document=_load_regular_document,
            )
            if registered_status is None:
                gate_artifact_statuses[gate].append("INCOMPLETE")
                issues.append(
                    Issue(
                        "release.gate-unattested",
                        (
                            f"gate {gate!r} is content-consistent but no registered deterministic "
                            "verifier attests its producer, candidate commit, "
                            "and raw evidence format"
                        ),
                        f"/artifacts/{index}",
                    )
                )
            else:
                gate_artifact_statuses[gate].append(registered_status)
                issues.extend(
                    Issue(issue.code, issue.message, f"{artifact['path']}:{issue.path}")
                    for issue in registered_issues
                )
        else:
            gate_artifact_statuses[gate].append(status)
        issues.extend(
            Issue(issue.code, issue.message, f"{artifact['path']}:{issue.path}")
            for issue in report_issues
        )

    for field, values in (("id", artifact_ids), ("path", artifact_paths)):
        duplicates = sorted({value for value in values if values.count(value) > 1})
        for value in duplicates:
            issues.append(
                Issue(
                    f"release.duplicate-artifact-{field}",
                    f"duplicate artifact {field} {value!r}",
                    "/artifacts",
                )
            )

    gate_statuses: dict[str, str] = {}
    content_gate_statuses: dict[str, str] = {}
    for gate in manifest["required_gates"]:
        statuses = gate_artifact_statuses.get(gate, [])
        content_statuses = gate_artifact_content_statuses.get(gate, [])
        if not statuses:
            gate_statuses[gate] = "INCOMPLETE"
            content_gate_statuses[gate] = "INCOMPLETE"
            issues.append(
                Issue(
                    "release.gate-missing",
                    f"required gate {gate!r} has no artifact",
                    "/required_gates",
                )
            )
        else:
            gate_statuses[gate] = aggregate_status(statuses)
            content_gate_statuses[gate] = aggregate_status(content_statuses)

    overall_status = aggregate_status(gate_statuses.values())
    content_status = aggregate_status(content_gate_statuses.values())
    content_issues = [issue for issue in issues if issue.code != "release.gate-unattested"]
    eligible = not issues and overall_status == "PASS"
    claimed = manifest.get("claimed_release_eligible")
    return {
        "valid": not issues,
        "release_eligible": eligible,
        "status": overall_status,
        "gate_statuses": gate_statuses,
        "content_valid": not content_issues,
        "content_status": content_status,
        "content_gate_statuses": content_gate_statuses,
        "claimed_release_eligible": claimed,
        "claim_matches_derived": claimed is None or claimed == eligible,
        "issues": [issue.as_dict() for issue in issues],
    }
