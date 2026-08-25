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
import re
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


def build_document_lifecycle_diagram_kit_svg(spec: AssetSpec, destination: str | Path) -> NativeVectorReport:
    """Build a monochrome-first six-stage document workflow diagram kit."""
    route = require_production_route(spec)
    if route.product_kind != "native_vector":
        raise NativeVectorError("Native SVG construction requires product_kind='native_vector'.")
    if spec.background_policy not in {"transparent", "white"}:
        raise NativeVectorError("Native SVG products require a transparent or white background policy.")
    if spec.text_policy != "none":
        raise NativeVectorError("Native SVG preset does not support text-bearing products.")
    if spec.isolation_policy != "cluster" or spec.layout_mode != "square":
        raise NativeVectorError("Document lifecycle diagram kit requires a separated square cluster framing.")

    width = height = 2048
    primary, secondary, accent = _palette(spec)
    root = ET.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width),
        "height": str(height),
        "viewBox": f"0 0 {width} {height}",
        "version": "1.1",
        "data-stockforge": "native-vector-document-lifecycle-diagram-kit-v1",
        "data-geometry-qa": "workflow-safe-v1",
        "aria-label": "document lifecycle workflow diagram kit",
    })
    if spec.background_policy == "white":
        _append(root, "rect", x="0", y="0", width=str(width), height=str(height), fill="#FFFFFF")

    connectors = _append(root, "g", id="workflow-connectors", fill="none", stroke=primary, stroke_width="18", stroke_linecap="round")
    for x1, y1, x2, y2 in ((620, 660, 744, 660), (1164, 660, 1288, 660), (1498, 890, 1498, 1230), (1288, 1460, 1164, 1460), (744, 1460, 620, 1460)):
        _append(connectors, "line", x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2), stroke=primary, stroke_width="18")

    cards = ((220, 450), (764, 450), (1308, 450), (1308, 1250), (764, 1250), (220, 1250))
    for index, (x, y) in enumerate(cards, start=1):
        cx, cy = x + 190, y + 210
        card = _append(
            root,
            "g",
            id=f"workflow-card-{index}",
            transform=f"translate({cx} {cy})",
            data_card_bounds=f"{x},{y},380,420",
            data_safe_zone="-145,-150,290,300",
        )
        _append(card, "rect", x="-190", y="-210", width="380", height="420", rx="40", fill="#FFFFFF", stroke=primary, stroke_width="18")
        _append(card, "rect", x="-190", y="-210", width="380", height="64", rx="40", fill=secondary, stroke="none", stroke_width="0")
        _append(card, "line", x1="-150", y1="-146", x2="150", y2="-146", stroke=primary, stroke_width="12")
        glyph = _append(card, "g", id=f"workflow-card-{index}-glyph", fill="none", stroke=primary, stroke_linecap="round", stroke_linejoin="round")
        if index == 1:  # intake
            _append(glyph, "path", d="M -115 55 L -115 105 L 115 105 L 115 55", fill=secondary, stroke=primary, stroke_width="20")
            _append(glyph, "path", d="M 0 -115 L 0 62 M -58 -57 L 0 -115 L 58 -57", stroke=primary, stroke_width="26")
        elif index == 2:  # organize
            _append(glyph, "rect", x="-105", y="-84", width="210", height="70", rx="18", fill=secondary, stroke=primary, stroke_width="20")
            _append(glyph, "rect", x="-105", y="25", width="210", height="70", rx="18", fill="#FFFFFF", stroke=primary, stroke_width="20")
            _append(glyph, "line", x1="-130", y1="-49", x2="-118", y2="-49", stroke=accent, stroke_width="22")
            _append(glyph, "line", x1="118", y1="60", x2="130", y2="60", stroke=accent, stroke_width="22")
        elif index == 3:  # review
            _append(glyph, "path", d="M -105 -105 L 32 -105 L 105 -32 L 105 105 L -105 105 Z", fill=secondary, stroke=primary, stroke_width="20")
            _append(glyph, "path", d="M 32 -105 L 32 -32 L 105 -32", stroke=primary, stroke_width="20")
            _append(glyph, "circle", cx="-15", cy="12", r="50", fill="#FFFFFF", stroke=primary, stroke_width="20")
            _append(glyph, "line", x1="22", y1="50", x2="82", y2="110", stroke=primary, stroke_width="20")
        elif index == 4:  # approve
            _append(glyph, "path", d="M -105 -105 L 32 -105 L 105 -32 L 105 105 L -105 105 Z", fill="#FFFFFF", stroke=primary, stroke_width="20")
            _append(glyph, "path", d="M 32 -105 L 32 -32 L 105 -32", stroke=primary, stroke_width="20")
            _append(glyph, "polyline", points="-62,12 -12,65 78,-44", fill="none", stroke=accent, stroke_width="30")
        elif index == 5:  # archive
            _append(glyph, "path", d="M -115 -58 L 115 -58 L 94 105 L -94 105 Z", fill=secondary, stroke=primary, stroke_width="20")
            _append(glyph, "path", d="M -115 -58 L -83 -105 L 83 -105 L 115 -58", fill="#FFFFFF", stroke=primary, stroke_width="20")
            _append(glyph, "line", x1="0", y1="-18", x2="0", y2="66", stroke=primary, stroke_width="22")
            _append(glyph, "polyline", points="-42,28 0,70 42,28", fill="none", stroke=primary, stroke_width="22")
        else:  # deliver
            _append(glyph, "path", d="M -105 -105 L 32 -105 L 105 -32 L 105 105 L -105 105 Z", fill=secondary, stroke=primary, stroke_width="20")
            _append(glyph, "path", d="M 32 -105 L 32 -32 L 105 -32", stroke=primary, stroke_width="20")
            _append(glyph, "line", x1="-64", y1="35", x2="70", y2="35", stroke=primary, stroke_width="22")
            _append(glyph, "polyline", points="28,-5 70,35 28,75", fill="none", stroke=accent, stroke_width="28")

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
    if normalized == "document_lifecycle_diagram_kit":
        return build_document_lifecycle_diagram_kit_svg(spec, destination)
    if normalized == "technical_badge":
        return build_technical_badge_svg(spec, destination)
    if normalized == "geometric_pattern":
        return build_geometric_pattern_svg(spec, destination)
    raise NativeVectorError(f"Unsupported native-vector preset: {preset!r}.")


def _number_list(value: str) -> tuple[float, ...]:
    return tuple(float(item) for item in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", value))


def _shape_bounds(element: ET.Element) -> tuple[float, float, float, float] | None:
    """Return a conservative local-coordinate bounds including stroke width."""
    tag = _tag_name(element)
    stroke = abs(float(element.attrib.get("stroke-width", "0") or "0")) / 2
    try:
        if tag == "rect":
            x = float(element.attrib.get("x", "0"))
            y = float(element.attrib.get("y", "0"))
            w = float(element.attrib.get("width", "0"))
            h = float(element.attrib.get("height", "0"))
            return (x - stroke, y - stroke, x + w + stroke, y + h + stroke)
        if tag == "circle":
            cx = float(element.attrib.get("cx", "0"))
            cy = float(element.attrib.get("cy", "0"))
            radius = float(element.attrib.get("r", "0")) + stroke
            return (cx - radius, cy - radius, cx + radius, cy + radius)
        if tag == "ellipse":
            cx = float(element.attrib.get("cx", "0"))
            cy = float(element.attrib.get("cy", "0"))
            rx = float(element.attrib.get("rx", "0")) + stroke
            ry = float(element.attrib.get("ry", "0")) + stroke
            return (cx - rx, cy - ry, cx + rx, cy + ry)
        if tag == "line":
            x1 = float(element.attrib.get("x1", "0"))
            y1 = float(element.attrib.get("y1", "0"))
            x2 = float(element.attrib.get("x2", "0"))
            y2 = float(element.attrib.get("y2", "0"))
            return (min(x1, x2) - stroke, min(y1, y2) - stroke, max(x1, x2) + stroke, max(y1, y2) + stroke)
        if tag == "path":
            values = _number_list(element.attrib.get("d", ""))
            if len(values) < 2:
                return None
            xs = values[0::2]
            ys = values[1::2]
            return (min(xs) - stroke, min(ys) - stroke, max(xs) + stroke, max(ys) + stroke)
        if tag in {"polygon", "polyline"}:
            values = _number_list(element.attrib.get("points", ""))
            if len(values) < 4:
                return None
            xs = values[0::2]
            ys = values[1::2]
            return (min(xs) - stroke, min(ys) - stroke, max(xs) + stroke, max(ys) + stroke)
    except (TypeError, ValueError):
        return None
    return None


def _union_bounds(bounds: list[tuple[float, float, float, float]]) -> tuple[float, float, float, float] | None:
    if not bounds:
        return None
    return (
        min(item[0] for item in bounds),
        min(item[1] for item in bounds),
        max(item[2] for item in bounds),
        max(item[3] for item in bounds),
    )


def _parse_bounds(value: str) -> tuple[float, float, float, float] | None:
    values = _number_list(value)
    if len(values) != 4:
        return None
    x, y, width, height = values
    return (x, y, x + width, y + height)


def _bounds_inside(inner: tuple[float, float, float, float], outer: tuple[float, float, float, float], tolerance: float = 0.01) -> bool:
    return inner[0] >= outer[0] - tolerance and inner[1] >= outer[1] - tolerance and inner[2] <= outer[2] + tolerance and inner[3] <= outer[3] + tolerance


def _bounds_intersect(first: tuple[float, float, float, float], second: tuple[float, float, float, float], gap: float = 0.0) -> bool:
    return not (first[2] + gap <= second[0] or second[2] + gap <= first[0] or first[3] + gap <= second[1] or second[3] + gap <= first[1])


def _workflow_geometry_qa(root: ET.Element) -> tuple[bool, str]:
    """Check safe zones and connector separation for the workflow-kit preset."""
    if root.attrib.get("data-geometry-qa") != "workflow-safe-v1":
        return True, "Not applicable; no workflow safe-zone contract is declared."
    cards: list[tuple[float, float, float, float]] = []
    failures: list[str] = []
    card_count = 0
    for group in root.iter():
        if _tag_name(group) != "g" or not group.attrib.get("id", "").startswith("workflow-card-") or group.attrib.get("id", "").endswith("-glyph"):
            continue
        card_count += 1
        card_bounds = _parse_bounds(group.attrib.get("data-card-bounds", ""))
        safe_zone = _parse_bounds(group.attrib.get("data-safe-zone", ""))
        glyph = next((item for item in group if item.attrib.get("id", "").endswith("-glyph")), None)
        if card_bounds is None or safe_zone is None or glyph is None:
            failures.append(f"card-{card_count}: missing card bounds, safe zone, or glyph group")
            continue
        cards.append(card_bounds)
        glyph_bounds = _union_bounds([bounds for item in glyph.iter() if (bounds := _shape_bounds(item)) is not None])
        if glyph_bounds is None:
            failures.append(f"card-{card_count}: glyph has no measurable native geometry")
        elif not _bounds_inside(glyph_bounds, safe_zone):
            failures.append(f"card-{card_count}: glyph stroke envelope escapes safe zone")
    connectors = next((item for item in root.iter() if item.attrib.get("id") == "workflow-connectors"), None)
    connector_count = 0
    if connectors is not None:
        for element in connectors.iter():
            bounds = _shape_bounds(element)
            if bounds is None:
                continue
            connector_count += 1
            if any(_bounds_intersect(bounds, card, gap=2.0) for card in cards):
                failures.append(f"connector-{connector_count}: connector envelope touches a card")
    if card_count != 6:
        failures.append(f"expected six workflow cards, found {card_count}")
    if connector_count != 5:
        failures.append(f"expected five separated workflow connectors, found {connector_count}")
    if failures:
        return False, "; ".join(failures)
    return True, f"Six card safe zones and {connector_count} connector envelopes pass clearance checks."


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
    geometry_ok, geometry_detail = _workflow_geometry_qa(root)
    checks.append(("geometry_clearance", geometry_detail))
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
    ready = width >= 1 and height >= 1 and not unknown and not forbidden and pattern_ok and geometry_ok
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
