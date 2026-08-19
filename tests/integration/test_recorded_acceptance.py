from __future__ import annotations

import json
from pathlib import Path

import pytest

from method_council.acceptance import verify_acceptance
from method_council.run import verify_run

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = ROOT / "evidence" / "acceptance"
SOURCE_COMMIT = "7da73bbeef496cff9e31828e97a3fb400f44ead5"
SOURCE_TREE = "03af9cb01c76f454b7182e428b7de0d760051b50"
RUN_IDS = (
    "accept-architecture-storage-20260819",
    "accept-investigation-duplicates-20260819",
    "accept-release-missing-evidence-20260819",
    "accept-hostile-review-20260819",
)


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("run_id", RUN_IDS)
def test_recorded_acceptance_recomputes_from_bound_source(run_id: str):
    bundle = EVIDENCE_ROOT / run_id

    run_verdict = verify_run(bundle, root=ROOT)
    acceptance_verdict = verify_acceptance(bundle, root=ROOT)
    recorded_run_verdict = _read(bundle / "verification.json")
    recorded_acceptance_verdict = _read(bundle / "acceptance-verdict.json")
    host = _read(bundle / "host-execution.json")

    assert run_verdict == recorded_run_verdict
    assert acceptance_verdict == recorded_acceptance_verdict
    assert run_verdict["valid"] is True
    assert run_verdict["status"] == "INCOMPLETE"
    assert run_verdict["side_conditions"] == ["CORRELATED"]
    assert run_verdict["issues"] == []
    assert acceptance_verdict["valid"] is True
    assert acceptance_verdict["run_status"] == "INCOMPLETE"
    assert acceptance_verdict["run_side_conditions"] == ["CORRELATED"]
    assert acceptance_verdict["issues"] == []
    assert acceptance_verdict["attestation"] == "unsigned-local-recorder"
    assert acceptance_verdict["source_commit"] == SOURCE_COMMIT
    assert acceptance_verdict["source_tree"] == SOURCE_TREE

    assert host["attestation"] == "unsigned-local-recorder"
    assert host["authentication_observed"] == "chatgpt"
    assert host["source_commit"] == SOURCE_COMMIT
    assert host["source_tree"] == SOURCE_TREE
    assert host["source_mutations"] == []
    assert host["process_exit_code"] == 0
    assert host["timed_out"] is False
    assert host["event_stream_truncated"] is False
    assert host["event_counts"]["thread.started"] == 1
    assert host["event_counts"]["turn.started"] == 1
    assert host["event_counts"]["turn.completed"] == 1
    assert host["model_requested"] is None
    assert host["model_observed"] is None
    assert host["raw_prompt_persisted"] is False
    assert host["raw_event_stream_persisted"] is False


def test_recorded_architecture_does_not_launder_under_evidenced_passes():
    report = _read(EVIDENCE_ROOT / "accept-architecture-storage-20260819" / "report.json")
    statuses = {entry["method_id"]: entry["status"] for entry in report["method_ledger"]}

    assert statuses == {
        "key-assumptions": "PASS",
        "systems-trade-study": "INCOMPLETE",
        "failure-modes": "INCOMPLETE",
        "devils-advocacy": "INCOMPLETE",
    }


def test_public_acceptance_summaries_do_not_claim_a_recorded_pass():
    summaries = (
        ROOT / "README.md",
        ROOT / "docs" / "ACCEPTANCE.md",
        ROOT / "docs" / "CODEX_WORKFLOW.md",
        ROOT / "docs" / "COMPATIBILITY.md",
        ROOT / "docs" / "DELIVERY_BRIEF.md",
        EVIDENCE_ROOT / "README.md",
    )

    for summary in summaries:
        text = summary.read_text(encoding="utf-8")
        assert "One is `PASS`" not in text, summary
        assert "acceptance pending" not in text, summary
