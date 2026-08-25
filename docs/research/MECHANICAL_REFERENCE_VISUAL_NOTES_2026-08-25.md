# Catatan Audit Referensi Mechanical — 2026-08-25

## Referensi 1: `/home/ubuntu/upload/1000802935.jpg`

Gambar asli berukuran 1219×1110 px dan terbaca tanpa tiling. Ini adalah screenshot marketplace yang menampilkan sebuah objek teknis kecil terisolasi pada bidang putih: bentuk umum berupa komponen silindris/koaksial dengan bagian logam warna tembaga/kuning, bagian tengah berwarna hijau-abu, dan ujung berulir. Screenshot juga memuat logo dan antarmuka Adobe, angka pendapatan, teks promosi, serta watermark/handle. Elemen-elemen antarmuka, logo, angka, watermark, layout, dan desain objek persis diperlakukan sebagai **bukan aset yang boleh disalin**. Sinyal yang dapat dipakai hanya grammar umum: komponen kecil, unbranded, isolated, siluet silindris, kontras material, dan keterbacaan pada bidang putih.

Tidak ada kesimpulan sah tentang penjualan, demand, ranking, approval, conversion, atau revenue dari screenshot tersebut. Klaim pengguna bahwa niche serupa pernah di-upload dicatat sebagai laporan pengguna saja.

## Referensi 2: `/home/ubuntu/upload/1000803314.jpg`

Dimensi asli 4096×4096 px, square, total 16.777.216 piksel. Karena ukuran/detailnya, gambar diperiksa melalui 9 crop overlap dalam manifest row-major.

### Tile 1 — x=0..1399, y=0..1399

Hampir seluruh tile adalah latar putih. Hanya bagian sangat kecil dari tepi objek gelap terlihat di sudut kanan bawah; belum cukup untuk mengidentifikasi objek sendirian.

### Tile 2 — x=1348..2747, y=0..1399

Terlihat bagian atas objek besar: lengkungan/segmen berbentuk annular berwarna graphite/abu gelap dengan tepi hitam, deretan lilitan/garis tembaga rapat di permukaan bagian dalam/atas, dan beberapa detail bundar seperti kepala fastener atau insert. Struktur ini konsisten dengan komponen rotor/armature berkumparan, bukan cable gland.

Temuan overlap awal: objek melintasi batas tile 1–2 dari sudut kanan bawah menuju area bawah tile 2; tile 2 memberi bukti material berupa copper winding dan housing graphite.

## Status rekonsiliasi sementara

Referensi kedua adalah output StockForge sebelumnya dengan grammar axial/annular, copper winding, graphite housing, dan detail fastener. Candidate baru harus menghindari rotor, armature, winding/coil, annular rotor body, dan motor-like silhouette; cable gland dipertimbangkan karena visible product job dan siluetnya threaded coaxial strain-relief, bukan rotating electromechanical assembly.

### Tile 3 — x=2696..4095, y=0..1399

Sebagian besar latar putih; sisi kiri bawah melanjutkan tepi luar dan ujung lilitan tembaga dari objek pada tile 2. Tidak ada komponen baru yang terlihat. Ini menguatkan bahwa bentuk utama berpusat di area tengah-kiri dan bukan connector kecil.

### Tile 4 — x=0..1399, y=1348..2747

Terlihat poros silindris logam terang yang menonjol dari pusat assembly, dengan lubang/permukaan gelap pada ujung depan. Di belakangnya ada piringan graphite dengan lubang bundar, cincin/komponen tembaga dan bagian annular warna kuning-keemasan. Bentuk ini jelas merupakan assembly berporos dan berputar secara konseptual.

### Rekonsiliasi tile 3–4

Batas tile 3–4 menunjukkan kelanjutan lilitan/casing di sisi kiri bawah; tidak ada perubahan identitas objek. Tile 4 menambahkan bukti paling kuat bahwa output sebelumnya adalah rotor/armature dengan shaft axial, bukan fitting kabel atau plumbing.

### Tile 5 — x=1348..2747, y=1348..2747

Pusat assembly memperlihatkan beberapa cincin/rotor lamination warna kuning-keemasan, inti graphite/abu, fastener bundar, dan lilitan tembaga rapat pada sisi kanan. Detail permukaan menunjukkan beberapa highlight kecil/titik kecil dan edge yang sangat kontras; ini relevan sebagai catatan kualitas visual, tetapi bukan alasan untuk membuat pseudo-retry.

### Tile 6 — x=2696..4095, y=1348..2747

Sisi kanan melanjutkan lilitan tembaga, cincin keemasan, dan silinder shaft logam terang yang keluar ke kanan. Bidang putih besar di kanan menjaga isolasi, tetapi objek crop/close-up terlihat terlalu besar untuk fungsi product icon kecil. Tidak tampak kabel, seal elastomer, cap nut, atau entry fitting.

### Rekonsiliasi tile 5–6

Overlap menunjukkan satu objek mekanis berlapis dengan copper winding dan axial shaft. Candidate cable-gland harus memakai grammar berbeda: cap nut/hex or rounded body, threaded entry, elastomer strain-relief/seal, dan short cable stub; tidak boleh memakai coil, rotor disc, shaft, atau repeated annular winding.

### Tile 7 — x=0..1399, y=2696..4095

Hampir seluruh tile kembali berupa latar putih; bagian kanan atas hanya melanjutkan cincin keemasan dan plate graphite dengan lubang. Tidak ada detail baru yang mengubah identitas objek.

### Tile 8 — x=1348..2747, y=2696..4095

Bagian bawah assembly memperlihatkan piringan/kerangka graphite melingkar, deretan lilitan tembaga pada sisi luar dan bagian dalam, serta beberapa fastener bundar. Struktur berulang dan bentuk cincin sangat dominan.

### Rekonsiliasi tile 7–8

Overlap memperlihatkan satu kerangka annular kontinu dengan copper winding; tidak ada kabel atau fitting entry. Ini makin memperjelas material distinctness yang dibutuhkan untuk candidate baru.

### Tile 9 — x=2696..4095, y=2696..4095

Bagian kiri tile memperlihatkan kelanjutan lilitan tembaga dan tepi luar graphite/keemasan; mayoritas area lain adalah latar putih. Tidak ada elemen baru.

## Rekonsiliasi akhir gambar kedua

Semua 9 tile pada manifest telah diperiksa row-major. Overlap antar tile tidak menimbulkan konflik identitas: gambar kedua adalah satu output StockForge berupa conceptual rotor/armature assembly dengan copper winding yang sangat dominan, annular graphite/gold frame, fasteners, dan axial shaft. Kekurangan yang relevan untuk keputusan berikutnya adalah objek terlalu besar/close-up dan sangat bergantung pada rotor/coil shorthand; candidate baru akan memakai product silhouette kecil yang lebih sederhana, non-rotating, dan memiliki buyer job installation/industrial wiring yang eksplisit.

## Sumber buyer-job yang dibuka langsung

**HELUKABEL Vietnam — Cable glands: Selection criteria and installation instructions.** Halaman resmi menjelaskan bahwa cable gland menghubungkan dan mengamankan kabel listrik ke equipment; struktur utamanya mencakup gland body, cap nut berulir, moulded seal, clamping seal insert, dan entry thread. Sumber juga menjelaskan penggunaan pada power, control, dan instrument cables, serta tahapan memilih, memasukkan, mengencangkan, dan memeriksa pemasangan. Sumber: https://www.helu.com/vn-en/select-and-install-cable-glands.html

**DigiKey TechForum — Cable Gland Installation.** Post teknis DigiKey mendefinisikan cable gland sebagai perangkat untuk melewatkan kabel masuk/keluar enclosure sambil mempertahankan ingress protection enclosure jika berlaku. Prosedur yang diperlihatkan mencakup membuat lubang, memasang gland, memasukkan kabel, dan mengencangkan nut agar kabel terjepit dan tidak bergerak. Sumber: https://forum.digikey.com/t/cable-gland-installation/55691

Kedua sumber mendukung buyer job yang konkret: ilustrasi objek untuk artikel/edukasi instalasi enclosure, wiring/interconnect explainer, dan materi katalog/produk generik. Mereka tidak mendukung klaim bahwa satu ilustrasi tertentu akan terjual atau disetujui marketplace.
