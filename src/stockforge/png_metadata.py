"""Embed marketplace-facing metadata into transparent PNG assets.

PNG metadata is ancillary data: this module writes text/XMP chunks while
preserving decoded RGBA pixels, dimensions, alpha extrema, and the embedded
ICC profile. Marketplace declarations remain the contributor's responsibility.
"""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from xml.sax.saxutils import escape

from PIL import Image, PngImagePlugin


class PngMetadataError(ValueError):
    """Raised when PNG metadata cannot be embedded safely."""


MAX_TITLE_CHARS = 200
MIN_KEYWORDS = 5
MAX_KEYWORDS = 49


def _clean_metadata(title: str, keywords: tuple[str, ...] | list[str]) -> tuple[str, tuple[str, ...]]:
    clean_title = title.strip()
    clean_keywords = tuple(item.strip() for item in keywords if item.strip())
    if not clean_title or len(clean_title) > MAX_TITLE_CHARS:
        raise PngMetadataError(f"PNG metadata title must contain 1-{MAX_TITLE_CHARS} characters.")
    if not MIN_KEYWORDS <= len(clean_keywords) <= MAX_KEYWORDS:
        raise PngMetadataError(f"PNG metadata requires {MIN_KEYWORDS}-{MAX_KEYWORDS} keywords.")
    folded = tuple(item.casefold() for item in clean_keywords)
    if len(set(folded)) != len(folded):
        raise PngMetadataError("PNG metadata keywords must be unique.")
    return clean_title, clean_keywords


def _xmp_packet(*, title: str, keywords: tuple[str, ...], category: str, ai_disclosure: str) -> str:
    title_xml = escape(title)
    description = escape("StockForge transparent food utility asset; verify visual edges and marketplace declarations manually.")
    subject_items = "".join(f"<rdf:li>{escape(item)}</rdf:li>" for item in keywords)
    keyword_text = escape(", ".join(keywords))
    return f'''<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
    xmlns:xmp="http://ns.adobe.com/xap/1.0/"
    xmlns:stockforge="https://stockforge.local/ns/1.0/"
    photoshop:Category="{escape(category)}"
    xmp:CreatorTool="StockForge remote PNG alpha finalizer"
    stockforge:DeliveryFormat="PNG"
    stockforge:AI_Disclosure="{escape(ai_disclosure)}">
   <dc:title><rdf:Alt><rdf:li xml:lang="x-default">{title_xml}</rdf:li></rdf:Alt></dc:title>
   <dc:description><rdf:Alt><rdf:li xml:lang="x-default">{description}</rdf:li></rdf:Alt></dc:description>
   <dc:subject><rdf:Bag>{subject_items}</rdf:Bag></dc:subject>
   <photoshop:SupplementalCategories><rdf:Bag><rdf:li>{escape(category)}</rdf:li></rdf:Bag></photoshop:SupplementalCategories>
   <stockforge:Keywords>{keyword_text}</stockforge:Keywords>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>'''


def _pixel_digest(image: Image.Image) -> str:
    return sha256(image.tobytes()).hexdigest()


def embed_png_metadata(
    *,
    source: str | Path,
    destination: str | Path | None = None,
    title: str,
    keywords: tuple[str, ...] | list[str],
    category: str = "Food",
    ai_disclosure: str = "required",
) -> Path:
    """Embed title/keywords into an existing RGBA PNG without changing pixels."""
    source_path = Path(source).expanduser().resolve()
    destination_path = Path(destination).expanduser().resolve() if destination else source_path
    if source_path.suffix.casefold() != ".png" or destination_path.suffix.casefold() != ".png":
        raise PngMetadataError("Metadata embedding accepts PNG source and destination only.")
    if not source_path.is_file():
        raise PngMetadataError(f"PNG source does not exist: {source_path}")
    clean_title, clean_keywords = _clean_metadata(title, keywords)

    with Image.open(source_path) as image:
        image.load()
        if image.format != "PNG" or image.mode != "RGBA":
            raise PngMetadataError("Metadata embedding requires a decoded RGBA PNG.")
        if "A" not in image.getbands() or image.getchannel("A").getextrema() != (0, 255):
            raise PngMetadataError("Metadata embedding requires true alpha with extrema (0, 255).")
        icc_profile = image.info.get("icc_profile")
        if not icc_profile:
            raise PngMetadataError("Metadata embedding requires an embedded ICC profile; normalize to sRGB first.")
        pixels = _pixel_digest(image)
        dimensions = image.size
        alpha_extrema = image.getchannel("A").getextrema()
        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("Title", clean_title, zip=False)
        pnginfo.add_text("Description", "Isolated food utility asset; verify visual edges manually.", zip=False)
        pnginfo.add_text("Keywords", ", ".join(clean_keywords), zip=False)
        pnginfo.add_text("Subject", "; ".join(clean_keywords), zip=False)
        pnginfo.add_text("Category", category, zip=False)
        pnginfo.add_text("AI_Disclosure", ai_disclosure, zip=False)
        pnginfo.add_itxt("XML:com.adobe.xmp", _xmp_packet(title=clean_title, keywords=clean_keywords, category=category, ai_disclosure=ai_disclosure), zip=False)

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(prefix=f".{destination_path.name}.", suffix=".tmp", dir=destination_path.parent, delete=False) as temporary:
            temporary_path = Path(temporary.name)
        try:
            image.save(temporary_path, format="PNG", pnginfo=pnginfo, icc_profile=icc_profile, optimize=False)
            temporary_path.replace(destination_path)
        finally:
            temporary_path.unlink(missing_ok=True)

    with Image.open(destination_path) as result:
        result.load()
        if result.format != "PNG" or result.mode != "RGBA" or result.size != dimensions:
            raise PngMetadataError("Metadata embedding changed PNG format, mode, or dimensions.")
        if _pixel_digest(result) != pixels:
            raise PngMetadataError("Metadata embedding changed decoded RGBA pixels.")
        if result.getchannel("A").getextrema() != alpha_extrema:
            raise PngMetadataError("Metadata embedding changed alpha extrema.")
        if result.info.get("icc_profile") != icc_profile:
            raise PngMetadataError("Metadata embedding did not preserve ICC profile.")
        if result.info.get("Title") != clean_title or result.info.get("Keywords") != ", ".join(clean_keywords):
            raise PngMetadataError("Embedded title/keywords could not be read back from the PNG.")
    return destination_path


def read_embedded_png_metadata(path: str | Path) -> dict[str, str | None]:
    """Read the compatibility text fields written by :func:`embed_png_metadata`."""
    file_path = Path(path).expanduser().resolve()
    with Image.open(file_path) as image:
        image.load()
        return {
            "title": image.info.get("Title"),
            "description": image.info.get("Description"),
            "keywords": image.info.get("Keywords"),
            "subject": image.info.get("Subject"),
            "category": image.info.get("Category"),
            "ai_disclosure": image.info.get("AI_Disclosure"),
            "xmp": image.info.get("XML:com.adobe.xmp"),
        }
