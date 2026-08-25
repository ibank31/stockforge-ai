# Riset dan Pemilihan Niche JPEG Baru StockForge

**Tanggal:** 25 Agustus 2026  
**Status:** Hipotesis terpilih untuk dry-run; belum mengotorisasi live generation, finalizer, upload, atau submission.  
**Repository:** `ibank31/stockforge-ai`, branch `main`, HEAD `858e21b`.

## 1. Konfirmasi baseline

Repository telah terhubung dan berhasil di-clone pada branch `main`. HEAD aktual adalah `858e21b`, sesuai baseline eksplisit yang diberikan pengguna. Workflow JPEG yang dipertahankan adalah: market evidence → satu brief → dry-run/pre-GPU gates → satu ZeroGPU preview → review manusia dan mesin → `portfolio evaluate` → `portfolio learning-summary` → master/finalizer hanya setelah review. Upload Adobe tetap manual dan tidak akan dijalankan otomatis.

Dokumen aktif menunjukkan bahwa lane technical mechanical component dengan asset rotor-armature adalah reference workflow yang telah diverifikasi end-to-end, tetapi tetap **promising but unproven**. Lane baru harus berbeda secara material dari rotor-armature dan tidak boleh menjadi variasi seed, crop, warna, atau pseudo-retry. Preflight repository saat ini mensyaratkan raster JPEG sebagai produk terisolasi dengan background putih, tanpa copy-space reserved; karena itu kandidat baru sengaja dirancang sebagai satu objek/cluster terisolasi, bukan scene landscape. Perluasan scene gate tidak dilakukan pada sesi ini.

Terdapat satu ketidaksesuaian metadata: `SESSION_HANDOVER.md` dan `STATUS.md` masih menyebut baseline documentation commit `6d663ec`, sedangkan HEAD repository dan baseline pengguna adalah `858e21b`. Ini dicatat sebagai stale handover metadata dan tidak mengubah keputusan produk.

## 2. Cara membaca evidence

Tidak ada sumber publik yang dapat membuktikan bahwa satu micro-niche stock image pasti memiliki demand tinggi atau mudah dijual. Adobe sendiri menganjurkan contributor memilih niche, mempelajari buyer, memantau tren, dan memikirkan bagaimana asset dipakai pada banner, print, atau komunikasi lain; panduan tersebut adalah content strategy guidance, bukan sales-rate data [1]. Adobe 2026 Creative Trends menyoroti authenticity, sensory/tactile imagery, local specificity, human context, dan playful experimentation, sementara Getty menekankan bahwa visual AI yang generik perlu diganti dengan purpose, accountability, tools, dan human context [2] [3]. Keduanya adalah trend signals, bukan bukti checkout, download, ranking, atau approval.

Evidence supply yang dipakai di sini adalah angka hasil pencarian Adobe Stock pada 25 Agustus 2026. Angka tersebut hanya menjadi **supply/competition proxy pada timestamp tertentu**. Angka yang kecil tidak membuktikan demand; angka yang besar tidak membuktikan bahwa niche tidak dapat dijual.

Evidence buyer job untuk kandidat terpilih berasal dari University of Minnesota Extension dan Royal Horticultural Society. Keduanya menunjukkan bahwa indoor seed starting merupakan kegiatan tutorial/edukasi yang memakai tray, module, compost, seedling, label, dan proses bertahap [4] [5]. Itu memperkuat kejernihan use case visual, tetapi bukan bukti marketplace conversion.

## 3. Shortlist kandidat non-mekanis

Kandidat yang sudah aktif di registry StockForge, seperti `circular_packaging_systems`, tidak dihitung sebagai niche baru. `human_made_collage_elements` juga tidak dipilih karena route PNG true-alpha masih blocked. Kandidat berikut dipilih karena dapat dibuat sebagai JPEG raster, tidak memerlukan people release bila tidak ada manusia/property identifiable, dan dapat diberi buyer job konkret.

| Kandidat | Buyer job yang diuji | Supply proxy Adobe | Production fit | Compliance/IP risk | Seasonal risk | Status |
|---|---|---:|---|---|---|---|
| **Seed-starting tray / indoor seedling propagation** | Visual untuk gardening tutorial, horticulture education, seed-supplier article, atau growing guide | **6.589** hasil untuk `seed starting tray` | Kuat untuk satu isolated square JPEG; objek jelas dan tidak memerlukan scene gate | Rendah–menengah; risiko utama salah label spesies, teks pada packet/label, dan klaim hortikultura | Menengah; dapat dibuat evergreen sebagai propagation, tetapi timing tanam bersifat regional | **Prioritas** |
| Garden tools / planting setup | Visual untuk gardening blog, lawn-care tutorial, atau outdoor retail education | 440.892 hasil untuk `garden tools background` | Cukup kuat, tetapi query broad sangat padat dan tool cluster dapat drift ke hardware | Menengah; brand/tool shape dan deformasi objek perlu diawasi | Menengah | Kandidat kedua |
| Sustainable reusable water bottle | Visual untuk hydration, refill station, sustainability campaign, atau wellness article | 111.423 hasil untuk `sustainable water bottle` | Cukup kuat untuk isolated product illustration | Menengah–tinggi karena kata sustainable/eco dapat menjadi klaim; bentuk botol dapat menyerupai produk | Rendah–menengah | Kandidat ketiga |
| Surreal desert landscape illustration | Hero/background untuk campaign atau editorial concept | 72.574 hasil untuk `surreal desert landscape illustration` | Provider mampu membuat ilustrasi, tetapi current JPEG preflight lebih cocok isolated square daripada hero scene | Rendah untuk release, tetapi genericness dan utility kabur | Rendah–menengah | Ditunda |
| Recognizable craft/hobby cluster | Visual untuk DIY tutorial, craft blog, stationery, atau hobby education | 1.367.269 hasil untuk `craft supplies` | Mudah dipahami tetapi sangat crowded; cluster rawan menjadi generic | Menengah; deformasi alat, cute-face drift, dan style/IP shorthand | Rendah–menengah | Ditunda |
| Recognizable food object illustration | Visual untuk recipe, menu, grocery, nutrition, atau food packaging concept | 2.619.833 hasil untuk `food object illustration` | Provider fit baik, tetapi broad supply sangat tinggi dan food naming perlu akurat | Menengah; species/food identity dan packaging/brand risk | Rendah–menengah | Ditunda |
| Decorative botanical pattern | Stationery, textile, invitation, atau packaging background | 7.782.082 hasil untuk `botanical patterns` | Tidak cocok sebagai single JPEG first test; value lebih masuk akal sebagai pattern/set/PNG/SVG | Rendah–menengah, tetapi supply sangat padat dan format mismatch | Menengah | Ditunda |

Angka pembanding baseline untuk `electric actuator` adalah 59.163 hasil pada timestamp yang sama. Angka itu bukan target baru, melainkan proxy supply untuk lane rotor-armature yang sudah aktif. `reusable packaging illustration` menghasilkan 68.590 hasil, tetapi tidak dihitung sebagai kandidat baru karena lane circular packaging sudah terdaftar.

## 4. Scorecard konservatif

Scorecard ini hanya membantu memilih eksperimen murah berikutnya. Nilainya bukan purchase likelihood, sales forecast, atau ranking forecast. Skala 1–5 berarti semakin tinggi semakin baik; untuk supply burden, skor tinggi berarti supply proxy relatif lebih ringan. Bobot memprioritaskan kejernihan buyer job, kesiapan route, dan rendahnya risiko.

| Kandidat | Buyer job 25% | Supply 20% | Route 20% | Compliance 15% | Seasonality 10% | Distinctness 10% | Skor berbobot |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Seed-starting tray** | 5 | 5 | 4 | 5 | 3 | 5 | **4,60 / 5** |
| Garden tools | 5 | 2 | 4 | 4 | 3 | 4 | 3,75 / 5 |
| Sustainable water bottle | 4 | 3 | 4 | 3 | 4 | 4 | 3,65 / 5 |
| Surreal desert landscape | 3 | 4 | 4 | 4 | 3 | 3 | 3,55 / 5 |
| Food object illustration | 5 | 1 | 4 | 4 | 4 | 3 | 3,55 / 5 |
| Craft/hobby cluster | 4 | 1 | 4 | 4 | 4 | 3 | 3,30 / 5 |
| Botanical pattern | 4 | 1 | 2 | 4 | 3 | 2 | 2,90 / 5 |

## 5. Keputusan produk

StockForge memilih **Seed-starting tray / indoor seedling propagation** sebagai niche JPEG baru untuk first controlled internal hypothesis. Pilihan ini bukan klaim bahwa niche tersebut laku. Alasannya adalah kombinasi evidence relatif yang lebih kuat: query exact-object memiliki supply proxy jauh lebih kecil daripada broad craft, food, garden-tools, dan botanical queries; tray adalah objek yang jelas dan berulang dalam panduan hortikultura; buyer job dapat dijelaskan tanpa mengandalkan slogan abstrak; route existing mampu membuat satu isolated square JPEG; dan asset dapat dibuat tanpa manusia, logo, brand, named cultivar, property release, atau klaim engineering.

Produk tidak akan diposisikan sebagai foto dokumenter, tutorial lengkap, diagnosis tanaman, atau instruksi pertanian yang akurat untuk semua iklim. Produk akan diposisikan sebagai **conceptual horticultural illustration of an indoor seed-starting tray**, dengan objek yang terlihat seperti tray/module yang mudah dikenali dan konteks minimal. Jika preview terlihat sebagai pseudo-botanical decoration, tray tidak terbaca, atau image membuat klaim spesies/timing yang tidak dapat dipertanggungjawabkan, preview harus dinilai lemah meskipun JPEG technical gate lulus.

## 6. Batas evidence dan risiko

Sumber hortikultura membuktikan bahwa tray, module, compost, seedling, label, watering, cover, dan warm light adalah komponen proses yang nyata. Sumber tersebut tidak membuktikan bahwa buyer Adobe mencari satu ilustrasi AI tray, berapa conversion-nya, atau apakah asset akan diterima. Maka metadata hanya akan memakai istilah yang benar-benar terlihat. `tomato`, `chilli`, `basil`, `greenhouse`, `peat-free`, atau istilah spesies/material tidak boleh dipakai kecuali visual benar-benar mendukung dan telah direview.

Risiko utama adalah generative deformation pada cell tray, root/seedling anatomy yang tidak masuk akal, unreadable pseudo-label, overclaim “organic”, “sustainable”, “professional nursery”, atau “high yield”, serta kemiripan dengan kemasan/produk bermerek. Negative prompt harus menolak brand, logo, label, readable text, packet, named cultivar, fake certification, medical/food claims, and unrelated tools. Objek harus tetap satu cluster terkontrol; tidak boleh berubah menjadi meja penuh alat, greenhouse scene, atau collage.

## References

[1]: https://helpx.adobe.com/stock/contributor/help/artist-hub-migration/creat-what-s-in-demand.html "Create what's in demand | Adobe Stock Contributor"
[2]: https://business.adobe.com/resources/creative-trends-report.html "Innovation and authenticity — Adobe’s 2026 Creative Trends forecast"
[3]: https://www.gettyimages.com/visualgps/creative-trends/technology/2026-visual-trends-were-tracking "2026 Visual Trends We're Tracking | Getty Images"
[4]: https://extension.umn.edu/garden-and-home/yard-and-garden/gardening-in-minnesota/starting-seeds-indoors "Starting seeds indoors | University of Minnesota Extension"
[5]: https://www.rhs.org.uk/propagation/how-to-sow-seeds-indoors "How to Sow Seeds Indoors | Royal Horticultural Society"
[6]: https://stock.adobe.com/search?k=seed+starting+tray "Adobe Stock search — seed starting tray"
[7]: https://stock.adobe.com/search?k=garden+tools+background "Adobe Stock search — garden tools background"
[8]: https://stock.adobe.com/search?k=sustainable+water+bottle "Adobe Stock search — sustainable water bottle"
[9]: https://stock.adobe.com/search?k=surreal+desert+landscape+illustration "Adobe Stock search — surreal desert landscape illustration"
[10]: https://stock.adobe.com/search?k=craft+supplies "Adobe Stock search — craft supplies"
[11]: https://stock.adobe.com/search?k=food+object+illustration "Adobe Stock search — food object illustration"
[12]: https://stock.adobe.com/search?k=botanical+patterns "Adobe Stock search — botanical patterns"
[13]: https://stock.adobe.com/search?k=electric+actuator "Adobe Stock search — electric actuator"
[14]: https://stock.adobe.com/search?k=reusable+packaging+illustration "Adobe Stock search — reusable packaging illustration"

