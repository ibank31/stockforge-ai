# Format-lane research notes — 2026-08-26

## Initial authoritative findings

Adobe's transparent-PNG guidance describes PNG as a utility asset for layering over other design elements without blocking the background. The cited use cases include isolated objects and scene elements, creative materials and textures, graphical overlays, backgrounds and patterns, banners, mockups, icons, infographics, layouts, character/element sets, and flat lays. Adobe also advises cropping away empty space, removing or minimizing shadows, isolating each object, and limiting similar variations. The same guidance states that Adobe may add white backgrounds and offer PNG assets as JPEGs while the PNG collection grows, so format differentiation must be driven by compositing utility rather than merely exporting the same image twice. Source: https://stock.adobe.com/pages/artisthub/learn/why-you-should-be-contributing-transparent-pngs-to-adobe-stock

Adobe's contributor documentation separately provides the technical submission path for PNGs with transparent backgrounds. Exact dimensions, alpha, color-space, and file-size requirements must be verified from the current technical page and enforced by the StockForge PNG gate. Source: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-pngs/submit-png-files.html

These notes are preliminary research only. They do not prove demand, sales, ranking, acceptance, or first-mover advantage for any specific niche.

## Adobe format boundary

Adobe's June 11, 2026 upload guidelines list JPEG as the accepted format for photos, JPEG/AI/EPS/SVG for illustrations, and AI/EPS/SVG for vectors; generative-AI content must be disclosed during upload. The PNG-specific page separately defines transparent PNG requirements: no background, sRGB, 4–100 MP, and maximum 45 MB. Adobe explicitly says not to submit identical files as both PNG and JPEG, so StockForge must select one product route from the buyer job instead of exporting duplicates. Sources: https://helpx.adobe.com/stock/contributor/content-policies-guidelines/content-policies/content-upload-guidelines.html and https://helpx.adobe.com/ie/stock/contributor/help/png-with-transparency.html

Adobe's PNG guidance frames the format as a utility component used inside larger compositions. It recommends minimizing empty space, isolating individual objects/elements, and removing or minimizing shadows. These requirements favor compact, clean-edged, composable objects over scene illustrations for the first PNG production trial.

## Adobe buyer-search signal

Adobe's search guidance distinguishes isolated assets (a subject alone on solid or transparent background) from transparent assets (no background, shown with a checkerboard). Adobe exposes filters for transparent backgrounds, isolated assets, individual icons, and icon sheets because these assets are intended to be dropped into existing designs, campaigns, and interfaces. This supports a PNG strategy based on composable utility, not merely on a food image with a white background. Source: https://helpx.adobe.com/stock/web/search-for-assets/transparent-and-isolated-assets.html

A search-result page for `thai ingredients illustration` was not used as evidence after the browser subsystem became unavailable; no supply count is recorded from that failed visit. Any future Adobe search counts should be stored with timestamp and treated only as supply/crowding proxies, never as demand or sales proof.

## Supply proxy snapshots

Adobe search snapshots provide directional supply signals only. At the research timestamp, `isolated food` returned 31,140,420 results, `food ingredient isolated png` 1,860,118, `traditional food illustration` 1,530,085, `recipe ingredient illustration` 454,055, `isolated herbs transparent` 399,847, `thai ingredients illustration` 19,652, and `flat food illustration` 722. These counts are not demand, ranking, approval, downloads, revenue, or sales evidence; they are used only to avoid blindly entering the most crowded generic phrasing.

The result pages show a pattern: generic isolated food and generic ingredient families are extremely crowded, while a narrowly named style/query can be much smaller but still needs buyer utility. Therefore the format engine should score a specific buyer job and compositing behavior, not simply choose PNG for any food image. The first PNG candidate should not be a generic single herb or generic bowl; it should be a distinctive, hard-edged, culturally specific utility object with a clear placement use.

## Trend and category context

Adobe's 2026 Creative Trends report identifies four themes, including **All the Feels** (sensory, texture, taste, depth) and **Local Flavors** (regional culture, local craftsmanship, authentic local appeal). This supports two different production jobs: richly composed sensory visuals are better suited to JPEG, while culturally specific, composable ingredient/object elements can serve PNG utility buyers. Adobe also says the trend report is built from internal/external research and Creative Cloud community feedback; it does not establish sales for any individual asset. Source: https://business.adobe.com/resources/creative-trends-report.html

Adobe's category guide states that categories help customers find content and that contributors should review Sensei suggestions against the actual subject, context, mood, and intent. Food covers culinary photography, ingredients, recipes, dining scenes, and food preparation. Graphic Resources covers backgrounds, textures, symbols, patterns, icons, UI components, vectors, and digital assets. This means a PNG food ingredient remains Food when its core subject is edible content; decorative overlays, icons, or generic digital resources may instead fit Graphic Resources. Source: https://helpx.adobe.com/stock/contributor/content-policies-guidelines/metadata/choose-right-category-content.html

## Candidate comparison: Thai mango sticky rice

Thailand Foundation's Central Thai Cuisine page identifies `khao niew mamuang` (mango sticky rice) as a famous Central Thai dish and explains that sticky rice is traditionally used in Central Thai dessert menus. Its seasonal-fruit guide describes mango sticky rice as a famous seasonal dessert made with ripe sweet mangoes, while also noting that it is available year-round and should not be turned into an unsupported exclusivity claim. Sources: https://thailandfoundation.or.th/central-thai-cuisine-opening/ and https://thailandfoundation.or.th/th/the-beginners-guide-to-seasonal-thai-fruits/

Adobe's exact search snapshot for `"mango sticky rice"` returned 18,604 results. This is materially smaller than `isolated food` (31,140,420) and `traditional food illustration` (1,530,085), but it remains crowded. It supports a specific buyer-job test, not a sales prediction. Source: https://stock.adobe.com/search?k=%22mango+sticky+rice%22

Candidate decision is provisional: mango sticky rice has a recognizable color/form system (yellow mango, white sticky rice, coconut sauce, banana-leaf or ceramic serving surface), a clear food/menu/recipe buyer job, and mostly smooth hard edges suitable for an alpha extraction test. It is a better first PNG subject than a soup bowl with steam, hair-like prawn legs, or a generic herb bundle. The main production risk is that sticky rice and coconut sauce can create soft/sem-transparent edges; the brief must prohibit steam, pouring sauce, floating droplets, cut-off edges, and complex table scenes.

## Implemented format decision contract

StockForge now persists a `format_decision` in every portfolio brief and exposes a `strategy_key` in the route. The engine uses the buyer job and explicit product contract: `self_contained_raster` selects JPEG for a standalone composition, `transparent_utility_cutout` selects PNG when the asset must be dropped over another design and requires true alpha, and `editable_vector_utility` selects SVG when editable geometry is the buyer requirement. A concrete AssetSpec is still validated against the decision; keyword inference is disabled when an explicit route contract is already present so generic words such as “editable” cannot misroute a raster brief.

| Product job | Preferred format | First food examples | Main gate |
|---|---|---|---|
| Standalone bowl, scene, tonal illustration, or editorial composition | JPEG | Tom Yum Kung bowl | RGB/sRGB, resolution, sharpness, artifacts, metadata, human visual review |
| Drop-in ingredient, food element, overlay, or sticker-like object | PNG | Thai mango sticky rice cutout | true alpha, clean fringe-free edge, minimal unwanted shadow, 4–100 MP, under 45 MB, human edge review |
| Reusable editable paths or icon/diagram geometry | SVG | native utility sets only | native editable structure and visual coherence; AI-to-SVG routes remain frozen |

The first PNG trial uses Thai mango sticky rice because its yellow mango, white sticky rice, restrained coconut sauce, and leaf accent create a distinctive compact silhouette with fewer difficult edges than soup steam, fur, hair, glass, smoke, or branchy herbs. The lane is a controlled hypothesis, not evidence of demand, ranking, approval, or sales.
