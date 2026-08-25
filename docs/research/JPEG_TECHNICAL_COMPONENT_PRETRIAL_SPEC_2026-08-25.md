# JPEG Pretrial Specification — Technical Mechanical Component Illustration

**Tanggal:** 25 Agustus 2026  
**Status:** Draft pretrial; **belum diotorisasi untuk generation**.  
**Hypothesis ID:** `jpeg_technical_component_first_sale_v1`

## 1. Buyer hypothesis

Buyer yang dituju adalah content designer, technical writer, educator, small industrial supplier, repair/manual publisher, atau B2B marketer yang membutuhkan **satu visual konseptual untuk menjelaskan kelas komponen elektromechanical** dalam artikel, dokumentasi, materi pendidikan, atau industrial explainer—tanpa memakai foto produk bermerk.

Nilai produk bukan akurasi CAD atau engineering certification. Nilainya adalah focal subject yang langsung dikenali, silhouette bersih, material/shape yang memberi konteks mechanical, dan komposisi yang mudah ditempatkan pada layout editorial atau web.

## 2. Produk dan batas format

| Field | Kontrak |
|---|---|
| Asset type | `raster_illustration` |
| Delivery format | JPEG RGB/sRGB melalui jalur Adobe gate |
| Subject | Satu conceptual electromechanical component |
| Framing | Isolated on clean neutral light background; subject large enough for thumbnail recognition |
| Scene | Tidak ada manusia, tangan, tool tambahan, device, screen, workbench, diagram labels, atau environment clutter |
| Text | Tidak ada readable text, numbers, dimension marks, model numbers, or labels |
| Branding | Tidak ada logo, manufacturer mark, trademark, recognizable product design, or packaging |
| Technical claim | Tidak menyebut CAD, engineering standard, certified dimension, safety, fit, or real product identity |
| Buyer utility | Article, manual/explainer, education, technology/industry content, catalog concept |
| File family | One standalone JPEG; bukan PNG transparency, SVG/vector, CAD, or photograph |

## 3. Component class selection

Trial harus memilih satu kelas yang dapat disebut secara konservatif dari bentuk aktual. Kandidat awal paling aman adalah **conceptual electromechanical rotor/armature component** atau **conceptual threaded mechanical connector**, tetapi hanya satu yang dipilih sebelum prompt compilation. Jangan menggabungkan rotor, fitting, spark plug, motor, and connector menjadi “mechanical object” yang ambigu.

Nama final mengikuti visual yang benar-benar terlihat. Bila hasil tidak mendukung identifikasi kelas part, metadata harus turun menjadi `conceptual mechanical component illustration` dan candidate dapat ditolak karena buyer tidak dapat mengenali kegunaannya.

## 4. Visual identity

Ciri khas lane harus berupa **precision-friendly stylized technical illustration**: strong axial geometry, readable cylindrical/rotational structure, restrained industrial palette of copper/brass, graphite, muted teal or steel gray, one controlled accent, crisp edge hierarchy, subtle dimensional shading, and a clean editorial presentation. Illustration boleh stylized, tetapi tidak boleh menjadi pseudo-CAD dengan detail palsu.

Komposisi harus menggunakan one focal object, three-quarter or orthographic-like readable angle selected by the compiler, controlled contact shadow only if it improves grounding, generous quiet area for editorial placement, and no unrelated prop. The object must occupy enough of the canvas to be recognized in thumbnail while retaining a small amount of breathing room.

Distinctness must come from the component class, silhouette, axial construction, material relationship, and buyer context—not from a random color swap, crop, rotation, or repeated near-duplicate.

## 5. Prompt contract

Prompt compiler harus menyatakan: one conceptual electromechanical component; visible mechanical structure; clear silhouette; restrained copper/brass/graphite/steel palette; precise edge hierarchy; controlled studio illumination; clean neutral background; editorial explainer utility; and no false technical labeling. Prompt harus meminta visual originality tanpa nama artist, known product, manufacturer, trademark, franchise, or reference image.

Negative contract wajib meliputi: readable text, letters, numbers, dimension lines, labels, logos, watermarks, signatures, manufacturer marks, trademarks, brand-specific housings, known product resemblance, CAD screenshot, UI, screen, human, hand, tool, workshop clutter, multiple unrelated parts, deformed cylinders, impossible threads, broken symmetry, melted metal, duplicate components, floating fragments, excessive chrome, plastic toy look, noisy background, oversharpening, halos, chromatic aberration, compression artifacts, and false certification symbols.

## 6. Rights, legal, and release decisions

Tidak boleh ada recognizable person, hand, property, brand, manufacturer, trademark, fictional character, or known creative work. People/property release should remain **not applicable only if the final image truly contains none**. GenAI declaration must be selected in the Adobe portal because the image generation route is generative. Category remains manual-review-required; possible choices depend on final visual intent and must not be guessed by the compiler.

Technical accuracy is not automatic legal clearance. The review must explicitly mark whether the image is clearly conceptual and whether its title/keywords avoid claims that a buyer could reasonably interpret as real engineering specification.

## 7. Preview review questions

| Question | Pass condition |
|---|---|
| Can a buyer identify the object class within two seconds at thumbnail size? | Yes, or title/metadata would remain conservative and candidate is reviewed/rejected |
| Is there one focal subject? | Exactly one component; no accidental second object |
| Does the silhouette communicate mechanical function? | Geometry and axial/connector structure are readable |
| Does the image look like a purposeful illustration rather than random AI object? | Coherent construction, material logic, shadow, and edge hierarchy |
| Is it safe from brand/IP/text contamination? | No visible marks, lettering, numbers, recognizable product/trade dress |
| Is it clearly conceptual rather than falsely precise? | No dimensions, standards, certification, or implied real product identity |
| Is it useful for a buyer layout? | Clean background, crop tolerance, and enough quiet area |
| Is metadata truthful? | Every title/keyword/category decision is supported by visible inventory and intended buyer job |
| Does JPEG technical QA pass? | Adobe gate pass; semantic/commercial review still required |

## 8. Metadata preflight

Draft title pattern: **“Conceptual electromechanical component illustration for engineering documentation”** only if the visible subject supports it. Safer fallback: **“Conceptual mechanical component illustration on a clean background”**.

Possible keywords are limited to visually and contextually supported terms such as `mechanical component`, `electromechanical`, `industrial technology`, `engineering illustration`, `technical illustration`, `rotor`, `armature`, `connector`, or `machine part`. Use `rotor`, `armature`, or `connector` only when that class is visibly justified. Do not add `CAD`, `blueprint`, `photo`, `3D render`, `motor`, `spark plug`, `industrial standard`, `certified`, `dimension`, manufacturer, model number, or safety terms unless factually true and visibly supported.

Category must be reviewed manually. The compiler may present `Technology`, `Science`, or another candidate based on subject/context/intent, but it must not finalize the category automatically. `portfolio metadata-preflight` is report-only and must not perform upload or submit.

## 9. One-candidate trial rule

If authorized, generate exactly one candidate with the selected component class and one prompt package. Do not run batch generation, random seed retries, color-only variants, or a second call merely because the first result is imperfect. The first candidate is evidence: its review determines whether the lane/prompt contract improves or is rejected.

No Kaggle upscale is required before composition/semantic review. If the candidate survives review, the target-runtime Real-ESRGAN benchmark and finalizer path are evaluated separately. Original master remains unchanged; any upload copy is created only after explicit human approval.

## 10. Explicit authorization gate

Generation may begin only after the user explicitly approves this exact pretrial hypothesis and one-candidate JPEG trial. Approval must not be inferred from general instructions to mature JPEG. Until then, this document remains planning evidence only.
