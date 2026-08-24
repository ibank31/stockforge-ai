# Adobe Stock Multi-format Evidence

**Purpose:** Evidence base for StockForge's format router. This record does not make a claim about demand or acceptance of any individual asset.

## Official Adobe requirements and implications

| Format / category | Official evidence | StockForge implication |
|---|---|---|
| Generative AI | Adobe lists JPEG, AI, EPS, and SVG as accepted formats in its generic content-upload table; GenAI content must be labeled as created using generative AI. | JPEG remains the verified raster GenAI default. Native-vector candidates must be genuine SVG/EPS/AI, not a raster file relabeled as vector. |
| PNG transparent assets | Adobe requires PNG, sRGB, 4–100 MP, at most 45 MB, no watermark, and a transparent—not solid-color—background. Adobe also says to minimize excess canvas around the subject. | A white-background JPEG converted to PNG is not a PNG asset path. The exporter needs an actual alpha quality gate before enabling this route. |
| Vectors | Adobe accepts AI, EPS, and SVG vectors. Customers receive the original vector plus a JPEG preview; Adobe automatically creates a transparent PNG when the vector has transparent or flat-color background. | Native SVG is a high-leverage first vector route. Do not generate a raster and image-trace it as a default. |
| Raster/illustration | Adobe accepts original high-quality raster illustrations, including stylized, abstract, and conceptual compositions. | Textured/material concepts should stay raster JPEG; no reason to force vector where editable paths would not preserve the asset's value. |
| Distinct GenAI content | Adobe requires rights to submit, GenAI disclosure, accurate category/metadata, unique value, and avoidance of multiple similar prompt iterations. | The router should select one product format/brief, not export the same artwork indiscriminately as JPEG, PNG, and vector. |

## Sources

1. https://helpx.adobe.com/stock/contributor/content-policies-guidelines/content-policies/content-upload-guidelines.html
2. https://helpx.adobe.com/stock/contributor/submit-your-content/submit-pngs/technical-requirements-png-submission.html
3. https://helpx.adobe.com/stock/contributor/submit-your-content/submit-vectors/vector-submission-overview.html
4. https://helpx.adobe.com/stock/contributor/submit-your-content/submit-illustrations/illustration-submission-overview.html
5. https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html
