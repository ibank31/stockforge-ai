# Task 001: Ballpoint Pen (Click-Type)

**Status:** pending_review
**Created:** 2026-10-12
**Target:** Accurate multi-component 3D model for educational exploded-view animation

## Target Object

Standard retractable ballpoint pen (click-type), similar to Pilot G2 or generic office pen.

## Reference Requirements

ChatGPT: please help identify reliable dimension sources. Manufacturer specs preferred.
If exact brand dimensions unavailable, propose standard/typical dimensions with sources.

## Components (to be modeled individually)

| # | Component | Qty | Notes |
|---|-----------|-----|-------|
| 1 | Barrel (outer body) | 1 | Main cylinder, grip section |
| 2 | Click button (top) | 1 | Push mechanism cap |
| 3 | Click mechanism (cam) | 1 | Internal rotating cam |
| 4 | Spring | 1 | Compression spring |
| 5 | Ink cartridge | 1 | Tube + ink reservoir |
| 6 | Ballpoint tip | 1 | Metal tip with ball |
| 7 | Nose cone | 1 | Front tapered section |
| 8 | Clip | 1 | Pocket clip |

## Known Dimensions (mm) — TO BE VALIDATED

| Component | Dimension | Value | Source | Confidence |
|-----------|-----------|-------|--------|------------|
| Overall | Length | ~140 | Typical | Low — needs source |
| Barrel | Diameter | ~10 | Typical | Low — needs source |
| Barrel | Length | ~120 | Estimate | Low — needs source |

## Assembly Relationships

- Nose cone threads onto barrel front
- Ink cartridge slides inside barrel, tip protrudes through nose cone
- Spring sits around cartridge, compressed between nose cone and barrel shoulder
- Click mechanism at barrel rear, activated by click button
- Clip attaches to barrel upper section

## Modeling Method

Procedural Blender Python (bpy). Each component as separate mesh object.
Units: millimeters. Z-up.

## Expected Outputs

- `pen.blend` (Blender project)
- Component inventory report (part names, triangle counts, bounding boxes)
- Preview renders: front, side, exploded view
- Validation report: dimensions vs spec table

## Validation Criteria

1. Component count matches spec (8 parts)
2. All dimensions within ±0.5mm of validated references
3. No intersecting geometry in assembled state
4. Exploded view shows correct disassembly order

## Open Uncertainties (for ChatGPT)

1. Exact dimensions — need reliable source or standard reference
2. Click mechanism internal geometry — simplified or detailed?
3. Spring coil parameters (wire diameter, coil count, pitch)
4. Ballpoint tip internal structure (ball diameter, socket)

---
*ChatGPT: please review this spec. Flag any missing components,
questionable dimensions, or mechanical inaccuracies. Propose corrections
with sources where possible.*
