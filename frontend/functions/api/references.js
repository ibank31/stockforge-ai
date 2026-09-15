const DEFAULT_HF_SPACE = "https://ibank31-stockforge-zerogpu.hf.space";
const VISION_MODEL = "@cf/google/gemma-4-26b-a4b-it";
const REASONING_MODEL = "@cf/google/gemma-4-26b-a4b-it";
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
function extractModelText(raw) {
  if (typeof raw === "string") return raw;
  if (!raw || typeof raw !== "object") return "";
  const candidates = [
    raw?.response,
    raw?.result,
    raw?.choices?.[0]?.message?.content,
    raw?.choices?.[0]?.text,
    raw?.output_text,
    raw?.description,
  ];
  for (const candidate of candidates) {
    if (typeof candidate === "string" && candidate.trim()) return candidate;
    if (candidate && typeof candidate === "object") {
      const nested = extractModelText(candidate);
      if (nested) return nested;
    }
  }
  return "";
}
function unwrapResult(raw) {
  const root = parseJson(extractModelText(raw)) || (raw && typeof raw === "object" ? raw : {});
  if (root.result && typeof root.result === "object") return root.result;
  if (typeof root.result === "string") return parseJson(root.result) || { visual_summary: root.result };
  if (root.response && typeof root.response === "object") return root.response;
  if (typeof root.response === "string") return parseJson(root.response) || { visual_summary: root.response };
  return root;
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
function tokenSet(text) {
  return new Set(cleanText(text).toLowerCase().split(/[^a-z0-9]+/).filter(t => t.length >= 3));
}
function jaccard(a, b) {
  const A = tokenSet(a); const B = tokenSet(b);
  if (!A.size || !B.size) return 0;
  let intersection = 0;
  for (const t of A) if (B.has(t)) intersection += 1;
  return intersection / (A.size + B.size - intersection);
}

async function initDb(db) {
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS references_sf (id TEXT PRIMARY KEY, token TEXT NOT NULL, r2_key TEXT NOT NULL, filename TEXT, mime_type TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, analysis_json TEXT, created_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS workflows_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, progress INTEGER NOT NULL, message TEXT, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS jobs_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, prompt TEXT, width INTEGER, height INTEGER, steps INTEGER, seed INTEGER, randomize_seed INTEGER, event_id TEXT, raw_r2_key TEXT, final_r2_key TEXT, asset_token TEXT, result_json TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS plans_sf (reference_id TEXT PRIMARY KEY, plan_json TEXT NOT NULL, created_at TEXT NOT NULL)`),
  ]);
}

function normalizeFacts(raw) {
  const root = unwrapResult(raw);
  const facts = root.reference_facts || root.visual_facts || {};
  const scene = cleanText(root.visual_summary || root.description || root.caption, "");
  const visualSignals = Array.isArray(root.commercial_signals)
    ? root.commercial_signals.map(v => cleanText(v)).filter(Boolean).slice(0, 5)
    : [];
  return {
    visual_summary: scene,
    reference_facts: {
      subject: cleanText(facts.subject || root.subject),
      composition: cleanText(facts.composition || root.composition),
      viewpoint: cleanText(facts.viewpoint || root.viewpoint),
      color_direction: cleanText(facts.color_direction || facts.palette || root.color_direction || root.palette),
      context: cleanText(facts.context || root.context),
      visible_text_or_brands: cleanText(facts.visible_text_or_brands || facts.text || root.visible_text_or_brands),
      people_or_property: cleanText(facts.people_or_property || root.people_or_property),
    },
    commercial_signals: visualSignals,
  };
}
function validFacts(facts) {
  const f = facts?.reference_facts || {};
  return Boolean(
    facts?.visual_summary &&
    f.subject && f.composition && f.viewpoint && f.color_direction && f.context &&
    [f.visible_text_or_brands, f.people_or_property].some(Boolean)
  );
}
function normalizeOpportunity(raw, index) {
  const item = raw && typeof raw === "object" ? raw : {};
  return {
    id: cleanText(item.id, `opp_${index + 1}`),
    title: cleanText(item.title || item.name, `Distinct stock opportunity ${index + 1}`),
    subject: cleanText(item.subject),
    composition: cleanText(item.composition),
    viewpoint: cleanText(item.viewpoint),
    color_direction: cleanText(item.color_direction || item.color),
    context: cleanText(item.context),
    use_case: cleanText(item.use_case || item.buyer_job),
    why_fit: cleanText(item.why_fit || item.rationale),
    differences: Array.isArray(item.differences) ? item.differences.map(v => cleanText(v)).filter(Boolean).slice(0, 6) : [],
    similarity_risk: Number.isFinite(Number(item.similarity_risk)) ? Number(item.similarity_risk) : 1,
    genericity_risk: Number.isFinite(Number(item.genericity_risk)) ? Number(item.genericity_risk) : 1,
    ip_risk: Number.isFinite(Number(item.ip_risk)) ? Number(item.ip_risk) : 1,
    commercial_score: Number.isFinite(Number(item.commercial_score)) ? Number(item.commercial_score) : 0,
  };
}
function qualityCheckOpportunity(item) {
  const complete = [item.title, item.subject, item.composition, item.viewpoint, item.color_direction, item.context, item.use_case, item.why_fit].every(Boolean);
  const dimensionChanges = new Set(item.differences.map(v => v.toLowerCase())).size;
  return complete && dimensionChanges >= 3 && item.ip_risk < 0.65 && item.genericity_risk < 0.65 && item.similarity_risk < 0.65 && item.commercial_score >= 0.55;
}
function enforceDistinctness(opportunities, referenceSummary) {
  const accepted = [];
  for (const item of opportunities.map(normalizeOpportunity)) {
    if (!qualityCheckOpportunity(item)) continue;
    const fingerprint = `${item.subject}|${item.composition}|${item.viewpoint}|${item.context}`.toLowerCase();
    if (accepted.some(v => v.fingerprint === fingerprint)) continue;
    const refText = `${referenceSummary} ${item.subject} ${item.composition} ${item.viewpoint} ${item.context}`;
    if (jaccard(referenceSummary, item.subject) > 0.78) continue;
    if (accepted.some(v => jaccard(v.text, refText) > 0.72)) continue;
    accepted.push({ item, fingerprint, text: refText });
  }
  return accepted.map(v => v.item).slice(0, 5);
}

function visionPrompt(strict = false) {
  return `You are the visual forensics layer of a commercial stock-asset factory. Analyze the supplied image itself.
Do not guess hidden facts. Separate visible facts from commercial inference.
Do not create creative concepts in this step.
${strict ? "Be literal and complete. Never output a markdown fence. Never output an empty response." : "Be concise."}
Return ONLY a single JSON object with these exact keys:
{
  "visual_summary": "one precise factual sentence",
  "reference_facts": {
    "subject": "specific dominant subject, object class, physical attributes and count if useful",
    "composition": "framing, subject placement, orientation, foreground/background, negative space, depth and symmetry",
    "viewpoint": "camera height, angle, distance, lens-like perspective if visually inferable",
    "color_direction": "main palette, dominant hues, contrast, lighting direction and mood",
    "context": "specific visible setting or situation, without inventing location",
    "visible_text_or_brands": "readable text, logo, label or brand if visible; otherwise exactly none visible",
    "people_or_property": "people, recognizable private property, artwork or distinctive protected-looking objects if visible; otherwise exactly none visible"
  },
  "commercial_signals": ["2 to 5 concise buyer-use inferences grounded in what is visible"]
}`;
}
async function runVisionOnce(env, dataUrl, strict) {
  const result = await env.AI.run(VISION_MODEL, {
    messages: [
      { role: "system", content: "You are a meticulous visual analyst. Output JSON only." },
      {
        role: "user",
        content: [
          { type: "text", text: visionPrompt(strict) },
          { type: "image_url", image_url: { url: dataUrl } },
        ],
      },
    ],
    max_tokens: 1400,
    temperature: 0.05,
    chat_template_kwargs: { enable_thinking: false },
  });
  const text = extractModelText(result);
  const facts = normalizeFacts(text);
  return { facts, raw_text: text, raw: result };
}
async function analyzeVision(env, imageBytes, mimeType) {
  if (!env.AI) throw new Error("Cloudflare Workers AI binding is unavailable; cannot build reference intelligence.");
  const dataUrl = `data:${mimeType};base64,${bytesToBase64(imageBytes)}`;
  const first = await runVisionOnce(env, dataUrl, false);
  if (validFacts(first.facts)) return first.facts;
  const second = await runVisionOnce(env, dataUrl, true);
  if (validFacts(second.facts)) return second.facts;
  throw new Error("VISUAL_FORENSICS_FAILED: Gemma 4 returned no complete visual analysis.");
}

async function reasonOpportunities(env, facts) {
  const prompt = `You are the commercial opportunity strategist for a professional stock-asset factory.
Use the supplied VISUAL FORENSICS as the only source of truth about the reference.
Create exactly five distinct stock concepts. The concepts are NOT copies of the reference. They must convert the visible signal into different buyer problems, visual treatments and scenarios.
Adobe Stock requires meaningful diversification. Do not make five naming variations of one idea.
Every concept must materially change at least THREE of these dimensions versus the reference and versus the other concepts: subject treatment, composition, viewpoint, color_direction, context.
Use concrete buyer jobs such as advertising layout, editorial illustration, healthcare communication, finance education, sustainability campaign, food marketing, travel planning, workplace communication, etc. Only choose a job that is plausible from the visible signal.
Do not invent market statistics or demand claims.
Never use brands, artist names, real person names, fictional characters, copyrighted works, logos, government entities or proprietary product identities.
If the reference contains such material, explicitly avoid reproducing it.
Avoid generic phrases such as modern aesthetic, beautiful image, professional concept, creative background, trending, high quality, stock photo.
Each concept must be specific enough to guide a production prompt without needing the original image.
Return ONLY valid JSON. No markdown and no code fence.

VISUAL FORENSICS:
${JSON.stringify(facts)}

Schema:
{
  "asset_opportunities": [
    {
      "id": "opp_1",
      "title": "specific short concept title",
      "subject": "specific subject treatment for the new asset",
      "composition": "specific framing and element arrangement",
      "viewpoint": "specific camera/viewpoint",
      "color_direction": "specific palette and lighting",
      "context": "specific new commercial context",
      "use_case": "specific buyer communication job",
      "why_fit": "why the concept has useful commercial intent and is distinct",
      "differences": ["subject treatment", "composition", "viewpoint"],
      "similarity_risk": 0.0,
      "genericity_risk": 0.0,
      "ip_risk": 0.0,
      "commercial_score": 0.0
    }
  ]
}`;
  const result = await env.AI.run(REASONING_MODEL, {
    messages: [
      { role: "system", content: "You are a rigorous commercial concept strategist. JSON only." },
      { role: "user", content: prompt },
    ],
    max_tokens: 3600,
    temperature: 0.25,
    chat_template_kwargs: { enable_thinking: true },
  });
  const text = extractModelText(result);
  const root = unwrapResult(text);
  const rawOpps = Array.isArray(root.asset_opportunities) ? root.asset_opportunities : [];
  const reasoned = rawOpps.map(normalizeOpportunity);
  return enforceDistinctness(reasoned, facts.visual_summary);
}

function buildAnalysis(facts, opportunities) {
  if (opportunities.length !== 5) throw new Error(`OPPORTUNITY_QUALITY_FAILED: ${opportunities.length}/5 passed the distinctness and quality gates.`);
  return {
    schema_version: 5,
    visual_summary: facts.visual_summary,
    reference_facts: facts.reference_facts,
    commercial_signals: facts.commercial_signals,
    asset_opportunities: opportunities,
    intelligence: {
      architecture: "gemma4_multimodal_forensics -> gemma4_thinking_commercial_reasoning -> deterministic_quality_and_distinctness_gate",
      vision_model: VISION_MODEL,
      reasoning_model: REASONING_MODEL,
      opportunity_count: opportunities.length,
      fallback_count: 0,
      review_required: true,
      production_blocked_until_review: true,
    },
  };
}
async function visionAnalyze(env, imageBytes, mimeType) {
  const facts = await analyzeVision(env, imageBytes, mimeType);
  const opportunities = await reasonOpportunities(env, facts);
  return buildAnalysis(facts, opportunities);
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
    const analysis = await visionAnalyze(env, bytes, file.type);

    await env.ASSET_STORE.put(r2Key, bytes, { httpMetadata: { contentType: file.type } });
    const workflowId = id("wf");
    const timestamp = now();
    await env.DB.batch([
      env.DB.prepare(`INSERT INTO references_sf (id,token,r2_key,filename,mime_type,sha256,bytes,analysis_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)`)
        .bind(referenceId, accessToken, r2Key, file.name || "reference", file.type, hash, file.size, JSON.stringify(analysis), timestamp),
      env.DB.prepare(`INSERT INTO workflows_sf (id,reference_id,status,stage,progress,message,updated_at) VALUES (?,?,?,?,?,?,?)`)
        .bind(workflowId, referenceId, "ready", "ANALYZED", 100, "Reference intelligence passed visual forensics and five-opportunity quality gates; human review required.", timestamp),
    ]);

    return json({
      reference_id: referenceId,
      workflow_id: workflowId,
      file: `/api/assets/${referenceId}?kind=reference&token=${accessToken}`,
      profile: analysis,
      decision: "REVIEW_REQUIRED",
      notice: "No fallback opportunities are generated. Production remains blocked unless visual forensics and all five differentiated opportunities pass the quality gates.",
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return json({ detail: "Method not allowed" }, 405);
}
