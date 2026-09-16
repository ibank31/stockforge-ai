import { WorkflowEntrypoint } from "cloudflare:workers";

const HF_BASE = "https://ibank31-stockforge-zerogpu.hf.space";
const FALLBACK_BASE = "https://stockforge-ai.pages.dev";
const GENERATE_POLL_ATTEMPTS = 180;
const UPSCALE_POLL_ATTEMPTS = 360;
const QWEN_CANVASES = [
  [1328, 1328],
  [1664, 928],
  [928, 1664],
  [1472, 1104],
  [1104, 1472],
  [1584, 1056],
  [1056, 1584],
];

function now() { return new Date().toISOString(); }
function baseOf(env, fallback = false) {
  const value = fallback ? (env.STOCKFORGE_FALLBACK_BASE || FALLBACK_BASE) : (env.STOCKFORGE_HF_SPACE_URL || HF_BASE);
  return String(value).replace(/\/$/, "");
}
function authHeaders(env, extra = {}) {
  const headers = { ...extra };
  const token = String(env.STOCKFORGE_HF_TOKEN || "").trim();
  if (token) headers.authorization = `Bearer ${token}`;
  return headers;
}
function qwenCanvas(width, height) {
  const w = Number(width) || 1328;
  const h = Number(height) || 1328;
  const aspect = w / Math.max(1, h);
  return QWEN_CANVASES.reduce((best, current) => {
    const bestDelta = Math.abs(best[0] / best[1] - aspect);
    const currentDelta = Math.abs(current[0] / current[1] - aspect);
    return currentDelta < bestDelta ? current : best;
  }, QWEN_CANVASES[0]);
}
function mimeFromBytes(bytes) {
  if (bytes.length >= 3 && bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255) return "image/jpeg";
  if (bytes.length >= 8 && bytes[0] === 137 && bytes[1] === 80 && bytes[2] === 78 && bytes[3] === 71) return "image/png";
  if (bytes.length >= 12 && bytes[0] === 82 && bytes[1] === 73 && bytes[2] === 70 && bytes[8] === 87 && bytes[9] === 69 && bytes[10] === 66 && bytes[11] === 80) return "image/webp";
  return "application/octet-stream";
}
function extensionForMime(mime) {
  if (mime === "image/png") return "png";
  if (mime === "image/webp") return "webp";
  return "jpg";
}

async function remoteSubmit(base, apiName, data, env) {
  const response = await fetch(`${base}/gradio_api/call/${apiName}`, {
    method: "POST",
    headers: authHeaders(env, { "content-type": "application/json" }),
    body: JSON.stringify({ data }),
  });
  if (!response.ok) throw new Error(`Remote ${apiName} submit failed: HTTP ${response.status}`);
  const body = await response.json();
  if (!body.event_id) throw new Error(`Remote ${apiName} returned no event_id`);
  return body.event_id;
}

async function remotePoll(base, apiName, eventId, env) {
  const response = await fetch(`${base}/gradio_api/call/${apiName}/${eventId}`, {
    headers: authHeaders(env, { "cache-control": "no-cache" }),
  });
  if (!response.ok) throw new Error(`Remote ${apiName} poll failed: HTTP ${response.status}`);
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
  if (!last) return { state: "running", event: "heartbeat" };
  if (last.event === "complete") return { state: "completed", values: JSON.parse(last.data), event: last.event };
  if (last.event === "error" || last.event === "exception") return { state: "failed", error: last.data || last.event, event: last.event };
  let detail = last.data || null;
  try { detail = JSON.parse(last.data); } catch {}
  return { state: "running", event: last.event, detail };
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
  await env.DB.prepare(`UPDATE jobs_sf SET ${sets}, updated_at=? WHERE id=?`).bind(...Object.values(patch), now(), jobId).run();
}
async function saveWorkflowState(env, referenceId, status, stage, progress, message) {
  await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`).bind(status, stage, progress, message || null, now(), referenceId).run();
}
async function recordJobEvent(env, jobId, eventType, stage, status, message, details = null) {
  await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`).bind(jobId, eventType, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, now()).run();
}
function parseMode(event) {
  const mode = String(event.payload?.mode || "generate");
  if (mode !== "generate" && mode !== "upscale") throw new Error(`Unsupported pipeline mode: ${mode}`);
  return mode;
}
function classifyFailure(error) {
  const message = error instanceof Error ? error.message : String(error);
  const retryable = /(HTTP 429|HTTP 5\d\d|timeout|timed out|network|fetch failed|temporarily|queue|service unavailable|overloaded|rate limit|quota)/i.test(message);
  if (retryable) return { retryable: 1, code: "TRANSIENT_PROVIDER" };
  if (/no FileData|malformed|JSON\.parse|Unsupported pipeline mode|not found/i.test(message)) return { retryable: 0, code: "TERMINAL_PIPELINE" };
  return { retryable: 1, code: "UNKNOWN_RETRYABLE" };
}

async function runRemote(env, step, apiName, data, maxAttempts, label, jobId) {
  const primary = baseOf(env, false);
  const fallback = baseOf(env, true);
  let lastError;
  const candidates = [
    { base: primary, provider: "hf-zerogpu" },
    ...(fallback !== primary ? [{ base: fallback, provider: "cloudflare-workers-ai-fallback" }] : []),
  ];

  for (const candidate of candidates) {
    try {
      const eventId = await step.do(`${label} submit ${candidate.provider}`, () => remoteSubmit(candidate.base, apiName, data, env));
      for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
        await step.sleep(`${label} wait ${attempt} ${candidate.provider}`, `${attempt < 12 ? 5 : 10} seconds`);
        const poll = await step.do(`${label} poll ${attempt} ${candidate.provider}`, () => remotePoll(candidate.base, apiName, eventId, env));
        if (poll.event === "heartbeat") continue;
        if (poll.state === "failed") throw new Error(poll.error || `Remote ${label} failed`);
        if (poll.state === "completed") return { values: poll.values, provider: candidate.provider, event_id: eventId };
      }
      throw new Error(`Remote ${label} exceeded the workflow polling window`);
    } catch (error) {
      lastError = error;
      if (candidate.provider === "hf-zerogpu") {
        await recordJobEvent(env, jobId, "provider_fallback", label.toUpperCase(), "fallback", "HF ZeroGPU path failed; free Cloudflare fallback will be attempted.", { error: String(error), from: "hf-zerogpu", to: "cloudflare-workers-ai-fallback" });
      }
    }
  }
  throw lastError || new Error(`Remote ${label} failed`);
}

export class StockForgePipeline extends WorkflowEntrypoint {
  async run(event, step) {
    const jobId = String(event.payload?.jobId || "");
    const mode = parseMode(event);
    try {
      return await this.runInternal(event, step);
    } catch (error) {
      const failure = classifyFailure(error);
      const detail = (error instanceof Error ? error.message : String(error)).slice(0, 2000);
      if (this.env.DB && jobId) {
        const row = await this.env.DB.prepare(`SELECT status,reference_id FROM jobs_sf WHERE id=?`).bind(jobId).first();
        if (row && !["ready_upscale", "succeeded", "approved", "blocked"].includes(row.status)) {
          const stage = mode === "upscale" ? "FAILED_UPSCALE" : "FAILED_GENERATION";
          await saveJob(this.env, jobId, { status: "failed", stage, error: detail, failed_mode: mode, failure_code: failure.code, retryable: failure.retryable });
          await recordJobEvent(this.env, jobId, "workflow_failed", stage, "failed", detail, { mode, retryable: Boolean(failure.retryable), failure_code: failure.code });
          if (row.reference_id) await saveWorkflowState(this.env, row.reference_id, "failed", stage, 100, `${detail}${failure.retryable ? " Retry is allowed." : " Retry is not allowed."}`);
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
      const [width, height] = qwenCanvas(plan.generation?.width, plan.generation?.height);
      const remote = await runRemote(
        this.env,
        step,
        "generate_remote",
        [plan.generation_prompt, width, height, 4, plan.generation?.seed || 0, !!plan.generation?.randomize_seed, jobId],
        GENERATE_POLL_ATTEMPTS,
        "generation",
        jobId,
      );
      const rawMeta = await step.do("ingest generated artifact", async () => {
        const file = parseOutput(remote.values);
        const response = await fetch(file.url);
        if (!response.ok) throw new Error(`Unable to fetch generated artifact: HTTP ${response.status}`);
        const body = await response.arrayBuffer();
        const bytes = new Uint8Array(body);
        const mime = mimeFromBytes(bytes);
        const ext = extensionForMime(mime);
        const key = `artifacts/${jobId}/raw.${ext}`;
        await this.env.ASSET_STORE.put(key, body, { httpMetadata: { contentType: mime === "application/octet-stream" ? "image/png" : mime } });
        return { key, sha256: await sha256Hex(body), bytes: body.byteLength, mime, width, height };
      });
      const rawResult = {
        provider: remote.provider,
        model: remote.provider === "hf-zerogpu" ? "Qwen-Image-2512 + Lightning 4-step" : "stable-diffusion-xl-lightning",
        raw_r2_key: rawMeta.key,
        raw_sha256: rawMeta.sha256,
        raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`,
        size_bytes: rawMeta.bytes,
        mime: rawMeta.mime,
        generation: { canvas: [width, height], seed: remote.values?.[1] ?? null, gpu_seconds: remote.values?.[2] ?? 0 },
        next_stage: "READY_UPSCALE",
      };
      await step.do("release generation compute", async () => {
        await saveJob(this.env, jobId, { status: "ready_upscale", stage: "READY_UPSCALE", raw_r2_key: rawMeta.key, result_json: JSON.stringify(rawResult), error: null, retryable: 0, failed_mode: null, failure_code: null });
        await recordJobEvent(this.env, jobId, "generation_complete", "READY_UPSCALE", "ready_upscale", "Generation complete. Compute released; finalization is separate.", { provider: remote.provider, model: rawResult.model, canvas: [width, height] });
        await saveWorkflowState(this.env, job.reference_id, "ready", "READY_UPSCALE", 55, "Generation complete. Finalization is a separate request.");
      });
      return rawResult;
    }

    if (!job.raw_r2_key) throw new Error("Raw artifact is not ready for finalization");
    if (job.status === "succeeded" || job.status === "approved") return job.result_json ? JSON.parse(job.result_json) : {};

    await step.do("mark finalization running", async () => {
      await saveJob(this.env, jobId, { status: "upscale_submitted", stage: "UPSCALING", error: null, retryable: 0, failed_mode: null, failure_code: null });
      await recordJobEvent(this.env, jobId, "upscale_started", "UPSCALING", "upscale_submitted", "Finalization workflow started.");
      await saveWorkflowState(this.env, job.reference_id, "running", "UPSCALING", 70, "Finalization queued.");
    });

    const sourceUrl = `${this.env.PUBLIC_BASE_URL.replace(/\/$/, "")}/api/assets/${jobId}?kind=raw&token=${job.asset_token}`;
    const remote = await runRemote(this.env, step, "upscale_remote", [sourceUrl, `${jobId}-upscale`], UPSCALE_POLL_ATTEMPTS, "upscale", jobId);
    const finalMeta = await step.do("ingest final master", async () => {
      const file = parseOutput(remote.values);
      const response = await fetch(file.url);
      if (!response.ok) throw new Error(`Unable to fetch final artifact: HTTP ${response.status}`);
      const body = await response.arrayBuffer();
      const bytes = new Uint8Array(body);
      const mime = mimeFromBytes(bytes);
      const isHF = remote.provider === "hf-zerogpu";
      const width = isHF ? Number(remote.values?.[1]) : Number(remote.values?.[2] || 2048);
      const height = isHF ? Number(remote.values?.[2]) : Number(remote.values?.[3] || 2048);
      const scale = isHF ? Number(remote.values?.[3] || 4) : 1;
      const key = `artifacts/${jobId}/final.jpg`;
      await this.env.ASSET_STORE.put(key, body, { httpMetadata: { contentType: "image/jpeg" } });
      return { key, sha256: await sha256Hex(body), width, height, scale, bytes: body.byteLength, mime };
    });

    return await step.do("complete production pipeline", async () => {
      const duplicate = await this.env.DB.prepare(`SELECT id FROM jobs_sf WHERE artifact_sha256=? AND id<>? AND status IN ('succeeded','approved') LIMIT 1`).bind(finalMeta.sha256, jobId).first();
      const mp = finalMeta.width && finalMeta.height ? (finalMeta.width * finalMeta.height) / 1000000 : 0;
      const qa = {
        status: mp >= 4 && mp <= 100 && finalMeta.bytes <= 45 * 1024 * 1024 && finalMeta.mime === "image/jpeg" ? "PASS_WITH_VISUAL_REVIEW" : "FAIL",
        format: finalMeta.mime === "image/jpeg" ? "JPEG" : finalMeta.mime,
        color_space: "sRGB",
        dimensions: { width: finalMeta.width, height: finalMeta.height },
        megapixels: Number(mp.toFixed(4)),
        resolution_gate: mp >= 4 && mp <= 100,
        file_size_gate: finalMeta.bytes <= 45 * 1024 * 1024,
      };
      const result = {
        provider: remote.provider,
        model: resultModel(remote.provider),
        raw_r2_key: job.raw_r2_key,
        raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`,
        final: {
          provider: remote.provider,
          model: resultModel(remote.provider),
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
        technical_qa: qa,
        human_review_required: true,
        marketplace_submission: "manual_only",
      };
      const blocked = Boolean(duplicate || qa.status === "FAIL");
      await saveJob(this.env, jobId, { status: blocked ? "blocked" : "succeeded", stage: duplicate ? "BLOCKED_DUPLICATE" : (qa.status === "FAIL" ? "BLOCKED_TECHNICAL_QA" : "READY_REVIEW"), artifact_sha256: finalMeta.sha256, final_r2_key: finalMeta.key, result_json: JSON.stringify(result), error: duplicate ? `Exact duplicate of ${duplicate.id}` : (qa.status === "FAIL" ? "Final asset failed technical QA" : null), retryable: 0, failed_mode: null, failure_code: duplicate ? "EXACT_DUPLICATE" : (qa.status === "FAIL" ? "TECHNICAL_QA" : null) });
      await recordJobEvent(this.env, jobId, blocked ? "production_blocked" : "production_ready_review", blocked ? "BLOCKED" : "READY_REVIEW", blocked ? "blocked" : "succeeded", blocked ? (duplicate ? `Exact duplicate of ${duplicate.id}` : "Final asset failed technical QA") : "Finalization complete. Human visual/rights review remains mandatory.", { provider: remote.provider, model: result.model, megapixels: mp, bytes: finalMeta.bytes });
      await saveWorkflowState(this.env, job.reference_id, blocked ? "blocked" : "ready", blocked ? "QUALITY_GATE" : "READY_REVIEW", 100, blocked ? "Asset blocked by a production quality gate." : "Asset ready for human review.");
      return result;
    });
  }
}

function resultModel(provider) {
  return provider === "hf-zerogpu" ? "Real-ESRGAN_x4plus" : "cloudflare-free-fallback-resizer";
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname !== "/start") return new Response("Not Found", { status: 404 });
    if (!env.STOCKFORGE_PIPELINE) return Response.json({ detail: "STOCKFORGE_PIPELINE binding is missing" }, { status: 500 });
    const payload = await request.json();
    const instance = await env.STOCKFORGE_PIPELINE.create({ params: payload });
    return Response.json({ workflow_instance_id: await instance.id });
  },
};
