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
_ALLOWED_TAGS = frozenset({"svg", "g", "path", "rect", "circle", "ellipse", "polygon", "polyline", "line", "defs", "linearGradient", "stop"})
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


def build_svg_for_preset(spec: AssetSpec, destination: str | Path, preset: str = "modular_ribbon") -> NativeVectorReport:
    """Dispatch only to explicitly registered native-vector presets."""
    normalized = preset.strip().casefold()
    if normalized == "modular_ribbon":
        return build_modular_ribbon_svg(spec, destination)
    if normalized == "technical_badge":
        return build_technical_badge_svg(spec, destination)
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
    ready = width >= 1 and height >= 1 and not unknown and not forbidden
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
