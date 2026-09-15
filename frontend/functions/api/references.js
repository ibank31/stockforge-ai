const DEFAULT_HF_SPACE = "https://ibank31-stockforge-zerogpu.hf.space";
const VISION_MODEL = "@cf/llava-hf/llava-1.5-7b-hf";
const MAX_REFERENCE_BYTES = 8 * 1024 * 1024;
const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}
function now() { return new Date().toISOString(); }
function id(prefix) { return `${prefix}_${crypto.randomUUID().replaceAll("-", "")}`; }
function token() { return crypto.randomUUID().replaceAll("-", ""); }

async function initDb(db) {
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS references_sf (id TEXT PRIMARY KEY, token TEXT NOT NULL, r2_key TEXT NOT NULL, filename TEXT, mime_type TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, analysis_json TEXT, created_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS workflows_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, progress INTEGER NOT NULL, message TEXT, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS jobs_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, prompt TEXT, width INTEGER, height INTEGER, steps INTEGER, seed INTEGER, randomize_seed INTEGER, event_id TEXT, raw_r2_key TEXT, final_r2_key TEXT, asset_token TEXT, result_json TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS plans_sf (reference_id TEXT PRIMARY KEY, plan_json TEXT NOT NULL, created_at TEXT NOT NULL)`),
  ]);
}

function parseJsonDeep(value, maxDepth = 5) {
  if (maxDepth < 0) return null;
  if (value && typeof value === "object") return value;
  if (typeof value !== "string") return null;
  let text = value.trim();
  for (let i = 0; i < 2; i++) {
    text = text.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
    try {
      const parsed = JSON.parse(text);
      if (typeof parsed === "string") return parseJsonDeep(parsed, maxDepth - 1);
      return parsed;
    } catch (_) {
      const start = text.indexOf("{");
      const end = text.lastIndexOf("}");
      if (start >= 0 && end > start) {
        try {
          const parsed = JSON.parse(text.slice(start, end + 1));
          if (typeof parsed === "string") return parseJsonDeep(parsed, maxDepth - 1);
          return parsed;
        } catch (_) {}
      }
    }
    const unescaped = text.replace(/\\n/g, "\n").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
    if (unescaped === text) break;
    text = unescaped;
  }
  return null;
}

function firstObject(value) {
  if (!value || typeof value !== "object") return null;
  if (!Array.isArray(value)) return value;
  return value.find(item => item && typeof item === "object") || null;
}

function cleanText(value, fallback = "") {
  if (typeof value === "string") return value.replace(/\s+/g, " ").trim() || fallback;
  if (Array.isArray(value)) return value.map(v => cleanText(v)).filter(Boolean).join("; ") || fallback;
  return fallback;
}

function normalizeOpportunity(raw, index) {
  const item = firstObject(raw) || {};
  const concept = firstObject(item.concept) || {};
  return {
    id: cleanText(item.id, `opp_${index + 1}`),
    title: cleanText(item.title || item.name, `New stock concept ${index + 1}`),
    subject: cleanText(item.subject || concept.subject || item.asset, "A commercially useful new subject"),
    composition: cleanText(item.composition || concept.composition, "A deliberate commercial composition with useful negative space"),
    viewpoint: cleanText(item.viewpoint || concept.viewpoint, "A clearly differentiated camera viewpoint"),
    color_direction: cleanText(item.color_direction || item.color || concept.color_direction || concept.color, "A distinct color direction appropriate to the new use case"),
    context: cleanText(item.context || concept.context, "A new commercial context"),
    use_case: cleanText(item.use_case || item.buyer_job || concept.use_case, "A practical stock-buyer use case"),
    why_fit: cleanText(item.why_fit || item.rationale || item.buyer_relevance, "Derived from the visible reference and redirected to a new commercial use case."),
    differences: Array.isArray(item.differences) ? item.differences.map(v => cleanText(v)).filter(Boolean) : [],
  };
}

function normalizeAnalysis(raw, fallbackText = "") {
  const root = parseJsonDeep(raw) || {};
  const nested = root?.visual_summary && typeof root.visual_summary === "string" && root.visual_summary.trim().startsWith("{")
    ? (parseJsonDeep(root.visual_summary) || root)
    : root;
  const source = nested?.visual_summary && typeof nested.visual_summary === "string" ? nested : root;
  const opportunitiesRaw = Array.isArray(source.asset_opportunities)
    ? source.asset_opportunities
    : Array.isArray(source.opportunities)
      ? source.opportunities
      : [];
  const referenceFacts = source.reference_facts || source.visual_facts || {};
  const analysis = {
    schema_version: 2,
    visual_summary: cleanText(source.visual_summary, cleanText(fallbackText, "No structured visual summary returned.")),
    reference_facts: {
      subject: cleanText(referenceFacts.subject || source.subject, "Dominant subject not structurally extracted."),
      composition: cleanText(referenceFacts.composition || source.composition, "Composition not structurally extracted."),
      viewpoint: cleanText(referenceFacts.viewpoint || source.viewpoint, "Viewpoint not structurally extracted."),
      color_direction: cleanText(referenceFacts.color_direction || referenceFacts.palette || source.color_direction || source.palette, "Color direction not structurally extracted."),
      context: cleanText(referenceFacts.context || source.context, "Context not structurally extracted."),
    },
    commercial_signals: Array.isArray(source.commercial_signals)
      ? source.commercial_signals.map(v => cleanText(v)).filter(Boolean)
      : [],
    asset_opportunities: opportunitiesRaw.slice(0, 5).map(normalizeOpportunity),
  };
  if (analysis.asset_opportunities.length < 5 && Array.isArray(source.asset_opportunities)) {
    analysis.asset_opportunities = source.asset_opportunities.map(normalizeOpportunity).slice(0, 5);
  }
  return analysis;
}

async function visionAnalyze(env, imageBytes) {
  if (!env.AI) throw new Error("Cloudflare Workers AI binding is unavailable; cannot build reference intelligence.");
  const prompt = `You are the Reference Intelligence engine for a commercial stock-asset factory. Analyze the supplied image only.
Return ONE JSON OBJECT and nothing else. Never wrap the JSON in markdown. Do not repeat or reproduce logos, creator names, account names, earnings claims, or readable text from the image.
Schema:
{
  "visual_summary": "one concise factual description of the visible image",
  "reference_facts": {
    "subject": "dominant visible subject",
    "composition": "layout, framing, placement, negative space",
    "viewpoint": "camera/viewpoint",
    "color_direction": "dominant palette and lighting",
    "context": "visible scene/context"
  },
  "commercial_signals": ["3-5 observable buyer/use-case signals, clearly phrased as visual inference, not sales facts"],
  "asset_opportunities": [
    {
      "title": "distinct new stock concept",
      "subject": "new subject or subject treatment",
      "composition": "new composition",
      "viewpoint": "new viewpoint",
      "color_direction": "new color direction",
      "context": "new context",
      "use_case": "specific stock buyer use case",
      "why_fit": "why this is relevant to the reference's visible commercial signal without copying it",
      "differences": ["subject", "composition", "viewpoint", "context"]
    }
  ]
}
Requirements: provide exactly 5 opportunities. Each opportunity must materially change at least 3 of these dimensions: subject, composition, viewpoint, color_direction, context. Keep opportunities tightly relevant to what is visibly present in the reference. Do not invent market performance data.`;
  const result = await env.AI.run(VISION_MODEL, {
    image: Array.from(new Uint8Array(imageBytes)),
    prompt,
    max_tokens: 1800,
  });
  const rawText = typeof result === "string" ? result : (result?.description || result?.response || JSON.stringify(result));
  return normalizeAnalysis(rawText, rawText);
}

async function sha256Hex(bytes) {
  const buf = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(buf)].map(v => v.toString(16).padStart(2, "0")).join("");
}

export async function onRequestPost(context) {
  const { request, env } = context;
  try {
    if (!env.DB || !env.ASSET_STORE) return json({ detail: "Pages control-plane D1/R2 bindings are missing" }, 500);
    await initDb(env.DB);
    const form = await request.formData();
    const file = form.get("file");
    if (!(file instanceof File)) return json({ detail: "file is required" }, 400);
    if (!ALLOWED_TYPES.has(file.type)) return json({ detail: "Only JPG, PNG and WebP references are accepted" }, 400);
    if (file.size > MAX_REFERENCE_BYTES) return json({ detail: "Reference exceeds 8 MB" }, 413);

    const referenceId = id("ref");
    const accessToken = token();
    const extension = file.type === "image/png" ? ".png" : file.type === "image/webp" ? ".webp" : ".jpg";
    const r2Key = `references/${referenceId}${extension}`;
    const bytes = await file.arrayBuffer();
    const hash = await sha256Hex(bytes);
    const analysis = await visionAnalyze(env, bytes);
    if (!analysis.asset_opportunities || analysis.asset_opportunities.length < 5) {
      return json({ detail: "Reference intelligence did not return the required 5 structured opportunities", analysis }, 502);
    }

    await env.ASSET_STORE.put(r2Key, bytes, { httpMetadata: { contentType: file.type } });
    const workflowId = id("wf");
    const timestamp = now();
    await env.DB.batch([
      env.DB.prepare(`INSERT INTO references_sf (id,token,r2_key,filename,mime_type,sha256,bytes,analysis_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)`)
        .bind(referenceId, accessToken, r2Key, file.name || "reference", file.type, hash, file.size, JSON.stringify(analysis), timestamp),
      env.DB.prepare(`INSERT INTO workflows_sf (id,reference_id,status,stage,progress,message,updated_at) VALUES (?,?,?,?,?,?,?)`)
        .bind(workflowId, referenceId, "ready", "ANALYZED", 100, "Reference intelligence is ready; choose a synchronized creative opportunity.", timestamp),
    ]);

    return json({
      reference_id: referenceId,
      workflow_id: workflowId,
      file: `/api/assets/${referenceId}?kind=reference&token=${accessToken}`,
      profile: analysis,
      decision: "REVIEW_REQUIRED",
      notice: "Opportunities are derived from this reference. Commercial interpretation remains reviewable and human-controlled.",
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ detail: "Method not allowed" }, 405);
}
