const DEFAULT_HF_SPACE = "https://ibank31-stockforge-zerogpu.hf.space";
const VISION_MODEL = "@cf/meta/llama-3.2-11b-vision-instruct";
const REASONING_MODEL = "@cf/meta/llama-3.1-8b-instruct";
const MAX_REFERENCE_BYTES = 8 * 1024 * 1024;
const ALLOWED_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}
function now() { return new Date().toISOString(); }
function id(prefix) { return `${prefix}_${crypto.randomUUID().replaceAll("-", "")}`; }
function token() { return crypto.randomUUID().replaceAll("-", ""); }
function cleanText(value, fallback = "") {
  if (typeof value === "string") return value.replace(/\s+/g, " ").trim() || fallback;
  if (Array.isArray(value)) return value.map(v => cleanText(v)).filter(Boolean).join("; ") || fallback;
  return fallback;
}
function parseJson(value) {
  if (value && typeof value === "object") return value;
  if (typeof value !== "string") return null;
  let text = value.trim().replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
  try { return JSON.parse(text); } catch (_) {}
  const first = text.indexOf("{");
  const last = text.lastIndexOf("}");
  if (first >= 0 && last > first) {
    try { return JSON.parse(text.slice(first, last + 1)); } catch (_) {}
  }
  return null;
}
function unwrapResult(raw) {
  const root = parseJson(raw) || {};
  if (root.result && typeof root.result === "object") return root.result;
  if (typeof root.result === "string") return parseJson(root.result) || { visual_summary: root.result };
  if (root.response && typeof root.response === "object") return root.response;
  if (typeof root.response === "string") return parseJson(root.response) || { visual_summary: root.response };
  return root;
}

async function initDb(db) {
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS references_sf (id TEXT PRIMARY KEY, token TEXT NOT NULL, r2_key TEXT NOT NULL, filename TEXT, mime_type TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, analysis_json TEXT, created_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS workflows_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, progress INTEGER NOT NULL, message TEXT, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS jobs_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, prompt TEXT, width INTEGER, height INTEGER, steps INTEGER, seed INTEGER, randomize_seed INTEGER, event_id TEXT, raw_r2_key TEXT, final_r2_key TEXT, asset_token TEXT, result_json TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS plans_sf (reference_id TEXT PRIMARY KEY, plan_json TEXT NOT NULL, created_at TEXT NOT NULL)`),
  ]);
}

function normalizeFacts(raw, fallbackText = "") {
  const root = unwrapResult(raw);
  const facts = root.reference_facts || root.visual_facts || {};
  const scene = cleanText(root.visual_summary || root.description || root.caption || fallbackText, "No visual summary returned.");
  const visualSignals = Array.isArray(root.commercial_signals) ? root.commercial_signals.map(v => cleanText(v)).filter(Boolean) : [];
  return {
    visual_summary: scene,
    reference_facts: {
      subject: cleanText(facts.subject || root.subject, "Dominant subject not structurally extracted."),
      composition: cleanText(facts.composition || root.composition, "Composition not structurally extracted."),
      viewpoint: cleanText(facts.viewpoint || root.viewpoint, "Viewpoint not structurally extracted."),
      color_direction: cleanText(facts.color_direction || facts.palette || root.color_direction || root.palette, "Color direction not structurally extracted."),
      context: cleanText(facts.context || root.context, "Context not structurally extracted."),
      visible_text_or_brands: cleanText(facts.visible_text_or_brands || facts.text || root.visible_text_or_brands, "No readable brand or text information structurally extracted."),
      people_or_property: cleanText(facts.people_or_property || root.people_or_property, "No identifiable people or recognizable private property structurally extracted."),
    },
    commercial_signals: visualSignals,
  };
}

function fallbackOpportunities(facts) {
  const subject = facts.reference_facts.subject;
  const context = facts.reference_facts.context;
  const base = [
    { angle: "isolated commercial communication", composition: "clean hero composition with generous copy space", viewpoint: "three-quarter close view", context: "neutral studio-like commercial setting", use_case: "advertising layout and product messaging" },
    { angle: "everyday lifestyle utility", composition: "subject integrated into a believable daily scene", viewpoint: "natural eye-level environmental view", context: context || "routine lifestyle context", use_case: "lifestyle marketing and editorial illustration" },
    { angle: "workflow or process", composition: "multiple contextual elements arranged around the main subject", viewpoint: "slightly elevated documentary view", context: "work or task-oriented environment", use_case: "business process, how-to, or productivity communication" },
    { angle: "wellness or sustainability interpretation", composition: "balanced still life with supporting natural materials", viewpoint: "top-down or controlled overhead view", context: "wellness, responsible-consumption, or sustainability context", use_case: "wellness, sustainability, or responsible-living campaigns" },
    { angle: "seasonal or situational adaptation", composition: "dynamic scene with strong directional space for messaging", viewpoint: "wide environmental perspective", context: "specific seasonal, travel, outdoor, or situational context", use_case: "campaign banners, social media, and editorial storytelling" },
  ];
  return base.map((x, i) => ({
    id: `opp_${i + 1}`,
    title: `${x.angle}: ${subject}`,
    subject: `${subject} reinterpreted through ${x.angle}`,
    composition: x.composition,
    viewpoint: x.viewpoint,
    color_direction: i % 2 === 0 ? "natural balanced tones with controlled contrast" : "purposeful contemporary palette aligned to the use case",
    context: x.context,
    use_case: x.use_case,
    why_fit: `The concept keeps the reference's visible commercial signal but changes the presentation and buyer job instead of reproducing the source image.`,
    differences: ["subject treatment", "composition", "viewpoint", "context"],
    similarity_risk: 0.15,
    genericity_risk: 0.25,
    ip_risk: 0,
    commercial_score: 0.65,
  }));
}

function normalizeOpportunity(raw, index) {
  const item = raw && typeof raw === "object" ? raw : {};
  return {
    id: cleanText(item.id, `opp_${index + 1}`),
    title: cleanText(item.title || item.name, `Distinct stock opportunity ${index + 1}`),
    subject: cleanText(item.subject, "New subject treatment derived from the visible reference"),
    composition: cleanText(item.composition, "Distinct commercial composition"),
    viewpoint: cleanText(item.viewpoint, "Distinct camera viewpoint"),
    color_direction: cleanText(item.color_direction || item.color, "Purposeful color direction"),
    context: cleanText(item.context, "New commercial context"),
    use_case: cleanText(item.use_case || item.buyer_job, "Specific buyer use case"),
    why_fit: cleanText(item.why_fit || item.rationale, "Relevant to the visible signal without copying the reference."),
    differences: Array.isArray(item.differences) ? item.differences.map(v => cleanText(v)).filter(Boolean) : [],
    similarity_risk: Number.isFinite(Number(item.similarity_risk)) ? Number(item.similarity_risk) : 0.25,
    genericity_risk: Number.isFinite(Number(item.genericity_risk)) ? Number(item.genericity_risk) : 0.25,
    ip_risk: Number.isFinite(Number(item.ip_risk)) ? Number(item.ip_risk) : 0,
    commercial_score: Number.isFinite(Number(item.commercial_score)) ? Number(item.commercial_score) : 0.6,
  };
}

function enforceDistinctness(opportunities) {
  const seen = new Set();
  return opportunities.filter((item) => {
    const key = [item.subject, item.composition, item.viewpoint, item.context].map(v => v.toLowerCase()).join("|");
    if (seen.has(key)) return false;
    seen.add(key);
    return item.ip_risk < 0.8 && item.genericity_risk < 0.85 && item.similarity_risk < 0.85;
  });
}

async function analyzeVision(env, imageBytes) {
  if (!env.AI) throw new Error("Cloudflare Workers AI binding is unavailable; cannot build reference intelligence.");
  const prompt = `You are the visual forensics layer of a commercial stock-asset factory. Analyze only what is visible in the supplied image.
Do not invent market performance, sales data, brands, identities, or facts not supported by the image.
Return concise factual observations. Do NOT generate creative opportunities yet.
Return JSON with exactly this shape:
{
  "visual_summary": "one factual sentence",
  "reference_facts": {
    "subject": "dominant visible subject and important attributes",
    "composition": "framing, placement, orientation, negative space, depth",
    "viewpoint": "camera angle and distance",
    "color_direction": "palette, lighting, contrast",
    "context": "location or situational context that is actually visible",
    "visible_text_or_brands": "readable text, logos or brands if visibly present; otherwise say none",
    "people_or_property": "identifiable people, recognizable private property, artwork or distinctive objects if visibly present; otherwise say none"
  },
  "commercial_signals": ["2-5 visual inferences about plausible stock buyer jobs, clearly marked as inference"]
}`;
  const result = await env.AI.run(VISION_MODEL, {
    image: Array.from(new Uint8Array(imageBytes)),
    prompt,
    max_tokens: 900,
    temperature: 0.1,
  });
  const rawText = typeof result === "string" ? result : (result?.response || result?.result || result?.description || JSON.stringify(result));
  return normalizeFacts(rawText, rawText);
}

async function reasonOpportunities(env, facts) {
  const schema = {
    type: "object",
    properties: {
      asset_opportunities: {
        type: "array",
        minItems: 5,
        maxItems: 5,
        items: {
          type: "object",
          properties: {
            id: { type: "string" },
            title: { type: "string" },
            subject: { type: "string" },
            composition: { type: "string" },
            viewpoint: { type: "string" },
            color_direction: { type: "string" },
            context: { type: "string" },
            use_case: { type: "string" },
            why_fit: { type: "string" },
            differences: { type: "array", items: { type: "string" } },
            similarity_risk: { type: "number" },
            genericity_risk: { type: "number" },
            ip_risk: { type: "number" },
            commercial_score: { type: "number" }
          },
          required: ["id", "title", "subject", "composition", "viewpoint", "color_direction", "context", "use_case", "why_fit", "differences", "similarity_risk", "genericity_risk", "ip_risk", "commercial_score"]
        }
      }
    },
    required: ["asset_opportunities"]
  };
  const prompt = `You are the opportunity strategist for a professional stock-asset factory. The image has already been visually analyzed.
Your job is NOT to copy the reference. Convert the visible signal into five genuinely different commercial concepts that could be produced as separate stock assets.
Adobe Stock currently emphasizes meaningful concept diversification, commercially relevant unique value, and avoiding merely flipped, recolored, cropped, or compositionally similar iterations. Do not use artist names, real people names, fictional characters, copyrighted works, brands, logos, or government agencies in concepts. Do not invent market statistics.

Reference intelligence:
${JSON.stringify(facts)}

Create exactly five opportunities. Across the five, vary the buyer job and concept, not just style. Each must materially change at least three dimensions: subject treatment, composition, viewpoint, color direction, context.
Reject ideas that are generic enough to fit thousands of unrelated references. A good opportunity should name a concrete buyer need or communication job.
If the reference contains a brand/logo/person/private property, use it only as a compliance warning and design a new concept that avoids reproducing it.
Return ONLY JSON matching this schema:
${JSON.stringify(schema)}`;
  const result = await env.AI.run(REASONING_MODEL, {
    prompt,
    max_tokens: 2600,
    temperature: 0.25,
    response_format: {
      type: "json_schema",
      json_schema: schema,
    },
  });
  const rawText = typeof result === "string" ? result : (result?.response || result?.result || JSON.stringify(result));
  const root = unwrapResult(rawText);
  const rawOpps = Array.isArray(root.asset_opportunities) ? root.asset_opportunities : [];
  return rawOpps.map(normalizeOpportunity);
}

function buildAnalysis(facts, reasoned) {
  const fallback = fallbackOpportunities(facts);
  const merged = enforceDistinctness(reasoned);
  const selected = [...merged, ...fallback].slice(0, 5);
  while (selected.length < 5) selected.push(fallback[selected.length]);
  return {
    schema_version: 3,
    visual_summary: facts.visual_summary,
    reference_facts: facts.reference_facts,
    commercial_signals: facts.commercial_signals,
    asset_opportunities: selected.map(normalizeOpportunity),
    intelligence: {
      architecture: "vision_forensics -> commercial_reasoning -> deterministic_distinctness_guard",
      reasoned_count: reasoned.length,
      fallback_count: Math.max(0, 5 - merged.length),
      review_required: true,
    },
  };
}

async function visionAnalyze(env, imageBytes) {
  const facts = await analyzeVision(env, imageBytes);
  let reasoned = [];
  try {
    reasoned = await reasonOpportunities(env, facts);
  } catch (_) {
    reasoned = [];
  }
  const analysis = buildAnalysis(facts, reasoned);
  if (analysis.asset_opportunities.length < 5) throw new Error("Reference intelligence could not construct five reviewable opportunities");
  return analysis;
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

    await env.ASSET_STORE.put(r2Key, bytes, { httpMetadata: { contentType: file.type } });
    const workflowId = id("wf");
    const timestamp = now();
    await env.DB.batch([
      env.DB.prepare(`INSERT INTO references_sf (id,token,r2_key,filename,mime_type,sha256,bytes,analysis_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)`)
        .bind(referenceId, accessToken, r2Key, file.name || "reference", file.type, hash, file.size, JSON.stringify(analysis), timestamp),
      env.DB.prepare(`INSERT INTO workflows_sf (id,reference_id,status,stage,progress,message,updated_at) VALUES (?,?,?,?,?,?,?)`)
        .bind(workflowId, referenceId, "ready", "ANALYZED", 100, "Reference intelligence is ready; review differentiated commercial opportunities.", timestamp),
    ]);

    return json({
      reference_id: referenceId,
      workflow_id: workflowId,
      file: `/api/assets/${referenceId}?kind=reference&token=${accessToken}`,
      profile: analysis,
      decision: "REVIEW_REQUIRED",
      notice: "Opportunities are derived from visible reference signals, filtered for distinctness and policy risk, and remain human-reviewable.",
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ detail: "Method not allowed" }, 405);
}
