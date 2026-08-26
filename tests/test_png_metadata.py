from hashlib import sha256

import pytest
from PIL import Image, ImageCms

from stockforge.png_metadata import PngMetadataError, embed_png_metadata, read_embedded_png_metadata


TITLE = "Thai Mango Sticky Rice Dessert with Ripe Mango and Coconut Sauce"
KEYWORDS = (
    "mango sticky rice",
    "khao niew mamuang",
    "Thai dessert",
    "Thai food",
    "sticky rice",
    "ripe mango",
    "coconut sauce",
    "mango dessert",
)


def _make_rgba_source(path):
    image = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    for x in range(8, 24):
        for y in range(8, 24):
            image.putpixel((x, y), (240, 160, 20, 255))
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    image.save(path, format="PNG", icc_profile=profile)


def test_embed_png_metadata_preserves_pixels_alpha_dimensions_and_icc(tmp_path):
    source = tmp_path / "source.png"
    destination = tmp_path / "embedded.png"
    _make_rgba_source(source)

    with Image.open(source) as original:
        original.load()
        pixel_digest = sha256(original.tobytes()).hexdigest()
        alpha_extrema = original.getchannel("A").getextrema()
        icc = original.info["icc_profile"]

    output = embed_png_metadata(
        source=source,
        destination=destination,
        title=TITLE,
        keywords=KEYWORDS,
    )

    assert output == destination.resolve()
    with Image.open(output) as result:
        result.load()
        assert result.mode == "RGBA"
        assert result.size == (32, 32)
        assert sha256(result.tobytes()).hexdigest() == pixel_digest
        assert result.getchannel("A").getextrema() == alpha_extrema
        assert result.info["icc_profile"] == icc

    metadata = read_embedded_png_metadata(output)
    assert metadata["title"] == TITLE
    assert metadata["keywords"] == ", ".join(KEYWORDS)
    assert metadata["category"] == "Food"
    assert metadata["ai_disclosure"] == "required"
    assert "dc:title" in (metadata["xmp"] or "")


def test_embed_png_metadata_rejects_non_rgba_source(tmp_path):
    source = tmp_path / "rgb.png"
    Image.new("RGB", (32, 32), "white").save(source)

    with pytest.raises(PngMetadataError, match="RGBA"):
        embed_png_metadata(
            source=source,
            destination=tmp_path / "out.png",
            title=TITLE,
            keywords=KEYWORDS,
        )


def test_embed_png_metadata_rejects_duplicate_keywords(tmp_path):
    source = tmp_path / "source.png"
    _make_rgba_source(source)

    with pytest.raises(PngMetadataError, match="unique"):
        embed_png_metadata(
            source=source,
            destination=tmp_path / "out.png",
            title=TITLE,
            keywords=("mango sticky rice", "Mango Sticky Rice", "Thai dessert", "Thai food", "sticky rice"),
        )
