# Pre-trial Specification — Folder Upload SVG

**Tanggal:** 24 Agustus 2026
**Status:** `READY_FOR_TRIAL` lokal; **belum digenerate** dan belum divalidasi di portal.

## Hypothesis

> A single folder-upload icon may serve file-management and cloud-workflow buyers who need an editable SVG action symbol.

## Purpose

Validate recognizability, buyer-job clarity, thumbnail readability, native SVG safety, and artboard composition with exactly one local candidate before any portal decision.

## Selected route

| Field | Decision |
| --- | --- |
| Asset type | `native_object` |
| Lane | `native_vector_elements` |
| Concept | `folder-upload` |
| Product kind | `native_vector` |
| Delivery format | `svg` |
| Execution | Local deterministic native builder; no GPU/provider |
| Layout | Tight square product framing |
| Background | Transparent canvas |
| Provider call | Not allowed/needed |
| Portal status | Pending manual validation |
| Candidate count | Exactly one |

## Subject and visual mechanism

The subject is a **single recognizable folder icon with one upward upload arrow integrated into the folder front**. The visual mechanism is that the folder silhouette and upward arrow clearly communicate a file upload action.

The recommended style is **bold geometric with restrained hyper-minimal structure**. The icon should use a strong folder silhouette, one proportionate upload arrow, high contrast, transparent negative space, consistent geometry, and a centered artboard. The builder must not add a scene, screen, phone, dashboard, interface frame, packaging label, text, logo, trademark, decorative ribbon, glow, chrome, 3D material, collage, or unrelated prop.

## Metadata boundary

Working title: `Editable Folder Upload Icon for File Management`.

Metadata may describe only visible content and a reasonable visual use case. Candidate keywords include folder upload icon, file management, cloud workflow, editable SVG, native vector, upload arrow, folder symbol, digital file storage, web UI icon, mobile UI icon, and bold geometric icon. Human review must remove anything not visibly supported. The listing must not claim security, compliance, backup guarantees, official app identity, or marketplace acceptance.

Adobe’s generative-AI disclosure, category, releases, CAPTCHA, terms, and final submission remain manual. The upload bundle is not authorized by this pre-trial document.

## Deterministic gates

The persisted brief preflight passed the following checks:

| Gate | Result |
| --- | --- |
| Standalone policy | PASS |
| Subject-risk terms | PASS |
| Square composition contract | PASS |
| Spatial ambiguity contract | PASS |
| Visual mechanism present | PASS |
| Reviewed visual-first metadata | PASS |
| Local native-vector route | PASS as a local route; remote GPU is intentionally blocked |

The existing native SVG inspector must also pass: valid XML, positive dimensions, only allowed native elements, no raster/image embed, no script, no external reference, transparent canvas, and no hidden or textual content. The folder-upload preset additionally requires the expected `native-vector-folder-upload-v1` marker and must be tested for its distinctive folder and arrow geometry.

## Human visual review gate after build

The trial is not commercially accepted merely because the structural inspector passes. A human reviewer must inspect the visual without relying on the title and answer:

1. Is it identified as a folder with an upload action within two or three seconds?
2. Is the upload arrow visually integrated rather than appearing as an unrelated mark?
3. Does the silhouette remain legible at thumbnail size and on both light and dark surrounding contexts?
4. Does the object fill the square artboard with consistent margins and no excessive whitespace?
5. Is the icon useful as an editable web/mobile UI, file-management, cloud-workflow, or presentation element?
6. Is the form distinctive enough to avoid being a cosmetic duplicate of an ordinary generic icon?
7. Are the paths clean, editable, recolorable, and free of unintended artifacts?
8. Does the metadata describe only what is visible and avoid security, brand, or official-product claims?

A failure in recognizability or buyer job means `reject` even if the native SVG technical gate is `PASS`. No seed-only retry, color-only retry, batch, upload, or portal submission is permitted.

## Trial-readiness evidence

The local CLI returned:

- `readiness`: `READY_FOR_TRIAL`
- `trial_allowed`: `true`
- `provider_call_allowed`: `false`
- `single_candidate_only`: `true`
- blockers: human visual buyer-fit review and portal upload validation remain pending.

This document authorizes preparation for one local candidate but does not itself record user approval of a generated visual, marketplace acceptance, or upload readiness.

## References

The candidate and gates are based on [`SVG_MARKET_RESEARCH_2026-08-24.md`](SVG_MARKET_RESEARCH_2026-08-24.md), Adobe Stock vector/icon technical guidance, Adobe/Envato style reports, Etsy buyer-context signals, and the rejected `modular-ribbon` evidence under `../../trial_outputs/svg_modular_ribbon/`.
