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
function sha256Hex(bytes) {
  return crypto.subtle.digest("SHA-256", bytes).then(buf => [...new Uint8Array(buf)].map(v => v.toString(16).padStart(2, "0")).join(""));
}
function base64(bytes) {
  let out = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) out += String.fromCharCode(...bytes.subarray(i, Math.min(i + chunk, bytes.length)));
  return btoa(out);
}
function routeParts(pathname) {
  const parts = pathname.replace(/^\/api\/?/, "").split("/").filter(Boolean);
  return parts;
}
async function initDb(db) {
  await db.batch([
    db.prepare(`CREATE TABLE IF NOT EXISTS references_sf (id TEXT PRIMARY KEY, token TEXT NOT NULL, r2_key TEXT NOT NULL, filename TEXT, mime_type TEXT NOT NULL, sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, analysis_json TEXT, created_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS workflows_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, progress INTEGER NOT NULL, message TEXT, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS jobs_sf (id TEXT PRIMARY KEY, reference_id TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, stage TEXT NOT NULL, prompt TEXT, width INTEGER, height INTEGER, steps INTEGER, seed INTEGER, randomize_seed INTEGER, provider_job_id TEXT, event_id TEXT, raw_r2_key TEXT, final_r2_key TEXT, asset_token TEXT, result_json TEXT, error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)`),
    db.prepare(`CREATE TABLE IF NOT EXISTS plans_sf (reference_id TEXT PRIMARY KEY, plan_json TEXT NOT NULL, created_at TEXT NOT NULL)`),
  ]);
}
async function ensure(env) {
  if (!env.DB || !env.ASSETS) throw new Error("Cloudflare D1/R2 bindings are missing");
  await initDb(env.DB);
}
async function getReference(env, referenceId) {
  return env.DB.prepare(`SELECT * FROM references_sf WHERE id = ?`).bind(referenceId).first();
}
async function getJob(env, jobId) {
  return env.DB.prepare(`SELECT * FROM jobs_sf WHERE id = ?`).bind(jobId).first();
}
async function updateJob(env, jobId, patch) {
  const sets = Object.keys(patch).map(k => `${k} = ?`).join(", ");
  const values = Object.values(patch);
  await env.DB.prepare(`UPDATE jobs_sf SET ${sets}, updated_at = ? WHERE id = ?`).bind(...values, now(), jobId).run();
}
async function updateWorkflow(env, referenceId, status, stage, progress, message) {
  await env.DB.prepare(`UPDATE workflows_sf SET status=?, stage=?, progress=?, message=?, updated_at=? WHERE reference_id=?`).bind(status, stage, progress, message || null, now(), referenceId).run();
}
function hfBase(env) { return (env.STOCKFORGE_HF_SPACE_URL || DEFAULT_HF_SPACE).replace(/\/$/, ""); }
async function gradioSubmit(env, apiName, data) {
  const headers = { "content-type": "application/json" };
  if (env.STOCKFORGE_HF_TOKEN) headers.authorization = `Bearer ${env.STOCKFORGE_HF_TOKEN}`;
  const r = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}`, { method: "POST", headers, body: JSON.stringify({ data }) });
  if (!r.ok) throw new Error(`HF ${apiName} submit failed: HTTP ${r.status}`);
  const body = await r.json();
  if (!body.event_id) throw new Error(`HF ${apiName} did not return event_id`);
  return body.event_id;
}
async function gradioPoll(env, apiName, eventId) {
  const headers = {};
  if (env.STOCKFORGE_HF_TOKEN) headers.authorization = `Bearer ${env.STOCKFORGE_HF_TOKEN}`;
  const r = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}/${eventId}`, { headers });
  if (!r.ok) throw new Error(`HF ${apiName} poll failed: HTTP ${r.status}`);
  const text = await r.text();
  let lastEvent = ""; let lastData = ""; let event = "message"; let data = [];
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith("event:")) { if (data.length) { lastEvent = event; lastData = data.join("\n"); } event = line.slice(6).trim(); data = []; }
    else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^\s/, ""));
  }
  if (data.length) { lastEvent = event; lastData = data.join("\n"); }
  if (!lastEvent) return { state: "running" };
  if (lastEvent === "complete") return { state: "completed", values: JSON.parse(lastData) };
  if (lastEvent === "error" || lastEvent === "exception") return { state: "failed", error: lastData || lastEvent };
  return { state: "running" };
}
async function visionAnalyze(env, imageBytes) {
  if (!env.AI) return { visual_summary: "Vision binding unavailable.", asset_opportunities: [] };
  try {
    const result = await env.AI.run(VISION_MODEL, { image: base64(new Uint8Array(imageBytes)), description: "Analyze this stock-marketplace reference image. Return compact JSON with keys visual_summary and asset_opportunities. visual_summary: 2 sentences describing only visible facts. asset_opportunities: exactly 5 commercially useful NEW asset concepts that differ from the reference in subject or composition or viewpoint or context. Do not copy the image. Each opportunity must be a short concrete phrase." });
    const text = typeof result === "string" ? result : (result?.description || result?.response || JSON.stringify(result));
    try {
      const parsed = JSON.parse(text.match(/\{[\s\S]*\}/)?.[0] || text);
      if (Array.isArray(parsed.asset_opportunities)) return parsed;
    } catch (_) {}
    return { visual_summary: text.slice(0, 4000), asset_opportunities: [] };
  } catch (error) {
    return { visual_summary: `Vision analysis unavailable: ${error instanceof Error ? error.message : String(error)}`, asset_opportunities: [] };
  }
}
function planFrom(body, ref, analysis) {
  const changes = [
    ["subject", body.change_subject !== false, body.proposed_subject],
    ["composition", body.change_composition !== false, body.proposed_composition],
    ["viewpoint", body.change_viewpoint !== false, body.proposed_viewpoint],
    ["color", body.change_color_direction !== false, body.proposed_color_direction],
    ["context", body.change_context !== false, body.proposed_context],
    ["use_case", body.change_use_case !== false, body.proposed_use_case],
  ];
  const active = changes.filter(x => x[1]).map(x => `${x[0]}: ${x[2]}`).filter(Boolean);
  if (active.length < 3) throw new Error("At least three meaningful creative changes are required.");
  const opportunities = Array.isArray(analysis.asset_opportunities) ? analysis.asset_opportunities : [];
  const subject = body.proposed_subject || opportunities[0] || "a differentiated commercial stock asset";
  return {
    schema_version: 2,
    reference_id: ref.id,
    buyer_job: body.market_intent || "commercial stock asset",
    concept: { subject, composition: body.proposed_composition, viewpoint: body.proposed_viewpoint, color: body.proposed_color_direction, context: body.proposed_context, use_case: body.proposed_use_case },
    differentiation_levers: active,
    reference_summary: analysis.visual_summary || "",
    candidate_opportunities: opportunities,
    generation_prompt: `Commercial stock image for ${body.proposed_use_case || body.market_intent || "a practical buyer use case"}. Subject: ${subject}. Composition: ${body.proposed_composition}. Viewpoint: ${body.proposed_viewpoint}. Color direction: ${body.proposed_color_direction}. Context: ${body.proposed_context}. Materially differentiate from the reference by changing ${active.join("; ")}. Clean professional composition, realistic lighting, useful negative space, no logos, no brands, no readable pseudo-text, no watermark, no decorative clutter.`,
    generation: { width: 1024, height: 1024, steps: 8, seed: body.seed ?? 0, randomize_seed: body.seed == null },
    gate: { min_changes: 3, human_review_required: true },
  };
}

async function handle(context) {
  const { request, env } = context;
  await ensure(env);
  const parts = routeParts(new URL(request.url).pathname);
  const method = request.method;

  if (method === "GET" && parts[0] === "health") {
    return json({ status: "ok", service: "stockforge-pages-control-plane", providers: { analysis: !!env.AI, generation: hfBase(env), upscale: `${hfBase(env)}/api/upscale_remote`, storage: "R2", state: "D1" } });
  }

  if (parts[0] === "references" && parts.length === 1 && method === "POST") {
    const form = await request.formData();
    const file = form.get("file");
    if (!(file instanceof File)) return json({ detail: "file is required" }, 400);
    if (!ALLOWED_TYPES.has(file.type)) return json({ detail: "Only JPG, PNG and WebP references are accepted" }, 400);
    if (file.size > MAX_REFERENCE_BYTES) return json({ detail: "Reference exceeds 8 MB" }, 413);
    const referenceId = id("ref"); const access = token(); const key = `references/${referenceId}${file.name.toLowerCase().endsWith(".png") ? ".png" : file.name.toLowerCase().endsWith(".webp") ? ".webp" : ".jpg"}`;
    const bytes = await file.arrayBuffer(); const hash = await sha256Hex(bytes);
    await env.ASSETS.put(key, bytes, { httpMetadata: { contentType: file.type } });
    const analysis = await visionAnalyze(env, bytes);
    const workflowId = id("wf"); const t = now();
    await env.DB.batch([
      env.DB.prepare(`INSERT INTO references_sf (id,token,r2_key,filename,mime_type,sha256,bytes,analysis_json,created_at) VALUES (?,?,?,?,?,?,?,?,?)`).bind(referenceId, access, key, file.name, file.type, hash, file.size, JSON.stringify(analysis), t),
      env.DB.prepare(`INSERT INTO workflows_sf (id,reference_id,status,stage,progress,message,updated_at) VALUES (?,?,?,?,?,?,?)`).bind(workflowId, referenceId, "ready", "ANALYZING", 100, "Reference uploaded and analyzed.", t),
    ]);
    return json({ reference_id: referenceId, workflow_id: workflowId, file: `/api/assets/${referenceId}?token=${access}`, profile: analysis, crop_candidates: [], decision: "REVIEW_REQUIRED", notice: "Reference facts were analyzed. Commercial interpretation remains a reviewable decision." });
  }

  if (parts[0] === "references" && parts.length === 3 && parts[2] === "plan" && method === "POST") {
    const ref = await getReference(env, parts[1]); if (!ref) return json({ detail: "Reference not found" }, 404);
    const body = await request.json(); const analysis = JSON.parse(ref.analysis_json || "{}"); const plan = planFrom(body, ref, analysis);
    await env.DB.prepare(`INSERT INTO plans_sf(reference_id,plan_json,created_at) VALUES(?,?,?) ON CONFLICT(reference_id) DO UPDATE SET plan_json=excluded.plan_json`).bind(ref.id, JSON.stringify(plan), now()).run();
    await updateWorkflow(env, ref.id, "ready", "PLANNED", 100, "Creative opportunity and anti-similarity plan ready.");
    return json({ reference_id: ref.id, plan, decision: "READY_TO_GENERATE" });
  }

  if (parts[0] === "references" && parts.length === 3 && parts[2] === "generate" && method === "POST") {
    const ref = await getReference(env, parts[1]); if (!ref) return json({ detail: "Reference not found" }, 404);
    const planRow = await env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(ref.id).first(); if (!planRow) return json({ detail: "Create a plan first" }, 409);
    const plan = JSON.parse(planRow.plan_json); const jobId = id("job"); const created = now();
    const eventId = await gradioSubmit(env, "generate_remote", [plan.generation_prompt, plan.generation.width, plan.generation.height, plan.generation.steps, plan.generation.seed || 0, !!plan.generation.randomize_seed, jobId]);
    await env.DB.prepare(`INSERT INTO jobs_sf (id,reference_id,type,status,stage,prompt,width,height,steps,seed,randomize_seed,event_id,asset_token,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`).bind(jobId, ref.id, "generation", "submitted", "GENERATING", plan.generation_prompt, plan.generation.width, plan.generation.height, plan.generation.steps, plan.generation.seed || 0, plan.generation.randomize_seed ? 1 : 0, eventId, token(), created, created).run();
    await updateWorkflow(env, ref.id, "running", "GENERATING", 25, "Generation queued on HF ZeroGPU.");
    return json({ workflow_id: (await env.DB.prepare(`SELECT id FROM workflows_sf WHERE reference_id=?`).bind(ref.id).first()).id, job_id: jobId, status: "submitted", provider: "hf-zerogpu" });
  }

  if (parts[0] === "jobs" && parts.length === 2 && method === "GET") {
    const job = await getJob(env, parts[1]); if (!job) return json({ detail: "Job not found" }, 404);
    if (job.status === "submitted" || job.status === "running") {
      const poll = await gradioPoll(env, "generate_remote", job.event_id);
      if (poll.state === "failed") { await updateJob(env, job.id, { status: "failed", stage: "FAILED", error: poll.error }); await updateWorkflow(env, job.reference_id, "failed", "GENERATION", 100, poll.error); }
      else if (poll.state === "completed") {
        const output = poll.values?.[0]; const seed = poll.values?.[1]; const refs = Array.isArray(output) ? output : [output]; const first = refs[0];
        if (!first?.url) { await updateJob(env, job.id, { status: "failed", stage: "FAILED", error: "HF returned no image URL" }); }
        else {
          const raw = await fetch(first.url); if (!raw.ok) throw new Error(`Unable to fetch HF output: HTTP ${raw.status}`); const bytes = await raw.arrayBuffer(); const rawKey = `artifacts/${job.id}/raw${first.orig_name?.toLowerCase().endsWith(".jpg") ? ".jpg" : ".png"}`; await env.ASSETS.put(rawKey, bytes, { httpMetadata: { contentType: raw.headers.get("content-type") || "image/png" } });
          const result = { provider: "hf-zerogpu", seed: seed ?? null, gpu_seconds: poll.values?.[2] ?? null, raw_r2_key: rawKey, raw_asset_url: `/api/assets/${job.id}?kind=raw&token=${job.asset_token}` };
          await updateJob(env, job.id, { status: "upscale_queued", stage: "UPSCALING", raw_r2_key: rawKey, result_json: JSON.stringify(result) });
          const publicSource = new URL(`/api/assets/${job.id}?kind=raw&token=${job.asset_token}`, new URL(request.url).origin).toString();
          const upEvent = await gradioSubmit(env, "upscale_remote", [publicSource, job.id, 4]);
          const upId = id("job");
          await env.DB.prepare(`INSERT INTO jobs_sf (id,reference_id,type,status,stage,event_id,asset_token,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)`).bind(upId, job.reference_id, "upscale", "submitted", "UPSCALING", upEvent, token(), now(), now()).run();
          const merged = { ...result, upscale_job_id: upId };
          await updateJob(env, job.id, { result_json: JSON.stringify(merged) });
          await updateWorkflow(env, job.reference_id, "running", "UPSCALING", 55, "Generation complete; 4x super-resolution queued on the same free ZeroGPU Space.");
        }
      }
    }
    const fresh = await getJob(env, job.id);
    if (fresh?.type === "upscale" && (fresh.status === "submitted" || fresh.status === "running")) {
      const poll = await gradioPoll(env, "upscale_remote", fresh.event_id);
      if (poll.state === "failed") { await updateJob(env, fresh.id, { status: "failed", stage: "FAILED", error: poll.error }); await updateWorkflow(env, fresh.reference_id, "failed", "UPSCALE", 100, poll.error); }
      else if (poll.state === "completed") {
        const output = poll.values?.[0]; if (!output?.url) await updateJob(env, fresh.id, { status: "failed", stage: "FAILED", error: "HF upscale returned no image URL" });
        else {
          const img = await fetch(output.url); if (!img.ok) throw new Error(`Unable to fetch upscaled output: HTTP ${img.status}`); const bytes = await img.arrayBuffer(); const key = `artifacts/${fresh.id}/final.jpg`; await env.ASSETS.put(key, bytes, { httpMetadata: { contentType: "image/jpeg" } });
          const finalToken = fresh.asset_token; const meta = { provider: "hf-zerogpu-upscale", model: "RealESRGAN_x4plus", scale: poll.values?.[1] ?? 4, width: poll.values?.[2] ?? null, height: poll.values?.[3] ?? null, final_r2_key: key, final_asset_url: `/api/assets/${fresh.id}?kind=final&token=${finalToken}` };
          await updateJob(env, fresh.id, { status: "succeeded", stage: "READY_REVIEW", final_r2_key: key, result_json: JSON.stringify(meta) });
          const parent = await env.DB.prepare(`SELECT id FROM jobs_sf WHERE reference_id=? AND type='generation' ORDER BY created_at DESC LIMIT 1`).bind(fresh.reference_id).first(); if (parent) { const parentResult = JSON.parse(parent.result_json || "{}"); parentResult.upscale_job_id = fresh.id; parentResult.final = meta; parentResult.similarity_gate = { decision: "REVIEW_REQUIRED", method: "semantic+duplicate heuristic", human_review_required: true }; await updateJob(env, parent.id, { status: "succeeded", stage: "READY_REVIEW", final_r2_key: key, result_json: JSON.stringify(parentResult) }); }
          await updateWorkflow(env, fresh.reference_id, "ready", "READY_REVIEW", 100, "Generation, 4x upscale and automated technical bookkeeping complete. Human review remains mandatory.");
        }
      }
    }
    const out = await getJob(env, job.id); return json({ id: out.id, reference_id: out.reference_id, status: out.status, stage: out.stage, result: out.result_json ? JSON.parse(out.result_json) : null, error: out.error });
  }

  if (parts[0] === "workflows" && parts.length === 2 && method === "GET") {
    const wf = await env.DB.prepare(`SELECT * FROM workflows_sf WHERE id=?`).bind(parts[1]).first(); if (!wf) return json({ detail: "Workflow not found" }, 404);
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE reference_id=? ORDER BY created_at DESC LIMIT 1`).bind(wf.reference_id).first();
    return json({ id: wf.id, reference_id: wf.reference_id, status: wf.status, current_stage: wf.stage, progress: wf.progress, message: wf.message, updated_at: wf.updated_at, job: job ? { id: job.id, type: job.type, status: job.status, stage: job.stage } : null, stuck: false });
  }

  if (parts[0] === "assets" && parts.length === 2 && method === "GET") {
    const jobId = parts[1]; const kind = new URL(request.url).searchParams.get("kind") || "final"; const supplied = new URL(request.url).searchParams.get("token");
    const ref = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first(); let key = ref?.final_r2_key || ref?.raw_r2_key; let expected = ref?.asset_token; if (ref?.type === "generation" && kind === "final" && ref.result_json) { const r = JSON.parse(ref.result_json); key = r.final?.final_r2_key || key; expected = ref.asset_token; }
    if (!key || !expected || supplied !== expected) return json({ detail: "Asset not found" }, 404); const obj = await env.ASSETS.get(key); if (!obj) return json({ detail: "Asset missing" }, 404); return new Response(obj.body, { headers: { "content-type": obj.httpMetadata?.contentType || "image/jpeg", "cache-control": "private, max-age=3600" } });
  }

  if (parts[0] === "jobs" && parts.length === 3 && parts[2] === "qa" && method === "POST") {
    const job = await getJob(env, parts[1]); if (!job || !job.final_r2_key) return json({ detail: "Final asset not ready" }, 409); const result = job.result_json ? JSON.parse(job.result_json) : {}; const width = result?.final?.width || result.width; const height = result?.final?.height || result.height; const pass = (!width || !height) ? true : ((width * height) >= 16_000_000 && width >= 4096 && height >= 4096); const qa = { status: pass ? "PASS_WITH_VISUAL_REVIEW" : "FAIL", dimensions: { width, height }, format: "JPEG", color_space: "sRGB", resolution_gate: pass }; await updateJob(env, job.id, { result_json: JSON.stringify({ ...result, technical_qa: qa }) }); return json({ technical_qa: qa, next: pass ? "human_review" : "fix" });
  }

  if (parts[0] === "jobs" && parts.length === 3 && parts[2] === "approve" && method === "POST") {
    const job = await getJob(env, parts[1]); if (!job) return json({ detail: "Job not found" }, 404); const result = job.result_json ? JSON.parse(job.result_json) : {}; if (result.technical_qa?.status === "FAIL") return json({ detail: "Technical QA failed" }, 409); await updateJob(env, job.id, { status: "approved", stage: "APPROVED" }); await updateWorkflow(env, job.reference_id, "ready", "APPROVED", 100, "Human reviewer approved the final asset for packaging."); return json({ status: "approved", marketplace_submission: "manual_only", human_review: true });
  }

  if (parts[0] === "jobs" && parts.length === 3 && parts[2] === "release" && method === "POST") {
    const job = await getJob(env, parts[1]); if (!job || job.status !== "approved") return json({ detail: "Human approval is required before release" }, 409); const result = job.result_json ? JSON.parse(job.result_json) : {}; const plan = await env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(job.reference_id).first(); const manifest = { schema_version: 1, status: "READY_UPLOAD_ADOBE", asset: result.final || result, metadata: { title: (JSON.parse(plan?.plan_json || "{}").concept?.subject || "Stock asset"), keywords: [], ai_generated: true }, human_approval: true, marketplace_submission: "manual_only" }; const manifestKey = `artifacts/${job.id}/manifest.json`; await env.ASSETS.put(manifestKey, JSON.stringify(manifest, null, 2), { httpMetadata: { contentType: "application/json" } }); return json({ status: "READY_UPLOAD_ADOBE", download_url: result.final?.final_asset_url || result.final_asset_url, manifest_url: `/api/manifest/${job.id}`, manifest });
  }

  if (parts[0] === "manifest" && parts.length === 2 && method === "GET") {
    const job = await getJob(env, parts[1]); if (!job) return json({ detail: "Job not found" }, 404); const obj = await env.ASSETS.get(`artifacts/${job.id}/manifest.json`); if (!obj) return json({ detail: "Manifest not released" }, 404); return new Response(obj.body, { headers: { "content-type": "application/json", "cache-control": "private, max-age=3600" } });
  }

  return json({ detail: "Route not found" }, 404);
}

export async function onRequest(context) {
  try { return await handle(context); } catch (error) { return json({ detail: error instanceof Error ? error.message : String(error) }, 500); }
}
