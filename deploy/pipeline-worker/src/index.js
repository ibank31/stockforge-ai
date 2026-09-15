import { WorkflowEntrypoint } from "cloudflare:workers";

const DEFAULT_HF_SPACE = "https://ibank31-stockforge-zerogpu.hf.space";

function hfBase(env) { return (env.STOCKFORGE_HF_SPACE_URL || DEFAULT_HF_SPACE).replace(/\/$/, ""); }
async function hfHeaders(env, extra = {}) { const headers = new Headers(extra); if (env.STOCKFORGE_HF_TOKEN) headers.set("authorization", `Bearer ${env.STOCKFORGE_HF_TOKEN}`); return headers; }
async function gradioSubmit(env, apiName, data) { const response = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}`, { method: "POST", headers: await hfHeaders(env, { "content-type": "application/json" }), body: JSON.stringify({ data }) }); if (!response.ok) throw new Error(`HF ${apiName} submit failed: HTTP ${response.status}`); const body = await response.json(); if (!body.event_id) throw new Error(`HF ${apiName} returned no event_id`); return body.event_id; }
async function gradioPoll(env, apiName, eventId) { const response = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}/${eventId}`, { headers: await hfHeaders(env) }); if (!response.ok) throw new Error(`HF ${apiName} poll failed: HTTP ${response.status}`); const text = await response.text(); let event = "message"; let data = []; let last = null; for (const line of text.split(/\r?\n/)) { if (line.startsWith("event:")) { if (data.length) last = { event, data: data.join("\n") }; event = line.slice(6).trim(); data = []; } else if (line.startsWith("data:")) data.push(line.slice(5).replace(/^\s/, "")); } if (data.length) last = { event, data: data.join("\n") }; if (!last) return { state: "running" }; if (last.event === "complete") return { state: "completed", values: JSON.parse(last.data) }; if (last.event === "error" || last.event === "exception") return { state: "failed", error: last.data || last.event }; return { state: "running"); }
function parseOutput(values) { const output = values?.[0]; const first = Array.isArray(output) ? output[0] : output; if (!first?.url) throw new Error("Remote worker returned no FileData URL"); return first; }
async function sha256Hex(arrayBuffer) { const digest = await crypto.subtle.digest("SHA-256", arrayBuffer); return [...new Uint8Array(digest)].map((v) => v.toString(16).padStart(2, "0")).join(""); }
async function saveJob(env, jobId, patch) { const sets = Object.keys(patch).map((key) => `${key}=?`).join(", "); await env.DB.prepare(`UPDATE jobs_sf SET ${sets}, updated_at=? WHERE id=?`).bind(...Object.values(patch), new Date().toISOString(), jobId).run(); }
async function saveWorkflowState(env, referenceId, status, stage, progress, message) { await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`).bind(status,stage,progress,message||null,new Date().toISOString(),referenceId).run(); }

export class StockForgePipeline extends WorkflowEntrypoint {
  async run(event, step) {
    const jobId = String(event.payload?.jobId || "");
    if (!jobId) throw new Error("jobId is required");
    if (!this.env.DB || !this.env.ASSETS) throw new Error("D1/R2 bindings are missing");

    const job = await step.do("load generation job", async () => {
      const row = await this.env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
      if (!row) throw new Error(`Generation job ${jobId} not found`);
      return row;
    });
    const planRow = await step.do("load creative plan", async () => {
      const row = await this.env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(job.reference_id).first();
      if (!row) throw new Error("Creative plan not found");
      return row;
    });
    const plan = JSON.parse(planRow.plan_json);

    const generationEvent = await step.do("submit ZeroGPU generation", async () => {
      const existing = job.event_id;
      if (existing) return existing;
      const remote = await gradioSubmit(this.env, "generate_remote", [plan.generation_prompt, plan.generation.width, plan.generation.height, plan.generation.steps, plan.generation.seed || 0, !!plan.generation.randomize_seed, jobId]);
      await saveJob(this.env, jobId, { status: "submitted", stage: "GENERATING", event_id: remote });
      await saveWorkflowState(this.env, job.reference_id, "running", "GENERATING", 25, "Generation queued on HF ZeroGPU.");
      return remote;
    });

    let generationValues = null;
    for (let attempt = 1; attempt <= 80; attempt += 1) {
      await step.sleep(`wait generation ${attempt}`, "3 seconds");
      const poll = await step.do(`poll generation ${attempt}`, async () => gradioPoll(this.env, "generate_remote", generationEvent));
      if (poll.state === "failed") throw new Error(poll.error || "ZeroGPU generation failed");
      if (poll.state === "completed") { generationValues = poll.values; break; }
    }
    if (!generationValues) throw new Error("ZeroGPU generation exceeded the workflow polling window");

    const rawMeta = await step.do("ingest generated artifact", async () => {
      const file = parseOutput(generationValues);
      const response = await fetch(file.url);
      if (!response.ok) throw new Error(`Unable to fetch generated artifact: HTTP ${response.status}`);
      const body = await response.arrayBuffer();
      const key = `artifacts/${jobId}/raw.png`;
      await this.env.ASSETS.put(key, body, { httpMetadata: { contentType: "image/png" } });
      return { key, sha256: await sha256Hex(body), seed: generationValues?.[1] ?? null, gpu_seconds: generationValues?.[2] ?? null };
    });
    await step.do("mark raw artifact", async () => {
      await saveJob(this.env, jobId, { status: "upscale_queued", stage: "UPSCALING", raw_r2_key: rawMeta.key, result_json: JSON.stringify({ provider: "hf-zerogpu", raw_r2_key: rawMeta.key, raw_sha256: rawMeta.sha256, seed: rawMeta.seed, gpu_seconds: rawMeta.gpu_seconds }) });
      await saveWorkflowState(this.env, job.reference_id, "running", "UPSCALING", 55, "Generation complete; 4x super-resolution running on HF ZeroGPU.");
      return true;
    });

    const sourceUrl = `${this.env.PUBLIC_BASE_URL.replace(/\/$/, "")}/api/assets/${jobId}?kind=raw&token=${job.asset_token}`;
    const upscaleEvent = await step.do("submit ZeroGPU upscale", async () => gradioSubmit(this.env, "upscale_remote", [sourceUrl, `${jobId}-upscale`, 4]));
    let upscaleValues = null;
    for (let attempt = 1; attempt <= 80; attempt += 1) {
      await step.sleep(`wait upscale ${attempt}`, "3 seconds");
      const poll = await step.do(`poll upscale ${attempt}`, async () => gradioPoll(this.env, "upscale_remote", upscaleEvent));
      if (poll.state === "failed") throw new Error(poll.error || "ZeroGPU upscale failed");
      if (poll.state === "completed") { upscaleValues = poll.values; break; }
    }
    if (!upscaleValues) throw new Error("ZeroGPU upscale exceeded the workflow polling window");

    const finalMeta = await step.do("ingest final master", async () => {
      const file = parseOutput(upscaleValues);
      const response = await fetch(file.url);
      if (!response.ok) throw new Error(`Unable to fetch upscaled artifact: HTTP ${response.status}`);
      const body = await response.arrayBuffer();
      const key = `artifacts/${jobId}/final.jpg`;
      const hash = await sha256Hex(body);
      await this.env.ASSETS.put(key, body, { httpMetadata: { contentType: "image/jpeg" } });
      return { key, sha256: hash, width: upscaleValues?.[2] ?? null, height: upscaleValues?.[3] ?? null, scale: upscaleValues?.[1] ?? 4, bytes: body.byteLength };
    });

    await step.do("complete production pipeline", async () => {
      const duplicate = await this.env.DB.prepare(`SELECT id FROM jobs_sf WHERE artifact_sha256=? AND id<>? AND status IN ('succeeded','approved') LIMIT 1`).bind(finalMeta.sha256, jobId).first();
      const mp = finalMeta.width && finalMeta.height ? (finalMeta.width * finalMeta.height) / 1000000 : 0;
      const result = {
        provider: "hf-zerogpu",
        model: "Z-Image-Turbo",
        raw_r2_key: rawMeta.key,
        raw_sha256: rawMeta.sha256,
        final: { provider: "hf-zerogpu", model: "RealESRGAN_x4plus", scale: finalMeta.scale, width: finalMeta.width, height: finalMeta.height, megapixels: Number(mp.toFixed(4)), size_bytes: finalMeta.bytes, sha256: finalMeta.sha256, final_r2_key: finalMeta.key, final_asset_url: `/api/assets/${jobId}?kind=final&token=${job.asset_token}` },
        similarity_gate: { automated_duplicate: duplicate ? "BLOCK" : "PASS", duplicate_of_job: duplicate?.id || null, semantic_reference_similarity: "HUMAN_REVIEW_REQUIRED", decision: duplicate ? "BLOCK" : "REVIEW_REQUIRED", human_review_required: true },
        technical_qa: { status: mp >= 16 ? "PASS_WITH_VISUAL_REVIEW" : "FAIL", format: "JPEG", color_space: "sRGB", dimensions: { width: finalMeta.width, height: finalMeta.height }, megapixels: Number(mp.toFixed(4)), resolution_gate: mp >= 16 },
        human_review_required: true,
        marketplace_submission: "manual_only",
      };
      await saveJob(this.env, jobId, { status: duplicate || mp < 16 ? "blocked" : "succeeded", stage: duplicate ? "BLOCKED_DUPLICATE" : "READY_REVIEW", artifact_sha256: finalMeta.sha256, final_r2_key: finalMeta.key, result_json: JSON.stringify(result), error: duplicate ? `Exact duplicate of ${duplicate.id}` : (mp < 16 ? "Final master below 16 MP" : null) });
      await saveWorkflowState(this.env, job.reference_id, duplicate || mp < 16 ? "blocked" : "ready", duplicate ? "SIMILARITY_BLOCK" : "READY_REVIEW", 100, duplicate ? "Exact duplicate detected; human intervention required." : (mp < 16 ? "Final master is below the configured 16 MP production gate." : "Generation and 4x upscale complete. Human visual/rights review remains mandatory."));
      return result;
    });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method !== "POST" || url.pathname !== "/start") return new Response("Not Found", { status: 404 });
    if (!env.STOCKFORGE_PIPELINE) return Response.json({ detail: "Workflow binding missing" }, { status: 500 });
    const body = await request.json();
    const jobId = String(body?.job_id || "");
    if (!jobId) return Response.json({ detail: "job_id is required" }, { status: 400 });
    const existing = await env.STOCKFORGE_PIPELINE.get(jobId);
    try {
      const state = await existing.status();
      return Response.json({ workflow_instance_id: jobId, status: state?.status || "queued" }, { headers: { "cache-control": "no-store" } });
    } catch (_) {
      const instance = await env.STOCKFORGE_PIPELINE.create({ id: jobId, params: { jobId } });
      return Response.json({ workflow_instance_id: instance.id, status: "queued" }, { headers: { "cache-control": "no-store" } });
    }
  },
};
