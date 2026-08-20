"""Deterministic semantic checks for claimed method-result passes."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from method_council.evidence import validate_result_evidence
from method_council.issues import Issue


def expected_execution_for_method(run: Mapping[str, Any], method_id: str) -> Mapping[str, Any]:
    """Return the execution metadata assigned to one selected method."""

    plan = run.get("execution_plan")
    if isinstance(plan, Mapping):
        for assignment in plan.get("assignments", []):
            if isinstance(assignment, Mapping) and method_id in assignment.get("methods", []):
                execution = assignment.get("execution")
                if isinstance(execution, Mapping):
                    return execution
    host = run.get("host")
    return host if isinstance(host, Mapping) else {}


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
    if result.get("execution", {}).get("provider_state") != "verified":
        issues.append(
            Issue(
                "result.pass-provider-unverified",
                "PASS requires verified provider execution state",
                "/execution/provider_state",
            )
        )
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
        if (
            finding.get("type") == "assumption"
            and not method["evidence_rules"]["allow_unreferenced_assumptions"]
            and not finding.get("evidence_refs")
            and not finding.get("counterevidence_refs")
        ):
            issues.append(
                Issue(
                    "result.pass-assumption-evidence-required",
                    "method policy does not permit reference-free assumptions in a PASS result",
                    f"/findings/{index}/evidence_refs",
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


def validate_result_against_run(
    result: Mapping[str, Any],
    run: Mapping[str, Any],
    method: Mapping[str, Any] | None,
) -> tuple[list[Issue], list[Issue]]:
    """Validate one schema-checked result against its run and method record.

    The second return value isolates unsupported claimed-PASS issues so callers
    can derive an effective ``INCOMPLETE`` status without hiding other contract
    failures.
    """

    issues = validate_result_evidence(result, run)
    pass_issues: list[Issue] = []
    if method is None:
        issues.append(
            Issue(
                "run.method-unknown",
                f"result references unknown catalog method {result.get('method_id')!r}",
                "/method_id",
            )
        )
        return issues, pass_issues

    if result.get("method_version") != method.get("version"):
        issues.append(
            Issue(
                "run.method-version",
                "result method version does not match catalog",
                "/method_version",
            )
        )
    if result.get("rigor") != run.get("rigor"):
        issues.append(
            Issue(
                "run.rigor-mismatch",
                "result rigor does not match run",
                "/rigor",
            )
        )
    expected_execution = expected_execution_for_method(run, str(result.get("method_id", "")))
    if result.get("execution") != expected_execution:
        issues.append(
            Issue(
                "run.execution-mismatch",
                "result execution metadata does not match its run assignment",
                "/execution",
            )
        )

    rigor = run.get("rigor")
    if isinstance(rigor, str) and rigor in method.get("rigor", {}):
        pass_issues = validate_pass_semantics(result, method, rigor)
        issues.extend(pass_issues)

    correlation_group = result.get("execution", {}).get("correlation_group")
    expected_groups = [
        expected_execution_for_method(run, str(method_id)).get("correlation_group")
        for method_id in run.get("methods", [])
    ]
    if (
        correlation_group is not None
        and expected_groups.count(correlation_group) > 1
        and "CORRELATED" not in result.get("side_conditions", [])
    ):
        issues.append(
            Issue(
                "run.correlation-missing",
                "shared correlation group requires CORRELATED",
                "/side_conditions",
            )
        )
    if correlation_group is None and "CORRELATED" in result.get("side_conditions", []):
        issues.append(
            Issue(
                "run.correlation-unbound",
                "CORRELATED requires a non-null correlation group",
                "/side_conditions",
            )
        )
    if (
        "execution_plan" not in run
        and len(run.get("methods", [])) > 1
        and run.get("host", {}).get("adapter") == "codex"
        and run.get("host", {}).get("correlation_group") is None
    ):
        issues.append(
            Issue(
                "run.correlation-group-missing",
                "multi-method Codex run requires a correlation group",
                "/host/correlation_group",
            )
        )
    return issues, pass_issues
