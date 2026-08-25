# Diagnosis dua trial SVG

## Trial 1: file-flow micro-set

The first trial uses eight standalone symbols on a two-row grid. The symbols are visually consistent but mostly broad UI primitives: folder, upload, download, cloud, sync, archive, document, and share. The grid has large empty vertical gaps, no visual sequence, no grouping logic beyond equal-sized icons, and no framing system. It is technically clean but commercially generic. It communicates “file icon set,” not a differentiated buyer workflow.

## Trial 2: document-review-delivery micro-set

The second trial adds circular containers and changes several symbols to document review, approval, archive, restore, sync, and share. This increases theme specificity, but the implementation places thick outlines and action marks inside a small circular container without calculating the visible stroke envelope. In the intake icon, the upward arrow reaches beyond the circle's top boundary. In multiple symbols, document corners, arrowheads, circular outlines, and internal strokes come too close to or visually merge with the outer ring. The rendered preview therefore shows collisions and cramped joins even though XML/native-element validation passes.

## Root causes

1. **The QA gate is structural, not geometric.** It checks allowed tags, XML validity, dimensions, and forbidden embeds, but it does not compute bounding-box clearance, stroke envelope, overlap, minimum gap, or clipping risk.
2. **The design system is internally contradictory.** Circular containers are treated as decoration, while the symbol geometry is sized as if it had an open canvas. A container radius of 210 with 24px stroke leaves a much smaller usable area than the child geometry assumes.
3. **Stroke widths are too heavy for the available icon cell.** Several 24–34px strokes and arrowheads are placed within approximately 420px diameter containers, so small geometric errors become visible collisions.
4. **The set was designed as eight independent primitives, not as a composition.** There is no sequence line, editorial rhythm, focal hierarchy, or intentional contrast between action types. The result is consistent but flat and template-like.
5. **Semantic redundancy remains.** Review, approve, archive, restore, and sync are distinguishable only after explanation. At thumbnail scale, some document/action combinations compete with the container ring instead of owning a clear silhouette.
6. **The current renderer displays transparent artwork on a dark viewer backdrop.** That is not a file defect, but it makes pale shapes and edge clearance harder to judge. A white and checkerboard review render should both be generated before approval.

## Corrective direction

A third attempt should not be a minor coordinate tweak or recolor. The design needs a new layout grammar: fewer decorative rings, larger working cells, deliberate safe zones, consistent 16–20px stroke hierarchy, and a light connecting workflow spine or numbered-free sequence rhythm that explains the set without text. Every icon should be checked inside a bounded cell with an explicit inner safe radius. A geometry QA pass should reject any child path, polygon, circle, or stroke envelope that crosses the inner boundary, and should flag pairwise overlaps above a conservative threshold.

The third attempt should remain unbuilt until the revised brief and new geometry QA pass are approved. No upload, metadata package, or marketplace claim is authorized by this diagnosis.
