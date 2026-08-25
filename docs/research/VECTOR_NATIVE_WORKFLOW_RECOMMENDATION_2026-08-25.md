# Rekomendasi workflow vector native StockForge

**Tanggal:** 25 Agustus 2026  
**Status:** Preset dan batch sudah diimplementasikan; dry-run readiness lulus; belum ada SVG final atau upload.

## Kesimpulan eksekutif

Format vector dapat dibuat melalui mesin ini, tetapi jalurnya berbeda dari JPEG. StockForge tidak mengubah JPEG menjadi vector dan tidak menggunakan model raster untuk berpura-pura menghasilkan SVG. Route yang aman adalah **local native-vector build**: SVG disusun dari path, shape, group, dan pattern yang dapat diaudit, lalu dirender untuk pemeriksaan thumbnail dan dibuka ulang sebagai XML untuk memastikan tidak ada raster embed, text object, script, atau elemen asing.

Untuk trial pertama, pilihan yang paling rasional bukan “gambar vector apa saja,” melainkan **satu micro-set utility icon dengan buyer job yang sempit dan jelas**. Preset yang sudah tersedia adalah `file_flow_micro_set`, yang menghasilkan delapan icon bertema alur file. Ini adalah pilihan terbaik untuk *feasibility produksi* karena route, preset, schema, dan QA-nya sudah ada. Namun, istilah “mudah dijual” tidak dapat dijanjikan: supply proxy Adobe untuk `utility icons` sekitar 604.515 hasil dan `file management icon` sekitar 384.106 hasil, sehingga tema harus dipersempit dan desain harus benar-benar berbeda.

## Apa yang mesin bisa dan belum bisa

| Kemampuan | Status sekarang | Makna praktis |
|---|---|---|
| SVG native dari path/shape/group | **Tersedia dan production-verified** | Dapat menghasilkan SVG editable tanpa GPU atau image trace |
| Folder-upload icon | **Tersedia** | Cocok untuk satu simbol utility yang langsung terbaca |
| File-flow icon micro-set | **Tersedia** | Cocok untuk satu sheet delapan simbol dengan tema konsisten |
| Geometric seamless pattern | **Tersedia** | Cocok untuk tile berulang berbasis shape sederhana |
| Technical badge | **Tersedia, tetapi buyer-fit lebih lemah** | Cocok untuk simbol geometrik abstrak, bukan technical illustration kompleks |
| Modular ribbon | **Tersedia, tetapi abstract** | Feasible secara XML, namun buyer job kurang spesifik |
| AI raster-to-SVG trace | **Tidak digunakan** | Raster tidak boleh diklaim sebagai native vector |
| Character scene, textured illustration, complex product render | **Belum cocok** | Memerlukan preset path yang jauh lebih kompleks dan QA berbeda |
| Portrait vector template | **Belum diimplementasikan** | Route portrait ditolak oleh format router |

Route internal `native_vector` memakai `local_native_vector_build`, output `.svg`, artboard `2048×2048`, dan pemeriksaan XML native. SVG yang dihasilkan tidak memakai `<image>`, `<text>`, `<script>`, `foreignObject`, `data:image`, `javascript:`, atau `@import`. Ini membuat route lebih dapat diaudit daripada meminta model gambar menghasilkan “vector look”.

## Kandidat vector dan scorecard konservatif

Skor 0–5 berikut adalah penilaian workflow, bukan prediksi penjualan. **Buyer job** berarti kejelasan pekerjaan yang dapat dibantu aset. **Supply proxy** berarti jumlah hasil pencarian Adobe yang terlihat pada 25 Agustus 2026; angka besar menunjukkan istilah lebih crowded, bukan demand lebih tinggi.

| Kandidat | Buyer job | Feasibility mesin | Editability/QA | Distinctness headroom | IP/release burden | Supply proxy | Total / 25 | Keputusan |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Themed file-workflow utility icon micro-set | 4 | 5 | 5 | 3 | 5 | 1 | **23** | **Pilihan pertama untuk trial** |
| Single folder-upload utility icon | 4 | 5 | 5 | 2 | 5 | 1 | **22** | Fallback sederhana, tetapi sangat generik |
| Narrow technical pictogram micro-set | 3 | 4 | 4 | 4 | 5 | 3 | **23** | Perlu preset baru dan buyer job lebih tajam |
| Seamless geometric pattern tile | 3 | 5 | 4 | 2 | 5 | 1 | **20** | Feasible, tetapi broad pattern sangat crowded |
| Abstract modular ribbon system | 2 | 5 | 4 | 3 | 5 | 4 | **23** | Tidak dipilih karena utility pembeli terlalu kabur |

Supply proxy yang dipakai: `utility icons` 604.515 hasil, `file management icon` 384.106, `"tech icons"` 25.018, `"icon pack"` 86.903, dan `seamless geometric pattern` 6.279.918. Proxy ini tidak mengukur penjualan, ranking, approval, conversion, atau demand.

## Rekomendasi produk pertama

Rekomendasi saya adalah **themed file-workflow utility icon micro-set**, bukan generic “icon pack”. Buyer job yang konkret: menyediakan simbol konsisten untuk dokumentasi software, onboarding workflow, dashboard, slide explainer, atau artikel yang menjelaskan perpindahan file. Adobe menjelaskan bahwa icon sheets digunakan untuk marketing materials, UI, presentations, dan animations, sementara Google Material Design menjelaskan bahwa icon adalah simbol sederhana untuk mengidentifikasi action dan category serta perlu tetap jelas pada ukuran kecil [1] [2].

Untuk membedakan dari generic pack, satu trial sebaiknya mempunyai **satu workflow yang utuh**, misalnya `document review and delivery`: intake, organize, review, approve, archive, restore, sync, dan share. Ini adalah hipotesis desain, bukan jaminan pasar. Setiap icon harus memakai grid, stroke weight, corner logic, dan palette yang konsisten; tidak memakai text, brand, app logo, trademark, atau simbol yang dapat terbaca sebagai produk tertentu.

Preset baru `document_review_delivery_micro_set` sekarang sudah ditambahkan untuk merepresentasikan workflow tersebut dengan delapan simbol yang benar-benar berbeda dari folder/upload/download/cloud/file-flow generic. Preset ini tetap perlu QA SVG dan thumbnail setelah satu local trial disetujui. **Tidak boleh membuat candidate baru hanya dengan recolor atau rotasi.**

## Workflow yang disarankan

Pertama, StockForge memilih satu buyer job dan delapan simbol yang saling melengkapi. Kedua, brief menetapkan SVG, square artboard, transparent background bila edge quality sudah lolos, no text, no branding, no raster, and no hidden/locked groups. Ketiga, builder lokal menyusun native geometry secara deterministik. Keempat, validator memeriksa XML well-formedness, allowed element set, dimensions, artboard origin, viewBox, absence of raster/script/text, repeatability bila pattern, and group coherence. Kelima, renderer menghasilkan preview PNG hanya untuk review; preview bukan file upload vector. Keenam, human reviewer memeriksa apakah setiap symbol langsung terbaca, tidak terlalu mirip satu sama lain, tidak memiliki anchor-point clutter, broken strokes, accidental gaps, odd joins, or misleading semantics. Ketujuh, setelah explicit acceptance, file SVG asli yang diedit dikemas untuk upload manual.

Adobe menyatakan bahwa vector submission harus berupa AI, EPS, atau SVG, bukan JPEG atau ZIP sebagai file vector. Adobe juga meminta logical labeled groups/layers, outlined fonts, editable rather than rasterized assets, RGB, artboard offset `(0,0)`, dan maksimum 45 MB [3]. Untuk generative-AI-assisted vectors, Adobe menekankan bahwa contributor hanya mengirim konten yang dimiliki sendiri, harus mengerjakan ulang hasil agar mudah diedit seperti vector organik, dan hanya mengirim original editable scenes/subjects, simple editable icon shapes, atau seamlessly tileable patterns [4].

Dengan demikian, route yang paling aman untuk mesin ini adalah **local deterministic SVG first, human visual review second, manual Adobe submission last**. JPEG preview boleh dipakai untuk melihat thumbnail, tetapi tidak boleh menggantikan SVG yang sebenarnya.

## Gates minimum sebelum satu trial vector

| Gate | Pass condition |
|---|---|
| Buyer job | Satu pekerjaan pengguna jelas; bukan “dekorasi vector” umum |
| Native structure | Hanya path/shape/group/defs yang diizinkan; tidak ada `<image>` atau raster embed |
| Editability | Group teratur, anchor points tidak berlebihan, stroke/fill dapat diedit |
| Artboard | Offset `(0,0)`, square 2048×2048 route sekarang, RGB intent, file di bawah 45 MB |
| Background | Transparent atau flat color sesuai brief; tidak ada checkerboard palsu |
| Semantics | Setiap icon terbaca tanpa mengandalkan teks; icon sheet punya satu tema |
| IP/legal | Tidak ada logo, trademark, nama aplikasi, artist name, fictional character, atau reference artwork tanpa hak |
| Metadata | Judul dan keyword visual-first; 10 keyword pertama paling penting; tidak memasukkan kata `vector` sebagai gimmick atau istilah IP |
| Variation | Tidak mengirim beberapa versi minimal dari prompt atau recolor-only duplicates |
| Human review | Reviewer melihat SVG structure dan rendered preview sebelum upload |

## Keputusan dan langkah berikutnya

Lane `native_vector_workflow_sets`, concept `document-review-delivery-micro-set`, dan preset SVG native sudah terdaftar. Batch project-local sudah dibuat, full tests lulus, dan readiness dry-run mengizinkan satu local trial dengan `provider_call_allowed=false`. Langkah berikutnya adalah meminta approval untuk **satu local SVG trial**. Trial tersebut tidak memakai GPU, tidak memakai Kaggle, tidak memerlukan credential, dan tidak boleh dikirim ke Adobe sebelum human review.

## References

[1]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-icons/single-vector-icons-sheets-submission-overview.html "Single vector icons and sheets submission overview | Adobe Stock Contributor Help"
[2]: https://m3.material.io/styles/icons/applying-icons "Icons | Material Design 3"
[3]: https://helpx.adobe.com/in/stock/contributor/help/vector-requirements.html "Requirements for contributing vector art to Adobe Stock | Stock Contributor"
[4]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-vector-submission-guidelines.html "Generative AI vector submission guidelines | Adobe Stock Contributor Help"
