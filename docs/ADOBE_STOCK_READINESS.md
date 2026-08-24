# Marketplace Readiness: Standalone Asset Gate

**Status:** Engineering policy; bukan jaminan penerimaan marketplace

StockForge memperlakukan generation sebagai artefak intermediate. Aset baru boleh berstatus `submission_ready` hanya setelah seluruh gate teknis, visual, hak, metadata, deduplikasi, dan review manusia dipenuhi. Aturan marketplace dapat berubah; verifikasi aturan terbaru selalu wajib sebelum submission.

## Standalone-first gate

| Gate | Wajib | Kriteria awal |
|---|---|---|
| Subject clarity | Ya | satu subject inti, lengkap, terbaca pada thumbnail |
| Isolation | Ya | latar putih/transparent yang bersih, pinggir dapat diekstrak |
| Contamination | Ya | tidak ada manusia, tangan, alat, perangkat, layar, angka, text, frame, stamp, postmark, atau prop tambahan kecuali menjadi subject yang disetujui |
| Rights/IP | Ya | tidak ada logo, trademark, watermark, karakter berhak cipta, atau kemiripan selebritas |
| Geometry/material | Ya | objek utuh, tidak meleleh/terduplikasi, material meyakinkan |
| Technical integrity | Ya | file dapat dibaca, ukuran/format/profile sesuai policy saat submission |
| Duplicate control | Ya | hanya best-of-cluster yang dapat lanjut |
| Provenance | Ya | model, provider, prompt, seed, waktu, hash, dan policy record tersimpan |
| Human review | Ya | status `review_ready` belum berarti accepted atau submitted |

## Rejected first generation lesson

Generation pertama yang dibuat dengan prompt botanical menghasilkan beberapa subject: botanical art, frame/perangko, tangan, perangkat meter, dan angka. Ia adalah generation sukses, tetapi **gagal** sebagai baseline aset standalone karena melanggar single-subject, no-text/no-number, dan no-unrelated-props. Asset tersebut tetap `review_ready` dan tidak boleh dipakai sebagai benchmark portofolio.

## Technical pipeline

```text
Generation
  → standalone quality gate
  → technical/image integrity QA
  → OCR/logo/watermark and IP review
  → upscaling/finalization if required
  → technical re-QA
  → similarity cluster selection
  → metadata and AI disclosure
  → human review
  → submission package
```

## Metadata rule

Metadata harus menggambarkan apa yang benar-benar terlihat. Jangan memakai keyword stuffing, nama brand/artis, klaim lokasi/budaya yang tidak didukung, atau deskripsi subject yang tidak ada dalam gambar. Title, keywords, disclosure AI, state people/property, release state, dan provenance harus berasal dari record aset yang dapat diaudit.

## Portfolio rule

Aset yang lolos secara teknis belum tentu layak diproduksi lagi. Portfolio gate memeriksa utility buyer, uniqueness, copy-space, evidence confidence, serta keseimbangan lane. Variasi seed, crop, atau warna saja tidak cukup sebagai variasi komersial.
