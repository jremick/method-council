from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_script(name: str) -> ModuleType:
    path = REPO_ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"method_council_{name}", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validate_fixtures = _load_script("validate_fixtures")
tracked_file_hygiene = _load_script("tracked_file_hygiene")


def test_fixture_inventory_validates_all_wave1_cases() -> None:
    fixtures = validate_fixtures.validate_inventory(REPO_ROOT / "tests" / "fixtures")

    assert len(fixtures) == 8
    assert {fixture["id"] for fixture in fixtures} == {
        "architecture-tradeoff",
        "debugging-rca",
        "release-decision-missing-evidence",
        "adversarial-risk",
        "hostile-prompt-injection",
        "provider-degraded-malformed",
        "split-conclusion",
        "unsupported-official-standard-claim",
    }


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (["PASS", "PASS"], "PASS"),
        (["PASS", "INCOMPLETE"], "INCOMPLETE"),
        (["INCOMPLETE", "ERROR"], "ERROR"),
        (["ERROR", "FAIL", "INCOMPLETE"], "FAIL"),
    ],
)
def test_status_aggregation_uses_canonical_precedence(statuses: list[str], expected: str) -> None:
    gates = [
        {"gate": f"gate-{index}", "status": status, "reason_code": "TEST_GATE"}
        for index, status in enumerate(statuses)
    ]

    assert validate_fixtures.aggregate_status(gates) == expected


def _init_tracked_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(path)], check=True)


def test_hygiene_scan_reports_only_path_and_category(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _init_tracked_repo(tmp_path)
    synthetic_token = "ghp_" + "A" * 36
    (tmp_path / "credential.txt").write_text(synthetic_token, encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "credential.txt"], check=True)

    exit_code = tracked_file_hygiene.main(["--repo", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "path=credential.txt category=github-token" in captured.err
    assert synthetic_token not in captured.out
    assert synthetic_token not in captured.err


def test_hygiene_scan_passes_for_public_safe_tracked_text(tmp_path: Path) -> None:
    _init_tracked_repo(tmp_path)
    (tmp_path / "README.md").write_text("Public-safe fixture repository.\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "README.md"], check=True)

    result = tracked_file_hygiene.scan_tracked(tmp_path)

    assert result.tracked_files == 1
    assert result.scanned_text_files == 1
    assert result.findings == ()
