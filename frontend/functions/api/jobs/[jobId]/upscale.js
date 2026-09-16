function now() { return new Date().toISOString(); }
function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
async function recordEvent(env, jobId, type, stage, status, message, details = null) { await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`).bind(jobId, type, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, now()).run(); }

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.ASSET_STORE) return json({ detail: "Pages control-plane bindings are missing" }, 500);
    if (!env.STOCKFORGE_KAGGLE_BRIDGE_URL) return json({ detail: "Kaggle upscale bridge is not configured" }, 500);
    const jobId = String(params.jobId || "");
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (!job.raw_r2_key) return json({ detail: "Raw generated asset is not ready" }, 409);
    if (job.status === "succeeded" || job.status === "approved") return json({ detail: "Final master already exists for this job", status: job.status }, 409);
    if (job.status === "upscale_submitted" || job.status === "upscaling") {
      let parsed = {};
      try { parsed = job.result_json ? JSON.parse(job.result_json) : {}; } catch (_) {}
      return json({ job_id: jobId, status: job.status, provider: "kaggle-realesrgan", provider_job_id: parsed.kaggle_provider_job_id || null, idempotent_reuse: true });
    }
    if (job.status !== "ready_upscale") return json({ detail: `Job is not ready for finalization: ${job.status}` }, 409);

    const sourceUrl = `${String(env.PUBLIC_BASE_URL || "https://stockforge-ai.pages.dev").replace(/\/$/, "")}/api/assets/${encodeURIComponent(jobId)}?kind=raw&token=${encodeURIComponent(job.asset_token || "")}`;
    const response = await fetch(`${String(env.STOCKFORGE_KAGGLE_BRIDGE_URL).replace(/\/$/, "")}/upscale/submit`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ source_url: sourceUrl, job_id: jobId, scale: 4 }),
    });
    if (!response.ok) throw new Error(`Kaggle bridge submit failed: HTTP ${response.status} ${await response.text()}`);
    const submitted = await response.json();
    const providerJobId = String(submitted.provider_job_id || "");
    if (!providerJobId) throw new Error("Kaggle bridge returned no provider_job_id");

    const t = now();
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,upscale_attempts=upscale_attempts+1,result_json=?,error=NULL,retryable=0,failed_mode=NULL,failure_code=NULL,updated_at=? WHERE id=? AND status='ready_upscale'`)
      .bind("upscale_submitted", "UPSCALING", JSON.stringify({ provider: "kaggle-realesrgan", kaggle_provider_job_id: providerJobId, raw_r2_key: job.raw_r2_key }), t, jobId).run();
    await recordEvent(env, jobId, "upscale_submitted", "UPSCALING", "upscale_submitted", "Kaggle 4× finalization submitted after ZeroGPU generation released.", { provider: "kaggle-realesrgan", provider_job_id: providerJobId });
    await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
      .bind("running", "UPSCALING", 70, "Kaggle 4× finalization is running.", t, job.reference_id).run();
    return json({ workflow_id: null, job_id: jobId, status: "upscale_submitted", provider: "kaggle-realesrgan", provider_job_id: providerJobId });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error), retryable: true }, 502);
  }
}
