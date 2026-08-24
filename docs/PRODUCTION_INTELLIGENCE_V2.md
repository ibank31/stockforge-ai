# StockForge Production Intelligence v2

**Status:** Implementation standard for controlled portfolio generation.  
**Objective:** Improve the probability that each permitted GPU preview is commercially useful, visually specific, distinct, and easy to review. This standard does **not** claim that a model, score, or marketplace policy can guarantee acceptance, sales, or universal quality across every niche.

## 1. Operating principle

> A GPU request is an experiment against a **visual contract**, not a request to "try a prompt".

The system must first prove that a candidate has one buyer job, one primary visual mechanism, one material strategy, a measurable composition, an evidence-backed lane, and a legitimate difference from retained work. A preview that fails its visual contract is a rejected experiment; it does not earn a seed retry or a Kaggle upscale.

Adobe requires GenAI contributors to submit only content that has unique value, to avoid multiple versions or similar prompt iterations, and to select content type and metadata that matches the visual result. [1] Adobe also directs contributors to use accurate, visual-first titles and keywords and to prioritize the first ten keywords by importance. [2]

## 2. Candidate production contract

Every candidate must carry the following contracts before `portfolio generate` can contact a remote provider.

| Contract | Required statement | Local enforcement |
|---|---|---|
| Buyer | One segment, one job, one primary use channel | Reject empty or conflicting brief fields. |
| Subject | One fully visible object or one controlled fused system | Reject ambiguous multi-object verbs and prohibited lane subjects. |
| Visual mechanism | A thumbnail-readable relationship explaining the buyer use | Reject missing or generic mechanism. |
| Material | One primary material family plus supporting material behavior | Reject incompatible material/lane pairs and generic material lists. |
| Composition | Subject placement plus crop and background policy | Require a direction and a copy-space instruction. |
| Copy-space | Direction and minimum usable area | Require an explicit directional field; use a wide canvas only when the brief needs it. |
| Originality | At least two genuine levers beyond seed, crop, or palette | Reject a repeat of a retained concept signature. |
| Metadata | A short visual-first title and visible-content keyword candidates | Do not treat buyer, workflow, GenAI disclosure, or marketplace terms as upload keywords. |
| Risk | Lane-specific banned subjects, IP/device/UI risks, and semantic contradictions | Block locally with no GPU call. |

## 3. Niche and material selection

The ten named lanes remain a **portfolio map**, not a batch-generation order. A lane receives one preview only after its score has a buyer job, evidence reference, distinct subject signature, and no unresolved portfolio collision.

| Asset family | Preferred material grammar | Common failure to block |
|---|---|---|
| `material_atmosphere` | One tangible material study, restrained accent, intentional negative field | Generic wallpaper, scene, multiple unrelated materials. |
| `ui_3d_metaphor` | Translucent acrylic, matte ceramic, paper, or simple modular geometry | Fake dashboard, screen, device, controls, text, compliance seal. |
| `surreal_concept` | One unexpected but physically legible object relationship | Decorative clutter, character-like subject, mixed metaphors, props. |
| `retro_tech_nostalgia` | Abstract modular form, cutout, soft glow, no literal hardware silhouette | Cassette, disk, reel, keyboard, terminal, monitor, cable, label. |
| `craft_element` | One cut/fold/woven material component with a reusable silhouette | Collage sheet, handwriting, stamp, badge/seal, style imitation. |

## 4. Prompt compiler v2

The prompt compiler must emit deliberate sections instead of a long undifferentiated description. It must place the primary subject and spatial relationship before style, then encode material behavior, composition/copy-space constraints, and an explicit exclusion set. The compiler must not include buyer-use terms as visual facts.

```text
Subject anchor → visual relationship → material behavior → composition and copy-space →
background/isolation → quality intent → lane-specific exclusions
```

Positive subject wording may override a generic negative prompt. Therefore a local gate must reject any positive subject phrase that conflicts with a lane rule before the prompt is sent.

## 5. Fast, quota-aware decision policy

| Stage | Compute | Required result | Stop rule |
|---|---|---|---|
| Niche ranking | CPU | A ranked, evidence-linked and distinct candidate | No market evidence or unresolved risk: do not plan. |
| Contract preflight | CPU | `gpu_eligible=true` with all checks recorded | Any blocker: no remote request. |
| ZeroGPU preview | Remote GPU | One artifact tied to one candidate and seed | Composition, subject, lane, or commercial failure: reject concept; no seed retry. |
| Technical and quality screen | CPU | Decodable output, technical report, quality screen, and project distinctness screen | Technical failure: reject; similarity: hold/reject. |
| Semantic review | Vision provider or human | Review visual contract, IP/text risk, anatomy/object integrity, and buyer utility | Missing semantic provider: never silently pass. |
| Kaggle master | Remote GPU | Only a selected preview with clean review record | Any unresolved review: do not upscale. |

## 6. Post-generation learning record

Each candidate receives a structured decision record: pass/review/fail; visible failure reasons; similarity findings; metadata corrections; marketplace outcome when the user supplies it. Lane allocation may change only from recorded evidence—not from a guessed trend, a single accepted file, or a seed retry.

## References

[1]: https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html "Adobe Stock Generative AI content guidelines" (updated 2026-06-11)
[2]: https://helpx.adobe.com/stock/contributor/content-policies-guidelines/metadata/tips-effective-titles-keywords.html "Adobe Stock: Tips for effective titles and keywords" (updated 2026-08-18)

