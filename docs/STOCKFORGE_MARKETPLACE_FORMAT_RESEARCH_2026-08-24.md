# StockForge AI — Riset Marketplace, Niche, dan Routing Format

**Tanggal:** 24 Agustus 2026  
**Status:** Riset selesai untuk screenshot turunan yang tersedia; tanpa generasi gambar, GPU, upload, atau perubahan portal.

## Ringkasan eksekutif

Analisis tidak sia-sia. Catatan bukti berhasil dipulihkan dan pembacaan tile turunan untuk screenshot `1000801962`–`1000801991` telah diselesaikan. Tiga original attachment `1000801961`, `1000801960`, dan `1000801959` tidak dibuka ulang sesuai batas instruksi, tetapi fakta awalnya tetap dicatat sebagai evidence tingkat rendah.

Temuan terpenting bukan bahwa satu niche pasti laku. Temuannya adalah adanya **tiga pekerjaan pembeli yang berbeda**: karya konseptual sinematik, elemen objek/clip-art yang langsung ditempel ke desain, serta pattern/background. Karena itu StockForge tidak boleh memaksa semua brief menjadi JPEG landscape.

Keputusan routing yang aman adalah sebagai berikut. **JPEG raster** tetap menjadi jalur generative aktif untuk scene, landscape, fantasy, seasonal image, warehouse, nature, dan artwork dengan pencahayaan kompleks. **Native SVG** menjadi prioritas investasi mesin untuk ikon, objek teknis, objek makanan, badge, karakter sederhana, dan pattern geometris yang dapat dibangun secara deterministik. **PNG transparan** adalah jalur buyer yang masuk akal untuk cutout, overlay, sticker, dan isolated object, tetapi belum boleh diaktifkan sampai producer alpha nyata dan upload portal tervalidasi. **Text-bearing quote graphics** tidak diprioritaskan karena screenshot hanya menunjukkan satu contoh dan generative text memiliki risiko legibility serta policy. **Pattern** hanya boleh dirutekan sebagai pattern bila lolos uji seamless edge-to-edge.

> Bukti pendapatan menunjukkan kemungkinan adanya pasar, tetapi tidak cukup untuk membuktikan format asli, asset ID, jumlah download, licence tier, atau repeatability.

## 1. Batas evidence

Screenshot Adobe memakai label `Your best seller` dan nominal `Yesterday you made`. Nominal tersebut adalah pendapatan harian yang terlihat pada screenshot, bukan revenue yang dapat dipetakan secara aman ke satu file. Menurut panduan royalty Adobe, rate dan payout dapat bergantung pada tipe lisensi serta buyer plan; karena itu nominal harian tidak boleh dibalik menjadi jumlah download atau format asset.

Kemiripan nama `klakon` dengan profil publik `klakonstudio` tetap **belum terverifikasi**. Profil Adobe dan Shutterstock yang ditemukan adalah lead publik, bukan bukti bahwa screenshot tersebut berasal dari akun yang sama.

## 2. Evidence screenshot yang tersimpan

| Kelompok bukti | Contoh visible motif | Nilai untuk StockForge | Confidence |
|---|---|---|---|
| `klakon`, scene konseptual | Surreal landscape `$15.94`, urban fantasy `$15.89`, superhero dogs `$17.63`, typography-like graphic `$28.00` | Ada sinyal untuk scene/illustration JPEG, tetapi tidak ada format asli atau asset ID. | Sedang untuk motif; rendah untuk format. |
| `River` | Kelompok alat gambar berwarna, `$1,276` | Menunjukkan bahwa object/icon illustration dapat muncul sebagai best seller pada akun lain. Tidak boleh digabung dengan `klakon`. | Sedang untuk screenshot; rendah untuk generalisasi. |
| `Achmad Rizal` | Fiery horse/calendar `$70.16`, Santa seasonal `$31.39`, warehouse `$22.28`, moss/nature `$16.64`, warehouse `$14.19` | Mendukung buyer jobs untuk seasonal, commercial/workplace, nature, dan dramatic raster scenes. | Sedang untuk motif; rendah untuk format. |
| Isolated illustrated objects | Fitness woman, rotor, camping badge, aviator cap, ham, spark plug, uniform, rocket, duffel, engine, tomatoes, strawberries | Ini adalah sinyal kuat bahwa object/clip-art family layak diuji, terutama sebagai native SVG atau future PNG alpha. | Sedang untuk motif; rendah untuk format. |
| Pattern/background | Wavy abstract bands, raindrops, floral illustration, children’s pattern example | Mendukung lane pattern/background, tetapi pattern harus diuji seamless dan tidak otomatis berarti SVG. | Sedang untuk motif; rendah untuk repeatability. |
| Text-bearing graphic | Quote `Happiness looks good on you` dan cursive graphic | Menunjukkan kemungkinan use case dekoratif, tetapi text accuracy, rights, dan legibility membuatnya bukan prioritas awal generative route. | Sedang untuk visual; rendah untuk strategy. |
| Tiga original attachment | Deer `$11.51`, UFO `$14.99`, lifetime `$461.23` dan `1,341 Licensed downloads` | Hanya dipakai sebagai fakta awal yang pengguna telah berikan; tidak dibuka ulang. | Rendah–sedang. |

## 3. Pola niche yang dapat dipertanggungjawabkan

### A. Isolated object illustration dan technical clip-art

Banyak thumbnail yang terlihat berupa satu objek dengan latar putih: rotor/armature, spark-plug-like component, motorcycle engine, aviator cap, travel bag, uniform, camping badge, food, dan drawing tools. Ini bukan bukti bahwa file aslinya transparan atau vector, tetapi merupakan sinyal buyer job yang jelas: objek dimasukkan ke presentasi, artikel, packaging, educational material, social post, atau composition lain.

Niche ini paling cocok untuk **native SVG** bila objek dapat dibangun dari bentuk, path, stroke, dan warna yang terkontrol. Untuk objek yang memerlukan tekstur painterly atau bentuk organik sulit, gunakan **JPEG raster** terlebih dahulu. PNG alpha baru dipakai ketika subjek benar-benar harus diletakkan di atas background lain dan alpha dapat dibuktikan secara teknis.

### B. Scene dan conceptual illustration

Surreal landscape, urban fantasy, superhero dogs, fiery horse, Santa, warehouse, moss, dan beberapa artwork lain lebih cocok dipahami sebagai scene atau illustration dengan lighting dan depth. Jalur paling realistis untuk produksi gratis yang sudah terverifikasi adalah **JPEG raster melalui Z-Image Turbo** setelah gate pra-GPU.

Jangan memaksa scene kompleks menjadi SVG. Trace otomatis akan menghasilkan path yang berat, tidak rapi, dan berisiko menyesatkan buyer tentang editability. Bila scene memiliki ruang kosong yang sengaja dibuat untuk copy, ruang tersebut harus menjadi bagian dari brief dan gate komposisi, bukan efek samping canvas.

### C. Pattern, background, dan decorative elements

Wavy bands, raindrops, flowers, dan children’s pattern menunjukkan lane yang berbeda dari isolated object. Buyer dapat membutuhkan tile yang dapat diulang, background luas, atau elemen dekoratif. **Square** adalah format komposisi yang masuk akal untuk pattern preview, tetapi square saja tidak membuktikan seamlessness.

StockForge harus memiliki uji yang menyalin tile pada empat arah dan memeriksa boundary. Jika terdapat seam, brief tidak boleh diberi label seamless pattern. Pattern geometris sederhana layak diarahkan ke native SVG; watercolour atau painterly pattern lebih aman sebagai JPEG/PNG berdasarkan kebutuhan transparency.

### D. Quote graphics dan typography

Satu screenshot menampilkan quote square dengan daisy, dan satu lagi graphic hitam dengan lettering kecil. Ini menarik sebagai market motif, tetapi bukan prioritas mesin generative karena teks dapat salah, tidak legible, atau menyerupai karya pihak lain. Jika suatu saat lane ini dibangun, sebaiknya route ke deterministic editable layout atau outlined vector dengan teks yang ditentukan secara eksplisit, bukan mengandalkan generator untuk mengeja kalimat panjang.

## 4. Bukti buyer-use dari sumber resmi

Adobe menjelaskan bahwa customer mencari asset PNG transparan yang mengomunikasikan satu ide dan dipakai sebagai komponen desain yang lebih besar. Adobe memberi contoh isolated lightbulb, vintage frame, dan geometric overlay, serta menyebut website, social media, collage, overlay, texture, mockup, pattern, icon, infographic, layout, letter set, character set, dan element collection sebagai use case.[1]

Adobe juga menjelaskan bahwa vector dipakai untuk logo/branding, digital illustration, product packaging, motion graphics, dan karya yang perlu diskalakan atau diubah warnanya. Adobe menerima AI, EPS, dan SVG. Untuk vector dengan background transparan atau flat-colour, Adobe menyatakan bahwa PNG transparan dibuat otomatis untuk customer, sehingga contributor tidak perlu mengunggah duplikat PNG.[2]

Implikasinya penting: **native vector yang genuine dapat melayani dua buyer job sekaligus**, yaitu buyer yang memerlukan file editable dan buyer yang memerlukan PNG praktis. Namun hal itu hanya berlaku jika file benar-benar vector, bukan raster generative yang ditrace secara dangkal.

Shutterstock menekankan path yang bersih dan terorganisasi, komposisi yang usable, text yang legible, penghapusan extra objects, serta expanded objects. Untuk seamless design, setiap sisi harus dapat diulang tanpa boundary yang terlihat. Shutterstock juga memiliki aturan EPS 8/EPS 10 untuk vector submission.[3] Ini menguatkan kebutuhan gate lokal untuk editability, seam, extra object, dan text safety.

Adobe mewajibkan contributor memeriksa hak submission dari tool generative yang digunakan dan memilih label `Created using generative AI tools` untuk semua konten yang dibuat dengan software generative AI. Adobe juga membatasi artist names, real people, fictional characters, copyrighted creative-work references, third-party IP, dan deskripsi actual newsworthy events dalam prompt/title/keywords.[4]

## 5. Matriks keputusan format

| Buyer job / produk | Format utama | Format sekunder | Status StockForge | Alasan routing |
|---|---|---|---|---|
| Surreal landscape, urban fantasy, dramatic scene | JPEG | — | **Verified production** | Z-Image Turbo sudah terbukti untuk raster; detail dan lighting tidak cocok dipaksa menjadi vector. |
| Seasonal illustration dengan scene dan depth | JPEG | Future PNG bila benar-benar isolated | **Verified JPEG; PNG research only** | Seasonal demand terlihat, tetapi alpha tidak dapat disimpulkan dari thumbnail. |
| Satu objek teknis sederhana, alat, food icon, badge | Native SVG | Future PNG alpha | **Locally ready SVG; portal-unverified** | Bentuk dapat dibangun sebagai path editable; buyer mendapat skalabilitas dan editability. |
| Satu objek organik/painterly yang perlu ditempel ke design | Future PNG alpha | JPEG | **PNG blocked** | Adobe buyer-use evidence kuat, tetapi alpha producer belum siap dan belum portal-verified. |
| Geometric pattern dan icon set | Native SVG | JPEG preview | **Locally ready SVG; seam gate required** | SVG mendukung scaling/editability; pattern harus lulus seamless test. |
| Painterly pattern atau watercolour element | JPEG | Future PNG alpha | **JPEG verified; PNG blocked** | Tekstur organik sulit dibuat native vector dengan rapi. |
| Quote graphic / lettering | Deterministic layout atau outlined SVG | JPEG | **Research only** | Text generative memiliki risiko legibility, rights, dan duplicate-like output. |
| True seamless repeat | SVG atau JPEG/PNG sesuai visual | — | **Research only sampai seam test** | Square bukan sinonim seamless. |
| Video / motion background | Belum ditetapkan | — | **Research only** | Belum ada jalur gratis yang diverifikasi untuk produksi dan QA. |

## 6. Prioritas mesin yang direkomendasikan

| Prioritas | Lane | Investasi yang tepat sekarang | GPU? |
|---:|---|---|---:|
| 1 | Native SVG object/icon/technical | Perluas library deterministic builders, palette, path validation, metadata, dan preview; jangan memakai raster trace sebagai shortcut. | Tidak. |
| 2 | JPEG conceptual scenes | Pertahankan pre-GPU gate, prompt compiler, layout gate, dan satu preview terpilih per hypothesis. | Hanya setelah lolos gate. |
| 3 | PNG transparent cutout | Bangun producer alpha nyata, checkerboard preview, edge/fringe test, canvas trim, Adobe dimension/color gate, lalu satu upload validation. | Tidak untuk engineering; GPU hanya bila source visual diperlukan. |
| 4 | Seamless pattern | Tambahkan four-direction tile test dan boundary diff. | Tidak. |
| 5 | Text/quote assets | Tunda sampai deterministic text-safe route tersedia. | Tidak. |
| 6 | Video | Jangan prioritaskan sebelum ada provider gratis dan jalur QA yang benar-benar terverifikasi. | Tidak. |

## 7. Rekomendasi allocation awal, bukan janji penjualan

Untuk eksperimen portofolio berikutnya, allocation yang rasional adalah sekitar **50% object/icon/technical native SVG**, **35% JPEG conceptual/seasonal/commercial scenes**, dan **15% pattern/background research**. PNG alpha belum dimasukkan sebagai lane produksi sampai pipeline teknis dan portal terbukti. Angka ini adalah alokasi engineering hypothesis, bukan prediksi sales dan bukan klaim bahwa proporsi tersebut akan menghasilkan revenue tertentu.

Object lane dipilih lebih besar bukan karena screenshot membuktikan SVG laku lebih tinggi, melainkan karena evidence memperlihatkan banyak buyer-like isolated object motifs dan mesin lokal sudah dapat membangun SVG sederhana tanpa GPU. Scene JPEG tetap penting karena bukti `klakon` dan `Achmad Rizal` menunjukkan visual cinematic/conceptual yang tidak masuk akal diproduksi sebagai SVG.

## 8. Roadmap no-GPU

Tahap pertama adalah memperkuat data model agar setiap brief memiliki `buyer_job`, `product_kind`, `delivery_format`, `layout_mode`, `alpha_required`, `seamless_required`, dan `source_format_confidence`. Router harus menolak brief jika format dipilih hanya berdasarkan tampilan thumbnail tanpa buyer job yang jelas.

Tahap kedua adalah menyelesaikan native SVG lane dengan builder untuk object silhouettes, technical components, food/produce icons, badges, simple characters, and geometric patterns. Setiap SVG harus lolos pemeriksaan tidak ada raster embed, script, external link, hidden object, live font, atau path yang tidak valid.

Tahap ketiga adalah membangun alpha producer lokal dengan output checkerboard preview, true alpha assertion, anti-fringe check, excess-canvas trim, sRGB check, decodability check, dan Adobe dimension/file-size gate. Setelah itu baru lakukan **satu** validasi portal yang direncanakan; jangan mengunggah batch.

Tahap keempat adalah menghubungkan evidence log ke brief scoring. Motif yang sering muncul boleh menaikkan prioritas riset, tetapi tidak boleh langsung menaikkan prioritas GPU. Hanya kandidat yang memiliki buyer job, format route, rights-safe prompt, layout, dan acceptance gate yang jelas boleh memanggil remote GPU.

Tahap kelima adalah menambahkan report per asset yang membedakan tiga status: **verified production**, **locally ready but portal-unverified**, dan **research only**. Ini mencegah mesin mengemas SVG lokal seolah-olah sudah terbukti diterima Adobe.

## 9. Kesimpulan operasional

Tidak ada dasar yang cukup untuk menyatakan “format terbaik selalu JPEG”, “PNG pasti lebih laku”, atau “SVG pasti menghasilkan royalty lebih tinggi”. Kesimpulan yang didukung evidence adalah bahwa format harus mengikuti pekerjaan pembeli.

Keputusan paling aman sekarang adalah: lanjutkan **JPEG untuk scene kompleks**, investasi utama pada **native SVG untuk isolated object dan technical/icon families**, dan siapkan **PNG alpha sebagai lane berikutnya** setelah producer dan portal tervalidasi. Jangan mengaktifkan `woven-loop` sebagai master sampai jalur alpha benar-benar selesai. Jangan menggunakan screenshot nominal untuk mengatur kuota GPU atau menjanjikan hasil penjualan.

## Referensi

[1]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-pngs/png-files-submission-overview.html "Adobe Stock — PNG files with transparency"
[2]: https://helpx.adobe.com/ca/stock/contributor/help/vector-requirements.html "Adobe Stock — Content Guidelines: Vectors"
[3]: https://submit.shutterstock.com/help/en/articles/10594650-vector-and-illustration-quality-requirements "Shutterstock Contributor — Vector and Illustration Quality Requirements"
[4]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html "Adobe Stock — Generative AI content guidelines"
[5]: https://helpx.adobe.com/stock/contributor/payments-earnings/royalties-pricing/royalty-rates-assets.html "Adobe Stock — Royalty rates"
[6]: https://stock.adobe.com/contributor/211179033/klakonstudio "Adobe Stock — Public contributor lead, unverified"
[7]: https://www.shutterstock.com/g/klakonstudio "Shutterstock — Public contributor lead, unverified"
