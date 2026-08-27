# StockForge Termux Control Plane — Active Runbook

**Updated:** 2026-08-25
**Status:** Active baseline
**Branch:** `main`
**Scope:** JPEG portfolio generation, learning, finalization, and manual Adobe upload preparation

## Prinsip utama

Termux adalah control plane StockForge. Termux menyimpan source, database, project plans, artifacts, provenance, evaluation ledger, Kaggle requests/results, technical bundles, and master lineage. Android hanya menerima dua jenis file visual untuk dilihat pengguna: preview review dan upload-copy JPEG yang sudah disetujui. Jangan membuat folder output tambahan di Download.

> **Folder visual baku:** `/storage/emulated/0/Download/MACHINE STOCKFORGE/`
>
> Isinya hanya `PREVIEW_TO_MANUS/` dan `READY_UPLOAD_ADOBE/`.

ZeroGPU dipakai untuk satu preview terpilih. Kaggle finalizer dipakai untuk satu preview yang telah lulus review dan hanya melalui satu job private. Tidak ada seed-only retry, blind batch, automatic upload, atau automatic submission.

## Sinkronisasi standar

Selalu mulai dari repository `main` dan gunakan fast-forward pull:

```bash
cd "$HOME/stockforge-ai"
test "$(git branch --show-current)" = "main" || { echo 'Branch bukan main; hentikan.'; exit 1; }
git pull --ff-only origin main
```

Source of truth untuk status adalah `docs/STATUS.md`. Handover lintas agent adalah `docs/SESSION_HANDOVER.md`. Kontrak user/engine dan folder adalah `docs/LEARNING_LOOP_POLICY.md`. Jangan memakai dokumen di `docs/archive/` sebagai instruksi operasi aktif.

## Alur resmi satu asset JPEG

```text
market evidence
  → lane dan buyer job dipilih mesin
  → satu portfolio brief
  → dry-run dan pre-GPU gate
  → satu ZeroGPU preview
  → artifact/provenance/review package
  → deterministic auto-critique + niche memory update
  → audit visual sederhana oleh pengguna dan audit teknis oleh mesin
  → portfolio evaluate
  → portfolio learning-summary + portfolio learning-memory
  → prepare-master
  → satu private Kaggle finalizer
  → import-kaggle-master
  → full-resolution master audit
  → prepare-adobe-upload --latest-master --approved
  → JPEG upload-copy + XMP/CSV/checklist
  → pengguna upload dan submit manual di Adobe
```

Pengguna tidak perlu memilih niche, prompt, negative prompt, format, provider, category, atau keyword. Mesin memilih berdasarkan evidence market, buyer job, technical readiness, compliance risk, cost, dan learning history. Pengguna hanya memberi verdict visual bila diminta.

## Alur resmi external renderer

External renderer boleh menjadi sumber render, tetapi tidak boleh melewati audit StockForge. File dari aplikasi luar disalin ke `~/.stockforge/incoming/external/`, kemudian diimpor satu per satu dengan command berikut:

```bash
cd "$HOME/stockforge-ai"
export PYTHONPATH="$PWD/src"
python3 -m stockforge.cli portfolio import-external \
  --project stock-assets \
  --source "$HOME/.stockforge/incoming/external/<nama-file>" \
  --candidate-id <candidate-id> \
  --provider chatgpt
```

Command ini menyalin file ke `artifacts/external/`, menghitung SHA-256, membuat artifact dan execution `image.import_external`, mencatat provenance, menjalankan pemeriksaan raster/true-alpha CPU-only, memperbarui auto-critique konservatif, dan mengekspor hanya preview visual. Import tidak melakukan crop, resize, ekstraksi alpha, konversi format, ZeroGPU, Kaggle, KEEP/REJECT, package Adobe, atau submission. Untuk dua source yang sedang diuji, gunakan `png-v2-002` untuk crate dan `jpeg-external-e-cargo-battery-swap` untuk scene e-cargo. Source PNG yang secara konsep akan menjadi JPEG tetap dicatat sebagai `source_encoding=PNG`; finalizer/export JPEG nanti harus membuat file JPEG yang sesungguhnya.

Setelah import, pengguna menilai hasil visual dan menjalankan `portfolio evaluate`. Hanya setelah verdict `accept`/KEEP yang eksplisit, pipeline format yang sesuai boleh dilanjutkan. Crate PNG 1536×1024 belum boleh dikirim ke PNG finalizer yang saat ini mensyaratkan input square 1024×1024 tanpa kebijakan crop/resize yang disetujui; jangan melakukan mutasi diam-diam.

## Output Android

Generation yang berhasil mengekspor satu preview visual ke:

```text
/storage/emulated/0/Download/MACHINE STOCKFORGE/PREVIEW_TO_MANUS/
```

Upload preparation yang berhasil mengekspor satu JPEG yang disetujui ke:

```text
/storage/emulated/0/Download/MACHINE STOCKFORGE/READY_UPLOAD_ADOBE/
```

Kode sumber membakukan root tersebut dengan `USER_VISIBLE_ROOT = "MACHINE STOCKFORGE"`. Folder visual tidak boleh berisi JSON, JSONL, CSV, ZIP, Markdown, log, request, database, model weights, PNG intermediate, atau XMP sidecar. File teknis tetap berada di project workspace, terutama di `adobe-upload-bundles/`, `artifacts/`, `masters/`, `evaluations/`, dan `master-finalizer-requests/`.

Jangan menggunakan atau membuat lagi `Download/AdobeStock/`, `Download/stockforge-review/`, `Download/stockforge-final/`, atau folder ekspor lama lain.

## Menjalankan portfolio generation

Untuk asset baru, gunakan perintah portfolio yang menyimpan brief di project. Tampilkan lane dan readiness terlebih dahulu; perintah ini tidak menggunakan GPU:

```bash
python -m stockforge.cli portfolio lanes
python -m stockforge.cli portfolio asset-types
```

Setelah mesin menetapkan lane dan brief, jalankan `portfolio show` dan `portfolio generate --dry-run`. Gunakan path plan serta `brief_id` yang dikeluarkan CLI; jangan menebak tanggal atau membuat path manual. Hapus `--dry-run` hanya setelah pre-GPU gate lulus. Satu command live hanya boleh menghasilkan satu candidate.

Output live harus memiliki artifact ID, execution ID, release package, Android preview export, dan auto-critique advisory bila portfolio context tersedia. Auto-critique berjalan setelah artifact tersimpan, tidak memanggil GPU kedua, tidak memanggil Kaggle, dan tidak mengubah prompt secara retroaktif. Jika live request gagal, baca error dan log, dokumentasikan, lalu berhenti. Jangan mengulang hanya dengan seed lain.

## Learning wajib setelah setiap review

Setiap generation yang selesai atau ditolak harus masuk evaluation ledger. Generation portfolio yang sukses juga membuat auto-critique di project-local `learning/auto-critiques/` dan memperbarui `learning/niche-memory.json`. Gunakan `portfolio evaluate` setelah review teknis dan visual, lalu `portfolio learning-summary` untuk evidence review dan `portfolio learning-memory` untuk melihat memory otomatis. Auto-memory hanya menyimpan observasi deterministik dan hipotesis belum terverifikasi; ia tidak memprediksi sales, tidak memberi KEEP otomatis, tidak mengubah prompt asli, dan tidak memicu generation otomatis.

Satu evaluation tidak cukup untuk menaikkan lane menjadi terbukti. Keputusan berikutnya tetap harus memakai evidence market dan perbedaan produk yang material.

## Finalizer Kaggle

Gunakan finalizer hanya setelah preview lolos review. `prepare-master`, `kaggle-finalizer doctor`, `kaggle-finalizer status`, `kaggle-finalizer output`, dan `import-kaggle-master` tidak menggunakan GPU. Hanya `kaggle-finalizer submit` yang mengirim job GPU private. Untuk satu preview, kirim satu job saja.

Setelah status Kaggle `COMPLETE`, unduh output ke project workspace, lalu import folder yang langsung berisi `result.json`, `master.jpg`, dan `master.upscaled.png`. Master harus lulus 4–100 MP policy yang berlaku, RGB, embedded sRGB, decodable JPEG, dan full-resolution visual audit. Preview WebP tidak pernah menjadi upload file.

## Paket siap upload Adobe

Setelah master lulus audit visual dan pengguna secara eksplisit mengizinkan persiapan upload-copy, gunakan:

```bash
cd "$HOME/stockforge-ai"
python -m stockforge.cli portfolio prepare-adobe-upload --project stock-assets --latest-master --approved
```

Default technical bundle sekarang dibuat di project-local `adobe-upload-bundles/`, bukan di Download. Hanya JPEG upload-copy yang disalin ke `READY_UPLOAD_ADOBE/`. Mesin otomatis membuat filename aman, title, maksimum 49 visual-first keywords, XMP title/keywords, CSV resmi, category mapping yang sudah direview, technical report, GenAI marker, dan manual checklist.

Status bundle bukan approval Adobe. Pengguna tetap harus membuka JPEG, memeriksa metadata portal, memilih atau mengonfirmasi `Created using generative AI tools`, mengonfirmasi rights/releases sesuai keadaan sebenarnya, menerima Terms, menyelesaikan CAPTCHA, dan menekan Submit secara manual. StockForge tidak melakukan tindakan portal tersebut.

## Current verified reference

Reference asset adalah `technical_mechanical_component_illustrations--rotor-armature`. Preview execution `d3c2c121-77c7-590c-97b1-3da15ff26dcc` menghasilkan artifact `d419cdcf-da49-49f8-98c4-5ef4c8415920`. Satu private Kaggle finalizer job menghasilkan master JPEG 4096×4096, 16.777216 MP, RGB, embedded sRGB, JPEG quality 95, 4:4:4. Master lulus deterministic technical gate dan empat-tile full-resolution audit. Niche tetap promising but unproven; positioning yang benar adalah conceptual electromechanical rotor/armature illustration, bukan CAD, blueprint, certified drawing, dimensional reference, atau manufacturer-specific component.

## Non-negotiable safety

Jangan menghapus project workspace, database, learning ledger, master lineage, atau source repository saat membersihkan Download. Jangan membuka kembali image yang secara eksplisit dilarang oleh handover. Jangan menjalankan generation, finalizer, upload, atau submission hanya karena dokumen lama menyebutnya sebagai next step. Selalu periksa `STATUS.md` dan `SESSION_HANDOVER.md` terlebih dahulu.
