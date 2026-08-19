from method_council.evidence import canonical_json_digest, content_digest, validate_result_evidence


def test_canonical_digest_is_key_order_independent():
    assert canonical_json_digest({"a": 1, "b": 2}) == canonical_json_digest({"b": 2, "a": 1})
    assert content_digest("hello").startswith("sha256:")


def test_result_evidence_must_be_bound_to_run():
    run = {
        "run_id": "run-12345678",
        "methods": ["key-assumptions-check"],
        "evidence": [{"id": "ev-1", "digest": "sha256:" + "0" * 64}],
    }
    result = {
        "run_id": "run-12345678",
        "method_id": "key-assumptions-check",
        "findings": [
            {
                "type": "fact",
                "evidence_refs": ["missing"],
                "counterevidence_refs": [],
            },
            {"type": "inference", "evidence_refs": []},
            {"type": "unknown", "evidence_refs": []},
        ],
    }

    issues = validate_result_evidence(result, run)
    codes = [issue.code for issue in issues]

    assert "evidence.reference-unbound" in codes
    assert "evidence.required" in codes
    assert codes.count("evidence.required") == 1


def test_result_run_and_method_must_match_manifest():
    issues = validate_result_evidence(
        {"run_id": "other", "method_id": "other-method", "findings": []},
        {"run_id": "run", "methods": ["selected-method"], "evidence": []},
    )

    assert {issue.code for issue in issues} == {"evidence.run-mismatch", "evidence.method-unbound"}
