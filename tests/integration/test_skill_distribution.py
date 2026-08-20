from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL = ROOT / "skill" / "method-council"


def _tree(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def test_account_skill_zip_is_deterministic_and_contains_the_catalogue(tmp_path: Path) -> None:
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    for output in (first, second):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/package_skill.py"), "--output", str(output)],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    assert (
        hashlib.sha256(first.read_bytes()).digest() == hashlib.sha256(second.read_bytes()).digest()
    )
    with zipfile.ZipFile(first) as archive:
        names = set(archive.namelist())
        metadata = json.loads(archive.read("method-council/skill-package.json"))
    assert "method-council/SKILL.md" in names
    assert "method-council/references/hosts.md" in names
    assert "method-council/references/catalog/methods/key-assumptions/method.yaml" in names
    assert "method-council/references/catalog/methods/key-assumptions/METHOD.md" in names
    assert "method-council/references/catalog/profiles/rapid-analysis.yaml" in names
    assert sum(name.endswith("/method.yaml") for name in names) == 24
    assert (
        sum(
            name.startswith("method-council/references/catalog/profiles/")
            and name.endswith(".yaml")
            for name in names
        )
        == 12
    )
    assert metadata["kind"] == "method-council-account-skill"
    assert metadata["bundled_catalogue"] is True
    assert metadata["deterministic_cli_bundled"] is False


def test_local_installer_writes_exact_codex_and_claude_skill_copies(tmp_path: Path) -> None:
    environment = os.environ.copy()
    environment["HOME"] = str(tmp_path / "home")
    command = [sys.executable, str(ROOT / "scripts/install.py"), "--no-cli"]

    first = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )
    assert first.returncode == 0, first.stdout + first.stderr
    codex = tmp_path / "home/.agents/skills/method-council"
    claude = tmp_path / "home/.claude/skills/method-council"
    assert _tree(codex) == _tree(CANONICAL)
    assert _tree(claude) == _tree(CANONICAL)

    refusal = subprocess.run(
        command,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )
    assert refusal.returncode == 1
    assert "--force" in refusal.stderr

    replaced = subprocess.run(
        [*command, "--force"],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        check=False,
        text=True,
        timeout=30,
    )
    assert replaced.returncode == 0, replaced.stdout + replaced.stderr
    assert _tree(codex) == _tree(CANONICAL)
    assert _tree(claude) == _tree(CANONICAL)
