import hashlib
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_LINK = re.compile(r"!?\[[^]]*\]\(([^)]+)\)")


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


def test_council_in_practice_sources_and_exports_match():
    diagrams = {
        "council-in-practice.svg": "0 0 1120 760",
        "council-in-practice-complex.svg": "0 0 1120 860",
    }

    for filename, expected_view_box in diagrams.items():
        source = REPO_ROOT / "assets/source" / filename
        export = REPO_ROOT / "assets/exported" / filename

        root = ET.parse(source).getroot()
        title = root.find("{http://www.w3.org/2000/svg}title")
        description = root.find("{http://www.w3.org/2000/svg}desc")
        assert root.attrib["viewBox"] == expected_view_box
        assert title is not None and title.text
        assert description is not None and "source" in description.text.lower()
        assert source.read_bytes() == export.read_bytes()


def test_public_markdown_local_links_resolve_inside_repository():
    markdown_files = [
        *REPO_ROOT.glob("*.md"),
        *(REPO_ROOT / "docs").rglob("*.md"),
        *(REPO_ROOT / "evidence" / "acceptance").glob("*.md"),
    ]

    for markdown in sorted(markdown_files):
        content = markdown.read_text(encoding="utf-8")
        for raw_target in LOCAL_LINK.findall(content):
            target = raw_target.split("#", 1)[0].strip()
            if not target or target.startswith(("https://", "http://", "mailto:")):
                continue
            resolved = (markdown.parent / target).resolve()
            assert resolved.is_relative_to(REPO_ROOT), f"escaping link in {markdown}: {target}"
            assert resolved.exists(), f"missing link target in {markdown}: {target}"
