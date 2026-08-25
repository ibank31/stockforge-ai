"""Native SVG construction and safety checks for StockForge vector products.

The generator is deliberately limited to geometric, editable assets.  It does
not image-trace raster output and does not pretend that a raster illustration is
a vector.  Future AI concept selection may supply a compliant ``AssetSpec``;
the final SVG geometry remains locally auditable.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from xml.etree import ElementTree as ET

from .asset_spec import AssetSpec
from .format_router import FormatRoutingError, require_production_route


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
_ALLOWED_TAGS = frozenset({"svg", "g", "path", "rect", "circle", "ellipse", "polygon", "polyline", "line", "defs", "pattern", "linearGradient", "stop"})
_FORBIDDEN_TOKENS = ("<image", "<text", "<script", "foreignobject", "data:image", "javascript:", "@import")


class NativeVectorError(ValueError):
    """Raised when an SVG is not a safe native-vector delivery candidate."""


@dataclass(frozen=True, slots=True)
class NativeVectorReport:
    path: str
    width: int
    height: int
    element_count: int
    transparent_background: bool
    native_paths_only: bool
    ready: bool
    checks: tuple[tuple[str, str], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "element_count": self.element_count,
            "transparent_background": self.transparent_background,
            "native_paths_only": self.native_paths_only,
            "ready": self.ready,
            "checks": [{"name": name, "detail": detail} for name, detail in self.checks],
        }


def _tag_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _palette(spec: AssetSpec) -> tuple[str, str, str]:
    fallback = ("#164E63", "#F8FAFC", "#F59E0B")
    supplied = tuple(item for item in spec.palette if item.startswith("#") and len(item) in {4, 7})
    return (supplied + fallback)[:3]


def _seed(spec: AssetSpec) -> int:
    return int(sha256(spec.asset_id.encode("utf-8")).hexdigest()[:8], 16)


def _append(parent: ET.Element, tag: str, **attrs: str) -> ET.Element:
    return ET.SubElement(parent, f"{{{SVG_NS}}}{tag}", {key.replace("_", "-"): value for key, value in attrs.items()})


def build_modular_ribbon_svg(spec: AssetSpec, destination: str | Path) -> NativeVectorReport:
    """Build one editable abstract ribbon system from a native-vector contract.

    The preset is intentionally constrained: it is appropriate for abstract
    systems, modular paths, and editorial geometric elements—not illustrative
    subjects, textured objects, or photographic scenes.
    """
    route = require_production_route(spec)
    if route.product_kind != "native_vector":
        raise NativeVectorError("Native SVG construction requires product_kind='native_vector'.")
    if spec.background_policy not in {"transparent", "white"}:
        raise NativeVectorError("Native SVG products require a transparent or white background policy.")
    if spec.text_policy != "none":
        raise NativeVectorError("Native SVG preset does not support text-bearing products.")

    width = height = 2048
    primary, secondary, accent = _palette(spec)
    shift = 48 + (_seed(spec) % 72)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "data-stockforge": "native-vector-v1",
        "aria-label": "abstract modular ribbon",
    })
    if spec.background_policy == "white":
        _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="#FFFFFF")

    group = _append(root, "g", fill="none", stroke_linecap="round", stroke_linejoin="round")
    # A single continuous ribbon and three detachable modules preserve editability
    # while providing a recognisable, non-icon-generic silhouette.
    _append(
        group,
        "path",
        d=(f"M {260 + shift} 1540 C 390 520, 1040 420, 1210 830 "
           f"C 1380 1240, 810 1450, 1640 1560"),
        stroke=primary,
        stroke_width="150",
    )
    _append(
        group,
        "path",
        d=(f"M {260 + shift} 1540 C 390 520, 1040 420, 1210 830 "
           f"C 1380 1240, 810 1450, 1640 1560"),
        stroke=secondary,
        stroke_width="72",
    )
    for index, (x, y, color) in enumerate(((560, 690, accent), (1030, 700, secondary), (1280, 1230, accent))):
        module = _append(group, "g", transform=f"translate({x} {y}) rotate({-18 + index * 21})")
        _append(module, "rect", x="-112", y="-112", width="224", height="224", rx="42", fill=color)
        _append(module, "circle", cx="0", cy="0", r="45", fill="#FFFFFF")

    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    path = Path(destination).expanduser().resolve()
    if path.suffix.lower() != ".svg":
        raise NativeVectorError("Native vector destination must use the .svg extension.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    report = inspect_native_svg(path)
    if not report.ready:
        path.unlink(missing_ok=True)
        details = "; ".join(f"{name}: {detail}" for name, detail in report.checks)
        raise NativeVectorError(f"Generated SVG failed its own native-vector gate: {details}")
    return report


def build_folder_upload_svg(spec: AssetSpec, destination: str | Path) -> NativeVectorReport:
    """Build one recognizable folder-upload icon for file-management workflows."""
    route = require_production_route(spec)
    if route.product_kind != "native_vector":
        raise NativeVectorError("Native SVG construction requires product_kind='native_vector'.")
    if spec.background_policy not in {"transparent", "white"}:
        raise NativeVectorError("Native SVG products require a transparent or white background policy.")
    if spec.text_policy != "none":
        raise NativeVectorError("Native SVG preset does not support text-bearing products.")
    if spec.isolation_policy != "isolated" or spec.layout_mode != "square":
        raise NativeVectorError("Folder-upload icon requires isolated square framing.")

    width = height = 2048
    primary, _secondary, accent = _palette(spec)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "data-stockforge": "native-vector-folder-upload-v1",
        "aria-label": "folder upload icon",
    })
    if spec.background_policy == "white":
        _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="#FFFFFF")

    group = _append(root, "g", stroke_linecap="round", stroke_linejoin="round")
    # The orange folder body and dark tab produce a two-part silhouette that
    # remains legible at thumbnail size. The white upward arrow is integrated
    # into the folder front so the buyer job is visible without a caption.
    _append(
        group,
        "path",
        d="M 360 700 Q 360 620 440 620 L 790 620 L 930 790 L 1688 790 Q 1768 790 1768 870 L 1768 1430 Q 1768 1510 1688 1510 L 440 1510 Q 360 1510 360 1430 Z",
        fill=accent,
        stroke=primary,
        stroke_width="72",
    )
    _append(
        group,
        "path",
        d="M 360 840 Q 360 760 440 760 L 790 760 L 930 930 L 1688 930",
        fill="none",
        stroke=primary,
        stroke_width="72",
    )
    _append(
        group,
        "path",
        d="M 1030 1360 L 1030 1030 M 860 1200 L 1030 1030 L 1200 1200",
        fill="none",
        stroke="#F8FAFC",
        stroke_width="108",
    )

    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    path = Path(destination).expanduser().resolve()
    if path.suffix.lower() != ".svg":
        raise NativeVectorError("Native vector destination must use the .svg extension.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    report = inspect_native_svg(path)
    if not report.ready:
        path.unlink(missing_ok=True)
        details = "; ".join(f"{name}: {detail}" for name, detail in report.checks)
        raise NativeVectorError(f"Generated SVG failed its own native-vector gate: {details}")
    return report


def build_file_flow_micro_set_svg(spec: AssetSpec, destination: str | Path) -> NativeVectorReport:
    """Build one coherent eight-icon file-flow utility sheet locally."""
    route = require_production_route(spec)
    if route.product_kind != "native_vector":
        raise NativeVectorError("Native SVG construction requires product_kind='native_vector'.")
    if spec.background_policy not in {"transparent", "white"}:
        raise NativeVectorError("Native SVG products require a transparent or white background policy.")
    if spec.text_policy != "none":
        raise NativeVectorError("Native SVG preset does not support text-bearing products.")
    if spec.isolation_policy != "cluster" or spec.layout_mode != "square":
        raise NativeVectorError("File-flow micro-set requires a separated square icon-sheet framing.")

    width = height = 2048
    primary, _secondary, accent = _palette(spec)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "data-stockforge": "native-vector-file-flow-micro-set-v1",
        "aria-label": "file flow utility icon set",
    })
    if spec.background_policy == "white":
        _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="#FFFFFF")

    sheet = _append(root, "g", fill="none", stroke_linecap="round", stroke_linejoin="round")
    positions = ((300, 560), (790, 560), (1280, 560), (1770, 560), (300, 1450), (790, 1450), (1280, 1450), (1770, 1450))
    for index, (cx, cy) in enumerate(positions):
        group = _append(sheet, "g", id=f"file-flow-icon-{index + 1}", transform=f"translate({cx} {cy})")
        if index == 0:  # folder
            _append(group, "path", d="M -150 -90 Q -150 -125 -115 -125 L -35 -125 L 5 -82 L 150 -82 Q 175 -82 175 -55 L 175 105 Q 175 130 150 130 L -115 130 Q -150 130 -150 95 Z", fill=accent, stroke=primary, stroke_width="28")
            _append(group, "path", d="M -150 -55 Q -150 -82 -115 -82 L -35 -82 L 5 -40 L 150 -40", stroke=primary, stroke_width="28")
        elif index == 1:  # upload
            _append(group, "path", d="M -135 70 L 135 70 L 135 115 L -135 115 Z", fill=accent, stroke=primary, stroke_width="28")
            _append(group, "path", d="M 0 75 L 0 -105 M -72 -34 L 0 -105 L 72 -34", stroke=primary, stroke_width="32")
        elif index == 2:  # download
            _append(group, "path", d="M -135 70 L 135 70 L 135 115 L -135 115 Z", fill=accent, stroke=primary, stroke_width="28")
            _append(group, "path", d="M 0 -105 L 0 45 M -72 -22 L 0 45 L 72 -22", stroke=primary, stroke_width="32")
        elif index == 3:  # cloud storage
            _append(group, "path", d="M -118 72 C -175 72 -190 10 -150 -20 C -142 -72 -88 -105 -40 -82 C 6 -140 100 -115 112 -50 C 172 -48 188 72 118 72 Z", fill=accent, stroke=primary, stroke_width="28")
            _append(group, "path", d="M -58 28 L 58 28", stroke=primary, stroke_width="24")
        elif index == 4:  # sync
            _append(group, "path", d="M -100 -35 A 112 112 0 0 1 80 -75", stroke=primary, stroke_width="28")
            _append(group, "polygon", points="78,-115 135,-72 72,-48", fill=accent, stroke=primary, stroke_width="18")
            _append(group, "path", d="M 100 35 A 112 112 0 0 1 -80 75", stroke=primary, stroke_width="28")
            _append(group, "polygon", points="-78,115 -135,72 -72,48", fill=accent, stroke=primary, stroke_width="18")
        elif index == 5:  # archive
            _append(group, "path", d="M -145 -90 L 145 -90 L 120 115 L -120 115 Z", fill=accent, stroke=primary, stroke_width="28")
            _append(group, "path", d="M -145 -90 L -122 -125 L 122 -125 L 145 -90 Z", stroke=primary, stroke_width="28")
            _append(group, "path", d="M -45 5 L 45 5", stroke=primary, stroke_width="28")
        elif index == 6:  # file/document
            _append(group, "path", d="M -105 -130 L 35 -130 L 112 -52 L 112 130 L -105 130 Z", fill=accent, stroke=primary, stroke_width="28")
            _append(group, "path", d="M 35 -130 L 35 -52 L 112 -52", stroke=primary, stroke_width="28")
            _append(group, "path", d="M -48 20 L 55 20 M -48 68 L 55 68", stroke=primary, stroke_width="20")
        else:  # share
            _append(group, "line", x1="-68", y1="-5", x2="58", y2="-70", stroke=primary, stroke_width="24")
            _append(group, "line", x1="-68", y1="5", x2="58", y2="70", stroke=primary, stroke_width="24")
            for x, y in ((-100, 0), (92, -92), (92, 92)):
                _append(group, "circle", cx=str(x), cy=str(y), r="45", fill=accent, stroke=primary, stroke_width="24")

    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    path = Path(destination).expanduser().resolve()
    if path.suffix.lower() != ".svg":
        raise NativeVectorError("Native vector destination must use the .svg extension.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    report = inspect_native_svg(path)
    if not report.ready:
        path.unlink(missing_ok=True)
        details = "; ".join(f"{name}: {detail}" for name, detail in report.checks)
        raise NativeVectorError(f"Generated SVG failed its own native-vector gate: {details}")
    return report


def build_document_review_delivery_micro_set_svg(spec: AssetSpec, destination: str | Path) -> NativeVectorReport:
    """Build an editable eight-icon document review and delivery workflow set."""
    route = require_production_route(spec)
    if route.product_kind != "native_vector":
        raise NativeVectorError("Native SVG construction requires product_kind='native_vector'.")
    if spec.background_policy not in {"transparent", "white"}:
        raise NativeVectorError("Native SVG products require a transparent or white background policy.")
    if spec.text_policy != "none":
        raise NativeVectorError("Native SVG preset does not support text-bearing products.")
    if spec.isolation_policy != "cluster" or spec.layout_mode != "square":
        raise NativeVectorError("Document-review-delivery micro-set requires a separated square icon-sheet framing.")

    width = height = 2048
    primary, secondary, accent = _palette(spec)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "data-stockforge": "native-vector-document-review-delivery-v1",
        "aria-label": "document review delivery utility icon set",
    })
    if spec.background_policy == "white":
        _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="#FFFFFF")

    sheet = _append(root, "g", fill="none", stroke_linecap="round", stroke_linejoin="round")
    positions = ((300, 560), (790, 560), (1280, 560), (1770, 560), (300, 1450), (790, 1450), (1280, 1450), (1770, 1450))
    for index, (cx, cy) in enumerate(positions):
        group = _append(sheet, "g", id=f"document-review-delivery-icon-{index + 1}", transform=f"translate({cx} {cy})")
        _append(group, "circle", cx="0", cy="0", r="210", fill=secondary, stroke=primary, stroke_width="24")
        if index == 0:  # intake
            _append(group, "rect", x="-125", y="-70", width="250", height="160", rx="24", fill=accent, stroke=primary, stroke_width="26")
            _append(group, "path", d="M 0 -230 L 0 -100 M -70 -165 L 0 -230 L 70 -165", stroke=primary, stroke_width="28")
        elif index == 1:  # organize
            _append(group, "rect", x="-125", y="-105", width="250", height="90", rx="16", fill=accent, stroke=primary, stroke_width="24")
            _append(group, "rect", x="-70", y="20", width="250", height="90", rx="16", fill="#FFFFFF", stroke=primary, stroke_width="24")
            _append(group, "path", d="M -165 35 L -115 35 M -165 35 L -145 15 M -165 35 L -145 55", stroke=primary, stroke_width="24")
        elif index == 2:  # review
            _append(group, "path", d="M -120 -135 L 40 -135 L 105 -70 L 105 135 L -120 135 Z", fill=accent, stroke=primary, stroke_width="24")
            _append(group, "path", d="M 40 -135 L 40 -70 L 105 -70", stroke=primary, stroke_width="24")
            _append(group, "circle", cx="-5", cy="10", r="58", fill="#FFFFFF", stroke=primary, stroke_width="22")
            _append(group, "path", d="M 38 52 L 95 108", stroke=primary, stroke_width="22")
        elif index == 3:  # approve
            _append(group, "path", d="M -120 -135 L 40 -135 L 105 -70 L 105 135 L -120 135 Z", fill="#FFFFFF", stroke=primary, stroke_width="24")
            _append(group, "path", d="M 40 -135 L 40 -70 L 105 -70", stroke=primary, stroke_width="24")
            _append(group, "polyline", points="-65,20 -15,70 75,-35", fill="none", stroke=accent, stroke_width="34")
        elif index == 4:  # archive
            _append(group, "path", d="M -150 -80 L 150 -80 L 120 125 L -120 125 Z", fill=accent, stroke=primary, stroke_width="24")
            _append(group, "path", d="M -150 -80 L -115 -130 L 115 -130 L 150 -80", fill="#FFFFFF", stroke=primary, stroke_width="24")
            _append(group, "path", d="M 0 -35 L 0 72 M -45 28 L 0 72 L 45 28", stroke=primary, stroke_width="26")
        elif index == 5:  # restore
            _append(group, "path", d="M 80 -80 A 118 118 0 1 0 85 85", stroke=primary, stroke_width="30")
            _append(group, "polygon", points="75,-135 145,-92 82,-55", fill=accent, stroke=primary, stroke_width="18")
            _append(group, "path", d="M -65 -90 L 35 -90 L 70 -55 L 70 80 L -65 80 Z", fill="#FFFFFF", stroke=primary, stroke_width="22")
            _append(group, "path", d="M 35 -90 L 35 -55 L 70 -55", stroke=primary, stroke_width="22")
        elif index == 6:  # sync
            _append(group, "path", d="M -120 -20 A 120 120 0 0 1 90 -80", stroke=primary, stroke_width="28")
            _append(group, "polygon", points="88,-125 150,-78 82,-52", fill=accent, stroke=primary, stroke_width="18")
            _append(group, "path", d="M 120 20 A 120 120 0 0 1 -90 80", stroke=primary, stroke_width="28")
            _append(group, "polygon", points="-88,125 -150,78 -82,52", fill=accent, stroke=primary, stroke_width="18")
            _append(group, "rect", x="-55", y="-55", width="110", height="110", rx="16", fill="#FFFFFF", stroke=primary, stroke_width="20")
        else:  # share
            _append(group, "line", x1="-70", y1="0", x2="60", y2="-75", stroke=primary, stroke_width="24")
            _append(group, "line", x1="-70", y1="0", x2="60", y2="75", stroke=primary, stroke_width="24")
            for x, y, fill in ((-100, 0, accent), (92, -92, "#FFFFFF"), (92, 92, accent)):
                _append(group, "circle", cx=str(x), cy=str(y), r="46", fill=fill, stroke=primary, stroke_width="24")

    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    path = Path(destination).expanduser().resolve()
    if path.suffix.lower() != ".svg":
        raise NativeVectorError("Native vector destination must use the .svg extension.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    report = inspect_native_svg(path)
    if not report.ready:
        path.unlink(missing_ok=True)
        details = "; ".join(f"{name}: {detail}" for name, detail in report.checks)
        raise NativeVectorError(f"Generated SVG failed its own native-vector gate: {details}")
    return report


def build_technical_badge_svg(spec: AssetSpec, destination: str | Path) -> NativeVectorReport:
    """Build one editable technical badge without text, logos, or raster embeds."""
    route = require_production_route(spec)
    if route.product_kind != "native_vector":
        raise NativeVectorError("Native SVG construction requires product_kind='native_vector'.")
    if spec.background_policy not in {"transparent", "white"}:
        raise NativeVectorError("Native SVG products require a transparent or white background policy.")
    if spec.text_policy != "none":
        raise NativeVectorError("Native SVG preset does not support text-bearing products.")

    width = height = 2048
    primary, secondary, accent = _palette(spec)
    seed = _seed(spec)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "data-stockforge": "native-vector-technical-badge-v1",
        "aria-label": "abstract technical badge",
    })
    if spec.background_policy == "white":
        _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="#FFFFFF")
    group = _append(root, "g", stroke_linecap="round", stroke_linejoin="round")
    radius = 420 + (seed % 80)
    _append(group, "rect", x=str(1024 - radius), y=str(1024 - radius), width=str(radius * 2), height=str(radius * 2), rx="180", fill=secondary, stroke=primary, stroke_width="72")
    _append(group, "circle", cx="1024", cy="1024", r="170", fill=accent, stroke="#FFFFFF", stroke_width="36")
    _append(group, "line", x1="1024", y1="530", x2="1024", y2="854", stroke=primary, stroke_width="64")
    _append(group, "line", x1="1024", y1="1194", x2="1024", y2="1518", stroke=primary, stroke_width="64")
    _append(group, "line", x1="530", y1="1024", x2="854", y2="1024", stroke=primary, stroke_width="64")
    _append(group, "line", x1="1194", y1="1024", x2="1518", y2="1024", stroke=primary, stroke_width="64")

    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    path = Path(destination).expanduser().resolve()
    if path.suffix.lower() != ".svg":
        raise NativeVectorError("Native vector destination must use the .svg extension.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    report = inspect_native_svg(path)
    if not report.ready:
        path.unlink(missing_ok=True)
        details = "; ".join(f"{name}: {detail}" for name, detail in report.checks)
        raise NativeVectorError(f"Generated SVG failed its own native-vector gate: {details}")
    return report


def build_geometric_pattern_svg(spec: AssetSpec, destination: str | Path) -> NativeVectorReport:
    """Build a repeatable geometric tile as native SVG geometry."""
    route = require_production_route(spec)
    if route.product_kind != "native_vector":
        raise NativeVectorError("Native SVG construction requires product_kind='native_vector'.")
    if spec.background_policy not in {"transparent", "white"}:
        raise NativeVectorError("Native SVG products require a transparent or white background policy.")
    if spec.text_policy != "none":
        raise NativeVectorError("Native SVG preset does not support text-bearing products.")

    width = height = 2048
    primary, secondary, accent = _palette(spec)
    seed = _seed(spec)
    tile = 512
    offset = 32 + (seed % 64)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "data-stockforge": "native-vector-geometric-pattern-v1",
        "aria-label": "repeatable geometric pattern",
    })
    defs = _append(root, "defs")
    pattern = _append(defs, "pattern", id="sf-tile", patternUnits="userSpaceOnUse", width=str(tile), height=str(tile))
    _append(pattern, "rect", x="0", y="0", width=str(tile), height=str(tile), fill=secondary)
    _append(pattern, "circle", cx=str(128 + offset), cy="128", r="72", fill=accent)
    _append(pattern, "circle", cx=str(384 - offset), cy="384", r="72", fill=accent)
    _append(pattern, "path", d="M 0 256 L 256 0 L 512 256 L 256 512 Z", fill="none", stroke=primary, stroke_width="28")
    if spec.background_policy == "white":
        _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="#FFFFFF")
    _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="url(#sf-tile)")

    raw = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    path = Path(destination).expanduser().resolve()
    if path.suffix.lower() != ".svg":
        raise NativeVectorError("Native vector destination must use the .svg extension.")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    report = inspect_native_svg(path)
    if not report.ready:
        path.unlink(missing_ok=True)
        details = "; ".join(f"{name}: {detail}" for name, detail in report.checks)
        raise NativeVectorError(f"Generated SVG failed its own native-vector gate: {details}")
    return report


def build_svg_for_preset(spec: AssetSpec, destination: str | Path, preset: str = "modular_ribbon") -> NativeVectorReport:
    """Dispatch only to explicitly registered native-vector presets."""
    normalized = preset.strip().casefold()
    if normalized == "modular_ribbon":
        return build_modular_ribbon_svg(spec, destination)
    if normalized == "folder_upload":
        return build_folder_upload_svg(spec, destination)
    if normalized == "file_flow_micro_set":
        return build_file_flow_micro_set_svg(spec, destination)
    if normalized == "document_review_delivery_micro_set":
        return build_document_review_delivery_micro_set_svg(spec, destination)
    if normalized == "technical_badge":
        return build_technical_badge_svg(spec, destination)
    if normalized == "geometric_pattern":
        return build_geometric_pattern_svg(spec, destination)
    raise NativeVectorError(f"Unsupported native-vector preset: {preset!r}.")


def inspect_native_svg(path: str | Path) -> NativeVectorReport:
    """Verify that an SVG contains only locally editable vector geometry."""
    file_path = Path(path).expanduser().resolve()
    checks: list[tuple[str, str]] = []
    if not file_path.is_file():
        return NativeVectorReport(str(file_path), 0, 0, 0, False, False, False, (("file_exists", "SVG file does not exist."),))
    if file_path.suffix.lower() != ".svg":
        return NativeVectorReport(str(file_path), 0, 0, 0, False, False, False, (("extension", "Expected .svg extension."),))
    text = file_path.read_text(encoding="utf-8")
    lowered = text.casefold()
    forbidden = [token for token in _FORBIDDEN_TOKENS if token in lowered]
    if forbidden:
        return NativeVectorReport(str(file_path), 0, 0, 0, False, False, False, (("no_raster_or_script", f"Forbidden SVG content: {', '.join(forbidden)}."),))
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return NativeVectorReport(str(file_path), 0, 0, 0, False, False, False, (("xml", f"Malformed SVG: {exc}."),))
    if _tag_name(root) != "svg":
        return NativeVectorReport(str(file_path), 0, 0, 0, False, False, False, (("root", "Root element must be svg."),))
    try:
        width = int(float(root.attrib.get("width", "0")))
        height = int(float(root.attrib.get("height", "0")))
    except ValueError:
        width = height = 0
    if width < 1 or height < 1:
        checks.append(("dimensions", "SVG requires positive width and height."))
    else:
        checks.append(("dimensions", f"{width}x{height} artboard."))
    tags = tuple(_tag_name(item) for item in root.iter())
    unknown = sorted(set(tags) - _ALLOWED_TAGS)
    if unknown:
        checks.append(("native_elements", f"Unsupported SVG elements: {', '.join(unknown)}."))
    else:
        checks.append(("native_elements", "Only editable SVG geometry and definitions are present."))
    transparent = not any(_tag_name(item) == "rect" and item.attrib.get("x") == "0" and item.attrib.get("y") == "0" and item.attrib.get("width") == str(width) and item.attrib.get("height") == str(height) for item in root.iter())
    checks.append(("background", "Transparent canvas." if transparent else "Flat background rectangle is explicit."))
    patterns = [item for item in root.iter() if _tag_name(item) == "pattern"]
    pattern_ok = True
    if patterns:
        try:
            pattern_ok = all(
                item.attrib.get("patternUnits") == "userSpaceOnUse"
                and float(item.attrib.get("width", "0")) > 0
                and float(item.attrib.get("height", "0")) > 0
                for item in patterns
            )
        except (TypeError, ValueError):
            pattern_ok = False
        checks.append(("pattern_repeatability", "Pattern definitions use positive user-space tiles." if pattern_ok else "Pattern definitions require positive user-space tile dimensions."))
    else:
        checks.append(("pattern_repeatability", "Not applicable; SVG contains no pattern definition."))
    ready = width >= 1 and height >= 1 and not unknown and not forbidden and pattern_ok
    return NativeVectorReport(
        path=str(file_path),
        width=width,
        height=height,
        element_count=len(tags),
        transparent_background=transparent,
        native_paths_only=not unknown and not forbidden,
        ready=ready,
        checks=tuple(checks),
    )
