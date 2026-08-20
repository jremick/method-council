from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run(
    command: list[str], *, cwd: Path, environment: dict[str, str]
) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )


def test_wheel_installs_with_catalogue_and_runs_outside_source_checkout(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is unavailable")

    environment = os.environ.copy()
    for name in ("VIRTUAL_ENV", "PYTHONPATH", "UV_PROJECT_ENVIRONMENT"):
        environment.pop(name, None)
    environment["UV_CACHE_DIR"] = str(tmp_path / "uv-cache")

    dist = tmp_path / "dist"
    build = _run(
        [uv, "build", str(ROOT), "--wheel", "--out-dir", str(dist)],
        cwd=tmp_path,
        environment=environment,
    )
    assert build.returncode == 0, build.stdout + build.stderr
    wheel = next(dist.glob("method_council-*.whl"))

    virtualenv = tmp_path / "venv"
    create = _run(
        [uv, "venv", str(virtualenv), "--python", "3.12"],
        cwd=tmp_path,
        environment=environment,
    )
    assert create.returncode == 0, create.stdout + create.stderr
    executable = virtualenv / (
        "Scripts/method-council.exe" if os.name == "nt" else "bin/method-council"
    )
    python = virtualenv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    install = _run(
        [uv, "pip", "install", "--python", str(python), str(wheel)],
        cwd=tmp_path,
        environment=environment,
    )
    assert install.returncode == 0, install.stdout + install.stderr

    workspace = tmp_path / "unrelated-project"
    workspace.mkdir()
    validation = _run([str(executable), "validate"], cwd=workspace, environment=environment)
    assert validation.returncode == 0, validation.stdout + validation.stderr
    assert json.loads(validation.stdout) == {
        "issues": [],
        "method_count": 24,
        "profile_count": 12,
        "valid": True,
    }

    prepared = subprocess.run(
        [
            str(executable),
            "prepare",
            "runs/portable-check",
            "--profile",
            "rapid-analysis",
            "--allow-preview",
        ],
        cwd=workspace,
        env=environment,
        input="Should this reversible migration proceed?",
        capture_output=True,
        check=False,
        text=True,
        timeout=60,
    )
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    payload = json.loads(prepared.stdout)
    assert payload["valid"]
    assert payload["run_path"] == "runs/portable-check/run.json"
    assert (workspace / payload["run_path"]).is_file()

    verification = _run(
        [str(executable), "verify-run", "runs/portable-check"],
        cwd=workspace,
        environment=environment,
    )
    assert verification.returncode == 1
    verdict = json.loads(verification.stdout)
    assert verdict["status"] == "INCOMPLETE"
    assert {issue["code"] for issue in verdict["issues"]} == {
        "run.report-missing",
        "run.result-missing",
    }
