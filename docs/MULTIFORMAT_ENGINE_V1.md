# StockForge Multi-format Engine v1

## Purpose

StockForge routes a commercial asset to one product format that matches its buyer job. It does **not** export one visual indiscriminately as JPEG, PNG, and vector. Every route remains subject to human visual review, rights review, metadata review, and Adobe portal declarations.

## Verified production routes

| Product contract | Delivery format | Build path | GPU policy | User-visible branch | Status |
|---|---|---|---|---|---|
| `raster_illustration` | JPEG | Existing raster generation, optional finalizer, existing XMP JPEG route | Allowed only after portfolio preflight | `READY_UPLOAD_ADOBE` | Verified existing route |
| `native_vector` | SVG | Local editable SVG geometry builder | **No GPU** | `READY_UPLOAD_ADOBE` after format-specific human review | Verified local build and structural gate |
| `transparent_cutout` | PNG with real alpha | Future alpha producer plus PNG finalizer | **Blocked** | `READY_UPLOAD_ADOBE` only after verification | Intentionally not production-ready |

## Non-negotiable routing rules

1. `raster_illustration` uses JPEG. It may use `square` or `hero_landscape`; only hero products may reserve directional copy space.
2. `transparent_cutout` uses PNG, square framing, transparent background, isolated subject, and no paid or remote execution until an alpha pipeline is tested. A white-background PNG is rejected.
3. `native_vector` uses SVG and is built as editable geometry. Raster tracing is not a native-vector route.
4. A square product has tight framing and no reserved copy space. Copy-space keywords cannot override `layout_mode`.
5. Only source files pass to internal review packages. Android user output remains one visual file per asset in `Downloads/MACHINE STOCKFORGE/PREVIEW_TO_MANUS` or `READY_UPLOAD_ADOBE`.

## Local gates

| Gate | Protects against |
|---|---|
| `format_router` | Incompatible format/product pairs and unverified routes reaching a provider |
| `adobe_png_gate` | Opaque PNGs, missing true alpha, wrong format, size limits, missing/incorrect color evidence |
| `native_vector` inspector | Raster `<image>` content, scripts, text, external data/links, malformed SVG, and unsupported elements |
| portfolio preflight v2 | Copy-space heuristics overriding a product contract, unsafe subject terms, ambiguous relations, and unreviewed metadata |

## Deliberate limits

The native SVG builder currently supports controlled modular geometric assets only. It is appropriate for abstract systems, icons, patterns, and editorial geometric elements. It does not claim that a textured illustration, photo, or generated 3D material asset can be converted into a valuable vector.

PNG remains planned but blocked until StockForge can create a true alpha channel, normalize sRGB, inspect edge quality, and validate the final file with the Adobe PNG gate. No GPU should be spent testing this path until an alpha-capable method and an explicit test brief are selected.

## Adobe evidence

Adobe accepts JPEG for raster/GenAI content; its published upload table lists AI, EPS, and SVG for vector-compatible content. PNG submissions require an actually transparent background, sRGB, 4–100 MP, and a file under 45 MB. See `ADOBE_MULTIFORMAT_EVIDENCE_2026-08-24.md` for official sources and scope.
