# StockForge External Renderer Workflow

**Status:** Active experimental lane  
**Default renderer:** GPT Image through the external ChatGPT application  
**Fallback/ideation renderer:** Z-Image-Turbo through the existing internal preview lane

## Decision

StockForge should prefer an external GPT image renderer for quality-sensitive, context-dependent microstock scenes and precise edits. OpenAI documents stronger instruction following, composition and lighting preservation during edits, and improved text rendering for its current image experience [1] [2]. This matches the direct StockForge observation that the earlier Z-Image-Turbo previews were generic or contextually incorrect.

Z-Image-Turbo remains useful as a fast open-source ideation route. Its official model card documents an efficient 8-NFE Turbo model with strong photorealism and instruction adherence, but also distinguishes the foundation Z-Image model as the higher-diversity, more controllable variant [3] [4]. These are model-level claims, not guarantees of commercial performance.

## Isolated workflow

```text
StockForge planner/brief
  -> user renders in external ChatGPT application
  -> user copies one visual source to ~/.stockforge/incoming/external/
  -> portfolio import-external
  -> SHA-256 + external provenance + candidate linkage
  -> CPU technical audit + conservative learning record
  -> user KEEP/REJECT/REVIEW
  -> portfolio prepare-external-finalizer
      JPEG: compact RGB JPEG staging -> protected RealESRGAN worker
      PNG: square 1024 RGB worker input -> isolated BiRefNet alpha worker
  -> one request-specific Kaggle job
  -> request_id matching gate
  -> master import/register + technical audit
  -> user 100% visual review
  -> visual-only final export
```

The external lane must not call ZeroGPU, revive the retired batch runner, or bypass StockForge provenance. The JPEG and PNG finalizers remain isolated. The external renderer is a renderer only; StockForge remains the audit, lineage, finalization, and packaging control plane.

## Android output contract

Kaggle outputs are downloaded only into the project workspace, never into the visual folders:

```text
/storage/emulated/0/StockForge/projects/stock-assets/kaggle-finalizer-output/
/storage/emulated/0/StockForge/projects/stock-assets/kaggle-png-finalizer-output/
```

Technical files remain there or in the other project folders. They include `request.json`, `result.json`, logs, WebP previews, intermediate PNGs, model weights, reports, and checksums.

Only these visual files may eventually be copied to Android's visible folders:

```text
/storage/emulated/0/Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/
/storage/emulated/0/Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/
```

`PREVIEW_TO_MANUS/` receives review previews only. `READY_UPLOAD_ADOBE/` receives only a master that has passed the format-specific technical gate, full-resolution visual review, metadata/package checks, and explicit user permission. No JSON, log, request, WebP, intermediate, model, or ZIP file is copied there.

The current Adobe bundle implementation is JPEG-focused. A PNG master must not be called Adobe-ready merely because Android export accepts the `.png` suffix; PNG packaging support must be audited and implemented separately before an automated PNG upload-copy is promised.

## Minimal user action

The user needs only to render the brief externally, copy the image into the incoming folder, and provide a simple KEEP/REJECT/REVIEW verdict. StockForge records the source hash, provider label, original filename, candidate/format context, technical findings, and finalizer lineage. It does not claim demand, approval, or sales.

## References

[1] OpenAI, “The new ChatGPT Images is here,” https://openai.com/index/new-chatgpt-images-is-here/  
[2] OpenAI, “GPT Image Generation Models Prompting Guide,” https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide  
[3] Tongyi-MAI, “Z-Image-Turbo model card,” https://huggingface.co/Tongyi-MAI/Z-Image-Turbo  
[4] Tongyi-MAI, “Z-Image GitHub repository,” https://github.com/Tongyi-MAI/Z-Image
