from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

from method_council.acceptance import (
    build_acceptance_prompt,
    expected_model_artifacts,
    extract_git_snapshot,
    git_source_identity,
    task_spec,
    verify_acceptance,
)
from method_council.evidence import content_digest, file_digest
from method_council.run import verify_run

ROOT = Path(__file__).resolve().parents[2]
RECORDED = ROOT / "evidence" / "acceptance" / "accept-architecture-storage-20260819"
RUN_ID = "accept-architecture-storage-20260819"
TASK_ID = "architecture-storage"


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_valid_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / RUN_ID
    profile, task_path = task_spec(TASK_ID)
    expected = expected_model_artifacts(ROOT, profile)
    for relative in expected:
        destination = bundle / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(RECORDED / relative, destination)
    run_path = bundle / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    run["route"].update(
        {
            "profile_id": profile,
            "allow_preview": True,
            "challenge_required": True,
        }
    )
    _write(run_path, run)
    for relative in expected:
        if not relative.startswith("method-results/"):
            continue
        result_path = bundle / relative
        result = json.loads(result_path.read_text(encoding="utf-8"))
        result["status"] = "INCOMPLETE"
        _write(result_path, result)
    report_path = bundle / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["status"] = "INCOMPLETE"
    report["method_ledger"] = [
        {
            "method_id": method_id,
            "status": "INCOMPLETE",
            "result_digest": file_digest(bundle / f"method-results/{method_id}.json"),
        }
        for method_id in run["methods"]
    ]
    _write(report_path, report)

    source = git_source_identity(ROOT)
    verification_root = tmp_path / "verification-source"
    extract_git_snapshot(ROOT, source["source_commit"], verification_root)
    verification_run = verification_root / "runs" / "acceptance" / RUN_ID
    for relative in expected:
        destination = verification_run / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bundle / relative, destination)
    verification = verify_run(verification_run, root=verification_root)
    assert verification["valid"] is True
    _write(bundle / "verification.json", verification)
    recorded_run_path = f"runs/acceptance/{RUN_ID}"
    prompt = build_acceptance_prompt(TASK_ID, profile, task_path, recorded_run_path, RUN_ID)
    sequence = ["thread.started", "turn.started", "item.completed", "turn.completed"]
    host = {
        "schema_version": "0.1.0",
        "kind": "codex-subscription-acceptance-evidence",
        "attestation": "unsigned-local-recorder",
        "run_id": RUN_ID,
        "task": TASK_ID,
        "profile": profile,
        "run_path": recorded_run_path,
        "source_commit": source["source_commit"],
        "source_tree": source["source_tree"],
        "source_manifest_digest": source["source_manifest_digest"],
        "source_mutations": [],
        "task_digest": file_digest(ROOT / task_path),
        "prompt_digest": content_digest(prompt),
        "model_artifact_ledger": [
            {"path": relative, "digest": file_digest(bundle / relative)} for relative in expected
        ],
        "raw_prompt_persisted": False,
        "raw_event_stream_persisted": False,
        "codex_cli_version": "codex-cli test",
        "codex_executable": {
            "command": "codex",
            "resolved_basename": "codex",
            "resolved_path_digest": content_digest("/test/codex"),
            "executable_digest": content_digest("test-codex-bytes"),
        },
        "authentication_observed": "chatgpt",
        "model_requested": None,
        "model_observed": None,
        "uv_sync": {
            "command": ["uv", "sync", "--frozen", "--all-groups"],
            "exit_code": 0,
        },
        "started_at": "2026-08-19T10:00:00Z",
        "completed_at": "2026-08-19T10:00:10Z",
        "duration_seconds": 10.0,
        "process_exit_code": 0,
        "timed_out": False,
        "event_counts": dict(sorted(Counter(sequence).items())),
        "event_sequence": sequence,
        "non_json_line_count": 0,
        "final_message_digest": content_digest("complete"),
        "verification_digest": file_digest(bundle / "verification.json"),
        "verification_valid": True,
        "verification_status": verification["status"],
    }
    _write(bundle / "host-execution.json", host)
    verdict = verify_acceptance(bundle, root=ROOT, require_recorded_verdict=False)
    assert verdict["valid"] is True, verdict
    _write(bundle / "acceptance-verdict.json", verdict)
    return bundle


def test_acceptance_bundle_is_recomputed_against_exact_source_commit(tmp_path):
    bundle = _build_valid_bundle(tmp_path)

    verdict = verify_acceptance(bundle, root=ROOT)

    assert verdict["valid"] is True
    assert verdict["issues"] == []
    assert verdict["attestation"] == "unsigned-local-recorder"
    assert verdict["host_execution_digest"] == file_digest(bundle / "host-execution.json")


def test_swapped_host_execution_is_rejected(tmp_path):
    bundle = _build_valid_bundle(tmp_path)
    swapped = tmp_path / "accept-swapped-host-20260819"
    shutil.copytree(bundle, swapped)

    verdict = verify_acceptance(swapped, root=ROOT)

    assert verdict["valid"] is False
    assert any(issue["code"] == "acceptance.directory-run-id" for issue in verdict["issues"])


def test_forged_host_verification_status_is_rejected(tmp_path):
    bundle = _build_valid_bundle(tmp_path)
    host_path = bundle / "host-execution.json"
    host = json.loads(host_path.read_text(encoding="utf-8"))
    host["verification_status"] = "ERROR"
    _write(host_path, host)

    verdict = verify_acceptance(bundle, root=ROOT)

    assert verdict["valid"] is False
    assert any(
        issue["code"] == "acceptance.verification-status-mismatch" for issue in verdict["issues"]
    )


def test_recorded_tracked_source_mutation_invalidates_acceptance(tmp_path):
    bundle = _build_valid_bundle(tmp_path)
    host_path = bundle / "host-execution.json"
    host = json.loads(host_path.read_text(encoding="utf-8"))
    host["source_mutations"] = [{"path": "README.md", "change": "content-changed"}]
    _write(host_path, host)

    verdict = verify_acceptance(bundle, root=ROOT)

    assert verdict["valid"] is False
    assert any(issue["code"] == "acceptance.source-mutations" for issue in verdict["issues"])
