import json
import shutil
from pathlib import Path

import pytest

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


def _run(methods: list[str] | None = None) -> dict:
    host = {
        "adapter": "codex",
        "provider_state": "verified",
        "model_requested": None,
        "model_observed": None,
        "external_api_calls": False,
        "correlation_group": "codex-test",
    }
    return {
        "schema_version": "0.1.0",
        "run_id": "run-12345678",
        "created_at": "2026-08-19T10:00:00Z",
        "activity": "analyse",
        "rigor": "rapid",
        "question_digest": "sha256:" + "0" * 64,
        "raw_prompt_persisted": False,
        "methods": methods or ["key-assumptions"],
        "evidence": [
            {
                "id": "case",
                "kind": "repository",
                "digest": "sha256:" + "1" * 64,
            }
        ],
        "route": {
            "source": "user-explicit",
            "validated": True,
            "profile_id": None,
            "allow_preview": True,
            "challenge_required": False,
            "why": ["CLI contract fixture."],
        },
        "host": host,
    }


def _valid_key_assumptions_pass(run: dict) -> dict:
    result = _result("key-assumptions")
    result["execution"] = run["host"]
    result["completed_steps"] = [
        "state-judgment",
        "enumerate",
        "challenge",
        "bound-impact",
    ]
    result["findings"] = [
        {
            "id": "finding-1",
            "type": "fact",
            "statement": "The bounded case evidence is present.",
            "evidence_refs": ["case"],
            "method_step": "state-judgment",
            "counterevidence_refs": [],
        }
    ]
    result["method_artifact"] = {
        "judgment": "The fixture is bounded.",
        "scope": "CLI contract test only.",
        "assumptions": ["The fixture remains unchanged."],
        "challenges": ["Check the fixture digest."],
        "counterevidence": ["No counterevidence is supplied."],
        "failure_impacts": ["A changed fixture invalidates the finding."],
        "revised_judgment": "Re-evaluate if the fixture changes.",
    }
    return result


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
        "verify-acceptance",
        "verify-release",
    }


def test_prepare_accepts_repository_multi_model_execution_plan(tmp_path, capsys):
    for name in ("schemas", "methods", "profiles"):
        shutil.copytree(REPO_ROOT / name, tmp_path / name)
    (tmp_path / "question.md").write_text("Review this bounded question.\n", encoding="utf-8")
    plan = {
        "mode": "multi-model",
        "assignments": [
            {
                "methods": ["evidence-quality"],
                "execution": {
                    "adapter": "codex",
                    "provider_state": "verified",
                    "model_requested": "gpt-5.5",
                    "model_observed": "gpt-5.5",
                    "external_api_calls": False,
                    "correlation_group": None,
                },
            },
            {
                "methods": ["key-assumptions"],
                "execution": {
                    "adapter": "gemini",
                    "provider_state": "preview",
                    "model_requested": "gemini-pro",
                    "model_observed": None,
                    "external_api_calls": True,
                    "correlation_group": None,
                },
            },
        ],
    }
    (tmp_path / "plan.json").write_text(json.dumps(plan), encoding="utf-8")

    exit_code = main(
        [
            "prepare",
            "runs/run-cli-multi",
            "--root",
            str(tmp_path),
            "--profile",
            "rapid-analysis",
            "--allow-preview",
            "--question-file",
            str(tmp_path / "question.md"),
            "--execution-plan",
            "plan.json",
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["valid"]
    assert payload["run"]["execution_plan"] == plan


def test_prepare_rejects_execution_plan_outside_repository(tmp_path, capsys):
    root = tmp_path / "repo"
    for name in ("schemas", "methods", "profiles"):
        shutil.copytree(REPO_ROOT / name, root / name)
    question = root / "question.md"
    question.write_text("Review this bounded question.\n", encoding="utf-8")
    outside_plan = tmp_path / "outside-plan.json"
    outside_plan.write_text("{}", encoding="utf-8")

    exit_code = main(
        [
            "prepare",
            "runs/run-cli-outside",
            "--root",
            str(root),
            "--profile",
            "rapid-analysis",
            "--allow-preview",
            "--question-file",
            str(question),
            "--execution-plan",
            str(outside_plan),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 2
    assert payload["error"]["code"] == "command.error"
    assert "repository file" in payload["error"]["message"]


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
    first.write_text(json.dumps(_result("method-a", "FAIL")), encoding="utf-8")
    second.write_text(json.dumps(_result("method-b", "INCOMPLETE")), encoding="utf-8")

    exit_code = main(["aggregate", str(first), str(second), "--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["valid"]
    assert payload["status"] == "FAIL"
    assert payload["side_conditions"] == ["CORRELATED"]
    assert len(payload["method_ledger"]) == 2
    assert all(entry["result_digest"].startswith("sha256:") for entry in payload["method_ledger"])
    assert "judgment" not in payload


def test_check_with_run_rejects_schema_valid_empty_pass(tmp_path, capsys):
    run_path = tmp_path / "run.json"
    result_path = tmp_path / "result.json"
    run = _run()
    result = _result("key-assumptions")
    result["execution"] = run["host"]
    result["side_conditions"] = []
    run_path.write_text(json.dumps(run), encoding="utf-8")
    result_path.write_text(json.dumps(result), encoding="utf-8")

    exit_code = main(
        [
            "check",
            str(result_path),
            "--schema",
            "method-result",
            "--run",
            str(run_path),
            "--root",
            str(REPO_ROOT),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert not payload["valid"]
    codes = {issue["code"] for issue in payload["issues"]}
    assert "result.pass-findings-empty" in codes
    assert "result.pass-step-missing" in codes


@pytest.mark.parametrize(
    ("mutation", "expected_code"),
    [
        ("version", "run.method-version"),
        ("rigor", "run.rigor-mismatch"),
        ("execution", "run.execution-mismatch"),
        ("correlation", "run.correlation-missing"),
    ],
)
def test_check_with_run_enforces_method_execution_and_correlation(
    tmp_path, capsys, mutation, expected_code
):
    run = _run()
    result = _result("key-assumptions", "INCOMPLETE")
    result["execution"] = run["host"]
    result["side_conditions"] = []
    if mutation == "version":
        result["method_version"] = "9.9.9"
    elif mutation == "rigor":
        result["rigor"] = "standard"
    elif mutation == "execution":
        result["execution"] = {**run["host"], "adapter": "other"}
    else:
        run["methods"] = ["key-assumptions", "evidence-quality"]

    run_path = tmp_path / "run.json"
    result_path = tmp_path / "result.json"
    run_path.write_text(json.dumps(run), encoding="utf-8")
    result_path.write_text(json.dumps(result), encoding="utf-8")

    exit_code = main(
        [
            "check",
            str(result_path),
            "--schema",
            "method-result",
            "--run",
            str(run_path),
            "--root",
            str(REPO_ROOT),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert expected_code in {issue["code"] for issue in payload["issues"]}


def test_aggregate_downgrades_pass_without_run_context(tmp_path, capsys):
    result_path = tmp_path / "result.json"
    result_path.write_text(json.dumps(_result("key-assumptions")), encoding="utf-8")

    exit_code = main(["aggregate", str(result_path), "--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "INCOMPLETE"
    assert payload["method_ledger"][0]["status"] == "INCOMPLETE"
    assert any(issue["code"] == "aggregate.run-required-for-pass" for issue in payload["issues"])


def test_aggregate_with_run_downgrades_unsupported_pass(tmp_path, capsys):
    run_path = tmp_path / "run.json"
    result_path = tmp_path / "result.json"
    run = _run()
    result = _result("key-assumptions")
    result["execution"] = run["host"]
    run_path.write_text(json.dumps(run), encoding="utf-8")
    result_path.write_text(json.dumps(result), encoding="utf-8")

    exit_code = main(
        [
            "aggregate",
            str(result_path),
            "--run",
            str(run_path),
            "--root",
            str(REPO_ROOT),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["status"] == "INCOMPLETE"
    assert payload["method_ledger"][0]["status"] == "INCOMPLETE"
    assert any(issue["code"] == "result.pass-findings-empty" for issue in payload["issues"])


def test_aggregate_with_run_preserves_supported_pass(tmp_path, capsys):
    run_dir = tmp_path / "run-12345678"
    result_dir = run_dir / "method-results"
    result_dir.mkdir(parents=True)
    run_path = run_dir / "run.json"
    result_path = result_dir / "key-assumptions.json"
    run = _run()
    run_path.write_text(json.dumps(run), encoding="utf-8")
    result_path.write_text(
        json.dumps(_valid_key_assumptions_pass(run)),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "aggregate",
            str(result_path),
            "--root",
            str(REPO_ROOT),
        ]
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["valid"]
    assert payload["status"] == "PASS"
    assert payload["method_ledger"][0]["status"] == "PASS"


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


def test_verify_release_cli_does_not_resolve_a_symlinked_manifest(tmp_path, capsys):
    target = tmp_path / "manifest-target.json"
    target.write_text("{}", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.symlink_to(target)

    exit_code = main(["verify-release", str(manifest), "--root", str(REPO_ROOT)])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert not payload["release_eligible"]
    issue = next(issue for issue in payload["issues"] if issue["code"] == "release.manifest-parse")
    assert "symlink" in issue["message"]
