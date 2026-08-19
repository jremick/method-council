#!/usr/bin/env python3
"""Validate the public-safe Wave 1 evaluation fixture inventory.

This helper is deliberately standard-library only. It performs no provider or
network calls and does not write files.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
ACTIVITIES = {"analyse", "investigate", "decide", "forecast", "architect", "review"}
RIGOR_LIMITS = {"rapid": (1, 2), "standard": (3, 4), "intensive": (4, 6)}
STATUSES = {"PASS", "FAIL", "ERROR", "INCOMPLETE"}
STATUS_PRECEDENCE = {"PASS": 1, "INCOMPLETE": 2, "ERROR": 3, "FAIL": 4}
SIDE_CONDITIONS = ("DEGRADED", "CORRELATED", "SKIPPED")
CATEGORIES = {"representative", "adversarial", "failure"}
ROUTE_SOURCES = {"profile", "model-proposal", "user-explicit"}
SYNTHESIS_MODES = {"judgment", "judgment-with-limitations", "preserve-split", "halt"}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
REASON_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")


class FixtureError(ValueError):
    """A validation error that never includes fixture content."""

    def __init__(self, path: Path, field: str, reason: str) -> None:
        super().__init__(reason)
        self.path = path
        self.field = field
        self.reason = reason


def _error(path: Path, field: str, reason: str) -> None:
    raise FixtureError(path, field, reason)


def _object(value: Any, path: Path, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _error(path, field, "must be an object")
    return value


def _string(value: Any, path: Path, field: str, *, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value.strip()) < minimum:
        _error(path, field, "must be a non-empty string")
    return value


def _string_list(value: Any, path: Path, field: str, *, minimum: int = 0) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        _error(path, field, "must be a string array of the required length")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        _error(path, field, "must contain only non-empty strings")
    if len(value) != len(set(value)):
        _error(path, field, "must not contain duplicates")
    return value


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return _object(json.load(handle), path, "$")
    except json.JSONDecodeError as exc:
        _error(path, "$", f"invalid JSON at line {exc.lineno}, column {exc.colno}")
    except OSError:
        _error(path, "$", "could not be read")


def aggregate_status(gate_statuses: list[dict[str, Any]]) -> str:
    """Return the strongest primary status using the canonical precedence."""

    return max(
        (gate["status"] for gate in gate_statuses),
        key=STATUS_PRECEDENCE.__getitem__,
    )


def _validate_route(
    route: dict[str, Any],
    rigor: str,
    path: Path,
) -> None:
    source = route.get("source")
    if source not in ROUTE_SOURCES:
        _error(path, "input.route.source", "uses an unsupported route source")

    methods = _string_list(route.get("methods"), path, "input.route.methods", minimum=1)
    if any(ID_PATTERN.fullmatch(method_id) is None for method_id in methods):
        _error(path, "input.route.methods", "contains an invalid method identifier")

    minimum, maximum = RIGOR_LIMITS[rigor]
    if not minimum <= len(methods) <= maximum:
        _error(path, "input.route.methods", "method count is outside the rigor limit")

    if source == "profile":
        profile_id = route.get("profile_id")
        if not isinstance(profile_id, str) or ID_PATTERN.fullmatch(profile_id) is None:
            _error(path, "input.route.profile_id", "profile routes require a valid profile ID")
    elif "profile_id" in route:
        _error(path, "input.route.profile_id", "is only allowed for profile routes")


def _validate_privacy(privacy: dict[str, Any], path: Path) -> None:
    required_false = (
        "raw_prompt_persisted",
        "hidden_chain_of_thought_requested",
        "external_calls_allowed",
    )
    for field in required_false:
        if privacy.get(field) is not False:
            _error(path, f"input.privacy.{field}", "must be false for offline public fixtures")
    if set(privacy) != set(required_false):
        _error(path, "input.privacy", "contains unsupported fields")


def _validate_gates(value: Any, path: Path) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        _error(path, "input.gate_statuses", "must be a non-empty array")

    gates: list[dict[str, Any]] = []
    names: set[str] = set()
    for index, item in enumerate(value):
        field = f"input.gate_statuses[{index}]"
        gate = _object(item, path, field)
        if set(gate) != {"gate", "status", "reason_code"}:
            _error(path, field, "must contain only gate, status, and reason_code")
        name = _string(gate.get("gate"), path, f"{field}.gate")
        if ID_PATTERN.fullmatch(name) is None or name in names:
            _error(path, f"{field}.gate", "must be a unique kebab-case identifier")
        names.add(name)
        if gate.get("status") not in STATUSES:
            _error(path, f"{field}.status", "uses an unsupported primary status")
        reason = gate.get("reason_code")
        if not isinstance(reason, str) or REASON_PATTERN.fullmatch(reason) is None:
            _error(path, f"{field}.reason_code", "must be an upper-snake-case code")
        gates.append(gate)
    return gates


def _validate_side_conditions(value: Any, path: Path, field: str) -> list[str]:
    conditions = _string_list(value, path, field)
    if any(condition not in SIDE_CONDITIONS for condition in conditions):
        _error(path, field, "contains an unsupported side condition")
    canonical = [condition for condition in SIDE_CONDITIONS if condition in conditions]
    if conditions != canonical:
        _error(path, field, "must use canonical DEGRADED, CORRELATED, SKIPPED order")
    return conditions


def validate_fixture(path: Path, expected_id: str) -> dict[str, Any]:
    fixture = _load_json(path)
    required = {
        "schema_version",
        "id",
        "title",
        "category",
        "public_safe",
        "input",
        "expected",
    }
    if set(fixture) != required:
        _error(path, "$", "must contain exactly the fixture contract fields")
    if fixture.get("schema_version") != SCHEMA_VERSION:
        _error(path, "schema_version", "uses an unsupported schema version")
    if fixture.get("id") != expected_id or path.stem != expected_id:
        _error(path, "id", "must match the inventory ID and filename")
    if ID_PATTERN.fullmatch(expected_id) is None:
        _error(path, "id", "must be a kebab-case identifier")
    _string(fixture.get("title"), path, "title", minimum=8)
    if fixture.get("category") not in CATEGORIES:
        _error(path, "category", "uses an unsupported fixture category")
    if fixture.get("public_safe") is not True:
        _error(path, "public_safe", "must be true")

    fixture_input = _object(fixture.get("input"), path, "input")
    required_input = {
        "activity",
        "rigor",
        "question",
        "route",
        "privacy",
        "gate_statuses",
        "side_conditions",
        "scenario_data",
    }
    if set(fixture_input) != required_input:
        _error(path, "input", "must contain exactly the input contract fields")
    if fixture_input.get("activity") not in ACTIVITIES:
        _error(path, "input.activity", "uses an unsupported activity")
    rigor = fixture_input.get("rigor")
    if rigor not in RIGOR_LIMITS:
        _error(path, "input.rigor", "uses an unsupported rigor")
    _string(fixture_input.get("question"), path, "input.question", minimum=20)
    _validate_route(_object(fixture_input.get("route"), path, "input.route"), rigor, path)
    _validate_privacy(_object(fixture_input.get("privacy"), path, "input.privacy"), path)
    gates = _validate_gates(fixture_input.get("gate_statuses"), path)
    input_conditions = _validate_side_conditions(
        fixture_input.get("side_conditions"), path, "input.side_conditions"
    )
    _object(fixture_input.get("scenario_data"), path, "input.scenario_data")

    expected = _object(fixture.get("expected"), path, "expected")
    required_expected = {
        "primary_status",
        "side_conditions",
        "route_allowed",
        "synthesis_mode",
        "reason_codes",
        "must_preserve",
        "must_not_claim",
    }
    if set(expected) != required_expected:
        _error(path, "expected", "must contain exactly the expected contract fields")
    calculated = aggregate_status(gates)
    if expected.get("primary_status") != calculated:
        _error(path, "expected.primary_status", "does not match deterministic precedence")
    expected_conditions = _validate_side_conditions(
        expected.get("side_conditions"), path, "expected.side_conditions"
    )
    if expected_conditions != input_conditions:
        _error(path, "expected.side_conditions", "does not preserve input side conditions")
    if not isinstance(expected.get("route_allowed"), bool):
        _error(path, "expected.route_allowed", "must be boolean")
    mode = expected.get("synthesis_mode")
    if mode not in SYNTHESIS_MODES:
        _error(path, "expected.synthesis_mode", "uses an unsupported synthesis mode")
    if calculated in {"FAIL", "ERROR"} and mode != "halt":
        _error(path, "expected.synthesis_mode", "FAIL and ERROR outcomes must halt")
    if calculated == "PASS" and mode in {"halt", "judgment-with-limitations"}:
        _error(path, "expected.synthesis_mode", "PASS outcomes cannot halt or imply incompleteness")
    if calculated == "INCOMPLETE" and mode != "judgment-with-limitations":
        _error(path, "expected.synthesis_mode", "INCOMPLETE outcomes require explicit limitations")

    reason_codes = _string_list(
        expected.get("reason_codes"), path, "expected.reason_codes", minimum=1
    )
    gate_codes = {gate["reason_code"] for gate in gates}
    if any(REASON_PATTERN.fullmatch(code) is None for code in reason_codes):
        _error(path, "expected.reason_codes", "contains an invalid reason code")
    if not set(reason_codes).issubset(gate_codes):
        _error(path, "expected.reason_codes", "must reference only observed gate reason codes")
    _string_list(expected.get("must_preserve"), path, "expected.must_preserve", minimum=1)
    _string_list(expected.get("must_not_claim"), path, "expected.must_not_claim", minimum=1)
    return fixture


def validate_inventory(fixtures_dir: Path) -> list[dict[str, Any]]:
    fixtures_dir = fixtures_dir.resolve()
    inventory_path = fixtures_dir / "inventory.json"
    inventory = _load_json(inventory_path)
    if set(inventory) != {"schema_version", "fixtures"}:
        _error(inventory_path, "$", "must contain schema_version and fixtures only")
    if inventory.get("schema_version") != SCHEMA_VERSION:
        _error(inventory_path, "schema_version", "uses an unsupported schema version")
    entries = inventory.get("fixtures")
    if not isinstance(entries, list) or len(entries) != 8:
        _error(inventory_path, "fixtures", "must inventory exactly eight Wave 1 fixtures")

    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, item in enumerate(entries):
        field = f"fixtures[{index}]"
        entry = _object(item, inventory_path, field)
        if set(entry) != {"id", "file", "purpose"}:
            _error(inventory_path, field, "must contain id, file, and purpose only")
        fixture_id = _string(entry.get("id"), inventory_path, f"{field}.id")
        filename = _string(entry.get("file"), inventory_path, f"{field}.file")
        _string(entry.get("purpose"), inventory_path, f"{field}.purpose", minimum=12)
        if fixture_id in seen_ids or filename in seen_files:
            _error(inventory_path, field, "contains a duplicate ID or filename")
        seen_ids.add(fixture_id)
        seen_files.add(filename)
        if filename != f"{fixture_id}.json" or Path(filename).name != filename:
            _error(inventory_path, f"{field}.file", "must match the ID without path traversal")
        candidate = fixtures_dir / filename
        fixture_path = candidate.resolve()
        try:
            fixture_path.relative_to(fixtures_dir)
        except ValueError:
            _error(inventory_path, f"{field}.file", "resolves outside the fixture directory")
        if candidate.is_symlink() or not fixture_path.is_file():
            _error(inventory_path, f"{field}.file", "must be a regular fixture file")
        validated.append(validate_fixture(fixture_path, fixture_id))

    discovered = {
        path.name for path in fixtures_dir.glob("*.json") if path.name != "inventory.json"
    }
    if discovered != seen_files:
        _error(inventory_path, "fixtures", "does not exactly match fixture JSON files on disk")
    return validated


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    default_dir = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
    parser.add_argument("--fixtures-dir", type=Path, default=default_dir)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        fixtures = validate_inventory(args.fixtures_dir)
    except FixtureError as exc:
        try:
            relative = exc.path.resolve().relative_to(Path.cwd().resolve())
        except ValueError:
            relative = Path(exc.path.name)
        print(f"ERROR path={relative} field={exc.field} issue={exc.reason}", file=sys.stderr)
        return 1

    statuses = Counter(fixture["expected"]["primary_status"] for fixture in fixtures)
    categories = Counter(fixture["category"] for fixture in fixtures)
    status_text = ",".join(f"{name}:{statuses[name]}" for name in sorted(statuses))
    category_text = ",".join(f"{name}:{categories[name]}" for name in sorted(categories))
    print(f"PASS fixtures={len(fixtures)} statuses={status_text} categories={category_text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
