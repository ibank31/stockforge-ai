# Runbook Kuota GPU StockForge

## Tujuan dan Status

Dokumen ini mengatur penggunaan GPU yang terbatas secara **produktif dan dapat diaudit**. Tujuannya bukan menghabiskan kuota dengan sebanyak mungkin gambar, melainkan menghasilkan kandidat master yang lebih baik atau bukti yang jelas untuk memperbaiki proses berikutnya.

> **Status 2026-08-24:** benchmark Kaggle pertama telah lulus secara teknis. Preview `3f12b829-0432-4720-83b5-38d358f996bc` berhasil diproses oleh `RealESRGAN_x4plus` menjadi JPEG sRGB 4096 × 4096 (16,78 MP). Benchmark membuktikan jalur runtime, manifest, checksum, dan impor master. Aset sumbernya tetap terlalu generik untuk direkomendasikan sebagai kandidat upload.

## Pembagian Peran Compute

| Compute | Peran utama | Kapan dipakai | Tidak digunakan untuk |
|---|---|---|---|
| ZeroGPU | Menguji satu konsep/brief preview 1024 px | Saat buyer hypothesis atau komposisi masih belum terbukti | Membuat master upload atau membuat variasi seed tanpa alasan |
| Kaggle GPU | Membuat master 4× dari preview yang telah dipilih; benchmark kualitas yang dibatasi | Saat preview punya konsep jelas, visual bersih, dan metadata dapat dipertanggungjawabkan | Meng-upscale seluruh preview, retry buta, atau menjadi endpoint permanen |
| CPU Termux | Planning, metadata, gate teknis, ZIP, dan inspeksi | Sebelum dan sesudah setiap job GPU | Inference model besar atau dependensi RealESRGAN lokal |

## Aturan Wajib Sebelum Job GPU

Setiap job harus memiliki satu `job_id` atau `request_id`, **hipotesis**, dan hasil yang diharapkan. Job dapat dijalankan hanya bila memenuhi salah satu kondisi di bawah.

| Tipe job | Syarat masuk | Bukti sukses | Keputusan sesudahnya |
|---|---|---|---|
| Preview konsep baru | Buyer use case dan diferensiasi tertulis | Konsep dapat dinilai secara visual | Pilih, revisi brief, atau tolak; jangan generate seed lain tanpa hipotesis baru |
| Master terpilih | Preview lolos inspeksi visual, IP, metadata, dan deduplikasi awal | JPEG sRGB ≥6 MP dengan lineage valid | Audit 100%, lalu `review_ready` atau tolak |
| Eksperimen kualitas | Satu cacat spesifik dan satu perubahan yang diuji | Perbandingan sebelum/sesudah yang dapat direkam | Pertahankan perubahan atau hentikan jalur |
| Diagnostik provider | Error baru terisolasi dan perbaikan telah diuji tanpa GPU | Log baru mengonfirmasi/menolak hipotesis | Satu retry saja; eskalasi atau stop bila tidak terisolasi |

Job **tidak boleh** dijalankan karena alasan berikut: kuota terlihat masih tersedia, ingin memperbanyak output, variasi seed/crop/warna tanpa buyer hypothesis baru, atau preview yang sudah memiliki pseudo-teks, anatomi/objek rusak, IP/brand, komposisi generik, atau metadata yang tidak cocok.

## Alokasi Kuota Adaptif

Alokasi dihitung dari durasi GPU aktual yang dicatat pada ledger, bukan dari asumsi durasi. Sampai data beberapa job tersedia, gunakan sasaran berikut untuk setiap blok **10 jam GPU Kaggle** yang tersedia.

| Porsi indikatif | Penggunaan | Stop rule |
|---:|---|---|
| 50% | Master dari preview terpilih | Hentikan bila master tidak menambah nilai visual dibanding preview atau preview tidak lolos review |
| 30% | Eksperimen kualitas dengan satu variabel | Hentikan setelah satu hasil tidak mendukung hipotesis; jangan lanjut varian acak |
| 20% | Cadangan untuk diagnosis atau konsep prioritas baru | Dipakai hanya dengan error baru yang terisolasi atau brief bernilai tinggi yang disetujui review |

Rasio ini bukan kewajiban untuk menghabiskan kuota. Bila tidak ada kandidat lolos, kuota disimpan. Bila master yang terpilih berkualitas konsisten dan durasinya rendah, porsi master dapat dinaikkan setelah ledger menunjukkan nilai tambah yang nyata.

## Ledger Wajib Per Job

Simpan satu baris ledger untuk setiap request GPU dan isi hasilnya segera setelah job selesai. Nilai yang tidak tersedia ditulis `DATA NOT PUBLICLY AVAILABLE`, bukan ditebak.

| Field | Contoh | Aturan |
|---|---|---|
| Tanggal UTC | `2026-08-24` | Tanggal job dipush |
| Provider | `kaggle-realesrgan` | Provider/model sebenarnya |
| Request / execution / artifact | `master-…` | ID yang mengikat lineage |
| Tipe job | `master` / `quality_experiment` / `diagnostic` | Pilih satu |
| Hipotesis | `4× master mempertahankan tepi token tanpa pseudo-teks` | Harus dapat diuji |
| Sumber / brief | `ai_governance--review-gate` | Wajib untuk generator preview |
| Alasan seleksi | `preview lolos clean-background dan metadata draft` | Tidak boleh kosong |
| Perubahan tunggal | `RealESRGAN x4plus` | Untuk eksperimen/diagnosis |
| Durasi GPU aktual | `DATA NOT PUBLICLY AVAILABLE` | Catat bila Kaggle menampilkan data |
| Bukti output | manifest, ukuran, log, path paket | Harus dapat diperiksa |
| Hasil visual | `pass`, `revise`, atau `reject` | Berdasarkan pemeriksaan 100% |
| Keputusan | `import review-ready` atau `stop` | Tidak pernah otomatis upload |
| Alasan keputusan | kalimat ringkas | Wajib untuk job ditolak |

## Prosedur Produksi Terkendali

Mulai dari `portfolio plan`, pilih satu brief yang memiliki buyer job jelas, dan buat **satu** preview melalui ZeroGPU. Audit preview sebelum `prepare-master`. Hanya preview yang bersih, berbeda, dan layak metadata yang boleh mendapatkan request Kaggle.

Sebelum `kaggle-finalizer submit`, jalankan `kaggle-finalizer doctor` dan `kaggle-finalizer test`. Setelah submit, ambil output sekali setelah job selesai; periksa `result.json`, checksum, master JPEG, dan crop 100%. Setelah `portfolio import-kaggle-master`, buka ZIP pada Android dan isi checklist review sebelum mempertimbangkan marketplace.

Jika job gagal, catat log dan klasifikasikan sebagai input, staging, dependensi, bobot, GPU/VRAM, encoding, atau kualitas. Perbaiki hanya jika penyebabnya tunggal dan dapat diuji tanpa GPU. Jalankan maksimal **satu retry** untuk hipotesis yang telah diperbaiki. Jika kegagalan berikutnya lebih mendasar atau kualitas tidak memberikan nilai tambah, hentikan jalur tersebut dan evaluasi metode finalisasi lain—bukan melakukan retry berulang.

## Status Marketplace

`review_ready` menunjukkan sumber, lineage, format, dan paket telah tersedia untuk **review manusia**. Status tersebut bukan `submission_ready`. Reviewer tetap harus memeriksa: detail hasil upscale, pseudo-teks, logo/brand/IP, kesesuaian metadata, unik/tidak duplikat, risiko hak, dan deklarasi GenAI marketplace.
