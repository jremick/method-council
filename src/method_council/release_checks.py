"""Registered, candidate-bound checks for the source-only public alpha."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from method_council.documents import DocumentError
from method_council.evidence import file_digest
from method_council.issues import Issue
from method_council.status import aggregate_status

LOCAL_ALPHA_PRODUCER = "method-council.local-alpha-v1"
LOCAL_ALPHA_RAW_FORMAT = "method-council.release-check-observation.v1"
MAX_CAPTURE_BYTES = 1_048_576


@dataclass(frozen=True)
class ReleaseCheck:
    identifier: str
    command: tuple[str, ...]
    timeout_seconds: int
    require_empty_stdout: bool = False


LOCAL_ALPHA_CHECKS = (
    ReleaseCheck("catalog", ("python", "-m", "method_council.cli", "validate"), 60),
    ReleaseCheck("skill-projection", ("python", "scripts/sync_codex_skill.py", "check"), 60),
    ReleaseCheck("method-screening", ("python", "scripts/evaluate_methods.py"), 60),
    ReleaseCheck(
        "method-screening-clean",
        ("git", "diff", "--exit-code", "--", "evals/methods/screening-report.json"),
        30,
    ),
    ReleaseCheck("fixtures", ("python", "scripts/validate_fixtures.py"), 60),
    ReleaseCheck("tracked-hygiene", ("python", "scripts/tracked_file_hygiene.py"), 60),
    ReleaseCheck("pytest", ("python", "-m", "pytest", "-q"), 300),
    ReleaseCheck("ruff-check", ("python", "-m", "ruff", "check", "."), 120),
    ReleaseCheck("ruff-format", ("python", "-m", "ruff", "format", "--check", "."), 120),
    ReleaseCheck("package-build", ("uv", "build"), 180),
    ReleaseCheck("gitleaks-history", ("gitleaks", "git", ".", "--redact", "--no-banner"), 180),
    ReleaseCheck("gitleaks-worktree", ("gitleaks", "dir", ".", "--redact", "--no-banner"), 180),
    ReleaseCheck(
        "repository-clean",
        ("git", "status", "--porcelain=v1", "--untracked-files=all"),
        30,
        require_empty_stdout=True,
    ),
)


def _resolve_command(command: tuple[str, ...]) -> tuple[list[str] | None, str | None]:
    executable = command[0]
    resolved = sys.executable if executable == "python" else shutil.which(executable)
    if not resolved:
        return None, f"required release executable is unavailable: {executable}"
    return [resolved, *command[1:]], None


def observe_release_check(root: Path, check: ReleaseCheck) -> dict[str, Any]:
    """Run one bounded check and return a stable, non-secret observation."""

    actual, resolution_error = _resolve_command(check.command)
    base: dict[str, Any] = {
        "schema_version": "0.1.0",
        "raw_format": LOCAL_ALPHA_RAW_FORMAT,
        "producer": LOCAL_ALPHA_PRODUCER,
        "check_id": check.identifier,
        "command": list(check.command),
        "timeout_seconds": check.timeout_seconds,
    }
    if resolution_error:
        return {
            **base,
            "status": "ERROR",
            "exit_code": None,
            "timed_out": False,
            "output_overflow": False,
            "stdout_bytes": 0,
            "stderr_bytes": 0,
            "stdout_digest": None,
            "stderr_digest": None,
            "error": resolution_error,
        }

    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
        timed_out = False
        error: str | None = None
        exit_code: int | None = None
        try:
            completed = subprocess.run(
                actual,
                cwd=root,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                timeout=check.timeout_seconds,
                check=False,
            )
            exit_code = completed.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            error = "release check timed out"
        except OSError as exc:
            error = f"release check could not start: {exc}"

        stdout_bytes = stdout_file.tell()
        stderr_bytes = stderr_file.tell()
        overflow = stdout_bytes > MAX_CAPTURE_BYTES or stderr_bytes > MAX_CAPTURE_BYTES
        stdout_file.seek(0)
        stderr_file.seek(0)
        stdout = stdout_file.read(MAX_CAPTURE_BYTES + 1)
        stderr = stderr_file.read(MAX_CAPTURE_BYTES + 1)

    stdout_digest = f"sha256:{hashlib.sha256(stdout).hexdigest()}" if not overflow else None
    stderr_digest = f"sha256:{hashlib.sha256(stderr).hexdigest()}" if not overflow else None
    status = "PASS"
    if timed_out or error or overflow:
        status = "ERROR"
    elif exit_code != 0 or (check.require_empty_stdout and stdout):
        status = "FAIL"
    return {
        **base,
        "status": status,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "output_overflow": overflow,
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
        "stdout_digest": stdout_digest,
        "stderr_digest": stderr_digest,
        "error": error,
    }


def _git_head(root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def build_local_alpha_evidence(
    root: Path, output_dir: Path, *, candidate_label: str = "0.1.0-alpha.1"
) -> dict[str, Any]:
    """Produce ignored release evidence that the verifier can independently rerun."""

    root = root.resolve()
    lexical_output = output_dir if output_dir.is_absolute() else root / output_dir
    cursor = Path(lexical_output.anchor)
    for part in lexical_output.parts[1:]:
        cursor /= part
        if cursor.is_symlink():
            raise ValueError("release evidence output must not contain symlinks")
    output_dir = lexical_output.resolve()
    if not output_dir.is_relative_to(root / "runs" / "release"):
        raise ValueError("release evidence output must be under runs/release")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("release evidence output must be new or empty")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = output_dir / "raw"
    raw_dir.mkdir()

    candidate = _git_head(root)
    if not candidate:
        raise ValueError("repository HEAD is unavailable")

    checks: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    for check in LOCAL_ALPHA_CHECKS:
        observation = observe_release_check(root, check)
        observation["candidate_commit"] = candidate
        observations.append(observation)
        observation_path = raw_dir / f"{check.identifier}.json"
        observation_path.write_text(
            json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        relative = observation_path.relative_to(root).as_posix()
        checks.append(
            {
                "id": check.identifier,
                "status": observation["status"],
                "evidence": [{"path": relative, "digest": file_digest(observation_path)}],
            }
        )

    status = aggregate_status(observation["status"] for observation in observations)
    report = {
        "schema_version": "0.1.0",
        "gate": "local-alpha",
        "status": status,
        "producer": LOCAL_ALPHA_PRODUCER,
        "raw_format": LOCAL_ALPHA_RAW_FORMAT,
        "candidate_commit": candidate,
        "checks": checks,
    }
    report_path = output_dir / "local-alpha.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = {
        "schema_version": "0.1.0",
        "candidate": candidate_label,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "artifacts": [
            {
                "id": "local-alpha-gate",
                "path": report_path.relative_to(root).as_posix(),
                "digest": file_digest(report_path),
                "gate": "local-alpha",
            }
        ],
        "required_gates": ["local-alpha"],
        "claimed_release_eligible": status == "PASS",
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "valid": status == "PASS",
        "status": status,
        "candidate_commit": candidate,
        "manifest": manifest_path.relative_to(root).as_posix(),
        "checks": [
            {"id": observation["check_id"], "status": observation["status"]}
            for observation in observations
        ],
    }


def verify_registered_gate(
    document: Any,
    *,
    expected_gate: str,
    root: Path,
    read_document: Callable[[Path], Any],
) -> tuple[str | None, list[Issue]]:
    """Rerun a registered gate, or return ``None`` for an unknown producer."""

    if not isinstance(document, dict):
        return None, []
    if expected_gate != "local-alpha" or document.get("producer") != LOCAL_ALPHA_PRODUCER:
        return None, []

    issues: list[Issue] = []
    if document.get("raw_format") != LOCAL_ALPHA_RAW_FORMAT:
        issues.append(Issue("release.producer-format", "registered raw format does not match"))
    candidate = document.get("candidate_commit")
    observed_head = _git_head(root)
    if not observed_head:
        issues.append(Issue("release.candidate-unavailable", "repository HEAD is unavailable"))
    elif candidate != observed_head:
        issues.append(
            Issue(
                "release.candidate-mismatch",
                f"gate candidate {candidate!r} does not match repository HEAD {observed_head!r}",
            )
        )

    checks = document.get("checks")
    by_id = (
        {check.get("id"): check for check in checks if isinstance(check, dict)}
        if isinstance(checks, list)
        else {}
    )
    expected_ids = [check.identifier for check in LOCAL_ALPHA_CHECKS]
    if list(by_id) != expected_ids or len(by_id) != len(checks or []):
        issues.append(
            Issue(
                "release.producer-check-set",
                "registered gate must contain the exact ordered local-alpha check set",
            )
        )

    recorded_statuses: list[str] = []
    for check in LOCAL_ALPHA_CHECKS:
        entry = by_id.get(check.identifier)
        if not isinstance(entry, dict):
            recorded_statuses.append("ERROR")
            continue
        bindings = entry.get("evidence")
        if not isinstance(bindings, list) or len(bindings) != 1:
            issues.append(
                Issue(
                    "release.producer-evidence-cardinality",
                    f"check {check.identifier!r} requires exactly one raw observation",
                )
            )
            recorded_statuses.append("ERROR")
            continue
        path_value = bindings[0].get("path") if isinstance(bindings[0], dict) else None
        observation_path = root / path_value if isinstance(path_value, str) else None
        try:
            if observation_path is None:
                raise DocumentError("raw observation path is invalid")
            observation = read_document(observation_path)
        except (DocumentError, OSError) as exc:
            issues.append(
                Issue(
                    "release.producer-observation",
                    f"could not parse raw observation for {check.identifier!r}: {exc}",
                )
            )
            recorded_statuses.append("ERROR")
            continue
        expected_fields = {
            "schema_version": "0.1.0",
            "producer": LOCAL_ALPHA_PRODUCER,
            "raw_format": LOCAL_ALPHA_RAW_FORMAT,
            "candidate_commit": candidate,
            "check_id": check.identifier,
            "command": list(check.command),
            "timeout_seconds": check.timeout_seconds,
            "status": entry.get("status"),
        }
        mismatched = [
            key for key, value in expected_fields.items() if observation.get(key) != value
        ]
        digest_values = (observation.get("stdout_digest"), observation.get("stderr_digest"))
        observation_invariants = (
            observation.get("exit_code") == 0
            and observation.get("timed_out") is False
            and observation.get("output_overflow") is False
            and observation.get("error") is None
            and all(
                isinstance(value, int) and 0 <= value <= MAX_CAPTURE_BYTES
                for value in (
                    observation.get("stdout_bytes"),
                    observation.get("stderr_bytes"),
                )
            )
            and all(
                isinstance(value, str)
                and value.startswith("sha256:")
                and len(value) == len("sha256:") + 64
                for value in digest_values
            )
        )
        if entry.get("status") != "PASS" or not observation_invariants:
            mismatched.append("pass_invariants")
        if mismatched:
            issues.append(
                Issue(
                    "release.producer-observation-mismatch",
                    f"raw observation fields do not match for {check.identifier!r}: {mismatched}",
                )
            )
            recorded_statuses.append("ERROR")
        else:
            recorded_statuses.append(str(entry.get("status")))

    if issues:
        return "ERROR", issues
    if aggregate_status(recorded_statuses) != "PASS":
        return aggregate_status(recorded_statuses), issues

    rerun_statuses: list[str] = []
    for check in LOCAL_ALPHA_CHECKS:
        observation = observe_release_check(root, check)
        rerun_statuses.append(str(observation["status"]))
        if observation["status"] != "PASS":
            issues.append(
                Issue(
                    "release.producer-rerun-failed",
                    f"registered check {check.identifier!r} reran as {observation['status']}",
                )
            )
    return aggregate_status(rerun_statuses), issues
