import pytest

from stockforge.market_discoverability import project_metadata, rank_canonical_keywords


def test_adobe_prioritizes_first_ten_and_accepts_bounded_visual_metadata() -> None:
    report = project_metadata(
        "adobe_stock",
        title="File Management Utility Icon Set",
        keywords=("file management", "folder", "upload", "download", "cloud storage", "sync", "archive", "document", "share", "editable SVG", "utility symbol"),
        category="Technology",
    )
    assert report.valid is True
    assert report.keywords[0] == "file management"
    assert any("first" in warning for warning in report.warnings)


def test_shutterstock_rejects_too_few_keywords_and_requires_category() -> None:
    report = project_metadata(
        "shutterstock",
        title="Folder upload icon",
        keywords=("folder", "upload"),
    )
    assert report.valid is False
    assert any("at least 7" in error for error in report.errors)
    assert any("category" in error for error in report.errors)


def test_freepik_warns_above_preferred_keyword_count_but_keeps_maximum() -> None:
    keywords = tuple(f"term{index}" for index in range(20))
    report = project_metadata("freepik", title="File flow utility icon set", keywords=keywords)
    assert report.valid is True
    assert len(report.keywords) == 20
    assert any("preferred 18" in warning for warning in report.warnings)


def test_exact_duplicates_and_repeated_stems_are_not_silent() -> None:
    report = project_metadata(
        "adobe_stock",
        title="Folder upload icon",
        keywords=("folder", "folder", "folder icon", "folder symbol", "folder graphic", "folder shape", "folder mark", "folder glyph"),
        category="Objects",
    )
    assert report.valid is False
    assert "folder" in report.removed_keywords
    assert any("repeated keyword stems" in error for error in report.errors)


def test_etsy_requires_exactly_thirteen_tags() -> None:
    report = project_metadata(
        "etsy",
        title="File flow utility icon set",
        keywords=tuple(f"tag {index}" for index in range(12)),
        category="Digital",
    )
    assert report.valid is False
    assert any("13" in error for error in report.errors)


def test_rank_canonical_keywords_uses_visible_terms_before_buyer_terms() -> None:
    ranked = rank_canonical_keywords(
        ("web UI icon", "file management", "folder", "upload arrow"),
        visible_terms=("folder", "upload arrow"),
        buyer_job_terms=("file management", "web UI icon"),
    )
    assert ranked[:2] == ("folder", "upload arrow")
    assert set(ranked) == {"web UI icon", "file management", "folder", "upload arrow"}


def test_unknown_platform_fails_closed() -> None:
    with pytest.raises(ValueError, match="Unsupported metadata platform"):
        project_metadata("unknown", title="x", keywords=("x",))
