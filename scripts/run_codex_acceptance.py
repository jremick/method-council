#!/usr/bin/env python3
"""Run one public-safe acceptance task through subscription-authenticated Codex."""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO, Final

from method_council.acceptance import (
    TASKS,
    build_acceptance_prompt,
    copy_expected_artifacts,
    detect_tracked_mutations,
    expected_model_artifacts,
    extract_git_snapshot,
    git_source_identity,
    task_spec,
    tracked_file_state,
    validate_run_id,
    verify_acceptance,
)
from method_council.evidence import content_digest, file_digest
from method_council.run import verify_run

_SYNC_COMMAND: Final = ["uv", "sync", "--frozen", "--all-groups"]
_EVENT_STREAM_MAX_BYTES: Final = 16 * 1024 * 1024
_ENV_ALLOWLIST: Final = {
    "HOME",
    "LANG",
    "LC_ALL",
    "LOGNAME",
    "PATH",
    "SHELL",
    "TERM",
    "TMPDIR",
    "USER",
}


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _prompt(task_id: str, profile: str, task_path: str, run_path: str, run_id: str) -> str:
    """Compatibility wrapper for the frozen prompt contract."""

    return build_acceptance_prompt(task_id, profile, task_path, run_path, run_id)


def _resolve_executable(command: str) -> tuple[Path, dict[str, str]]:
    located = shutil.which(command)
    if not located:
        raise RuntimeError(f"required executable is unavailable: {command}")
    resolved = Path(located).resolve(strict=True)
    if not resolved.is_file() or resolved.is_symlink():
        raise RuntimeError(f"resolved executable is not a regular file: {resolved}")
    return resolved, {
        "command": command,
        "resolved_basename": resolved.name,
        "resolved_path_digest": content_digest(str(resolved)),
        "executable_digest": file_digest(resolved),
    }


def _codex_state(executable: Path | None = None) -> tuple[str, str]:
    codex = executable or _resolve_executable("codex")[0]
    version = subprocess.run(
        [str(codex), "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    ).stdout.strip()
    login_result = subprocess.run(
        [str(codex), "login", "status"],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    login = "\n".join(
        part.strip() for part in (login_result.stdout, login_result.stderr) if part.strip()
    )
    if login != "Logged in using ChatGPT":
        raise RuntimeError("Codex is not observably signed in using ChatGPT")
    return version, "chatgpt"


def _event_summary(
    stream: BinaryIO,
) -> tuple[dict[str, int], list[str], int, str | None]:
    counts: Counter[str] = Counter()
    sequence: list[str] = []
    non_json_line_count = 0
    final_digest: str | None = None
    stream.seek(0)
    for encoded_line in stream:
        raw_line = encoded_line.decode("utf-8", errors="replace")
        try:
            event = json.loads(raw_line)
        except json.JSONDecodeError:
            non_json_line_count += 1
            continue
        event_type = str(event.get("type", "unknown"))
        counts[event_type] += 1
        sequence.append(event_type)
        item = event.get("item")
        if (
            event_type == "item.completed"
            and isinstance(item, dict)
            and item.get("type") == "agent_message"
            and isinstance(item.get("text"), str)
        ):
            final_digest = content_digest(item["text"])
    return dict(sorted(counts.items())), sequence, non_json_line_count, final_digest


def _kill_process_group(process_id: int) -> None:
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process_id, signal.SIGKILL)


def _run_codex(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    prompt: str,
    timeout: int,
    stream: BinaryIO,
) -> tuple[int, bool, bool]:
    """Run Codex in its own process group while bounding and draining output."""

    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=environment,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    assert process.stdin is not None and process.stdout is not None
    state = {"written": 0, "truncated": False}

    def drain() -> None:
        for chunk in iter(lambda: process.stdout.read(64 * 1024), b""):
            remaining = _EVENT_STREAM_MAX_BYTES - state["written"]
            if remaining > 0:
                retained = chunk[:remaining]
                stream.write(retained)
                state["written"] += len(retained)
            if len(chunk) > max(remaining, 0):
                state["truncated"] = True

    reader = threading.Thread(target=drain, name="codex-event-drain", daemon=True)
    reader.start()
    try:
        try:
            process.stdin.write(prompt.encode("utf-8"))
            process.stdin.close()
        except BrokenPipeError:
            pass
        try:
            process.wait(timeout=timeout)
            exit_code = int(process.returncode)
            timed_out = False
        except subprocess.TimeoutExpired:
            timed_out = True
            exit_code = 124
    finally:
        _kill_process_group(process.pid)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _kill_process_group(process.pid)
        reader.join(timeout=5)
        process.stdout.close()
    if reader.is_alive():
        raise RuntimeError("Codex event drain did not terminate after process-group shutdown")
    stream.flush()
    return exit_code, timed_out, bool(state["truncated"])


def _sanitized_environment() -> dict[str, str]:
    environment = {key: value for key, value in os.environ.items() if key in _ENV_ALLOWLIST}
    environment["CI"] = "1"
    environment["UV_NO_PROGRESS"] = "1"
    return environment


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=sorted(TASKS))
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout", type=int, default=1200)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validate_run_id(args.run_id)
    root = _root()
    profile, task_path = task_spec(args.task)
    run_path = f"runs/acceptance/{args.run_id}"
    run_dir = root / run_path
    if run_dir.exists():
        raise RuntimeError(f"refusing to reuse existing run directory: {run_path}")
    prompt = build_acceptance_prompt(args.task, profile, task_path, run_path, args.run_id)
    display_command = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "--json",
        "--ignore-user-config",
        "--sandbox",
        "workspace-write",
        "-C",
        ".",
        "-",
    ]
    source = git_source_identity(root)
    if args.dry_run:
        print(
            json.dumps(
                {
                    "valid": True,
                    "task": args.task,
                    "profile": profile,
                    "run_path": run_path,
                    "source_commit": source["source_commit"],
                    "source_tree": source["source_tree"],
                    "command": display_command,
                    "sync_command": _SYNC_COMMAND,
                    "prompt_digest": content_digest(prompt),
                    "raw_prompt_persisted": False,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    codex, codex_identity = _resolve_executable("codex")
    uv, _ = _resolve_executable("uv")
    version, auth_state = _codex_state(codex)
    environment = _sanitized_environment()
    execution_issues: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="method-council-acceptance-") as raw:
        temporary_root = Path(raw)
        execution_root = temporary_root / "execution-source"
        extract_git_snapshot(root, source["source_commit"], execution_root)
        baseline = tracked_file_state(execution_root, source["entries"])
        expected_paths = expected_model_artifacts(execution_root, profile)

        try:
            sync = subprocess.run(
                [str(uv), "sync", "--frozen", "--all-groups"],
                cwd=execution_root,
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=300,
            )
            sync_exit_code = sync.returncode
        except subprocess.TimeoutExpired:
            sync_exit_code = 124
        command = [str(codex), *display_command[1:]]
        started_at = _timestamp()
        started = time.monotonic()
        timed_out = False
        event_counts: dict[str, int] = {}
        event_sequence: list[str] = []
        non_json_line_count = 0
        event_stream_truncated = False
        final_message_digest: str | None = None
        if sync_exit_code == 0:
            with tempfile.TemporaryFile(mode="w+b") as stream:
                exit_code, timed_out, event_stream_truncated = _run_codex(
                    command,
                    cwd=execution_root,
                    environment=environment,
                    prompt=prompt,
                    timeout=args.timeout,
                    stream=stream,
                )
                (
                    event_counts,
                    event_sequence,
                    non_json_line_count,
                    final_message_digest,
                ) = _event_summary(stream)
        else:
            exit_code = 125
        completed_at = _timestamp()
        duration_seconds = round(time.monotonic() - started, 3)
        source_mutations = detect_tracked_mutations(execution_root, baseline)

        host_run = temporary_root / "host-output" / args.run_id
        host_run.parent.mkdir(parents=True)
        model_ledger: list[dict[str, str]] = []
        if not source_mutations:
            model_ledger, copy_issues = copy_expected_artifacts(
                execution_root / run_path,
                host_run,
                expected_paths,
            )
            execution_issues.extend(issue.as_dict() for issue in copy_issues)
            if not host_run.exists():
                host_run.mkdir(parents=True)
        else:
            host_run.mkdir(parents=True)
            execution_issues.append(
                {
                    "code": "acceptance.source-mutation",
                    "message": "tracked source mutation rejected model artifacts",
                    "path": "/source_mutations",
                }
            )

        verification_root = temporary_root / "verification-source"
        extract_git_snapshot(root, source["source_commit"], verification_root)
        pristine_run = verification_root / run_path
        pristine_run.mkdir(parents=True, exist_ok=True)
        for entry in model_ledger:
            relative = entry["path"]
            destination = pristine_run / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(host_run / relative, destination, follow_symlinks=False)
        run_verdict = verify_run(pristine_run, root=verification_root)
        verification_path = host_run / "verification.json"
        _write_json(verification_path, run_verdict)

        execution = {
            "schema_version": "0.1.0",
            "kind": "codex-subscription-acceptance-evidence",
            "attestation": "unsigned-local-recorder",
            "run_id": args.run_id,
            "task": args.task,
            "profile": profile,
            "run_path": run_path,
            "source_commit": source["source_commit"],
            "source_tree": source["source_tree"],
            "source_manifest_digest": source["source_manifest_digest"],
            "source_mutations": source_mutations,
            "task_digest": file_digest(execution_root / task_path),
            "prompt_digest": content_digest(prompt),
            "model_artifact_ledger": model_ledger,
            "raw_prompt_persisted": False,
            "raw_event_stream_persisted": False,
            "codex_cli_version": version,
            "codex_executable": codex_identity,
            "authentication_observed": auth_state,
            "model_requested": None,
            "model_observed": None,
            "uv_sync": {"command": _SYNC_COMMAND, "exit_code": sync_exit_code},
            "started_at": started_at,
            "completed_at": completed_at,
            "duration_seconds": duration_seconds,
            "process_exit_code": exit_code,
            "timed_out": timed_out,
            "event_counts": event_counts,
            "event_sequence": event_sequence,
            "non_json_line_count": non_json_line_count,
            "event_stream_truncated": event_stream_truncated,
            "final_message_digest": final_message_digest,
            "verification_digest": file_digest(verification_path),
            "verification_valid": bool(run_verdict["valid"]),
            "verification_status": run_verdict["status"],
        }
        _write_json(host_run / "host-execution.json", execution)
        acceptance_verdict = verify_acceptance(
            host_run,
            root=root,
            require_recorded_verdict=False,
        )
        _write_json(host_run / "acceptance-verdict.json", acceptance_verdict)

        run_dir.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix=f".{args.run_id}-publish-", dir=run_dir.parent
        ) as publish_parent:
            publish_candidate = Path(publish_parent) / args.run_id
            shutil.copytree(host_run, publish_candidate, symlinks=False)
            os.replace(publish_candidate, run_dir)

    acceptance_verdict = verify_acceptance(run_dir, root=root)

    result = {
        "valid": bool(acceptance_verdict["valid"]),
        "task": args.task,
        "run_path": run_path,
        "source_commit": source["source_commit"],
        "source_tree": source["source_tree"],
        "process_exit_code": exit_code,
        "timed_out": timed_out,
        "verification": run_verdict,
        "acceptance_verification": acceptance_verdict,
        "execution_issues": execution_issues,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
