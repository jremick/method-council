import pytest

from method_council.status import aggregate_results, aggregate_status


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ([], "INCOMPLETE"),
        (["PASS"], "PASS"),
        (["PASS", "INCOMPLETE"], "INCOMPLETE"),
        (["FAIL", "ERROR", "INCOMPLETE", "PASS"], "FAIL"),
        (["PASS", "ERROR"], "ERROR"),
    ],
)
def test_status_precedence(statuses, expected):
    assert aggregate_status(statuses) == expected


def test_unknown_status_is_rejected():
    with pytest.raises(ValueError, match="unknown primary status"):
        aggregate_status(["PASS", "DEGRADED"])


def test_results_preserve_side_conditions_without_upgrading_status():
    result = aggregate_results(
        [
            {"status": "PASS", "side_conditions": ["CORRELATED"]},
            {"status": "INCOMPLETE", "side_conditions": ["DEGRADED", "SKIPPED"]},
        ]
    )

    assert result == {
        "status": "INCOMPLETE",
        "side_conditions": ["DEGRADED", "CORRELATED", "SKIPPED"],
        "method_count": 2,
        "counts": {"FAIL": 0, "ERROR": 0, "INCOMPLETE": 1, "PASS": 1},
    }
