# StockForge Termux Control Plane

## Tujuan

Termux adalah **control plane** StockForge. Perangkat Android tidak mengunduh atau menjalankan checkpoint model. Termux menyimpan konfigurasi non-rahasia, membangun satu generation request yang dibatasi, membuat dan mengklaim job yang spesifik, lalu memanggil worker GPU remote melalui provider adapter. Worker remote melakukan inference; hasil yang berhasil di-ingest kembali ke proyek dan dikemas sebagai satu arsip unduhan. Default saat ini adalah profile `qwen-image`, karena itulah jalur ZeroGPU yang sudah memiliki bukti generation di repository. `z-image-turbo` tetap profile hemat yang harus dipasang hanya pada worker yang secara eksplisit menyatakannya didukung.

Paket unduhan memiliki status `review_ready`. Status ini berarti generation berhasil dipersist dan paket berisi gambar serta provenance ringkas. Status tersebut **bukan** jaminan penerimaan marketplace; compliance, hak, dan penilaian visual manusia tetap diperlukan sebelum submission.

## Instalasi Android

Jalankan sekali dari Termux. Control plane tidak membutuhkan Real-ESRGAN, BasicSR, atau checkpoint lokal; jangan memasang extra `upscale` pada Android. Paket `python-pillow` Termux dipakai sebagai dependency sistem untuk pemeriksaan gambar ringan.

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

Setelah environment aktif, gunakan `python -m stockforge.cli` pada seluruh contoh berikut. Jangan menggunakan `uv run` atau `uv sync --extra dev` pada Termux ini, karena resolver dapat mencoba memasang extra native `upscale` yang tidak dipakai oleh control plane remote.

## Konfigurasi worker GPU remote

Jangan menaruh token API dalam file konfigurasi atau prompt. Simpan token sebagai environment variable Termux dan rujuk hanya **nama** variable tersebut.

```bash
export STOCKFORGE_HF_TOKEN='nilai-token-anda'
stockforge provider configure \
  --id zerogpu \
  --endpoint 'https://RUANG-ANDA.hf.space' \
  --profile qwen-image \
  --secret-env STOCKFORGE_HF_TOKEN \
  --timeout-seconds 300 \
  --score 100
```

Endpoint harus mengekspos endpoint Gradio `generate_remote` StockForge. Perintah berikut hanya mencatat URL, capability, profil model, timeout, dan nama environment variable token. Nilai token tidak ditulis ke `providers.json`.

```bash
stockforge provider list
```

## Membuat proyek dan preflight

```bash
stockforge project create botanical-assets
stockforge generate \
  --project botanical-assets \
  --provider zerogpu \
  --profile qwen-image \
  --prompt 'single fictional vintage botanical postage stamp, tactile analog paper, clean white isolated background, no readable text' \
  --dry-run
```

`--dry-run` tidak memanggil GPU. Outputnya menampilkan provider, model, resolusi 1024×1024, delapan langkah, seed, batch satu gambar, serta estimasi waktu GPU profile. Gunakan preflight sebelum setiap batch untuk memastikan profile dan provider cocok.

## Menjalankan satu generation

```bash
stockforge generate \
  --project botanical-assets \
  --provider zerogpu \
  --profile qwen-image \
  --prompt 'single fictional vintage botanical postage stamp, tactile analog paper, clean white isolated background, no readable text' \
  --seed 42
```

Satu perintah membuat tepat satu job, mengklaim job tersebut berdasarkan ID sehingga tidak mengambil job lain dalam antrean, dan memakai execution identity yang dapat dipulihkan. Semua profile gratis saat ini dibatasi pada 1024×1024, delapan langkah, batch satu, dan satu kandidat per job untuk menghemat kuota provider; guidance mengikuti profile yang dipilih.

Jika berhasil, keluaran JSON menyertakan `job_id`, `execution_id`, `artifact_ids`, dan `release_package.path`. Arsip berada secara default di:

```text
<project>/deliveries/stockforge-<execution-id>.zip
```

Salin atau ekstrak arsip ke penyimpanan unduhan Android:

```bash
unzip -o '<release_package.path>' -d ~/storage/downloads/stockforge-final
```

Arsip hanya memuat `images/`, `manifest.json`, dan `README.txt`; log worker, cache, dan file intermediate tidak ikut.

## Profil model

| Profile | Peran | Batas default |
|---|---|---|
| `qwen-image` | Profile default untuk Space ZeroGPU yang sudah mempunyai bukti generation di repository. | 1024×1024, 8 langkah, batch 1, guidance 1. |
| `z-image-turbo` | Profile hemat untuk worker yang dikonfigurasi mendukung model ini dan telah lulus benchmark internal. | 1024×1024, 8 langkah, batch 1, guidance 0. |

Provider hanya akan dipilih jika metadata profile-nya menyatakan model tersebut didukung. Ini mencegah request Qwen terkirim ke worker yang hanya mendukung Z-Image-Turbo. Kaggle tetap fallback eksperimental sampai storage preflight dan benchmark generation berhasil.

## Kontrol Kaggle

Controller Kaggle sekarang memakai direktori `deploy/kaggle` yang dicek ke repository.

```bash
stockforge kaggle test
stockforge kaggle doctor
stockforge kaggle quota
```

`kaggle doctor` tidak memakai GPU dan membantu memeriksa CLI, autentikasi, metadata kernel, serta worker file. Jangan mendorong kernel atau menggunakan quota Kaggle sebelum doctor berhasil dan benchmark satu gambar tercatat.
