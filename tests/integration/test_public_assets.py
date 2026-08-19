import hashlib
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        length = struct.unpack(">I", handle.read(4))[0]
        chunk_type = handle.read(4)
        data = handle.read(length)
    assert signature == b"\x89PNG\r\n\x1a\n"
    assert chunk_type == b"IHDR"
    return struct.unpack(">II", data[:8])


def test_social_preview_has_expected_source_and_export_contract():
    source = REPO_ROOT / "assets/source/social-preview.svg"
    export = REPO_ROOT / "assets/exported/social-preview.png"

    root = ET.parse(source).getroot()
    assert root.attrib["viewBox"] == "0 0 1280 640"
    assert root.find("{http://www.w3.org/2000/svg}title") is not None
    assert root.find("{http://www.w3.org/2000/svg}desc") is not None
    assert _png_dimensions(export) == (1280, 640)


def test_analysis_bench_hero_matches_recorded_provenance_digest():
    hero = REPO_ROOT / "assets/generated/analysis-bench-hero.png"
    provenance = (REPO_ROOT / "assets/PROVENANCE.md").read_text(encoding="utf-8")

    digest = hashlib.sha256(hero.read_bytes()).hexdigest()
    width, height = _png_dimensions(hero)

    assert f"sha256:{digest}" in provenance
    assert (width, height) == (1983, 793)
    assert "not a product screenshot" in provenance
