import json
import os
import shutil
from pathlib import Path

import pytest

from method_council.catalog import load_catalog
from method_council.documents import MAX_DOCUMENT_BYTES
from method_council.evidence import content_digest, file_digest
from method_council.run import prepare_run, verify_run
from method_council.status import aggregate_status

REPO_ROOT = Path(__file__).resolve().parents[2]


def _root(tmp_path: Path) -> Path:
    for name in ("schemas", "methods", "profiles"):
        shutil.copytree(REPO_ROOT / name, tmp_path / name)
    return tmp_path


def _prepare(
    root: Path,
    *,
    question: str = "A private question",
    profile_id: str = "rapid-analysis",
    evidence_count: int = 1,
) -> tuple[Path, dict]:
    evidence_specs: list[str] = []
    for index in range(evidence_count):
        evidence_id = "case" if index == 0 else f"case-{index + 1}"
        evidence_path = root / f"{evidence_id}.md"
        evidence_path.write_text(f"Bound evidence {index + 1}.\n", encoding="utf-8")
        evidence_specs.append(f"{evidence_id}={evidence_path.name}")
    run_dir = root / "runs" / "run-12345678"
    result = prepare_run(
        root=root,
        run_dir=run_dir,
        question=question,
        catalog=load_catalog(root),
        profile_id=profile_id,
        activity=None,
        rigor=None,
        method_ids=[],
        allow_preview=True,
        require_challenge=False,
        evidence_specs=evidence_specs,
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


def _method_result(run: dict, method: dict, finding_id: str, status: str = "PASS") -> dict:
    selected_steps = method["rigor"][run["rigor"]]["steps"]
    procedure = {step["id"]: step for step in method["procedure"]}
    artifact_fields = {
        field
        for step_id in selected_steps
        for field in procedure[step_id].get("artifact_fields", [])
    }
    minimum_references = max(1, method["rigor"][run["rigor"]]["minimum_evidence_refs"])
    evidence_refs = [entry["id"] for entry in run["evidence"][:minimum_references]]
    return {
        "schema_version": "0.1.0",
        "run_id": run["run_id"],
        "method_id": method["id"],
        "method_version": "0.1.0",
        "rigor": run["rigor"],
        "status": status,
        "side_conditions": ["CORRELATED"],
        "completed_steps": selected_steps,
        "findings": [
            {
                "id": finding_id,
                "type": "fact",
                "statement": "The public fixture contains bound evidence.",
                "evidence_refs": evidence_refs,
                "method_step": selected_steps[0],
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
        "method_artifact": {
            field: f"Synthetic contract value for {field}." for field in artifact_fields
        },
    }


def _write_bundle(
    run_dir: Path,
    run: dict,
    *,
    statuses: tuple[str, ...] = ("PASS", "PASS"),
) -> list[Path]:
    paths: list[Path] = []
    results = []
    catalog = load_catalog(run_dir.parents[1])
    for index, (method_id, status) in enumerate(zip(run["methods"], statuses, strict=True)):
        result = _method_result(
            run,
            catalog.methods[method_id],
            f"finding-{index}",
            status,
        )
        path = run_dir / "method-results" / f"{method_id}.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        paths.append(path)
        results.append(result)
    primary = aggregate_status(statuses)
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


def _rewrite_run(run_dir: Path, run: dict) -> None:
    (run_dir / "run.json").write_text(
        json.dumps(run, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def test_prepare_persists_only_question_digest_and_requires_preview_opt_in(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    persisted = (run_dir / "run.json").read_text(encoding="utf-8")

    assert "A private question" not in persisted
    assert run["question_digest"] == content_digest("A private question")
    assert run["raw_prompt_persisted"] is False
    assert all(not Path(entry["locator"]).is_absolute() for entry in run["evidence"])
    assert run["route"] == {
        "source": "profile",
        "validated": True,
        "profile_id": "rapid-analysis",
        "allow_preview": True,
        "challenge_required": True,
        "why": [
            "profile:rapid-analysis",
            load_catalog(root).profiles["rapid-analysis"]["notes"],
        ],
    }

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


@pytest.mark.parametrize(
    ("mutation", "issue_code"),
    [
        ("profile-id", "run.profile-mismatch"),
        ("method-order", "run.profile-mismatch"),
        ("allow-preview", "run.profile-preview-disallowed"),
        ("challenge", "run.profile-mismatch"),
    ],
)
def test_verify_run_revalidates_exact_persisted_route_policy(
    tmp_path: Path, mutation: str, issue_code: str
):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    _write_bundle(run_dir, run)

    if mutation == "profile-id":
        run["route"]["profile_id"] = "standard-review"
    elif mutation == "method-order":
        run["methods"] = list(reversed(run["methods"]))
    elif mutation == "allow-preview":
        run["route"]["allow_preview"] = False
    else:
        run["route"]["challenge_required"] = False
    _rewrite_run(run_dir, run)

    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    assert any(issue["code"] == issue_code for issue in verdict["issues"])
    if mutation == "allow-preview":
        assert any(issue["code"] == "run.route-invalid" for issue in verdict["issues"])


def test_verify_run_binds_manifest_id_to_directory_name(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    _write_bundle(run_dir, run)
    run["run_id"] = "run-forged-id"
    _rewrite_run(run_dir, run)

    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    assert any(issue["code"] == "run.directory-id-mismatch" for issue in verdict["issues"])


@pytest.mark.parametrize(
    ("mutation", "issue_code"),
    [
        ("missing-step", "result.pass-step-missing"),
        ("unknown-completed-step", "result.pass-completed-step-unknown"),
        ("unknown-finding-step", "result.pass-finding-step-unknown"),
        ("incomplete-finding-step", "result.pass-finding-step-incomplete"),
        ("insufficient-evidence", "result.pass-evidence-minimum"),
        ("missing-artifact", "result.pass-artifact-field-missing"),
        ("empty-findings", "result.pass-findings-empty"),
        ("errors", "result.pass-errors-present"),
        ("skipped", "result.pass-skipped"),
    ],
)
def test_verify_run_downgrades_unsupported_pass_semantics(
    tmp_path: Path, mutation: str, issue_code: str
):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    paths = _write_bundle(run_dir, run)
    result = json.loads(paths[0].read_text(encoding="utf-8"))
    method = load_catalog(root).methods[result["method_id"]]

    if mutation == "missing-step":
        result["completed_steps"].pop()
    elif mutation == "unknown-completed-step":
        result["completed_steps"].append("invented-step")
    elif mutation == "unknown-finding-step":
        result["findings"][0]["method_step"] = "invented-step"
    elif mutation == "incomplete-finding-step":
        selected = set(method["rigor"][run["rigor"]]["steps"])
        unselected = next(step["id"] for step in method["procedure"] if step["id"] not in selected)
        result["findings"][0]["method_step"] = unselected
    elif mutation == "insufficient-evidence":
        result["findings"][0]["type"] = "assumption"
        result["findings"][0]["evidence_refs"] = []
    elif mutation == "missing-artifact":
        result["method_artifact"].pop(next(iter(result["method_artifact"])))
    elif mutation == "empty-findings":
        result["findings"] = []
        report_path = run_dir / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["key_judgments"] = []
        report_path.write_text(json.dumps(report), encoding="utf-8")
    elif mutation == "errors":
        result["errors"] = [{"code": "host.failed", "message": "Synthetic failure."}]
    else:
        result["side_conditions"].append("SKIPPED")
        report_path = run_dir / "report.json"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["side_conditions"].append("SKIPPED")
        report_path.write_text(json.dumps(report), encoding="utf-8")

    paths[0].write_text(json.dumps(result), encoding="utf-8")
    _rewrite_report_ledger(run_dir, paths)
    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    assert verdict["status"] == "INCOMPLETE"
    assert any(issue["code"] == issue_code for issue in verdict["issues"])
    assert any(issue["code"] == "run.report-status-unsupported-pass" for issue in verdict["issues"])
    assert any(issue["code"] == "run.report-ledger-unsupported-pass" for issue in verdict["issues"])


def test_pass_rejects_assumption_disallowed_by_method_evidence_policy(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(
        root,
        profile_id="standard-review",
        evidence_count=2,
    )
    paths = _write_bundle(run_dir, run, statuses=("PASS", "PASS", "PASS"))
    assert verify_run(run_dir, root=root)["valid"]

    result_path = next(path for path in paths if path.stem == "evidence-quality")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["findings"].append(
        {
            "id": "unreferenced-assumption",
            "type": "assumption",
            "statement": "This premise has no bound supporting or counterevidence reference.",
            "evidence_refs": [],
            "method_step": result["completed_steps"][0],
            "counterevidence_refs": [],
        }
    )
    result_path.write_text(json.dumps(result), encoding="utf-8")
    _rewrite_report_ledger(run_dir, paths)

    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    assert verdict["status"] == "INCOMPLETE"
    assert any(
        issue["code"] == "result.pass-assumption-evidence-required" for issue in verdict["issues"]
    )


def test_pass_allows_unreferenced_assumption_when_method_policy_permits_it(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(
        root,
        profile_id="standard-review",
        evidence_count=2,
    )
    paths = _write_bundle(run_dir, run, statuses=("PASS", "PASS", "PASS"))
    result_path = next(path for path in paths if path.stem == "key-assumptions")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["findings"].append(
        {
            "id": "explicit-unreferenced-assumption",
            "type": "assumption",
            "statement": "This explicitly labelled premise is not represented as evidence-backed.",
            "evidence_refs": [],
            "method_step": result["completed_steps"][0],
            "counterevidence_refs": [],
        }
    )
    result_path.write_text(json.dumps(result), encoding="utf-8")
    _rewrite_report_ledger(run_dir, paths)

    verdict = verify_run(run_dir, root=root)

    assert verdict["valid"]
    assert verdict["status"] == "PASS"


def test_unreferenced_assumption_does_not_invalidate_honest_incomplete(tmp_path: Path):
    root = _root(tmp_path)
    run_dir, run = _prepare(
        root,
        profile_id="standard-review",
        evidence_count=2,
    )
    paths = _write_bundle(run_dir, run, statuses=("INCOMPLETE", "PASS", "PASS"))
    result_path = next(path for path in paths if path.stem == "evidence-quality")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["findings"].append(
        {
            "id": "known-incomplete-assumption",
            "type": "assumption",
            "statement": "This premise remains explicitly unresolved in an incomplete result.",
            "evidence_refs": [],
            "method_step": result["completed_steps"][0],
            "counterevidence_refs": [],
        }
    )
    result_path.write_text(json.dumps(result), encoding="utf-8")
    _rewrite_report_ledger(run_dir, paths)

    verdict = verify_run(run_dir, root=root)

    assert verdict["valid"]
    assert verdict["status"] == "INCOMPLETE"


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (("FAIL", "PASS"), "FAIL"),
        (("ERROR", "PASS"), "ERROR"),
        (("INCOMPLETE", "PASS"), "ERROR"),
    ],
)
def test_verify_run_preserves_primary_precedence_with_integrity_issues(
    tmp_path: Path, statuses: tuple[str, str], expected: str
):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    _write_bundle(run_dir, run, statuses=statuses)
    run["evidence"][0]["digest"] = "sha256:" + "0" * 64
    _rewrite_run(run_dir, run)

    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    assert verdict["status"] == expected
    assert any(issue["code"] == "run.evidence-digest" for issue in verdict["issues"])


@pytest.mark.parametrize("document", ["run", "report", "result"])
@pytest.mark.parametrize("replacement", ["symlink", "directory"])
def test_verify_run_rejects_nonregular_child_documents(
    tmp_path: Path, document: str, replacement: str
):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    paths = _write_bundle(run_dir, run)
    path = {
        "run": run_dir / "run.json",
        "report": run_dir / "report.json",
        "result": paths[0],
    }[document]
    issue_code = {
        "run": "run.manifest-invalid",
        "report": "run.report-invalid",
        "result": "run.result-invalid",
    }[document]

    if replacement == "symlink":
        target = root / f"moved-{document}.json"
        path.replace(target)
        os.symlink(target, path)
    else:
        path.unlink()
        path.mkdir()

    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    assert any(issue["code"] == issue_code for issue in verdict["issues"])


@pytest.mark.parametrize("document", ["run", "report", "result"])
def test_verify_run_bounds_all_child_document_reads(tmp_path: Path, document: str):
    root = _root(tmp_path)
    run_dir, run = _prepare(root)
    paths = _write_bundle(run_dir, run)
    path = {
        "run": run_dir / "run.json",
        "report": run_dir / "report.json",
        "result": paths[0],
    }[document]
    issue_code = {
        "run": "run.manifest-invalid",
        "report": "run.report-invalid",
        "result": "run.result-invalid",
    }[document]
    path.write_bytes(b" " * (MAX_DOCUMENT_BYTES + 1))

    verdict = verify_run(run_dir, root=root)

    assert not verdict["valid"]
    matching = [issue for issue in verdict["issues"] if issue["code"] == issue_code]
    assert matching
    assert "exceeds" in matching[0]["message"]
