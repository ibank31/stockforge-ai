# JPEG Maturation Plan

**Tanggal:** 24 Agustus 2026
**Status:** Active plan; no new JPEG generation authorized by this document.

## Objective

Bring StockForge’s JPEG route to the highest defensible level before routine production. “Maximum” means the route is evidence-backed, technically gated, visually reviewed, legally/metadata-aware, and useful for a specific buyer job. It does not mean guaranteed Adobe acceptance, search placement, conversion, or earnings.

## What is already proven

The JPEG route has a verified architecture from remote ZeroGPU preview through project-local artifact/provenance, optional Kaggle finalizer handoff, JPEG/sRGB finalization, human review, XMP upload-copy preparation, and separated Android delivery. The technical gate checks JPEG format, RGB pixel mode, 4–100MP dimensions, a maximum 45MB file, embedded sRGB ICC profile, and safe decoding. Adobe’s active guidance confirms these baseline requirements and also requires the absence of watermarks/timestamps/branding, sharp focus, good lighting, and appropriate model/property permissions.[1]

The current deterministic image-quality screen checks decodability, exposure clipping, a sharpness proxy, extreme saturation, and a high-frequency residual metric. Portfolio review combines those signals with project-local duplicate/similarity checks. These checks deliberately remain screening signals, not Adobe moderation emulation.

The Real-ESRGAN x4plus contract exists and is designed to turn a 1024×1024 intermediate into 4096×4096 (16.78MP), but the actual inference benchmark in the target Kaggle environment has not been completed. The finalizer worker is private and the pipeline refuses to treat a prepared request as a GPU result. Therefore, the upscaler is not yet a proven production step.

The semantic/commercial QA seam also exists with thresholds for overall quality, commercial usefulness, integrity, artifact risk, anatomy, realism, composition, subject integrity, and text/logo risk. A real provider is still required for submission; the no-provider path fails or holds rather than pretending semantic review passed.

## Current gaps that matter most

| Gap | Why it matters | Required proof |
|---|---|---|
| Product-market fit | A technically clean scene can still be generic or replaceable | One researched buyer job with a clear visual problem and qualified human review |
| Scene distinctness | Adobe warns against repetitive or near-duplicate submissions | Distinctness plan, one strongest candidate, project-level similarity screen, human comparison |
| AI visual integrity | AI scenes can contain malformed objects, lighting errors, or implausible geometry | 100% inspection plus a real vision-capable QA provider or human review |
| Upscale quality | AI enlargement can create halos, plastic texture, invented detail, or oversharpening | One real Kaggle benchmark with source/output comparison and final technical gate |
| Composition utility | Buyers often need copy space and adaptable layouts, not only attractive centered scenes | Buyer-job-specific layout contract and thumbnail/full-size review |
| Metadata coverage | Current automatic Adobe category mapping is intentionally narrow | Reviewed lane/category mapping or explicit human category input per lane |
| Portal reality | Local PASS does not prove portal acceptance | One manual validation only after all preceding gates pass |

## Product strategy

JPEG should not compete as a stream of attractive but interchangeable scenes. Each candidate must be designed around a commercial communication job such as a website hero, editorial header, sustainability explainer, healthcare/wellness communication, authentic remote-work story, or seasonal/conceptual campaign. Adobe’s current photo overview highlights real people in natural environments, authentic everyday relationships, remote work/technology/industries, sustainable living/climate action, cultural heritage, and healthcare/wellness as popular subject areas.[2]

The current portfolio already contains conceptual lanes for AI governance, playful-surreal product metaphors, tactile material atmospheres, synthetic-media trust, returns/recommerce, digital accessibility, and related topics. These lanes are useful hypotheses, not sales claims. Before choosing the next JPEG subject, the market-intelligence layer should compare demand signals, growth, saturation/competition, buyer fit, visual differentiation, variation potential, commercial clarity, legal burden, and production cost.

## Execution sequence

### Stage 1 — Freeze the baseline

Keep the historically successful JPEG workflow and existing scene lanes intact. Record the exact prompt, model, provider, seed, preview dimensions, finalizer model, and visual-review decision for every future candidate. Do not add a new lane merely because a trend page contains a high-growth query.

### Stage 2 — Select one buyer job globally

Research official and public signals across Adobe Stock, Shutterstock, Freepik, Envato, Creative Market, Etsy where relevant, and broader design/industry sources. Separate result counts and trend growth from actual demand or sales. Exclude celebrity, brand, government, news-event, copyrighted, and legally ambiguous themes before scoring an opportunity. The output should be one ranked JPEG hypothesis, not a batch of prompts.

### Stage 3 — Strengthen the prompt and composition contract

Keep buyer context in provenance and metadata, while the image-facing prompt should express the visible subject, action, material, lighting, composition, copy-space requirement, authentic representation, and distinctness lever. Every JPEG prompt must require a clear focal point, intentional lighting, natural or purposefully restrained color, realistic texture, no accidental text/branding, and no invented UI/device details unless they are the approved subject. Adobe’s editing guidance specifically recommends clean composition, natural or intentional lighting, balanced color, authentic representation, subtle correction, and avoiding overprocessing, artificial blur/vignettes, heavy grading, flares, and other non-natural presets.[3]

### Stage 4 — Add stronger local QA before GPU cost

Run deterministic checks before any provider call: plan/preflight, prompt/negative prompt compilation, rights-risk scan, composition/layout contract, single-candidate limit, provider health/quota, and exact lineage. After preview generation, run decodability, dimensions, quality signals, duplicate/similarity checks, and a whole-image plus 100% review. A candidate that is technically clean but semantically weak remains `REVIEW` or `REJECT`.

### Stage 5 — Benchmark Kaggle finalizer once

Only after a preview passes the human visual gate should one selected preview be sent through the prepared Kaggle Real-ESRGAN route. Compare the preview and master at 100% for texture, edges, faces/hands, object geometry, noise, halos, ringing, color shifts, and invented detail. The benchmark must record source/output hashes, provider/model identity, scale, dimensions, file size, sRGB result, and final reviewer decision. Never silently lower quality to fit the file-size limit.

### Stage 6 — Semantic/commercial review

Use a real vision-capable provider only when configured and authorized. The provider must return normalized scores and notes for overall quality, commercial usefulness, integrity, artifact risk, realism, composition, subject adherence, and text/logo risk. If no provider exists, the route must remain blocked for submission while human review can still classify the artifact as review-only evidence. Adobe’s refusal guidance includes soft focus, exposure, white-balance/color issues, over-editing, noise, artifacts, unnatural saturation, and similar content; GenAI content additionally requires accurate anatomy/proportions, intentional lighting, commercial-use rights, correct labeling, and unique value.[4] [5]

### Stage 7 — Metadata, finalization, and manual Adobe package

Finalize only a human-selected master. Preserve the original preview and master lineage. Normalize to RGB/sRGB, retain 4–100MP and maximum 45MB constraints, embed reviewed title/keywords where supported, and require a safe lane/category mapping or explicit human category selection. The upload bundle must remain a copy, never overwrite the master. Adobe’s GenAI checkbox, people/property declarations, releases, terms, CAPTCHA, and final submit remain manual.

## Success gates for the next JPEG trial

A next JPEG trial should not be authorized until it has one evidence-backed buyer hypothesis, a non-generic visible concept, a prompt and negative prompt that encode the visual job, a valid pre-GPU plan, a configured provider/quota path, a single-candidate limit, and a review protocol. After generation, the preview must pass technical screening and human visual/commercial review before any upscale. After upscale, the master must pass the JPEG/sRGB gate, 100% artifact review, distinctness review, metadata review, and explicit human approval. Only then may one manual portal validation be considered.

The target is not an artificial probability. The target is a product that a qualified buyer can identify, use, and prefer over a generic alternative. Any later buyer-value percentage is an internal review estimate unless it comes from real listing data.

## Current decision

JPEG is now the active maturation track. SVG product expansion is frozen as a documented future plan. No new JPEG generation is required to complete this audit. The next safe implementation step is to strengthen and document the JPEG market-opportunity and semantic-review gates, then re-run the full regression suite. A real ZeroGPU/Kaggle trial should occur only after the user explicitly authorizes it and the provider/runtime prerequisites are available.

## References

[1]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-photos/technical-legal-requirements-photo-submission.html "Adobe — Technical and legal requirements for photo submission"
[2]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-photos/photo-submission-overview.html "Adobe — Photo submission overview"
[3]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-photos/photo-editing-best-practices.html "Adobe — Photo editing best practices"
[4]: https://helpx.adobe.com/stock/contributor/content-moderation/quality-technical-standards-reasons-content-refusal.html "Adobe — Quality and technical issues behind content refusal"
[5]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/submit-generative-ai-content.html "Adobe — Submit generative AI content"
