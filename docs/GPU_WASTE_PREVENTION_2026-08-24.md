# Pencegahan Pemborosan GPU — Pelajaran dari `cassette-cloud`

**Tanggal:** 2026-08-24  
**Status:** Aturan operasional dan target implementasi untuk memblokir brief berisiko sebelum request remote dibuat.

## Keputusan

Preview `retro_tech_developer_metaphors--cassette-cloud` ditolak. Ia tidak boleh di-upscale, diberi XMP, dimasukkan ke bundel Adobe, atau diunggah. Satu request ZeroGPU telah dipakai untuk eksperimen ini; tidak boleh ada retry dengan seed, crop, palet, atau variasi kecil.

> **Aturan baru:** GPU hanya dipakai untuk sebuah brief setelah lolos pemeriksaan struktur, risiko semantik, kontrak komposisi, dan metadata visual. Status `planned` atau `dry-run` sendiri tidak lagi cukup.

## Mengapa hasil tidak memenuhi brief

| Kegagalan yang terlihat | Penyebab di brief/pipeline | Mengapa negative prompt tidak cukup | Perbaikan wajib sebelum GPU |
|---|---|---|---|
| Kaset tampak sebagai perangkat audio nyata yang distilisasi | Subjek positif menyebut `cassette`; prompt memberi model bentuk, reel, sekrup, slot, dan jendela pita yang sangat dikenali | Negative prompt melarang `devices`, tetapi biasanya instruksi subjek positif lebih dominan daripada larangan generik | Tolak kata dan konsep yang menyiratkan perangkat nyata apabila lane melarang perangkat nyata; jangan gunakan kaset, disk, reel, keyboard, terminal, atau bentuk hardware mapan sebagai subjek | 
| Awan berada di luar, bukan berada di dalam kaset | Frasa `holding one soft cloud form` tidak mengunci hubungan spasial | Model dapat menginterpretasikan hubungan sebagai tumpukan atau ornamen | Setiap hubungan visual wajib memakai kontrak eksplisit: `inside/contained by`, `single fused sculpture`, atau `cut-out negative space`, disertai kondisi yang bisa diaudit | 
| Ruang salin di kanan tidak terbentuk | `clean copy space right` merupakan aspirasi, bukan batas tata letak terukur | Prompt tidak menetapkan letak atau luas subjek | Gunakan kontrak komposisi: subjek terbatas pada sisi kiri atau tengah-kiri; sedikitnya sepertiga kanvas kanan harus latar bersih; pilih `hero-landscape` bila arah copy space adalah kebutuhan inti | 
| Hasil lebih dekoratif daripada metafora DevRel yang jelas | Hipotesis pembeli dan mekanisme visual tidak diterjemahkan menjadi indikator visual yang dapat diuji | Model tidak dapat memverifikasi nilai komersial abstrak dari prompt | Tulis satu kalimat *visual proof*: apa yang harus terlihat pada thumbnail agar pembeli memahami objek tanpa teks | 
| Kandidat eksperimen mencapai remote GPU tanpa pemeriksaan risiko lane | Loader plan hanya memeriksa JSON, prompt, dan marker review manusia; tidak memvalidasi makna subjek, larangan lane, atau kontrak komposisi | Tidak ada penolakan deterministik sebelum `route_remote_generation()` | Tambahkan gate CPU pada jalur `portfolio generate`; setiap konsep harus memiliki catatan kelayakan GPU eksplisit atau diblokir | 

## Model gate pra-GPU yang wajib

Semua pemeriksaan berikut berjalan lokal/CPU dan tidak memanggil worker remote.

| Gate | Pertanyaan yang wajib dijawab | Keputusan bila gagal |
|---|---|---|
| **G0 — Hipotesis tunggal** | Apakah buyer job, nilai visual, dan kriteria pass/reject dapat ditulis masing-masing dalam satu kalimat? | Jangan buat plan produksi. |
| **G1 — Risiko lane** | Apakah subject bertentangan dengan larangan spesifik lane, seperti perangkat nyata pada retro-tech atau UI palsu pada metafora 3D? | Blok request GPU. |
| **G2 — Kontrak objek** | Apakah ada satu objek lengkap/satu sculpture terfusi, dan apakah hubungan antarbagian dinyatakan tegas? | Kembali ke konsep; jangan "perbaiki" dengan seed baru. |
| **G3 — Kontrak komposisi** | Apakah posisi subjek, area copy space, latar, dan crop dapat diverifikasi secara visual? | Revisi brief sebelum GPU. |
| **G4 — Kelayakan metadata** | Apakah tersedia judul visual-first dan kata kunci yang dapat dipertahankan hanya jika benar-benar terlihat? | Blok hingga metadata draf diperbaiki. |
| **G5 — Persetujuan konsep** | Apakah konsep terdaftar sebagai `gpu_eligible` setelah G0–G4? | `portfolio generate` harus berhenti secara lokal. |

## Aturan penghentian dan alokasi

Satu job ZeroGPU hanya boleh menguji satu hipotesis baru. Sebuah hasil yang gagal pada siluet, hubungan spasial, komposisi, atau fungsi pembeli ditolak pada level konsep. Ia tidak boleh memperoleh retry seed ataupun finalisasi Kaggle. Job berikutnya harus menggunakan **brief baru yang secara material berbeda**, dengan alasan perubahan yang terdokumentasi.

Kaggle hanya boleh dipanggil jika preview lulus audit visual menyeluruh: siluet bersih dan non-merek, satu subject koheren, hubungan bagian benar, ruang salin sesuai, tanpa teks/artefak, metadata visual dapat dipertahankan, dan perbedaan komersial terhadap aset terdahulu jelas.

## Dampak UX Termux

Agen harus mengirim satu blok perintah multiline yang memiliki tombol **Copy** di aplikasi. Blok tidak boleh menyertakan placeholder, nama file yang harus dicari pengguna, atau beberapa alternatif. Jika output diperlukan, agen harus selalu menyisipkan ID dan path aktual ke blok berikutnya.

