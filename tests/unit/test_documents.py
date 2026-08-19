import pytest

from method_council.documents import MAX_DOCUMENT_BYTES, DocumentError, load_document


def test_structured_document_size_is_bounded_before_parsing(tmp_path):
    oversized = tmp_path / "oversized.json"
    with oversized.open("wb") as handle:
        handle.truncate(MAX_DOCUMENT_BYTES + 1)

    with pytest.raises(DocumentError, match="byte limit"):
        load_document(oversized)
