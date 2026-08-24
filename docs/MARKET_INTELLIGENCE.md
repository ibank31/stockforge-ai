# Marketplace Intelligence: Standalone Asset Portfolio

**Version:** 2.0
**Status:** Research foundation; automated collection remains planned

## Purpose

StockForge tidak boleh mengoptimalkan jumlah gambar atau mengejar satu keyword. Ia harus memilih candidate yang memiliki fungsi desain jelas, pembeda visual, dan kemungkinan dipakai di lebih dari satu channel. Evidence market membantu memilih **hipotesis uji**, bukan membuat klaim penjualan.

## Evidence hierarchy

Kumpulkan evidence dengan urutan berikut: marketplace-native search/trend pages, contributor/customer guidance resmi, trend reports resmi, aturan lisensi/submission, lalu riset sekunder jika sumber primer tidak tersedia. Result count adalah sinyal supply, bukan penjualan. Semua signal harus menyimpan URL dan timestamp.

## Portfolio opportunity lanes

| Lane | Pekerjaan desain | Candidate awal | Alasan uji | Risiko utama |
|---|---|---|---|---|
| Material atmospheres | hero web, background campaign, deck | satu material/translucent object atau texture study | Adobe menekankan visual sensori; Canva melihat pertumbuhan texture/tactile design.[1] [2] | terlihat sebagai scene, tekstur tidak meyakinkan, terlalu mirip karya tertentu |
| UI-adjacent 3D metaphors | landing page, product explainer, DevRel | satu metafora 3D non-merek | kebutuhan visual bisnis meningkat dan aset mudah dikomposisikan perlu diuji.[1] | layar palsu, perangkat bermerek, text/angka |
| Playful conceptual objects | campaign, social, editorial | satu objek surealis dengan metafora tunggal | Adobe menandai surealisme playful sebagai arah kreatif 2026.[1] | beberapa ide digabung, props acak, humor tanpa fungsi |
| Retro-tech metaphors | product marketing, developer content | icon/illustration non-merek | Canva melaporkan peningkatan minat lo-fi/retro-tech.[2] | kode terbaca, UI imitasi, logo/perangkat nyata |
| Craft and collage elements | newsletter, social, editorial | elemen potong/kertas/tactile single object | Canva melaporkan kenaikan DIY/scrapbook style.[2] | full collage sheet, frame, stamp/postmark, tulisan |
| Natural and local motifs | packaging, local brand storytelling | botanical/craft motif dengan provenance | Adobe menekankan autentisitas lokal, bukan imitasi generik.[1] | apropriasi budaya atau klaim lokasi tanpa bukti |

## Differentiation framework

Setiap opportunity dinilai pada search/trend signal, supply saturation, buyer utility, visual differentiation, variation potential, compliance risk, dan portfolio fit. High demand dengan saturation ekstrem dapat tetap menjadi `REJECT`; demand rendah dengan buyer utility yang belum terbukti harus `REVIEW`.

## Standalone production rule

Untuk eksperimen awal, semua candidate dimulai dengan satu subject lengkap, latar putih, isolasi jelas, tanpa text dan tanpa branding. Scene, manusia, tangan, alat, perangkat, layar, angka, label, frame, perangko, atau props tambahan hanya boleh muncul bila menjadi subject inti pada AssetSpec dan evidence mendukungnya. Batch harus diseimbangkan antar lane; satu lane atau keyword tidak boleh menguasai seluruh produksi.

## Anti-spam rule

Satu collection harus berisi variasi yang benar-benar berbeda pada fungsi, material, subject, atau komposisi. Perubahan seed, crop, atau warna saja tidak cukup. Jalur targetnya adalah `generate → quality gate → similarity clustering → best-of-cluster selection → portfolio diversity check`.

## Automation target

Market Intelligence di masa depan harus menyimpan `marketplace`, `query`, `result_count`, `trend_signal`, `growth_signal`, `commercial_use_cases`, `visual_patterns`, `saturation_score`, `opportunity_score`, `research_timestamp`, dan `source_urls`. Tidak ada score yang boleh disajikan sebagai fakta tanpa sumber dan waktu observasi.

## References

[1]: https://business.adobe.com/resources/creative-trends-report.html "Adobe 2026 Creative Trends Forecast"
[2]: https://www.canva.com/newsroom/news/design-trends-2026/ "Canva 2026 Design Trends"
