"""Content-bound run preparation and deterministic verification."""

from __future__ import annotations

import json
import os
import stat
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from method_council.catalog import Catalog, load_catalog
from method_council.documents import MAX_DOCUMENT_BYTES, DocumentError
from method_council.evidence import content_digest, file_digest, validate_result_evidence
from method_council.issues import Issue
from method_council.result_validation import validate_pass_semantics
from method_council.routing import validate_route
from method_council.schema import SchemaRegistry
from method_council.status import aggregate_results, aggregate_status


def _under_root(root: Path, candidate: Path, *, require_file: bool = False) -> Path:
    root = root.resolve()
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes repository root: {candidate}") from exc
    if require_file and (not resolved.is_file() or resolved.is_symlink()):
        raise ValueError(f"path is not a regular repository file: {candidate}")
    return resolved


def _relative_locator(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def prepare_run(
    *,
    root: Path,
    run_dir: Path,
    question: str,
    catalog: Catalog,
    profile_id: str | None,
    activity: str | None,
    rigor: str | None,
    method_ids: Sequence[str],
    allow_preview: bool,
    require_challenge: bool,
    evidence_specs: Sequence[str],
    evidence_kind: str,
    adapter: str,
    provider_state: str,
    model_requested: str | None,
    model_observed: str | None,
    external_api_calls: bool,
    correlation_group: str | None,
) -> dict[str, Any]:
    """Create a bounded run scaffold without persisting the raw question."""

    root = root.resolve()
    run_dir = _under_root(root, run_dir)
    if run_dir.exists() and (not run_dir.is_dir() or any(run_dir.iterdir())):
        raise ValueError(f"run directory must not exist or must be empty: {run_dir}")
    if not question.strip():
        raise ValueError("question input is empty")

    if profile_id:
        if activity or rigor or method_ids:
            raise ValueError(
                "--profile cannot be combined with explicit activity, rigor, or methods"
            )
        profile = catalog.profiles.get(profile_id)
        if profile is None:
            raise ValueError(f"unknown profile {profile_id!r}")
        if profile["status"] == "preview" and not allow_preview:
            raise ValueError("preview profile requires --allow-preview")
        activity = profile["activity"]
        rigor = profile["rigor"]
        method_ids = profile["methods"]
        require_challenge = profile["challenge_required"]
        route_source = "profile"
        route_why = [f"profile:{profile_id}", profile["notes"]]
    else:
        if not activity or not rigor or not method_ids:
            raise ValueError(
                "explicit routes require --activity, --rigor, and at least one --method"
            )
        route_source = "user-explicit"
        route_why = ["Explicit route supplied to deterministic preparation."]

    route = validate_route(
        catalog,
        activity=activity,
        rigor=rigor,
        method_ids=method_ids,
        allow_preview=allow_preview,
        challenge_required=require_challenge,
    )
    if not route["valid"]:
        return {"valid": False, "route": route, "issues": route["issues"]}

    run_id = run_dir.name
    if len(method_ids) > 1 and correlation_group is None:
        correlation_group = f"{adapter}-{run_id}"

    evidence: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for spec in evidence_specs:
        if "=" not in spec:
            raise ValueError("evidence must use ID=PATH")
        identifier, raw_path = spec.split("=", 1)
        if not identifier or identifier in seen_ids:
            raise ValueError(f"invalid or duplicate evidence id: {identifier!r}")
        raw_candidate = Path(raw_path)
        path = _under_root(
            root,
            raw_candidate if raw_candidate.is_absolute() else root / raw_candidate,
            require_file=True,
        )
        seen_ids.add(identifier)
        evidence.append(
            {
                "id": identifier,
                "kind": evidence_kind,
                "digest": file_digest(path),
                "locator": _relative_locator(root, path),
                "limitations": [],
            }
        )

    run = {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "created_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "activity": activity,
        "rigor": rigor,
        "question_digest": content_digest(question),
        "raw_prompt_persisted": False,
        "methods": list(method_ids),
        "evidence": evidence,
        "route": {
            "source": route_source,
            "validated": True,
            "profile_id": profile_id,
            "allow_preview": allow_preview,
            "challenge_required": require_challenge,
            "why": route_why,
        },
        "host": {
            "adapter": adapter,
            "provider_state": provider_state,
            "model_requested": model_requested,
            "model_observed": model_observed,
            "external_api_calls": external_api_calls,
            "correlation_group": correlation_group,
        },
    }
    schema_issues = SchemaRegistry(root / "schemas").validate(run, "run")
    if schema_issues:
        return {
            "valid": False,
            "route": route,
            "issues": [issue.as_dict() for issue in schema_issues],
        }

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "method-results").mkdir()
    run_path = run_dir / "run.json"
    temporary = run_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(run_path)
    return {
        "valid": True,
        "run": run,
        "run_path": _relative_locator(root, run_path),
        "route": route,
        "issues": [],
    }


def _prefixed(issues: Sequence[Issue], prefix: str) -> list[Issue]:
    return [Issue(issue.code, issue.message, f"{prefix}:{issue.path}") for issue in issues]


def _read_regular_document(path: Path) -> bytes:
    """Read one regular child document without following symlinks or exceeding the cap."""

    try:
        if path.is_symlink():
            raise DocumentError(f"structured document is a symlink: {path}")
        flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
    except (OSError, DocumentError) as exc:
        if isinstance(exc, DocumentError):
            raise
        raise DocumentError(f"could not read {path}: {exc}") from exc

    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise DocumentError(f"structured document is not a regular file: {path}")
        if metadata.st_size > MAX_DOCUMENT_BYTES:
            raise DocumentError(
                f"structured document exceeds {MAX_DOCUMENT_BYTES} byte limit: {path}"
            )
        with os.fdopen(descriptor, "rb") as handle:
            descriptor = -1
            data = handle.read(MAX_DOCUMENT_BYTES + 1)
    except OSError as exc:
        raise DocumentError(f"could not read {path}: {exc}") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)

    if len(data) > MAX_DOCUMENT_BYTES:
        raise DocumentError(f"structured document exceeds {MAX_DOCUMENT_BYTES} byte limit: {path}")
    return data


def _load_object(
    path: Path, code: str, issues: list[Issue]
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = _read_regular_document(path)
        document = json.loads(raw)
    except (DocumentError, json.JSONDecodeError, UnicodeError) as exc:
        issues.append(Issue(code, str(exc), path.as_posix()))
        return None, None
    if not isinstance(document, dict):
        issues.append(Issue(code, "document must be an object", path.as_posix()))
        return None, None
    return document, content_digest(raw)


def _invalid_status(issues: Sequence[Issue], valid_status: str) -> str:
    incomplete_codes = {
        "run.result-missing",
        "run.report-missing",
        "run.evidence-missing",
        "run.report-status-unsupported-pass",
        "run.report-ledger-unsupported-pass",
    }
    issue_status = (
        "INCOMPLETE"
        if issues
        and all(
            issue.code in incomplete_codes or issue.code.startswith("result.pass-")
            for issue in issues
        )
        else "ERROR"
    )
    return aggregate_status([valid_status, issue_status])


def _validate_manifest_route(run: Mapping[str, Any], catalog: Catalog, issues: list[Issue]) -> None:
    route_policy = run["route"]
    source = route_policy["source"]
    profile_id = route_policy["profile_id"]
    if source == "profile":
        profile = catalog.profiles.get(profile_id)
        if profile is None:
            issues.append(
                Issue(
                    "run.profile-unknown",
                    f"route references unknown profile {profile_id!r}",
                    "/route/profile_id",
                )
            )
        else:
            expected = {
                "activity": profile["activity"],
                "rigor": profile["rigor"],
                "methods": profile["methods"],
            }
            for field, expected_value in expected.items():
                if run[field] != expected_value:
                    issues.append(
                        Issue(
                            "run.profile-mismatch",
                            f"run {field} does not exactly match profile {profile_id!r}",
                            f"/{field}",
                        )
                    )
            if route_policy["challenge_required"] != profile["challenge_required"]:
                issues.append(
                    Issue(
                        "run.profile-mismatch",
                        f"challenge policy does not exactly match profile {profile_id!r}",
                        "/route/challenge_required",
                    )
                )
            if profile["status"] in {"draft", "preview"} and not route_policy["allow_preview"]:
                issues.append(
                    Issue(
                        "run.profile-preview-disallowed",
                        f"profile {profile_id!r} requires preview opt-in",
                        "/route/allow_preview",
                    )
                )
    elif profile_id is not None:
        issues.append(
            Issue(
                "run.profile-unexpected",
                "non-profile route must not carry a profile id",
                "/route/profile_id",
            )
        )

    route = validate_route(
        catalog,
        activity=run["activity"],
        rigor=run["rigor"],
        method_ids=run["methods"],
        allow_preview=route_policy["allow_preview"],
        challenge_required=route_policy["challenge_required"],
        include_catalog_issues=False,
    )
    for issue in route["issues"]:
        issues.append(Issue("run.route-invalid", issue["message"], issue["path"]))


def verify_run(run_dir: Path, *, root: Path) -> dict[str, Any]:
    """Recompute run completeness, digests, status, and report binding."""

    root = root.resolve()
    run_dir = _under_root(root, run_dir)
    registry = SchemaRegistry(root / "schemas")
    issues: list[Issue] = []
    run_path = run_dir / "run.json"
    run, _ = _load_object(run_path, "run.manifest-invalid", issues)
    if run is None:
        return _verdict("unknown", [], [], None, [], issues)
    run_schema_issues = registry.validate(run, "run")
    issues.extend(_prefixed(run_schema_issues, "run.json"))
    run_id = str(run.get("run_id", "unknown"))
    selected = [str(item) for item in run.get("methods", [])]
    if run_schema_issues:
        return _verdict(run_id, selected, [], None, [], issues)
    if run_id != run_dir.name:
        issues.append(
            Issue(
                "run.directory-id-mismatch",
                "run_id must exactly match the run directory name",
                "/run_id",
            )
        )

    for index, evidence in enumerate(run.get("evidence", [])):
        if not isinstance(evidence, Mapping) or not evidence.get("locator"):
            continue
        locator = Path(str(evidence["locator"]))
        if locator.is_absolute():
            issues.append(
                Issue(
                    "run.evidence-absolute",
                    "evidence locator must be repository-relative",
                    f"/evidence/{index}/locator",
                )
            )
            continue
        try:
            evidence_path = _under_root(root, root / locator, require_file=True)
        except ValueError as exc:
            issues.append(Issue("run.evidence-missing", str(exc), f"/evidence/{index}/locator"))
            continue
        if file_digest(evidence_path) != evidence.get("digest"):
            issues.append(
                Issue(
                    "run.evidence-digest",
                    "evidence digest does not match current bytes",
                    f"/evidence/{index}/digest",
                )
            )

    try:
        catalog = load_catalog(root, registry)
    except (OSError, ValueError) as exc:
        issues.append(Issue("run.catalog-error", str(exc), "methods"))
        catalog = Catalog()
    for issue in catalog.issues:
        issues.append(Issue("run.catalog-invalid", issue.message, issue.path))
    _validate_manifest_route(run, catalog, issues)

    result_dir = run_dir / "method-results"
    if result_dir.is_symlink() or (result_dir.exists() and not result_dir.is_dir()):
        issues.append(
            Issue(
                "run.result-directory-invalid",
                "method-results must be a real directory",
                "method-results",
            )
        )
        result_paths: list[Path] = []
    elif result_dir.is_dir():
        try:
            result_paths = sorted(path for path in result_dir.iterdir() if path.suffix == ".json")
        except OSError as exc:
            issues.append(Issue("run.result-directory-invalid", str(exc), "method-results"))
            result_paths = []
    else:
        result_paths = []
    results: list[dict[str, Any]] = []
    claimed_results: list[dict[str, Any]] = []
    ledger: list[dict[str, str]] = []
    claimed_ledger: list[dict[str, str]] = []
    finding_ids: list[str] = []
    observed_methods: list[str] = []
    host = run.get("host", {})
    for path in result_paths:
        result, result_digest = _load_object(path, "run.result-invalid", issues)
        if result is None:
            continue
        schema_issues = registry.validate(result, "method-result")
        if schema_issues:
            issues.extend(_prefixed(schema_issues, path.relative_to(run_dir).as_posix()))
            continue
        result_issues = validate_result_evidence(result, run)
        issues.extend(_prefixed(result_issues, path.relative_to(run_dir).as_posix()))
        method_id = str(result["method_id"])
        observed_methods.append(method_id)
        method = catalog.methods.get(method_id)
        if method and result["method_version"] != method["version"]:
            issues.append(
                Issue(
                    "run.method-version",
                    "result method version does not match catalog",
                    path.as_posix(),
                )
            )
        if result["rigor"] != run.get("rigor"):
            issues.append(
                Issue("run.rigor-mismatch", "result rigor does not match run", path.as_posix())
            )
        if result["execution"] != host:
            issues.append(
                Issue(
                    "run.execution-mismatch",
                    "result execution metadata does not match run host",
                    path.as_posix(),
                )
            )
        semantic_issues = validate_pass_semantics(result, method, run["rigor"]) if method else []
        issues.extend(_prefixed(semantic_issues, path.relative_to(run_dir).as_posix()))
        finding_ids.extend(str(finding["id"]) for finding in result.get("findings", []))
        claimed_results.append(result)
        effective_result = dict(result)
        if result["status"] == "PASS" and semantic_issues:
            effective_result["status"] = "INCOMPLETE"
        results.append(effective_result)
        assert result_digest is not None
        ledger.append(
            {
                "method_id": method_id,
                "status": effective_result["status"],
                "result_digest": result_digest,
            }
        )
        claimed_ledger.append(
            {
                "method_id": method_id,
                "status": result["status"],
                "result_digest": result_digest,
            }
        )

    counts = Counter(observed_methods)
    for method_id, count in sorted(counts.items()):
        if count > 1:
            issues.append(
                Issue(
                    "run.result-duplicate", f"multiple results for {method_id!r}", "method-results"
                )
            )
    for method_id in sorted(set(selected) - set(observed_methods)):
        issues.append(
            Issue("run.result-missing", f"missing result for {method_id!r}", "method-results")
        )
    for method_id in sorted(set(observed_methods) - set(selected)):
        issues.append(
            Issue("run.result-extra", f"unselected result for {method_id!r}", "method-results")
        )

    duplicate_findings = sorted(
        identifier for identifier, count in Counter(finding_ids).items() if count > 1
    )
    for identifier in duplicate_findings:
        issues.append(
            Issue(
                "run.finding-duplicate",
                f"finding id {identifier!r} is not globally unique",
                "method-results",
            )
        )

    groups = Counter(
        result["execution"]["correlation_group"]
        for result in results
        if result["execution"]["correlation_group"] is not None
    )
    for result in results:
        group = result["execution"]["correlation_group"]
        if (
            group is not None
            and groups[group] > 1
            and "CORRELATED" not in result["side_conditions"]
        ):
            issues.append(
                Issue(
                    "run.correlation-missing",
                    "shared correlation group requires CORRELATED",
                    f"method-results/{result['method_id']}",
                )
            )
        if group is None and "CORRELATED" in result["side_conditions"]:
            issues.append(
                Issue(
                    "run.correlation-unbound",
                    "CORRELATED requires a non-null correlation group",
                    f"method-results/{result['method_id']}",
                )
            )
    if (
        len(selected) > 1
        and host.get("adapter") == "codex"
        and host.get("correlation_group") is None
    ):
        issues.append(
            Issue(
                "run.correlation-group-missing",
                "multi-method Codex run requires a correlation group",
                "/host/correlation_group",
            )
        )

    order = {method_id: index for index, method_id in enumerate(selected)}
    ledger.sort(key=lambda entry: order.get(entry["method_id"], len(order)))
    claimed_ledger.sort(key=lambda entry: order.get(entry["method_id"], len(order)))
    aggregate = (
        aggregate_results(results) if results else {"status": "INCOMPLETE", "side_conditions": []}
    )
    claimed_aggregate = (
        aggregate_results(claimed_results)
        if claimed_results
        else {"status": "INCOMPLETE", "side_conditions": []}
    )
    report_path = run_dir / "report.json"
    report_digest: str | None = None
    report = None
    if not report_path.exists() and not report_path.is_symlink():
        issues.append(Issue("run.report-missing", "report.json is missing", "report.json"))
    else:
        report, report_digest = _load_object(report_path, "run.report-invalid", issues)
    if report is not None:
        report_schema_issues = registry.validate(report, "report")
        issues.extend(_prefixed(report_schema_issues, "report.json"))
        if not report_schema_issues:
            if report["run_id"] != run_id:
                issues.append(Issue("run.report-run-id", "report run_id does not match", "/run_id"))
            if report["status"] != aggregate["status"]:
                mismatch_code = (
                    "run.report-status-unsupported-pass"
                    if report["status"] == claimed_aggregate["status"]
                    and claimed_aggregate["status"] != aggregate["status"]
                    else "run.report-status"
                )
                issues.append(
                    Issue(
                        mismatch_code,
                        "report status is not deterministically derived",
                        "/status",
                    )
                )
            if set(report["side_conditions"]) != set(aggregate["side_conditions"]):
                issues.append(
                    Issue(
                        "run.report-side-conditions",
                        "report side conditions do not match",
                        "/side_conditions",
                    )
                )
            expected_ledger = {entry["method_id"]: entry for entry in ledger}
            claimed_expected_ledger = {entry["method_id"]: entry for entry in claimed_ledger}
            report_ledger = {entry["method_id"]: entry for entry in report["method_ledger"]}
            if report_ledger != expected_ledger or len(report["method_ledger"]) != len(ledger):
                mismatch_code = (
                    "run.report-ledger-unsupported-pass"
                    if report_ledger == claimed_expected_ledger
                    and len(report["method_ledger"]) == len(claimed_ledger)
                    and claimed_expected_ledger != expected_ledger
                    else "run.report-ledger"
                )
                issues.append(
                    Issue(
                        mismatch_code,
                        "report ledger does not match checked result bytes and canonical statuses",
                        "/method_ledger",
                    )
                )
            known_findings = set(finding_ids)
            for index, judgment in enumerate(report["key_judgments"]):
                for reference in judgment["finding_refs"]:
                    if reference not in known_findings:
                        issues.append(
                            Issue(
                                "run.report-finding",
                                f"unknown finding reference {reference!r}",
                                f"/key_judgments/{index}/finding_refs",
                            )
                        )

    return _verdict(
        run_id,
        selected,
        sorted(set(observed_methods)),
        report_digest,
        aggregate.get("side_conditions", []),
        issues,
        valid_status=aggregate.get("status", "INCOMPLETE"),
    )


def _verdict(
    run_id: str,
    selected: list[str],
    checked: list[str],
    report_digest: str | None,
    side_conditions: list[str],
    issues: Sequence[Issue],
    *,
    valid_status: str = "INCOMPLETE",
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "valid": not issues,
        "status": valid_status if not issues else _invalid_status(issues, valid_status),
        "side_conditions": side_conditions,
        "selected_methods": selected,
        "checked_methods": checked,
        "report_digest": report_digest,
        "issues": [issue.as_dict() for issue in issues],
    }
