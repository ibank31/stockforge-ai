# StockForge Upload-Readiness Research 2026

**Prepared by:** Manus AI  
**Purpose:** Define an evidence-based delivery standard for StockForge’s fully Generative-AI visual assets before any marketplace upload.  
**Scope date:** 24 August 2026. Marketplace rules can change; the contributor portal and terms in force at submission remain controlling.

## Executive conclusion

A clean image file is **not automatically a stock-ready asset**. Readiness requires four independent conditions: technical compliance, visual quality, rights/policy compliance, and truthful marketplace-specific metadata. The first StockForge test image validated the new standalone runtime, but its 1024 × 1024 WebP output is a **review preview**, not an upload master: it is about 1.05 MP, while Adobe and Shutterstock specify a 4 MP floor and 123RF’s published GenAI guidance specifies 6 MP.[1] [7] [15]

StockForge should therefore produce one **market-neutral master candidate** at a preferred 6 MP or greater, in RGB/sRGB JPEG format, and create a per-market eligibility matrix. This does not mean every marketplace accepts GenAI. Official contributor policies currently support Adobe Stock and Dreamstime as initial targets for fully generated images; Shutterstock, Getty/iStock, Alamy, and Depositphotos state that they do not accept this type of contributor submission.[2] [8] [10] [11] [14]

> **Operating rule:** The app may label an asset `review_ready` after generation. It may label an asset `submission_ready_adobe` or `submission_ready_dreamstime` only after all technical, visual, policy, metadata, and human-review gates pass. It must never label a fully GenAI asset “ready for every marketplace.”

## 1. Marketplace eligibility and delivery requirements

The following is a policy matrix, not a claim about marketplace popularity or sales potential. “Conditional” means the cited public guide is older or incomplete, so the current contributor portal must be verified manually before upload.

| Marketplace | Fully GenAI contributor asset | Minimum file evidence | AI disclosure / classification | StockForge action |
|---|---|---:|---|---|
| **Adobe Stock** | Eligible if policy, rights, and quality requirements are met.[2] | JPEG photo, minimum **4 MP**.[1] | Mark **Created using generative AI**. Use fictional people/property declaration only when applicable.[2] | **Primary target**; run all gates. |
| **Dreamstime** | Eligible under stated conditions.[12] | JPG, RGB/sRGB, **3–70 MP**.[12] | Select `Illustrations & Clipart/Generative AI`; title or description must clearly say AI-generated.[12] | **Secondary target**; prohibit realistic visible faces and GenAI editorial content. |
| **123RF** | Public contributor blog says eligible if requirements are met.[15] | Minimum **6 MP**.[15] | `AI Generated Images` category only.[15] | **Conditional target**; verify live policy first because cited rule was last updated in 2023. |
| **Freepik Contributor** | Historical official guidance describes an AI upload check/tag.[16] | `DATA NOT PUBLICLY AVAILABLE` in cited AI guidance. | Upload check adds `ai_generated` tag.[16] | **Conditional target**; verify current portal and terms first. |
| **Shutterstock** | **Not eligible.** Shutterstock says it does not accept GenAI submissions from contributors.[8] | JPEG/TIFF, 4 MP for normally eligible content.[7] | Not applicable to fully GenAI contributor output. | **Block** delivery for fully GenAI assets. |
| **Getty Images / iStock** | **Not eligible.** Getty says it does not accept GenAI-created content; limited AI retouching on traditional work is a different case.[9] [10] | Not applicable to fully GenAI output. | Not applicable. | **Block** delivery for fully GenAI assets. |
| **Alamy** | **Not eligible.** Alamy says it does not accept AI-generated imagery.[11] | Traditional image QC requires JPEG and >17 MB uncompressed open-file size.[11] | Not applicable to fully GenAI output. | **Block** delivery for fully GenAI assets. |
| **Depositphotos** | **Not eligible.** It does not accept AI-generated files from external contributors.[13] [14] | Not applicable to fully GenAI output. | Not applicable. | **Block** delivery for fully GenAI assets. |

## 2. Recommended StockForge production master

The master standard below is a **StockForge recommendation**, not a statement that every marketplace guarantees acceptance. It deliberately exceeds the 4 MP floor used by Adobe and Shutterstock and the 3 MP Dreamstime floor, while meeting 123RF’s published 6 MP GenAI guidance.[1] [7] [12] [15]

| Field | Recommended production rule | Reason and evidence class |
|---|---|---|
| Master purpose | One unbranded, non-watermarked, no-text master per distinct concept. | Avoid duplicate and watermark refusals. **A — official policy**.[2] [4] |
| File format | JPEG (`.jpg`) for raster/photo-style delivery. Do not hand a raw WebP preview to a stock uploader. | Adobe photo upload is JPEG; Shutterstock accepts/recommends JPEG; Dreamstime requires JPG.[1] [7] [12] |
| Color | RGB with embedded **sRGB** ICC profile. | Shutterstock recommends sRGB to avoid conversion changes; Dreamstime requires RGB/sRGB.[7] [12] |
| Pixel area | Preferred minimum **6 MP**; never below the destination’s explicit minimum. | Cross-market target derived from 123RF’s published GenAI rule; Adobe/Shutterstock lower floor remains 4 MP. **E — StockForge policy inference**.[1] [7] [15] |
| Suggested square master | `2450 × 2450 px` (6.00 MP) or larger. | Meets preferred target. **E — implementation recommendation.** |
| Suggested landscape master | `3000 × 2000 px` (6.00 MP) or larger. | Meets preferred target. **E — implementation recommendation.** |
| Suggested portrait master | `2000 × 3000 px` (6.00 MP) or larger. | Meets preferred target. **E — implementation recommendation.** |
| Suggested 4:5 master | `2400 × 3000 px` (7.20 MP). | Useful when a vertical marketing composition is intentionally designed. **E — implementation recommendation.** |
| Suggested 16:9 master | `3270 × 1840 px` (6.02 MP). | Useful only when the concept genuinely needs a wide composition. **E — implementation recommendation.** |
| Bit depth / alpha | Export an ordinary flattened RGB JPEG, no alpha channel for the raster-photo delivery lane. | Keeps the delivery format aligned with JPEG workflows. **E — implementation recommendation.** |
| File integrity | Decode successfully; dimensions, MIME type, pixel area, RGB mode, ICC presence, and extension must agree. | Deterministic technical gate. **E — implementation recommendation.** |

### About upscaling

A generated 1024 × 1024 image may be enlarged, but pixel count alone is not evidence of quality. Dreamstime’s contributor guidance notes that scaling can create blurry artifacts when viewed at full resolution; Adobe requires artifacts/noise to be minimized and expects the main subject to be clean and usable.[3] [12] StockForge should therefore prefer **native generation at a production resolution** when the worker can sustain it. If an upscale is used, it must remain a provisional master and pass an additional full-resolution human inspection. It must never be promoted merely because its dimensions reach 6 MP.

## 3. Why stock images are commonly rejected

The following rejection taxonomy consolidates official marketplace rules. It is intended to produce actionable machine checks and required human checks, not to predict moderation outcomes.

| Rejection family | What reviewers/platforms flag | StockForge prevention |
|---|---|---|
| **Insufficient technical file** | Wrong format, insufficient pixel area, unsupported color profile, failed decoding, or unsuitable output dimensions. Adobe requires 4 MP JPEG photos; Shutterstock requires 4 MP and recommends sRGB; Dreamstime requires JPG/RGB/sRGB 3–70 MP.[1] [7] [12] | Enforce `TECHNICAL_PASS` only after JPEG + RGB + sRGB + destination pixel area checks. Treat worker preview output as non-uploadable. |
| **Blur, noise, artifacts, pixelation** | Soft subject, noise, halos, chromatic fringing, over-processing, broken detail, bad focus, weak lighting, or blur visible at 100%.[3] [4] [11] | Create 100% inspection instructions and machine reports; human reviewer must inspect subject edges, gradients, transparent surfaces, tiny details, and shadows. |
| **GenAI defects** | Malformed body/object geometry, odd anatomy, extra limbs/digits, distorted/incoherent objects, impossible shadows, depth, lighting, proportions, or model inconsistencies.[4] [5] [15] | Add explicit `visual_anomaly_review_required`; reject if any defect appears, even when technical metadata passes. Avoid people as a first production lane. |
| **Embedded or incoherent text** | Watermarks, signatures, logo-like marks, unreadable pseudo-text, misspellings, or text that does not make commercial sense.[4] [5] [12] [15] | Default prompt bans text, letters, numerals, watermarks, stamps, labels, and screens. Human review confirms no pseudo-typography; do not rely on OCR alone. |
| **IP, brands, real people, property, or news** | Trademarks, branded packaging, copyrighted artwork/designs, named real people/characters/artist styles, government agencies, actual-news claims, recognizable property without appropriate releases.[2] [4] | Prompt/title/keyword denylist; rights-risk flag; target isolated fictional objects. Human reviewer decides release status and commercial suitability. |
| **Wrong or misleading metadata** | Irrelevant keywords, keyword stuffing, mismatched title/description, wrong category, wrong language, repeated keywords, missing GenAI disclosure.[2] [4] [6] [12] | Generate metadata draft only; run linter; require review against final pixels. Keep marketplace-specific metadata separate. |
| **Near duplicates / spam** | Flips, crops, different background colors, filters, minor color shifts, same composition, repeated icons, or superficially varied batches.[4] [7] [17] | Require concept-level uniqueness, perceptual/embedding similarity checks, and an explicit different buyer use case for each asset. |
| **Weak commercial usefulness** | An otherwise clean image may still be refused or perform poorly when the concept is generic, confusing, overrepresented, or lacks a clear buyer purpose. Dreamstime notes commercial potential is assessed alongside technical/aesthetic suitability.[12] | Reject outputs that do not visually communicate the niche brief; maintain buyer use-case and unique-value fields per plan. |

## 4. Metadata rules for StockForge

Adobe’s current metadata guidance recommends short, accurate titles, ideally below 70 characters; up to 49 relevant keywords; strongest terms in the first ten positions; one language; and no repeated keyword, personal information, IP, brand, artist, or real-person references.[6] Adobe further prohibits artist names, real people, fictional characters, copyrighted works, government agencies, third-party IP, and descriptions implying an actual news event in GenAI prompts, titles, or keywords.[2]

| Metadata field | Required StockForge rule | Gate |
|---|---|---|
| Title | Factual, visual-first, single language, ≤70 characters for Adobe candidate. No clickbait, sales claim, brand, artist, person, agency, or real event claim. | Automatic lint + human confirmation. |
| Description | Describe visible objects, composition, and conceptual use honestly. Do not invent a specific organization, regulation, location, product, or event. | Automatic denylist + human confirmation. |
| Keywords | 15–49 unique, relevant terms; first 10 describe the visible primary subject and buyer concept. Remove generic filler and every term not verifiable in the image. | Keyword dedupe/rank lint + human confirmation. |
| AI disclosure | Store `created_with_generative_ai=true`. Export marketplace-specific instructions, not a universal claim. | Required for Adobe; required category/title handling for Dreamstime. |
| People/property | Default: `no_recognizable_people_or_property=true`. If false, stop for human release/policy review; do not infer clearance from a prompt. | Blocking human gate. |
| Content classification | Store `suggested_content_type`; require reviewer choice based on visual characteristics. A 3D conceptual asset should not be auto-labeled photo, illustration, or vector merely from its prompt. | Human gate. |

## 5. Required status model

```text
planned
  → preview_generated
  → technical_failed | visual_review_required
  → policy_review_required
  → review_ready
  → submission_ready_adobe | submission_ready_dreamstime | conditional_market_review
  → submitted (manual account action only)
  → accepted | refused | withdrawn
```

`submission_ready_*` means the package has passed StockForge’s internal checks. It is **not** a guarantee of acceptance, licensing, search rank, downloads, or sales. Only the marketplace moderator can accept an asset, and only the contributor’s own account data can show actual approval/download performance.

## 6. Final download package to Android

A mature download must be a review package, not a folder of unnamed images. For every distinct asset, the ZIP should contain the following:

| File | Purpose | Required before manual upload |
|---|---|---|
| `master/<asset_id>.jpg` | The selected 6 MP+ JPEG candidate, not the 1024 WebP preview. | Yes |
| `preview/<asset_id>.webp` | Lightweight phone-review file. Never upload this to stock. | Optional |
| `TECHNICAL_READINESS.json` | Dimensions, MP, JPEG/RGB/sRGB checks, file size, decode result, transform/upscale history, and pass/fail reasons. | Yes |
| `VISUAL_REVIEW.md` | Human checklist for artifacts, pseudo-text, anatomy, object logic, lighting, shadow, background, branding, and distinctness. | Yes |
| `MARKETPLACE_ELIGIBILITY.json` | Adobe/Dreamstime/conditional/blocked status plus the rule date and source. | Yes |
| `metadata/adobe.csv` | Adobe title, keywords, category suggestion, GenAI disclosure instruction, fictional people/property reminder. | Yes for Adobe candidate |
| `metadata/dreamstime.csv` | Dreamstime title/description/keywords/categories and GenAI category instruction. | Yes for Dreamstime candidate |
| `manifest.json` | Immutable lineage: plan, brief, prompt, negative prompt, model/version, provider, seed, generation time, finalization steps, checksum. | Yes |
| `REVIEW_CHECKLIST.md` | Final manual sign-off; must be marked reviewed before package becomes `submission_ready_*`. | Yes |

## 7. Prioritized implementation roadmap

### Priority 0 — Keep current safety boundary

Do not generate batches while final output is only a 1024 × 1024 WebP. The current output is useful for prompt/runtime validation but must remain `review_ready` only.

### Priority 1 — Add production-master finalization

Introduce a `finalize` step that either requests a native 6 MP+ raster from a capable provider or creates a separately labeled enlarged candidate. It must export JPEG RGB/sRGB, record every transformation, and fail on incorrect extension/MIME/mode/dimension/profile. Native resolution is preferred; an enlarged output requires full-resolution review.

### Priority 2 — Build marketplace eligibility into the package

Replace a single generic “upload-ready” field with a marketplace matrix. For fully GenAI images, default values should be:

```json
{
  "adobe_stock": "review_required",
  "dreamstime": "review_required",
  "123rf": "conditional_verify_current_policy",
  "freepik": "conditional_verify_current_policy",
  "shutterstock": "blocked_fully_genai_contributor_policy",
  "getty_istock": "blocked_fully_genai_contributor_policy",
  "alamy": "blocked_fully_genai_contributor_policy",
  "depositphotos": "blocked_fully_genai_contributor_policy"
}
```

### Priority 3 — Add visual and metadata gate records

Technical checks alone cannot see anatomy, pseudo-text, bad object logic, or brand similarity. The system must require reviewer statuses for `visual_integrity`, `rights_risk`, `metadata_accuracy`, `distinctness`, and `marketplace_declaration`. The app should record a refusal reason if a marketplace later rejects an asset, enabling evidence-based prompt and pipeline improvements.

### Priority 4 — Add distinctness control before batch scale

Generate one concept at a time until its quality is proven. Before batch expansion, compare candidate fingerprints and plan fields such as primary subject, buyer use case, composition, semantic metaphor, color logic, and copy-space intent. A new color, crop, flip, filter, or seed is not enough.

## 8. Immediate decision for the first AI-governance test

The first result should be preserved as `deployment_validation_preview`, not finalized for upload. It proved the construction prompt injection has been removed, but it is 1.05 MP WebP and has visual concerns: two rather than clearly three review tokens, abstract buyer meaning, and pseudo-text-like line marks. It should not enter an upload package. The next test should be generated at a production-capable size, use text-free tokens, include the intended three distinct gate elements, and be checked at 100% before any metadata is finalized.

## References

[1]: https://helpx.adobe.com/stock/contributor/content-policies-guidelines/content-policies/content-upload-guidelines.html "Adobe Stock contributor content upload guidelines"
[2]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html "Adobe Stock Generative AI content guidelines"
[3]: https://helpx.adobe.com/stock/contributor/content-moderation/quality-technical-standards-reasons-content-refusal.html "Adobe Stock quality and technical issues behind content refusal"
[4]: https://helpx.adobe.com/stock/contributor/help/reasons-for-content-rejection.html "Adobe Stock common reasons for content refusal"
[5]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-photo-submission-guidelines.html "Adobe Stock GenAI photo submission guidelines"
[6]: https://helpx.adobe.com/stock/contributor/content-policies-guidelines/metadata/tips-effective-titles-keywords.html "Adobe Stock tips for effective titles and keywords"
[7]: https://submit.shutterstock.com/help/en/articles/10617390-what-are-the-technical-requirements-for-images "Shutterstock technical requirements for images"
[8]: https://submit.shutterstock.com/help/en/articles/10594622-content-policy-updates-ai-generated-content "Shutterstock AI-generated contributor policy"
[9]: https://www.gettyimages.com/workwithus "Getty Images work with us"
[10]: https://contributors.gettyimages.com/article/10847 "Getty Creative Content Retouching and Modification Requirements"
[11]: https://www.alamy.com/help/contributor-quality-control/ "Alamy contributor quality control"
[12]: https://www.dreamstime.com/faqs-detail-2 "Dreamstime contributor FAQ"
[13]: https://depositphotos.com/faq/contributor/article/23198060694674.html "Depositphotos contributor AI-upload policy"
[14]: https://depositphotos.com/faq/ai/article/24050422417810.html "Depositphotos AI-content approach"
[15]: https://www.blog.123rf.com/123rf-guidelines-for-ai-generated-content "123RF Guidelines for AI Generated Content"
[16]: https://contributor.freepik.com/blog/how-to-upload-ai-generated-content-on-freepik-contributor/ "Freepik Contributor AI upload guidance"
[17]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/distinct-generative-ai-submission-best-practices.html "Adobe Stock distinct GenAI submission best practices"

---

**Evidence labels:** A = current official marketplace documentation; B = official but older/public guidance that requires portal verification; E = StockForge implementation inference/recommendation. No public marketplace sales, approval-rate, or demand claim is made in this document.
