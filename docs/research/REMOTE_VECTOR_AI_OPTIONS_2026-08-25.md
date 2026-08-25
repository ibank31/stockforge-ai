# Remote AI Vector Options — Research Notes

## Recraft

Recraft's official API documentation lists raster and vector image generation, image vectorization, style creation, image editing, and account information. The model documentation lists Recraft V4.1 Vector, V4.1 Vector Pro, Utility Vector, and Utility Pro Vector; it states that Vector outputs are exportable and can be reshaped, recolored, and tweaked. The published API pricing page lists V4.1 Vector/Utility Vector at USD 0.08 per image and Pro Vector at USD 0.30 per image. API authentication uses a Bearer token generated in the Recraft profile. This is the strongest immediate candidate for a hosted automated SVG route, but provider output must still pass StockForge's native SVG safety and geometry gates.

## QuiverAI

The official Text-to-SVG API documentation provides `POST /v1/svgs/generations`, models `arrow-1.1` and `arrow-1.1-max`, optional references, instructions, and `n` from 1 to 16. It explicitly describes output as clean and editable SVG. Arrow 1.1 Max is positioned for higher-fidelity dense illustrations, logos, and technical diagrams. The API requires a user API key and supports public or base64 reference images. This is a strong second hosted candidate, especially for art-directed diagram/icon generation; API availability and commercial terms must be confirmed before activation.

## Adobe Firefly

Adobe's user-facing Firefly page supports Text to Vector and SVG download/editing. However, the official Firefly Services API reference currently lists image, video, composite, upscale, and job operations; its generated-image endpoint specifies raster image models and does not document a Text-to-Vector/SVG endpoint. Therefore Firefly is a strong manual quality benchmark and possible future Adobe integration, but it should not be presented as an available automated SVG API route without a confirmed endpoint.

## Open-source research models

StarVector is an Apache-2.0 research/open-source model with 1B and 8B checkpoints. Its official repository describes both text-to-SVG and image-to-SVG generation and reports strong SVG-Bench results, especially for icons and diagrams, but it notes that the models are not intended for natural images or illustrations. Its documented quick start requires CUDA/GPU and substantial model/runtime setup; it is not a lightweight drop-in for the current local machine. OmniSVG is a NeurIPS 2025 research model with text-to-SVG, image-to-SVG, and character-reference SVG generation. Its project page says it targets complex SVG structure and is designed to move beyond oversimplified monochrome icons, but it is research code/weights rather than a verified hosted production endpoint in StockForge.

## Preliminary conclusion

The practical order is: hosted Recraft or QuiverAI for design generation, then StockForge for deterministic safety/geometry/editability QA, packaging, provenance, and manual review. StarVector/OmniSVG are experimental self-hosted alternatives only if a persistent GPU environment is later approved. Adobe Firefly should be used as a visual benchmark unless official API documentation confirms programmatic SVG output.


## StockForge architecture implication

Current `format_router.py` routes every `native_vector` product to `local_native_vector_build` and explicitly states that editable SVG paths are built locally without raster tracing or GPU generation. The remote Gradio adapter is designed around prompt/width/height/steps and remote image artifacts, so it is not yet a vector-aware provider adapter. The new design should add a separate remote-vector route rather than silently changing the local route or sending SVG jobs through the raster worker.

## Options comparison

| Approach | What it contributes | Main tradeoff | Cost / setup | StockForge fit |
| --- | --- | --- | --- | --- |
| Recraft V4.1 Vector API | Hosted text-to-vector generation through `/v1/images/generations/vector`; explicit vector model IDs; API can return URL or base64 and supports a seed; V4.1 Vector is documented as recolorable/editable | Requires a user API token; V4/V4.1 styles are not supported, so art direction must live in prompt/reference controls; provider output still needs sanitization and geometry QA | Official published charge is USD 0.08/image for standard Vector and USD 0.30/image for Pro Vector; moderate adapter work | Strongest direct REST candidate for a production remote-vector route |
| QuiverAI Text-to-SVG / existing MCP | Hosted SVG generation with Arrow 1.1 and Arrow 1.1 Max, instructions, references, and up to 1–16 outputs; existing QuiverAI connector is present in session config but disabled and requires authorization | Public beta/account limits and pricing need confirmation; connector is currently unavailable until enabled/authorized; output quality and structure must be benchmarked | API key or existing connector authorization; moderate adapter work; pricing not claimed here because official pricing page was not retrievable | Strongest low-friction experiment if the user authorizes enabling the existing connector |
| StarVector / OmniSVG self-hosted | Actual research models for text/image-to-SVG; StarVector is Apache-2.0 and reports strengths on icons/diagrams; OmniSVG targets more complex SVG structure | Requires persistent GPU/runtime work, model downloads, security review, and a separate commercial/data-rights review; no verified production endpoint in StockForge | High setup complexity and ongoing compute/storage; no sales or quality guarantee | Experimental fallback, not first implementation |
| Adobe Firefly app/API | Firefly web/Illustrator can produce downloadable editable SVG and is a useful visual benchmark | Current official Firefly Services API reference documents image, video, composite, and upscale endpoints, not a Text-to-Vector/SVG endpoint | Manual app use is available subject to account; automated SVG route not verified | Benchmark only until Adobe documents an SVG API endpoint |

## Recommended integration pattern

Use an AI vector provider only as a remote design engine, not as the final authority. StockForge should compile one buyer-specific brief, call one provider with `n=1`, preserve the raw provider artifact and provenance, quarantine the SVG, reject unsafe elements or external references, normalize namespaces and dimensions without flattening, render a preview, run semantic and geometry QA, and ask the user for a simple visual verdict. Only a human KEEP should allow later evaluation; no finalizer or Adobe package should be reused from the JPEG path.

The first adapter should expose provider-neutral operations: `vector.generate.remote`, `vector.retrieve`, `vector.sanitize`, and `vector.inspect`. Provider-specific fields such as model ID, reference images, instructions, seed, and asynchronous task IDs should remain inside the adapter. The route should record that a remote provider was used, unlike the current local deterministic builder. The output must be proven to remain editable SVG; a provider that returns only a PNG or a visually convincing but flattened embed must fail closed.

The quality loop should separate creative generation from deterministic QA. A visual language model may score the rendered preview for icon recognizability, collisions, hierarchy, and buyer-job fit, but its score is advisory and cannot replace human review. A deterministic SVG inspector must remain authoritative for forbidden raster/script content, external references, dimensions, groups, element counts, stroke envelopes, transformed bounds, clipping, and thumbnail renders. For diagram products, a machine-readable connector/card contract should be retained where possible; free-form AI SVG should not be allowed to bypass it.

## Decision boundary

No connector was enabled and no external provider was called in this research. Recraft requires a new user-supplied API token because no Recraft connector is configured. QuiverAI already has a disabled non-editable connector entry with authorization required. The next practical decision is whether to authorize a single QuiverAI benchmark through that existing connector or to supply a Recraft API token for a direct REST adapter. A benchmark must not be described as proof of sales, acceptance, demand, or marketplace performance.

## References

[1]: https://www.recraft.ai/docs/api-reference/getting-started "Recraft API getting started"
[2]: https://www.recraft.ai/docs/recraft-models/recraft-v4-1 "Recraft V4.1 model documentation"
[3]: https://www.recraft.ai/docs/api-reference/pricing "Recraft API pricing"
[4]: https://www.recraft.ai/docs/api-reference/endpoints "Recraft API endpoints"
[5]: https://www.recraft.ai/docs/api-reference/styles "Recraft API styles"
[6]: https://docs.quiver.ai/api/models/text-to-svg "QuiverAI Text to SVG API"
[7]: https://docs.quiver.ai/api/guides/sandbox-and-test-keys "QuiverAI sandbox and test keys"
[8]: https://developer.adobe.com/firefly-services/docs/firefly-api/api/ "Adobe Firefly API reference"
[9]: https://helpx.adobe.com/firefly/web/generate-vectors/text-to-vector/generate-vectors-using-text-prompts.html "Adobe Firefly Text to Vector user documentation"
[10]: https://github.com/joanrod/star-vector "StarVector official repository"
[11]: https://omnisvg.github.io/ "OmniSVG official project page"
