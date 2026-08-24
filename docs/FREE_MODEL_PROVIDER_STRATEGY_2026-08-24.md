# Strategi Model dan Provider Gratis StockForge

**Status:** Kebijakan produksi aktif.  
**Tujuan:** Memaksimalkan kualitas dan produktivitas aset tanpa kartu, trial berbayar, atau provider yang belum tervalidasi untuk workflow StockForge.

## Keputusan utama

> **Z-Image Turbo pada Space ZeroGPU StockForge tetap menjadi satu-satunya model preview produksi aktif.** Ia sudah terbukti end-to-end pada workflow Termux dan memiliki jalur gratis yang sedang digunakan. Kandidat lain dicatat, tetapi tidak dapat dirutekan otomatis sebelum akses, worker, lisensi, dan benchmarknya benar-benar selesai.

Keputusan ini sengaja konservatif. Menambah daftar model tanpa worker yang kompatibel justru menciptakan tombol yang terlihat siap, lalu menghabiskan kuota GPU pada model yang belum teruji. StockForge akan mengutamakan satu model yang terukur, prompt yang tepat, komposisi yang tidak tertimpa wrapper, dan seleksi pasca-generate yang ketat.

## Matriks keputusan

| Model / provider | Status dalam StockForge | Jalur gratis / akses | Keputusan | Alasan operasional |
|---|---|---|---|---|
| **Z-Image Turbo + Hugging Face ZeroGPU** | **Aktif dan terverifikasi** | Endpoint StockForge yang sudah berjalan; kuota ZeroGPU harian | **Default preview** | Model berlisensi Apache-2.0, dirancang untuk sekitar delapan evaluasi/steps, dan worker Termux–Gradio sudah terbukti. [1] [2] |
| **Kaggle + worker Z-Image** | Worker tersedia, endpoint bukan layanan permanen | GPU Notebook gratis bersifat antrean dan sesi | **Fallback / benchmark terkontrol** | Kaggle mendokumentasikan satu P100 gratis, tetapi worker perlu dijalankan dan dibagikan untuk tiap sesi. Bukan default interactive preview. [3] |
| **Qwen-Image** | Katalog kondisional; tidak aktif | Memerlukan worker kompatibel dan benchmark disk/VRAM | **Tidak dirutekan** | Lisensi Apache-2.0, tetapi kartu model resmi menunjukkan ukuran 20B dan contoh 50 steps; itu tidak cocok menjadi default kuota kecil. [4] |
| **FLUX.1 Schnell** | Katalog kondisional; tidak aktif | Memerlukan acceptance akses dan worker sendiri | **Tidak dirutekan** | Model Apache-2.0 dan cepat (1–4 steps), tetapi akses bobot meminta pemegang akun menerima syarat serta membagikan kontak. Tidak diaktifkan otomatis. [5] |
| **Cloudflare Workers AI** | Tidak dikonfigurasi | Membutuhkan akun dan token API sendiri | **Dikecualikan saat ini** | Dokumentasi menyebut alokasi gratis harian, namun ini bukan provider yang telah diuji, membutuhkan kredensial eksternal, dan kebijakan pendaftarannya belum dibuktikan bebas-kartu untuk akun pengguna. [6] |
| API/website “unlimited free” tidak resmi | Tidak dipakai | Tidak dapat diaudit | **Ditolak** | Tidak ada jaminan lisensi komersial, stabilitas, privasi prompt, atau kuota; berisiko bagi pipeline aset stok. |

## Perbaikan yang diimplementasikan

| Perbaikan | Dampak kualitas / produktivitas |
|---|---|
| Katalog model dengan status `verified_free`, `conditional`, atau `research_only` | Model yang belum memiliki worker, akses, atau benchmark tidak dapat dipanggil secara tidak sengaja. |
| Perintah `provider models --json` | Status, lisensi, kebutuhan aktivasi, dan batasan setiap kandidat dapat dilihat tanpa GPU atau token. |
| Routing normal hanya menerima `verified_free` | `qwen-image` ditolak lokal sebelum provider dipilih; tidak ada pemborosan kuota akibat profile teoritis. |
| Portfolio prompt tidak lagi dibungkus policy “centered object” umum | Kontrak komposisi kiri/kanan dari compiler tetap sampai ke worker ZeroGPU. Ini memperbaiki penyebab struktural hasil yang salah layout. |
| Pemilihan kanvas portfolio otomatis | Brief dengan copy space kiri/kanan memilih `hero-landscape`; brief lain tetap `square` agar pixel budget dan waktu tetap hemat. |

## Aturan penggunaan model

1. Satu **Z-Image Turbo** preview hanya boleh menguji satu brief baru yang telah lolos preflight CPU. Tidak ada retry seed untuk masalah konsep, siluet, hubungan spasial, atau komposisi.
2. **Kaggle** hanya menyelesaikan master/upscale dari preview yang telah dipilih; bukan mesin variasi atau endpoint background.
3. **Qwen-Image** hanya boleh naik menjadi kandidat benchmark setelah ada worker terpisah yang membuktikan model dapat memuat, menyelesaikan satu job, menghasilkan output yang layak, dan tidak melampaui batas storage/quota.
4. **FLUX.1 Schnell** tidak boleh diaktifkan sampai pemilik akun sendiri menyetujui kondisi akses model dan worker khusus berhasil dibenchmark. Kondisi akses tidak boleh diterima secara otomatis.
5. Tidak ada provider baru yang ditambahkan bila membutuhkan kartu, kredit berbayar, trial dengan tagihan otomatis, atau secret yang belum diberikan pemilik akun.

## Eksperimen model berikutnya bila diizinkan

Benchmark bukan tindakan produksi. Benchmark hanya boleh dilakukan setelah persetujuan pengguna dan memakai **satu brief netral yang sama**, satu seed, satu kanvas, serta audit yang sama untuk semua model. Ukur: GPU seconds, keberhasilan job, kepatuhan subjek, copy space, artefak, kemiripan, dan kelayakan komersial. Jangan memakai aset benchmark untuk Adobe.

## Referensi

[1]: https://huggingface.co/Tongyi-MAI/Z-Image-Turbo "Tongyi-MAI/Z-Image-Turbo model card"
[2]: https://huggingface.co/docs/hub/en/spaces-zerogpu "Hugging Face Spaces ZeroGPU documentation"
[3]: https://www.kaggle.com/docs/notebooks "Kaggle Notebooks documentation"
[4]: https://huggingface.co/Qwen/Qwen-Image "Qwen/Qwen-Image model card"
[5]: https://huggingface.co/black-forest-labs/FLUX.1-schnell "FLUX.1 Schnell model card"
[6]: https://developers.cloudflare.com/workers-ai/platform/pricing/ "Cloudflare Workers AI pricing"
