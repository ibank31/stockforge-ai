# Audit Report: Existing Zippo-Style Lighter Model

**Date:** 2026-10-12
**Auditor:** Muse
**Script:** `pipeline-3d/colab-modules/lighter_model_v1.py` (v2)
**Method:** Blender 4.5.0 headless, read-only inspection (no modifications)
**Reference:** Real Zippo dimensions 38.1 × 12.7 × 57.15 mm

---

## 1. Component Inventory (VERIFIED)

All 8 components exist as **separate mesh objects**. Confirmed via `bpy.data.objects`.

| # | Object Name | Type | Verts | BBox (mm) X×Y×Z | Z Range (mm) |
|---|-------------|------|-------|------------------|--------------|
| 1 | lid | MESH | 288 | 38.00 × 16.00 × 19.00 | 38.0 – 57.0 |
| 2 | body | MESH | 96 | 38.00 × 13.00 × 38.00 | 0.0 – 38.0 |
| 3 | insert | MESH | 280 | 34.00 × 11.00 × 32.00 | 3.0 – 35.0 |
| 4 | chimney | MESH | 224 | 30.00 × 9.00 × 10.00 | 35.0 – 45.0 |
| 5 | flint_wheel | MESH | 192 | 10.00 × 6.00 × 10.00 | 38.0 – 48.0 |
| 6 | flint_spring | MESH | 128 | 3.00 × 3.00 × 19.50 | 21.0 – 40.5 |
| 7 | wick | MESH | 64 | 3.00 × 3.00 × 18.00 | 31.0 – 49.0 |
| 8 | cotton_packing | MESH | 8 | 30.00 × 8.00 × 26.00 | 5.0 – 31.0 |

**Note:** `flint_spring` is a joined object containing flint (top) + spring (bottom).
`lid` is a joined object containing lid box + 3 hinge knuckles.
`insert` is a joined object of 5 panels (bottom + 4 walls).
`chimney` is a joined object of 4 walls.

---

## 2. Overall Envelope (VERIFIED)

| Axis | Model | Real Zippo | Delta | Verdict |
|------|-------|------------|-------|---------|
| X (width) | 38.0 mm | 38.1 mm | -0.1 mm | ✓ PASS |
| Y (depth) | 19.3 mm | 12.7 mm | **+6.6 mm** | ✗ FAIL |
| Z (height) | 57.0 mm | 57.15 mm | -0.15 mm | ✓ PASS |

**Y-axis failure analysis:** The 3 hinge knuckles are positioned at Y=-7.5mm
(6.8mm behind the body rear face at Y=-6.5mm). Each knuckle has radius 2mm,
extending to Y=-9.5mm. Total depth = 9.5 - (-9.5) = 19mm... measured 19.3mm
with bevel. **The knuckles protrude too far rearward.** On a real Zippo, the
hinge is more flush with the body.

**This is a VERIFIED dimensional error, not an assumption.**

---

## 3. Hinge & Animation (VERIFIED)

- **Hinge knuckles:** 3 cylinders (r=2mm, depth=6mm, axis along X) joined to `lid`.
- **Separate hinge pin:** **NOT FOUND.** No object with "pin" in name exists.
- **Animation data:** **NONE.** Zero objects have `animation_data`. Scene frame range is 1-250 (default, not configured for this model).
- **Lid opening:** Cannot be tested — no rig, no pivot empty, no keyframes.

**To add hinge functionality:**
1. Create separate pin cylinder (r≈1.5mm, length≈30mm along X at knuckle location)
2. Create Empty at hinge axis as pivot
3. Parent lid to pivot Empty
4. Animate pivot rotation for open/close

---

## 4. Geometric Plausibility (VERIFIED unless noted)

### Correct nesting (verified via bounding boxes):
- Insert (34×11mm) inside body (38×13mm): 2mm X-clearance, 1mm Y-clearance ✓
- Cotton (30×8×26mm) inside insert interior: fits ✓
- Wick passes through chimney, tip extends 4mm above chimney top ✓ (correct — wick tip is exposed)
- Chimney sits on insert top (Z 35mm = insert top) ✓

### Intentional intersections (verified):
- **Flint tip extends 2.5mm into flint wheel.** Flint top at Z=40.5mm, wheel bottom at Z=38.0mm. This represents the spring-loaded contact, but the **geometry physically intersects** — not just touches. For a static render this is invisible; for exploded view the parts will clip during separation.
- **All "OVERLAP" warnings from AABB check are expected nesting**, not errors — except the flint/wheel intersection above.

### Missing geometry (verified by inspection):
- **No hinge pin** (see §3)
- **No felt pad** at insert bottom (real Zippos have this)
- **No chimney holes** — the chimney is 4 solid walls. Real Zippo chimneys have ~16 holes. The reference photo shows the hole pattern clearly.
- **Flint wheel knurling is NOT real geometry.** The wheel is a smooth beveled cylinder (192 verts). No teeth, grooves, or knurl pattern modeled.
- **No cam/spring for lid** — the lid has no stay-open mechanism detail.

---

## 5. What Would Be Required for Improvements

| Improvement | Effort | Approach |
|-------------|--------|----------|
| Fix Y-dimension (knuckle position) | Low | Move knuckles to Y=-6.5mm (flush), reduce radius to 1.5mm |
| Add hinge pin | Low | Cylinder r=1.5mm, length 30mm, at (0, -6.5, 40)mm along X |
| Lid open animation | Medium | Pivot Empty + parent + 2 keyframes (closed/open at 95°) |
| Real knurling geometry | Medium | Procedural teeth via array modifier or manual loop (est. 20-30 teeth) |
| Chimney holes | Medium | Boolean modifier with cylinder cutters (16 holes) or texture |
| Felt pad | Low | Thin box (30×8×1mm) at insert bottom Z=3.5mm |

---

## 6. Assumptions vs Verified

**VERIFIED** (Blender measurement):
- All 8 objects exist as separate meshes
- All bounding box dimensions above
- Y-axis dimensional error (+6.6mm)
- No hinge pin, no animation data
- Flint/wheel geometric intersection (2.5mm)
- Chimney has no holes (solid walls)

**ASSUMED** (from script comments, not independently verified):
- That 38.1×12.7×57.15mm are correct real Zippo dimensions (from script docstring)
- That brass material values match the reference photo (visual judgment)
- That the 0.5mm lid seam gap is correct (mentioned in render script, not in model)

---

## 7. Preview Render

A quick Cycles preview (16 samples) confirms the assembled model looks like
a closed Zippo from the hinge side. Brass material renders correctly.
Hinge knuckles visible at the lid/body seam.

*Render: `renders/audit/` (to be pushed)*

---

## Summary for Production Decision

**Strengths:**
- 8 separate parts, correct nesting, plausible proportions (except Y)
- Clean topology, reasonable vertex counts
- Materials already tuned for brass
- Existing render pipeline (`render-kanonis-korek.py`) locked and working

**Weaknesses:**
- Y-dimension wrong (+52% too deep due to hinge placement)
- No hinge pin, no animation rig
- Chimney missing holes (highly visible in reference photo)
- Flint wheel has no knurling geometry
- Flint intersects wheel (2.5mm)

**Estimated fix time:** 2-4 hours for dimensional fix + hinge pin + felt pad.
Chimney holes + knurling: additional 2-3 hours.
Lid animation: additional 1-2 hours.
