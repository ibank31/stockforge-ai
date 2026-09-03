# StockForge Active Status

**Updated:** 2026-09-03
**Branch:** `main`
**Active scope:** [`ACTIVE_SCOPE.md`](ACTIVE_SCOPE.md)
**Operational source of truth:** [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md)

## Current architecture

StockForge memakai pembagian yang tetap: **GPT adalah brain** untuk memilih candidate, buyer job, format, prompt, dan langkah berikutnya; **Termux adalah executor** untuk menjalankan command, audit, provenance, GitHub, Hugging Face, Kaggle, dan Android export.

Produksi aktif hanya mencakup **JPEG** dan **PNG**. Infrastruktur PNG sudah diimplementasikan dan test-covered; status live pada environment Termux pengguna tetap harus dibuktikan oleh satu runtime validation nyata. Semua pekerjaan berat dilakukan oleh renderer atau worker remote. Model AI generator lokal, batch runner lama, llama.cpp/Qwen, SVG/vector, provider trial, dan pretrial tidak termasuk workflow produksi.

## Production routes

| Route | Status | Buyer job | Finalizer | Technical master gate |
|---|---|---|---|---|
| JPEG | **LIVE / verified** | Scene, environment, hero image, narrative illustration, background composition, copy-space visual | Protected Kaggle RealESRGAN | JPEG, RGB, sRGB, valid dimensions, decodable, within file/megapixel limits |
| PNG | **IMPLEMENTED / runtime validation required** | Isolated object, cutout, sticker, overlay, transparent utility asset | Isolated Kaggle BiRefNet | PNG, RGBA, true alpha, sRGB, 4096×4096 target, valid dimensions, decodable |

Technical pass tidak sama dengan marketplace approval. Kedua route tetap membutuhkan review visual 100%, metadata yang akurat, deklarasi generative AI, pemeriksaan hak, dan upload Adobe secara manual.

## Current PNG candidates

The furniture PNG trial is `household_furniture_small_space_png--rolling-kitchen-island-cart-cutout`. The new food PNG trial is `traditional_food_banh_mi_cutaway_png--banh-mi-cutaway`: one unbranded Vietnamese banh mi sandwich cutaway with a visible layered filling, intended for recipe cards, menu layouts, culinary tourism, packaging concepts, and social compositions. Mango sticky rice and Tom Yum Kung are excluded from the new trial because the user reports they were already used; mango sticky rice was rejected for Similar Content. Do not revive either candidate or create seed/color/crop variants. Each trial remains capped at one preview and requires human review.

## Canonical lifecycle

```text
candidate/brief
→ format decision: JPEG atau PNG
→ satu preview
→ PREVIEW_TO_MANUS
→ human KEEP / REJECT / REVIEW
→ matching finalizer preparation
→ explicit GPU confirmation
→ satu Kaggle job
→ COMPLETE + request/checksum matching
→ master import
→ technical audit
→ visual review 100%
→ metadata/package
→ READY_UPLOAD_ADOBE
→ manual Adobe upload
```

Tidak ada finalizer preparation atau GPU submission sebelum `KEEP`. Tidak ada upload export sebelum approval visual eksplisit.

## Format-specific commands

| Tahap | JPEG | PNG |
|---|---|---|
| Preview external import | `portfolio import-external --delivery-format jpeg` | `portfolio import-external --delivery-format png` |
| Finalizer preparation | `portfolio prepare-external-finalizer` | `portfolio prepare-external-finalizer` |
| GPU submission | `kaggle-finalizer submit` | `kaggle-png-finalizer submit` |
| Master import | `portfolio import-kaggle-master` | `portfolio import-kaggle-png-master` |
| Upload package | `portfolio prepare-adobe-upload` | `portfolio prepare-adobe-png-upload` |
| Android visual export | `portfolio export-ready-visual` | `portfolio export-ready-visual` |

Gunakan path, execution ID, artifact ID, request ID, dan result directory yang benar-benar dikeluarkan oleh Termux. Jangan mengarang nilai tersebut.

## Android output contract

```text
/storage/emulated/0/Download/MACHINE STOCKFORGE/
├── PREVIEW_TO_MANUS/       # satu preview visual untuk review
└── READY_UPLOAD_ADOBE/     # satu master JPEG/PNG yang telah disetujui
```

Folder visual Android tidak boleh berisi JSON, log, request, `result.json`, ZIP, WebP intermediate, staging image, model, database, checksum, atau laporan teknis.

## Safety gates

GPT/agent tidak boleh mengklaim command telah dijalankan tanpa output Termux. Status Kaggle `COMPLETE` saja tidak cukup; output wajib dicocokkan dengan request terbaru menggunakan request ID, source checksum, format, target dimensions, profile/color mode, provider, dan manifest.

Jangan melakukan blind retry, batch generation, automatic Adobe upload, automatic marketplace submission, force-push, reset, rebase, atau perubahan worker hanya karena sebuah dokumen menyebut “next step”. Jangan pernah mengekspos credential.

## History boundary

Riset niche tetap tersedia di `docs/research/` sebagai evidence dan tidak otomatis menjadi keputusan produksi. Dokumentasi eksperimen lama, SVG/vector, batch, local AI, provider trial, dan pretrial yang telah digantikan berada di `docs/archive/` dan **bukan instruksi aktif**.

Jika status atau command berubah, perbarui file ini, [`ACTIVE_SCOPE.md`](ACTIVE_SCOPE.md), dan [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md) dalam commit yang sama. Jangan membuat runbook operasional duplikat.
