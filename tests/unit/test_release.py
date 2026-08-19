import json
from pathlib import Path

import pytest

from method_council import release_checks
from method_council.documents import MAX_DOCUMENT_BYTES
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


def test_arbitrary_bound_bytes_and_self_asserted_pass_cannot_make_release_eligible(tmp_path):
    manifest, _, _ = _write_release(tmp_path)

    result = _verify(manifest, tmp_path)

    assert not result["valid"]
    assert not result["release_eligible"]
    assert result["status"] == "INCOMPLETE"
    assert result["gate_statuses"] == {"tests": "INCOMPLETE"}
    assert result["content_valid"]
    assert result["content_status"] == "PASS"
    assert result["content_gate_statuses"] == {"tests": "PASS"}
    assert any(issue["code"] == "release.gate-unattested" for issue in result["issues"])


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


def test_bound_evidence_cannot_be_a_symlink(tmp_path):
    manifest, _, evidence = _write_release(tmp_path)
    target = tmp_path / "evidence" / "actual-results.txt"
    target.write_bytes(evidence.read_bytes())
    evidence.unlink()
    evidence.symlink_to(target)

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "ERROR"
    assert any(issue["code"] == "release.path-symlink" for issue in result["issues"])


def test_gate_report_artifact_cannot_be_a_symlink(tmp_path):
    manifest, report, _ = _write_release(tmp_path)
    target = tmp_path / "reports" / "actual-tests.json"
    target.write_bytes(report.read_bytes())
    report.unlink()
    report.symlink_to(target)

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "ERROR"
    assert any(issue["code"] == "release.path-symlink" for issue in result["issues"])


def test_top_level_manifest_cannot_be_a_symlink(tmp_path):
    manifest, _, _ = _write_release(tmp_path)
    linked_manifest = tmp_path / "linked-manifest.json"
    linked_manifest.symlink_to(manifest)

    result = _verify(linked_manifest, tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "ERROR"
    issue = next(issue for issue in result["issues"] if issue["code"] == "release.manifest-parse")
    assert "symlink" in issue["message"]


@pytest.mark.skipif(not Path("/dev/zero").exists(), reason="requires a POSIX zero device")
def test_top_level_manifest_device_fails_closed_without_reading(tmp_path):
    result = _verify(Path("/dev/zero"), tmp_path)

    assert not result["release_eligible"]
    assert result["status"] == "ERROR"
    issue = next(issue for issue in result["issues"] if issue["code"] == "release.manifest-parse")
    assert "not a regular file" in issue["message"]


@pytest.mark.parametrize(
    ("input_name", "issue_code"),
    [
        ("manifest", "release.manifest-parse"),
        ("report", "release.artifact-read"),
        ("evidence", "release.evidence-read"),
    ],
)
def test_every_release_input_is_bounded(tmp_path, input_name, issue_code):
    manifest, report, evidence = _write_release(tmp_path)
    path = {"manifest": manifest, "report": report, "evidence": evidence}[input_name]
    with path.open("wb") as handle:
        handle.truncate(MAX_DOCUMENT_BYTES + 1)

    result = _verify(manifest, tmp_path)

    assert not result["release_eligible"]
    issue = next(issue for issue in result["issues"] if issue["code"] == issue_code)
    assert "exceeds" in issue["message"]


def test_registered_local_alpha_gate_is_rerun_and_can_be_eligible(tmp_path, monkeypatch):
    check = release_checks.ReleaseCheck("smoke", ("python", "-c", "raise SystemExit(0)"), 30)
    monkeypatch.setattr(release_checks, "LOCAL_ALPHA_CHECKS", (check,))
    monkeypatch.setattr(release_checks, "_git_head", lambda root: "abc123")

    result = release_checks.build_local_alpha_evidence(
        tmp_path, tmp_path / "runs" / "release" / "candidate"
    )
    verdict = _verify(tmp_path / result["manifest"], tmp_path)

    assert result["valid"]
    assert verdict["valid"]
    assert verdict["release_eligible"]
    assert verdict["status"] == "PASS"
    assert verdict["gate_statuses"] == {"local-alpha": "PASS"}
    assert verdict["issues"] == []


def test_registered_gate_rejects_candidate_drift(tmp_path, monkeypatch):
    check = release_checks.ReleaseCheck("smoke", ("python", "-c", "raise SystemExit(0)"), 30)
    monkeypatch.setattr(release_checks, "LOCAL_ALPHA_CHECKS", (check,))
    monkeypatch.setattr(release_checks, "_git_head", lambda root: "candidate-a")
    result = release_checks.build_local_alpha_evidence(
        tmp_path, tmp_path / "runs" / "release" / "candidate"
    )
    monkeypatch.setattr(release_checks, "_git_head", lambda root: "candidate-b")

    verdict = _verify(tmp_path / result["manifest"], tmp_path)

    assert not verdict["valid"]
    assert not verdict["release_eligible"]
    assert verdict["status"] == "ERROR"
    assert any(issue["code"] == "release.candidate-mismatch" for issue in verdict["issues"])


def test_release_evidence_output_rejects_symlink_components(tmp_path):
    release_root = tmp_path / "runs" / "release"
    release_root.mkdir(parents=True)
    target = tmp_path / "elsewhere"
    target.mkdir()
    linked = release_root / "linked"
    linked.symlink_to(target, target_is_directory=True)

    with pytest.raises(ValueError, match="must not contain symlinks"):
        release_checks.build_local_alpha_evidence(tmp_path, linked / "candidate")
