from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skill" / "method-council"
ADAPTER = ROOT / "adapters" / "codex"


def _frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match is not None, f"missing YAML frontmatter: {path}"
    return yaml.safe_load(match.group(1))


def _relative_markdown_links(path: Path) -> list[Path]:
    text = path.read_text(encoding="utf-8")
    targets = re.findall(r"\[[^]]+\]\(([^)]+)\)", text)
    return [path.parent / target for target in targets if "://" not in target]


def test_skill_entrypoint_and_references_are_packaged() -> None:
    skill_path = SKILL / "SKILL.md"
    metadata = _frontmatter(skill_path)

    assert metadata["name"] == "method-council"
    assert isinstance(metadata["description"], str)
    assert 40 <= len(metadata["description"]) <= 500
    assert all(path.is_file() for path in _relative_markdown_links(skill_path))


def test_openai_interface_is_consistent_and_has_no_remote_dependency() -> None:
    config = yaml.safe_load((SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8"))

    assert config["interface"]["display_name"] == "Method Council"
    assert "$method-council" in config["interface"]["default_prompt"]
    assert "dependencies" not in config


def test_adapter_declares_fail_closed_codex_defaults() -> None:
    manifest = yaml.safe_load((ADAPTER / "adapter.yaml").read_text(encoding="utf-8"))

    assert manifest["kind"] == "adapter-compiler-input"
    assert manifest["host"]["family"] == "codex"
    assert manifest["host"]["authentication"] == "chatgpt-subscription"
    assert manifest["host"]["external_provider_dependencies"] == []
    assert manifest["defaults"] == {
        "external_provider_calls": False,
        "tool_side_effects": False,
        "raw_prompt_persistence": False,
        "hidden_chain_of_thought_requested": False,
        "same_host_passes_correlated": True,
        "default_rigor": "standard",
        "execution_strategy": "single-gpt",
        "multi_model_execution_plan": "optional-user-authorised",
    }
    assert manifest["activities"] == [
        "analyse",
        "investigate",
        "decide",
        "forecast",
        "architect",
        "review",
    ]
    assert manifest["command_contract"] == [
        "validate",
        "route",
        "prepare",
        "check",
        "aggregate",
        "verify-run",
        "verify-acceptance",
        "verify-release",
    ]


def test_adapter_templates_and_canonical_inputs_resolve() -> None:
    manifest = yaml.safe_load((ADAPTER / "adapter.yaml").read_text(encoding="utf-8"))

    for relative in manifest["canonical_inputs"]:
        target = ROOT / relative
        assert target.exists(), f"missing canonical input: {relative}"

    for relative in manifest["templates"].values():
        target = ROOT / relative
        assert target.is_file(), f"missing adapter template: {relative}"

    required_metadata = set(manifest["compiler"]["generated_metadata_required"])
    assert required_metadata == {
        "canonical_input_digest",
        "generator_id",
        "generator_version",
    }
    assert manifest["skill_projection"] == {
        "target": ".agents/skills/method-council",
        "generator_id": "method-council-agent-skill-sync",
        "generator_version": "0.2.0",
        "metadata": ".agents/skills/method-council/.projection.json",
    }


def test_templates_keep_untrusted_data_in_explicit_boundaries() -> None:
    method_task = (ADAPTER / "templates" / "method-task.md").read_text(encoding="utf-8")
    challenge_task = (ADAPTER / "templates" / "challenge-task.md").read_text(encoding="utf-8")
    synthesis_task = (ADAPTER / "templates" / "synthesis-task.md").read_text(encoding="utf-8")

    assert "<question>\n{{question}}\n</question>" in method_task
    assert "<evidence-manifest>\n{{evidence_manifest}}\n</evidence-manifest>" in method_task
    assert "<checked-method-results>" in challenge_task
    assert "<deterministic-aggregation>" in synthesis_task
    assert "{{output_path}}" in method_task
    assert "{{output_path}}" in challenge_task
    assert "{{output_path}}" in synthesis_task
    for template in (method_task, challenge_task):
        assert "{{adapter}}" in template
        assert "{{provider_state}}" in template
        assert "{{model_requested}}" in template
        assert "{{model_observed}}" in template
        assert "{{external_api_calls}}" in template
        assert "{{correlation_group}}" in template
        assert "CORRELATED" in template
    assert "method-council verify-run" in synthesis_task
