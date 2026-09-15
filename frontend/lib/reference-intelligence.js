const VISION_MODEL = "@cf/google/gemma-4-26b-a4b-it";
const REASONING_MODEL = "@cf/google/gemma-4-26b-a4b-it";

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

function extractModelText(raw) {
  if (typeof raw === "string") return raw;
  if (!raw || typeof raw !== "object") return "";
  if (Array.isArray(raw)) {
    return raw.map(extractModelText).filter(Boolean).join("\n");
  }
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
      const nested = extractModelText(candidate);
      if (nested) return nested;
    }
  }
  return "";
}

function unwrapObject(value) {
  const root = parseJson(value) || (value && typeof value === "object" ? value : {});
  if (root.result && typeof root.result === "object") return root.result;
  if (typeof root.result === "string") return parseJson(root.result) || {};
  if (root.response && typeof root.response === "object") return root.response;
  if (typeof root.response === "string") return parseJson(root.response) || {};
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

function normalizedScore(value, fallback) {
  const n = Number(value);
  if (!Number.isFinite(n)) return fallback;
  if (n > 10) return Math.max(0, Math.min(1, n / 100));
  if (n > 1) return Math.max(0, Math.min(1, n / 10));
  return Math.max(0, Math.min(1, n));
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

function normalizeFacts(raw) {
  const root = unwrapObject(raw);
  const facts = root.reference_facts || root.visual_facts || {};
  return {
    visual_summary: cleanText(root.visual_summary || root.description || root.caption),
    reference_facts: {
      subject: cleanText(facts.subject || root.subject),
      composition: cleanText(facts.composition || root.composition),
      viewpoint: cleanText(facts.viewpoint || root.viewpoint),
      color_direction: cleanText(facts.color_direction || facts.palette || root.color_direction || root.palette),
      context: cleanText(facts.context || root.context),
      visible_text_or_brands: cleanText(facts.visible_text_or_brands || facts.text || root.visible_text_or_brands),
      people_or_property: cleanText(facts.people_or_property || root.people_or_property),
    },
    commercial_signals: Array.isArray(root.commercial_signals)
      ? root.commercial_signals.map(cleanText).filter(Boolean).slice(0, 5)
      : [],
  };
}

function validFacts(facts) {
  const f = facts?.reference_facts || {};
  return Boolean(
    facts?.visual_summary &&
    f.subject && f.composition && f.viewpoint && f.color_direction && f.context &&
    f.visible_text_or_brands && f.people_or_property
  );
}

function normalizeOpportunity(raw, index) {
  const item = raw && typeof raw === "object" ? raw : {};
  return {
    id: cleanText(item.id, `opp_${index + 1}`),
    title: cleanText(item.title || item.name),
    subject: cleanText(item.subject),
    composition: cleanText(item.composition),
    viewpoint: cleanText(item.viewpoint),
    color_direction: cleanText(item.color_direction || item.color),
    context: cleanText(item.context),
    use_case: cleanText(item.use_case || item.buyer_job),
    why_fit: cleanText(item.why_fit || item.rationale),
    differences: Array.isArray(item.differences) ? item.differences.map(cleanText).filter(Boolean).slice(0, 8) : [],
    similarity_risk: normalizedScore(item.similarity_risk, 1),
    genericity_risk: normalizedScore(item.genericity_risk, 1),
    ip_risk: normalizedScore(item.ip_risk, 1),
    commercial_score: normalizedScore(item.commercial_score, 0),
  };
}

function changedDimensions(differences) {
  const result = new Set();
  for (const raw of differences) {
    const text = raw.toLowerCase();
    if (/subject|object|product|prop|item|element/.test(text)) result.add("subject_treatment");
    if (/composition|frame|framing|layout|placement|negative space|arrangement|crop/.test(text)) result.add("composition");
    if (/view|camera|angle|perspective|distance|shot|lens/.test(text)) result.add("viewpoint");
    if (/color|colour|palette|lighting|tone|hue|contrast/.test(text)) result.add("color_direction");
    if (/context|setting|environment|scenario|location|scene/.test(text)) result.add("context");
    if (/use.?case|buyer|application|communication|job/.test(text)) result.add("use_case");
  }
  return result;
}

const GENERIC_PHRASES = [
  "beautiful image", "modern aesthetic", "professional concept", "creative background",
  "high quality", "stock photo", "visually appealing", "trending concept", "generic lifestyle",
];

function qualityCheckOpportunity(item) {
  const complete = [item.title, item.subject, item.composition, item.viewpoint, item.color_direction, item.context, item.use_case, item.why_fit].every(Boolean);
  const dimensions = changedDimensions(item.differences);
  const allText = [item.title, item.subject, item.composition, item.viewpoint, item.color_direction, item.context, item.use_case, item.why_fit].join(" ").toLowerCase();
  const generic = GENERIC_PHRASES.some(p => allText.includes(p));
  return complete &&
    item.title.length >= 12 &&
    item.use_case.length >= 18 &&
    dimensions.size >= 3 &&
    !generic &&
    item.ip_risk < 0.75 &&
    item.genericity_risk < 0.75 &&
    item.similarity_risk < 0.75 &&
    item.commercial_score >= 0.50;
}

function enforceDistinctness(opportunities) {
  const ranked = opportunities
    .map(normalizeOpportunity)
    .filter(qualityCheckOpportunity)
    .sort((a, b) => (b.commercial_score - b.similarity_risk - b.genericity_risk) - (a.commercial_score - a.similarity_risk - a.genericity_risk));
  const accepted = [];
  for (const item of ranked) {
    const text = [item.title, item.subject, item.composition, item.viewpoint, item.color_direction, item.context, item.use_case].join(" ");
    if (accepted.some(v => jaccard(v.text, text) > 0.78)) continue;
    accepted.push({ item, text });
    if (accepted.length === 5) break;
  }
  return accepted.map(v => v.item);
}

function visionPrompt(strict) {
  return `You are a forensic visual analyst for a commercial stock-asset factory.
Analyze the supplied image itself. Never invent hidden facts, identities, market data, brands, locations, or ownership.
${strict ? "Be exhaustive and literal. Never output markdown, a code fence, commentary, or an empty response." : "Be precise and concise."}
Return ONLY one valid JSON object with this exact structure:
{
  "visual_summary": "one precise factual sentence describing the visible scene",
  "reference_facts": {
    "subject": "specific dominant visible subject, object class, count and useful physical attributes",
    "composition": "framing, placement, orientation, foreground/background, negative space, depth and symmetry",
    "viewpoint": "camera height, angle, distance and perspective if visually inferable",
    "color_direction": "dominant hues, palette, contrast, lighting direction and mood",
    "context": "specific visible setting or situation without inventing location",
    "visible_text_or_brands": "readable text, logos, labels or brands if visible; otherwise exactly none visible",
    "people_or_property": "visible people, recognizable private property, artwork or distinctive protected-looking objects; otherwise exactly none visible"
  },
  "commercial_signals": ["2 to 5 plausible buyer-use inferences grounded in visible evidence"]
}`;
}

async function runVision(env, dataUrl, strict) {
  const result = await env.AI.run(VISION_MODEL, {
    messages: [
      { role: "system", content: "You are a meticulous visual forensic analyst. Output JSON only." },
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
  return normalizeFacts(text);
}

async function analyzeVision(env, imageBytes, mimeType) {
  if (!env.AI) throw new Error("REFERENCE_AI_UNAVAILABLE");
  const dataUrl = `data:${mimeType};base64,${bytesToBase64(imageBytes)}`;
  const first = await runVision(env, dataUrl, false);
  if (validFacts(first)) return first;
  const second = await runVision(env, dataUrl, true);
  if (validFacts(second)) return second;
  throw new Error("VISUAL_FORENSICS_FAILED: incomplete multimodal visual extraction");
}

function reasoningPrompt(facts, repair = false) {
  return `You are the commercial opportunity strategist for an Adobe Stock production factory.
Use the VISUAL FORENSICS below as the only factual source about the reference.
${repair ? "This is a repair pass. Produce missing alternatives that are materially different from the candidate set." : "Produce a complete candidate set."}
Create exactly five commercially useful stock concepts that are inspired by the visible signal but are NOT copies of the reference.
Meaningful diversification is mandatory. Each concept must materially change at least THREE of these dimensions: subject treatment, composition, viewpoint, color direction, context. Prefer different buyer problems as well.
Use concrete buyer jobs such as advertising layout, education, healthcare communication, finance education, sustainability campaigns, food marketing, travel planning, workplace communication or editorial storytelling only when plausible from the reference.
Never invent demand statistics.
Never use or reproduce brands, logos, artist names, real person names, fictional characters, copyrighted works, government entities or proprietary product identities.
Avoid generic filler like beautiful image, modern aesthetic, professional concept, creative background, trending, high quality, stock photo.
Every concept must be specific enough to guide an image-generation prompt without seeing the reference.
Use risk and score values on a 0 to 1 scale.
Return ONLY valid JSON, with no markdown or code fence, matching this schema:
{
  "asset_opportunities": [
    {
      "id": "opp_1",
      "title": "specific short concept title",
      "subject": "specific new subject treatment",
      "composition": "specific framing and element arrangement",
      "viewpoint": "specific camera/viewpoint",
      "color_direction": "specific palette and lighting",
      "context": "specific commercial setting or scenario",
      "use_case": "specific buyer communication job",
      "why_fit": "specific rationale tied to visible evidence and distinctness",
      "differences": ["subject treatment", "composition", "viewpoint", "context"],
      "similarity_risk": 0.10,
      "genericity_risk": 0.10,
      "ip_risk": 0.00,
      "commercial_score": 0.80
    }
  ]
}

VISUAL FORENSICS:
${JSON.stringify(facts)}${repair ? "\n\nDo not repeat generic or near-duplicate ideas. Maximize conceptual distance among the five results." : ""}`;
}

async function runReasoning(env, facts, repair = false) {
  const result = await env.AI.run(REASONING_MODEL, {
    messages: [
      { role: "system", content: "You are a strict commercial concept strategist. Output JSON only." },
      { role: "user", content: reasoningPrompt(facts, repair) },
    ],
    max_tokens: 4500,
    temperature: repair ? 0.30 : 0.20,
    chat_template_kwargs: { enable_thinking: false },
  });
  const root = unwrapObject(extractModelText(result));
  return Array.isArray(root.asset_opportunities) ? root.asset_opportunities : [];
}

async function reasonOpportunities(env, facts) {
  let candidates = await runReasoning(env, facts, false);
  let best = enforceDistinctness(candidates);
  if (best.length === 5) return best;
  const repaired = await runReasoning(env, facts, true);
  candidates = candidates.concat(repaired);
  best = enforceDistinctness(candidates);
  if (best.length !== 5) throw new Error(`OPPORTUNITY_QUALITY_FAILED: ${best.length}/5 valid distinct opportunities`);
  return best;
}

export async function buildReferenceAnalysis(env, imageBytes, mimeType) {
  const facts = await analyzeVision(env, imageBytes, mimeType);
  const opportunities = await reasonOpportunities(env, facts);
  return {
    schema_version: 6,
    visual_summary: facts.visual_summary,
    reference_facts: facts.reference_facts,
    commercial_signals: facts.commercial_signals,
    asset_opportunities: opportunities,
    intelligence: {
      architecture: "gemma4_multimodal_forensics -> gemma4_structured_opportunity_reasoning -> deterministic_quality_and_distinctness_gate",
      vision_model: VISION_MODEL,
      reasoning_model: REASONING_MODEL,
      opportunity_count: opportunities.length,
      fallback_count: 0,
      review_required: true,
      production_blocked_until_review: true,
    },
  };
}
