from __future__ import annotations

import json
from pathlib import Path

import pytest

from method_council.evaluation import evaluate_method_suite, write_evaluation_report

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "evals" / "methods" / "inventory.json"


def test_method_screen_covers_catalog_and_remains_incomplete():
    report = evaluate_method_suite(ROOT, INVENTORY)

    assert report["valid"] is True
    assert report["overall_status"] == "INCOMPLETE"
    assert report["totals"] == {
        "catalog_methods": 24,
        "inventoried_methods": 8,
        "unevaluated_methods": 16,
        "structurally_valid": 8,
        "procedure_complete": 6,
        "correlated_semantic_screen_met": 8,
        "baseline_delta_measured": 0,
        "independently_reviewed": 0,
    }
    assert report["unevaluated_methods"] == [
        "adaptive-management",
        "capability-distribution-review",
        "causal-factors",
        "concept-clarification",
        "contextual-interpretation",
        "human-centred-design-inquiry",
        "outside-in",
        "outside-view",
        "pragmatic-clarification",
        "reflective-equilibrium",
        "reflexive-thematic-analysis",
        "rights-proportionality-review",
        "speech-act-analysis",
        "structured-expert-elicitation",
        "theory-of-change",
        "value-sensitive-inquiry",
    ]
    assert report["issues"] == []
    for method in report["methods"]:
        assert method["structural"]["valid"] is True
        assert method["correlated_semantic_screen"]["status"] == "MET"
        assert method["usefulness"]["evaluation_status"] == "INCOMPLETE"
        assert "missing-sample-types:adversarial,edge" in method["usefulness"]["blockers"]
        assert "no-blinded-no-method-baseline-comparison" in method["usefulness"]["blockers"]
        assert "no-independent-practitioner-review" in method["usefulness"]["blockers"]

    incomplete_procedures = {
        item["method_id"]
        for item in report["methods"]
        if not item["structural"]["procedure_complete"]
    }
    assert incomplete_procedures == {"competing-hypotheses", "systems-trade-study"}


def test_checked_in_report_matches_recomputed_report():
    expected = evaluate_method_suite(ROOT, INVENTORY)
    recorded = json.loads(
        (ROOT / "evals" / "methods" / "screening-report.json").read_text(encoding="utf-8")
    )

    assert recorded == expected


def test_evaluation_report_refuses_noncanonical_output():
    with pytest.raises(ValueError, match="output must be the canonical report path"):
        write_evaluation_report(ROOT, INVENTORY, Path("../outside-report.json"))
