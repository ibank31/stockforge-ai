import { runReferenceForensics } from "../../lib/reference-forensics.js";

const MAX_REFERENCE_BYTES = 8 * 1024 * 1024;
const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}

export async function onRequestPost(context) {
  const { request, env } = context;
  try {
    if (!env.AI) return json({ detail: "Reference intelligence AI binding is missing" }, 500);
    const form = await request.formData();
    const file = form.get("file");
    if (!(file instanceof File)) return json({ detail: "file is required" }, 400);
    if (!ALLOWED_TYPES.has(file.type)) return json({ detail: "Only JPG, PNG and WebP references are accepted" }, 400);
    if (file.size > MAX_REFERENCE_BYTES) return json({ detail: "Reference exceeds 8 MB" }, 413);
    const bytes = await file.arrayBuffer();
    const analysis = await runReferenceForensics(env, bytes, file.type);
    return json({
      filename: file.name || "reference",
      bytes: file.size,
      mime_type: file.type,
      ...analysis,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const status = /^(REFERENCE_CLASSIFICATION_FAILED|ASSET_DNA_EXTRACTION_FAILED|FORENSICS_MODEL_INVALID_JSON|REFERENCE_AI_UNAVAILABLE)$/.test(message) ? 422 : 500;
    return json({ detail: message }, status);
  }
}
