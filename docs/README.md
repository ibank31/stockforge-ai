# StockForge Documentation

## Mulai di sini

Untuk operasi apa pun, GPT/agent wajib membaca **[`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md)** terlebih dahulu. Dokumen tersebut adalah satu-satunya panduan operasional aktif dan mencakup dua flow produksi resmi: **JPEG** dan **PNG**.

Setelah itu, baca **[`STATUS.md`](STATUS.md)** hanya untuk snapshot kondisi repository. Jangan mengambil instruksi operasional dari dokumen historis, changelog, riset, atau arsip.

## Sumber kebenaran

| Kebutuhan | Sumber |
|---|---|
| Workflow GPT → Termux → Kaggle → Android | [`GPT_TO_TERMUX_CANONICAL_WORKFLOW.md`](GPT_TO_TERMUX_CANONICAL_WORKFLOW.md) |
| Status route dan batasan aktif | [`STATUS.md`](STATUS.md) |
| Perubahan repository | [`CHANGELOG.md`](CHANGELOG.md) |
| Riset niche dan market evidence | [`research/`](research/) sebagai referensi saja |
| Kontrak kode terperinci | Source code dan test terkait; bukan pengganti workflow canonical |

## Dua route produksi

| Route | Untuk | Worker finalizer | Output |
|---|---|---|---|
| JPEG | Scene, environment, hero composition, ilustrasi berlatar, dan visual dengan copy space | Protected Kaggle RealESRGAN | Master JPEG RGB/sRGB |
| PNG | Isolated object, cutout, sticker, overlay, dan utility asset transparan | Isolated Kaggle BiRefNet | Master PNG RGBA/true-alpha/sRGB |

SVG/vector, batch generation, local AI, llama.cpp/Qwen, dan jalur eksperimen lama **bukan bagian dari produksi aktif**.

## Kontrak folder Android

```text
Download/MACHINE STOCKFORGE/
├── PREVIEW_TO_MANUS/       # hanya preview visual
└── READY_UPLOAD_ADOBE/     # hanya master JPEG/PNG yang telah disetujui
```

JSON, log, request, `result.json`, ZIP, WebP intermediate, staging image, database, model, checksum, dan artefak teknis harus tetap berada di workspace proyek.

## Aturan pemeliharaan

Jika ada perubahan pada flow JPEG atau PNG, perbarui `GPT_TO_TERMUX_CANONICAL_WORKFLOW.md` dan `STATUS.md` dalam commit yang sama. Jangan membuat runbook operasional baru yang menduplikasi dokumen canonical. Dokumen lama boleh dipertahankan hanya sebagai bukti sejarah di `archive/`; dokumen tersebut tidak boleh digunakan sebagai instruksi.
