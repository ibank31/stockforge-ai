# Deep Research Pasar SVG untuk StockForge

**Tanggal:** 24 Agustus 2026
**Status:** Riset selesai untuk tahap pemilihan hipotesis; belum ada objek baru yang dibuat dan belum ada trial baru yang dijalankan.

## Ringkasan eksekutif

Riset menunjukkan bahwa pasar SVG tidak membeli “bentuk vector” secara abstrak. Buyer membeli **solusi visual yang dapat langsung dipakai**: ikon untuk web/UI, elemen bisnis dan infografik, file cut-ready untuk Cricut/Silhouette/laser/CNC, pattern, packaging, wedding/decor, atau komponen branding. Adobe Stock sendiri mengelompokkan vector menurut buyer job seperti components, icons, scenes, backgrounds, infographics, dan patterns.[^1]

Trial `modular-ribbon` gagal karena secara teknis ia memang SVG, tetapi secara komersial tidak memberi jawaban yang jelas: objeknya apa, dipakai untuk apa, dan buyer mana yang membutuhkannya. Riset ini menguatkan bahwa StockForge harus mengunci **buyer job → objek yang dikenali → gaya → format**, bukan sebaliknya.

Untuk trial berikutnya pada **opsi 1**, hipotesis paling aman adalah satu **folder-upload icon** untuk konteks file management/cloud workflow. Ini bukan klaim bahwa folder-upload pasti paling laku. Ini adalah kandidat pertama yang paling rasional untuk diuji karena memiliki use case eksplisit, siluet yang relatif mudah dikenali, kompatibilitas SVG yang kuat, risiko legal rendah jika dibuat generik, dan volume kompetisi snapshot yang lebih rendah daripada beberapa kandidat umum lain yang dibandingkan.[^2]

## Metodologi dan bobot bukti

Riset memakai hierarki bukti berikut. Kebijakan dan panduan resmi Adobe Stock dipakai untuk menentukan buyer value, technical fit, legal constraints, dan submission usability. Kategori serta hasil pencarian marketplace dipakai sebagai sinyal kategori dan proxy kompetisi. Etsy Seller Trend Reports dipakai untuk membaca buyer context dan tema retail/craft, bukan untuk menggeneralisasi penjualan ke Adobe Stock. Editorial trend reports dari Adobe Express dan Envato dipakai hanya sebagai sinyal style, bukan bukti demand.

| Sinyal | Makna yang boleh diambil | Makna yang tidak boleh diambil |
| --- | --- | --- |
| Kategori resmi marketplace | Ada use case yang diakui platform | Bukan jaminan penjualan |
| Jumlah hasil pencarian | Proxy volume kompetisi/supply | Bukan jumlah pembeli/download |
| Review listing Etsy | Bukti adanya transaksi/engagement pada listing tertentu | Bukan demand Adobe Stock dan bukan laporan penjualan lengkap |
| Trend report | Arah style atau tema yang sedang dibahas platform | Bukan bukti bahwa semua objek dalam style tersebut diminati |
| Panduan teknis | Syarat minimum usability dan submission | Bukan indikator komersial dengan sendirinya |

## Apa yang sebenarnya dibutuhkan buyer SVG

Adobe menjelaskan bahwa customer memakai vector untuk branding, digital illustration, product packaging, motion graphics, billboard scaling, dan recoloring icon.[^1] Nilai produknya berasal dari editability, scaling, recolor, dan penggunaan lintas konteks. Adobe juga merekomendasikan layers/groups yang terorganisasi, paths yang bersih, outlined strokes, satu artboard, dan desain yang fit terhadap artboard.[^3]

Untuk icon, Adobe membedakan single icon dan icon sheet. Single icon harus berupa bentuk gabungan dengan outlined stroke, background dan negative space transparan, serta tanpa collage, marketing text, raster, logo, trademark, atau brand.[^4] Dengan demikian, opsi 1 sebaiknya diperlakukan sebagai **single functional icon**, bukan mini-ilustrasi abstrak.

Etsy memberi sinyal yang berbeda tetapi berguna: buyer craft/DIY membeli file karena workflow-nya jelas—apparel, Cricut/Silhouette, laser/CNC, wedding/decor, packaging, floral/animal motifs, dan pola yang dapat dipotong atau diulang. Listing best-selling yang terlihat banyak berupa bundle lintas format, quote, motif, karakter, panel CNC, floral, dan geometric patterns.[^5] Sinyal ini memperkuat prinsip “jelas dipakai untuk apa”, tetapi segmen Etsy tidak boleh dicampur langsung dengan demand Adobe Stock.

## Sinyal bentuk dan style yang sedang dipakai

Adobe Express menyebut bold minimalism, metallics, pixels, bold/unique shapes, textured grains, maximalist illustration, gothic badges/crests, dan handcrafted aesthetics sebagai tren 2025.[^6] Untuk 2026, Adobe Express menekankan organic/imperfect design, warm personal style, local/cultural flavor, tactile materials, collage, and freeform storytelling.[^7]

Envato menyoroti soft 3D, hyper-minimal line icons, retrofuturist icons, mascot icons, micro-illustrated icons, variable icons, bold geometric icons, dan multi-material icons. Dalam konteks use case, hyper-minimal line icons diarahkan ke productivity tools, SaaS UI, privacy/crypto apps, dan dashboards; bold geometric icons diarahkan ke brand-led digital products, social media, dan event branding.[^8]

Untuk StockForge, style bukan pemimpin keputusan. Style harus menjadi lapisan kedua setelah objek dan buyer job. Untuk trial pertama, **bold geometric atau restrained hyper-minimal** lebih aman daripada soft 3D, multi-material, collage, atau maximalism karena lebih mudah dijaga sebagai native SVG, terbaca pada thumbnail, dan diedit lintas aplikasi. Trend tidak boleh membuat objek kembali menjadi ambigu seperti `modular-ribbon`.

## Proxy kompetisi kandidat objek

Snapshot hasil pencarian Adobe Stock pada 24 Agustus 2026 memberikan angka berikut. Angka mencakup seluruh media pada halaman pencarian, bukan hanya SVG/vector, dan bukan angka download atau sales.[^2]

| Kandidat/query | Hasil snapshot | Buyer job yang terlihat | Interpretasi awal |
| --- | ---: | --- | --- |
| `folder upload icon` | 166.830 | file upload, file management, cloud/storage workflow | Kompetisi relatif lebih rendah pada sampel; fungsi cukup jelas |
| `data backup icon` | 349.129 | cloud backup, database save, file storage | Fungsi jelas, tetapi istilah security/protection perlu dijaga agar tidak menjadi klaim |
| `cloud upload icon` | 371.713 | data transfer, cloud storage, backup, web/mobile UI | Use case kuat, tetapi sudah sangat kompetitif |
| `file management icon` | 383.722 | document management, upload/download, file organization | Buyer job jelas; bentuk berisiko terlalu generik |
| `shopping cart icon` | 858.927 | ecommerce, checkout, online shopping | Sangat kompetitif dan mudah menjadi ikon generik |
| `packaging box icon` | 1.343.579 | packaging, shipping, product box | Use case luas tetapi supply snapshot sangat besar |
| `calendar icon` | 2.041.766 | scheduling, appointment, productivity, event planning | Sangat jenuh; tidak ideal sebagai trial pembuktian pertama |
| `arrow icon` | 5.968.162 | navigation, direction, progress, flowchart | Sangat jenuh dan sering menjadi komponen, bukan produk tunggal kuat |

Angka tersebut hanya membantu memilih eksperimen awal. Volume hasil yang rendah tidak membuktikan demand tinggi, dan volume tinggi tidak membuktikan peluang rendah; keduanya harus dibaca bersama recognizability, buyer job, technical fit, dan rights safety.

## Ranking hipotesis objek untuk opsi 1

| Peringkat | Hipotesis objek tunggal | Kejelasan buyer job | Saturation proxy | SVG fit | Risiko utama | Status |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | **Folder-upload icon** untuk file management/cloud workflow | Tinggi | Relatif lebih rendah dalam sampel | Tinggi | Terlalu generik bila tanpa treatment yang distinctive | Kandidat trial pertama |
| 2 | **Data-backup icon** berupa database/folder dengan panah simpan | Tinggi | Menengah-rendah dalam sampel | Tinggi | Mudah bergeser menjadi security/protection claim | Kandidat cadangan |
| 3 | **Cloud-upload icon** | Tinggi | Menengah | Tinggi | Supply besar dan banyak duplikasi | Kandidat cadangan |
| 4 | **Shopping-cart icon** | Tinggi | Tinggi | Tinggi | Sangat generik dan kompetitif | Tunda |
| 5 | **Packaging-box icon** | Menengah-tinggi | Tinggi | Tinggi | Terlalu luas; banyak hasil packaging/box | Tunda |
| 6 | **Calendar icon** | Tinggi | Sangat tinggi | Tinggi | Saturation dan similarity | Tunda |
| 7 | **Arrow icon** | Tinggi sebagai komponen | Sangat tinggi | Tinggi | Lebih cocok sebagai bagian sheet/infographic | Tunda |

## Rekomendasi trial pertama

Hipotesis trial yang direkomendasikan adalah:

> **Satu single SVG folder-upload icon yang langsung dikenali, terisolasi, terpusat, kontras tinggi, editable, dan ditujukan untuk file management/cloud workflow pada web, mobile UI, dashboard, atau presentation.**

Bentuk tidak boleh berupa folder abstrak dengan ornament. Elemen visual minimum harus cukup untuk mengkomunikasikan dua hal: **folder/file storage** dan **upload/action**. Tidak boleh ada logo aplikasi, nama brand, teks, label, monitor, smartphone, dashboard frame, atau decorative ribbon. Penggunaan istilah “secure”, “protected”, atau “guaranteed backup” harus dihindari karena dapat mengubah simbol desain menjadi klaim keamanan.

Gaya awal yang direkomendasikan adalah **bold geometric dengan restrained hyper-minimal structure**: siluet folder yang tegas, satu panah upload yang proporsional, stroke atau merged shape yang konsisten, dua atau tiga warna dengan kontras tinggi, dan transparent negative space. Jangan memakai 3D, glow, chrome, material texture, collage, atau multi-object scene pada trial pertama. Style boleh membuat icon lebih modern, tetapi tidak boleh mengurangi recognizability.

Artboard harus fit-to-content dengan margin konsisten, tidak menempatkan objek di sudut, dan tidak menyisakan whitespace berlebihan. File harus tetap native-only, tanpa raster, script, external reference, atau hidden content. Metadata harus menyebut objek dan fungsi visual secara literal dan akurat, misalnya “Editable folder upload icon for file management and cloud workflow”; kata-kata seperti secure, compliant, guaranteed, or official tidak boleh dipakai.

## Gate evaluasi sebelum trial

Trial hanya boleh dijalankan setelah brief final dikunci dan tetap satu kandidat. Review manusia harus menjawab pertanyaan berikut tanpa membaca title terlebih dahulu:

| Gate | Pertanyaan lulus |
| --- | --- |
| Recognizability | Dalam 2–3 detik, apakah orang menyebutnya folder dengan tindakan upload? |
| Buyer job | Apakah terlihat konteks penggunaan web/mobile UI, dashboard, file management, atau cloud workflow? |
| Distinctness | Apakah treatment memiliki pembeda nyata tanpa menjadi dekorasi abstrak? |
| Thumbnail | Apakah siluet dan panah tetap terbaca pada ukuran kecil? |
| Composition | Apakah objek terpusat dan menggunakan artboard secara wajar? |
| Editability | Apakah paths/compound shapes mudah diedit, recolor, dan dipakai ulang? |
| Rights safety | Apakah tidak ada brand, logo, app likeness, text, atau IP pihak ketiga? |
| Metadata | Apakah title/keywords hanya menyebut hal yang terlihat dan buyer job yang wajar? |

Jika buyer job atau recognizability gagal, trial ditolak meskipun structural SVG gate PASS. Tidak boleh ada seed-only retry, batch generation, atau variasi warna untuk mengejar skor.

## Apa yang belum terbukti

Riset ini belum membuktikan objek mana yang paling laku, karena data download, conversion, dan revenue per query tidak tersedia secara publik dari sumber yang diakses. Riset juga belum memberi bukti bahwa demand Etsy craft/DIY dapat dipindahkan ke Adobe Stock. Karena itu, `folder-upload icon` harus diperlakukan sebagai **hypothesis candidate**, bukan keputusan upload atau klaim market fit.

Tidak ada perubahan kode dan tidak ada generation berdasarkan laporan ini. Langkah berikutnya adalah meminta persetujuan atas kandidat dan buyer job, kemudian mematangkan lane/brief/metadata/QA gate sebelum satu trial lokal SVG dijalankan.

## Referensi

[^1]: [Adobe Stock — Vector submissions](https://helpx.adobe.com/stock/contributor/submit-your-content/submit-vectors/vector-submission-overview.html), diakses 24 Agustus 2026.
[^2]: [Adobe Stock — Search snapshots for folder upload, data backup, cloud upload, file management, shopping cart, packaging box, calendar, and arrow icons](https://stock.adobe.com/search?k=folder+upload+icon), diakses 24 Agustus 2026. Tautan query lain tercatat di [catatan riset mentah](./svg_market_2026-08-24.md).
[^3]: [Adobe Stock — Design requirements for vector submissions](https://helpx.adobe.com/stock/contributor/submit-your-content/submit-vectors/design-requirements-for-vector-submissions.html) dan [Vector creation best practices](https://helpx.adobe.com/stock/contributor/submit-your-content/submit-vectors/vector-creation-best-practices.html), diakses 24 Agustus 2026.
[^4]: [Adobe Stock — Technical and legal requirements for vector icons and sheets](https://helpx.adobe.com/stock/contributor/submit-your-content/submit-icons/technical-legal-requirements-vector-icons-sheets-submission.html) dan [Icons creation best practices](https://helpx.adobe.com/stock/contributor/submit-your-content/submit-icons/tips-submit-vector-icons-sheets.html), diakses 24 Agustus 2026.
[^5]: [Etsy — Best Selling SVG Files](https://www.etsy.com/market/best_selling_svg_files) dan [Etsy — SVG Design Patterns](https://www.etsy.com/market/svg_design_patterns), diakses 24 Agustus 2026.
[^6]: [Adobe Express — Graphic design trends for 2025](https://www.adobe.com/express/learn/blog/design-trends-2025), diakses 24 Agustus 2026.
[^7]: [Adobe Express — Design trends for 2026](https://www.adobe.com/express/learn/blog/design-trends-2026), diakses 24 Agustus 2026.
[^8]: [Envato Elements — Icon design trends 2026](https://elements.envato.com/learn/icon-design-trends), diakses 24 Agustus 2026.
