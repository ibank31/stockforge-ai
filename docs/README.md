# StockForge Documentation

Dokumentasi aktif StockForge dipisahkan berdasarkan fungsi. **`STATUS.md` adalah snapshot status saat ini; `ARCHITECTURE.md` adalah desain sistem aktif; `FEATURE_ROADMAP.md` adalah daftar pekerjaan; `CHANGELOG.md` adalah sejarah.** Dokumen lain menjadi referensi teknis yang lebih spesifik dan tidak boleh diperlakukan sebagai status terbaru kecuali disebut oleh dokumen aktif.

## Mulai dari sini

| Kebutuhan | Dokumen |
|---|---|
| Memahami kondisi terbaru dan batasan proyek | [`STATUS.md`](STATUS.md) |
| Melanjutkan sesi berikutnya | [`SESSION_HANDOVER.md`](SESSION_HANDOVER.md) |
| Melihat rencana pematangan mesin | [`ENGINE_MATURATION_PLAN.md`](ENGINE_MATURATION_PLAN.md) |
| Memahami arsitektur dan alur asset factory | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Melihat pekerjaan selesai dan berikutnya | [`FEATURE_ROADMAP.md`](FEATURE_ROADMAP.md) |
| Membaca sejarah keputusan dan verifikasi | [`CHANGELOG.md`](CHANGELOG.md) |

## Produk dan format

- [`MULTIFORMAT_ENGINE_V1.md`](MULTIFORMAT_ENGINE_V1.md) — kontrak routing JPEG, native SVG, dan PNG alpha.
- [`FORMAT_AND_NICHE_DECISION_2026-08-24.md`](research/FORMAT_AND_NICHE_DECISION_2026-08-24.md) — keputusan niche/format berbasis evidence terbaru.
- [`ADOBE_MULTIFORMAT_EVIDENCE_2026-08-24.md`](ADOBE_MULTIFORMAT_EVIDENCE_2026-08-24.md) — bukti marketplace dan scope inferensi.
- [`MARKETPLACE_UPLOAD_READINESS_STANDARD.md`](MARKETPLACE_UPLOAD_READINESS_STANDARD.md) — standar teknis, policy, metadata, dan human review sebelum upload.
- [`ADOBE_STOCK_READINESS.md`](ADOBE_STOCK_READINESS.md) — gate kesiapan Adobe Stock.

## Operasi dan delivery

- [`TERMUX_CONTROL_PLANE.md`](TERMUX_CONTROL_PLANE.md) — workflow Android/Termux.
- [`PORTFOLIO_PRODUCTION_ENGINE.md`](PORTFOLIO_PRODUCTION_ENGINE.md) — perencanaan portfolio dan brief.
- [`PORTFOLIO_DELIVERY_PIPELINE.md`](PORTFOLIO_DELIVERY_PIPELINE.md) — review package dan delivery.
- `portfolio metadata-preflight --project ... --plan ... --brief ...` — laporan metadata JPEG lintas platform; hanya validasi dan reorder keyword existing, tanpa provider call, upload, atau submit.
- [`GPU_QUOTA_RUNBOOK.md`](GPU_QUOTA_RUNBOOK.md) — aturan penggunaan quota.
- [`GPU_WASTE_PREVENTION_2026-08-24.md`](GPU_WASTE_PREVENTION_2026-08-24.md) — pre-GPU guard.
- [`FINALIZER_AND_INFRASTRUCTURE_ROADMAP.md`](FINALIZER_AND_INFRASTRUCTURE_ROADMAP.md) — finalizer dan infrastructure follow-up.

## Engineering contracts

- [`CORE_CONTRACTS.md`](CORE_CONTRACTS.md)
- [`ASSET_REGISTRY.md`](ASSET_REGISTRY.md)
- [`JOB_QUEUE.md`](JOB_QUEUE.md)
- [`PIPELINE_CONTRACT.md`](PIPELINE_CONTRACT.md)
- [`PLUGIN_CONTRACT.md`](PLUGIN_CONTRACT.md)
- [`MODEL_PROVIDER_ARCHITECTURE.md`](MODEL_PROVIDER_ARCHITECTURE.md)
- [`provider-backends.md`](provider-backends.md)
- [`PROVIDER_SECURITY.md`](PROVIDER_SECURITY.md)
- [`IMAGE_QA_PREFLIGHT.md`](IMAGE_QA_PREFLIGHT.md)
- [`VISION_QA.md`](VISION_QA.md)
- [`VISION_ENSEMBLE.md`](VISION_ENSEMBLE.md)

## Intelligence and research

- [`MARKET_INTELLIGENCE.md`](MARKET_INTELLIGENCE.md)
- [`JPEG_NICHE_KNOWLEDGE_AUDIT_2026-08-25.md`](research/JPEG_NICHE_KNOWLEDGE_AUDIT_2026-08-25.md) — audit kedalaman knowledge, overlap framing, dan identity framework sembilan niche JPEG.
- [`ADOBE_STOCK_BEST_SELLER_SCREENSHOT_ANALYSIS_2026-08-25.md`](research/ADOBE_STOCK_BEST_SELLER_SCREENSHOT_ANALYSIS_2026-08-25.md) — klasifikasi sepuluh screenshot, cross-check Adobe/marketplace, product families, dan batas anecdotal earnings evidence.
- [`LEGACY_BEST_SELLER_EVIDENCE_RECOVERY_2026-08-25.md`](research/LEGACY_BEST_SELLER_EVIDENCE_RECOVERY_2026-08-25.md) — recovery 31 catatan screenshot lama dari handover Git, fakta versus inference, dan provenance limitations.
- [`FIRST_SALE_JPEG_NICHE_SHORTLIST_2026-08-25.md`](research/FIRST_SALE_JPEG_NICHE_SHORTLIST_2026-08-25.md) — shortlist niche JPEG low-cost dengan evidence hierarchy dan rekomendasi hypothesis pertama.
- [`BUYER_SEGMENTS.md`](BUYER_SEGMENTS.md)
- [`BUYER_MARKET_MATRIX.md`](BUYER_MARKET_MATRIX.md)
- [`CONCEPT_ENGINE_V4.md`](CONCEPT_ENGINE_V4.md)
- [`PROMPT_COMPILER.md`](PROMPT_COMPILER.md)
- [`PRODUCTION_INTELLIGENCE_V2.md`](PRODUCTION_INTELLIGENCE_V2.md)
- [`VISION_PROVIDER_BENCHMARK.md`](VISION_PROVIDER_BENCHMARK.md)
- [`PORTFOLIO_STANDALONE_RESEARCH_2026.md`](PORTFOLIO_STANDALONE_RESEARCH_2026.md)
- [`FREE_MODEL_PROVIDER_STRATEGY_2026-08-24.md`](FREE_MODEL_PROVIDER_STRATEGY_2026-08-24.md)
- [`SVG_MARKET_RESEARCH_2026-08-24.md`](research/SVG_MARKET_RESEARCH_2026-08-24.md) — deep research SVG market, buyer jobs, competition proxies, trends, and first folder-upload hypothesis.
- [`svg_market_2026-08-24.md`](research/svg_market_2026-08-24.md) — raw source notes and caveats for the SVG research.
- [`FOLDER_UPLOAD_PRETRIAL_SPEC_2026-08-24.md`](research/FOLDER_UPLOAD_PRETRIAL_SPEC_2026-08-24.md) — approved single-object hypothesis, metadata boundary, deterministic gates, and human review questions before the next SVG trial.
- [`svg_global_discoverability_notes_2026-08-24.md`](research/svg_global_discoverability_notes_2026-08-24.md) — global platform metadata/discoverability evidence and anti-spam constraints.
- [`SVG_VALUE_AND_MARKET_ALGORITHM_PLAN_2026-08-24.md`](research/SVG_VALUE_AND_MARKET_ALGORITHM_PLAN_2026-08-24.md) — micro-set value hypothesis, buyer test, platform projections, and safe learning loop.

## Riset terarsip tetapi masih menjadi bukti

Direktori [`research/`](research/) berisi catatan sumber dan audit. Dokumen riset tidak otomatis menjadi keputusan produksi; keputusan aktif harus diringkas di `STATUS.md` atau `FORMAT_AND_NICHE_DECISION_2026-08-24.md`.

## Output dan evaluasi

- `Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/` — satu visual untuk review manusia setelah generation masa depan.
- `Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/` — satu salinan JPEG yang sudah disetujui dan diberi XMP title/keywords bila formatnya mendukung.
- `evaluations/generation_evaluations.jsonl` — ledger append-only untuk skor, keputusan, rejection reason, format, provider, model, dan buyer job.

Perintah `portfolio evaluate` hanya mencatat review; perintah `portfolio evaluation-summary` hanya merangkum data yang sudah direview. Keduanya tidak menjalankan GPU, upload, submit, atau perubahan prompt otomatis.

## Aturan pemeliharaan

Setiap perubahan status harus memperbarui `STATUS.md` dan menambahkan entry ke `CHANGELOG.md`. Dokumen dengan tanggal lama boleh tetap dipertahankan bila merupakan bukti yang tidak tergantikan; dokumen yang hanya mengulang status atau handoff harus dihapus atau digabungkan, bukan dibuatkan salinan baru.
