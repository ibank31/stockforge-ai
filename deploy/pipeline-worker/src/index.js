import { WorkflowEntrypoint } from "cloudflare:workers";

const DEFAULT_HF_SPACE = "https://ibank31-stockforge-zerogpu.hf.space";
const GENERATE_POLL_ATTEMPTS = 180;
const UPSCALE_POLL_ATTEMPTS = 360;

function hfBase(env) {
  return (env.STOCKFORGE_HF_SPACE_URL || DEFAULT_HF_SPACE).replace(/\/$/, "");
}

async function hfHeaders(env, extra = {}) {
  const headers = new Headers(extra);
  if (env.STOCKFORGE_HF_TOKEN) headers.set("authorization", `Bearer ${env.STOCKFORGE_HF_TOKEN}`);
  return headers;
}

async function gradioSubmit(env, apiName, data) {
  const response = await fetch(`${hfBase(env)}/gradio_api/call/${apiName}`, {
    method: "POST",
    headers: await hfHeaders(env, { "content-type": "application/json" }),
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
  if (!first?.url) throw new Error("Remote worker returned no FileData URL");
  return first;
}

async function sha256Hex(arrayBuffer) {
  const digest = await crypto.subtle.digest("SHA-256", arrayBuffer);
  return [...new Uint8Array(digest)].map((v) => v.toString(16).padStart(2, "0")).join("");
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

async function recordJobEvent(env, jobId, eventType, stage, status, message, details = null) {
  await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`)
    .bind(jobId, eventType, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, new Date().toISOString())
    .run();
}

function parseMode(event) {
  const mode = String(event.payload?.mode || "generate");
  if (mode !== "generate" && mode !== "upscale") throw new Error(`Unsupported pipeline mode: ${mode}`);
  return mode;
}

function classifyFailure(error) {
  const message = error instanceof Error ? error.message : String(error);
  const transient = /(HTTP 429|HTTP 5\d\d|timeout|timed out|network|fetch failed|temporarily|queue|polling window|service unavailable|overloaded|rate limit)/i.test(message);
  if (transient) return { retryable: 1, code: "TRANSIENT_PROVIDER" };
  if (/no FileData|malformed|JSON\.parse|Unsupported pipeline mode|not found/i.test(message)) return { retryable: 0, code: "TERMINAL_PIPELINE" };
  return { retryable: 1, code: "UNKNOWN_RETRYABLE" };
}

function pollDelaySeconds(label, attempt) {
  if (label === "generation") return attempt < 12 ? 5 : 10;
  return attempt < 12 ? 5 : 10;
}

async function pollUntilComplete(env, step, apiName, eventId, maxAttempts, label) {
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    await step.sleep(`wait ${label} ${attempt}`, `${pollDelaySeconds(label, attempt)} seconds`);
    const poll = await step.do(`poll ${label} ${attempt}`, async () => gradioPoll(env, apiName, eventId));
    if (poll.state === "failed") throw new Error(poll.error || `ZeroGPU ${label} failed`);
    if (poll.state === "completed") return poll.values;
  }
  throw new Error(`ZeroGPU ${label} exceeded the workflow polling window`);
}

export class StockForgePipeline extends WorkflowEntrypoint {
  async run(event, step) {
    const jobId = String(event.payload?.jobId || "");
    try {
      return await this.runInternal(event, step);
    } catch (error) {
      const mode = String(event.payload?.mode || "generate");
      const failure = classifyFailure(error);
      const detail = (error instanceof Error ? error.message : String(error)).slice(0, 2000);
      if (this.env.DB && jobId) {
        const job = await this.env.DB.prepare(`SELECT status,reference_id FROM jobs_sf WHERE id=?`).bind(jobId).first();
        if (job && !["ready_upscale", "succeeded", "approved", "blocked"].includes(job.status)) {
          const stage = mode === "upscale" ? "FAILED_UPSCALE" : "FAILED_GENERATION";
          await saveJob(this.env, jobId, {
            status: "failed",
            stage,
            error: detail,
            failed_mode: mode,
            failure_code: failure.code,
            retryable: failure.retryable,
          });
          await recordJobEvent(this.env, jobId, "workflow_failed", stage, "failed", detail, { mode, retryable: Boolean(failure.retryable), failure_code: failure.code });
          if (job.reference_id) await saveWorkflowState(this.env, job.reference_id, "failed", stage, 100, `${detail}${failure.retryable ? " Retry is allowed." : " Retry is not allowed."}`);
        }
      }
      throw error;
    }
  }

  async runInternal(event, step) {
    const jobId = String(event.payload?.jobId || "");
    const mode = parseMode(event);
    if (!jobId) throw new Error("jobId is required");
    if (!this.env.DB || !this.env.ASSET_STORE) throw new Error("D1/R2 bindings are missing");

    const job = await step.do("load generation job", async () => {
      const row = await this.env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
      if (!row) throw new Error(`Generation job ${jobId} not found`);
      return row;
    });

    const plan = await step.do("load creative plan", async () => {
      const row = await this.env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(job.reference_id).first();
      if (!row) throw new Error("Creative plan not found");
      return JSON.parse(row.plan_json);
    });

    if (mode === "generate") {
      const generationEvent = await step.do("submit ZeroGPU generation", async () => {
        if (job.event_id) return job.event_id;
        const remote = await gradioSubmit(this.env, "generate_remote", [
          plan.generation_prompt,
          plan.generation.width,
          plan.generation.height,
          plan.generation.steps,
          plan.generation.seed || 0,
          !!plan.generation.randomize_seed,
          jobId,
        ]);
        await saveJob(this.env, jobId, { status: "submitted", stage: "GENERATING", event_id: remote, error: null });
        await recordJobEvent(this.env, jobId, "zerogpu_generation_submitted", "GENERATING", "submitted", "Generation submitted to HF ZeroGPU.", { event_id: remote });
        await saveWorkflowState(this.env, job.reference_id, "running", "GENERATING", 25, "Generation queued on HF ZeroGPU.");
        return remote;
      });

      const generationValues = await pollUntilComplete(this.env, step, "generate_remote", generationEvent, GENERATE_POLL_ATTEMPTS, "generation");
      const rawMeta = await step.do("ingest generated artifact", async () => {
        const file = parseOutput(generationValues);
        const response = await fetch(file.url);
        if (!response.ok) throw new Error(`Unable to fetch generated artifact: HTTP ${response.status}`);
        const body = await response.arrayBuffer();
        const key = `artifacts/${jobId}/raw.png`;
        await this.env.ASSET_STORE.put(key, body, { httpMetadata: { contentType: "image/png" } });
        return {
          key,
          sha256: await sha256Hex(body),
          seed: generationValues?.[1] ?? null,
          gpu_seconds: generationValues?.[2] ?? null,
          bytes: body.byteLength,
        };
      });

      const rawResult = {
        provider: "hf-zerogpu",
        model: "Z-Image-Turbo",
        raw_r2_key: rawMeta.key,
        raw_sha256: rawMeta.sha256,
        raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`,
        seed: rawMeta.seed,
        gpu_seconds: rawMeta.gpu_seconds,
        size_bytes: rawMeta.bytes,
        next_stage: "READY_UPSCALE",
      };

      await step.do("release generation GPU", async () => {
        await saveJob(this.env, jobId, {
          status: "ready_upscale",
          stage: "READY_UPSCALE",
          raw_r2_key: rawMeta.key,
          result_json: JSON.stringify(rawResult),
          error: null,
          retryable: 0,
          failed_mode: null,
          failure_code: null,
        });
        await recordJobEvent(this.env, jobId, "generation_complete", "READY_UPSCALE", "ready_upscale", "Generation complete. GPU released; 4x finalization is a separate request.", { raw_r2_key: rawMeta.key, gpu_seconds: rawMeta.gpu_seconds });
        await saveWorkflowState(this.env, job.reference_id, "ready", "READY_UPSCALE", 55, "Generation complete. GPU released; 4x finalization is a separate request.");
        return true;
      });
      return rawResult;
    }

    if (!job.raw_r2_key) throw new Error("Raw artifact is not ready for upscale");
    if (job.status === "succeeded" || job.status === "approved") {
      const result = job.result_json ? JSON.parse(job.result_json) : {};
      return result;
    }

    await step.do("mark upscale running", async () => {
      await saveJob(this.env, jobId, { status: "upscale_submitted", stage: "UPSCALING", error: null, retryable: 0, failed_mode: null, failure_code: null });
      await recordJobEvent(this.env, jobId, "upscale_started", "UPSCALING", "upscale_submitted", "4x finalization workflow started.");
      await saveWorkflowState(this.env, job.reference_id, "running", "UPSCALING", 70, "4x finalization queued on HF ZeroGPU.");
      return true;
    });

    const sourceUrl = `${this.env.PUBLIC_BASE_URL.replace(/\/$/, "")}/api/assets/${jobId}?kind=raw&token=${job.asset_token}`;
    const upscaleEvent = await step.do("submit ZeroGPU upscale", async () => {
      const remote = await gradioSubmit(this.env, "upscale_remote", [sourceUrl, `${jobId}-upscale`, 4]);
      await saveJob(this.env, jobId, {
        status: "upscaling",
        stage: "UPSCALING",
        result_json: JSON.stringify({
          provider: "hf-zerogpu",
          model: "Z-Image-Turbo",
          raw_r2_key: job.raw_r2_key,
          raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`,
          upscale_event_id: remote,
          next_stage: "UPSCALING",
        }),
      });
      await recordJobEvent(this.env, jobId, "zerogpu_upscale_submitted", "UPSCALING", "upscaling", "Upscale submitted to HF ZeroGPU.", { event_id: remote });
      return remote;
    });

    const upscaleValues = await pollUntilComplete(this.env, step, "upscale_remote", upscaleEvent, UPSCALE_POLL_ATTEMPTS, "upscale");

    const finalMeta = await step.do("ingest final master", async () => {
      const file = parseOutput(upscaleValues);
      const response = await fetch(file.url);
      if (!response.ok) throw new Error(`Unable to fetch upscaled artifact: HTTP ${response.status}`);
      const body = await response.arrayBuffer();
      const key = `artifacts/${jobId}/final.jpg`;
      const hash = await sha256Hex(body);
      await this.env.ASSET_STORE.put(key, body, { httpMetadata: { contentType: "image/jpeg" } });
      return {
        key,
        sha256: hash,
        width: upscaleValues?.[2] ?? null,
        height: upscaleValues?.[3] ?? null,
        scale: upscaleValues?.[1] ?? 4,
        bytes: body.byteLength,
      };
    });

    return await step.do("complete production pipeline", async () => {
      const duplicate = await this.env.DB.prepare(`SELECT id FROM jobs_sf WHERE artifact_sha256=? AND id<>? AND status IN ('succeeded','approved') LIMIT 1`)
        .bind(finalMeta.sha256, jobId).first();
      const mp = finalMeta.width && finalMeta.height ? (finalMeta.width * finalMeta.height) / 1000000 : 0;
      const result = {
        provider: "hf-zerogpu",
        model: "Z-Image-Turbo",
        raw_r2_key: job.raw_r2_key,
        raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`,
        final: {
          provider: "hf-zerogpu",
          model: "RealESRGAN_x4plus",
          scale: finalMeta.scale,
          width: finalMeta.width,
          height: finalMeta.height,
          megapixels: Number(mp.toFixed(4)),
          size_bytes: finalMeta.bytes,
          sha256: finalMeta.sha256,
          final_r2_key: finalMeta.key,
          final_asset_url: `/api/assets/${jobId}?kind=final&token=${job.asset_token}`,
        },
        similarity_gate: {
          automated_duplicate: duplicate ? "BLOCK" : "PASS",
          duplicate_of_job: duplicate?.id || null,
          semantic_reference_similarity: "HUMAN_REVIEW_REQUIRED",
          decision: duplicate ? "BLOCK" : "REVIEW_REQUIRED",
          human_review_required: true,
        },
        technical_qa: {
          status: mp >= 16 ? "PASS_WITH_VISUAL_REVIEW" : "FAIL",
          format: "JPEG",
          color_space: "sRGB",
          dimensions: { width: finalMeta.width, height: finalMeta.height },
          megapixels: Number(mp.toFixed(4)),
          resolution_gate: mp >= 16,
        },
        human_review_required: true,
        marketplace_submission: "manual_only",
      };
      const blocked = Boolean(duplicate || mp < 16);
      await saveJob(this.env, jobId, {
        status: blocked ? "blocked" : "succeeded",
        stage: duplicate ? "BLOCKED_DUPLICATE" : (mp < 16 ? "BLOCKED_RESOLUTION" : "READY_REVIEW"),
        artifact_sha256: finalMeta.sha256,
        final_r2_key: finalMeta.key,
        result_json: JSON.stringify(result),
        error: duplicate ? `Exact duplicate of ${duplicate.id}` : (mp < 16 ? "Final master below 16 MP" : null),
        retryable: 0,
        failed_mode: null,
        failure_code: duplicate ? "EXACT_DUPLICATE" : (mp < 16 ? "RESOLUTION_GATE" : null),
      });
      await recordJobEvent(this.env, jobId, blocked ? "production_blocked" : "production_ready_review", duplicate ? "BLOCKED_DUPLICATE" : (mp < 16 ? "BLOCKED_RESOLUTION" : "READY_REVIEW"), blocked ? "blocked" : "succeeded", blocked ? (duplicate ? `Exact duplicate of ${duplicate.id}` : "Final master below 16 MP") : "4x finalization complete. Human visual/rights review remains mandatory.", { megapixels: mp, sha256: finalMeta.sha256 });
      await saveWorkflowState(
        this.env,
        job.reference_id,
        blocked ? "blocked" : "ready",
        duplicate ? "SIMILARITY_BLOCK" : (mp < 16 ? "TECHNICAL_QA_FAIL" : "READY_REVIEW"),
        100,
        duplicate
          ? "Exact duplicate detected; human intervention required."
          : (mp < 16 ? "Final master is below the configured 16 MP production gate." : "4x finalization complete. Human visual/rights review remains mandatory."),
      );
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
    const mode = String(body?.mode || "generate");
    const workflowId = String(body?.workflow_id || (mode === "generate" ? jobId : `${jobId}-upscale-${crypto.randomUUID().replaceAll("-", "")}`));
    if (!jobId) return Response.json({ detail: "job_id is required" }, { status: 400 });
    if (mode !== "generate" && mode !== "upscale") return Response.json({ detail: "mode must be generate or upscale" }, { status: 400 });
    const instance = await env.STOCKFORGE_PIPELINE.create({ id: workflowId, params: { jobId, mode } });
    return Response.json({ workflow_instance_id: instance.id, status: "queued", mode }, { headers: { "cache-control": "no-store" } });
  },
};
