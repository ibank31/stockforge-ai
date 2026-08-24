# Audit Knowledge dan Visual Identity Niche JPEG

**Tanggal:** 25 Agustus 2026  
**Status:** Audit engineering dan evidence; tidak mengotorisasi generation atau upload.

## Kesimpulan singkat

StockForge sudah memiliki **knowledge terstruktur tingkat menengah** untuk sembilan niche JPEG. Setiap lane memiliki buyer segment, buyer job, channel, asset family, micro-niche, visual language, medium, commercial use cases, keyword map, palette, test cap, notes, dan lima concept cards. Struktur ini cukup untuk membuat prompt yang aman dan tidak sepenuhnya generik.

Namun, knowledge tersebut **belum maksimal** jika standar yang dimaksud adalah setiap niche mempunyai ciri khas visual yang konsisten, dapat dibedakan secara kuat dari niche lain, dan telah terbukti meningkatkan buyer value. Riset yang tersimpan masih dominan berupa sinyal platform dan trend-level. Belum ada evidence lane-specific yang terhubung secara eksplisit ke opportunity IDs, belum ada data transaksi atau feedback buyer per niche, dan belum ada test yang membandingkan distinctiveness prompt antar-lane.

## Niche JPEG yang saat ini terdaftar

| Lane | Buyer job tersimpan | Identity yang sudah didefinisikan | Status knowledge |
|---|---|---|---|
| `ai_governance` | AI governance explainer dan compliance landing page | Deep navy, ivory, amber; frosted glass, matte ceramic, translucent layers; review/traceability metaphors | Terstruktur, tetapi masih hypothesis |
| `playful_surreal_product_metaphors` | Brand campaign dan product-benefit hero | Warm cream, cobalt, coral; paper, ceramic, soft rubber; one witty visual sentence | Terstruktur, tetapi masih hypothesis |
| `tactile_material_atmospheres` | Web hero background dan brand-system material study | Warm white, sand, sage; fiber paper, frosted glass, porcelain, organic foam; copy-safe material composition | Terstruktur, tetapi risiko generic texture masih tinggi |
| `synthetic_media_trust` | Media-literacy editorial illustration dan trust explainer | Ink blue, paper white, transparent aqua; capsule, frame, lens, source-path metaphors | Terstruktur, tetapi masih hypothesis |
| `returns_recommerce` | Retail operations dan reverse-logistics explainer | Kraft, recommerce green, charcoal; parcel, recovery, route, refurbishment metaphors | Terstruktur, tetapi masih hypothesis |
| `digital_accessibility` | Inclusive design dan adaptable-access explainer | Deep blue, warm white, clear yellow; raised paths, open portals, adaptable hubs | Terstruktur; tidak boleh menjadi klaim compliance |
| `retro_tech_developer_metaphors` | Developer relations dan coding editorial hero | Dusty lilac, beige, soft teal; matte plastic, acrylic, phosphor glow; brand-free retro-future objects | Terstruktur, tetapi risiko generic nostalgia/IP shorthand masih ada |
| `circular_packaging_systems` | Refill dan reuse packaging-system explainer | Recycled kraft, moss green, ceramic white; blank containers, refill route, material flow | Terstruktur, tetapi risiko environmental claim tetap terbuka |
| `software_supply_chain_integrity` | DevSecOps integrity dan dependency explainer | Graphite, white, electric blue; modular components, transparent path, build verification | Terstruktur, tetapi sangat bergantung pada abstract metaphor |

`human_made_collage_elements` tidak dihitung sebagai JPEG niche aktif karena route-nya adalah PNG true-alpha dan status PNG masih **BLOCKED**.

## Apa yang sudah dimiliki sistem

Setiap `PortfolioLane` memiliki struktur yang cukup baik untuk perencanaan: buyer segment, buyer job, channel, asset family, asset type, micro-niche, visual language, medium, commercial use cases, keywords, initial tier, evidence confidence, test cap, dan notes. Setiap `LaneConcept` menambahkan subject, visual mechanism, composition, negative-space contract, palette, originality levers, product kind, delivery format, layout mode, background policy, dan isolation policy.

Compiler prompt juga sudah memasukkan subject, visual mechanism, material behavior, composition, negative-space contract, palette, originality levers, visual language, quality constraints, dan legal constraints. Prompt compiler sengaja tidak memasukkan buyer-job language secara langsung ke image-facing prompt agar istilah seperti dashboard, SaaS, developer, atau packaging tidak menarik model ke arah fake UI, label, device, atau branding. Buyer context tetap disimpan di metadata dan provenance.

## Mengapa belum maksimal

### 1. Riset belum lane-specific

Dokumen market JPEG yang ada terutama memuat guidance Adobe, Shutterstock, Freepik, dan trend signals seperti tactile, surreal, authentic connection, remote work, sustainability, dan editorial utility. Ini berguna sebagai arah, tetapi belum membuktikan bahwa sembilan lane tertentu memiliki demand, conversion, atau keunggulan kompetitif yang terukur. `evidence_confidence="medium"` adalah label perencanaan, bukan bukti penjualan.

Pencarian repository terhadap opportunity IDs lane JPEG (`C01`, `C42`, `C41`, `C59`, `C26`, `C37`, `C43`, `C21`, dan `C08`) tidak menemukan evidence records terpisah yang terhubung langsung ke masing-masing lane. Dengan demikian, opportunity ID saat ini berfungsi sebagai identifier rencana, bukan bundle evidence yang lengkap.

### 2. Visual grammar masih terlalu pendek

Lane memiliki palette, medium, visual language, subject, mechanism, composition, dan levers. Akan tetapi, belum ada identity card yang menetapkan secara eksplisit hal-hal berikut untuk masing-masing niche: camera or rendering grammar, lighting signature, depth-of-field policy, environmental context, subject scale, preferred perspective, recurring shape language, prohibited metaphor family, acceptable variation boundaries, copy-space behavior, thumbnail test, dan “what this niche must never look like.”

Akibatnya, dua niche berbeda dapat sama-sama menghasilkan objek centered, white-background, matte/translucent, minimal, dan conceptual 3D. Perbedaan buyer job belum otomatis menjadi perbedaan visual yang cukup kuat.

### 3. Banyak lane JPEG masih memakai policy standalone generic

Helper `_concept` menormalkan konsep yang memakai `layout_mode="square"` dan `isolation_policy="isolated"` menjadi centered square framing dengan minimal surrounding margin dan tanpa reserved copy space. Sebagian besar niche JPEG saat ini memakai default `isolated`, `square`, dan `white`.

Asset prompt compiler memang sudah memiliki conditional `_SCENE_NEGATIVE` yang mengizinkan human-centered scene secara terkontrol. Namun, guard tersebut hanya aktif jika `delivery_format="jpeg"` dan `isolation_policy="scene"`. Lane JPEG yang terdaftar saat ini pada umumnya tetap `isolated`, sehingga belum memakai scene-specific negative prompt tersebut. Jadi, kemampuan scene human-centered sudah tersedia sebagai fondasi, tetapi belum diwujudkan sebagai lane identity aktif.

### 4. Distinctiveness belum diuji secara otomatis per niche

Test suite memverifikasi safety, format, standalone policy, dan satu contoh scene-human split. Belum ada regression test yang memeriksa bahwa setiap lane menghasilkan prompt yang memiliki token visual identity unik, bahwa dua lane tidak terlalu overlap secara visual, atau bahwa setiap concept memiliki distinctness lever yang benar-benar berbeda dari sibling dan lane lain.

### 5. Tidak ada feedback komersial lane-specific

Belum ada data marketplace transaction yang dapat dipakai sebagai sales proof. Trial SVG sebelumnya hanya membuktikan bahwa structural validity tidak sama dengan buyer value; hasil tersebut tidak dapat dipindahkan sebagai bukti JPEG. Karena belum ada JPEG trial baru pada fase ini, belum ada human buyer review untuk memilih lane JPEG berikutnya.

## Penilaian maturity

| Komponen | Status saat ini | Penilaian |
|---|---|---|
| Buyer job dan buyer segment | Ada di setiap lane | Baik untuk planning |
| Subject dan visual mechanism | Ada di setiap concept card | Baik, tetapi belum cukup sebagai identity system |
| Palette dan material | Ada dan cukup terarah | Cukup kuat untuk art direction dasar |
| Composition dan copy-space | Ada, tetapi sering dinormalisasi ke square isolated | Belum maksimal |
| Negative prompt | Shared safety plus conditional scene safety | Aman, tetapi belum niche-specific |
| Legal/release awareness | Generic safeguards dan manual review | Belum lane-specific |
| Metadata | Reviewed draft dan platform preflight | Cukup secara mekanis; belum bukti discoverability/sales |
| Market evidence | Platform/trend-level | Belum cukup untuk klaim niche demand |
| Prompt distinctiveness testing | Belum ada | Gap utama |
| Human commercial validation | Belum ada JPEG phase trial | Gap utama |

## Audit verdict

Status yang paling akurat adalah **structured but not maximal**. Sistem sudah mampu memilih dan membangun prompt JPEG yang berbeda pada level subject, material, palette, composition, dan metaphor. Sistem belum mampu menjamin bahwa setiap niche memiliki “signature” yang kuat dan konsisten karena signature tersebut belum diformalisasi sebagai identity framework dan belum diuji lintas lane.

Tidak boleh menyimpulkan bahwa semua sembilan niche sama kuatnya. Tier `first`, `secondary`, dan `experimental` hanya mengatur prioritas hypothesis testing. Tidak boleh menyimpulkan bahwa medium, palette, atau trend signal tertentu menjamin Adobe acceptance, search placement, checkout, atau penjualan.

## Kebutuhan sebelum niche disebut matang

Sebelum satu niche disebut matang untuk prompt production, lane tersebut perlu memiliki identity card yang menyatukan buyer problem, visible subject family, visual grammar, material/light behavior, composition/copy-space rules, distinctness levers, prohibited shorthand, release/IP policy, metadata inventory, and human review questions. Identity card tersebut harus masuk ke prompt compilation dan provenance, lalu diuji dengan regression tests yang membuktikan adanya perbedaan bermakna antar-lane.

Perubahan ini dapat dilakukan tanpa generation. Generation baru hanya diperlukan setelah satu niche dipilih, satu buyer hypothesis disetujui, pretrial specification selesai, provider path tersedia, dan pengguna memberi otorisasi eksplisit.

## Sumber internal

- `src/stockforge/portfolio.py` — lane dan concept registry.
- `src/stockforge/asset_prompt_compiler.py` — image-facing prompt compiler dan shared safety policy.
- `src/stockforge/asset_spec.py` — format, layout, isolation, dan quality contracts.
- `src/stockforge/market_intelligence.py` — evidence-bound opportunity model.
- `docs/research/jpeg_market_2026-08-24.md` — official marketplace/trend research dan caveats.
- `docs/research/JPEG_MATURATION_PLAN_2026-08-24.md` — active JPEG maturation sequence.
- `tests/test_asset_prompt_compiler.py` — shared prompt safety tests; belum lane-by-lane distinctiveness tests.
- `tests/test_portfolio.py` — portfolio lane and preflight tests.

## Current decision

Knowledge tiap niche **sudah ada pada level struktur dan hypothesis**, tetapi **belum maksimal pada level lane-specific evidence, visual identity, distinctiveness testing, dan commercial validation**. Langkah aman berikutnya adalah membangun identity framework niche-specific dan mengintegrasikannya ke compiler sebelum melakukan trial JPEG.


## Evidence eksternal yang baru divalidasi

Audit eksternal memperkuat kebutuhan buyer yang tersirat pada niche `software_supply_chain_integrity`, tetapi belum membuktikan penjualan asset stock. CISA Secure by Demand menjelaskan bahwa customer perlu meminta artefak seperti software bill of materials (SBOM), provenance dependency pihak ketiga, dan proses vetting open-source components. NCSC Cyber Essentials Supply Chain Playbook menekankan risk assessment, supplier profiling, setting requirements, communicating expectations, procurement integration, monitoring adoption, serta supplier security profiles. Implikasi visualnya: niche ini memiliki buyer problem konkret berupa due diligence, provenance, supplier assurance, dan controlled handoff. Prompt yang matang sebaiknya memvisualkan alur dependency/provenance/verification secara abstrak dan non-literal, bukan memakai lock, shield, dashboard, kode, badge sertifikasi, atau klaim keamanan.

Sumber: [CISA Secure by Demand Guide](https://www.cisa.gov/resources-tools/resources/secure-demand-guide), diakses 25 Agustus 2026; [NCSC Cyber Essentials Supply Chain Playbook](https://www.ncsc.gov.uk/information/cyber-essentials-supply-chain-playbook), diakses 25 Agustus 2026. Kedua sumber adalah kebutuhan praktik/governance, bukan data download atau conversion marketplace.


Temuan tambahan memperjelas dua niche lain. Section508.gov menyarankan penyederhanaan makna dan navigasi, layout sederhana dan konsisten, minim clutter, visual cues yang recognizable, struktur informasi yang jelas, serta usability testing dengan pengguna nyata. Untuk `digital_accessibility`, visual identity sebaiknya berupa mekanisme adaptasi, clear paths, contrast, hierarchy, dan multiple participation routes; gambar tidak boleh dipakai untuk mengklaim conformance atau accessibility compliance.

Ellen MacArthur Foundation memetakan model reusable packaging berdasarkan refill oleh user atau return ke bisnis, serta lokasi home atau on-the-go. Halaman tersebut juga menekankan bahwa reuse dapat memberi manfaat bisnis, tetapi efektivitas circularity bergantung pada desain refill/return yang tidak menambah waste. Untuk `circular_packaging_systems`, prompt identity harus memvisualkan satu sistem refill/return yang dapat dikenali—misalnya container ownership, dispensing/refill, return loop, dan material-flow handoff—bukan sekadar paket hijau dengan simbol daur ulang. Sumber: [Section508.gov — Designing Digital Content for Users With Cognitive Disabilities](https://www.section508.gov/design/digital-content-users-with-cognitive-disabilities/), diakses 25 Agustus 2026; [Ellen MacArthur Foundation — Reusable packaging business models](https://www.ellenmacarthurfoundation.org/reusable-packaging-business-models), diakses 25 Agustus 2026.


## Hasil audit registry numerik

Audit deterministik terhadap `list_lanes()` dan `build_brief()` menemukan 9 lane JPEG. Dari sembilan lane tersebut, **8 memakai** `jpeg/square/isolated/white` dan hanya **1 memakai** `jpeg/hero_landscape/isolated/white`. Delapan lane juga dinormalisasi menjadi komposisi `single centered object with tight square product framing`; hanya `tactile_material_atmospheres/fiber-arch` yang mempertahankan `wide horizontal composition`. Semua lane JPEG memakai prompt negative policy `standalone`, bukan `scene`.

Temuan ini tidak berarti subject atau palette semua sama. Medium, palette, subject, mechanism, dan originality levers memang berbeda per lane. Namun, secara framing dan policy, sebagian besar niche masih berjalan melalui shell visual yang sama. Ini adalah bukti engineering bahwa niche identity saat ini belum cukup kuat untuk disebut maksimal; identity card perlu dapat mengontrol framing mode, environmental context, lighting grammar, and allowable subject complexity per niche.


## Identity framework yang sekarang diimplementasikan

Sebagai perbaikan tanpa generation, dibuat registry `JpegNicheIdentity` untuk sembilan lane JPEG. Setiap identity menyimpan signature visual, lighting signature, framing rule, environmental context, distinctness anchors, dan prohibited shorthand. Field tersebut dipersist ke `AssetSpec`, dipulihkan oleh `route_from_dict`, masuk ke prompt image-facing, dan menambahkan niche-specific shorthand ke negative prompt. SVG tidak menerima profile ini.

Perubahan ini memperbaiki **prompt identity**, bukan membuktikan market demand. Signature membantu menjaga arah visual antar concept dalam satu niche dan membedakan lane secara eksplisit, tetapi kualitas output tetap memerlukan provider benchmark, technical QA, 100% visual review, semantic/commercial review, rights review, dan—bila akan submit—human portal review.

Regression coverage baru memeriksa sembilan JPEG lane memiliki signature unik yang masuk ke prompt/negative prompt dan SVG tetap tidak berubah. Full suite setelah perubahan: **287 passed, 1 skipped**, 45 non-blocking Pillow deprecation warnings; compileall dan `git diff --check` lulus.

