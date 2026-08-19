from method_council.catalog import Catalog
from method_council.routing import validate_route


def _method(*, status="validated", activities=None, disabled=(), conflicts=()):
    rigor = {
        level: {"enabled": level not in disabled, "steps": [], "minimum_evidence_refs": 0}
        for level in ("rapid", "standard", "intensive")
    }
    return {
        "status": status,
        "activities": activities or ["analyse"],
        "rigor": rigor,
        "conflicts": list(conflicts),
    }


def _catalog():
    return Catalog(
        methods={
            "method-a": _method(conflicts=("method-b",)),
            "method-b": _method(),
            "method-c": _method(status="preview"),
            "method-d": _method(activities=["decide"]),
            "method-e": _method(disabled=("standard",)),
        }
    )


def test_valid_route_is_accepted():
    result = validate_route(
        _catalog(),
        activity="analyse",
        rigor="standard",
        method_ids=["method-a", "method-d", "method-e"],
    )

    assert not result["valid"]
    assert {issue["code"] for issue in result["issues"]} == {
        "route.activity-mismatch",
        "route.rigor-disabled",
    }


def test_preview_requires_explicit_allowance():
    denied = validate_route(_catalog(), activity="analyse", rigor="rapid", method_ids=["method-c"])
    allowed = validate_route(
        _catalog(),
        activity="analyse",
        rigor="rapid",
        method_ids=["method-c"],
        allow_preview=True,
    )

    assert not denied["valid"]
    assert allowed["valid"]
    assert allowed["preview_methods"] == ["method-c"]


def test_unknown_duplicate_conflict_and_count_are_rejected():
    result = validate_route(
        _catalog(),
        activity="analyse",
        rigor="standard",
        method_ids=["method-a", "method-b", "method-a", "missing", "method-c"],
        allow_preview=True,
    )

    codes = {issue["code"] for issue in result["issues"]}
    assert {
        "route.method-count",
        "route.duplicate-method",
        "route.unknown-method",
        "route.conflict",
    } <= codes
