# StockForge Feature Roadmap — Active

**Updated:** 2026-08-25
**Branch:** `main`
**Status vocabulary:** `DONE` berarti teruji lokal atau live sesuai klaim; `LIVE` berarti exercised di runtime target; `IN PROGRESS` berarti implementasi ada tetapi belum lengkap; `BLOCKED` berarti route sengaja ditahan; `PLANNED` berarti belum diimplementasikan.

## Active product flow

```text
market evidence → buyer job → AssetSpec → prompt contract
→ pre-GPU gate → one provider request → artifact/provenance
→ preview review → learning ledger → selected finalizer
→ master technical/visual audit → metadata upload-copy
→ manual marketplace upload
```

## Current implementation ledger

| Area | Feature | Status | Evidence / boundary |
|---|---|---|---|
| Core | CLI, project init, SQLite, manifest, rollback | DONE | Core test suite |
| Core | Asset registry, execution lineage, provenance | DONE | Registry/provenance tests and rotor-armature lineage |
| Intelligence | Market evidence and buyer taxonomy | DONE | Evidence-bound research; signals are not sales proof |
| Intelligence | Niche identity and buyer-job briefs | DONE | Nine JPEG identity profiles plus technical component lane |
| Intelligence | Prompt/negative policy compiler | DONE | Rights-safe, format-aware, pre-GPU contracts |
| Intelligence | Asset-type selector and readiness report | DONE | Selector fails closed for unsupported routes |
| Intelligence | JPEG metadata preflight | DONE | Visual-first platform limits and duplicate checks without upload |
| Intelligence | Niche learning summary | DONE | `portfolio learning-summary`; descriptive decision support only |
| Generation | Remote Gradio durable adapter | LIVE | ZeroGPU `generate_remote`, durable job ID, terminal polling |
| Generation | Hugging Face ZeroGPU preview | LIVE | Space commit `935faa5`; one rotor-armature preview completed |
| Format | JPEG raster route | LIVE | Preview → learning → Kaggle finalizer → master → upload-copy path |
| Format | Native SVG route | IN PROGRESS | Local editable builders and gates; SVG production frozen |
| Format | PNG true-alpha route | BLOCKED | True-alpha/anti-fringe/trim and portal validation still required |
| QA | JPEG technical gate | DONE | Dimensions, decodability, RGB/sRGB, quality and file integrity |
| QA | Full-resolution master audit | LIVE | Rotor-armature audited in four overlapping tiles |
| QA | Semantic/commercial review | IN PROGRESS | Agent audit plus user visual verdict; no automatic approval claim |
| Delivery | Android single visual root | DONE | Only `MACHINE STOCKFORGE/PREVIEW_TO_MANUS` and `READY_UPLOAD_ADOBE` |
| Delivery | JPEG XMP/CSV/checklist bundle | DONE | Technical files remain project-local; JPEG copy only reaches Android |
| Delivery | Adobe submission | MANUAL | User verifies portal, AI disclosure, rights/releases, CAPTCHA, Terms, Submit |

## Verified reference asset

`technical_mechanical_component_illustrations--rotor-armature` is the current end-to-end reference. Its preview execution is `d3c2c121-77c7-590c-97b1-3da15ff26dcc`; preview artifact is `d419cdcf-da49-49f8-98c4-5ef4c8415920`. One private Kaggle finalizer job produced and imported a 4096×4096 RGB/sRGB JPEG master. The master passed the deterministic technical gate and full-resolution tile audit. The niche remains a promising but unproven hypothesis. It must be described as a conceptual electromechanical illustration, not as CAD, a blueprint, a certified drawing, a dimensional reference, or a manufacturer-specific component.

## Active priorities

The first priority is to preserve this workflow as the canonical baseline and make every future generation produce a preview, an evaluation record, a niche-learning record, and a clear technical/market decision. The second priority is to keep Android output clean and stable across agents by allowing only the two visual branches under `Download/MACHINE STOCKFORGE/`. The third priority is to strengthen provider-backed semantic/commercial QA without allowing it to replace human visual review. SVG value upgrades and PNG production remain frozen until their separate gates and evidence are complete.

## Non-negotiable boundaries

A preview or technical pass is not marketplace acceptance. A clean master is not a sales forecast. One generation is not proof of demand. The system must not run blind seed retries, large batches, automatic uploads, or automatic submissions. The code repository, project database, learning ledger, master lineage, HF Space, and Kaggle remote worker must be preserved when cleaning user-facing Download folders.

## Source of truth

Use `STATUS.md` for the current snapshot, `SESSION_HANDOVER.md` for continuation, `LEARNING_LOOP_POLICY.md` for user/engine responsibility and output folders, `TERMUX_CONTROL_PLANE.md` for commands, `ARCHITECTURE.md` for system design, and `CHANGELOG.md` for history. Older plans and superseded runbooks are in `archive/2026-08-25/`.
