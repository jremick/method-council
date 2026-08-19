import json
from pathlib import Path

from method_council.evidence import file_digest
from method_council.release import verify_release_manifest
from method_council.schema import SchemaRegistry

REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _write_release(tmp_path, *, check_status="PASS", claimed_status="PASS", evidence=True):
    evidence_path = tmp_path / "evidence" / "unit-results.txt"
    evidence_path.parent.mkdir()
    evidence_path.write_text("42 tests passed", encoding="utf-8")
    bindings = []
    if evidence:
        bindings.append({"path": "evidence/unit-results.txt", "digest": file_digest(evidence_path)})
    report_path = tmp_path / "reports" / "tests.json"
    _write_json(
        report_path,
        {
            "schema_version": "0.1.0",
            "gate": "tests",
            "status": claimed_status,
            "checks": [{"id": "unit", "status": check_status, "evidence": bindings}],
        },
    )
    manifest_path = tmp_path / "manifest.json"
    _write_json(
        manifest_path,
        {
            "schema_version": "0.1.0",
            "candidate": "0.1.0-alpha.1",
            "generated_at": "2026-08-19T10:00:00Z",
            "artifacts": [
                {
                    "id": "test-gate",
                    "path": "reports/tests.json",
                    "digest": file_digest(report_path),
                    "gate": "tests",
                }
            ],
            "required_gates": ["tests"],
            "claimed_release_eligible": True,
        },
    )
    return manifest_path, report_path, evidence_path


def _verify(manifest, root):
    return verify_release_manifest(
        manifest, root=root, registry=SchemaRegistry(REPO_ROOT / "schemas")
    )


def test_release_eligibility_is_derived_from_bound_bytes(tmp_path):
    manifest, _, _ = _write_release(tmp_path)

    result = _verify(manifest, tmp_path)

    assert result["valid"]
    assert result["release_eligible"]
    assert result["status"] == "PASS"


def test_forged_top_level_pass_does_not_override_failed_check(tmp_path):
    manifest, _, _ = _write_release(tmp_path, check_status="FAIL", claimed_status="PASS")

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "FAIL"
    assert any(issue["code"] == "release.gate-claim-mismatch" for issue in result["issues"])


def test_top_level_pass_without_content_binding_is_incomplete(tmp_path):
    manifest, _, _ = _write_release(tmp_path, evidence=False)

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "INCOMPLETE"
    assert any(issue["code"] == "release.gate-check-unbound" for issue in result["issues"])


def test_manifest_digest_mismatch_is_a_hard_failure(tmp_path):
    manifest, report, _ = _write_release(tmp_path)
    report.write_text("{}", encoding="utf-8")

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "FAIL"
    assert any(issue["code"] == "release.artifact-digest-mismatch" for issue in result["issues"])


def test_bound_evidence_is_reread_and_tampering_is_detected(tmp_path):
    manifest, _, evidence = _write_release(tmp_path)
    evidence.write_text("forged output", encoding="utf-8")

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "ERROR"
    assert any(issue["code"] == "release.evidence-digest-mismatch" for issue in result["issues"])


def test_claimed_manifest_flag_is_not_release_authority(tmp_path):
    manifest, _, _ = _write_release(
        tmp_path, check_status="INCOMPLETE", claimed_status="INCOMPLETE"
    )

    result = _verify(manifest, tmp_path)

    assert result["claimed_release_eligible"] is True
    assert result["claim_matches_derived"] is False
    assert not result["release_eligible"]


def test_release_artifact_cannot_escape_repository_root(tmp_path):
    manifest, _, _ = _write_release(tmp_path)
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["artifacts"][0]["path"] = "../outside.json"
    manifest.write_text(json.dumps(document), encoding="utf-8")

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert any(issue["code"] == "release.path-escapes-root" for issue in result["issues"])


def test_gate_report_cannot_bind_itself_as_evidence(tmp_path):
    manifest, report, _ = _write_release(tmp_path)
    document = json.loads(report.read_text(encoding="utf-8"))
    document["checks"][0]["evidence"] = [
        {"path": "reports/tests.json", "digest": file_digest(report)}
    ]
    report.write_text(json.dumps(document), encoding="utf-8")
    manifest_document = json.loads(manifest.read_text(encoding="utf-8"))
    manifest_document["artifacts"][0]["digest"] = file_digest(report)
    manifest.write_text(json.dumps(manifest_document), encoding="utf-8")

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert any(issue["code"] == "release.evidence-self-reference" for issue in result["issues"])
