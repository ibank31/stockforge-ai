const FORENSICS_MODEL = "@cf/google/gemma-4-26b-a4b-it";

function cleanText(value, fallback = "") {
  if (typeof value === "string") return value.replace(/\s+/g, " ").trim() || fallback;
  if (Array.isArray(value)) return value.map(v => cleanText(v)).filter(Boolean).join("; ") || fallback;
  return fallback;
}

function parseJson(value) {
  if (value && typeof value === "object") return value;
  if (typeof value !== "string") return null;
  const text = value.trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
  try { return JSON.parse(text); } catch (_) {}
  const first = text.indexOf("{");
  const last = text.lastIndexOf("}");
  if (first >= 0 && last > first) {
    try { return JSON.parse(text.slice(first, last + 1)); } catch (_) {}
  }
  return null;
}

function extractText(raw) {
  if (typeof raw === "string") return raw;
  if (!raw || typeof raw !== "object") return "";
  if (Array.isArray(raw)) return raw.map(extractText).filter(Boolean).join("\n");
  const candidates = [
    raw.response,
    raw.result,
    raw.output_text,
    raw.description,
    raw.choices?.[0]?.message?.content,
    raw.choices?.[0]?.text,
  ];
  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) return candidate;
    if (candidate && typeof candidate === "object") {
      const nested = extractText(candidate);
      if (nested) return nested;
    }
  }
  return "";
}

function bytesToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, Math.min(i + chunk, bytes.length)));
  }
  return btoa(binary);
}

function arr(value, max = 8) {
  return Array.isArray(value) ? value.map(v => cleanText(v)).filter(Boolean).slice(0, max) : [];
}

function num(value, fallback = null) {
  const n = Number(value);
  return Number.isFinite(n) ? Math.max(0, Math.min(1, n > 1 ? n / 100 : n)) : fallback;
}

function normalizeClassification(raw) {
  const root = parseJson(raw) || {};
  return {
    reference_type: cleanText(root.reference_type, "UNKNOWN"),
    confidence: num(root.confidence, 0),
    presentation_layer_present: Boolean(root.presentation_layer_present),
    presentation_elements: arr(root.presentation_elements, 12),
    evidence_layer_present: Boolean(root.evidence_layer_present),
    evidence_elements: arr(root.evidence_elements, 12),
    asset_layer_present: Boolean(root.asset_layer_present),
    asset_elements: arr(root.asset_elements, 12),
    primary_asset_candidate: cleanText(root.primary_asset_candidate),
    separation_notes: arr(root.separation_notes, 8),
  };
}

function normalizeDna(raw) {
  const root = parseJson(raw) || {};
  return {
    asset_type: cleanText(root.asset_type),
    primary_subject: cleanText(root.primary_subject),
    subject_count: cleanText(root.subject_count),
    morphology: cleanText(root.morphology),
    structure: cleanText(root.structure),
    orientation: cleanText(root.orientation),
    visual_style: cleanText(root.visual_style),
    line_style: cleanText(root.line_style),
    shading: cleanText(root.shading),
    material: cleanText(root.material),
    colors: arr(root.colors, 8),
    distinctive_features: arr(root.distinctive_features, 12),
    asset_function: arr(root.asset_function, 8),
    target_background: cleanText(root.target_background, "transparent"),
    source_background_status: cleanText(root.source_background_status, "unknown"),
    text_as_asset: Boolean(root.text_as_asset),
    logo_or_brand_as_asset: Boolean(root.logo_or_brand_as_asset),
    confidence: num(root.confidence, 0),
  };
}

function validClassification(x) {
  return Boolean(
    x &&
    ["SOCIAL_MEDIA_POST", "EMAIL_SCREENSHOT", "MARKETPLACE_SCREENSHOT", "PRODUCT_PAGE", "RAW_ASSET", "UNKNOWN"].includes(x.reference_type) &&
    x.primary_asset_candidate &&
    x.confidence >= 0.5
  );
}

function validDna(x) {
  return Boolean(
    x && x.asset_type && x.primary_subject && x.visual_style &&
    x.target_background === "transparent" && x.confidence >= 0.5
  );
}

function classificationPrompt() {
  return `You are a forensic intake classifier for a commercial PNG asset factory.
Analyze the supplied image as evidence, not as a generation template.
The image may be a social-media post, email screenshot, marketplace screenshot, product page, poster, presentation, collage, or raw asset.
Your first task is to separate presentation/context/evidence from the likely asset itself.
A dark or white background, email shell, social-media chrome, congratulation text, earnings amount, username, platform logo, reaction UI, watermark, page framing, buttons, or other UI can be PRESENTATION or EVIDENCE and must not automatically be treated as part of the asset.
The actual reusable asset may be much smaller than the screenshot canvas. If there is one illustration/photo embedded inside a page, identify that artwork/photo as the primary asset rather than the page.
Never invent a brand, platform, sales claim, metadata, location, ownership, or hidden object.
Return ONLY valid JSON using exactly:
{
  "reference_type": "SOCIAL_MEDIA_POST|EMAIL_SCREENSHOT|MARKETPLACE_SCREENSHOT|PRODUCT_PAGE|RAW_ASSET|UNKNOWN",
  "confidence": 0.0,
  "presentation_layer_present": true,
  "presentation_elements": ["..."],
  "evidence_layer_present": true,
  "evidence_elements": ["..."],
  "asset_layer_present": true,
  "asset_elements": ["..."],
  "primary_asset_candidate": "specific object or asset family",
  "separation_notes": ["why the candidate is separated from wrapper/evidence"]
}`;
}

function dnaPrompt(classification) {
  return `You are the asset-DNA extractor for a commercial PNG factory.
The image was already classified. Extract only the likely PRIMARY ASSET, not the presentation wrapper or sales-proof text.
The target output is a transparent-background PNG asset.
The source image may contain a black/white/colored presentation background, email shell, congratulation message, earnings amount, username, marketplace UI, watermark, or other context. Treat those as source-context unless the classifier explicitly indicates that they are the actual asset.
Do not copy or preserve visible text, logos, brands, usernames, earnings figures, or interface chrome as asset features.
Describe the primary asset precisely enough for a later creative mutation engine.
Return ONLY valid JSON using exactly:
{
  "asset_type": "illustrated_object|photo_object|icon|clipart|decorative_element|pattern|ui_element|character|object_set|other",
  "primary_subject": "specific subject",
  "subject_count": "exact visible count or approximate count",
  "morphology": "shape and silhouette",
  "structure": "major physical/graphic structure",
  "orientation": "pose/orientation",
  "visual_style": "specific rendering style",
  "line_style": "line characteristics or none",
  "shading": "shading/rendering characteristics",
  "material": "visible or inferred material only when defensible",
  "colors": ["dominant colors"],
  "distinctive_features": ["specific visible features useful for differentiation"],
  "asset_function": ["plausible commercial asset functions grounded in the visual"],
  "target_background": "transparent",
  "source_background_status": "presentation_wrapper|asset_background|unknown",
  "text_as_asset": false,
  "logo_or_brand_as_asset": false,
  "confidence": 0.0
}

REFERENCE CLASSIFICATION:
${JSON.stringify(classification)}`;
}

async function runModel(env, imageBase64, mimeType, prompt) {
  const result = await env.AI.run(FORENSICS_MODEL, {
    messages: [
      { role: "system", content: "You are a strict visual forensics system. Output JSON only." },
      { role: "user", content: prompt },
    ],
    image: imageBase64,
    max_tokens: 1600,
    temperature: 0.05,
    chat_template_kwargs: { enable_thinking: false },
  });
  const text = extractText(result);
  const parsed = parseJson(text);
  if (!parsed) throw new Error("FORENSICS_MODEL_INVALID_JSON");
  return parsed;
}

export async function runReferenceForensics(env, imageBytes, mimeType) {
  if (!env.AI) throw new Error("REFERENCE_AI_UNAVAILABLE");
  const imageBase64 = bytesToBase64(imageBytes);
  const classification = normalizeClassification(await runModel(env, imageBase64, mimeType, classificationPrompt()));
  if (!validClassification(classification)) throw new Error("REFERENCE_CLASSIFICATION_FAILED");
  const dna = normalizeDna(await runModel(env, imageBase64, mimeType, dnaPrompt(classification)));
  if (!validDna(dna)) throw new Error("ASSET_DNA_EXTRACTION_FAILED");
  return {
    schema_version: 2,
    stage: "REFERENCE_FORENSICS",
    reference_classification: classification,
    asset_dna: dna,
    generation_contract: {
      output_type: "PNG",
      alpha_required: true,
      background: "transparent",
      text_allowed: false,
      logos_allowed: false,
      watermarks_allowed: false,
    },
  };
}
