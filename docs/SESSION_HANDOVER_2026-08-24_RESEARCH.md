# StockForge AI — Handoff Riset Screenshot dan Format

**Tanggal:** 24 Agustus 2026  
**Bahasa kerja:** Bahasa Indonesia  
**Tujuan sesi berikutnya:** melanjutkan riset niche dan format produk StockForge berdasarkan bukti marketplace, tanpa membuang kuota GPU.

## 1. Permintaan pengguna saat ini

Pengguna meminta sesi dihentikan dan dibuatkan handoff agar dapat pindah sesi. Jangan melanjutkan ekstraksi atau riset sekarang. Handoff ini harus menjadi sumber konteks utama pada sesi berikutnya.

Pengguna ingin StockForge menjadi mesin aset Adobe Stock multi-format dan hemat GPU. Pemilihan JPEG, PNG transparan, atau SVG harus didasarkan pada pekerjaan pembeli dan bukti marketplace, bukan mengekspor semua format secara mekanis.

Pengguna meminta semua perintah Termux diberikan dalam satu blok multiline siap copy-paste, tanpa placeholder, variabel yang harus dirakit manual, atau langkah teknis yang sulit. Jangan meminta pengguna mengerjakan prosedur rumit bila dapat dibuatkan perintah siap tempel.

## 2. Status engineering yang sudah terbukti

Repo GitHub: `ibank31/stockforge-ai`  
Branch: `feat/asset-factory-architecture`  
Commit terakhir yang diketahui: `ad55ca8` — guarded multi-format asset engine.

Perubahan penting yang sudah dipush:

| Commit | Isi |
|---|---|
| `4e81b2b` | Gate pra-GPU untuk memblokir siluet perangkat nyata, relasi spasial ambigu, metadata fallback, dan copy-space lemah. |
| `276c68f` | Production intelligence. |
| `2ad57ea` | Model routing dan layout. |
| `ad55ca8` | Guarded multi-format engine. |

Tes lokal setelah perubahan multi-format: **245 passed, 1 skipped**.

Kontrak format saat ini:

| Product kind | Format | Status |
|---|---|---|
| `raster_illustration` | JPEG | Jalur produksi raster terverifikasi dengan ZeroGPU Z-Image Turbo. |
| `transparent_cutout` | PNG | Router sengaja memblokir sebelum producer alpha nyata tersedia. Gate menolak PNG opaque atau latar putih palsu. |
| `native_vector` | SVG | Builder SVG native lokal sudah dapat membuat path editable dan menyimpan provenance tanpa GPU. Portal Adobe belum diuji end-to-end untuk jalur SVG ini. |

ZeroGPU dengan Z-Image Turbo 8 steps adalah satu-satunya generator preview production yang aktif. Qwen-Image dan FLUX.1 Schnell hanya katalog kondisional; jangan dirutekan otomatis. Jangan melakukan generation, retry acak, batch besar, Kaggle, XMP, upload Adobe, atau perubahan portal dalam sesi handoff ini.

Workflow yang telah terbukti: JPEG dapat diberi XMP title/keywords, lalu Adobe membaca metadata tersebut pada upload-copy. Asset `fiber-arch` berada di Adobe pada status **In review**, File ID **2168151996**. Jangan submit ulang, mengubah, atau menyentuh portal Adobe tanpa konfirmasi eksplisit pengguna.

`cassette-cloud` telah ditolak secara visual dan menjadi pelajaran untuk gate pra-GPU. `woven-loop` dinilai visualnya baik, tetapi harus direklasifikasi sebagai elemen craft/collage square dengan kemungkinan PNG transparan, bukan hero landscape. Jangan membuat master `woven-loop` sebelum producer alpha nyata tervalidasi.

Folder Android yang disetujui pengguna hanya:

- `Downloads/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/` untuk image preview.
- `Downloads/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/` untuk file final siap upload.

Folder user-facing hanya berisi file visual. Jangan menyalin ZIP, JSON, CSV, log, atau technical files ke folder tersebut. Jangan membersihkan folder lama tanpa daftar dan persetujuan eksplisit.

## 3. Lokasi bukti dan aturan pembacaan

Raw screenshot tersimpan di:

`/home/ubuntu/stockforge-evidence-raw/2026-08-24/`

Tile yang telah dibuat untuk screenshot yang diizinkan tersimpan di:

`/home/ubuntu/stockforge-evidence-tiles/2026-08-24/`

Log riset internal:

`/home/ubuntu/stockforge-evidence-raw/2026-08-24/RESEARCH_LOG.md`

Screenshot memiliki ukuran 1220 × 2712 px dan telah ditile vertikal menjadi tiga tile dengan manifest. Panduan `read-special-images` mewajibkan membaca manifest lalu setiap tile sesuai urutan top-to-bottom, mencatat fakta sebelum lanjut, serta tidak menebak teks atau angka yang tidak terbaca.

**Larangan penting:** jangan gunakan `file` tool untuk membuka ulang tiga lampiran asli terakhir `1000801961.jpg`, `1000801960.jpg`, dan `1000801959.jpg`. Tiga file itu belum dianalisis ulang dalam sesi riset ini karena instruksi lampiran pengguna. Jika analisis spesifik terhadap ketiganya benar-benar diperlukan, minta izin jelas pengguna terlebih dahulu. Fakta awal yang sudah tersimpan dari konteks sebelumnya boleh dipakai dengan label sebagai fakta awal, bukan pembacaan baru.

## 4. Titik berhenti ekstraksi

Pembacaan dan catatan telah selesai untuk screenshot `1000801962.jpg` sampai `1000801988.jpg`. Screenshot `1000801989.jpg` baru terbaca sampai tile 2; tile 3 belum dibaca ketika pengguna meminta handoff. Screenshot `1000801990.jpg` dan `1000801991.jpg` belum dilanjutkan dalam bagian riset ini. Jangan mengklaim seluruh 30 screenshot tiled sudah selesai dibaca.

Ringkasan fakta eksplisit yang sudah dicatat:

| File | Fakta visible yang dicatat | Motif best seller / isi |
|---|---:|---|
| `1000801962` | `klakon`, `$15.94` | Lanskap surreal horizontal: bentuk pucat seperti dunes/rocks, bola langit besar, langit biru berawan. |
| `1000801963` | `klakon`, `$15.89` | Adegan urban gelap: figur humanoid bersayap di rooftop di atas skyline kota. |
| `1000801964` | `$17.63` | Ilustrasi lebar beberapa karakter anjing antropomorfik berkostum superhero di kota. |
| `1000801965` | `$28.00` | Kartu hitam minimalis dengan lettering putih cursive kecil; teks tidak cukup terbaca. |
| `1000801966` | Akun berbeda, `River`, `$1,276` | Kelompok alat gambar berwarna: gunting, alat mirip palu, alat mirip bor, dan spool. Ini bukan bukti akun `klakon`. |
| `1000801967` | Akun berbeda, `Achmad Rizal`, `$70.16` | Adegan gelap dengan kuda api bercahaya, batu/storm scene, dan teks `2026`. |
| `1000801968` | `Achmad Rizal`, `$31.39` | Visual Natal lebar: figur Santa-like berbaju merah di latar hijau. |
| `1000801969` | `Achmad Rizal`, `$22.28` | Pandangan atas area warehouse/fulfilment dengan kotak, meja, dan orang. |
| `1000801970` | `Achmad Rizal`, `$16.64` | Close-up moss/tanaman hijau kecil dengan warm golden bokeh. |
| `1000801971` | `Achmad Rizal`, `$14.19` | Warehouse overhead dengan pallet, karton, aisle, dan forklift-like vehicles. |
| `1000801972` | Bukan sales notification | Contoh Patterny: `Jungle party for kids` dan `Jagung dan wortel lucu`; pola/ilustrasi anak-anak. Bukan bukti penjualan. |
| `1000801973` | `$11.28`, creator tidak terbaca | Kartun perempuan retro fitness/dance dalam ring/halo warna-warni. |
| `1000801974` | `$12.98`, creator obscured | Isolated electric motor rotor/armature di atas putih, technical clip-art appearance. |
| `1000801975` | `$4.62`, creator obscured | Ilustrasi camping seperti badge: pine trees, mobil retro biru, trailer/tent. |
| `1000801976` | `$4.42`, creator obscured | Isolated vintage leather aviator cap dengan goggles dan ear flaps. |
| `1000801977` | `$3.47`, creator obscured | Isolated stylised sliced ham/roast illustration. |
| `1000801978` | `$4.52`, creator obscured | Isolated metal spark-plug-like/threaded mechanical component. |
| `1000801979` | `$3.25`, creator obscured | Isolated red bellhop/concierge uniform dengan gold trim. |
| `1000801980` | `$1.02`, creator obscured | Retro space-shuttle/rocket badge dengan red planets dan starfield. |
| `1000801981` | `$1.96`, creator obscured | Isolated quilted brown duffel/travel bag illustration. |
| `1000801982` | `$0.99`, creator obscured | Front view black-and-silver V-twin motorcycle engine illustration. |
| `1000801983` | `$1.78`, creator obscured | Square dark-green quote graphic: daisy dan lettering `Happiness looks good on you.` |
| `1000801984` | `$0.98`, creator obscured | Cluster ilustrasi tomatoes berwarna merah/orange/kuning/hijau. |
| `1000801985` | `$0.59`, creator obscured | Cluster strawberries merah pada putih; engagement Threads terlihat `4.7K` likes, `260` comments, `608` reposts, `1K` sends. Engagement bukan bukti sales. |
| `1000801986` | `$0.99`, creator obscured | Red tomatoes pada green vine di atas putih; engagement Threads juga terlihat, tetapi bukan bukti sales. |
| `1000801987` | `$0.89`, creator obscured | Square abstract wavy bands/pattern warna kuning, peach, cokelat, putih, dark linework. |
| `1000801988` | `$0.89`, creator obscured | Square scattered blue watercolour-like raindrops di atas putih. |
| `1000801989` | `$0.76`, creator obscured; baru sampai tile 2 | Loose painterly pink-red heart dengan peach outline di atas putih. Tile 3 belum dibaca. |

Nominal di atas adalah nominal `Yesterday you made` pada screenshot, bukan estimasi royalty per asset. Satu screenshot tidak membuktikan download count, licence tier, exact asset ID, original format, account ownership, atau repeatable demand. Jangan menjumlahkan semua nominal tanpa terlebih dahulu memeriksa overlap/duplikasi hari dan akun.

## 5. Bukti awal yang belum boleh diperluas

Dari konteks sebelumnya, tiga screenshot terakhir memiliki fakta awal berikut, tetapi jangan membuka ulang file aslinya tanpa izin:

| File | Fakta awal yang sudah dicatat | Batas inferensi |
|---|---|---|
| `1000801961.jpg` | Adobe notification untuk `klakon`, `$11.51`, best seller berupa rusa geometris monokrom. | Tidak membuktikan ID, format, licence, akun, atau repeatability. |
| `1000801960.jpg` | Adobe notification untuk `klakon`, `$14.99`, best seller berupa ilustrasi UFO gelap. | Tidak membuktikan ID, format, licence, akun, atau repeatability. |
| `1000801959.jpg` | Earnings screen: `$461.23` lifetime earnings dan `1,341 Licensed downloads`. | Tidak mengidentifikasi portfolio, format, periode, licence mix, atau economics per file. |

## 6. Riset publik yang sudah dilakukan

Lead Adobe publik: [Adobe contributor profile klakonstudio](https://stock.adobe.com/contributor/211179033/klakonstudio), Contributor ID `211179033`. Profil ini merupakan **lead tidak terverifikasi**; kemiripan handle dengan salutation `klakon` tidak cukup untuk menyimpulkan bahwa sumber screenshot adalah akun tersebut. Portfolio publik terlihat broad/mixed dan tidak menghasilkan exact verified match untuk deer saat pencarian scoped.

Lead Shutterstock: [KlakonStudio By Eko](https://www.shutterstock.com/g/klakonstudio), Indonesia, dengan tampilan profil publik sekitar 670 images, 649 videos, 10 collections, dan 1K+ assets. Portfolio terlihat campuran: product photography, editorial local photography, 3D mockups/podiums, gradients, vectors, dan video. Ini tidak membuktikan hubungan dengan screenshot Adobe.

Sumber resmi Adobe yang sudah dipakai:

1. [Adobe Contributor Content Upload Guidelines](https://helpx.adobe.com/stock/contributor/content-policies-guidelines/content-policies/content-upload-guidelines.html) — JPEG, AI, EPS, SVG untuk kategori yang relevan; jalur GenAI dan vector memiliki syarat berbeda.
2. [Adobe Contributor Royalty Rates](https://helpx.adobe.com/stock/contributor/payments-earnings/royalties-pricing/royalty-rates-assets.html) — standard royalty images/vectors/illustrations disebut 33%, tetapi payout yang tampak dapat berbeda menurut buyer plan/licence.
3. [Adobe Royalties overview](https://contributor.stock.adobe.com/royalties).
4. [Adobe geometric deer search](https://stock.adobe.com/search?k=geometric+deer) — menunjukkan motif deer luas di marketplace, bukan exact match sumber screenshot.
5. [Adobe UFO search](https://stock.adobe.com/search?k=ufo) — market reference umum, bukan exact match.

Dokumen internal format: `docs/ADOBE_MULTIFORMAT_EVIDENCE_2026-08-24.md` dan `docs/MULTIFORMAT_ENGINE_V1.md`.

## 7. Kesimpulan sementara yang aman

Bukti yang sudah terbaca menunjukkan dua kelompok visual yang berbeda. Kelompok `klakon` memperlihatkan karya konseptual/illustrative yang lebar—surreal landscape, urban fantasy, superhero dogs, dan typography-like graphic. Kelompok lain memperlihatkan permintaan atau performa anecdotal untuk isolated object clip art, technical objects, food/produce, seasonal illustration, patterns, and backgrounds. Ini mendukung riset lanjutan terhadap beberapa buyer jobs, tetapi belum membuktikan bahwa satu niche atau satu format pasti lebih laku.

Tampilan putih di sekitar objek hanya berasal dari thumbnail/notifikasi; jangan menganggapnya sebagai bukti bahwa file asli opaque JPEG. Sebaliknya, isolated presentation adalah sinyal buyer-job yang mungkin cocok untuk PNG transparan atau vector, namun format harus diverifikasi melalui asset metadata atau sumber publik yang exact-match. Jangan mengubah semua objek menjadi PNG hanya karena terlihat isolated.

PNG transparan belum production-ready karena alpha producer dan portal route belum tervalidasi. SVG native lokal sudah dapat dibuat tanpa GPU untuk bentuk sederhana, tetapi tidak boleh dipakai sebagai klaim bahwa hasil generative raster dapat ditrace menjadi vector yang sah. JPEG raster adalah satu-satunya jalur generative preview yang saat ini benar-benar terverifikasi end-to-end.

## 8. Langkah aman untuk sesi berikutnya

1. Baca file ini terlebih dahulu.
2. Baca `RESEARCH_LOG.md` sebelum meneruskan, tetapi jangan membuka ulang tiga original attachment terakhir.
3. Lanjutkan hanya tile `1000801989` tile 3, lalu manifest dan semua tile `1000801990` dan `1000801991` jika tersedia dan diizinkan.
4. Setelah ekstraksi selesai, buat tabel terstruktur berisi file, akun bila terbaca, nominal, tanggal/context bila terbaca, motif, likely buyer job hanya jika ditandai sebagai hipotesis, dan confidence.
5. Lakukan riset publik bertahap dengan sumber resmi Adobe dan marketplace publik. Cari exact matches hanya bila ada sufficient visible clue. Jangan mengklaim `klakonstudio` adalah pemilik screenshot tanpa verifikasi.
6. Bandingkan buyer job dengan routing: JPEG raster, native SVG, future PNG alpha, dan video hanya jika ada jalur produksi gratis yang terverifikasi. Pisahkan status **verified production**, **locally ready but portal-unverified**, dan **research only**.
7. Tulis laporan Markdown Indonesia dengan citation links, tabel fakta versus hipotesis, matriks format, dan roadmap no-GPU.
8. Jangan menulis kode, menjalankan GPU, membuat gambar, memakai Kaggle, mengubah XMP, upload, submit, atau mengubah portal sebelum pengguna menyetujui rekomendasi riset.

## 9. Pesan pembuka siap copy ke sesi berikutnya

Gunakan pesan ini pada chat baru di Project STOCKFORGE AI:

> Baca dulu `docs/SESSION_HANDOVER_2026-08-24_RESEARCH.md` dan `docs/SESSION_HANDOVER_2026-08-24.md` di repo `ibank31/stockforge-ai`. Lanjutkan hanya dari handoff terbaru. Jangan buka ulang tiga original attachment `1000801961.jpg`, `1000801960.jpg`, `1000801959.jpg` tanpa izin saya. Titik berhenti riset: screenshot `1000801989` baru terbaca sampai tile 2; lanjutkan tile 3, lalu `1000801990` dan `1000801991` bila diizinkan. Setelah itu selesaikan riset marketplace dan rekomendasi format/niche. Jangan generate gambar, pakai GPU, Kaggle, XMP, upload, submit Adobe, mengubah portal, atau menulis kode sebelum saya menyetujui roadmap.

**Akhir handoff.**
