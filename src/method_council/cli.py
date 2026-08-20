"""Command-line interface for deterministic Method Council controls."""

from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from method_council.acceptance import verify_acceptance
from method_council.catalog import load_catalog, validate_repository
from method_council.documents import (
    DocumentError,
    catalog_root,
    load_document,
    workspace_root,
)
from method_council.evidence import file_digest
from method_council.issues import Issue
from method_council.release import verify_release_manifest
from method_council.result_validation import validate_result_against_run
from method_council.routing import ACTIVITIES, RIGOR_COUNTS, validate_route
from method_council.run import prepare_run, verify_run
from method_council.schema import SCHEMA_ALIASES, SchemaRegistry
from method_council.status import aggregate_results, aggregate_status


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _catalog_root(value: str | None, start: Path | None = None) -> Path:
    if value:
        return Path(value).resolve()
    return catalog_root(start)


def _workspace_root(value: str | None, start: Path | None = None) -> Path:
    if value:
        return Path(value).resolve()
    return workspace_root(start)


def _package_version() -> str:
    try:
        return version("method-council")
    except PackageNotFoundError:
        return "0+unknown"


def _validate_command(args: argparse.Namespace) -> int:
    result = validate_repository(_catalog_root(args.root))
    _emit(result)
    return 0 if result["valid"] else 1


def _route_command(args: argparse.Namespace) -> int:
    root = _catalog_root(args.root)
    catalog = load_catalog(root)
    result = validate_route(
        catalog,
        activity=args.activity,
        rigor=args.rigor,
        method_ids=args.method,
        allow_preview=args.allow_preview,
        challenge_required=args.require_challenge,
    )
    _emit(result)
    return 0 if result["valid"] else 1


def _check_command(args: argparse.Namespace) -> int:
    document_path = Path(args.document).resolve()
    root = _catalog_root(args.root, document_path)
    registry = SchemaRegistry(root / "schemas")
    try:
        document = load_document(document_path)
    except DocumentError as exc:
        result = {
            "valid": False,
            "schema": args.schema,
            "document": str(document_path),
            "issues": [Issue("document.parse-error", str(exc), str(document_path)).as_dict()],
        }
        _emit(result)
        return 1
    issues = registry.validate(document, args.schema)
    if args.run:
        if args.schema != "method-result":
            issues.append(
                Issue("check.run-not-applicable", "--run is valid only for method-result checks")
            )
        else:
            try:
                run = load_document(Path(args.run).resolve())
            except DocumentError as exc:
                issues.append(Issue("check.run-parse-error", str(exc), str(args.run)))
            else:
                run_issues = registry.validate(run, "run")
                issues.extend(run_issues)
                if (
                    not issues
                    and not run_issues
                    and isinstance(document, dict)
                    and isinstance(run, dict)
                ):
                    catalog = load_catalog(root, registry)
                    issues.extend(
                        Issue("check.catalog-invalid", issue.message, issue.path)
                        for issue in catalog.issues
                    )
                    if not catalog.issues:
                        method = catalog.methods.get(str(document["method_id"]))
                        result_issues, _ = validate_result_against_run(document, run, method)
                        issues.extend(result_issues)
    result = {
        "valid": not issues,
        "schema": args.schema,
        "document": str(document_path),
        "digest": file_digest(document_path),
        "issues": [issue.as_dict() for issue in issues],
    }
    _emit(result)
    return 0 if result["valid"] else 1


def _aggregate_command(args: argparse.Namespace) -> int:
    result_paths = [Path(result_name).resolve() for result_name in args.results]
    root = _catalog_root(args.root, result_paths[0])
    registry = SchemaRegistry(root / "schemas")
    claimed_results: list[tuple[Path, dict[str, Any]]] = []
    issues: list[Issue] = []
    for path in result_paths:
        try:
            result = load_document(path)
        except DocumentError as exc:
            issues.append(Issue("aggregate.parse-error", str(exc), str(path)))
            continue
        schema_issues = registry.validate(result, "method-result")
        if schema_issues:
            issues.extend(
                Issue(issue.code, issue.message, f"{path}:{issue.path}") for issue in schema_issues
            )
            continue
        claimed_results.append((path, result))

    run: dict[str, Any] | None = None
    catalog = None
    run_path: Path | None = Path(args.run).resolve() if args.run else None
    if run_path is None:
        candidates = {
            path.parent.parent / "run.json"
            for path, _ in claimed_results
            if path.parent.name == "method-results" and (path.parent.parent / "run.json").is_file()
        }
        if len(candidates) == 1:
            run_path = candidates.pop()
        elif len(candidates) > 1:
            issues.append(
                Issue(
                    "aggregate.multiple-runs",
                    "results resolve to more than one run; supply --run explicitly",
                    "/results",
                )
            )
    if run_path is not None:
        try:
            loaded_run = load_document(run_path)
        except DocumentError as exc:
            issues.append(Issue("aggregate.run-parse-error", str(exc), str(run_path)))
        else:
            run_issues = registry.validate(loaded_run, "run")
            issues.extend(
                Issue(issue.code, issue.message, f"{run_path}:{issue.path}") for issue in run_issues
            )
            if not run_issues and isinstance(loaded_run, dict):
                run = loaded_run
                catalog = load_catalog(root, registry)
                issues.extend(
                    Issue("aggregate.catalog-invalid", issue.message, issue.path)
                    for issue in catalog.issues
                )

    loaded: list[dict[str, Any]] = []
    ledger: list[dict[str, str]] = []
    method_ids: list[str] = []
    for path, claimed_result in claimed_results:
        effective_result = dict(claimed_result)
        method_ids.append(str(claimed_result["method_id"]))
        if run is not None and catalog is not None and not catalog.issues:
            method = catalog.methods.get(str(claimed_result["method_id"]))
            result_issues, pass_issues = validate_result_against_run(claimed_result, run, method)
            issues.extend(
                Issue(issue.code, issue.message, f"{path}:{issue.path}") for issue in result_issues
            )
            if claimed_result["status"] == "PASS" and pass_issues:
                effective_result["status"] = "INCOMPLETE"
        elif claimed_result["status"] == "PASS":
            if run_path is None:
                issues.append(
                    Issue(
                        "aggregate.run-required-for-pass",
                        "PASS results require --run or a discoverable sibling run.json",
                        str(path),
                    )
                )
            effective_result["status"] = "INCOMPLETE"
        loaded.append(effective_result)
        ledger.append(
            {
                "method_id": str(effective_result["method_id"]),
                "status": str(effective_result["status"]),
                "result_digest": file_digest(path),
            }
        )
    duplicates = sorted(
        {identifier for identifier in method_ids if method_ids.count(identifier) > 1}
    )
    for identifier in duplicates:
        issues.append(
            Issue(
                "aggregate.duplicate-method",
                f"multiple results supplied for method {identifier!r}",
                "/results",
            )
        )

    derived = aggregate_results(loaded)
    if issues:
        incomplete_codes = {"aggregate.run-required-for-pass"}
        issue_status = (
            "INCOMPLETE"
            if all(
                issue.code in incomplete_codes or issue.code.startswith("result.pass-")
                for issue in issues
            )
            else "ERROR"
        )
        derived["status"] = aggregate_status((derived["status"], issue_status))
    result = {
        "valid": not issues,
        **derived,
        "method_ledger": ledger,
        "issues": [issue.as_dict() for issue in issues],
    }
    _emit(result)
    return 0 if result["valid"] else 1


def _prepare_command(args: argparse.Namespace) -> int:
    root = _workspace_root(args.root)
    catalogue = _catalog_root(args.catalog_root, root)
    question_path = Path(args.question_file).resolve() if args.question_file else None
    question = question_path.read_text(encoding="utf-8") if question_path else sys.stdin.read()
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = root / run_dir
    execution_plan = None
    if args.execution_plan:
        plan_path = Path(args.execution_plan)
        if not plan_path.is_absolute():
            plan_path = root / plan_path
        resolved_plan = plan_path.resolve()
        try:
            resolved_plan.relative_to(root)
        except ValueError as exc:
            raise ValueError("execution plan must be a repository file") from exc
        if plan_path.is_symlink() or not resolved_plan.is_file():
            raise ValueError("execution plan must be a regular repository file")
        loaded_plan = load_document(resolved_plan)
        if not isinstance(loaded_plan, dict):
            raise ValueError("execution plan must be an object")
        execution_plan = loaded_plan
    result = prepare_run(
        root=root,
        run_dir=run_dir,
        question=question,
        catalog=load_catalog(catalogue),
        profile_id=args.profile,
        activity=args.activity,
        rigor=args.rigor,
        method_ids=args.method or [],
        allow_preview=args.allow_preview,
        require_challenge=args.require_challenge,
        evidence_specs=args.evidence or [],
        evidence_kind=args.evidence_kind,
        adapter=args.adapter,
        provider_state=args.provider_state,
        model_requested=args.model_requested,
        model_observed=args.model_observed,
        external_api_calls=args.external_api_calls,
        correlation_group=args.correlation_group,
        execution_plan=execution_plan,
        catalog_root=catalogue,
    )
    _emit(result)
    return 0 if result["valid"] else 1


def _verify_run_command(args: argparse.Namespace) -> int:
    root = _workspace_root(args.root)
    catalogue = _catalog_root(args.catalog_root, root)
    run_dir = Path(args.run_dir)
    if not run_dir.is_absolute():
        run_dir = root / run_dir
    result = verify_run(run_dir, root=root, catalog_root=catalogue)
    _emit(result)
    return 0 if result["valid"] else 1


def _verify_acceptance_command(args: argparse.Namespace) -> int:
    root = _catalog_root(args.root, Path(args.bundle_dir))
    bundle_dir = Path(args.bundle_dir)
    if not bundle_dir.is_absolute():
        bundle_dir = root / bundle_dir
    result = verify_acceptance(bundle_dir, root=root)
    _emit(result)
    return 0 if result["valid"] else 1


def _verify_release_command(args: argparse.Namespace) -> int:
    manifest = Path(args.manifest)
    if not manifest.is_absolute():
        manifest = Path.cwd() / manifest
    root = _catalog_root(args.root, manifest)
    result = verify_release_manifest(manifest, root=root)
    _emit(result)
    return 0 if result["release_eligible"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="method-council",
        description=(
            "Deterministic validation for Method Council. No command calls a model provider."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {_package_version()}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="validate schemas, methods, profiles, and catalog semantics"
    )
    validate_parser.add_argument("--root", help="repository root (auto-detected by default)")
    validate_parser.set_defaults(handler=_validate_command)

    route_parser = subparsers.add_parser("route", help="validate a proposed method route")
    route_parser.add_argument("--root", help="repository root (auto-detected by default)")
    route_parser.add_argument("--activity", choices=sorted(ACTIVITIES), required=True)
    route_parser.add_argument("--rigor", choices=sorted(RIGOR_COUNTS), required=True)
    route_parser.add_argument("--method", action="append", required=True, help="method id; repeat")
    route_parser.add_argument(
        "--allow-preview",
        action="store_true",
        help="allow preview methods; never allows draft/retired",
    )
    route_parser.add_argument(
        "--require-challenge",
        action="store_true",
        help="require at least one selected method with the challenge capability",
    )
    route_parser.set_defaults(handler=_route_command)

    check_parser = subparsers.add_parser("check", help="validate one canonical document")
    check_parser.add_argument("document", help="JSON or YAML document")
    check_parser.add_argument("--schema", choices=sorted(SCHEMA_ALIASES), required=True)
    check_parser.add_argument("--root", help="repository root (auto-detected by default)")
    check_parser.add_argument("--run", help="run manifest for method-result evidence binding")
    check_parser.set_defaults(handler=_check_command)

    aggregate_parser = subparsers.add_parser(
        "aggregate", help="derive status and ledger from validated method results"
    )
    aggregate_parser.add_argument("results", nargs="+", help="method-result JSON or YAML files")
    aggregate_parser.add_argument("--root", help="repository root (auto-detected by default)")
    aggregate_parser.add_argument(
        "--run", help="run manifest; auto-detected for results inside method-results/"
    )
    aggregate_parser.set_defaults(handler=_aggregate_command)

    prepare_parser = subparsers.add_parser(
        "prepare", help="create a content-bound run scaffold without calling a model"
    )
    prepare_parser.add_argument("run_dir", help="new or empty run directory under the repository")
    prepare_parser.add_argument(
        "--root", help="workspace root for run files and evidence (auto-detected by default)"
    )
    prepare_parser.add_argument(
        "--catalog-root", help="catalogue root (nearby checkout or installed data by default)"
    )
    prepare_parser.add_argument("--profile", help="canonical profile id")
    prepare_parser.add_argument("--activity", choices=sorted(ACTIVITIES))
    prepare_parser.add_argument("--rigor", choices=sorted(RIGOR_COUNTS))
    prepare_parser.add_argument("--method", action="append", help="method id; repeat")
    prepare_parser.add_argument("--allow-preview", action="store_true")
    prepare_parser.add_argument("--require-challenge", action="store_true")
    prepare_parser.add_argument(
        "--question-file", help="public/non-sensitive question fixture; stdin otherwise"
    )
    prepare_parser.add_argument(
        "--evidence", action="append", help="bind repository file as ID=PATH"
    )
    prepare_parser.add_argument(
        "--evidence-kind",
        choices=["user-supplied", "repository", "retrieved", "observed", "generated"],
        default="repository",
    )
    prepare_parser.add_argument("--adapter", default="codex")
    prepare_parser.add_argument(
        "--provider-state",
        choices=["verified", "preview", "unverified", "unavailable", "degraded"],
        default="unverified",
    )
    prepare_parser.add_argument("--model-requested")
    prepare_parser.add_argument("--model-observed")
    prepare_parser.add_argument("--external-api-calls", action="store_true")
    prepare_parser.add_argument("--correlation-group")
    prepare_parser.add_argument(
        "--execution-plan",
        help="repository JSON or YAML assigning selected methods to multiple model targets",
    )
    prepare_parser.set_defaults(handler=_prepare_command)

    run_parser = subparsers.add_parser(
        "verify-run", help="derive a deterministic verdict from a run directory"
    )
    run_parser.add_argument("run_dir", help="run directory containing run.json and artifacts")
    run_parser.add_argument(
        "--root", help="workspace root for run files and evidence (auto-detected by default)"
    )
    run_parser.add_argument(
        "--catalog-root", help="catalogue root (nearby checkout or installed data by default)"
    )
    run_parser.set_defaults(handler=_verify_run_command)

    acceptance_parser = subparsers.add_parser(
        "verify-acceptance",
        help="recompute a content-bound verdict for host-recorded acceptance evidence",
    )
    acceptance_parser.add_argument(
        "bundle_dir", help="acceptance bundle containing run and host evidence"
    )
    acceptance_parser.add_argument("--root", help="repository root (auto-detected by default)")
    acceptance_parser.set_defaults(handler=_verify_acceptance_command)

    release_parser = subparsers.add_parser(
        "verify-release",
        help="recompute registered release gates and fail closed on unattested reports",
    )
    release_parser.add_argument("manifest", help="release manifest JSON or YAML")
    release_parser.add_argument("--root", help="repository and release artifact root")
    release_parser.set_defaults(handler=_verify_release_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (DocumentError, KeyError, OSError, ValueError) as exc:
        _emit(
            {
                "valid": False,
                "error": {"code": "command.error", "message": str(exc)},
            }
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
