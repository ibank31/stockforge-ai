# StockForge Batch Preview Runner

Runner ini menjalankan Backlog v2 sebagai antrean preview serial. Ia memproses tepat satu brief per request dengan profile `z-image-turbo`, `batch_size=1`, dan cap default empat percobaan per jendela 24 jam. Ia tidak menjalankan Kaggle, tidak mengubah prompt backlog, tidak melakukan seed-only retry, dan masuk cooldown saat provider gagal.

## Persiapan dan dry-run

Dari Termux:

```bash
cd ~/stockforge-ai
export PYTHONPATH=src
export STOCKFORGE_HOME="$HOME/.stockforge"
python3 scripts/run_backlog_preview_batch.py \
  --backlog "$HOME/stockforge-backlog-v2/StockForge_Backlog_v2_2026-08-27.json" \
  --project stock-assets \
  --daily-cap 4 \
  --dry-run
```

Path backlog harus disesuaikan dengan lokasi file di Termux. Dry-run membuat atau memeriksa plan portfolio lokal, menjalankan pre-GPU validation untuk seluruh 30 brief, dan tidak memanggil ZeroGPU.

## Menjalankan satu batch harian

Setelah dry-run menunjukkan empat `next_candidates` dan Anda memang ingin memulai generation:

```bash
cd ~/stockforge-ai
export PYTHONPATH=src
export STOCKFORGE_HOME="$HOME/.stockforge"
termux-wake-lock
python3 scripts/run_backlog_preview_batch.py \
  --backlog "$HOME/stockforge-backlog-v2/StockForge_Backlog_v2_2026-08-27.json" \
  --project stock-assets \
  --daily-cap 4 \
  > "$HOME/stockforge-batch-day.log" 2>&1
termux-wake-unlock
```

`termux-wake-lock` membantu mencegah Android menidurkan proses selama runner berjalan. Tetap matikan battery optimization untuk Termux jika Android masih menghentikan proses. Runner mengirim request serial, menulis log, lalu menyimpan state atomik setelah setiap kandidat.

## Resume dan batas keamanan

Jalankan command yang sama pada jendela berikutnya. Runner memakai state lokal di folder `portfolio-plans` dan menghitung jendela 24 jam dari percobaan pertama. Candidate `preview_ready` selalu terminal. Jika provider mengembalikan quota/error, runner mencatat `provider_error_no_auto_retry`, masuk cooldown, dan tidak mengirim candidate itu maupun candidate berikutnya dalam jendela aktif. Setelah jendela 24 jam reset, candidate yang gagal menjadi item berikutnya untuk dicoba satu kali; preview yang sudah sukses tetap tidak diulang. Jika proses mati ketika request masih `in_flight`, runner tidak mengirim ulang secara otomatis; periksa log dan endpoint terlebih dahulu. Ini sengaja mencegah pemakaian quota ganda.

Preview yang berhasil akan diekspor oleh pipeline existing ke folder preview visual yang ditentukan konfigurasi. JSON, log, dan state tetap berada di workspace, bukan folder Android visual.

## Setelah preview muncul

Review preview secara manual. Beri keputusan `KEEP` atau `REJECT` per candidate. Hanya candidate `KEEP` yang boleh diteruskan ke `prepare-master` dan satu finalizer yang sesuai. JPEG memakai protected RealESRGAN finalizer; PNG memakai finalizer alpha terisolasi. Runner ini tidak memanggil Kaggle dan tidak menyiapkan upload Adobe.

## Quality invariants

Prompt dan negative prompt backlog disalin ke plan tanpa rewrite; canvas backlog tetap square; profile tetap `z-image-turbo`; batch size tetap satu; tidak ada parallel generation; provider error menghentikan batch dan memulai cooldown sampai reset quota; dan human review tetap wajib sebelum finalisasi. Active ZeroGPU API menerima prompt, ukuran, steps, seed, randomize flag, serta job id; negative prompt tetap dicatat sebagai provenance/quality contract karena endpoint aktif belum mengekspos field negative prompt terpisah.
