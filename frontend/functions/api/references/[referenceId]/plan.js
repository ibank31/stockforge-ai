function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}
function now() { return new Date().toISOString(); }
function firstObject(value) { if (!value || typeof value !== "object") return {}; return Array.isArray(value) ? (value.find(v => v && typeof v === "object") || {}) : value; }
function parseJsonDeep(value, maxDepth = 5) {
  if (maxDepth < 0) return null;
  if (value && typeof value === "object") return value;
  if (typeof value !== "string") return null;
  let text = value.trim();
  for (let i = 0; i < 3; i++) {
    text = text.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
    try { const parsed = JSON.parse(text); return typeof parsed === "string" ? parseJsonDeep(parsed, maxDepth - 1) : parsed; }
    catch (_) {
      const start = text.indexOf("{"); const end = text.lastIndexOf("}");
      if (start >= 0 && end > start) { try { const parsed = JSON.parse(text.slice(start, end + 1)); return typeof parsed === "string" ? parseJsonDeep(parsed, maxDepth - 1) : parsed; } catch (_) {} }
    }
    const unescaped = text.replace(/\\n/g, "\n").replace(/\\"/g, '"').replace(/\\\\/g, "\\");
    if (unescaped === text) break;
    text = unescaped;
  }
  return null;
}
function text(value, fallback = "") {
  if (typeof value === "string") return value.replace(/\s+/g, " ").trim() || fallback;
  if (Array.isArray(value)) return value.map(v => text(v)).filter(Boolean).join("; ") || fallback;
  return fallback;
}
function normalizeAnalysis(raw) {
  const root = parseJsonDeep(raw) || {};
  const nested = root?.visual_summary && typeof root.visual_summary === "string" && root.visual_summary.trim().startsWith("{") ? (parseJsonDeep(root.visual_summary) || root) : root;
  const source = nested?.asset_opportunities ? nested : root;
  const rf = firstObject(source.reference_facts || source.visual_facts);
  const dna = firstObject(source.asset_dna);
  const localization = firstObject(source.localization);
  const primary = firstObject(localization.primary_asset || source.generation_reference?.source_asset);
  const list = Array.isArray(source.asset_opportunities) ? source.asset_opportunities : (Array.isArray(source.opportunities) ? source.opportunities : []);
  return {
    visual_summary: text(source.visual_summary, "No visual summary."),
    reference_facts: {
      subject: text(rf.subject || source.subject || primary.label, "Unknown visible subject."),
      composition: text(rf.composition || source.composition || primary.composition, "Unknown composition."),
      viewpoint: text(rf.viewpoint || source.viewpoint || dna.orientation, "Unknown viewpoint."),
      color_direction: text(rf.color_direction || rf.palette || source.color_direction || source.palette || primary.colors, "Unknown color direction."),
      context: text(rf.context || source.context, "Unknown context."),
    },
    asset_profile: {
      medium: text(dna.asset_type || primary.medium, "unknown"),
      realism: text(dna.realism || primary.realism, "unknown"),
      visual_style: text(dna.visual_style || primary.visual_style, "unknown visual style"),
      materials: Array.isArray(dna.materials) ? dna.materials.map(text).filter(Boolean) : (Array.isArray(primary.materials) ? primary.materials.map(text).filter(Boolean) : []),
      colors: Array.isArray(dna.colors) ? dna.colors.map(text).filter(Boolean) : (Array.isArray(primary.colors) ? primary.colors.map(text).filter(Boolean) : []),
      distinctive_features: Array.isArray(dna.distinctive_features) ? dna.distinctive_features.map(text).filter(Boolean) : (Array.isArray(primary.distinctive_features) ? primary.distinctive_features.map(text).filter(Boolean) : []),
    },
    commercial_signals: Array.isArray(source.commercial_signals) ? source.commercial_signals.map(v => text(v)).filter(Boolean) : [],
    asset_opportunities: list.slice(0, 5).map((raw, index) => {
      const item = firstObject(raw); const concept = firstObject(item.concept);
      return {
        id: text(item.id, `opp_${index + 1}`),
        title: text(item.title || item.name, `New stock concept ${index + 1}`),
        subject: text(item.subject || concept.subject || item.asset, "A differentiated commercial stock concept"),
        composition: text(item.composition || concept.composition, "A new commercial composition with useful negative space"),
        viewpoint: text(item.viewpoint || concept.viewpoint, "A new camera viewpoint"),
        color_direction: text(item.color_direction || item.color || concept.color_direction || concept.color, "A distinct color direction"),
        context: text(item.context || concept.context, "A new commercial context"),
        use_case: text(item.use_case || item.buyer_job || concept.use_case, "A practical stock buyer use case"),
        why_fit: text(item.why_fit || item.rationale || item.buyer_relevance, "Relevant to the visible commercial signal without copying the reference."),
        differences: Array.isArray(item.differences) ? item.differences.map(v => text(v)).filter(Boolean) : [],
        visual_medium: text(item.visual_medium || dna.asset_type || primary.medium, "unknown"),
        visual_realism: text(item.visual_realism || dna.realism || primary.realism, "unknown"),
        visual_style: text(item.visual_style || dna.visual_style || primary.visual_style, "unknown visual style"),
      };
    }),
  };
}
function tokens(value) { return new Set(text(value).toLowerCase().split(/[^a-z0-9]+/).filter(v => v.length >= 3)); }
function lexicalOverlap(a, b) { const A = tokens(a), B = tokens(b); if (!A.size || !B.size) return 0; let common = 0; for (const item of A) if (B.has(item)) common += 1; return common / Math.max(A.size, B.size); }
function differenceCount(refFacts, opp) {
  const pairs = [[refFacts.subject, opp.subject],[refFacts.composition, opp.composition],[refFacts.viewpoint, opp.viewpoint],[refFacts.color_direction, opp.color_direction],[refFacts.context, opp.context]];
  return pairs.filter(([a, b]) => text(b) && text(a).toLowerCase() !== text(b).toLowerCase() && lexicalOverlap(a, b) < 0.80).length;
}
function canonicalDifference(value) {
  const s = text(value).toLowerCase().replace(/[_-]+/g, " ").replace(/\s+/g, " ").trim();
  if (/^subject( treatment)?$|^object( treatment)?$|^asset( treatment)?$/.test(s)) return "subject";
  if (/^composition$|^framing$|^layout$|^placement$|^arrangement$|^negative space$/.test(s)) return "composition";
  if (/^viewpoint$|^camera$|^camera angle$|^perspective$|^view$/.test(s)) return "viewpoint";
  if (/^color( direction)?$|^colour( direction)?$|^palette$|^lighting$|^tone$/.test(s)) return "color_direction";
  if (/^context$|^setting$|^environment$|^scenario$|^scene$/.test(s)) return "context";
  return s;
}
function validateOpportunity(refFacts, opp) {
  const explicit = new Set((opp.differences || []).map(canonicalDifference));
  const diff = differenceCount(refFacts, opp);
  const declared = ["subject", "composition", "viewpoint", "color_direction", "context"].filter(v => explicit.has(v)).length;
  return { passed: diff >= 3 && declared >= 3, measured_changes: diff, declared_changes: declared };
}
function styleInstruction(profile) {
  const medium = profile.medium;
  const realism = profile.realism;
  if (medium === "digital_illustration") return `Preserve the source medium as digital illustration, not photography. Preserve the observed illustration language: ${profile.visual_style}.`;
  if (medium === "vector_graphic") return `Preserve the source medium as vector graphic, with clean vector geometry and edges. Do not turn it into a photograph.`;
  if (medium === "3d_render") return `Preserve the source medium as 3D rendered artwork with style-consistent materials and lighting.`;
  if (medium === "photography") return `Preserve the source medium as stock photography with ${realism} visual treatment.`;
  if (medium === "ai_generated_graphic") return `Preserve the source as a stylized generated graphic, while creating a genuinely new composition and subject treatment.`;
  return `Preserve the source visual medium and style: ${medium}, ${realism}, ${profile.visual_style}.`;
}
function buildPlan(referenceId, intent, opp, index, seed, profile) {
  const rationale = opp.differences.length ? opp.differences : ["subject", "composition", "viewpoint"];
  const prompt = [
    `Create a commercially useful original stock asset for: ${opp.use_case}.`,
    `Source asset family: ${opp.subject}.`,
    styleInstruction(profile),
    `Composition: ${opp.composition}.`,
    `Viewpoint: ${opp.viewpoint}.`,
    `Color direction: ${opp.color_direction}.`,
    `Context: ${opp.context}.`,
    profile.materials.length ? `Relevant source materials: ${profile.materials.join(", ")}.` : "",
    profile.colors.length ? `Observed source colors may inform the palette without copying the exact artwork: ${profile.colors.join(", ")}.` : "",
    `This concept was derived from a supplied visual reference as intelligence, not as a template.`,
    `Maintain material distance from the reference by changing at least these dimensions: ${rationale.join(", ")}.`,
    `Do not reproduce the source screenshot, platform UI, logos, usernames, watermarks, prices, earnings figures, social proof, or copied layout.`,
    `Create an original commercially useful asset with technically coherent rendering and useful negative space where appropriate.`,
  ].filter(Boolean).join(" ");
  return {
    schema_version: 4,
    reference_id: referenceId,
    buyer_job: intent || opp.use_case,
    selected_opportunity_index: index,
    reference_anchor: { subject: undefined, commercial_signals: undefined },
    source_visual_profile: profile,
    concept: { title: opp.title, subject: opp.subject, composition: opp.composition, viewpoint: opp.viewpoint, color: opp.color_direction, context: opp.context, use_case: opp.use_case, why_fit: opp.why_fit },
    differentiation_levers: rationale,
    generation_prompt: prompt,
    generation: { width: 1024, height: 1024, steps: 8, seed: seed ?? 0, randomize_seed: seed == null },
    gate: { min_changes: 3, human_review_required: true },
  };
}

export async function onRequestPost(context) {
  try {
    const { env, params, request } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    const referenceId = String(params.referenceId || "");
    const reference = await env.DB.prepare(`SELECT * FROM references_sf WHERE id=?`).bind(referenceId).first();
    if (!reference) return json({ detail: "Reference not found" }, 404);
    const analysis = normalizeAnalysis(reference.analysis_json || "{}");
    if (analysis.asset_opportunities.length < 5) return json({ detail: "Reference has fewer than 5 structured opportunities. Re-upload after updating the vision analysis." }, 409);

    const body = await request.json().catch(() => ({}));
    const index = Number.isInteger(body.opportunity_index) ? body.opportunity_index : 0;
    if (index < 0 || index >= analysis.asset_opportunities.length) return json({ detail: `opportunity_index must be between 0 and ${analysis.asset_opportunities.length - 1}` }, 400);
    const opportunity = analysis.asset_opportunities[index];
    const validation = validateOpportunity(analysis.reference_facts, opportunity);
    if (!validation.passed) return json({ detail: "Selected opportunity does not pass the minimum material-difference gate", validation, reference_facts: analysis.reference_facts, opportunity }, 422);

    const plan = buildPlan(referenceId, text(body.market_intent, opportunity.use_case), opportunity, index, Number.isInteger(body.seed) ? body.seed : null, analysis.asset_profile);
    plan.reference_anchor = { subject: analysis.reference_facts.subject, composition: analysis.reference_facts.composition, viewpoint: analysis.reference_facts.viewpoint, color_direction: analysis.reference_facts.color_direction, context: analysis.reference_facts.context, commercial_signals: analysis.commercial_signals };
    plan.validation = validation;

    await env.DB.prepare(`INSERT INTO plans_sf(reference_id,plan_json,created_at) VALUES(?,?,?) ON CONFLICT(reference_id) DO UPDATE SET plan_json=excluded.plan_json, created_at=excluded.created_at`).bind(referenceId, JSON.stringify(plan), now()).run();
    await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`).bind("ready", "PLANNED", 100, `Opportunity ${index + 1} is synchronized to the uploaded reference and passed the material-difference gate.`, now(), referenceId).run();

    return json({ reference_id: referenceId, reference_anchor: plan.reference_anchor, candidates: analysis.asset_opportunities, selected_opportunity: opportunity, validation, plan, decision: "READY_TO_GENERATE" });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
