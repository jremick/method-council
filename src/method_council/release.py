"""Fail-closed, content-bound public-alpha release verification."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from method_council.documents import DocumentError, load_document
from method_council.evidence import file_digest
from method_council.issues import Issue
from method_council.schema import SchemaRegistry
from method_council.status import PRIMARY_STATUSES, aggregate_status


def _resolve_local(root: Path, relative: object, *, field: str) -> tuple[Path | None, Issue | None]:
    if not isinstance(relative, str) or not relative:
        return None, Issue(
            "release.path-invalid", f"{field} must be a non-empty relative path", field
        )
    candidate = Path(relative)
    if candidate.is_absolute():
        return None, Issue("release.path-absolute", f"{field} must be relative", field)
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
    if not path.is_file():
        return [
            Issue("release.evidence-missing", f"bound evidence does not exist: {path}", check_path)
        ]
    expected = binding.get("digest")
    if not isinstance(expected, str) or not expected.startswith("sha256:"):
        return [Issue("release.evidence-digest-invalid", "invalid evidence digest", check_path)]
    observed = file_digest(path)
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
        manifest = load_document(manifest_path)
    except DocumentError as exc:
        return {
            "valid": False,
            "release_eligible": False,
            "status": "ERROR",
            "gate_statuses": {},
            "issues": [Issue("release.manifest-parse", str(exc), str(manifest_path)).as_dict()],
        }
    issues.extend(registry.validate(manifest, "release-manifest"))
    if issues or not isinstance(manifest, Mapping):
        return {
            "valid": False,
            "release_eligible": False,
            "status": "ERROR",
            "gate_statuses": {},
            "issues": [issue.as_dict() for issue in issues],
        }

    artifact_ids: list[str] = []
    artifact_paths: list[str] = []
    gate_artifact_statuses: dict[str, list[str]] = {}
    for index, artifact in enumerate(manifest["artifacts"]):
        artifact_ids.append(artifact["id"])
        artifact_paths.append(artifact["path"])
        gate = artifact["gate"]
        gate_artifact_statuses.setdefault(gate, [])
        path, path_issue = _resolve_local(root, artifact["path"], field=f"/artifacts/{index}/path")
        if path_issue:
            issues.append(path_issue)
            gate_artifact_statuses[gate].append("ERROR")
            continue
        assert path is not None
        if not path.is_file():
            issues.append(
                Issue(
                    "release.artifact-missing",
                    f"release artifact does not exist: {path}",
                    f"/artifacts/{index}",
                )
            )
            gate_artifact_statuses[gate].append("INCOMPLETE")
            continue
        observed_digest = file_digest(path)
        if observed_digest != artifact["digest"]:
            issues.append(
                Issue(
                    "release.artifact-digest-mismatch",
                    f"artifact digest mismatch for {artifact['path']}",
                    f"/artifacts/{index}/digest",
                )
            )
            gate_artifact_statuses[gate].append("FAIL")
            continue
        try:
            report = load_document(path)
        except DocumentError as exc:
            issues.append(Issue("release.gate-report-parse", str(exc), f"/artifacts/{index}/path"))
            gate_artifact_statuses[gate].append("ERROR")
            continue
        status, report_issues = _verify_gate_report(
            report, expected_gate=gate, root=root, report_path=path
        )
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
    for gate in manifest["required_gates"]:
        statuses = gate_artifact_statuses.get(gate, [])
        if not statuses:
            gate_statuses[gate] = "INCOMPLETE"
            issues.append(
                Issue(
                    "release.gate-missing",
                    f"required gate {gate!r} has no artifact",
                    "/required_gates",
                )
            )
        else:
            gate_statuses[gate] = aggregate_status(statuses)

    overall_status = aggregate_status(gate_statuses.values())
    eligible = not issues and overall_status == "PASS"
    claimed = manifest.get("claimed_release_eligible")
    return {
        "valid": not issues,
        "release_eligible": eligible,
        "status": overall_status,
        "gate_statuses": gate_statuses,
        "claimed_release_eligible": claimed,
        "claim_matches_derived": claimed is None or claimed == eligible,
        "issues": [issue.as_dict() for issue in issues],
    }
