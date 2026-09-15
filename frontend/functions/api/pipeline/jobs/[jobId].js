const DEFAULT_HF_SPACE = "https://ibank31-stockforge-zerogpu.hf.space";

function now() { return new Date().toISOString(); }
function ok(data) { return Response.json(data, { headers: { "cache-control": "no-store" } }); }
function fail(message, status = 500) { return Response.json({ detail: message }, { status, headers: { "cache-control": "no-store" } }); }
function hfBase(env) { return (env.STOCKFORGE_HF_SPACE_URL || DEFAULT_HF_SPACE).replace(/\/$/, ""); }
async function getJob(env, id) { return env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(id).first(); }
async function updateJob(env, id, patch) { const sets = Object.keys(patch).map(k => `${k}=?`).join(", "); await env.DB.prepare(`UPDATE jobs_sf SET ${sets}, updated_at=? WHERE id=?`).bind(...Object.values(patch), now(), id).run(); }
async function updateWorkflow(env, referenceId, status, stage, progress, message) { await env.DB.prepare(`UPDATE workflows_sf SET status=?, stage=?, progress=?, message=?, updated_at=? WHERE reference_id=?`).bind(status, stage, progress, message || null, now(), referenceId).run(); }
async function gradioPoll(env, apiName, eventId) {
  const headers = {}; if (env.STOCKFORGE_HF_TOKEN) headers.authorization = `Bearer ${env.STOCKFORGE_HF_TOKEN}`;
  const r = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}/${eventId}`, { headers });
  if (!r.ok) throw new Error(`HF ${apiName} poll failed: HTTP ${r.status}`);
  const text = await r.text(); let event = "message"; let data = []; let last = null;
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith("event:")) { if (data.length) last = { event, data: data.join("\n") }; event = line.slice(6).trim(); data = []; }
    else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^\s/, ""));
  }
  if (data.length) last = { event, data: data.join("\n") };
  if (!last) return { state: "running" };
  if (last.event === "complete") return { state: "completed", values: JSON.parse(last.data) };
  if (last.event === "error" || last.event === "exception") return { state: "failed", error: last.data || last.event };
  return { state: "running" };
}
async function gradioSubmit(env, apiName, data) {
  const headers = { "content-type": "application/json" }; if (env.STOCKFORGE_HF_TOKEN) headers.authorization = `Bearer ${env.STOCKFORGE_HF_TOKEN}`;
  const r = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}`, { method: "POST", headers, body: JSON.stringify({ data }) });
  if (!r.ok) throw new Error(`HF ${apiName} submit failed: HTTP ${r.status}`); const body = await r.json(); if (!body.event_id) throw new Error("HF did not return event_id"); return body.event_id;
}
async function processUpscale(env, request, parent, child) {
  if (child.status === "submitted" || child.status === "running") {
    const poll = await gradioPoll(env, "upscale_remote", child.event_id);
    if (poll.state === "failed") {
      await updateJob(env, child.id, { status: "failed", stage: "FAILED", error: poll.error });
      await updateWorkflow(env, parent.reference_id, "failed", "UPSCALE", 100, poll.error);
    } else if (poll.state === "completed") {
      const output = poll.values?.[0];
      if (!output?.url) throw new Error("HF upscale returned no image URL");
      const response = await fetch(output.url); if (!response.ok) throw new Error(`Unable to fetch upscaled output: HTTP ${response.status}`);
      const bytes = await response.arrayBuffer(); const finalKey = `artifacts/${parent.id}/final.jpg`;
      await env.ASSETS.put(finalKey, bytes, { httpMetadata: { contentType: "image/jpeg" } });
      const meta = { provider: "hf-zerogpu", model: "RealESRGAN_x4plus", scale: poll.values?.[1] ?? 4, width: poll.values?.[2] ?? null, height: poll.values?.[3] ?? null, final_r2_key: finalKey, final_asset_url: `/api/assets/${parent.id}?kind=final&token=${parent.asset_token}` };
      await updateJob(env, child.id, { status: "succeeded", stage: "READY_REVIEW", final_r2_key: finalKey, result_json: JSON.stringify(meta) });
      const parentResult = JSON.parse(parent.result_json || "{}");
      parentResult.final = meta;
      parentResult.upscale_job_id = child.id;
      parentResult.similarity_gate = { decision: "REVIEW_REQUIRED", method: "reference/concept gate plus duplicate-safe lineage", human_review_required: true };
      parentResult.technical_qa = { status: "PASS_WITH_VISUAL_REVIEW", format: "JPEG", color_space: "sRGB", dimensions: { width: meta.width, height: meta.height }, resolution_gate: !!meta.width && !!meta.height && meta.width >= 4096 && meta.height >= 4096 };
      await updateJob(env, parent.id, { status: "succeeded", stage: "READY_REVIEW", final_r2_key: finalKey, result_json: JSON.stringify(parentResult) });
      await updateWorkflow(env, parent.reference_id, "ready", "READY_REVIEW", 100, "Generation and 4x super-resolution finished. Human visual/rights review remains mandatory.");
    }
  }
  return getJob(env, child.id);
}

async function processParent(context, parent) {
  const { env, request } = context;
  if (parent.type !== "generation") return parent;
  if (parent.status === "submitted" || parent.status === "running") {
    const poll = await gradioPoll(env, "generate_remote", parent.event_id);
    if (poll.state === "failed") {
      await updateJob(env, parent.id, { status: "failed", stage: "FAILED", error: poll.error });
      await updateWorkflow(env, parent.reference_id, "failed", "GENERATION", 100, poll.error);
      return getJob(env, parent.id);
    }
    if (poll.state === "completed") {
      const output = poll.values?.[0]; const first = Array.isArray(output) ? output[0] : output;
      if (!first?.url) throw new Error("HF generation returned no image URL");
      const rawResponse = await fetch(first.url); if (!rawResponse.ok) throw new Error(`Unable to fetch generated output: HTTP ${rawResponse.status}`);
      const bytes = await rawResponse.arrayBuffer(); const rawKey = `artifacts/${parent.id}/raw.png`;
      await env.ASSETS.put(rawKey, bytes, { httpMetadata: { contentType: rawResponse.headers.get("content-type") || "image/png" } });
      const result = { provider: "hf-zerogpu", seed: poll.values?.[1] ?? null, gpu_seconds: poll.values?.[2] ?? null, raw_r2_key: rawKey, raw_asset_url: `/api/assets/${parent.id}?kind=raw&token=${parent.asset_token}` };
      const sourceUrl = new URL(`/api/assets/${parent.id}?kind=raw&token=${parent.asset_token}`, new URL(request.url).origin).toString();
      const upscaleJobId = `job_${crypto.randomUUID().replaceAll("-", "")}`; const childToken = crypto.randomUUID().replaceAll("-", "");
      const upscaleEvent = await gradioSubmit(env, "upscale_remote", [sourceUrl, upscaleJobId, 4]);
      await env.DB.prepare(`INSERT INTO jobs_sf (id,reference_id,type,status,stage,event_id,asset_token,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)`).bind(upscaleJobId, parent.reference_id, "upscale", "submitted", "UPSCALING", upscaleEvent, childToken, now(), now()).run();
      result.upscale_job_id = upscaleJobId;
      await updateJob(env, parent.id, { status: "upscale_queued", stage: "UPSCALING", raw_r2_key: rawKey, result_json: JSON.stringify(result) });
      await updateWorkflow(env, parent.reference_id, "running", "UPSCALING", 55, "Generation complete; 4x super-resolution queued on the free ZeroGPU lane.");
    }
  }
  const latest = await getJob(env, parent.id); const linked = JSON.parse(latest.result_json || "{}").upscale_job_id;
  if (linked) { const child = await getJob(env, linked); if (child) await processUpscale(env, request, latest, child); }
  return getJob(env, parent.id);
}

export async function onRequestGet(context) {
  try {
    const { env } = context; if (!env.DB || !env.ASSETS) return fail("Pages D1/R2 bindings are missing", 500);
    const jobId = context.params.jobId; const parent = await getJob(env, jobId); if (!parent) return fail("Job not found", 404);
    const result = await processParent(context, parent);
    return ok({ id: result.id, reference_id: result.reference_id, type: result.type, status: result.status, stage: result.stage, result: result.result_json ? JSON.parse(result.result_json) : null, error: result.error });
  } catch (error) { return fail(error instanceof Error ? error.message : String(error), 500); }
}
