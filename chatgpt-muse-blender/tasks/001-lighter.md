# Task 001: Disposable Lighter (Korek Api Gas)

**Status:** pending_review
**Created:** 2026-10-12
**Target:** Accurate multi-component 3D model for educational exploded-view animation

## Target Object

Standard disposable gas lighter (korek api gas), like the common BIC-style or
generic Asian market lighter. Transparent or translucent body preferred for
educational visibility of internal components.

## Why This Object

Rich internal mechanism (flint wheel, fork, valve, gas reservoir) in a small
package. Excellent for exploded-view educational animation. Multiple interacting
mechanical parts with real functional relationships.

## Reference Requirements

ChatGPT: you mentioned having many references for lighters. Please share:
- Reliable dimension sources (manufacturer specs, technical drawings, teardowns)
- Component names and their mechanical functions
- Any cross-section diagrams or exploded-view references you can describe

## Components (to be modeled individually)

| # | Component | Qty | Function |
|---|-----------|-----|----------|
| 1 | Body / fuel tank | 1 | Translucent plastic, holds liquid butane |
| 2 | Top cap / windguard | 1 | Metal shroud around flame area |
| 3 | Flint wheel (roda) | 1 | Knurled steel wheel, creates spark |
| 4 | Flint (batu api) | 1 | Ferrocerium rod, wears against wheel |
| 5 | Flint spring | 1 | Pushes flint up against wheel |
| 6 | Fork / lever | 1 | Lifts valve when pressed, holds flint assembly |
| 7 | Gas valve / nozzle | 1 | Releases butane when fork lifts it |
| 8 | Valve spring | 1 | Keeps valve closed by default |
| 9 | Adjustment wheel | 1 | Controls flame height (on some models) |
| 10 | Fuel (butane liquid) | 1 | Visible through translucent body |

## Known Dimensions (mm) — TO BE VALIDATED BY CHATGPT

| Component | Dimension | Value | Source | Confidence |
|-----------|-----------|-------|--------|------------|
| Overall | Height | ~80 | Typical disposable | Low |
| Overall | Width | ~25 | Typical disposable | Low |
| Overall | Depth | ~12 | Typical disposable | Low |
| Body | Wall thickness | ~2 | Estimate | Low |

*All dimensions need validation from your references.*

## Assembly Relationships

- Flint wheel sits in fork arms, axle through wheel center
- Flint (rod) sits vertically below wheel, pushed up by flint spring
- Fork pivots: pressing thumb lever rotates fork, lifting gas valve
- Gas valve at top of fuel tank, normally closed by valve spring
- Windguard press-fits over top of body, surrounds wheel + valve area
- Adjustment wheel (if present) on side, controls valve opening

## Key Mechanical Interactions (for animation)

1. **Spark:** Flint wheel rotates → knurling grinds flint → sparks fall toward valve
2. **Gas release:** Thumb presses fork lever → fork lifts valve stem → butane escapes
3. **Ignition:** Sparks ignite butane at nozzle → flame
4. **Flame adjust:** Adjustment wheel changes valve lift distance

## Modeling Method

Procedural Blender Python (bpy). Each component as separate mesh object.
Units: millimeters. Z-up. Body material: translucent plastic (transmission).

## Expected Outputs

- `lighter.blend` (Blender project)
- Component inventory report (part names, triangle counts, bounding boxes)
- Preview renders: front, side, top, exploded view
- Validation report: dimensions vs spec table

## Validation Criteria

1. Component count matches spec (10 parts)
2. All dimensions within ±0.5mm of validated references
3. Flint wheel knurling visible and correctly positioned above flint
4. Fork pivot geometry allows valve lift motion (no intersection)
5. No intersecting geometry in assembled state
6. Exploded view shows correct disassembly order

## Open Questions for ChatGPT

1. **Dimensions:** What are the real dimensions? Can you provide a dimension table from your references?
2. **Flint wheel:** Diameter? Width? Knurl pattern details? Axle diameter?
3. **Fork geometry:** Exact shape? Pivot point location? How does it engage the valve?
4. **Valve:** How does the nozzle look? What lifts it — direct fork contact or intermediate part?
5. **Windguard:** Hole pattern? How is it attached to body?
6. **Variants:** Should we model the simple version (no adjustment) or the adjustable version?
7. **Missing parts:** Are there components I'm missing? (e.g., seals, O-rings, filter?)

---
*ChatGPT: please review this spec against your references. Correct dimensions,
add missing components, flag mechanical inaccuracies. Be specific — this will
directly drive the Blender modeling script.*
