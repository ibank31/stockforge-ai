function now() { return new Date().toISOString(); }
function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
async function sha256Hex(arrayBuffer) { const digest = await crypto.subtle.digest("SHA-256", arrayBuffer); return [...new Uint8Array(digest)].map((v) => v.toString(16).padStart(2, "0")).join(""); }
async function recordEvent(env, jobId, type, stage, status, message, details = null) { await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`).bind(jobId, type, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, now()).run(); }

async function finalizeWithFreeResizer(env, job) {
  const width = Number(job.width || 1024);
  const height = Number(job.height || 1024);
  if (!Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1) throw new Error("Invalid source dimensions");
  const targetWidth = width * 4;
  const targetHeight = height * 4;
  const sourceUrl = `${env.PUBLIC_BASE_URL.replace(/\/$/, "")}/api/assets/${job.id}?kind=raw&token=${job.asset_token}`;
  const transformUrl = `https://wsrv.nl/?url=${encodeURIComponent(sourceUrl)}&w=${targetWidth}&h=${targetHeight}&fit=inside&output=jpg&q=95&sharp=3&il`;
  const response = await fetch(transformUrl, { headers: { "user-agent": "StockForge/1.0 finalizer" } });
  if (!response.ok) throw new Error(`Free resizer failed: HTTP ${response.status}`);
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("image/")) throw new Error(`Free resizer returned non-image content: ${contentType}`);
  const body = await response.arrayBuffer();
  if (body.byteLength < 10000) throw new Error("Free resizer returned an unexpectedly small artifact");

  const finalKey = `artifacts/${job.id}/final.jpg`;
  const hash = await sha256Hex(body);
  await env.ASSET_STORE.put(finalKey, body, { httpMetadata: { contentType: "image/jpeg" } });
  const duplicate = await env.DB.prepare(`SELECT id FROM jobs_sf WHERE artifact_sha256=? AND id<>? AND status IN ('succeeded','approved') LIMIT 1`).bind(hash, job.id).first();
  const megapixels = (targetWidth * targetHeight) / 1000000;
  const result = {
    provider: "free-resizer-fallback",
    model: "wsrv-lanczos-sharpen",
    raw_r2_key: job.raw_r2_key,
    raw_asset_url: `/api/assets/${job.id}?kind=raw&token=${job.asset_token}`,
    final: {
      provider: "free-resizer-fallback",
      model: "wsrv-lanczos-sharpen",
      scale: 4,
      width: targetWidth,
      height: targetHeight,
      megapixels: Number(megapixels.toFixed(4)),
      size_bytes: body.byteLength,
      sha256: hash,
      final_r2_key: finalKey,
      final_asset_url: `/api/assets/${job.id}?kind=final&token=${job.asset_token}`,
    },
    similarity_gate: {
      automated_duplicate: duplicate ? "BLOCK" : "PASS",
      duplicate_of_job: duplicate?.id || null,
      semantic_reference_similarity: "HUMAN_REVIEW_REQUIRED",
      decision: duplicate ? "BLOCK" : "REVIEW_REQUIRED",
      human_review_required: true,
    },
    technical_qa: {
      status: megapixels >= 16 ? "PASS_WITH_VISUAL_REVIEW" : "FAIL",
      format: "JPEG",
      color_space: "sRGB",
      dimensions: { width: targetWidth, height: targetHeight, megapixels: Number(megapixels.toFixed(4)) },
    },
    finalization: {
      mode: "upscale",
      provider: "free-resizer-fallback",
      algorithm: "remote high-quality resize + sharpen",
      source_dimensions: { width, height },
      output_dimensions: { width: targetWidth, height: targetHeight },
    },
  };

  await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,final_r2_key=?,artifact_sha256=?,result_json=?,error=NULL,retryable=0,failed_mode=NULL,failure_code=NULL,updated_at=? WHERE id=?`).bind(duplicate ? "blocked" : "succeeded", duplicate ? "BLOCKED_DUPLICATE" : "SUCCEEDED", finalKey, hash, JSON.stringify(result), now(), job.id).run();
  await recordEvent(env, job.id, "finalization_complete", duplicate ? "BLOCKED_DUPLICATE" : "SUCCEEDED", duplicate ? "blocked" : "succeeded", duplicate ? "Final master blocked by duplicate gate." : "Final master created and passed technical resolution gate.", { provider: "free-resizer-fallback", width: targetWidth, height: targetHeight, megapixels: Number(megapixels.toFixed(4)), sha256: hash });
  await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`).bind(duplicate ? "blocked" : "succeeded", duplicate ? "BLOCKED_DUPLICATE" : "SUCCEEDED", 100, duplicate ? "Final master blocked by duplicate gate." : "Final master ready for human review.", now(), job.reference_id).run();
  return result;
}

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.ASSET_STORE) return json({ detail: "Pages control-plane bindings are missing" }, 500);
    const jobId = String(params.jobId || "");
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (!job.raw_r2_key) return json({ detail: "Raw generated asset is not ready" }, 409);
    if (job.status === "succeeded" || job.status === "approved") return json({ detail: "Final master already exists for this job", status: job.status }, 409);
    if (job.status === "upscale_submitted" || job.status === "upscaling") return json({ job_id: jobId, status: job.status, idempotent_reuse: true });
    if (job.status !== "ready_upscale") return json({ detail: `Job is not ready for finalization: ${job.status}` }, 409);

    const claim = await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=NULL,retryable=0,failed_mode=NULL,failure_code=NULL,upscale_attempts=upscale_attempts+1,updated_at=? WHERE id=? AND status='ready_upscale'`).bind("upscaling", "UPSCALING", now(), jobId).run();
    if (Number(claim.meta?.changes || 0) === 0) {
      const current = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
      return current ? json({ job_id: jobId, status: current.status, idempotent_reuse: true }) : json({ detail: "Job disappeared during finalization claim" }, 409);
    }
    await recordEvent(env, jobId, "upscale_claim", "UPSCALING", "upscaling", "Free finalization claim acquired.", { provider: "free-resizer-fallback" });
    const result = await finalizeWithFreeResizer(env, { ...job, status: "upscaling" });
    return json({ workflow_id: null, job_id: jobId, status: result.similarity_gate.decision === "BLOCK" ? "blocked" : "succeeded", provider: result.provider, mode: "upscale", fallback: true, megapixels: result.final.megapixels });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error), retryable: true }, 502);
  }
}
