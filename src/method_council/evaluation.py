"""Deterministic method-suite evaluation over recorded run artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from method_council.catalog import load_catalog
from method_council.evidence import file_digest
from method_council.run import verify_run

RUBRIC_DIMENSIONS = (
    "method_fidelity",
    "evidence_discipline",
    "calibration",
    "actionability",
    "failure_mode_resistance",
)
EVALUATION_REPORT_PATH = Path("evals/methods/screening-report.json")


def _load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected an object: {path}")
    return value


def _repo_path(root: Path, locator: str, *, expect: str) -> Path:
    root = root.resolve()
    path = (root / locator).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{expect} path escapes repository root: {locator}") from exc
    if expect == "file" and (not path.is_file() or path.is_symlink()):
        raise ValueError(f"expected a regular repository file: {locator}")
    if expect == "directory" and (not path.is_dir() or path.is_symlink()):
        raise ValueError(f"expected a repository directory: {locator}")
    return path


def _has_content(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, list, dict)):
        return bool(value)
    return True


def _validate_review(
    review: dict[str, Any], *, method_id: str, threshold: int
) -> tuple[bool, list[str]]:
    issues: list[str] = []
    if review.get("method_id") != method_id:
        issues.append("review method_id does not match the specimen")
    dimensions = review.get("dimensions")
    if not isinstance(dimensions, dict):
        return False, [*issues, "review dimensions are missing"]
    if set(dimensions) != set(RUBRIC_DIMENSIONS):
        issues.append("review dimensions do not exactly match the rubric")
    for name in RUBRIC_DIMENSIONS:
        item = dimensions.get(name)
        if not isinstance(item, dict):
            issues.append(f"{name} review is missing")
            continue
        score = item.get("score")
        rationale = item.get("rationale")
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 4:
            issues.append(f"{name} score must be an integer from 0 to 4")
        if not isinstance(rationale, str) or len(rationale.strip()) < 12:
            issues.append(f"{name} rationale is too short")
    measured_delta = review.get("decision_relevant_delta")
    if measured_delta is not None:
        if not isinstance(measured_delta, dict):
            issues.append("decision_relevant_delta must be null or an object")
        elif measured_delta.get("baseline_artifact") is None:
            issues.append("a measured decision delta requires a baseline artifact")
    scores = [
        dimensions[name]["score"]
        for name in RUBRIC_DIMENSIONS
        if isinstance(dimensions.get(name), dict)
        and isinstance(dimensions[name].get("score"), int)
        and not isinstance(dimensions[name].get("score"), bool)
    ]
    met = not issues and len(scores) == len(RUBRIC_DIMENSIONS) and min(scores) >= threshold
    return met, issues


def evaluate_method_suite(root: Path, inventory_path: Path) -> dict[str, Any]:
    """Evaluate catalog coverage and recorded specimens without upgrading claim authority."""

    root = root.resolve()
    inventory_path = _repo_path(root, inventory_path.as_posix(), expect="file")
    inventory = _load_object(inventory_path)
    review_path = _repo_path(root, inventory["review_file"], expect="file")
    review_document = _load_object(review_path)
    reviews = {review["method_id"]: review for review in review_document.get("reviews", [])}
    catalog = load_catalog(root)
    issues = [issue.as_dict() for issue in catalog.issues]
    specimens = inventory.get("methods", [])
    specimen_ids = [item.get("method_id") for item in specimens if isinstance(item, dict)]
    if len(specimen_ids) != len(set(specimen_ids)):
        issues.append({"code": "eval.duplicate-method", "message": "duplicate method specimen"})
    catalog_ids = set(catalog.methods)
    if set(specimen_ids) != catalog_ids:
        issues.append(
            {
                "code": "eval.catalog-coverage",
                "message": "inventory must cover every catalog method exactly once",
                "missing": sorted(catalog_ids - set(specimen_ids)),
                "unexpected": sorted(set(specimen_ids) - catalog_ids),
            }
        )
    if set(reviews) != catalog_ids:
        issues.append(
            {
                "code": "eval.review-coverage",
                "message": "review file must cover every catalog method exactly once",
                "missing": sorted(catalog_ids - set(reviews)),
                "unexpected": sorted(set(reviews) - catalog_ids),
            }
        )

    threshold = inventory["policy"]["correlated_screening_minimum_dimension_score"]
    results: list[dict[str, Any]] = []
    for specimen in specimens:
        method_id = specimen["method_id"]
        method = catalog.methods.get(method_id)
        if method is None:
            continue
        bundle = _repo_path(root, specimen["bundle"], expect="directory")
        result_path = _repo_path(root, specimen["result"], expect="file")
        run_verdict = verify_run(bundle, root=root)
        result = _load_object(result_path)
        rigor = result.get("rigor")
        variant = method["rigor"].get(rigor, {})
        selected_steps = variant.get("steps", [])
        completed_steps = result.get("completed_steps", [])
        missing_steps = sorted(set(selected_steps) - set(completed_steps))
        step_by_id = {step["id"]: step for step in method["procedure"]}
        required_artifact_fields = sorted(
            {
                field
                for step_id in selected_steps
                for field in step_by_id[step_id]["artifact_fields"]
            }
        )
        artifact = result.get("method_artifact")
        if not isinstance(artifact, dict):
            artifact = {}
        missing_artifact_fields = [
            field for field in required_artifact_fields if not _has_content(artifact.get(field))
        ]
        evidence_refs = sorted(
            {
                reference
                for finding in result.get("findings", [])
                for reference in finding.get("evidence_refs", [])
            }
        )
        review = reviews.get(method_id, {})
        screen_met, review_issues = _validate_review(
            review, method_id=method_id, threshold=threshold
        )
        structural_valid = (
            run_verdict.get("valid") is True
            and method_id in run_verdict.get("checked_methods", [])
            and result.get("method_id") == method_id
        )
        procedure_complete = not missing_steps and not missing_artifact_fields
        baseline_measured = review.get("decision_relevant_delta") is not None
        independent_reviews = specimen.get("independent_reviews", [])
        blockers: list[str] = []
        missing_sample_types = sorted(
            set(inventory["policy"]["required_sample_types"])
            - set(specimen.get("sample_types", []))
        )
        if missing_sample_types:
            blockers.append("missing-sample-types:" + ",".join(missing_sample_types))
        if not baseline_measured:
            blockers.append("no-blinded-no-method-baseline-comparison")
        if not independent_reviews:
            blockers.append("no-independent-practitioner-review")
        if len(specimen.get("runs", [])) < inventory["policy"]["minimum_runs_per_method"]:
            blockers.append("minimum-repeated-run-count-not-met")
        results.append(
            {
                "method_id": method_id,
                "intent": specimen["intent"],
                "desired_usefulness": specimen["desired_usefulness"],
                "specimen": {
                    "bundle": specimen["bundle"],
                    "result": specimen["result"],
                    "result_digest": file_digest(result_path),
                    "result_status": result.get("status"),
                    "sample_types": specimen.get("sample_types", []),
                },
                "structural": {
                    "valid": structural_valid,
                    "procedure_complete": procedure_complete,
                    "run_status": run_verdict.get("status"),
                    "run_side_conditions": run_verdict.get("side_conditions", []),
                    "selected_step_count": len(selected_steps),
                    "completed_selected_step_count": len(selected_steps) - len(missing_steps),
                    "missing_steps": missing_steps,
                    "required_artifact_field_count": len(required_artifact_fields),
                    "populated_required_artifact_field_count": len(required_artifact_fields)
                    - len(missing_artifact_fields),
                    "missing_artifact_fields": missing_artifact_fields,
                    "distinct_evidence_refs": evidence_refs,
                },
                "correlated_semantic_screen": {
                    "reviewer_kind": review_document.get("reviewer_kind"),
                    "review_digest": file_digest(review_path),
                    "status": "MET" if screen_met else "NOT_MET",
                    "dimensions": review.get("dimensions", {}),
                    "issues": review_issues,
                },
                "usefulness": {
                    "baseline_delta_measured": baseline_measured,
                    "independent_review_count": len(independent_reviews),
                    "evaluation_status": "INCOMPLETE",
                    "blockers": blockers,
                },
            }
        )
        if not structural_valid:
            issues.append(
                {
                    "code": "eval.specimen-invalid",
                    "message": f"recorded specimen did not verify for {method_id}",
                }
            )
        if review_issues:
            issues.append(
                {
                    "code": "eval.review-invalid",
                    "message": f"correlated review is invalid for {method_id}",
                    "details": review_issues,
                }
            )

    totals = {
        "catalog_methods": len(catalog.methods),
        "inventoried_methods": len(results),
        "structurally_valid": sum(item["structural"]["valid"] for item in results),
        "procedure_complete": sum(item["structural"]["procedure_complete"] for item in results),
        "correlated_semantic_screen_met": sum(
            item["correlated_semantic_screen"]["status"] == "MET" for item in results
        ),
        "baseline_delta_measured": sum(
            item["usefulness"]["baseline_delta_measured"] for item in results
        ),
        "independently_reviewed": sum(
            item["usefulness"]["independent_review_count"] > 0 for item in results
        ),
    }
    valid = not issues and totals["inventoried_methods"] == totals["catalog_methods"]
    return {
        "schema_version": "0.1.0",
        "evaluation_id": inventory["evaluation_id"],
        "valid": valid,
        "overall_status": "INCOMPLETE",
        "claim_boundary": inventory["claim_boundary"],
        "rubric": {
            "dimensions": list(RUBRIC_DIMENSIONS),
            "scale": "0-4 uncalibrated screening heuristic",
            "minimum_dimension_score": threshold,
        },
        "totals": totals,
        "issues": issues,
        "methods": sorted(results, key=lambda item: item["method_id"]),
    }


def write_evaluation_report(root: Path, inventory_path: Path, output_path: Path) -> dict[str, Any]:
    """Recompute the checked-in report without exposing a general file writer."""

    report = evaluate_method_suite(root, inventory_path)
    root = root.resolve()
    if output_path != EVALUATION_REPORT_PATH:
        raise ValueError(f"output must be the canonical report path: {EVALUATION_REPORT_PATH}")
    output = _repo_path(root, EVALUATION_REPORT_PATH.as_posix(), expect="file")
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
