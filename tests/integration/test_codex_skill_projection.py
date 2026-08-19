from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "skill" / "method-council"
PROJECTION = ROOT / ".agents" / "skills" / "method-council"
SYNC_SCRIPT = ROOT / "scripts" / "sync_codex_skill.py"


def _load_sync_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sync_codex_skill", SYNC_SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _files(root: Path, *, exclude: set[str] | None = None) -> dict[str, bytes]:
    excluded = exclude or set()
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.relative_to(root).as_posix() not in excluded
    }


def _digest(files: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative, content in sorted(files.items()):
        relative_bytes = relative.encode("utf-8")
        digest.update(len(relative_bytes).to_bytes(8, "big"))
        digest.update(relative_bytes)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return f"sha256:{digest.hexdigest()}"


def _strings(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for entry in value for item in _strings(entry)]
    if isinstance(value, dict):
        return [item for entry in value.values() for item in _strings(entry)]
    return []


def test_checked_in_projection_exactly_matches_canonical_skill() -> None:
    canonical_files = _files(CANONICAL)
    projected_files = _files(PROJECTION, exclude={".projection.json"})

    assert projected_files == canonical_files

    metadata = json.loads((PROJECTION / ".projection.json").read_text(encoding="utf-8"))
    assert metadata == {
        "schema_version": "0.1.0",
        "kind": "codex-skill-projection",
        "source": "skill/method-council",
        "target": ".agents/skills/method-council",
        "canonical_input_digest": _digest(canonical_files),
        "generator_id": "method-council-codex-skill-sync",
        "generator_version": "0.1.0",
        "generated_files": sorted(canonical_files),
    }


def test_projection_metadata_and_content_have_no_personal_absolute_paths() -> None:
    metadata = json.loads((PROJECTION / ".projection.json").read_text(encoding="utf-8"))
    for value in _strings(metadata):
        assert not Path(value).is_absolute()

    forbidden = (str(ROOT), "/Users/", "file://")
    for relative, content in _files(PROJECTION).items():
        text = content.decode("utf-8")
        assert all(marker not in text for marker in forbidden), relative


def test_sync_is_content_bound_idempotent_and_removes_stale_files(tmp_path: Path) -> None:
    module = _load_sync_script()
    temporary_source = tmp_path / "skill" / "method-council"
    shutil.copytree(CANONICAL, temporary_source)

    module.sync_projection(tmp_path)
    first = _files(tmp_path / ".agents" / "skills" / "method-council")
    module.sync_projection(tmp_path)
    assert _files(tmp_path / ".agents" / "skills" / "method-council") == first
    assert module.projection_issues(tmp_path) == []

    stale = tmp_path / ".agents" / "skills" / "method-council" / "stale.txt"
    stale.write_text("stale\n", encoding="utf-8")
    assert module.projection_issues(tmp_path) == ["stale:stale.txt"]
    module.sync_projection(tmp_path)
    assert not stale.exists()
    assert module.projection_issues(tmp_path) == []


@pytest.mark.parametrize("skill_path", [CANONICAL, PROJECTION])
def test_skill_passes_bundled_quick_validate(skill_path: Path) -> None:
    configured = os.environ.get("CODEX_SKILL_QUICK_VALIDATE")
    validator = (
        Path(configured).expanduser()
        if configured
        else Path.home()
        / ".codex"
        / "skills"
        / ".system"
        / "skill-creator"
        / "scripts"
        / "quick_validate.py"
    )
    if not validator.is_file():
        pytest.skip("bundled Codex skill quick_validate.py is unavailable")

    result = subprocess.run(
        [sys.executable, str(validator), str(skill_path)],
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
