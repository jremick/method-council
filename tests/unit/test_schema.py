from pathlib import Path

from method_council.schema import SchemaRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_registry_schemas_are_valid():
    registry = SchemaRegistry(REPO_ROOT / "schemas")

    assert registry.validate_registry() == []


def test_format_checker_rejects_invalid_date_time():
    registry = SchemaRegistry(REPO_ROOT / "schemas")
    provider_status = {
        "schema_version": "0.1.0",
        "adapter": "codex",
        "state": "verified",
        "checked_at": "not-a-date",
        "checks": [],
        "external_call_performed": False,
    }

    issues = registry.validate(provider_status, "provider-status")

    assert any(issue.path == "/checked_at" and "date-time" in issue.message for issue in issues)


def test_format_checker_rejects_invalid_source_uri():
    registry = SchemaRegistry(REPO_ROOT / "schemas")
    source = {
        "schema_version": "0.1.0",
        "id": "test-method",
        "version": "0.1.0",
        "title": "Test method",
        "summary": "A sufficiently long summary for this test method.",
        "status": "preview",
        "provenance": {
            "class": "project-adaptation",
            "sources": [
                {
                    "id": "source.one",
                    "title": "Source",
                    "publisher": "Publisher",
                    "url": "not a uri",
                    "accessed": "2026-08-19",
                    "supports": ["Procedure"],
                }
            ],
            "adaptation": "Adapted into a deterministic test method record.",
            "claim_limits": ["This fixture makes no external quality claim."],
        },
        "activities": ["analyse"],
        "applicability": {
            "use_when": ["Testing"],
            "avoid_when": ["Not testing"],
            "prerequisites": [],
        },
        "rigor": {
            level: {"enabled": True, "steps": ["inspect"], "minimum_evidence_refs": 1}
            for level in ("rapid", "standard", "intensive")
        },
        "procedure": [
            {
                "id": "inspect",
                "title": "Inspect",
                "instruction": "Inspect the supplied evidence for the test.",
                "required": True,
            }
        ],
        "result_schema": "schemas/method-result.schema.json",
        "evidence_rules": {"minimum_references": 1, "allow_unreferenced_assumptions": True},
        "complements": [],
        "conflicts": [],
        "failure_modes": ["Insufficient evidence for a reliable result."],
    }

    issues = registry.validate(source, "method")

    assert any(issue.path.endswith("/url") and "uri" in issue.message for issue in issues)
