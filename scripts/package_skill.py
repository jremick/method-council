#!/usr/bin/env python3
"""Build a deterministic Method Council skill ZIP for account upload."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
import zipfile
from pathlib import Path

ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_skill_zip(output: Path) -> None:
    root = _repo_root()
    source = root / "skill" / "method-council"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    files: dict[Path, bytes] = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"skill contains a symbolic link: {path.relative_to(source)}")
        if path.is_file():
            files[Path("method-council") / path.relative_to(source)] = path.read_bytes()
    for catalogue_root in (root / "methods", root / "profiles"):
        for path in sorted(catalogue_root.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"catalogue contains a symbolic link: {path.relative_to(root)}")
            if path.is_file():
                relative = Path("references/catalog") / path.relative_to(root)
                files[Path("method-council") / relative] = path.read_bytes()

    digest = hashlib.sha256()
    for relative, content in sorted(files.items(), key=lambda item: item[0].as_posix()):
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    metadata = {
        "schema_version": "0.1.0",
        "kind": "method-council-account-skill",
        "project_version": project["project"]["version"],
        "bundled_catalogue": True,
        "deterministic_cli_bundled": False,
        "content_digest": f"sha256:{digest.hexdigest()}",
    }
    files[Path("method-council/skill-package.json")] = (
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")

    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative, content in sorted(files.items(), key=lambda item: item[0].as_posix()):
            info = zipfile.ZipInfo(relative.as_posix(), ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    temporary.replace(output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package the Method Council skill as a ZIP.")
    parser.add_argument(
        "--output",
        type=Path,
        default=_repo_root() / "dist" / "method-council-skill.zip",
    )
    args = parser.parse_args(argv)
    try:
        build_skill_zip(args.output.resolve())
    except (OSError, ValueError) as exc:
        print(f"Packaging failed: {exc}", file=sys.stderr)
        return 1
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
