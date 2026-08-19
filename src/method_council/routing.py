"""Deterministic validation of model-, profile-, or user-proposed routes."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from method_council.issues import Issue

if TYPE_CHECKING:
    from method_council.catalog import Catalog


RIGOR_COUNTS = {"rapid": (1, 2), "standard": (3, 4), "intensive": (4, 6)}
ACTIVITIES = {"analyse", "investigate", "decide", "forecast", "architect", "review"}


def validate_route(
    catalog: Catalog,
    *,
    activity: str,
    rigor: str,
    method_ids: Sequence[str],
    allow_preview: bool = False,
    include_catalog_issues: bool = True,
) -> dict[str, Any]:
    issues: list[Issue] = []
    if include_catalog_issues:
        issues.extend(catalog.issues)

    if activity not in ACTIVITIES:
        issues.append(
            Issue("route.unknown-activity", f"unknown activity {activity!r}", "/activity")
        )
    if rigor not in RIGOR_COUNTS:
        issues.append(Issue("route.unknown-rigor", f"unknown rigor {rigor!r}", "/rigor"))
    else:
        minimum, maximum = RIGOR_COUNTS[rigor]
        if not minimum <= len(method_ids) <= maximum:
            issues.append(
                Issue(
                    "route.method-count",
                    f"{rigor} rigor requires {minimum}-{maximum} methods; got {len(method_ids)}",
                    "/methods",
                )
            )

    duplicate_ids = sorted(
        {identifier for identifier in method_ids if method_ids.count(identifier) > 1}
    )
    for identifier in duplicate_ids:
        issues.append(
            Issue(
                "route.duplicate-method",
                f"method {identifier!r} is selected more than once",
                "/methods",
            )
        )

    selected = set(method_ids)
    preview_methods: list[str] = []
    for index, identifier in enumerate(method_ids):
        method = catalog.methods.get(identifier)
        if method is None:
            issues.append(
                Issue("route.unknown-method", f"unknown method {identifier!r}", f"/methods/{index}")
            )
            continue
        status = method["status"]
        if status == "preview" and allow_preview:
            preview_methods.append(identifier)
        elif status != "validated":
            issues.append(
                Issue(
                    "route.method-status",
                    f"method {identifier!r} has disallowed catalog status {status!r}",
                    f"/methods/{index}",
                )
            )
        if activity in ACTIVITIES and activity not in method["activities"]:
            issues.append(
                Issue(
                    "route.activity-mismatch",
                    f"method {identifier!r} does not support activity {activity!r}",
                    f"/methods/{index}",
                )
            )
        if rigor in RIGOR_COUNTS and not method["rigor"][rigor]["enabled"]:
            issues.append(
                Issue(
                    "route.rigor-disabled",
                    f"method {identifier!r} does not support {rigor} rigor",
                    f"/methods/{index}",
                )
            )

    conflict_pairs: set[tuple[str, str]] = set()
    for identifier in selected & set(catalog.methods):
        for conflict in set(catalog.methods[identifier]["conflicts"]) & selected:
            conflict_pairs.add(tuple(sorted((identifier, conflict))))
    for left, right in sorted(conflict_pairs):
        issues.append(
            Issue(
                "route.conflict",
                f"selected methods {left!r} and {right!r} conflict",
                "/methods",
            )
        )

    return {
        "valid": not issues,
        "activity": activity,
        "rigor": rigor,
        "methods": list(method_ids),
        "allow_preview": allow_preview,
        "preview_methods": preview_methods,
        "issues": [issue.as_dict() for issue in issues],
    }
