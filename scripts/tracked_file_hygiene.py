#!/usr/bin/env python3
"""Scan tracked files for public-release hygiene risks without exposing content.

The scanner performs no network calls and writes nothing. Findings contain
only repository-relative paths and category names; matched values are never
returned or printed.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_SCAN_BYTES = 8 * 1024 * 1024
ALLOWED_ENV_SUFFIXES = {".example", ".sample", ".template"}
SENSITIVE_EXTENSIONS = {".key", ".p12", ".pfx"}

CONTENT_PATTERNS: tuple[tuple[str, re.Pattern[bytes]], ...] = (
    (
        "private-key-material",
        re.compile(b"-" * 5 + rb"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY" + b"-" * 5),
    ),
    ("github-token", re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("openai-style-token", re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("aws-access-key", re.compile(rb"\bAKIA[0-9A-Z]{16}\b")),
    (
        "credential-assignment",
        re.compile(
            rb"(?i)[\"']?(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)"
            rb"[\"']?\s*[:=]\s*[\"']?"
            rb"(?!(?:example|placeholder|redacted|dummy|test)(?:[\"']|\b))"
            rb"[A-Za-z0-9_./+=-]{12,}"
        ),
    ),
    ("credential-in-url", re.compile(rb"https?://[^/\s:@]+:[^/\s@]+@")),
    ("local-user-path", re.compile(rb"/(?:Users|home)/[A-Za-z0-9._-]+/")),
    ("windows-user-path", re.compile(rb"[A-Za-z]:\\Users\\[^\\\r\n]+\\")),
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    category: str


@dataclass(frozen=True)
class ScanResult:
    tracked_files: int
    scanned_text_files: int
    findings: tuple[Finding, ...]


def _tracked_paths(repo: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [
        part.decode("utf-8", "surrogateescape") for part in completed.stdout.split(b"\0") if part
    ]


def _path_categories(relative: str) -> set[str]:
    categories: set[str] = set()
    name = Path(relative).name.lower()
    if name == ".env" or (
        name.startswith(".env.")
        and not any(name.endswith(suffix) for suffix in ALLOWED_ENV_SUFFIXES)
    ):
        categories.add("tracked-environment-file")
    if Path(name).suffix in SENSITIVE_EXTENSIONS:
        categories.add("tracked-private-key-file")
    return categories


def scan_tracked(repo: Path) -> ScanResult:
    repo = repo.resolve()
    tracked = _tracked_paths(repo)
    findings: set[Finding] = set()
    scanned_text_files = 0

    for relative in tracked:
        for category in _path_categories(relative):
            findings.add(Finding(relative, category))

        candidate = repo / relative
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            findings.add(Finding(relative, "tracked-path-unreadable"))
            continue
        try:
            resolved.relative_to(repo)
        except ValueError:
            findings.add(Finding(relative, "tracked-symlink-escape"))
            continue
        if not resolved.is_file():
            continue
        try:
            size = resolved.stat().st_size
        except OSError:
            findings.add(Finding(relative, "tracked-path-unreadable"))
            continue
        if size > MAX_SCAN_BYTES:
            findings.add(Finding(relative, "unscanned-large-file"))
            continue
        try:
            data = resolved.read_bytes()
        except OSError:
            findings.add(Finding(relative, "tracked-path-unreadable"))
            continue
        if b"\0" in data[:8192]:
            continue
        scanned_text_files += 1
        for category, pattern in CONTENT_PATTERNS:
            if pattern.search(data) is not None:
                findings.add(Finding(relative, category))

    return ScanResult(
        tracked_files=len(tracked),
        scanned_text_files=scanned_text_files,
        findings=tuple(sorted(findings)),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    default_repo = Path(__file__).resolve().parents[1]
    parser.add_argument("--repo", type=Path, default=default_repo)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = scan_tracked(args.repo)
    except (OSError, subprocess.CalledProcessError):
        print("ERROR category=tracked-file-inventory-unavailable", file=sys.stderr)
        return 2

    if args.as_json:
        payload = {
            "status": "FAIL" if result.findings else "PASS",
            "tracked_files": result.tracked_files,
            "scanned_text_files": result.scanned_text_files,
            "findings": [asdict(finding) for finding in result.findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif result.findings:
        print(
            f"FAIL tracked_files={result.tracked_files} findings={len(result.findings)}",
            file=sys.stderr,
        )
        for finding in result.findings:
            print(f"path={finding.path} category={finding.category}", file=sys.stderr)
    else:
        print(
            f"PASS tracked_files={result.tracked_files} "
            f"scanned_text_files={result.scanned_text_files} findings=0"
        )
    return 1 if result.findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
