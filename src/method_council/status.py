"""Primary-status aggregation with frozen precedence."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from typing import Any

PRIMARY_STATUSES = ("PASS", "INCOMPLETE", "ERROR", "FAIL")
STATUS_PRECEDENCE = {status: rank for rank, status in enumerate(PRIMARY_STATUSES)}
SIDE_CONDITIONS = ("DEGRADED", "CORRELATED", "SKIPPED")


def aggregate_status(statuses: Iterable[str]) -> str:
    """Return the strongest primary status; no inputs is ``INCOMPLETE``."""

    values = list(statuses)
    if not values:
        return "INCOMPLETE"
    unknown = sorted(set(values) - set(PRIMARY_STATUSES))
    if unknown:
        raise ValueError(f"unknown primary status: {', '.join(unknown)}")
    return max(values, key=STATUS_PRECEDENCE.__getitem__)


def aggregate_results(results: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate validated method results without synthesising their semantics."""

    result_list = list(results)
    statuses = [str(result["status"]) for result in result_list]
    conditions = {
        str(condition) for result in result_list for condition in result.get("side_conditions", [])
    }
    unknown_conditions = conditions - set(SIDE_CONDITIONS)
    if unknown_conditions:
        raise ValueError(f"unknown side condition: {', '.join(sorted(unknown_conditions))}")
    counts = Counter(statuses)
    return {
        "status": aggregate_status(statuses),
        "side_conditions": [condition for condition in SIDE_CONDITIONS if condition in conditions],
        "method_count": len(result_list),
        "counts": {status: counts.get(status, 0) for status in reversed(PRIMARY_STATUSES)},
    }
