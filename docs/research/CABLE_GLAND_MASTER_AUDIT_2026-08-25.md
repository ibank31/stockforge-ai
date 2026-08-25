# Cable-gland Master Audit Notes — 2026-08-25

Master: `/home/ubuntu/stockforge-live/workspace/projects/stock-assets/masters/b846ec0c-4017-4221-a803-822b8d3264f0-master.jpg`

Dimensions: 4096×4096 px, square, 16.777216 MP. Audit uses 9 ordered overlapping grid tiles at `/home/ubuntu/stockforge-live/master-cable-gland-tiles/`.

## Tile 1 — x=0..1399, y=0..1399

Entirely clean white background; object is outside this top-left tile. No contamination or text visible.

## Tile 2 — x=1348..2747, y=0..1399

Upper object is visible in large detail. It has a faceted metallic cap/nut with a circular opening, a dark blue/black elastomer ring below it, and clean white surrounding space. No readable text, logo, watermark, or pseudo-text is visible. Minor small speck-like marks on the metal surface are visible but not yet judged blocking.

The overlap from tile 1 to tile 2 confirms a clean object boundary entering from the lower portion of the grid; no edge crop at the actual asset boundary.

## Tile 3 — x=2696..4095, y=0..1399

Clean white background; no object content or text in this tile.

## Tile 4 — x=0..1399, y=1348..2747

Mostly clean white background with only the far-right edge of the fitting entering the tile. No readable text, watermark, or severe fringe is visible. The object remains fully inside the overall master rather than cropped at the image border.

The vertical overlap between tiles 2 and 4 is consistent with a single centered object; no duplication or displaced geometry is observed at the boundary.

## Tile 5 — x=1348..2747, y=1348..2747

Central body shows faceted metal, upper dark elastomer ring, lower collar, and the beginning of the lower thread. The master contains many small bright/dark specks and irregular stippled texture on the central metal face, especially toward the right side. These appear to be texture/upscale artifacts rather than readable text or a duplicated object. Geometry remains continuous, but the surface is not perfectly clean at 100%.

## Tile 6 — x=2696..4095, y=1348..2747

Mostly white background with the rightmost edge of the central body entering from the left. No halo, colored fringe, readable text, or duplicated geometry is visible along this edge. The overlap with tile 5 is consistent with a single fitting silhouette.

## Tile 7 — x=0..1399, y=2696..4095

Clean white background; the object does not enter the left-bottom tile. No text, watermark, or contamination is visible.

## Tile 8 — x=1348..2747, y=2696..4095

Lower external thread is clearly visible and continuous, with several metallic thread ridges and a dark lower edge. The thread remains inside the canvas with clean white margin below. No duplicated ridges, broken geometry, colored fringe, or readable markings are visible in this crop.

The overlap with tile 5 confirms the lower thread belongs to the same central fitting and is not a separate object.

## Tile 9 — x=2696..4095, y=2696..4095

Clean white background; no object content enters the lower-right tile. No text, watermark, halo, colored fringe, or contamination is visible.

## Final reconciliation

All 9 ordered overlapping tiles were inspected. The master is a single centered, fully contained metallic threaded fitting with a dark elastomer ring and clean white background. The object has no readable text, labels, logos, watermarks, people, hands, tools, protected characters, or obvious duplicated geometry. The thread and outer silhouette remain continuous across overlap boundaries.

The main non-blocking visual note is the irregular stippled/speckled texture on the central metal body seen most clearly in tile 5. It may be an AI/upscale surface artifact and should receive human marketplace judgment. The master also preserves the preview's semantic limitation: the short cable stub is not visible, so the object may read as a generic threaded adapter rather than an unmistakable cable gland. This is recorded transparently; no prompt mutation or retry is authorized.

Deterministic import gate passed before this visual audit: JPEG, 4096×4096, 16.777216 MP, RGB, embedded sRGB/assumed sRGB, decodable, quality 95, 4:4:4 subsampling, 723,102 bytes. Master artifact: `7976851d-acfb-4b96-8a9f-3720694296c2`; master execution: `9b01c985-d2dd-42a4-a142-42e1118dcca6`; master path: `masters/b846ec0c-4017-4221-a803-822b8d3264f0-master.jpg`.

Status: `review_ready` / `visual_review_required`. Upload-copy preparation and manual Adobe upload remain separate gates; no upload-copy or submission has occurred.
