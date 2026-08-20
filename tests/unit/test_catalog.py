import json
import shutil
from pathlib import Path

from method_council.catalog import load_catalog
from method_council.schema import SchemaRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]


def _method(identifier: str, **overrides):
    document = {
        "schema_version": "0.1.0",
        "id": identifier,
        "version": "0.1.0",
        "title": f"Method {identifier}",
        "summary": "A sufficiently long method summary used by deterministic unit tests.",
        "status": "validated",
        "family": "analytical",
        "provenance": {
            "class": "project-adaptation",
            "sources": [
                {
                    "id": "source.one",
                    "title": "Source one",
                    "publisher": "Publisher",
                    "url": "https://example.com/source",
                    "accessed": "2026-08-19",
                    "supports": ["The fixture procedure."],
                }
            ],
            "adaptation": "Adapted into a bounded deterministic fixture for this unit test.",
            "claim_limits": ["This fixture makes no external method-quality claim."],
        },
        "activities": ["analyse"],
        "capabilities": ["challenge"],
        "applicability": {
            "use_when": ["A deterministic fixture is required."],
            "avoid_when": ["Real method fidelity is being evaluated."],
            "prerequisites": [],
        },
        "requires_methods": [],
        "rigor": {
            level: {"enabled": True, "steps": ["inspect"], "minimum_evidence_refs": 1}
            for level in ("rapid", "standard", "intensive")
        },
        "procedure": [
            {
                "id": "inspect",
                "title": "Inspect evidence",
                "instruction": "Inspect the supplied evidence and record bounded findings.",
                "required": True,
            }
        ],
        "result_schema": "schemas/method-result.schema.json",
        "evidence_rules": {"minimum_references": 1, "allow_unreferenced_assumptions": True},
        "complements": [],
        "conflicts": [],
        "failure_modes": ["Evidence may be incomplete or unsuitable for the method."],
    }
    document.update(overrides)
    return document


def _profile(methods):
    return {
        "schema_version": "0.1.0",
        "id": "analysis-profile",
        "version": "0.1.0",
        "title": "Analysis profile",
        "activity": "analyse",
        "rigor": "rapid",
        "methods": methods,
        "challenge_required": True,
        "status": "validated",
    }


def _write_catalog(tmp_path, methods, profile_methods):
    (tmp_path / "methods").mkdir()
    (tmp_path / "profiles").mkdir()
    (tmp_path / "schemas").mkdir()
    shutil.copy(
        REPO_ROOT / "schemas" / "method-result.schema.json",
        tmp_path / "schemas" / "method-result.schema.json",
    )
    for method in methods:
        directory = tmp_path / "methods" / method["id"]
        directory.mkdir()
        (directory / "method.json").write_text(json.dumps(method), encoding="utf-8")
    (tmp_path / "profiles" / "analysis-profile.json").write_text(
        json.dumps(_profile(profile_methods)), encoding="utf-8"
    )


def test_real_catalog_covers_all_method_families():
    catalog = load_catalog(REPO_ROOT, SchemaRegistry(REPO_ROOT / "schemas"))

    assert {method["family"] for method in catalog.methods.values()} == {
        "analytical",
        "interpretive",
        "normative",
        "pragmatic",
        "participatory",
    }


def test_valid_catalog_passes_semantic_validation(tmp_path):
    _write_catalog(tmp_path, [_method("method-a")], ["method-a"])

    catalog = load_catalog(tmp_path, SchemaRegistry(REPO_ROOT / "schemas"))

    assert catalog.issues == []


def test_unknown_relationship_and_required_step_omission_fail(tmp_path):
    method = _method("method-a", complements=["missing-method"])
    method["rigor"]["rapid"]["steps"] = []
    _write_catalog(tmp_path, [method], ["method-a"])

    catalog = load_catalog(tmp_path, SchemaRegistry(REPO_ROOT / "schemas"))
    codes = {issue.code for issue in catalog.issues}

    assert "method.unknown-complement" in codes
    assert "method.rigor-missing-required-step" in codes


def test_structurally_invalid_record_is_not_loaded(tmp_path):
    method = _method("method-a")
    method["provenance"]["sources"][0]["accessed"] = "yesterday"
    _write_catalog(tmp_path, [method], ["method-a"])

    catalog = load_catalog(tmp_path, SchemaRegistry(REPO_ROOT / "schemas"))

    assert "method-a" not in catalog.methods
    assert any(issue.code == "schema.invalid" for issue in catalog.issues)


def test_unknown_method_family_is_rejected(tmp_path):
    _write_catalog(tmp_path, [_method("method-a", family="rhetorical")], ["method-a"])

    catalog = load_catalog(tmp_path, SchemaRegistry(REPO_ROOT / "schemas"))

    assert "method-a" not in catalog.methods
    assert any(issue.code == "schema.invalid" for issue in catalog.issues)


def test_profile_requires_a_challenge_capability(tmp_path):
    method = _method("method-a", capabilities=["evidence-assessment"])
    _write_catalog(tmp_path, [method], ["method-a"])

    catalog = load_catalog(tmp_path, SchemaRegistry(REPO_ROOT / "schemas"))

    assert any(issue.code == "profile.route.challenge-missing" for issue in catalog.issues)


def test_unknown_and_self_required_method_are_rejected(tmp_path):
    method = _method("method-a", requires_methods=["method-a", "missing-method"])
    _write_catalog(tmp_path, [method], ["method-a"])

    catalog = load_catalog(tmp_path, SchemaRegistry(REPO_ROOT / "schemas"))
    codes = {issue.code for issue in catalog.issues}

    assert "method.unknown-required-method" in codes
    assert "method.self-reference" in codes
