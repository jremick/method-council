import json
from pathlib import Path

from method_council.cli import build_parser, main

REPO_ROOT = Path(__file__).resolve().parents[2]


def _result(method_id: str, status: str = "PASS") -> dict:
    return {
        "schema_version": "0.1.0",
        "run_id": "run-12345678",
        "method_id": method_id,
        "method_version": "0.1.0",
        "rigor": "rapid",
        "status": status,
        "side_conditions": ["CORRELATED"],
        "completed_steps": ["inspect"],
        "findings": [],
        "alternatives": [],
        "confidence": {
            "band": "not-assessed",
            "basis": "No semantic confidence was assessed.",
        },
        "change_conditions": [],
        "errors": [],
        "execution": {
            "adapter": "codex",
            "provider_state": "verified",
            "model_requested": None,
            "model_observed": None,
            "external_api_calls": False,
            "correlation_group": "codex-test",
        },
    }


def test_frozen_wave_one_commands_are_exposed():
    parser = build_parser()
    choices = next(
        action.choices
        for action in parser._actions  # noqa: SLF001 - argparse exposes no public accessor
        if getattr(action, "choices", None)
    )

    assert set(choices) == {
        "validate",
        "route",
        "prepare",
        "check",
        "aggregate",
        "verify-run",
        "verify-release",
    }


def test_check_emits_json_and_nonzero_for_invalid_document(tmp_path, capsys):
    document = tmp_path / "provider.json"
    document.write_text(
        json.dumps(
            {
                "schema_version": "0.1.0",
                "adapter": "codex",
                "state": "verified",
                "checked_at": "not-a-date",
                "checks": [],
                "external_call_performed": False,
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "check",
            str(document),
            "--schema",
            "provider-status",
            "--root",
            str(REPO_ROOT),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert not payload["valid"]
    assert any(issue["path"] == "/checked_at" for issue in payload["issues"])


def test_aggregate_emits_only_derived_envelope_and_content_ledger(tmp_path, capsys):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(_result("method-a")), encoding="utf-8")
    second.write_text(json.dumps(_result("method-b", "INCOMPLETE")), encoding="utf-8")

    exit_code = main(["aggregate", str(first), str(second), "--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["valid"]
    assert payload["status"] == "INCOMPLETE"
    assert payload["side_conditions"] == ["CORRELATED"]
    assert len(payload["method_ledger"]) == 2
    assert all(entry["result_digest"].startswith("sha256:") for entry in payload["method_ledger"])
    assert "judgment" not in payload


def test_aggregate_rejects_duplicate_method_passes(tmp_path, capsys):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text(json.dumps(_result("method-a")), encoding="utf-8")
    second.write_text(json.dumps(_result("method-a")), encoding="utf-8")

    exit_code = main(["aggregate", str(first), str(second), "--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "ERROR"
    assert any(issue["code"] == "aggregate.duplicate-method" for issue in payload["issues"])
