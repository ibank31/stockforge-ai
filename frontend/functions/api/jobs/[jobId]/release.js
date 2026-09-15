function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }

async function generateMetadata(env, concept, summary) {
  const fallbackWords = [concept.subject, concept.use_case, concept.composition, concept.context, concept.color, concept.viewpoint]
    .filter(Boolean).flatMap((value) => String(value).toLowerCase().split(/[^a-z0-9]+/)).filter((word) => word.length >= 3);
  const fallback = {
    title: String(concept.subject || "Commercial stock asset").replace(/\s+/g, " ").slice(0, 70),
    keywords: [...new Set(fallbackWords)].slice(0, 49),
    source: "deterministic-fallback",
  };
  if (!env.AI) return fallback;
  try {
    const response = await env.AI.run("@cf/meta/llama-3.2-1b-instruct", {
      messages: [
        { role: "system", content: "Create conservative Adobe Stock metadata. Return JSON only with title and keywords. Title must be a concise visual description, max 70 characters. Return up to 30 single-word or short-phrase keywords, most important first. Never invent brands, people, locations, or facts not supplied." },
        { role: "user", content: JSON.stringify({ concept, visual_summary: summary }) },
      ],
      max_tokens: 350,
      temperature: 0.2,
    });
    const text = response?.response || response?.result || JSON.stringify(response);
    const parsed = JSON.parse(String(text).match(/\{[\s\S]*\}/)?.[0] || text);
    if (!parsed?.title || !Array.isArray(parsed?.keywords)) return fallback;
    return { title: String(parsed.title).slice(0, 70), keywords: [...new Set(parsed.keywords.map((v) => String(v).trim().toLowerCase()).filter(Boolean))].slice(0, 49), source: "workers-ai-llama-3.2-1b" };
  } catch (_) {
    return fallback;
  }
}

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.ASSETS) return json({ detail: "D1/R2 bindings are missing" }, 500);
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (job.status !== "approved") return json({ detail: "Explicit human approval is required before release" }, 409);
    const result = job.result_json ? JSON.parse(job.result_json) : {};
    if (result.technical_qa?.status === "FAIL") return json({ detail: "Technical QA failed" }, 409);
    if (result.similarity_gate?.automated_duplicate === "BLOCK") return json({ detail: "Duplicate gate is blocking this asset" }, 409);
    const planRow = await env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(job.reference_id).first();
    const plan = JSON.parse(planRow?.plan_json || "{}");
    const metadata = await generateMetadata(env, plan.concept || {}, plan.reference_summary || "");
    const manifest = {
      schema_version: 3,
      status: "READY_UPLOAD_ADOBE",
      asset: result.final || result,
      metadata: { ...metadata, ai_generated: true, ai_disclosure_required: true, human_metadata_review_required: true },
      provenance: { generation_provider: "hf-zerogpu", generation_model: result.model || "Z-Image-Turbo", upscale_provider: "hf-zerogpu", upscale_model: result.final?.model || "RealESRGAN_x4plus", workflow_job_id: job.id },
      gates: { technical: result.technical_qa, duplicate: result.similarity_gate, human_approval: result.human_review || null },
      marketplace_submission: "manual_only",
      human_review_required: true,
    };
    const key = `artifacts/${job.id}/manifest.json`;
    await env.ASSETS.put(key, JSON.stringify(manifest, null, 2), { httpMetadata: { contentType: "application/json" } });
    return json({ status: "READY_UPLOAD_ADOBE", download_url: result.final?.final_asset_url || null, manifest_url: `/api/manifest/${job.id}`, manifest });
  } catch (error) { return json({ detail: error instanceof Error ? error.message : String(error) }, 500); }
}
