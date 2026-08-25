# StockForge AI

StockForge AI adalah asset factory berbasis **Android/Termux** yang mengubah market evidence dan buyer job menjadi asset package yang dapat diproduksi, diperiksa, dan disiapkan untuk marketplace dengan provenance yang jelas.

## Status saat ini

Branch aktif adalah `main`. Jalur yang sudah terbukti adalah JPEG raster melalui remote worker dan native SVG deterministic secara lokal; JPEG sekarang menjadi track pematangan aktif. SVG value-upgrade dibekukan sebagai roadmap, sedangkan PNG transparan masih diblokir sampai true alpha producer, edge-quality gate, dan validasi portal tersedia. Lihat [`docs/STATUS.md`](docs/STATUS.md) untuk snapshot terbaru.

## Quick start

```bash
uv sync
uv run stockforge version
uv run stockforge doctor
uv run stockforge init
uv run stockforge project create demo
uv run stockforge project list
```

Untuk Android, Termux menjadi control plane. Heavy model inference berjalan di provider remote; dependency GPU tidak dipasang di perangkat.

## Alur utama

```text
market evidence → buyer job → AssetSpec → concept/prompt
→ pre-GPU gate → provider/local route → generation/build
→ QA → deduplication → metadata/compliance → human review
```

Sistem tidak menganggap generation success sebagai marketplace acceptance. Sebelum upload JPEG, gunakan `portfolio metadata-preflight --project ... --plan ... --brief ...` untuk laporan lintas platform; perintah ini hanya memvalidasi dan mengurutkan keyword yang sudah ada, tanpa provider call, upload, atau submit. Upload, disclosure, release decision, CAPTCHA, dan final submit tetap memerlukan tindakan manusia.

## Dokumentasi

Mulai dari [`docs/README.md`](docs/README.md), lalu gunakan [`docs/STATUS.md`](docs/STATUS.md) untuk kondisi terbaru dan [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) untuk desain aktif. Daftar feature dan pekerjaan berikutnya ada di [`docs/FEATURE_ROADMAP.md`](docs/FEATURE_ROADMAP.md); keputusan niche/format terbaru ada di [`docs/research/FORMAT_AND_NICHE_DECISION_2026-08-24.md`](docs/research/FORMAT_AND_NICHE_DECISION_2026-08-24.md). Audit kedalaman knowledge dan visual identity JPEG ada di [`docs/research/JPEG_NICHE_KNOWLEDGE_AUDIT_2026-08-25.md`](docs/research/JPEG_NICHE_KNOWLEDGE_AUDIT_2026-08-25.md). Analisis sepuluh screenshot Adobe Stock dan hasil riset product family ada di [`docs/research/ADOBE_STOCK_BEST_SELLER_SCREENSHOT_ANALYSIS_2026-08-25.md`](docs/research/ADOBE_STOCK_BEST_SELLER_SCREENSHOT_ANALYSIS_2026-08-25.md).

## Quality rule

Setiap perubahan harus diuji. Setiap market claim harus memiliki source dan confidence. Setiap format harus dipilih karena buyer job, bukan karena file extension. Jangan menjalankan GPU, upload, atau submission tanpa hypothesis dan human review yang jelas.
