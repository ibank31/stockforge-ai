import { WorkflowEntrypoint } from "cloudflare:workers";

const DEFAULT_HF_SPACE = "https://ibank31-stockforge-zerogpu.hf.space";

function hfBase(env) {
  return (env.STOCKFORGE_HF_SPACE_URL || DEFAULT_HF_SPACE).replace(/\/$/, "");
}

async function hfHeaders(env, extra = {}) {
  const headers = new Headers(extra);
  if (env.STOCKFORGE_HF_TOKEN) headers.set("authorization", `Bearer ${env.STOCKFORGE_HF_TOKEN}`);
  return headers;
}

async function gradioSubmit(env, apiName, data) {
  const headers = await hfHeaders(env, { "content-type": "application/json" });
  const response = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}`, {
    method: "POST",
    headers,
    body: JSON.stringify({ data }),
  });
  if (!response.ok) throw new Error(`HF ${apiName} submit failed: HTTP ${response.status}`);
  const body = await response.json();
  if (!body.event_id) throw new Error(`HF ${apiName} returned no event_id`);
  return body.event_id;
}

async function gradioPoll(env, apiName, eventId) {
  const response = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}/${eventId}`, {
    headers: await hfHeaders(env),
  });
  if (!response.ok) throw new Error(`HF ${apiName} poll failed: HTTP ${response.status}`);
  const text = await response.text();
  let event = "message";
  let data = [];
  let last = null;
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith("event:")) {
      if (data.length) last = { event, data: data.join("\n") };
      event = line.slice(6).trim();
      data = [];
    } else if (line.startsWith("data:")) {
      data.push(line.slice(5).replace(/^\s/, ""));
    }
  }
  if (data.length) last = { event, data: data.join("\n") };
  if (!last) return { state: "running" };
  if (last.event === "complete") return { state: "completed", values: JSON.parse(last.data) };
  if (last.event === "error" || last.event === "exception") return { state: "failed", error: last.data || last.event };
  return { state: "running" };
}

function parseOutput(values) {
  const output = values?.[0];
  const first = Array.isArray(output) ? output[0] : output;
  if (!first || !first.url) throw new Error("Remote worker returned no FileData URL");
  return first;
}

async function saveJob(env, jobId, patch) {
  const sets = Object.keys(patch).map((key) => `${key}=?`).join(", ");
  await env.DB.prepare(`UPDATE jobs_sf SET ${sets}, updated_at=? WHERE id=?`)
    .bind(...Object.values(patch), new Date().toISOString(), jobId)
    .run();
}

async function saveWorkflowState(env, referenceId, status, stage, progress, message) {
  await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
    .bind(status, stage, progress, message || null, new Date().toISOString(), referenceId)
    .run();
}

export class StockForgePipeline extends WorkflowEntrypoint {
  async run(event, step) {
    const payload = event.payload || {};
    const jobId = String(payload.jobId || "");
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

    const eventId = await step.do("submit ZeroGPU generation", async () => {
      if (job.event_id) return job.event_id;
      const id = await gradioSubmit(this.env, "generate_remote", [
        plan.generation_prompt,
        plan.generation.width,
        plan.generation.height,
        plan.generation.steps,
        plan.generation.seed || 0,
        !!plan.generation.randomize_seed,
        jobId,
      ]);
      await saveJob(this.env, jobId, { status: "submitted", stage: "GENERATING", event_id: id });
      await saveWorkflowState(this.env, job.reference_id, "running", "GENERATING", 25, "Generation queued on HF ZeroGPU.");
      return id;
    });

    let generationValues = null;
    for (let attempt = 1; attempt <= 40; attempt += 1) {
      await step.sleep(`wait generation ${attempt}`, "3 seconds");
      const poll = await step.do(`poll generation ${attempt}`, async () => gradioPoll(this.env, "generate_remote", eventId));
      if (poll.state === "failed") throw new Error(poll.error || "ZeroGPU generation failed");
      if (poll.state === "completed") {
        generationValues = poll.values;
        break;
      }
    }
    if (!generationValues) throw new Error("ZeroGPU generation exceeded the workflow polling window");

    const rawMeta = await step.do("ingest generated artifact", async () => {
      const file = parseOutput(generationValues);
      const response = await fetch(file.url);
      if (!response.ok) throw new Error(`Unable to fetch generated artifact: HTTP ${response.status}`);
      const key = `artifacts/${jobId}/raw.${String(file.orig_name || "png").toLowerCase().endsWith(".jpg") ? "jpg" : "png"}`;
      await this.env.ASSETS.put(key, response.body, { httpMetadata: { contentType: response.headers.get("content-type") || "image/png" } });
      return { key, seed: generationValues?.[1] ?? null, gpu_seconds: generationValues?.[2] ?? null };
    });
    await step.do("mark raw artifact", async () => {
      await saveJob(this.env, jobId, {
        status: "upscale_queued",
        stage: "UPSCALING",
        raw_r2_key: rawMeta.key,
        result_json: JSON.stringify({ provider: "hf-zerogpu", raw_r2_key: rawMeta.key, seed: rawMeta.seed, gpu_seconds: rawMeta.gpu_seconds }),
      });
      await saveWorkflowState(this.env, job.reference_id, "running", "UPSCALING", 55, "Generation complete; 4x super-resolution running on HF ZeroGPU.");
      return true;
    });

    const sourceUrl = `${this.env.PUBLIC_BASE_URL.replace(/\/$/, "")}/api/assets/${jobId}?kind=raw&token=${job.asset_token}`;
    const upscaleEventId = await step.do("submit ZeroGPU upscale", async () => gradioSubmit(this.env, "upscale_remote", [sourceUrl, `${jobId}-upscale`, 4]));

    let upscaleValues = null;
    for (let attempt = 1; attempt <= 40; attempt += 1) {
      await step.sleep(`wait upscale ${attempt}`, "3 seconds");
      const poll = await step.do(`poll upscale ${attempt}`, async () => gradioPoll(this.env, "upscale_remote", upscaleEventId));
      if (poll.state === "failed") throw new Error(poll.error || "ZeroGPU upscale failed");
      if (poll.state === "completed") {
        upscaleValues = poll.values;
        break;
      }
    }
    if (!upscaleValues) throw new Error("ZeroGPU upscale exceeded the workflow polling window");

    const finalMeta = await step.do("ingest final master", async () => {
      const file = parseOutput(upscaleValues);
      const response = await fetch(file.url);
      if (!response.ok) throw new Error(`Unable to fetch upscaled artifact: HTTP ${response.status}`);
      const key = `artifacts/${jobId}/final.jpg`;
      await this.env.ASSETS.put(key, response.body, { httpMetadata: { contentType: "image/jpeg" } });
      return { key, width: upscaleValues?.[2] ?? null, height: upscaleValues?.[3] ?? null, scale: upscaleValues?.[1] ?? 4 };
    });

    await step.do("complete production pipeline", async () => {
      const result = {
        provider: "hf-zerogpu",
        model: "Z-Image-Turbo",
        final: {
          provider: "hf-zerogpu",
          model: "RealESRGAN_x4plus",
          scale: finalMeta.scale,
          width: finalMeta.width,
          height: finalMeta.height,
          final_r2_key: finalMeta.key,
          final_asset_url: `/api/assets/${jobId}?kind=final&token=${job.asset_token}`,
        },
        similarity_gate: { decision: "REVIEW_REQUIRED", automated_duplicate_hash: "PENDING", human_review_required: true },
        technical_qa: { status: "PASS_WITH_VISUAL_REVIEW", resolution_gate: !!finalMeta.width && !!finalMeta.height && (finalMeta.width * finalMeta.height) >= 16000000 },
        human_review_required: true,
        marketplace_submission: "manual_only",
      };
      await saveJob(this.env, jobId, { status: "succeeded", stage: "READY_REVIEW", final_r2_key: finalMeta.key, result_json: JSON.stringify(result) });
      await saveWorkflowState(this.env, job.reference_id, "ready", "READY_REVIEW", 100, "Generation, 4x upscale and technical processing complete. Human visual/rights review remains mandatory.");
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
    const instance = await env.STOCKFORGE_PIPELINE.create({ id: jobId, params: { jobId } });
    return Response.json({ workflow_instance_id: instance.id, status: "queued" }, { headers: { "cache-control": "no-store" } });
  },
};
