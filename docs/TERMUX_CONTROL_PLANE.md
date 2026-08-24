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
  --profile qwen-image \
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
  --profile qwen-image \
  --prompt 'single translucent resin pebble with a soft internal sage-to-coral gradient and frosted microtexture' \
  --seed 42 \
  --dry-run
```

`--dry-run` tidak memanggil GPU. Output harus menunjukkan profile, resolusi 1024×1024, delapan langkah, batch satu, satu kandidat, dan `asset_policy: standalone_single_subject_v1`.

## Menjalankan satu generation

Hapus `--dry-run` hanya setelah preflight benar.

```bash
python -m stockforge.cli generate \
  --project standalone-portfolio \
  --provider zerogpu \
  --profile qwen-image \
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

`qwen-image` adalah profile default untuk Space ZeroGPU. `z-image-turbo` hanya boleh dipakai pada worker yang menyatakan profile tersebut didukung. Kaggle tetap fallback eksperimental; lakukan `python -m stockforge.cli kaggle test`, `doctor`, dan `quota` sebelum memakai quota GPU.
