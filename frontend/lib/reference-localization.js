const MODEL = "@cf/google/gemma-4-26b-a4b-it";
const TYPES = new Set(["SOCIAL_MEDIA_POST", "EMAIL_SCREENSHOT", "MARKETPLACE_SCREENSHOT", "PRODUCT_PAGE", "RAW_ASSET", "UNKNOWN"]);

function parse(value) {
  if (value && typeof value === "object") return value;
  if (typeof value !== "string") return null;
  const text = value.trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "");
  try { return JSON.parse(text); } catch {}
  const first = text.indexOf("{");
  const last = text.lastIndexOf("}");
  try { return first >= 0 && last > first ? JSON.parse(text.slice(first, last + 1)) : null; } catch { return null; }
}

function responseText(value) {
  if (typeof value === "string") return value;
  if (!value || typeof value !== "object") return "";
  if (value.primary_asset || value.asset_candidates || value.reference_type) return value;
  for (const candidate of [value.response, value.result, value.output_text, value.choices?.[0]?.message?.content, value.choices?.[0]?.text]) {
    if (typeof candidate === "string" && candidate.trim()) return candidate;
    if (candidate && typeof candidate === "object") {
      if (candidate.primary_asset || candidate.asset_candidates || candidate.reference_type) return candidate;
      const nested = responseText(candidate);
      if (nested) return nested;
    }
  }
  return "";
}

function score(value) {
  const number = Number(value);
  return Number.isFinite(number) ? Math.max(0, Math.min(1, number > 1 ? number / 100 : number)) : NaN;
}

function bbox(value) {
  if (Array.isArray(value) && value.length >= 4) {
    const [x1, y1, x2, y2] = value.map(score);
    if ([x1, y1, x2, y2].every(Number.isFinite) && x2 > x1 && y2 > y1) return bbox({ x: x1, y: y1, width: x2 - x1, height: y2 - y1 });
  }
  if (!value || typeof value !== "object") return null;
  const x = score(value.x ?? value.left ?? value.x_min);
  const y = score(value.y ?? value.top ?? value.y_min);
  const width = score(value.width ?? ((Number.isFinite(Number(value.x_max)) && Number.isFinite(Number(value.x_min))) ? Number(value.x_max) - Number(value.x_min) : NaN));
  const height = score(value.height ?? ((Number.isFinite(Number(value.y_max)) && Number.isFinite(Number(value.y_min))) ? Number(value.y_max) - Number(value.y_min) : NaN));
  if (![x, y, width, height].every(Number.isFinite) || width <= 0 || height <= 0 || x + width > 1.0001 || y + height > 1.0001) return null;
  return { x, y, width: Math.min(width, 1 - x), height: Math.min(height, 1 - y) };
}

function assetCandidate(value) {
  return { label: String(value?.label || value?.name || value?.subject || "").trim(), confidence: score(value?.confidence ?? value?.score) || 0, bbox_normalized: bbox(value?.bbox_normalized || value?.bbox || value?.bounding_box), why_asset: String(value?.why_asset || value?.reason || "").trim() };
}

function sameCandidate(left, right) {
  const a = left.label.toLowerCase();
  const b = right.label.toLowerCase();
  const boxA = left.bbox_normalized;
  const boxB = right.bbox_normalized;
  return a === b && boxA && boxB && boxA.x === boxB.x && boxA.y === boxB.y && boxA.width === boxB.width && boxA.height === boxB.height;
}

function normalize(value) {
  const raw = parse(value) || {};
  const primaryRaw = raw.primary_asset || raw.primary_asset_candidate || raw.primary || {};
  const primary = assetCandidate({ ...primaryRaw, label: primaryRaw?.label || raw.primary_asset_candidate || raw.primary_subject || "" });
  const candidates = (Array.isArray(raw.asset_candidates) ? raw.asset_candidates : Array.isArray(raw.candidates) ? raw.candidates : []).map(assetCandidate).filter(candidate => candidate.label && candidate.bbox_normalized).slice(0, 8);
  if (primary.label && primary.bbox_normalized && !candidates.some(candidate => sameCandidate(candidate, primary))) candidates.unshift(primary);
  return { reference_type: TYPES.has(raw.reference_type) ? raw.reference_type : "UNKNOWN", confidence: score(raw.confidence) || 0, presentation_elements: Array.isArray(raw.presentation_elements) ? raw.presentation_elements.slice(0, 12) : [], evidence_elements: Array.isArray(raw.evidence_elements) ? raw.evidence_elements.slice(0, 12) : [], asset_candidates: candidates.slice(0, 8), primary_asset: primary };
}

function prompt(retry = false) {
  return `You are the spatial asset locator for a commercial visual-asset factory. Analyze ANY supplied image; never assume a fixed subject. Separate presentation/UI/evidence from the actual reusable visual asset. Identify up to 8 plausible reusable asset candidates and give a TIGHT normalized bounding box for each. Exclude UI, text, platform chrome, margins, unrelated background, watermarks and sales-proof elements unless they are themselves the deliberate standalone asset. Coordinates: x=left,y=top,width,height, all 0..1 relative to the full image. Select ONE primary asset using visual salience and standalone commercial reuse potential. For multi-object references, a coherent asset set may be a candidate. For raw assets, the box can cover most of the canvas. If no real asset can be located confidently, use null primary bbox; never invent facts. IMPORTANT: primary_asset must be an object with label, confidence and bbox_normalized; bbox_normalized MUST be an object with numeric x,y,width,height, not an array. Return ONLY a JSON object, no markdown.${retry ? " Previous localization was rejected, so be especially strict about providing a valid primary_asset bbox." : ""} Return ONLY JSON with reference_type, confidence, presentation_elements, evidence_elements, asset_candidates, primary_asset, primary_asset_candidate.`;
}

function dataUrl(bytes, mime) {
  const data = new Uint8Array(bytes);
  let binary = "";
  for (let index = 0; index < data.length; index += 0x8000) binary += String.fromCharCode(...data.subarray(index, Math.min(index + 0x8000, data.length)));
  return `data:${mime};base64,${btoa(binary)}`;
}

async function runLocator(env, imageBytes, mimeType, retry = false) {
  const image = dataUrl(imageBytes, mimeType);
  return env.AI.run(MODEL, {
    messages: [
      { role: "system", content: "Strict visual locator. Return a valid JSON object only." },
      { role: "user", content: prompt(retry) },
    ],
    image,
    response_format: { type: "json_object" },
    max_tokens: 1800,
    temperature: retry ? 0 : 0.02,
    chat_template_kwargs: { enable_thinking: false },
  });
}

export async function locatePrimaryAsset(env, imageBytes, mimeType) {
  if (!env.AI) throw new Error("REFERENCE_AI_UNAVAILABLE");
  let output = normalize(responseText(await runLocator(env, imageBytes, mimeType, false)));
  if (!(output.primary_asset.confidence >= 0.5 && output.primary_asset.label && output.primary_asset.bbox_normalized && output.asset_candidates.length)) output = normalize(responseText(await runLocator(env, imageBytes, mimeType, true)));
  if (!(output.primary_asset.confidence >= 0.5 && output.primary_asset.label && output.primary_asset.bbox_normalized && output.asset_candidates.length)) throw new Error("ASSET_LOCALIZATION_FAILED");
  return { schema_version: 1, stage: "ASSET_LOCALIZATION", ...output, localization: { method: "vision_bbox_normalized", coordinate_system: "full_image_0_to_1", primary_bbox: output.primary_asset.bbox_normalized, confidence: output.primary_asset.confidence } };
}
