"""Command-line interface for deterministic Method Council controls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from method_council.catalog import load_catalog, validate_repository
from method_council.documents import DocumentError, load_document, repository_root
from method_council.evidence import file_digest, validate_result_evidence
from method_council.issues import Issue
from method_council.release import verify_release_manifest
from method_council.routing import ACTIVITIES, RIGOR_COUNTS, validate_route
from method_council.schema import SCHEMA_ALIASES, SchemaRegistry
from method_council.status import aggregate_results, aggregate_status


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def _root(value: str | None, start: Path | None = None) -> Path:
    if value:
        return Path(value).resolve()
    return repository_root(start or Path.cwd())


def _validate_command(args: argparse.Namespace) -> int:
    result = validate_repository(_root(args.root))
    _emit(result)
    return 0 if result["valid"] else 1


def _route_command(args: argparse.Namespace) -> int:
    root = _root(args.root)
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
    root = _root(args.root, document_path)
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
                if not run_issues and isinstance(document, dict) and isinstance(run, dict):
                    issues.extend(validate_result_evidence(document, run))
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
    root = _root(args.root, Path(args.results[0]))
    registry = SchemaRegistry(root / "schemas")
    loaded: list[dict[str, Any]] = []
    ledger: list[dict[str, str]] = []
    issues: list[Issue] = []
    method_ids: list[str] = []
    for result_name in args.results:
        path = Path(result_name).resolve()
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
        loaded.append(result)
        method_ids.append(result["method_id"])
        ledger.append(
            {
                "method_id": result["method_id"],
                "status": result["status"],
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

    if issues:
        result = {
            "valid": False,
            "status": aggregate_status([item["status"] for item in loaded] + ["ERROR"]),
            "side_conditions": [],
            "method_count": len(loaded),
            "counts": {},
            "method_ledger": ledger,
            "issues": [issue.as_dict() for issue in issues],
        }
    else:
        result = {
            "valid": True,
            **aggregate_results(loaded),
            "method_ledger": ledger,
            "issues": [],
        }
    _emit(result)
    return 0 if result["valid"] else 1


def _verify_release_command(args: argparse.Namespace) -> int:
    manifest = Path(args.manifest).resolve()
    root = _root(args.root, manifest)
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
    aggregate_parser.set_defaults(handler=_aggregate_command)

    release_parser = subparsers.add_parser(
        "verify-release", help="derive release eligibility from content-bound gate reports"
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
