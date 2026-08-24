# StockForge Termux Control Plane

## Tujuan

Termux adalah **control plane** StockForge. Android tidak mengunduh atau menjalankan checkpoint model. Termux menyimpan konfigurasi non-rahasia, membangun satu generation request yang dibatasi, membuat dan mengklaim job spesifik, lalu memanggil worker GPU remote. Worker melakukan inference, hasil di-ingest kembali ke proyek, dan satu paket unduhan dibuat untuk setiap execution sukses.

Control plane sekarang menerapkan kebijakan `standalone_single_subject_v1` pada setiap `generate`. Anda memberi **subject**, bukan scene atau prompt panjang. Sistem menambahkan aturan: satu subjek lengkap, latar putih bersih, tanpa scene, manusia, tangan, alat, perangkat, layar, angka, text, stamp/postmark, branding, atau props yang tidak diminta.

Paket unduhan berstatus `review_ready`. Ini berarti generation berhasil dipersist dan memiliki provenance ringkas; status tersebut bukan jaminan penerimaan marketplace atau pengganti review hak/compliance manusia.

## Instalasi Android

```bash
pkg update
pkg install git python python-pillow
pip install uv
termux-setup-storage

cd ~/stockforge-ai
rm -rf .venv
uv venv --system-site-packages
uv pip install --python .venv/bin/python 'typer>=0.16,<1.0'
uv pip install --python .venv/bin/python --no-deps -e .

source .venv/bin/activate
python -m stockforge.cli init
```

Jangan menggunakan `uv sync --extra dev` pada Termux; control plane remote tidak membutuhkan checkpoint lokal, BasicSR, atau Real-ESRGAN.

## Konfigurasi worker GPU remote

```bash
export STOCKFORGE_HF_TOKEN='nilai-token-anda'
python -m stockforge.cli provider configure \
  --id zerogpu \
  --endpoint 'https://ibank31-stockforge-zerogpu.hf.space' \
  --profile z-image-turbo \
  --secret-env STOCKFORGE_HF_TOKEN \
  --timeout-seconds 300 \
  --score 100

python -m stockforge.cli provider list
```

Hanya nama environment variable yang disimpan pada konfigurasi; nilai token tidak pernah ditulis ke `providers.json` atau manifest.

## Membuat proyek dan preflight

```bash
python -m stockforge.cli project create standalone-portfolio

python -m stockforge.cli generate \
  --project standalone-portfolio \
  --provider zerogpu \
  --profile z-image-turbo \
  --prompt 'single translucent resin pebble with a soft internal sage-to-coral gradient and frosted microtexture' \
  --seed 42 \
  --dry-run
```

`--dry-run` tidak memanggil GPU. Default `--canvas square` menghasilkan 1024×1024. Untuk brief web hero dengan ruang copy yang memang membutuhkan orientasi lebar, gunakan `--canvas hero-landscape` (1344×768); keduanya memakai satu kandidat dan batas pixel yang hampir sama. Ukuran lain sengaja ditolak.

## Menjalankan satu generation

Hapus `--dry-run` hanya setelah preflight benar.

```bash
python -m stockforge.cli generate \
  --project standalone-portfolio \
  --provider zerogpu \
  --profile z-image-turbo \
  --prompt 'single translucent resin pebble with a soft internal sage-to-coral gradient and frosted microtexture' \
  --seed 42
```

Satu perintah membuat tepat satu job. Jangan menjalankan request kedua secara paralel ketika worker masih mengantre atau cold-start.

Jika sukses, output JSON memuat `release_package.path`. Ekstrak ke Download Android:

```bash
unzip -o '<PATH_DARI_release_package.path>' \
  -d ~/storage/downloads/stockforge-final
```

## Lane portofolio awal

| Lane | Contoh subject one-object |
|---|---|
| Material atmosphere | translucent resin pebble, waxed paper sculpture, iridescent glass droplet |
| UI-adjacent 3D metaphor | abstract modular node, floating translucent toggle metaphor, soft geometric stack |
| Playful conceptual object | single cloud-shaped pencil eraser, rubber duck made of folded paper, fruit-shaped cable organizer |
| Retro-tech metaphor | non-branded retro cursor object, pixel-inspired ceramic token, floppy-disk-shaped resin icon |
| Craft/natural motif | hand-cut paper leaf, textile knot, botanical silhouette without stamp/frame/text |

## Profil model dan Kaggle

`z-image-turbo` adalah profile default untuk Space ZeroGPU karena runtime live memakai FP8 Z-Image Turbo yang telah diverifikasi. `qwen-image` tetap profile alternatif dan hanya boleh dipakai pada worker yang secara eksplisit menyatakan dukungannya. Jalur finalizer Kaggle telah lulus benchmark 4× 1024→4096 JPEG sRGB; tetap jalankan `kaggle-finalizer doctor` dan `test`, lalu gunakan hanya untuk preview yang sudah dipilih secara visual.

## Portfolio Engine: Batch Niche yang Aman

Untuk production portfolio, jangan mulai dari prompt bebas atau batch besar. Buat dahulu plan deterministik yang menyimpan buyer job, prompt package, metadata draft, deklarasi GenAI, dan checklist human review. Perintah ini **tidak** memanggil GPU dan tidak membuat aset menjadi `submission_ready`.

```bash
cd ~/stockforge-ai
source .venv/bin/activate

git pull --ff-only origin feat/asset-factory-architecture

# Lihat sepuluh lane riset, tier prioritas, dan batas batch awal.
python -m stockforge.cli portfolio lanes

# Preview dua brief; hasil JSON memuat prompt, negative prompt, metadata, dan checklist review.
python -m stockforge.cli portfolio plan \
  --lane ai_governance \
  --count 2

# Simpan batch plan ke project; contoh lane produksi awal.
python -m stockforge.cli portfolio create-batch \
  --project stock-assets \
  --lane tactile_material_atmospheres \
  --count 5

# Tampilkan plan yang sudah tersimpan sebelum generation.
python -m stockforge.cli portfolio list \
  --project stock-assets \
  --status planned
```

| Tier | Lane | Batas test awal |
|---|---|---:|
| First | `ai_governance` | 20 |
| First | `playful_surreal_product_metaphors` | 20 |
| First | `tactile_material_atmospheres` | 20 |
| Secondary | `synthetic_media_trust`, `returns_recommerce`, `digital_accessibility` | 15 per lane |
| Experimental | `retro_tech_developer_metaphors`, `human_made_collage_elements` | 15 dan 10 |
| Experimental | `circular_packaging_systems`, `software_supply_chain_integrity` | 10 per lane |

Gunakan `portfolio plan` untuk memilih satu brief yang paling sesuai, lalu jalankan melalui `portfolio generate` agar identitas brief dan metadata tetap terhubung dengan hasil. Jalankan **satu kandidat per generation**. Setelah gambar selesai, lakukan technical check, periksa visual pada resolusi penuh, pastikan metadata benar-benar cocok dengan gambar, lalu pertahankan hanya aset yang berbeda secara komersial. Jangan upload beruntun berdasarkan seed, crop, atau perubahan warna saja.

Dokumen desain lengkap dan batasan status ada di [`PORTFOLIO_PRODUCTION_ENGINE.md`](PORTFOLIO_PRODUCTION_ENGINE.md) serta [`PORTFOLIO_DELIVERY_PIPELINE.md`](PORTFOLIO_DELIVERY_PIPELINE.md).

## Menjalankan Satu Brief Portfolio

Setelah plan dibuat, jangan salin prompt secara manual kecuali untuk inspeksi. Gunakan `portfolio show` untuk melihat satu brief dan `portfolio generate` untuk membekukan identitas brief, metadata draft, dan checklist review bersama execution. Cara ini tetap memakai **satu request GPU per perintah**.

```bash
# Ganti dengan path dari output create-batch dan salah satu brief_id dari batch tersebut.
PLAN='/storage/emulated/0/StockForge/projects/stock-assets/portfolio-plans/ai_governance-YYYYMMDDTHHMMSSZ-XXXXXXXX.json'
BRIEF='ai_governance--review-gate'

# Inspeksi brief; tidak memakai GPU.
python -m stockforge.cli portfolio show \
  --project stock-assets \
  --plan "$PLAN" \
  --brief "$BRIEF"

# Preview request remote; tidak memakai GPU.
python -m stockforge.cli portfolio generate \
  --project stock-assets \
  --plan "$PLAN" \
  --brief "$BRIEF" \
  --provider zerogpu \
  --profile z-image-turbo \
  --seed 42 \
  --dry-run

# Jalankan tepat satu brief setelah preview benar.
python -m stockforge.cli portfolio generate \
  --project stock-assets \
  --plan "$PLAN" \
  --brief "$BRIEF" \
  --provider zerogpu \
  --profile z-image-turbo \
  --seed 42

# Untuk brief dengan copy space horizontal yang eksplisit, gunakan salah satu
# kanvas yang dibatasi ini; tidak ada ukuran arbitrer.
python -m stockforge.cli portfolio generate \
  --project stock-assets \
  --plan "$PLAN" \
  --brief "$BRIEF" \
  --provider zerogpu \
  --profile z-image-turbo \
  --canvas hero-landscape \
  --seed 42 \
  --dry-run
```

Output sukses memuat `release_package.path`. Paket ZIP untuk portfolio sekarang berisi image, `manifest.json`, `portfolio_metadata_draft.json`, `portfolio_metadata_draft.csv`, dan `REVIEW_CHECKLIST.md`. Statusnya tetap `review_ready`, bukan `submission_ready`. Metadata dan checklist adalah draft yang harus diperiksa terhadap gambar akhir; jangan mengunggah batch berdasarkan status generation saja.

```bash
unzip -o '<PATH_DARI_release_package.path>' \
  -d ~/storage/downloads/stockforge-review
```

Setelah ekstrak, buka gambar pada ukuran penuh. Lengkapi checklist: hapus keyword yang tidak benar-benar tampak, pastikan tidak ada teks/brand/artefak, bandingkan dengan aset lain agar tidak duplikat, lakukan finalization/technical check bila perlu, dan isi pengungkapan GenAI secara jujur di marketplace. Mesin tidak mengubah `review_ready` menjadi `submission_ready` secara otomatis.


## Master Finalizer via Kaggle: Preview → 4× AI Upscale → Review ZIP

Gunakan jalur ini **hanya setelah** satu preview lolos inspeksi awal. Ia tidak cocok untuk memperbesar semua hasil generation. Command `prepare-master`, `doctor`, `status`, `output`, dan `import-kaggle-master` tidak memakai GPU; hanya `kaggle-finalizer submit` yang mengirim satu job GPU privat.

```bash
# 1. Buat request terikat pada preview yang telah dipilih. Tidak memakai GPU.
REQUEST=$(python -m stockforge.cli portfolio prepare-master \
  --project stock-assets \
  --execution '<EXECUTION_ID_PREVIEW>' \
  --artifact '<ARTIFACT_ID_PREVIEW>' \
  --minimum-megapixels 6 \
  --scale 4 | python -c 'import json,sys; print(json.load(sys.stdin)["path"])')

# 2. Validasi bundle dan akses Kaggle. Tidak memakai GPU.
python -m stockforge.cli kaggle-finalizer doctor
python -m stockforge.cli kaggle-finalizer test

# 3. Jalankan SATU finalizer AI 4× pada GPU Kaggle privat.
# Ini memakai quota GPU Kaggle.
python -m stockforge.cli kaggle-finalizer submit \
  --project stock-assets \
  --request "$REQUEST"

# 4. Periksa status hingga selesai. Tidak memakai GPU tambahan.
python -m stockforge.cli kaggle-finalizer status

# 5. Unduh output Kaggle—termasuk log diagnostik bila job gagal—ke proyek. Tidak memakai GPU.
python -m stockforge.cli kaggle-finalizer output \
  --project stock-assets

# 6. Verifikasi checksum/request/format/ukuran lalu buat ZIP review master.
# Lokasi default result.json dan master.jpg adalah folder berikut.
RESULT_DIR='/storage/emulated/0/StockForge/projects/stock-assets/kaggle-finalizer-output/stockforge-finalizer-output'
python -m stockforge.cli portfolio import-kaggle-master \
  --project stock-assets \
  --request "$REQUEST" \
  --result-dir "$RESULT_DIR"

# Bila audit visual menemukan keyword lane yang tidak tampak di gambar, simpan
# metadata yang telah direview di dalam project lalu terapkan saat import.
# Override ini tetap menghasilkan status review_ready, bukan submission_ready.
python -m stockforge.cli portfolio import-kaggle-master \
  --project stock-assets \
  --request "$REQUEST" \
  --result-dir "$RESULT_DIR" \
  --metadata-review '/storage/emulated/0/StockForge/projects/stock-assets/reviews/metadata-review.json'
```

Worker hanya menerima request `prepared_no_gpu` dengan SHA-256 preview yang cocok. Ia mengunduh bobot RealESRGAN x4plus bila belum tersedia, menghasilkan master JPEG RGB/sRGB, lalu membuat `result.json`; hasil tanpa manifest, checksum, dimensi target, atau gate teknis yang sesuai akan ditolak saat import. Meski sukses, status akhir tetap `review_ready`: periksa master pada ukuran 100%, bandingkan dengan preview, dan jangan upload jika ada detail rekaan, halo, blur, kerusakan tekstur, perubahan objek, pseudo-teks, atau risiko hak/IP. Hapus keyword yang hanya menggambarkan material lane umum tetapi tidak benar-benar terlihat pada master; gunakan `--metadata-review` untuk merekam draft hasil audit tersebut pada paket final.
