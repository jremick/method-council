import json
import shutil
from pathlib import Path

import pytest

from method_council.catalog import load_catalog
from method_council.evidence import content_digest, file_digest
from method_council.run import prepare_run, verify_run

REPO_ROOT = Path(__file__).resolve().parents[2]


def _root(tmp_path: Path) -> Path:
    for name in ("schemas", "methods", "profiles"):
        shutil.copytree(REPO_ROOT / name, tmp_path / name)
    return tmp_path


def _prepare(root: Path, *, question: str = "A private question") -> tuple[Path, dict]:
    evidence = root / "case.md"
    evidence.write_text("Bound evidence.\n", encoding="utf-8")
    run_dir = root / "runs" / "run-12345678"
    result = prepare_run(
        root=root,
        run_dir=run_dir,
        question=question,
        catalog=load_catalog(root),
        profile_id="rapid-analysis",
        activity=None,
        rigor=None,
        method_ids=[],
        allow_preview=True,
        require_challenge=False,
        evidence_specs=["case=case.md"],
        evidence_kind="repository",
        adapter="codex",
        provider_state="verified",
        model_requested=None,
        model_observed=None,
        external_api_calls=False,
        correlation_group="codex-test",
    )
    assert result["valid"]
    return run_dir, result["run"]


def _method_result(run: dict, method_id: str, finding_id: str, status: str = "PASS") -> dict:
    return {
        "schema_version": "0.1.0",
        "run_id": run["run_id"],
        "method_id": method_id,
        "method_version": "0.1.0",
        "rigor": run["rigor"],
        "status": status,
        "side_conditions": ["CORRELATED"],
        "completed_steps": ["bounded-test"],
        "findings": [
            {
                "id": finding_id,
                "type": "fact",
                "statement": "The public fixture contains bound evidence.",
                "evidence_refs": ["case"],
                "method_step": "bounded-test",
                "counterevidence_refs": [],
            }
        ],
        "alternatives": [],
        "confidence": {
            "band": "moderate",
            "basis": "The finding is limited to the bound fixture.",
        },
        "change_conditions": ["Different fixture bytes."],
        "errors": [],
        "execution": run["host"],
    }


def _write_bundle(
    run_dir: Path,
    run: dict,
    *,
    statuses: tuple[str, str] = ("PASS", "PASS"),
) -> list[Path]:
    paths: list[Path] = []
    results = []
    for index, (method_id, status) in enumerate(zip(run["methods"], statuses, strict=True)):
        result = _method_result(run, method_id, f"finding-{index}", status)
        path = run_dir / "method-results" / f"{method_id}.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths.append(path)
        results.append(result)
    primary = "INCOMPLETE" if "INCOMPLETE" in statuses else "PASS"
    report = {
        "schema_version": "0.1.0",
        "run_id": run["run_id"],
        "status": primary,
        "side_conditions": ["CORRELATED"],
        "judgment": "The bounded fixture supports a limited judgment.",
        "decision_boundary": "Test the run-verification contract only.",
        "next_action": "Retain the stated limitations.",
        "key_judgments": [
            {
                "statement": "The first checked finding is bound.",
                "finding_refs": ["finding-0"],
                "confidence": "moderate",
                "confidence_basis": "One public fixture supports the statement.",
            }
        ],
        "strongest_alternative": "The fixture may not generalize.",
        "assumptions": [],
        "unknowns": ["General method fidelity is not tested."],
        "dissent": [],
        "checkpoint": {"trigger": "Fixture changes", "indicators": ["Digest changes"]},
        "method_ledger": [
            {
                "method_id": result["method_id"],
                "status": result["status"],
                "result_digest": file_digest(path),
            }
            for result, path in zip(results, paths, strict=True)
        ],
        "limitations": ["This is synthetic contract evidence."],
    }
    (run_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return paths


def _rewrite_report_ledger(run_dir: Path, result_paths: list[Path]) -> None:
    report_path = run_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["method_ledger"] = [
        {
            "method_id": json.loads(path.read_text(encoding="utf-8"))["method_id"],
            "status": json.loads(path.read_text(encoding="utf-8"))["status"],
            "result_digest": file_digest(path),
        }
        for path in result_paths
    ]
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_prepare_persists_only_question_digest_and_requires_preview_opt_in(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    persisted = (run_dir / "run.json").read_text(encoding="utf-8")

    assert "A private question" not in persisted
    assert run["question_digest"] == content_digest("A private question")
    assert run["raw_prompt_persisted"] is False
    assert all(not Path(entry["locator"]).is_absolute() for entry in run["evidence"])

    with pytest.raises(ValueError, match="preview profile requires"):
        prepare_run(
            root=root,
            run_dir=root / "runs" / "run-preview-off",
            question="Question",
            catalog=load_catalog(root),
            profile_id="rapid-analysis",
            activity=None,
            rigor=None,
            method_ids=[],
            allow_preview=False,
            require_challenge=False,
            evidence_specs=[],
            evidence_kind="repository",
            adapter="codex",
            provider_state="unverified",
            model_requested=None,
            model_observed=None,
            external_api_calls=False,
            correlation_group=None,
        )


def test_prepare_rejects_outside_evidence_and_nonempty_target(tmp_path: Path):
    root = _root(tmp_path / "repo")
    outside = tmp_path / "outside.md"
    outside.write_text("outside", encoding="utf-8")
    target = root / "runs" / "run-12345678"
    target.mkdir(parents=True)
    (target / "keep.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(ValueError, match="must not exist or must be empty"):
        _prepare(root)
    target.joinpath("keep.txt").unlink()
    target.rmdir()

    with pytest.raises(ValueError, match="escapes repository root"):
        prepare_run(
            root=root,
            run_dir=target,
            question="Question",
            catalog=load_catalog(root),
            profile_id="rapid-analysis",
            activity=None,
            rigor=None,
            method_ids=[],
            allow_preview=True,
            require_challenge=False,
            evidence_specs=[f"outside={outside}"],
            evidence_kind="repository",
            adapter="codex",
            provider_state="unverified",
            model_requested=None,
            model_observed=None,
            external_api_calls=False,
            correlation_group="codex-test",
        )


def test_verify_run_accepts_valid_pass_and_honest_incomplete(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    _write_bundle(run_dir, run)
    verdict = verify_run(run_dir, root=root)

    assert verdict["valid"]
    assert verdict["status"] == "PASS"
    assert verdict["side_conditions"] == ["CORRELATED"]

    _write_bundle(run_dir, run, statuses=("INCOMPLETE", "PASS"))
    verdict = verify_run(run_dir, root=root)
    assert verdict["valid"]
    assert verdict["status"] == "INCOMPLETE"


def test_verify_run_rejects_forged_status_digest_and_missing_result(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    paths = _write_bundle(run_dir, run)
    report_path = run_dir / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["status"] = "FAIL"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    verdict = verify_run(run_dir, root=root)
    assert not verdict["valid"]
    assert any(issue["code"] == "run.report-status" for issue in verdict["issues"])

    _write_bundle(run_dir, run)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["method_ledger"][0]["result_digest"] = "sha256:" + "0" * 64
    report_path.write_text(json.dumps(report), encoding="utf-8")
    verdict = verify_run(run_dir, root=root)
    assert not verdict["valid"]
    assert any(issue["code"] == "run.report-ledger" for issue in verdict["issues"])

    _write_bundle(run_dir, run)
    paths[0].unlink()
    verdict = verify_run(run_dir, root=root)
    assert not verdict["valid"]
    assert verdict["status"] != "PASS"
    assert any(issue["code"] == "run.result-missing" for issue in verdict["issues"])


@pytest.mark.parametrize(
    ("mutation", "issue_code"),
    [
        ("unbound", "evidence.reference-unbound"),
        ("execution", "run.execution-mismatch"),
        ("correlation", "run.correlation-missing"),
        ("duplicate-finding", "run.finding-duplicate"),
    ],
)
def test_verify_run_rejects_semantic_binding_failures(
    tmp_path: Path, mutation: str, issue_code: str
):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    paths = _write_bundle(run_dir, run)
    first = json.loads(paths[0].read_text(encoding="utf-8"))
    second = json.loads(paths[1].read_text(encoding="utf-8"))
    if mutation == "unbound":
        first["findings"][0]["evidence_refs"] = ["not-bound"]
    elif mutation == "execution":
        first["execution"]["provider_state"] = "degraded"
    elif mutation == "correlation":
        first["side_conditions"] = []
    else:
        second["findings"][0]["id"] = first["findings"][0]["id"]
    paths[0].write_text(json.dumps(first), encoding="utf-8")
    paths[1].write_text(json.dumps(second), encoding="utf-8")
    _rewrite_report_ledger(run_dir, paths)

    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    assert any(issue["code"] == issue_code for issue in verdict["issues"])
