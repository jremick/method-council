#!/usr/bin/env python3
"""Build candidate-bound local-alpha evidence under the ignored runs directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from method_council.release_checks import build_local_alpha_evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "output_dir",
        type=Path,
        help="new or empty output directory under runs/release",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--candidate", default="0.1.0-alpha.1")
    args = parser.parse_args()
    result = build_local_alpha_evidence(args.root, args.output_dir, candidate_label=args.candidate)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
