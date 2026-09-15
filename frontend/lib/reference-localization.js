const MODEL = "@cf/moondream/moondream3.1-9B-A2B";
function dataUrl(bytes, mime) { const data = new Uint8Array(bytes); let binary = ""; for (let index = 0; index < data.length; index += 0x8000) binary += String.fromCharCode(...data.subarray(index, Math.min(index + 0x8000, data.length))); return `data:${mime};base64,${btoa(binary)}`; }
function cleanSubject(value) { return String(value || "").replace(/\s+/g, " ").replace(/^['"`]+|['"`]+$/g, "").trim().slice(0, 120); }
function normalizeBox(value) { const x = Number(value?.x_min), y = Number(value?.y_min), x2 = Number(value?.x_max), y2 = Number(value?.y_max); if (![x,y,x2,y2].every(Number.isFinite) || x < 0 || y < 0 || x2 <= x || y2 <= y || x2 > 1.001 || y2 > 1.001) return null; return { x, y, width: Math.min(x2 - x, 1 - x), height: Math.min(y2 - y, 1 - y) }; }
function area(box) { return box ? box.width * box.height : 0; }
async function querySubject(env, image) { const result = await env.AI.run(MODEL, { task: "query", image, question: "Identify the main reusable visual asset in this image. Ignore social-media UI, browser chrome, captions, usernames, buttons, watermarks, prices, comments, and other evidence. Answer with a concise 2 to 8 word noun phrase describing the actual asset that could be redesigned as a commercial stock asset.", reasoning: false, max_tokens: 80, temperature: 0 }); return cleanSubject(result?.answer || result?.response); }
async function detect(env, image, target) { const result = await env.AI.run(MODEL, { task: "detect", image, target, max_objects: 20 }); return Array.isArray(result?.objects) ? result.objects.map((object) => ({ ...object, bbox_normalized: normalizeBox(object) })).filter(object => object.bbox_normalized) : []; }

export async function locatePrimaryAsset(env, imageBytes, mimeType) {
  if (!env.AI) throw new Error("REFERENCE_AI_UNAVAILABLE");
  const image = dataUrl(imageBytes, mimeType);
  const subject = (await querySubject(env, image)) || "main reusable visual asset";
  const targets = [subject, "main object", "main product", "object", "product", "visual asset"];
  let objects = [];
  for (const target of [...new Set(targets)]) {
    objects = await detect(env, image, target);
    if (objects.length) break;
  }
  if (!objects.length) throw new Error("ASSET_LOCALIZATION_FAILED");
  objects.sort((left, right) => area(right.bbox_normalized) - area(left.bbox_normalized));
  const primary = objects[0];
  const confidence = Math.min(0.95, Math.max(0.55, 0.55 + Math.min(0.4, area(primary.bbox_normalized))));
  const candidate = { label: subject, confidence, bbox_normalized: primary.bbox_normalized, why_asset: "Moondream visual query plus zero-shot object detection selected the largest matching reusable asset region." };
  return { schema_version: 2, stage: "ASSET_LOCALIZATION", reference_type: "UNKNOWN", confidence, presentation_elements: [], evidence_elements: [], asset_candidates: objects.slice(0, 8).map((object, index) => ({ label: index === 0 ? subject : `${subject} instance ${index + 1}`, confidence: index === 0 ? confidence : Math.max(0.5, confidence - index * 0.05), bbox_normalized: object.bbox_normalized })), primary_asset: candidate, localization: { method: "moondream_query_detect", coordinate_system: "full_image_0_to_1", primary_bbox: candidate.bbox_normalized, confidence } };
}
