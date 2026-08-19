"""Canonical method/profile catalog loading and semantic validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from method_council.documents import DocumentError, load_document
from method_council.issues import Issue
from method_council.schema import SchemaRegistry


@dataclass(slots=True)
class Catalog:
    methods: dict[str, dict[str, Any]] = field(default_factory=dict)
    profiles: dict[str, dict[str, Any]] = field(default_factory=dict)
    method_paths: dict[str, Path] = field(default_factory=dict)
    profile_paths: dict[str, Path] = field(default_factory=dict)
    issues: list[Issue] = field(default_factory=list)


def _structured_files(directory: Path, stem: str | None = None) -> list[Path]:
    if not directory.is_dir():
        return []
    files = {
        path
        for suffix in ("*.json", "*.yaml", "*.yml")
        for path in directory.rglob(suffix)
        if stem is None or path.stem == stem
    }
    return sorted(files)


def _load_records(
    paths: list[Path], schema_name: str, registry: SchemaRegistry
) -> tuple[list[tuple[Path, dict[str, Any]]], list[Issue]]:
    records: list[tuple[Path, dict[str, Any]]] = []
    issues: list[Issue] = []
    for path in paths:
        try:
            document = load_document(path)
        except DocumentError as exc:
            issues.append(Issue("catalog.parse-error", str(exc), str(path)))
            continue
        if not isinstance(document, dict):
            issues.append(
                Issue("catalog.not-object", "catalog record must be an object", str(path))
            )
            continue
        schema_issues = registry.validate(document, schema_name)
        if schema_issues:
            issues.extend(
                Issue(issue.code, issue.message, f"{path}:{issue.path}") for issue in schema_issues
            )
            continue
        records.append((path, document))
    return records, issues


def load_catalog(root: Path, registry: SchemaRegistry | None = None) -> Catalog:
    root = root.resolve()
    registry = registry or SchemaRegistry(root / "schemas")
    catalog = Catalog()

    method_paths = _structured_files(root / "methods", stem="method")
    profile_paths = _structured_files(root / "profiles")
    if not method_paths:
        catalog.issues.append(
            Issue("catalog.methods-empty", "no method definitions found", "methods")
        )
    if not profile_paths:
        catalog.issues.append(
            Issue("catalog.profiles-empty", "no profile definitions found", "profiles")
        )

    method_records, method_issues = _load_records(method_paths, "method", registry)
    profile_records, profile_issues = _load_records(profile_paths, "profile", registry)
    catalog.issues.extend(method_issues)
    catalog.issues.extend(profile_issues)

    for path, method in method_records:
        identifier = method["id"]
        if identifier in catalog.methods:
            catalog.issues.append(
                Issue("catalog.duplicate-method", f"duplicate method id {identifier!r}", str(path))
            )
            continue
        catalog.methods[identifier] = method
        catalog.method_paths[identifier] = path

    for path, profile in profile_records:
        identifier = profile["id"]
        if identifier in catalog.profiles:
            catalog.issues.append(
                Issue(
                    "catalog.duplicate-profile", f"duplicate profile id {identifier!r}", str(path)
                )
            )
            continue
        catalog.profiles[identifier] = profile
        catalog.profile_paths[identifier] = path

    catalog.issues.extend(validate_catalog_semantics(root, catalog))
    return catalog


def validate_catalog_semantics(root: Path, catalog: Catalog) -> list[Issue]:
    issues: list[Issue] = []
    known_methods = set(catalog.methods)

    for identifier, method in catalog.methods.items():
        path = catalog.method_paths[identifier]
        if path.parent.name != identifier:
            issues.append(
                Issue(
                    "method.directory-mismatch",
                    f"method id {identifier!r} must match its parent directory name",
                    str(path),
                )
            )

        step_ids = [step["id"] for step in method["procedure"]]
        duplicate_steps = sorted({step_id for step_id in step_ids if step_ids.count(step_id) > 1})
        for step_id in duplicate_steps:
            issues.append(
                Issue(
                    "method.duplicate-step",
                    f"procedure step {step_id!r} is duplicated",
                    str(path),
                )
            )
        step_set = set(step_ids)
        required_steps = {step["id"] for step in method["procedure"] if step["required"]}
        for rigor, variant in method["rigor"].items():
            variant_steps = set(variant["steps"])
            for unknown in sorted(variant_steps - step_set):
                issues.append(
                    Issue(
                        "method.rigor-unknown-step",
                        f"{rigor} rigor references unknown step {unknown!r}",
                        str(path),
                    )
                )
            if variant["enabled"]:
                for missing in sorted(required_steps - variant_steps):
                    issues.append(
                        Issue(
                            "method.rigor-missing-required-step",
                            f"{rigor} rigor omits required step {missing!r}",
                            str(path),
                        )
                    )
            elif variant_steps:
                issues.append(
                    Issue(
                        "method.disabled-rigor-has-steps",
                        f"disabled {rigor} rigor must not select procedure steps",
                        str(path),
                    )
                )

        source_ids = [source["id"] for source in method["provenance"]["sources"]]
        if len(source_ids) != len(set(source_ids)):
            issues.append(
                Issue("method.duplicate-source", "provenance source ids must be unique", str(path))
            )

        complements = set(method["complements"])
        conflicts = set(method["conflicts"])
        required_methods = set(method["requires_methods"])
        for relation, references in (
            ("complement", complements),
            ("conflict", conflicts),
            ("required-method", required_methods),
        ):
            for reference in sorted(references - known_methods):
                issues.append(
                    Issue(
                        f"method.unknown-{relation}",
                        f"{relation} references unknown method {reference!r}",
                        str(path),
                    )
                )
        if identifier in complements or identifier in conflicts or identifier in required_methods:
            issues.append(
                Issue(
                    "method.self-reference",
                    "a method cannot reference itself through complements, conflicts, "
                    "or requires_methods",
                    str(path),
                )
            )
        for reference in sorted(complements & conflicts):
            issues.append(
                Issue(
                    "method.contradictory-relation",
                    f"method {reference!r} is both a complement and a conflict",
                    str(path),
                )
            )

        result_path = (root / method["result_schema"]).resolve()
        try:
            result_path.relative_to(root.resolve())
        except ValueError:
            issues.append(
                Issue(
                    "method.result-schema-escapes-root",
                    "result_schema escapes repository root",
                    str(path),
                )
            )
        else:
            if not result_path.is_file():
                issues.append(
                    Issue(
                        "method.result-schema-missing",
                        f"result_schema does not exist: {method['result_schema']}",
                        str(path),
                    )
                )

    from method_council.routing import validate_route

    for identifier, profile in catalog.profiles.items():
        path = catalog.profile_paths[identifier]
        allow_preview = profile["status"] in {"draft", "preview"}
        route = validate_route(
            catalog,
            activity=profile["activity"],
            rigor=profile["rigor"],
            method_ids=profile["methods"],
            allow_preview=allow_preview,
            challenge_required=profile["challenge_required"],
            include_catalog_issues=False,
        )
        for route_issue in route["issues"]:
            issues.append(
                Issue(
                    f"profile.{route_issue['code']}",
                    route_issue["message"],
                    str(path),
                )
            )
        if profile["status"] == "validated":
            preview_methods = [
                method_id
                for method_id in profile["methods"]
                if method_id in catalog.methods
                and catalog.methods[method_id]["status"] != "validated"
            ]
            if preview_methods:
                issues.append(
                    Issue(
                        "profile.validated-uses-unvalidated-method",
                        f"validated profile uses unvalidated methods: {', '.join(preview_methods)}",
                        str(path),
                    )
                )
    return issues


def validate_repository(root: Path) -> dict[str, Any]:
    registry = SchemaRegistry(root / "schemas")
    schema_issues = registry.validate_registry()
    if schema_issues:
        issues = schema_issues
        method_count = profile_count = 0
    else:
        catalog = load_catalog(root, registry)
        issues = catalog.issues
        method_count = len(catalog.methods)
        profile_count = len(catalog.profiles)
    return {
        "valid": not issues,
        "method_count": method_count,
        "profile_count": profile_count,
        "issues": [issue.as_dict() for issue in issues],
    }
