from __future__ import annotations

import json
from pathlib import Path

import pytest

from method_council.run import verify_run

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = ROOT / "evidence" / "acceptance"

CASES = [
    (
        "accept-architecture-storage-20260819",
        "PASS",
        ["CORRELATED"],
        4,
    ),
    (
        "accept-investigation-duplicates-20260819",
        "INCOMPLETE",
        ["CORRELATED"],
        3,
    ),
    (
        "accept-release-missing-evidence-20260819",
        "INCOMPLETE",
        ["CORRELATED", "SKIPPED"],
        3,
    ),
    (
        "accept-hostile-review-20260819",
        "INCOMPLETE",
        ["DEGRADED", "CORRELATED"],
        3,
    ),
]


@pytest.mark.parametrize(("bundle", "status", "conditions", "method_count"), CASES)
def test_recorded_codex_bundle_reverifies(
    bundle: str,
    status: str,
    conditions: list[str],
    method_count: int,
) -> None:
    bundle_path = EVIDENCE_ROOT / bundle
    verdict = verify_run(bundle_path, root=ROOT)
    execution = json.loads((bundle_path / "host-execution.json").read_text(encoding="utf-8"))

    assert verdict["valid"] is True
    assert verdict["issues"] == []
    assert verdict["status"] == status
    assert verdict["side_conditions"] == conditions
    assert len(verdict["checked_methods"]) == method_count
    assert verdict == json.loads((bundle_path / "verification.json").read_text(encoding="utf-8"))

    assert execution["kind"] == "codex-subscription-acceptance-evidence"
    assert execution["authentication_observed"] == "chatgpt"
    assert execution["process_exit_code"] == 0
    assert execution["timed_out"] is False
    assert execution["raw_prompt_persisted"] is False
    assert execution["raw_event_stream_persisted"] is False
    assert execution["model_requested"] is None
    assert execution["model_observed"] is None
    assert execution["verification_valid"] is True
    assert execution["verification_status"] == status
