import { getKaggleStatus, downloadKaggleOutput } from "../../../../lib/kaggle-upscale.js";

function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
async function sha256Hex(arrayBuffer) { const digest = await crypto.subtle.digest("SHA-256", arrayBuffer); return [...new Uint8Array(digest)].map(v => v.toString(16).padStart(2, "0")).join(""); }
async function recordEvent(env, jobId, type, stage, status, message, details = null) { await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`).bind(jobId, type, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, new Date().toISOString()).run(); }
async function reconcileKaggle(env, job) {
  if (!env.KAGGLE_API_TOKEN || !job.result_json) return;
  let result = {};
  try { result = JSON.parse(job.result_json); } catch (_) { return; }
  const providerJobId = String(result.kaggle_provider_job_id || "");
  if (!providerJobId || !["upscale_submitted", "upscaling"].includes(job.status)) return;
  const remote = await getKaggleStatus(env, providerJobId);
  const state = String(remote.status || remote.state || remote.result?.status || "").toLowerCase();
  if (/(error|failed|cancel)/.test(state)) {
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,failure_code=?,retryable=?,updated_at=? WHERE id=?`).bind("failed", "FAILED_UPSCALE", JSON.stringify(remote).slice(0, 2000), "KAGGLE_UPSCALE_FAILED", 1, new Date().toISOString(), job.id).run();
    await recordEvent(env, job.id, "upscale_failed", "FAILED_UPSCALE", "failed", "Kaggle upscale failed.", { provider_job_id: providerJobId, kaggle_status: state });
    return;
  }
  if (!/(complete|completed|success|succeeded)/.test(state)) return;
  const resultResponse = await downloadKaggleOutput(env, providerJobId, "result.json");
  if (!resultResponse.ok) return;
  const remoteResult = await resultResponse.json();
  const artifactResponse = await downloadKaggleOutput(env, providerJobId, "master.jpg");
  if (!artifactResponse.ok) return;
  const body = await artifactResponse.arrayBuffer();
  if (body.byteLength < 10000) throw new Error("Kaggle final artifact is unexpectedly small");
  const finalKey = `artifacts/${job.id}/final.jpg`;
  const hash = await sha256Hex(body);
  await env.ASSET_STORE.put(finalKey, body, { httpMetadata: { contentType: "image/jpeg" } });
  const final = remoteResult.master || {};
  const width = Number(final.width || 0);
  const height = Number(final.height || 0);
  const megapixels = Number(final.megapixels || (width && height ? width * height / 1000000 : 0));
  const duplicate = await env.DB.prepare(`SELECT id FROM jobs_sf WHERE artifact_sha256=? AND id<>? AND status IN ('succeeded','approved') LIMIT 1`).bind(hash, job.id).first();
  const finalResult = { provider: "kaggle-realesrgan", model: String(remoteResult.model_id || "RealESRGAN_x4plus"), raw_r2_key: job.raw_r2_key, final: { provider: "kaggle-realesrgan", model: String(remoteResult.model_id || "RealESRGAN_x4plus"), scale: 4, width, height, megapixels: Number(megapixels.toFixed(4)), size_bytes: body.byteLength, sha256: hash, final_r2_key: finalKey, final_asset_url: `/api/assets/${job.id}?kind=final&token=${job.asset_token}` }, similarity_gate: { automated_duplicate: duplicate ? "BLOCK" : "PASS", duplicate_of_job: duplicate?.id || null, semantic_reference_similarity: "HUMAN_REVIEW_REQUIRED", decision: duplicate ? "BLOCK" : "REVIEW_REQUIRED", human_review_required: true }, technical_qa: { status: megapixels >= 16 ? "PASS_WITH_VISUAL_REVIEW" : "FAIL", format: "JPEG", color_space: "sRGB", dimensions: { width, height, megapixels: Number(megapixels.toFixed(4)) } }, finalization: { mode: "ai_upscale", provider: "kaggle-realesrgan", algorithm: "Real-ESRGAN x4", source_dimensions: { width: Number(job.width || 0), height: Number(job.height || 0) }, output_dimensions: { width, height }, kaggle_version_number: result.kaggle_version_number || null } };
  const nextStatus = duplicate ? "blocked" : "succeeded";
  await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,final_r2_key=?,artifact_sha256=?,result_json=?,error=NULL,retryable=0,failed_mode=NULL,failure_code=NULL,updated_at=? WHERE id=?`).bind(nextStatus, duplicate ? "BLOCKED_DUPLICATE" : "SUCCEEDED", finalKey, hash, JSON.stringify(finalResult), new Date().toISOString(), job.id).run();
  await recordEvent(env, job.id, "finalization_complete", duplicate ? "BLOCKED_DUPLICATE" : "SUCCEEDED", nextStatus, duplicate ? "Kaggle final master blocked by duplicate gate." : "Kaggle 4× final master created; human review remains required.", { provider: "kaggle-realesrgan", provider_job_id: providerJobId, width, height, megapixels });
  await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`).bind(duplicate ? "blocked" : "succeeded", duplicate ? "BLOCKED_DUPLICATE" : "SUCCEEDED", 100, duplicate ? "Final master blocked by duplicate gate." : "Final master ready for human review.", new Date().toISOString(), job.reference_id).run();
}
export async function onRequestGet(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    let job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (["upscale_submitted", "upscaling"].includes(job.status)) { try { await reconcileKaggle(env, job); } catch (_) {} job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first(); }
    let result = null;
    try { result = job.result_json ? JSON.parse(job.result_json) : null; } catch (_) { result = { raw_result_json: job.result_json }; }
    const events = await env.DB.prepare(`SELECT id,event_type,stage,status,message,created_at FROM job_events_sf WHERE job_id=? ORDER BY id DESC LIMIT 25`).bind(job.id).all();
    return json({ id: job.id, reference_id: job.reference_id, type: job.type, status: job.status, stage: job.stage, retryable: Boolean(job.retryable), failure_code: job.failure_code, failed_mode: job.failed_mode, attempts: { generation: Number(job.generation_attempts || 0), upscale: Number(job.upscale_attempts || 0) }, last_workflow_id: job.last_workflow_id, last_workflow_created_at: job.last_workflow_created_at, result, error: job.error, events: (events.results || []).reverse(), created_at: job.created_at, updated_at: job.updated_at });
  } catch (error) { return json({ detail: error instanceof Error ? error.message : String(error) }, 500); }
}
