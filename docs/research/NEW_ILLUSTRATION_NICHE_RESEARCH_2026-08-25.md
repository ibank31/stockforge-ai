# New illustration JPEG niche research

**Tanggal:** 25 Agustus 2026  
**Tujuan:** Memilih satu niche ilustrasi JPEG baru yang berbeda secara material dari `seed_starting_tray_propagation` dan `technical_mechanical_component_illustrations`, lalu menyiapkan satu brief untuk dry-run.

## Baseline boundary

The user reports that the seed-starting tray asset was manually uploaded to Adobe Stock. No portal screenshot, moderation result, acceptance, download, revenue, or sale evidence was provided. This event is therefore recorded only as a user-reported manual upload and does not prove marketplace acceptance or demand. The next niche must be a new illustration lane, not a seed-only retry and not another mechanical component.

## Evidence ledger

| Evidence type | Finding | Interpretation |
|---|---|---|
| Adobe contributor guidance | Adobe recommends choosing a niche, studying buyers, monitoring supply/demand, and mixing evergreen with timely content. Adobe also recommends thinking about how a buyer will use the asset. [1] | Supports an evidence-bound buyer-job workflow; it is not a sales forecast. |
| Pet-welfare buyer job | ASPCA describes regular enrichment as allowing dogs to engage in innate behaviors such as playing, chasing, smelling, chewing, and scavenging; it gives food puzzles, snuffle mats, scent games, and other activities as concrete examples. [2] | Strong evidence that pet-care education and product communication have concrete visual jobs. |
| Pet-welfare safety boundary | RSPCA states that enrichment can support exploration, play, problem-solving, physical/mental stimulation, and wellbeing, while emphasizing safe materials, suitable size, no sharp/loose parts, supervision, and regular inspection. [3] | Enables a useful object illustration while defining conservative exclusions and claims. |
| Adobe supply proxy | Query `pet enrichment toy illustration`: **339 results** in all; the query visibly returns puzzle feeders, chew toys, snuffle-related objects, cat tunnels, bird toys, and pet-care illustrations. [4] | Narrow exact-query supply proxy; lower than broad food/fermentation queries but not proof of scarcity or demand. |
| Adobe supply proxy | Query `sourdough starter`: **273,363 results** in all. Query `fermented dough`: **14,776**. Query `fermentation bread`: **47,999**. [5] [6] [7] | Concrete buyer job exists, but supply is materially denser in the queried terms. |
| Adobe supply proxy | Query `home compost caddy illustration`: **34 results**. [8] | Very narrow exact-query proxy, but buyer-job evidence was weaker in this pass and the subject remains adjacent to the existing horticulture/environment territory. |
| Adobe supply proxy | Query `ceramic repair illustration`: **8,306 results**. [9] | Recognizable craft/repair job, but materially more crowded and more metaphorically varied. |

## Shortlist scorecard

Scores are internal decision support on a five-point scale, not market probability, ranking, approval, conversion, or sales evidence.

| Candidate | Buyer-job clarity | Distinctness from existing lanes | Exact-query supply proxy | Production control | Rights/policy risk | Internal score |
|---|---:|---:|---:|---:|---:|---:|
| **Interactive pet enrichment object / puzzle feeder** | 5 | 5 | 4 | 4 | 3 | **4.20** |
| Sourdough starter fermentation jar | 5 | 4 | 1 | 5 | 4 | 3.80 |
| Home compost caddy | 3 | 4 | 5 | 4 | 4 | 4.00 |
| Ceramic repair / kintsugi bowl | 4 | 5 | 3 | 4 | 3 | 3.80 |

The selected hypothesis is **interactive pet enrichment object illustration**, specifically a single recognizable treat-puzzle feeder / enrichment board for indoor companion-animal care. It wins because the buyer job is concrete, the exact-query proxy is narrow enough to justify a controlled test, the object can be isolated without people or animal anatomy, and it is materially different from horticulture and electromechanical product lanes.

## Selected niche identity

**Lane:** `pet_enrichment_object_illustrations`  
**Brief:** `pet_enrichment_object_illustrations--puzzle-feeder`  
**Primary buyer jobs:** pet-care article, humane-rescue education, veterinary clinic handout, pet-accessory packaging, and companion-animal enrichment guide. These are buyer-job hypotheses, not confirmed customer demand.  
**Asset:** one square JPEG illustration of a single modern interactive treat-puzzle feeder / enrichment board, isolated on a clean warm-white background. The object should be recognizable without an animal, hands, or text.  
**Style:** polished editorial product illustration, soft three-quarter view, limited tactile materials, muted teal/coral/cream palette, clear silhouette, restrained shadow, generous negative space.  
**Must include:** one single feeder board with a small number of visible compartments, rounded safe-looking forms, a few generic treat pieces, a clear interaction surface, no brand or named product.  
**Must avoid:** people, hands, animal faces/bodies, logos, labels, readable text, product claims, medical/behavioral guarantees, sharp exposed parts, loose hazardous components, generic pile of unrelated pet toys, cluttered room, excessive food, and trademark-like product styling.

## Compliance and metadata boundary

This is a generative-AI JPEG illustration and must be declared as created using generative AI if submitted. The image must not claim that the depicted feeder is safe for every animal, prevents anxiety, treats a condition, or guarantees behavioral improvement. The RSPCA safety guidance is used only to define conservative visual exclusions, not as a product certification. A category must be manually reviewed against the final visible subject; a likely candidate is Adobe category **9 — Hobbies and Leisure** because the primary use is companion-animal play/enrichment, but the final portal category must remain human-verified.

## Decision

Proceed to repository registration and dry-run only. Do not call a generation provider until the lane, identity, metadata draft, pre-GPU gate, and one-candidate readiness report are complete and the user explicitly approves one preview.

## References

[1]: https://helpx.adobe.com/stock/contributor/help/artist-hub-migration/creat-what-s-in-demand.html "Adobe Stock — Create what's in demand"
[2]: https://www.aspca.org/pet-care/dog-care/canine-diy-enrichment "ASPCA — Canine DIY Enrichment"
[3]: https://kb.rspca.org.au/categories/companion-animals/dogs/caring-for-my-dog/how-can-i-create-low-cost-diy-enrichment-for-my-cat-or-dog "RSPCA Australia — How can I create low-cost DIY enrichment for my cat or dog?"
[4]: https://stock.adobe.com/search?k=pet+enrichment+toy+illustration "Adobe Stock search — pet enrichment toy illustration"
[5]: https://stock.adobe.com/search?k=sourdough+starter "Adobe Stock search — sourdough starter"
[6]: https://stock.adobe.com/search?k=fermented+dough "Adobe Stock search — fermented dough"
[7]: https://stock.adobe.com/search?k=fermentation+bread "Adobe Stock search — fermentation bread"
[8]: https://stock.adobe.com/search?k=home+compost+caddy+illustration "Adobe Stock search — home compost caddy illustration"
[9]: https://stock.adobe.com/search?k=ceramic+repair+illustration "Adobe Stock search — ceramic repair illustration"


## Implementation and dry-run result

The selected lane was registered as `pet_enrichment_object_illustrations` with concept `puzzle-feeder`. The repository now supports the `product_illustration` asset family, and regression coverage verifies the new identity, prompt contract, square isolated JPEG route, and metadata title. Targeted tests passed **17/17**; the full suite passed **299 passed, 1 skipped, 49 non-blocking Pillow deprecation warnings**.

A one-candidate portfolio batch was created:

| Field | Value |
|---|---|
| Batch | `pet_enrichment_object_illustrations-20260825T064838Z-60a86ece` |
| Plan | `portfolio-plans/pet_enrichment_object_illustrations-20260825T064838Z-60a86ece.json` |
| Brief | `pet_enrichment_object_illustrations--puzzle-feeder` |
| Provider route | `huggingface-zerogpu` |
| Profile | `z-image-turbo` |
| Canvas | square, 1024×1024 preview |
| Batch size | 1 |
| Estimated GPU time | 55 seconds |
| Pre-GPU gate | `gpu_eligible=true`, 7 checks pass, 0 blockers |
| Provider call | **not made** |

The dry-run confirms a remote raster JPEG route, white background, isolated square product framing, human review required, and `READY_UPLOAD_ADOBE` as the eventual user-export branch. Generation is intentionally paused pending the user's explicit approval for one preview of this exact brief.
