#!/usr/bin/env python3
"""Generate the recorded method-suite screening report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from method_council.evaluation import write_evaluation_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--inventory", type=Path, default=Path("evals/methods/inventory.json"))
    parser.add_argument("--output", type=Path, default=Path("evals/methods/screening-report.json"))
    args = parser.parse_args()
    report = write_evaluation_report(args.root, args.inventory, args.output)
    print(json.dumps(report["totals"], indent=2, sort_keys=True))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
