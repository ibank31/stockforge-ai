# Riset Sistem Asset Makanan Tradisional Global

**Tanggal riset:** 26 Agustus 2026 (GMT+7)
**Penulis:** Manus AI
**Repository:** `ibank31/stockforge-ai`
**Branch:** `main` (merged from `research/traditional-food-niches-2026`)
**Status:** Riset operasional dan backlog prioritas yang sudah merged; katalog tidak otomatis mengotorisasi generation, upload, submission, atau klaim penjualan.

## Ringkasan eksekutif

Arah produk yang dipakai dalam dokumen ini bukan memilih satu makanan negara sebagai pemenang. Arah yang dipakai adalah membangun **sistem katalog asset makanan tradisional per negara**, kemudian mengatur urutan produksi melalui prioritas konservatif. Setiap negara memiliki satu atau lebih `anchor food candidate`; istilah ini sengaja digunakan sebagai kandidat representatif, bukan klaim bahwa makanan tersebut adalah satu-satunya makanan nasional, versi paling autentik, atau makanan yang pasti laku.

Riset ini menghasilkan dua lapisan data. Katalog global berisi **63 kandidat anchor dari berbagai negara** dalam tiga tier produksi: P0 berisi 12 kandidat yang relatif mudah dikenali dan memiliki bukti budaya atau buyer utility yang lebih kuat; P1 berisi 22 kandidat yang memerlukan lokalisasi dan validasi lebih lanjut; P2 berisi 29 kandidat eksplorasi dengan kebutuhan validasi lokal yang lebih tinggi. Katalog Indonesia berisi **32 kandidat regional**, termasuk 8 P0, 12 P1, dan 12 P2. Keduanya adalah seed catalog, bukan daftar final seluruh negara atau seluruh kuliner Indonesia.

Temuan utama adalah bahwa nilai asset tidak hanya berada pada gambar piring. Sumber akademik tentang Indonesia menekankan hubungan makanan dengan alam, sejarah, budaya, bahan, teknik, penyajian, dan praktik sosial [1]. UNESCO juga mendeskripsikan banyak praktik kuliner sebagai sistem pengetahuan, musim, komunitas, transmisi antargenerasi, dan hubungan dengan sumber daya alam, bukan sekadar resep [2] [3] [4] [5] [6] [7] [8]. Karena itu, satu negara sebaiknya memiliki beberapa jenis asset: **dish object**, **ingredient identity**, **preparation/material study**, dan bila aman serta memiliki bukti, **social or seasonal context**.

Untuk Stockforge, produksi awal sebaiknya tetap mengikuti aturan standalone yang sudah aktif: satu subjek yang jelas, background putih atau bersih, tanpa teks dan branding, lalu diuji sebagai JPEG raster yang dapat digunakan pada menu, artikel resep, tourism editorial, packaging concept, atau social creative. Scene, manusia, ritual, signage, dan properti lokal ditambahkan hanya setelah AssetSpec dan evidence mendukungnya. Adobe menekankan niche study, pemahaman buyer, campuran evergreen/seasonal/trending, realism, local authenticity, dan commercial usability [9]. Adobe juga mewajibkan metadata akurat, kata kunci relevan, penandaan AI, serta hak komersial yang memadai [10] [11].

## 1. Pertanyaan riset dan batasan

Pertanyaan kerja riset ini adalah: bagaimana Stockforge dapat membuat asset makanan tradisional dari setiap negara secara sistematis, dengan prioritas produksi yang transparan, mudah dilacak, dan aman secara budaya serta platform? Pertanyaan ini tidak sama dengan “makanan mana yang paling laku”. Tidak ada data publik yang cukup untuk menyimpulkan conversion atau pendapatan dari satu niche hanya dari result count, screenshot, atau popularitas kuliner.

Prioritas di sini berarti **urutan eksperimen produksi**, bukan probabilitas penjualan. Prioritas dapat berubah setelah human review, QA visual, metadata validation, similarity clustering, dan evidence baru. Nama negara dan makanan diperlakukan sebagai metadata faktual yang harus benar-benar terlihat atau didukung sumber; bukan sebagai dekorasi keyword.

| Istilah | Definisi operasional | Tidak boleh disalahartikan sebagai |
|---|---|---|
| `anchor food candidate` | Makanan atau praktik kuliner yang dipakai sebagai titik awal katalog suatu negara | Satu-satunya makanan nasional atau versi paling autentik |
| `P0` | Kandidat untuk controlled pilot karena kombinasi recognizability, visual clarity, buyer utility, dan evidence relatif kuat | Jaminan demand atau approval |
| `P1` | Kandidat yang layak diproduksi setelah validasi lokal dan penetapan varian | Prioritas rendah secara budaya |
| `P2` | Kandidat eksplorasi yang membutuhkan sumber lokal, konsultasi, atau QA lebih ketat | Kandidat tidak bernilai |
| `validated anchor` | Ada dukungan sumber yang cukup untuk nama/fungsi umum kandidat | Semua detail resep, wilayah, ritual, dan plating sudah tervalidasi |
| `source confidence` | Keyakinan terhadap kecukupan provenance untuk tahap katalog | Skor penjualan atau kualitas gambar |

## 2. Evidence yang digunakan

### 2.1 Evidence budaya dan kuliner Indonesia

Wijaya memetakan makanan Indonesia sebagai hasil interaksi alam, sejarah, dan budaya. Artikel tersebut menyatakan bahwa promosi kuliner seharusnya menyampaikan nilai sosial-budaya di balik makanan, bukan hanya menampilkan daftar hidangan. Artikel itu juga mencatat ketidakseimbangan exposure antara Jawa/Sumatra dan wilayah lain, serta membedakan fase original/indigenous, multicultural, dan contemporary dalam perkembangan kuliner Indonesia [1]. Kerangka ini mendukung keputusan produk untuk membuat **regional identity atom** pada setiap asset, bukan memproduksi piring generik berlabel “Asian food”.

Studi tentang sambal meninjau 110 variasi dari berbagai wilayah Indonesia. Artikel tersebut melaporkan 64,5% varian yang ditinjau berasal dari Jawa, 10,9% dari Borneo, 9,1% dari Sulawesi, dan 15,5% dari Bali, Nusa Tenggara, Maluku, serta Papua. Lebih dari 80% varian diproses dengan crushing dan cooking; secondary ingredients seperti buah, ikan, seafood, tumbuhan aromatik, terasi, tempe, oncom, petis, andaliman, tempoyak, dan kluwak memberikan identitas visual dan regional [12]. Angka tersebut berlaku pada corpus review dan cookbook yang digunakan penulis, bukan sensus final seluruh sambal Indonesia.

Studi sejarah pempek menghubungkan pempek dengan Palembang, ikan sungai, tapioka/sagu, cuko, praktik sosial, dan transformasi dari produksi rumah tangga menjadi industri serta oleh-oleh [13]. Ini membuat pempek cocok sebagai contoh asset system: bentuk adonan, bahan ikan, sago, cuko, proses, dan plated dish dapat dipisah menjadi beberapa asset yang berbeda secara fungsi. Model tidak boleh menggabungkan seluruh variasi pempek menjadi satu bentuk “canonical”.

Studi lintas sembilan negara, termasuk Indonesia, mendefinisikan traditional foods and beverages sebagai makanan yang terhubung dengan identitas budaya, diwariskan lintas generasi, representatif, dikenal, dan masih dikonsumsi. Untuk Indonesia, peneliti melonggarkan kriteria nasional karena negara kepulauan memiliki variasi antarpulau; makanan serupa dengan nama berbeda dapat dikelompokkan ketika bahan, bentuk, dan tipe makanannya sebanding [14]. Studi yang sama menemukan bahwa kelompok lebih muda cenderung menyebut snack dan makanan on-the-go, sementara kelompok lebih tua lebih sering menyebut hidangan gurih yang memerlukan waktu persiapan. Temuan ini berguna sebagai hipotesis format, tetapi data surveinya berasal dari 2018 dan bukan data demand marketplace terkini.

### 2.2 Evidence global

UNESCO memberi contoh bahwa kategori “makanan tradisional” sering mencakup praktik, pengetahuan, ritual, komunitas, alat, musim, dan lingkungan. Washoku dikaitkan dengan bahan lokal, penghormatan terhadap alam, tableware, perayaan Tahun Baru, dan transmisi dalam keluarga [2]. Kimjang mencakup siklus tahunan pengadaan seafood, garam, cabai, musim pembuatan, kerja kolektif, pertukaran kimchi, dan perbedaan antardaerah [3]. Traditional Mexican cuisine mencakup jagung, kacang, cabai, milpa, chinampa, nixtamalization, alat batu, komunitas, serta rantai dari penanaman sampai konsumsi [4]. Gastronomic meal of the French menekankan kebersamaan, pemilihan bahan, urutan sajian, table setting, dan pengetahuan gastronomes [5]. Art of Neapolitan Pizzaiuolo menekankan tahap adonan dan pemanggangan wood-fired dengan gerak rotasi serta transmisi dalam bottega [6]. Tomyum Kung dideskripsikan sebagai sup udang dengan herbs lokal, warna kuat, rasa kompleks, ekologi sungai, dan transmisi keluarga/komunitas [7]. Mediterranean diet menekankan keterampilan, panen, fishing, preservation, cooking, sharing, market, dan social identity lintas beberapa negara [8].

Dari sumber tersebut, struktur katalog global tidak boleh hanya memiliki kolom `country` dan `dish`. Minimal perlu ada `food_family`, `visual_signature`, `heritage_or_identity_angle`, `buyer_jobs`, `asset_series_plan`, `source_basis`, dan `risk_notes`. Struktur itu sudah diterapkan pada CSV yang disertakan dalam branch ini.

### 2.3 Evidence marketplace dan submission

Panduan resmi Adobe menganjurkan contributor memilih niche, mempelajari kebutuhan buyer, memantau tren dan supply/demand, serta mencampur konten evergreen, seasonal, dan trending. Adobe menyebut food sebagai tema evergreen, tetapi menganjurkan local angle atau fresh take agar tidak menjadi konten generik [9]. Panduan metadata Adobe menyatakan bahwa metadata harus mendeskripsikan apa yang benar-benar terlihat, menggunakan satu bahasa secara konsisten, menempatkan keyword terpenting di sepuluh urutan pertama, menjaga title tetap ringkas, dan biasanya memakai sekitar 15–35 keyword yang relevan. Adobe juga memperingatkan bahwa keyword spamming merusak relevansi dan dapat berdampak pada visibility atau akun [10].

Adobe menyediakan kategori `Food` untuk culinary photography, ingredients, recipes, dining scenes, dan food preparation; kategori `Culture and religion` atau `Travel` hanya dipakai bila subject dan konteks benar-benar mendukungnya [11]. Untuk konten generatif AI, Adobe mensyaratkan contributor memiliki hak yang diperlukan dari tool, menandai `Created using generative AI tools`, melarang nama artis, orang nyata, karakter fiksi, karya berhak cipta, third-party IP, serta klaim seolah-olah gambar menunjukkan peristiwa nyata. Konten AI yang menampilkan orang atau properti yang dapat dikenali dapat memerlukan release; konten AI tidak dapat disubmit sebagai Illustrative Editorial [15] [16].

## 3. Kerangka prioritas produksi

Prioritas bersifat multi-criteria dan harus dihitung per kandidat, bukan per negara secara permanen. Gunakan nilai 1–5 untuk setiap dimensi berikut. Skor adalah alat sequencing internal, bukan forecast.

| Dimensi | Pertanyaan penilaian | Skor tinggi berarti |
|---|---|---|
| Recognizability | Apakah bentuk atau komponen mudah dikenali oleh buyer lintas bahasa? | Siluet, warna, atau bentuk kuat |
| Visual distinctness | Apakah kandidat berbeda secara visual dari generic food imagery? | Identitas bahan, bentuk, vessel, atau proses jelas |
| Buyer utility | Pekerjaan komunikasi apa yang diselesaikan? | Recipe, menu, tourism, packaging, education, atau editorial jelas |
| Variation potential | Dapatkah dibuat beberapa asset yang benar-benar berbeda? | Dish, ingredient, method, serving, seasonal variant |
| Evidence confidence | Apakah nama, wilayah, dan konteks didukung sumber? | Detail dapat diverifikasi |
| Production fit | Apakah dapat dibuat sebagai single subject sesuai route aktif? | Tidak memerlukan people/property/scene gate |
| Compliance safety | Apakah risiko IP, release, cultural claim, dan policy rendah? | Food object tanpa brand/person/claim |
| Saturation proxy | Apakah kandidat tidak hanya menjadi keyword generic dengan supply ekstrem? | Search term dapat dibuat spesifik |

Urutan produksi digunakan sebagai berikut.

| Tier | Kriteria keputusan | Bentuk produksi awal |
|---|---|---|
| **P0 — controlled pilot** | Recognizable, visual clarity tinggi, buyer job jelas, evidence relatif kuat, dan dapat dibuat standalone | 1 dish object + 1 ingredient identity + 1 preparation/material study |
| **P1 — localized expansion** | Anchor kuat tetapi varian, transliterasi, wilayah, atau sumber perlu diperjelas | 1 dish object setelah local-source check, lalu modular components |
| **P2 — discovery and consultation** | Visual atau budaya menarik tetapi recognizability/evidence rendah, atau ada risiko context collapse | Research brief, source validation, optional consultation, baru kemudian asset |

**Urutan ini tidak membandingkan nilai budaya antarnegara.** Tier hanya menentukan kapan Stockforge memiliki cukup informasi dan kesiapan produksi untuk menguji kandidat secara aman.

## 4. Katalog dan cakupan saat ini

File `data/research/global_traditional_food_asset_catalog.csv` adalah seed catalog lintas kawasan. File tersebut memiliki 63 rows: 12 P0, 22 P1, dan 29 P2. File `data/research/indonesia_regional_food_asset_candidates.csv` memiliki 32 rows: 8 P0, 12 P1, dan 12 P2. Ringkasan ini diverifikasi secara programatik oleh `scripts/analyze_food_catalog.py` dan disimpan pada `data/research/food_catalog_summary.json`.

| Dataset | Rows | P0 | P1 | P2 | Confidence high | Confidence medium | Confidence low |
|---|---:|---:|---:|---:|---:|---:|---:|
| Global seed catalog | 63 | 12 | 22 | 29 | 19 | 34 | 10 |
| Indonesia regional catalog | 32 | 8 | 12 | 12 | 8 | 18 | 6 |

Katalog global sengaja mencakup Asia, Eropa, Afrika, Timur Tengah, Amerika, Karibia, dan Oseania agar sistem tidak berhenti pada satu wilayah. Namun, 63 rows tersebut bukan klaim telah menyelesaikan seluruh negara. Agent berikutnya harus mempertahankan schema yang sama, menambahkan negara yang belum terwakili, dan mengisi sumber lokal sebelum memindahkan kandidat dari P2 ke P1 atau P0.

### 4.1 Prioritas awal global

P0 global saat ini mencakup **Indonesia–rendang**, **Jepang–washoku seasonal meal**, **Meksiko–traditional maize/tamale or tortilla system**, **Italia–Neapolitan pizza**, **Thailand–tom yum kung**, **Korea Selatan–kimjang/kimchi practice**, **India–biryani or thali**, **China–dim sum or Peking duck**, **Vietnam–phở**, **Türkiye–baklava or kebab**, **Prancis–gastronomic meal or baguette**, dan **Peru–ceviche**. Kandidat dengan “or” harus dipecah menjadi keputusan AssetSpec terpisah sebelum generation; jangan membuat satu asset yang mencampurkan dua makanan.

Pilot P0 yang disarankan adalah 12 country briefs, masing-masing dengan tiga konsep non-identik:

| Concept family | Contoh output | Tujuan |
|---|---|---|
| Dish object | satu piring/mangkuk/produk makanan, isolated, no text | Menguji recognizability dan buyer utility |
| Ingredient identity | bahan utama, bumbu, condiment, atau komponen yang terlihat | Menguji local specificity dan modularity |
| Preparation/material study | adonan, saus, fermentasi, spice paste, vessel, atau teknik tanpa orang | Menguji storytelling tanpa people release |

Pilot tidak berarti 36 variasi seed/crop. Tiga konsep hanya sah bila fungsi, subject, atau komposisinya berbeda. Similarity clustering dan portfolio diversity check harus dijalankan sebelum asset dipertimbangkan untuk upload.

### 4.2 Prioritas Indonesia

P0 Indonesia terdiri atas **rendang**, **sambal sebagai family yang harus dipecah per varian**, **pempek**, **gudeg**, **gado-gado**, **sate**, **soto**, dan **nasi goreng**. P0 dipilih bukan karena semua hidangan itu memiliki demand yang terbukti, tetapi karena namanya cukup recognizable, bentuk/warna/komponen dapat dibedakan, dan buyer job seperti recipe, menu, tourism, packaging, atau food editorial dapat dijelaskan. `Sambal` bukan satu asset; ia adalah collection family dengan region, method, dan secondary ingredient sebagai differentiator.

P1 Indonesia mencakup ayam betutu, ayam taliwang, andaliman/arsik, tempoyak, oncom/karedok, tempe/sambal tumpang, rawon, rujak cingur, coto Makassar, tinutuan/cakalang, papeda/kuah kuning, dan beberapa candidate regional lain. Semua P1 yang belum memiliki source lokal di CSV harus dianggap **research-gated**. P2 berisi snack, staple, porridge, dan regional foods yang menarik secara visual tetapi membutuhkan local-source verification atau konsultasi komunitas.

## 5. Asset contract untuk agent berikutnya

Setiap candidate harus diubah menjadi satu `AssetSpec` dengan field minimal berikut. Field ini sengaja selaras dengan prinsip Stockforge tentang buyer job, provenance, QA, dan standalone production.

```text
asset_id
country
region_or_city
food_name_native
food_name_en
food_family
candidate_priority
source_urls
source_confidence
heritage_claim_level       # none | general | regional | ritual; ritual requires stronger evidence
buyer_jobs
subject_scope              # one dish | one ingredient | one process/material | people/scene
visual_signature
allowed_props
forbidden_elements         # text, logo, brand, fake label, unrelated props, etc.
format_route               # JPEG first; PNG/SVG only if separately authorized
metadata_language
metadata_title_draft
metadata_keywords_top10
metadata_keywords_secondary
ai_disclosure_required
model_release_required
property_release_required
cultural_review_required
qa_flags
similarity_cluster_id
status                     # research | brief | dry-run | human-review | rejected | approved-for-next-gate
```

### 5.1 Prompt contract

Prompt harus menyebut subject secara spesifik, tetapi tidak menggunakan nama artis, orang nyata, karakter fiksi, brand, restoran, atau karya berhak cipta. Untuk tahap awal, gunakan formula: **[food name] + [region only if verified] + [visible ingredients/technique] + [commercial composition] + [clean background] + [no text/no brand]**. Jangan menambahkan kata “authentic” kecuali brief memiliki evidence dan hasil visual memang tidak mengklaim satu-satunya versi autentik.

Untuk ritual, festival, pakaian, rumah adat, market, atau manusia, agent harus membuat brief baru. Jangan menempelkan props etnik secara acak pada piring makanan. `Cultural review required=true` bila asset menampilkan simbol sakral, ritual, komunitas tertentu, indigenous identity, religious practice, atau klaim sejarah.

### 5.2 Metadata contract

Gunakan satu bahasa metadata secara konsisten, idealnya English untuk jangkauan global, dengan nama makanan lokal hanya bila merupakan nama yang benar dan relevan. Title harus ringkas dan deskriptif. Sepuluh keyword pertama harus memuat subject inti, nama makanan, negara/region yang terlihat atau terverifikasi, dan bentuk/teknik utama. Keyword berikutnya boleh memuat ingredient, cuisine, recipe, menu, tourism, food preparation, atau cultural food hanya bila image mendukungnya.

Contoh title untuk asset yang memang terlihat: `Pempek Palembang fish and tapioca dumpling with cuko sauce`. Contoh top keywords: `pempek, Palembang, fish dumpling, tapioca, cuko sauce, Indonesian food, traditional food, savory snack, food preparation, isolated`. Jangan menambahkan `healthy`, `organic`, `authentic`, `street market`, `family`, `festival`, `halal`, `vegan`, atau `tourism` bila tidak benar-benar didukung subject atau brief. Kategori default untuk food object adalah `Food`; `Culture and religion` atau `Travel` hanya bila context-nya nyata dan menjadi subject.

## 6. Cultural authenticity dan risk framework

Risiko utama sistem ini bukan hanya deformasi visual. Risiko lain adalah **context collapse**, yaitu menjadikan makanan dari komunitas tertentu sebagai props generik tanpa wilayah, sejarah, atau variasi; **false authenticity**, yaitu menyajikan satu versi buatan model sebagai satu-satunya versi asli; **ownership simplification**, yaitu menghapus fakta bahwa beberapa makanan memiliki lintasan lintas batas dan beberapa varian hidup berdampingan; serta **ritual extraction**, yaitu memakai simbol sakral untuk dekorasi marketing.

| Risiko | Contoh failure | Guardrail |
|---|---|---|
| Salah identitas makanan | Papeda dibuat seperti nasi, pempek dibuat seperti dumpling generik | Ingredient/shape QA dan sumber lokal |
| Variasi regional dihapus | Semua sambal diberi label sambal terasi Jawa | Tambahkan region, method, dan secondary ingredient |
| Klaim asal eksklusif | Shared dish diberi label sebagai milik satu negara tanpa sumber | Pakai “regional variation” atau “shared culinary tradition” |
| Ritual dijadikan dekorasi | Simbol upacara ditempel pada menu biasa | Pisahkan dish object dari ritual brief |
| People/property risk | Penjual, restoran, rumah adat, signage generatif | Hindari di P0; releases dan review untuk scene |
| Keyword spamming | Semua asset batch diberi semua negara dan semua dish | Metadata case-by-case dan top-10 relevance |
| AI artifact | Teks palsu, label, tangan, alat, anatomi makanan salah | No text/no label; QA crop dan reviewer |
| Food claim | “healthy”, “healing”, “organic”, “halal”, “vegan” tanpa basis | Hapus claim atau verifikasi dengan source khusus |

UNESCO menyediakan nomination files, consent of communities, inventories, dan deskripsi praktik. Itu dapat menjadi evidence budaya, tetapi bukan lisensi bebas untuk menyalin foto, memakai simbol sakral, atau mengklaim endorsement UNESCO. Adobe tetap mensyaratkan hak komersial dari tool dan kepatuhan contributor agreement [15] [16].

## 7. Workflow agent lanjutan

Agent berikutnya harus memulai dari `docs/README.md` dan `docs/STATUS.md`. File ini dipakai bila memilih candidate makanan; katalog, sumber, dan risk notes harus dibaca untuk candidate tersebut. Agent tidak boleh langsung melakukan generation hanya karena kandidat memiliki tier P0.

| Fase | Input | Output wajib | Gate |
|---|---|---|---|
| 1. Source validation | CSV row + URLs | verified food brief, transliteration, region, confidence | dua sumber kuat atau satu sumber primer yang memadai |
| 2. Buyer brief | verified food brief | buyer job, composition, route, title hypothesis | fungsi komunikasi jelas |
| 3. AssetSpec | brief | prompt/negative prompt, metadata draft, QA flags | no brand/text/unsupported claims |
| 4. Dry-run | AssetSpec | one provider dry-run or local preflight record | bukan batch generation |
| 5. Human review | preview | accept/reject and reasons | reviewer sees food identity and artefacts |
| 6. Similarity/portfolio review | accepted preview | cluster and diversity record | no near-duplicate spam |
| 7. Submission readiness | accepted asset | metadata/release/policy package | manual authorization remains required |

Priority should be recalculated when evidence changes. A P0 row with weak local attribution must be downgraded to P1 or P2. A P2 row can be upgraded only after provenance and use case improve; not merely because an image looks attractive.

## 8. Recommended continuation backlog

Pertama, selesaikan source validation untuk 12 P0 global dan 8 P0 Indonesia, terutama kandidat yang memiliki beberapa pilihan dish atau shared regional lineage. Kedua, buat `AssetSpec` hanya untuk satu candidate per iteration dan tambahkan explicit `source_urls` serta `heritage_claim_level`. Ketiga, buat 12 pilot briefs dengan tiga asset families, lalu jalankan dry-run dan human review sebelum membangun batch. Keempat, tambahkan remaining countries menggunakan schema global yang sama, tetapi jangan menyalin dish yang sama ke banyak negara tanpa country-specific variation. Kelima, setelah 24–36 pilot concepts direview, baru putuskan apakah field, weighting, dan tier perlu diubah.

## 9. File dalam branch ini

| File | Fungsi |
|---|---|
| `docs/research/TRADITIONAL_FOOD_GLOBAL_ASSET_RESEARCH_2026-08-26.md` | Dokumen utama, methodology, priorities, prompt/metadata/policy guardrails, handoff |
| `docs/archive/2026-08-26/research/WORKING_NOTES_TRADITIONAL_FOOD_NICHES_2026-08-26.md` | Provenance notes dan temuan awal selama riset; archive only |
| `data/research/global_traditional_food_asset_catalog.csv` | 63 global anchor candidates dengan tier dan risk notes |
| `data/research/indonesia_regional_food_asset_candidates.csv` | 32 Indonesian regional candidates |
| `data/research/food_catalog_summary.json` | Ringkasan row count, tier, confidence hasil validasi |
| `scripts/analyze_food_catalog.py` | Pemeriksaan reproducible untuk CSV schema dan count |

## References

[1]: https://link.springer.com/article/10.1186/s42779-019-0009-3 "Indonesian food culture mapping: a starter contribution to promote Indonesian culinary tourism"
[2]: https://ich.unesco.org/en/RL/washoku-traditional-dietary-cultures-of-the-japanese-notably-for-the-celebration-of-new-year-00869 "Washoku, traditional dietary cultures of the Japanese"
[3]: https://ich.unesco.org/en/RL/kimjang-making-and-sharing-kimchi-in-the-republic-of-korea-00881 "Kimjang, making and sharing kimchi in the Republic of Korea"
[4]: https://ich.unesco.org/en/RL/traditional-mexican-cuisine-ancestral-ongoing-community-culture-the-michoacan-paradigm-00400 "Traditional Mexican cuisine"
[5]: https://ich.unesco.org/en/RL/gastronomic-meal-of-the-french-00437 "Gastronomic meal of the French"
[6]: https://ich.unesco.org/en/RL/art-of-neapolitan-pizzaiuolo-00722 "Art of Neapolitan Pizzaiuolo"
[7]: https://ich.unesco.org/en/RL/tomyum-kung-01879 "Tomyum Kung"
[8]: https://ich.unesco.org/en/RL/mediterranean-diet-00884 "Mediterranean diet"
[9]: https://stock.adobe.com/pages/artisthub/get-started/create-stock-content-that-sells-stock-contributor-guide-pt-1 "Creating What’s In Demand — Adobe Stock Artist Hub"
[10]: https://stock.adobe.com/pages/artisthub/get-started/photo-video-metadata-stock-contributor-guide-pt-3 "Maximize Metadata to Get Discovered — Adobe Stock Artist Hub"
[11]: https://helpx.adobe.com/stock/contributor/content-policies-guidelines/metadata/choose-right-category-content.html "Choose the right category for your content — Adobe Stock Help"
[12]: https://link.springer.com/article/10.1186/s42779-022-00142-7 "Diversity of sambals, traditional Indonesian chili pastes"
[13]: https://link.springer.com/article/10.1186/s42779-023-00209-z "Pempek Palembang: history, food making tradition, and ethnic identity"
[14]: https://pmc.ncbi.nlm.nih.gov/articles/PMC8415227/ "The Food Identity of Countries Differs Between Younger and Older Generations"
[15]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html "Adobe Stock generative AI content guidelines"
[16]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/submit-generative-ai-content.html "Submit generative AI content — Adobe Stock Help"
