# Riset lanjutan StockForge — 2026-08-24

## Sumber resmi Adobe: PNG dengan transparansi

URL: https://helpx.adobe.com/ie/stock/contributor/help/png-with-transparency.html

Fakta yang terbaca:

- Adobe menjelaskan bahwa utility assets yang menyampaikan satu ide dengan cepat dapat dipakai sebagai komponen desain yang lebih besar.
- Contoh buyer use yang disebut: isolated object seperti lightbulb untuk web page, vintage frame di atas foto, dan geometric graphic sebagai video overlay.
- Use case yang disebut mencakup website, social media/layout, art/collage, overlay, isolated objects, backgrounds, patterns, textures, banners, mockups, icon/logo, infographics, layouts, letter sets, character sets, dan element sets.
- PNG transparan mendukung opacity/transparency dan cocok untuk aset yang dilayer di atas background lain.
- Syarat dasar PNG Adobe: background none, color space sRGB, maksimum 45 MB, resolusi minimum 4 MP, maksimum 100 MP.
- Best practice: upload benar-benar transparan, memberi unique customer value, crop untuk meminimalkan ruang kosong, mengisolasi individual objects/elements/people, dan meminimalkan shadow.
- Larangan penting: jangan mengunggah file identik sebagai PNG dan JPEG; jangan memakai checkerboard/colored background sebagai pura-pura transparansi; jangan memakai nama artist, real known people, fictional characters, atau creative works berhak cipta pada keyword/title.

Implikasi aman untuk StockForge:

1. Lane PNG transparan memang didukung buyer use resmi, tetapi harus tetap diblokir sampai alpha channel nyata, edge/fringe check, sRGB, crop/trim, dan portal validation tersedia.
2. Asset isolated object adalah buyer job yang valid, bukan bukti bahwa semua thumbnail putih harus dirutekan ke PNG.
3. Jangan membuat duplikat visual JPEG dan PNG. Format dipilih dari buyer job dan unique value.
4. Native SVG tetap relevan untuk objek geometric/editable; PNG dipakai untuk raster utility asset yang benar-benar membutuhkan transparency.

## Sumber resmi Adobe: vector

URL: https://helpx.adobe.com/ie/stock/contributor/help/vector-requirements.html

Fakta yang terbaca:

- Adobe menerima vector dalam AI, EPS, dan SVG; vector tidak boleh diunggah sebagai JPEG.
- Untuk vector transparan atau flat-color, Adobe otomatis memberi customer PNG transparan; contributor tidak perlu mengunggah duplikat PNG.
- Adobe menekankan groups/layers yang logis, tidak flattened, font di-outline, dan menghindari linked/rasterized assets.
- Adobe menyebut vector dipakai untuk logo/branding, digital illustration, packaging, motion graphics, dan karya yang perlu diskalakan atau warnanya diubah.
- Ukuran yang direkomendasikan berbeda menurut buyer use: design elements/sets (icons, logos, patterns, characters, lettering) 1000–4800 px; scenes/illustrations 1200–4800 px; small digital designs/social media sets 1000–3600 px; large digital designs 1200–7200 px.
- Adobe melarang logo/trademark/company names/brand names dan meminta perhatian pada legal rights.
- Adobe menyarankan hanya memilih vector terbaik dan menghindari spam/variasi yang tidak memberi nilai unik.
- Keyword/title harus akurat; 10 keyword pertama paling diprioritaskan dan istilah seperti “vector”/“illustration” tidak boleh dipakai sebagai pengganti deskripsi visual bila aturan melarangnya.

Implikasi aman untuk StockForge:

1. Native SVG bukan sekadar format ekspor; file harus genuine editable vector dan tidak meng-embed raster.
2. Satu SVG transparan sudah memiliki jalur customer PNG otomatis di Adobe, sehingga membuat PNG duplikat dapat melanggar prinsip unique value.
3. Lane SVG paling cocok untuk icons, objects, patterns, characters sederhana, dan design elements yang dapat dibuat sebagai geometry/path lokal.
4. Builder perlu menjaga ukuran artboard, struktur path, absence of raster/script/external links, dan metadata visual yang akurat.

## Sumber resmi Shutterstock: vector dan illustration quality

URL: https://submit.shutterstock.com/help/en/articles/10594650-vector-and-illustration-quality-requirements

Fakta yang terbaca:

- Shutterstock menilai submission melalui pemeriksaan compliance, metadata, dan quality; kegagalan dapat menyebabkan penolakan.
- Path vector dan ilustrasi harus bersih, terorganisasi, dan mudah dipahami agar usable bagi customer.
- “Seamless design” berarti asset memang dimaksudkan untuk diduplikasi menjadi pattern besar yang halus tanpa boundary terlihat pada semua sisi.
- Pattern dengan visible edges yang dimaksudkan seamless dianggap tidak sesuai untuk marketplace.
- Halaman juga memuat kategori masalah yang perlu diawasi: rasterization, design composition, gradient/blend, bitmap, color mismatch, color profiles, extra vector objects, EPS requirements, inaccessible objects, dan font requirements.

Implikasi aman untuk StockForge:

1. Four-direction tile/boundary test wajib dipisahkan sebagai gate, bukan menganggap square preview sebagai seamless.
2. Native SVG builder perlu structural QA untuk path, bitmap/raster embed, extra objects, font/text behavior, dan color profile/output assumptions.
3. Pattern yang gagal seam test harus diklasifikasikan sebagai decorative square/background biasa, bukan seamless pattern.

## Sumber resmi Adobe: Generative AI content guidelines

URL: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html

Fakta yang terbaca:

- Contributor harus memiliki semua hak yang diperlukan untuk melisensikan konten generative AI secara komersial dan perlu memeriksa terms tool yang digunakan.
- Prompt, title, dan keyword tidak boleh memuat nama artist, real people, fictional characters, creative works yang masih dilindungi, government agencies, third-party IP, atau deskripsi yang menyiratkan actual newsworthy event.
- Konten generative AI wajib diberi label `Created using generative AI tools` di Contributor Portal.
- Jika menampilkan fictional person/property, checkbox `People and Property are fictional` diperlukan; jika tidak ada recognizable people/property, release tidak diperlukan.
- Konten yang dibuat, ditambah, atau diubah secara generative AI pada primary subject tetap harus dilabeli; aturan label tidak hilang hanya karena hasil akhir dirapikan.

Implikasi aman untuk StockForge:

1. Rights-safe prompt firewall harus tetap berada sebelum GPU.
2. Metadata generator tidak boleh menyalin istilah model, artist, brand, atau workflow ke keyword visual.
3. Output package harus menyimpan status GenAI disclosure dan release decision sebagai metadata internal, tetapi tidak menganggapnya sebagai keyword.
4. SVG deterministic lokal dapat memiliki aturan berbeda dari raster GenAI, namun jika SVG memakai hasil generative raster atau primary subject generative, policy label dan rights tetap berlaku.

## Sumber tren kreatif Adobe 2026

URL: https://blog.adobe.com/en/publish/2026/01/08/how-creators-leveraging-adobe-2026-creative-trends

Fakta yang terbaca:

- Adobe menekankan bahwa audience menginginkan karya yang relatable, relevant, dan genuinely useful, bukan hanya visually attractive.
- Empat koleksi tren yang disebut: `All the Feels`, `Connectioneering`, `Surreal Silliness`, dan `Local Flavor`.
- Adobe menyebut tren ditentukan dari commercial campaigns dan creative projects lintas sektor, customer feedback dari Creative Cloud communities, serta search history.
- Adobe melaporkan pencarian keyword terkait tren 2026 meningkat 150% sejak 2024; ini adalah sinyal tren agregat Adobe, bukan bukti penjualan per asset atau format tertentu.
- `Surreal Silliness` mendukung continued research untuk conceptual/surreal scenes; `Local Flavor` mendukung regional specificity/authentic perspective; `All the Feels` mendukung tactile/material/multisensory visual language; `Connectioneering` mendukung human connection, tetapi jalur people memiliki release/policy burden.

Implikasi aman:

1. Scene JPEG yang sudah menjadi lane verified dapat memakai hypothesis visual surreal, tactile/material, dan local specificity tanpa menyebutnya sebagai jaminan sales.
2. Local specificity harus diwujudkan melalui pengalaman/visual context yang rights-safe, bukan meniru artist atau brand.
3. People/connection lane jangan diprioritaskan untuk generator awal karena model/property release dan policy complexity lebih tinggi.
4. Data tren dipakai untuk menaikkan prioritas hypothesis riset, bukan untuk langsung menaikkan kuota GPU atau mengklaim demand terbukti.

## Shutterstock Trends page

URL: https://www.shutterstock.com/trends

Halaman publik tidak dapat dibaca secara reliable pada sesi ini karena hanya menampilkan `Please enable JS and disable any ad blocker`. Tidak ada angka tren yang dipakai sebagai fakta. Sumber ini tidak boleh dijadikan dasar keputusan sampai data dapat dibaca dari halaman atau API publik yang dapat diverifikasi.
