# Vector route evidence — 2026-08-25

## Adobe official requirements

Adobe's current Vector Requirements page states that it accepts AI, EPS, and SVG vector files and does not accept vector files uploaded as JPEGs or packed in ZIP folders [1]. Customers receive a JPEG preview plus the original vector file; Adobe may generate a transparent PNG when the vector uses a transparent or flat-color background [1].

The same page specifies a maximum file size of 45 MB, artboard offset `(0,0)`, RGB document color mode, and a recommended artboard range of 15MP to 65MP for vector files [1]. Adobe recommends logical labeled layers/groups, outlined fonts, avoiding unnecessary swatches/effects, and editable embedded design elements rather than linked or rasterized assets [1]. For design elements and sets such as icons, patterns, and characters, Adobe lists 1000x1000 to 4800x4800 pixels; for scenes and illustrations, 1200x1200 to 4800x4800 pixels [1].

Adobe also says the first 10 keywords are prioritized, and titles/keywords must not use trademarks, camera specifications, content-type words, artist names, real known people, fictional characters, or copyrighted creative works [1]. Vector art based on a photograph or artwork needs a property release; logos, trademarks, company names, and brand names are not accepted in vectors [1]. Adobe's vector overview confirms the accepted formats AI, EPS, and SVG and that a ZIP is not itself the submitted vector [2].

## Current StockForge route

`format_router.py` already routes `product_kind=native_vector` to `delivery_format=svg`, `execution_mode=local_native_vector_build`, `canvas=vector-artboard`, and `verified_for_production=True` for non-portrait layouts. It explicitly states that editable SVG paths are built locally and no raster image trace or GPU generation is used.

`native_vector.py` currently validates XML, forbids raster embeds/scripts/text/imports, limits elements to editable SVG geometry and definitions, and supports the deterministic presets `modular_ribbon`, `folder_upload`, `file_flow_micro_set`, `technical_badge`, and `geometric_pattern`. The local builder writes SVG under the project workspace and creates a release package; it does not call a remote provider, use GPU, add XMP, or submit to Adobe.

The current route is therefore technically feasible for simple geometric assets, utility icon sheets, and repeatable patterns. It is not yet a general-purpose AI-to-SVG illustrator and should not be used for textured animal scenes, painterly character art, complex product renders, or traced raster outputs.

## Sources

[1]: https://helpx.adobe.com/in/stock/contributor/help/vector-requirements.html "Requirements for contributing vector art to Adobe Stock | Stock Contributor"
[2]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-vectors/vector-submission-overview.html "Vector submission overview | Stock Contributor Help"

## Buyer-job and supply-proxy evidence

Adobe's icon submission overview states that icons and icon sheets help customers locate design elements for marketing materials, user interfaces, presentations, and animations. It defines icons as simplified symbols for interface navigation or infographic components and describes icon sheets as themed groups that maintain visual consistency [3]. Google Material Design similarly defines system icons as simple, minimal representations of common UI concepts, optimized for clarity across sizes and platforms; it documents use in web, Android, iOS, mockups, and prototypes [4]. These are buyer-job signals, not proof that any StockForge asset will sell.

Adobe's pattern documentation describes patterns as repeatable designs applied as fills or strokes, with custom tiles that control size, spacing, overlap, and rotation [5]. This supports a real design workflow, but the current StockForge pattern preset remains geometric and limited; a pattern with complex illustrations would require a different preset and stronger QA.

Snapshot Adobe search supply proxies collected on 25 August 2026:

| Query | Visible result count | Interpretation |
|---|---:|---|
| `file management icon` | 384,106 | Very crowded broad utility phrase |
| `utility icons` | 604,515 | Crowded broad infrastructure/utility phrase |
| `"tech icons"` | 25,018 | Smaller phrase but still generic and competitive |
| `"icon pack"` | 86,903 | Moderate-broad pack phrase; theme specificity still needed |
| `seamless geometric pattern` | 6,279,918 | Extremely crowded broad pattern phrase |
| `geometric pattern` | 24,763,273 | Extremely crowded broad pattern phrase |

Counts are snapshots of Adobe search pages and supply proxies only. They do not measure demand, sales, ranking, approval probability, or conversion.

## Added sources

[3]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-icons/single-vector-icons-sheets-submission-overview.html "Single vector icons and sheets submission overview | Adobe Stock Contributor Help"
[4]: https://m3.material.io/styles/icons/applying-icons "Icons | Material Design 3"
[5]: https://helpx.adobe.com/illustrator/desktop/paint-and-fill/create-and-edit-patterns/patterns-overview.html "Pattern overview | Adobe Illustrator Help"

## Monochrome convention and current quality gap

Adobe's vector requirements page, updated 7 April 2026, says customers use vectors for logos, branding, digital illustrations, packaging, motion graphics, and more, including changing icon colors. It also recommends logical editable groups/layers, avoiding unnecessary color swatches/effects, and transparent backgrounds rather than a checkerboard faux background [6]. Adobe's icon-sheet overview says icons are simplified visual communication tools that prioritize clarity and instant recognition over artistic complexity; icon sheets group related symbols by theme/style for consistent reuse [7].

Google's Material Icons guide provides a concrete design-system precedent for monochrome: active icons on light backgrounds are commonly black at partial opacity, and icons can be styled to other colors through tinting/CSS. The guide describes icons as simple, minimal representations of universal UI concepts optimized for clarity across sizes [8]. This explains why monochrome appears frequently in utility icon search results: it is flexible as an alpha-mask/tintable base and avoids committing the buyer to a palette. It does **not** prove that most Adobe Stock icons are monochrome, nor does it prove monochrome assets sell better.

The two StockForge trials have a different problem than color alone. Trial 1 uses generic primitives and thick strokes whose semantic marks touch or cross their base shapes by construction. Trial 2 adds decorative circular containers but fails to reserve an inner safe zone: child document corners, arrowheads, and strokes approach or cross the container boundary. Both pass XML/native-element checks because the current QA does not measure geometric clearance, stroke envelopes, pairwise overlaps, or thumbnail perception.

The correct response is not simply to recolor the existing SVG. The next route should use a monochrome-first or two-tone-neutral system, remove decorative circular containers unless they carry semantic value, apply a fixed safe grid, reduce stroke hierarchy, use consistent cap/join rules, and add geometry QA before visual review. A restrained optional accent can be kept only where it communicates state (for example, approval) rather than decoration.

[6]: https://helpx.adobe.com/in/stock/contributor/help/vector-requirements.html "Requirements for contributing vector art to Adobe Stock | Stock Contributor"
[7]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-icons/single-vector-icons-sheets-submission-overview.html "Single vector icons and icon sheets submission overview | Adobe Stock"
[8]: https://developers.google.com/fonts/docs/material_icons "Material Icons Guide | Google Developers"
