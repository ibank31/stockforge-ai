# StockForge — Keputusan niche dan format

**Tanggal:** 24 Agustus 2026  
**Status:** keputusan riset lanjutan; bukan janji penjualan

## Ringkasan keputusan

StockForge tidak boleh merutekan seluruh hasil ke JPEG, PNG, atau SVG secara mekanis. Format harus mengikuti **buyer job**, kebutuhan editability/transparency, dan kemampuan produksi yang benar-benar sudah diverifikasi.

Keputusan kerja saat ini:

| Buyer job | Lane | Status produksi |
|---|---|---|
| Scene konseptual, cinematic, surreal, seasonal, workplace, nature | JPEG raster | **Verified production** melalui jalur raster yang sudah terbukti |
| Isolated object, technical clip-art, icon, badge, food/produce, geometric element | Native SVG | **Locally ready; portal belum diverifikasi** |
| Cutout, overlay, sticker, isolated painterly object | PNG dengan real alpha | **Blocked** sampai alpha producer dan portal validation tersedia |
| Seamless pattern | SVG atau raster sesuai material | **Blocked per candidate** sampai edge-to-edge seam test lulus |
| Quote/typography graphic | Deterministic text-safe layout atau outlined SVG | **Research only** |
| Video/motion background | Belum ditetapkan | **Research only** |

## Bukti sosial dan marketplace yang dipertahankan

Handoff sesi sebelumnya mencatat dua kelompok sinyal. Kelompok pertama menampilkan karya konseptual/illustrative seperti surreal landscape, urban fantasy, superhero dogs, seasonal scene, warehouse, nature, dan artwork dengan lighting/depth. Kelompok kedua menampilkan isolated object/clip-art, technical component, food/produce, badge, pattern, dan decorative element. Fakta ini dipakai sebagai **sinyal buyer job**, bukan sebagai bukti bahwa format asli asset adalah PNG/SVG atau bahwa nominal screenshot dapat dipetakan ke satu file.

Nominal earnings dan engagement sosial tidak boleh diperlakukan sebagai download count, licence tier, asset ID, format asli, atau repeatable demand. Tiga original attachment yang dibatasi oleh handoff tidak dibuka ulang. Kesimpulan yang menggunakan fakta tersebut tetap berstatus evidence awal dengan confidence terbatas.

## Bukti publik yang sudah diverifikasi

Adobe menjelaskan bahwa PNG transparan digunakan sebagai utility asset yang mengomunikasikan satu ide dan ditempatkan ke desain yang lebih besar. Contohnya isolated object, overlay, texture, pattern, icon, infographic, layout, character set, dan element set. Syarat teknis yang relevan adalah background none, sRGB, file maksimal 45 MB, resolusi 4–100 MP, serta transparency yang nyata.[1]

Adobe juga menerima vector dalam AI, EPS, dan SVG, dan menyatakan bahwa vector transparan dapat menghasilkan PNG transparan otomatis untuk customer. Karena itu StockForge tidak perlu membuat duplikat PNG dari SVG yang sama. Vector harus genuine editable geometry, bukan raster yang di-trace dangkal.[2]

Shutterstock menekankan path yang bersih dan terorganisasi, pengendalian rasterization/bitmap, extra vector objects, font, warna, serta pengujian seamless design. Pattern yang terlihat memiliki boundary ketika ditile tidak boleh diberi label seamless.[3]

Adobe Creative Trends 2026 mengarahkan perhatian pada karya yang relatable, relevant, dan useful, dengan empat sinyal visual: `All the Feels`, `Connectioneering`, `Surreal Silliness`, dan `Local Flavor`. Adobe menyebut sumbernya mencakup commercial campaigns, customer feedback, dan search history, tetapi angka tren agregat tidak dapat diubah menjadi prediksi penjualan satu niche.[4]

Adobe mewajibkan hak komersial yang memadai untuk tool generative AI, disclosure `Created using generative AI tools`, serta melarang nama artist, real people, fictional characters, creative works berhak cipta, third-party IP, dan actual newsworthy event dalam prompt/title/keyword.[5]

## Prioritas mesin

Prioritas pertama adalah memperluas **native SVG lane** untuk object/icon/technical families yang dapat dibangun sebagai path lokal: silhouette object, technical component, food/produce icon, badge, simple character, dan geometric element. Jalur ini tidak memakai GPU dan harus melewati structural gate.

Prioritas kedua adalah mempertahankan **JPEG scene lane** dengan pre-GPU gate, prompt compiler, layout contract, visual QC, deduplication, dan hanya satu preview per hypothesis yang jelas. Sinyal `Surreal Silliness`, tactile material, dan local specificity boleh menjadi hypothesis, bukan alasan untuk batch generation.

Prioritas ketiga adalah membangun **PNG alpha lane** secara bertahap: real alpha producer, checkerboard preview hanya untuk review, anti-fringe check, excess-canvas trim, sRGB/decodability check, Adobe PNG gate, dan satu validasi portal terkontrol. Sebelum semua itu tersedia, route harus tetap ditolak.

Prioritas keempat adalah seam gate untuk pattern. Kandidat raster yang mengaku seamless harus memiliki edge continuity horizontal dan vertikal; hasil gate hanya menyatakan continuity, bukan commercial quality atau marketplace acceptance.

## Alokasi eksperimen awal

Sebagai alokasi engineering hypothesis, bukan forecast sales, eksperimen berikutnya dapat memakai sekitar **50% native SVG object/icon/technical**, **35% JPEG conceptual/seasonal/commercial scenes**, dan **15% pattern/background research**. PNG alpha belum masuk lane produksi.

Setiap GPU job harus memiliki buyer hypothesis yang jelas dan menghasilkan selected master, concept experiment, atau diagnostic evidence. Seed-only retry, batch besar, dan upscale terhadap preview lemah tetap dilarang.

## Status implementasi yang diteruskan

Mesin saat ini sudah memiliki `AssetSpec`, `format_router`, `native_vector`, `adobe_png_gate`, Android export separation, provenance, dan provider routing. Perubahan lanjutan pada sesi ini bersifat additive: menambahkan catatan riset dan deterministic raster seam gate, tanpa menghapus atau mengubah jalur JPEG, SVG, atau PNG gate yang sudah ada.

## Referensi

[1]: https://helpx.adobe.com/ie/stock/contributor/help/png-with-transparency.html "Adobe Stock — PNG files with transparency"
[2]: https://helpx.adobe.com/ie/stock/contributor/help/vector-requirements.html "Adobe Stock — Content Guidelines: Vectors"
[3]: https://submit.shutterstock.com/help/en/articles/10594650-vector-and-illustration-quality-requirements "Shutterstock Contributor — Vector and Illustration Quality Requirements"
[4]: https://blog.adobe.com/en/publish/2026/01/08/how-creators-leveraging-adobe-2026-creative-trends "Adobe — How creators are leveraging Adobe's 2026 Creative Trends"
[5]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html "Adobe Stock — Generative AI content guidelines"
