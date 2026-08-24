# Buyer Segment Intelligence: Standalone Asset Portfolio

**Version:** 2.0
**Status:** Portfolio-first planning model

Marketplace queries menunjukkan istilah yang dicari, tetapi tidak cukup untuk menjelaskan fungsi sebuah aset. StockForge memodelkan buyer, pekerjaan komunikasi, channel, dan kebutuhan komposisi sebelum membuat candidate. Segmen berikut merupakan heuristik perencanaan, bukan bukti bahwa buyer tertentu akan membeli aset tertentu.

| Segment | Pengguna | Pekerjaan komunikasi | Aset standalone yang dicari | Larangan default |
|---|---|---|---|---|
| Web/product teams | product designers, developer advocates, product marketers | landing page, feature explainer, docs, deck | metafora 3D, material atmosphere, icon object | UI palsu, layar, perangkat bermerek, teks |
| Brand marketing teams | brand/campaign/content teams | campaign, ad, email, hero web | visual sensori, playful conceptual object, prop kreatif | komposisi ramai, props acak, klaim merek |
| Editorial/content teams | editors, newsletter producers, content strategists | article art, newsletter, explainer | simbol editorial, craft element, texture | tulisan di gambar, scene tanpa kebutuhan, metafora tidak jelas |
| Small business commerce | merchants, shop managers, growth teams | product page, promotion, packaging insert | generic product-adjacent prop, sticker, material | label, packaging text, logo, tangan |
| Social creator teams | creators, community/social managers | post, story, thumbnail, serial content | bold icon-like object, playful surreal metaphor | objek jamak, teks/angka, crop yang rapuh |
| Local brand storytelling | hospitality and local brand teams | campaign, packaging, editorial | natural motif atau craft element dengan provenance | apropriasi budaya, klaim lokasi/komunitas yang tidak didukung |

## Aturan buyer-first

Setiap candidate wajib menjawab: siapa yang akan menggunakannya, pekerjaan komunikasi apa yang dapat ia bantu, di channel mana ia dipakai, dan mengapa satu objek standalone lebih berguna daripada visual dekoratif generik. Jika alasan tersebut belum didukung evidence atau masih hipotesis, candidate tetap berstatus `REVIEW`.

## Standalone-first composition

Untuk batch awal, mesin memakai satu subjek lengkap pada latar putih bersih, dengan ruang kosong yang dapat dipakai desainer. Manusia, tangan, alat, perangkat, layar, angka, text, frame, perangko, dan prop tambahan dilarang kecuali AssetSpec menjadikannya subjek inti dan evidence mendukung pengecualian tersebut.

## Portfolio balancing

Satu subject tidak boleh dijadikan seluruh strategi. Scheduler masa depan harus membagi candidate di antara material atmospheres, UI-adjacent 3D metaphors, playful conceptual objects, retro-tech metaphors, human-made collage elements, serta natural/craft motifs. Setiap lane harus memiliki batas batch, catatan evidence, dan deduplication gate sendiri.

## Principle

> Jangan membuat gambar untuk satu niche. Buat aset yang menyelesaikan pekerjaan komunikasi yang jelas, lalu uji apakah aset tersebut dapat dipakai ulang oleh lebih dari satu buyer dan channel.
