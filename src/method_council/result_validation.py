"""Deterministic semantic checks for claimed method-result passes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from method_council.issues import Issue


def _has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (Mapping, list, tuple, set)):
        return bool(value)
    return True


def validate_pass_semantics(
    result: Mapping[str, Any], method: Mapping[str, Any], rigor: str
) -> list[Issue]:
    """Return reasons a claimed ``PASS`` is not canonically supportable.

    These checks deliberately assess contract completion, not the truth or
    quality of model-authored prose. Non-PASS results remain honest primary
    statuses and are not upgraded by this function.
    """

    if result.get("status") != "PASS":
        return []

    issues: list[Issue] = []
    variant = method["rigor"][rigor]
    selected_steps = list(variant["steps"])
    selected_set = set(selected_steps)
    procedure = {step["id"]: step for step in method["procedure"]}
    known_steps = set(procedure)
    completed_steps = {str(step) for step in result.get("completed_steps", [])}

    for step_id in sorted(completed_steps - known_steps):
        issues.append(
            Issue(
                "result.pass-completed-step-unknown",
                f"completed step {step_id!r} is not defined by the method",
                "/completed_steps",
            )
        )
    for step_id in sorted(selected_set - completed_steps):
        issues.append(
            Issue(
                "result.pass-step-missing",
                f"selected rigor step {step_id!r} is not completed",
                "/completed_steps",
            )
        )

    findings = list(result.get("findings", []))
    if not findings:
        issues.append(
            Issue(
                "result.pass-findings-empty",
                "PASS requires at least one finding",
                "/findings",
            )
        )
    for index, finding in enumerate(findings):
        step_id = str(finding.get("method_step", ""))
        if step_id not in known_steps:
            issues.append(
                Issue(
                    "result.pass-finding-step-unknown",
                    f"finding references unknown method step {step_id!r}",
                    f"/findings/{index}/method_step",
                )
            )
        elif step_id not in completed_steps:
            issues.append(
                Issue(
                    "result.pass-finding-step-incomplete",
                    f"finding references uncompleted method step {step_id!r}",
                    f"/findings/{index}/method_step",
                )
            )

    distinct_evidence = {
        str(reference)
        for finding in findings
        for field in ("evidence_refs", "counterevidence_refs")
        for reference in finding.get(field, [])
    }
    minimum_references = int(variant["minimum_evidence_refs"])
    if len(distinct_evidence) < minimum_references:
        issues.append(
            Issue(
                "result.pass-evidence-minimum",
                "PASS requires at least "
                f"{minimum_references} distinct evidence references for {rigor} rigor; "
                f"got {len(distinct_evidence)}",
                "/findings",
            )
        )

    artifact = result.get("method_artifact")
    artifact = artifact if isinstance(artifact, Mapping) else {}
    required_fields = {
        field
        for step_id in selected_steps
        for field in procedure[step_id].get("artifact_fields", [])
    }
    for field in sorted(required_fields):
        if field not in artifact or not _has_content(artifact[field]):
            issues.append(
                Issue(
                    "result.pass-artifact-field-missing",
                    f"selected rigor steps require nonempty method_artifact field {field!r}",
                    f"/method_artifact/{field}",
                )
            )

    if result.get("errors"):
        issues.append(
            Issue(
                "result.pass-errors-present",
                "PASS cannot contain execution errors",
                "/errors",
            )
        )
    if "SKIPPED" in result.get("side_conditions", []):
        issues.append(
            Issue(
                "result.pass-skipped",
                "PASS cannot carry the SKIPPED side condition",
                "/side_conditions",
            )
        )

    return issues
