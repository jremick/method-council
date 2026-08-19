from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ADAPTER_IDS = ("claude", "gemini")
CAPABILITY_KEYS = {
    "probe",
    "render",
    "launch",
    "collect",
    "timeout-retry",
    "model-observation",
    "cancel",
    "error-normalization",
}
ALLOWED_CAPABILITY_STATUSES = {
    "documented-unverified",
    "designed-unverified",
    "host-enforced-unverified",
    "unverified",
    "unavailable",
}
CANONICAL_INPUTS = {
    "schemas/method.schema.json",
    "schemas/profile.schema.json",
    "schemas/run.schema.json",
    "schemas/method-result.schema.json",
    "schemas/report.schema.json",
    "schemas/provider-status.schema.json",
    "methods/",
    "profiles/",
}


def load_adapter(adapter_id: str) -> dict:
    path = ROOT / "adapters" / adapter_id / "adapter.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_preview_adapters_preserve_canonical_inputs() -> None:
    for adapter_id in ADAPTER_IDS:
        adapter = load_adapter(adapter_id)

        assert adapter["kind"] == "adapter-compiler-input"
        assert adapter["id"] == adapter_id
        assert set(adapter["canonical_inputs"]) == CANONICAL_INPUTS
        assert adapter["compiler"]["id"] == "method-council-adapter-compiler"
        assert set(adapter["compiler"]["generated_metadata_required"]) == {
            "canonical_input_digest",
            "generator_id",
            "generator_version",
        }


def test_preview_adapters_are_disabled_and_make_no_verified_claim() -> None:
    for adapter_id in ADAPTER_IDS:
        adapter = load_adapter(adapter_id)
        support = adapter["support"]

        assert adapter["status"] == "preview"
        assert support["maturity"] == "preview"
        assert support["authentication"] == "unverified"
        assert support["functional_compatibility"] == "unverified"
        assert support["execution_validation"] == "not-run"
        assert support["verified"] is False
        assert adapter["defaults"]["external_provider_calls"] is False
        assert adapter["defaults"]["tool_side_effects"] is False
        assert adapter["capability_interface"]["launch"]["enabled"] is False
        assert adapter["capability_interface"]["collect"]["enabled"] is False


def test_preview_adapters_expose_complete_capability_interface() -> None:
    for adapter_id in ADAPTER_IDS:
        interface = load_adapter(adapter_id)["capability_interface"]

        assert set(interface) == CAPABILITY_KEYS
        for capability in CAPABILITY_KEYS:
            assert interface[capability]["status"] in ALLOWED_CAPABILITY_STATUSES

        assert interface["probe"]["external_call"] is False
        assert interface["launch"]["external_call"] is True
        assert interface["timeout-retry"]["maximum_attempts"] == 1
        assert interface["timeout-retry"]["retry_default"] is False
        assert interface["collect"]["deterministic_validation_required"] is True
        assert interface["model-observation"]["observed_model"]["fallback"] is None


def test_preview_adapter_sources_are_primary_and_claim_bounded() -> None:
    expected_domains = {
        "claude": "https://code.claude.com/",
        "gemini": "https://github.com/google-gemini/gemini-cli/",
    }

    for adapter_id in ADAPTER_IDS:
        adapter = load_adapter(adapter_id)
        source_path = ROOT / adapter["sources"]
        source_text = source_path.read_text(encoding="utf-8")

        assert expected_domains[adapter_id] in source_text
        assert "do not prove" in source_text
        assert "No live request" in source_text


def test_preview_adapter_files_contain_no_credentials_or_live_enablement() -> None:
    forbidden = ("api_key:", "token:", "secret:", "enabled: true\n    external_call: true")

    for adapter_id in ADAPTER_IDS:
        text = (ROOT / "adapters" / adapter_id / "adapter.yaml").read_text(encoding="utf-8")
        lowered = text.lower()

        assert not any(item in lowered for item in forbidden)
