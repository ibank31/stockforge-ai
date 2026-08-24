# Finalizer dan Infrastruktur StockForge

Dokumen ini menjelaskan jalur dari preview rendah resolusi menuju master kandidat yang dapat diperiksa untuk marketplace. Status utama mesin tetap **`review_ready`**; tidak ada command di bawah ini yang menjamin penerimaan, hak penggunaan, performa penjualan, atau otomatis mengunggah ke marketplace.

## Status implementasi saat ini

| Komponen | Status | Batas penting |
|---|---|---|
| Preview generation dari Termux | Aktif | Preview 1024×1024 digunakan untuk menilai brief dan kualitas awal; bukan file upload. |
| Master finalizer domain | Aktif di core | Menerima hasil AI upscale provider, memverifikasi dimensi, lalu mengekspor JPEG RGB/sRGB dan menjalankan gate teknis. |
| Lineage preview → master | Aktif di core | Master dicatat sebagai artefak `finalized-master` dengan relasi `upscaled`, provenance, serta execution terpisah. |
| Paket master | Aktif di core | Paket final dapat memuat `masters/*.jpg`, `MASTER_FINALIZATION.json`, laporan teknis, metadata draft, dan checklist review. |
| `portfolio prepare-master` | Aktif | Membuat request master yang terikat pada execution dan source SHA-256. **Tidak memanggil GPU.** |
| Provider GPU AI upscale otomatis | Aktif sebagai jalur Kaggle experimental | `kaggle-finalizer submit` menjalankan tepat satu request 4× private; output masih wajib diimpor dan direview. |
| Kaggle finalizer worker | Aktif untuk benchmark satu-per-satu | Kaggle adalah worker batch privat, bukan endpoint permanen; validasi kualitas nyata tetap diperlukan sebelum batch. |
| Cloudflare R2 / queue | Opsional, belum dikonfigurasi | Memerlukan akun dan kredensial pengguna. Cloudflare bukan AI upscaler master. |
| Provider burst berbayar | Opsional, belum diaktifkan | Hanya setelah benchmark dan persetujuan budget eksplisit. |

## Alur yang diwajibkan

```text
preview_generated
  → visual selection
  → prepare-master (tanpa GPU)
  → actual AI upscale / native master pada worker GPU
  → JPEG RGB/sRGB technical gate
  → visual_review_required
  → review_ready package
  → human sign-off per marketplace
  → submission_ready_<marketplace>
  → upload manual
```

Master finalizer tidak melakukan `Pillow.resize` untuk mengklaim peningkatan kualitas. Ia meminta provider visual/AI yang dilaporkan eksplisit, lalu menyimpan model, scale, output intermediate, dan transform ke lineage. Upscale tetap dapat membuat artefak atau mengubah detail; reviewer wajib membandingkan master dengan preview pada ukuran 100%.

## Menyiapkan request master dari Termux

Setelah memilih satu preview yang valid, buat request terikat-lineage berikut. Ini aman dan tidak memakai GPU:

```bash
python -m stockforge.cli portfolio prepare-master \
  --project stock-assets \
  --execution '<EXECUTION_ID_PREVIEW>' \
  --artifact '<ARTIFACT_ID_PREVIEW>' \
  --minimum-megapixels 6 \
  --scale 4
```

Output adalah file pada `master-finalizer-requests/`. Ia menyimpan ID artefak, SHA-256 preview, ukuran sumber, target 6 MP, output JPEG/sRGB yang diharapkan, konteks portfolio, serta syarat review manusia. Request ini harus menjadi satu-satunya input yang boleh diterima oleh worker finalizer, sehingga worker tidak dapat menjalankan file/proyek yang berbeda secara tidak sengaja.

## Compute dan delivery: prinsip pemilihan

| Jalur | Tugas | Mengapa | Jangan digunakan untuk |
|---|---|---|---|
| Hugging Face ZeroGPU Space | Satu preview interaktif | Worker sudah ada dan dapat dikontrol Termux. | Batch besar atau jaminan throughput. |
| Kaggle GPU | Finalizer batch kecil/fallback | Kuota GPU mingguan dan job berbasis output cocok untuk pekerjaan terpilih. | Endpoint API permanen. |
| Cloudflare R2 + Queue | Penyimpanan ZIP/master, retry, job-state saat skala meningkat. | Control/data plane terpisah dari provider GPU. | Menjadi model upscale AI atau GPU custom gratis. |
| Burst provider berbayar | Master GPU sesekali ketika kuota gratis habis. | Tidak memerlukan GPU selalu aktif. | Diaktifkan tanpa benchmark, cap biaya, dan persetujuan pengguna. |

## Pekerjaan berikutnya

1. Benchmark satu aset 1024×1024 → master 4096×4096 melalui `kaggle-finalizer` dan periksa hasil pada ukuran 100% sebelum membuka batch lebih besar.
2. Tambahkan deduplikasi/visual-review record sebelum status marketplace-specific dapat dipromosikan.
3. Tambahkan bounded retry/error import untuk Kaggle, berdasarkan hasil benchmark nyata dan tanpa menyembunyikan log provider.
4. Setelah volume membenarkan, aktifkan R2/Queue atau satu provider burst dengan secret dan budget cap di sisi server.

Referensi keputusan dan bukti resmi tersedia pada dokumen riset infrastruktur dan standar marketplace yang menyertai proyek.
