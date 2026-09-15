import { buildReferenceAnalysis } from "../../lib/reference-intelligence.js";

const MAX_REFERENCE_BYTES = 8 * 1024 * 1024;
const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}
function id(prefix) { return `${prefix}_${crypto.randomUUID().replaceAll("-", "")}`; }
function token() { return crypto.randomUUID().replaceAll("-", ""); }

async function initDb(db) {
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS references_sf (id TEXT PRIMARY KEY, token TEXT NOT NULL, r2_key TEXT NOT NULL, filename TEXT, mime_type TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, analysis_json TEXT, created_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS workflows_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, progress INTEGER NOT NULL, message TEXT, updated_at TEXT NOT NULL)`),
  ]);
}

async function sha256Hex(bytes) {
  const buf = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(buf)].map(v => v.toString(16).padStart(2, "0")).join("");
}

export async function onRequestPost(context) {
  const { request, env } = context;
  try {
    if (!env.DB || !env.ASSET_STORE || !env.AI) return json({ detail: "Reference intelligence bindings are incomplete" }, 500);
    await initDb(env.DB);

    const form = await request.formData();
    const file = form.get("file");
    if (!(file instanceof File)) return json({ detail: "file is required" }, 400);
    if (!ALLOWED_TYPES.has(file.type)) return json({ detail: "Only JPG, PNG and WebP references are accepted" }, 400);
    if (file.size > MAX_REFERENCE_BYTES) return json({ detail: "Reference exceeds 8 MB" }, 413);

    const referenceId = id("ref");
    const workflowId = id("wf");
    const accessToken = token();
    const extension = file.type === "image/png" ? ".png" : file.type === "image/webp" ? ".webp" : ".jpg";
    const r2Key = `references/${referenceId}${extension}`;
    const bytes = await file.arrayBuffer();
    const hash = await sha256Hex(bytes);

    const analysis = await buildReferenceAnalysis(env, bytes, file.type);
    const timestamp = new Date().toISOString();

    await env.ASSET_STORE.put(r2Key, bytes, { httpMetadata: { contentType: file.type } });
    await env.DB.batch([
      env.DB.prepare(`INSERT INTO references_sf (id,token,r2_key,filename,mime_type,sha256,bytes,analysis_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)`)
        .bind(referenceId, accessToken, r2Key, file.name || "reference", file.type, hash, file.size, JSON.stringify(analysis), timestamp),
      env.DB.prepare(`INSERT INTO workflows_sf (id,reference_id,status,stage,progress,message,updated_at) VALUES (?,?,?,?,?,?,?)`)
        .bind(workflowId, referenceId, "ready", "ANALYZED", 100, "Reference intelligence passed multimodal forensics and five-opportunity quality gates; human review required.", timestamp),
    ]);

    return json({
      reference_id: referenceId,
      workflow_id: workflowId,
      file: `/api/assets/${referenceId}?kind=reference&token=${accessToken}`,
      profile: analysis,
      decision: "REVIEW_REQUIRED",
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const status = /^(VISUAL_FORENSICS_FAILED|OPPORTUNITY_QUALITY_FAILED|REFERENCE_AI_UNAVAILABLE)/.test(message) ? 422 : 500;
    return json({ detail: message }, status);
  }
}
