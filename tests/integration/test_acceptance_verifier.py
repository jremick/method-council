from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

import pytest

from method_council.acceptance import (
    TASKS,
    build_acceptance_prompt,
    expected_model_artifacts,
    extract_git_snapshot,
    git_source_identity,
    task_spec,
    verify_acceptance,
)
from method_council.catalog import load_catalog
from method_council.evidence import content_digest, file_digest
from method_council.run import prepare_run, verify_run

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "accept-architecture-storage-20260819"
TASK_ID = "architecture-storage"


def test_forecast_task_closes_initial_method_coverage() -> None:
    profile, task_path = task_spec("forecast-plugin-ecosystem")

    assert profile == "intensive-forecast"
    assert task_path == "evals/acceptance/forecast-plugin-ecosystem.md"
    assert expected_model_artifacts(ROOT, profile) == [
        "run.json",
        "report.json",
        "method-results/evidence-quality.json",
        "method-results/key-assumptions.json",
        "method-results/alternative-futures.json",
        "method-results/indicators-signposts.json",
        "method-results/devils-advocacy.json",
    ]
    host_schema = json.loads(
        (ROOT / "schemas" / "host-execution.schema.json").read_text(encoding="utf-8")
    )
    assert set(host_schema["properties"]["task"]["enum"]) == set(TASKS)


def _write(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_valid_bundle(tmp_path: Path) -> Path:
    bundle = tmp_path / RUN_ID
    profile, task_path = task_spec(TASK_ID)
    source = git_source_identity(ROOT)
    verification_root = tmp_path / "verification-source"
    extract_git_snapshot(ROOT, source["source_commit"], verification_root)
    verification_run = verification_root / "runs" / "acceptance" / RUN_ID
    question = (verification_root / task_path).read_text(encoding="utf-8")
    prepared = prepare_run(
        root=verification_root,
        run_dir=verification_run,
        question=question,
        catalog=load_catalog(verification_root),
        profile_id=profile,
        activity=None,
        rigor=None,
        method_ids=[],
        allow_preview=True,
        require_challenge=False,
        evidence_specs=[f"case={task_path}"],
        evidence_kind="repository",
        adapter="codex",
        provider_state="verified",
        model_requested=None,
        model_observed=None,
        external_api_calls=False,
        correlation_group=f"codex-{RUN_ID}",
    )
    assert prepared["valid"] is True
    run = prepared["run"]
    result_paths: dict[str, Path] = {}
    for method_id in run["methods"]:
        result = {
            "schema_version": "0.1.0",
            "run_id": RUN_ID,
            "method_id": method_id,
            "method_version": "0.1.0",
            "rigor": "standard",
            "status": "INCOMPLETE",
            "side_conditions": ["CORRELATED"],
            "completed_steps": [],
            "findings": [],
            "alternatives": [],
            "method_artifact": {},
            "confidence": {
                "band": "not-assessed",
                "basis": "Synthetic verifier fixture only.",
            },
            "change_conditions": [],
            "errors": [],
            "execution": run["host"],
        }
        result_path = verification_run / "method-results" / f"{method_id}.json"
        _write(result_path, result)
        result_paths[method_id] = result_path
    report = {
        "schema_version": "0.1.0",
        "run_id": RUN_ID,
        "status": "INCOMPLETE",
        "side_conditions": ["CORRELATED"],
        "judgment": "Synthetic verifier fixture remains incomplete.",
        "decision_boundary": "Acceptance contract checks only.",
        "next_action": "Retain the incomplete status.",
        "key_judgments": [],
        "strongest_alternative": "No model judgment was produced.",
        "assumptions": [],
        "unknowns": ["No live model execution occurred."],
        "dissent": [],
        "checkpoint": {"trigger": "Fixture changes", "indicators": ["Digest changes"]},
        "method_ledger": [
            {
                "method_id": method_id,
                "status": "INCOMPLETE",
                "result_digest": file_digest(result_paths[method_id]),
            }
            for method_id in run["methods"]
        ],
        "limitations": ["This is structural test data, not execution evidence."],
    }
    _write(verification_run / "report.json", report)
    verification = verify_run(verification_run, root=verification_root)
    assert verification["valid"] is True
    expected = expected_model_artifacts(verification_root, profile)
    for relative in expected:
        destination = bundle / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(verification_run / relative, destination)
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
        "event_stream_truncated": False,
        "descendant_cleanup": {
            "mechanism": "process-group-plus-polled-ps-ancestry",
            "assurance": "best-effort-unverified",
            "observer_state": "completed",
            "poll_count": 3,
            "observed_count": 0,
            "terminated_count": 0,
            "observed_survivor_count": 0,
            "copy_out_allowed": True,
            "limitation": "Synthetic structural fixture; not execution authenticity.",
        },
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


def test_unestablished_descendant_cleanup_invalidates_acceptance(tmp_path):
    bundle = _build_valid_bundle(tmp_path)
    host_path = bundle / "host-execution.json"
    host = json.loads(host_path.read_text(encoding="utf-8"))
    host["descendant_cleanup"].update(
        {
            "observer_state": "error",
            "observed_survivor_count": 1,
            "copy_out_allowed": False,
        }
    )
    _write(host_path, host)

    verdict = verify_acceptance(bundle, root=ROOT)

    assert verdict["valid"] is False
    assert any(
        issue["code"] == "acceptance.descendant-cleanup-observer-state"
        for issue in verdict["issues"]
    )


def test_current_runner_source_requires_explicit_unverified_cleanup_record(tmp_path):
    bundle = _build_valid_bundle(tmp_path)
    host_path = bundle / "host-execution.json"
    host = json.loads(host_path.read_text(encoding="utf-8"))
    del host["descendant_cleanup"]
    _write(host_path, host)

    verdict = verify_acceptance(bundle, root=ROOT)

    assert verdict["valid"] is False
    assert any(
        issue["code"] == "acceptance.descendant-cleanup-missing" for issue in verdict["issues"]
    )


@pytest.mark.parametrize(
    ("artifact", "issue_code"),
    [
        ("host-execution.json", "acceptance.host-invalid"),
        ("verification.json", "acceptance.verification-invalid"),
        ("acceptance-verdict.json", "acceptance.verdict-invalid"),
    ],
)
def test_top_level_acceptance_symlink_is_rejected_without_reading_device(
    tmp_path, artifact, issue_code
):
    bundle = _build_valid_bundle(tmp_path)
    target = bundle / artifact
    target.unlink()
    target.symlink_to("/dev/zero")

    verdict = verify_acceptance(bundle, root=ROOT)

    assert verdict["valid"] is False
    assert any(issue["code"] == issue_code for issue in verdict["issues"])
