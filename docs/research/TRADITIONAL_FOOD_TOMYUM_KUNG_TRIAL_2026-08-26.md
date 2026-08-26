# Traditional food trial — Thailand Tomyum Kung

## Decision

StockForge selected **Thailand — Tomyum Kung** as the first traditional-food trial after a read-only inspection of the food-research branch. The research branch was not checked out, merged, rebased, modified, or deleted. The lane was added to `main` as `traditional_food_tomyum_kung` with one concept, `tomyum-kung`, and `test_cap=1`.

The selection is an evidence-bound production hypothesis. It is not a prediction of demand, ranking, approval, downloads, conversion, revenue, or sales.

## Evidence and buyer job

UNESCO identifies Tomyum Kung as a traditional prawn soup from Thailand and describes prawns boiled with herbs including lemongrass, kaffir lime leaves, galangal, and shallots. UNESCO also records its recognizable aroma and vibrant colours, and places its origin among Buddhist riverside communities in Thailand's Central Plains. [1]

The buyer job is intentionally narrow: a single recognizable bowl for recipe editorial, restaurant menu concepts, culinary-tourism articles, food education, and Thai-cuisine social content. The visual identity is ingredient-led rather than dependent on random cultural decoration. The prompt prioritizes prawns, red-orange broth, straw mushrooms, lemongrass, makrut lime leaves, galangal, shallots, a warm ceramic bowl, a clean white background, and a complete thumbnail-readable silhouette.

Adobe's current contributor guidance places food-focused subject matter in category **7 — Food**, which is a suggested category only and remains subject to portal verification. [2]

## Controlled generation

| Field | Value |
|---|---|
| Lane | `traditional_food_tomyum_kung` |
| Concept | `tomyum-kung` |
| Batch | `traditional_food_tomyum_kung-20260826T124113Z-aed031a2` |
| Preview execution | `32a8bd7c-6565-547c-8433-2fa51b7baf3c` |
| Preview artifact | `ed286457-fd83-4065-a1e2-6757d476bf2e` |
| Provider | `huggingface-zerogpu` / `z-image-turbo` |
| Canvas | 1024×1024 square, one candidate only |
| User verdict | KEEP |
| Evaluation | visual 4/5; technical 3/5; buyer fit 4/5; metadata accuracy 4/5; overall 3.75/5 |
| Marketplace outcome | `not_submitted` |

The preview is a bowl illustration with clearly readable prawns, red-orange broth, mushrooms, aromatic stalks, green leaves, and lime. A non-blocking deviation is recorded: the model introduced pale curved strands that resemble noodles even though the prompt prohibited noodles. The user accepted the candidate; no silent edit or second visual generation was made.

## JPEG finalization

The first finalizer submission was Kaggle kernel `iqbalteguh/stockforge-finalizer` version 14 on a P100 and failed with `CUDA error: no kernel image is available for execution on the device`. The log states that Tesla P100 is `sm_60`, while the current PyTorch runtime supports `sm_70` through `sm_120`; the failure occurred in RealESRGAN during `model.half()`. This was an accelerator/runtime incompatibility, not a source-image, VRAM, storage, or metadata failure. The protected JPEG worker was not modified.

The identical request was then submitted once to a compatible T4 as kernel version 15. It completed successfully with `RealESRGAN_x4plus` at 4×. The request remained bound to the same preview artifact and source checksum.

| Finalizer field | Value |
|---|---|
| Request | `master-ed286457-fd83-4065-a1e2-6757d476bf2e-696f541d` |
| Kaggle kernel | `iqbalteguh/stockforge-finalizer`, version 15 |
| Master execution | `4c8d3bfd-c3ef-49ae-95fb-5e0fbafce0fa` |
| Master artifact | `7d506166-62b2-4c61-988c-4c72d42a8860` |
| Master path | `masters/ed286457-fd83-4065-a1e2-6757d476bf2e-master.jpg` |
| Dimensions | 4096×4096; 16.777216 MP |
| Format | JPEG, RGB, sRGB, quality 95, 4:4:4 |
| Master SHA-256 | `2e32b8fac36c5e3cfc7ce7c4b3c08a4a1a5b6ada2bba8ff0d4db3ef22c2bb655` |
| Status | `review_ready` / `visual_review_required` |

The importer verified the request kind, request ID, source lineage, source dimensions, source checksum, target dimensions, master checksum, JPEG/RGB/sRGB gate, and megapixel minimum. No upload copy or Adobe submission was created.

## Visual audit

The master was inspected at whole-image scale and through four 2048×2048 tiles. The bowl silhouette, prawns, mushrooms, broth, aromatic herbs, lime slices, ceramic material, and soft cast shadow remain coherent. No readable text, logo, watermark, human hand, unrelated scene element, fatal object drift, or severe halo was observed in the agent audit. The pale noodle-like strands remain visible in the broth and are retained as a review note because the user accepted the preview.

The master is therefore **technically finalized and review-ready**, not automatically ready for marketplace acceptance. The user must still inspect the actual master at 100% and independently verify Adobe's AI disclosure, metadata, category, rights/compliance fields, Terms, CAPTCHA, and Submit action.

## References

[1]: https://ich.unesco.org/en/RL/tomyum-kung-01879 "UNESCO Intangible Cultural Heritage — Tomyum Kung"

[2]: https://helpx.adobe.com/stock/contributor/content-policies-guidelines/metadata/choose-right-category-content.html "Adobe Stock Contributor — Choose the right category for your content"
