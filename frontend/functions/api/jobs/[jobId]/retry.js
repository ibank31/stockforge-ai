function now() { return new Date().toISOString(); }
function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
function parseResult(job) { try { return job.result_json ? JSON.parse(job.result_json) : {}; } catch (_) { return {}; } }

async function recordEvent(env, jobId, type, stage, status, message, details = null) {
  await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`)
    .bind(jobId, type, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, now()).run();
}

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.STOCKFORGE_WORKFLOW) return json({ detail: "Pages control-plane bindings are missing" }, 500);
    const jobId = String(params.jobId || "");
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (job.status !== "failed" || Number(job.retryable) !== 1) return json({ detail: "Job is not retryable", status: job.status, retryable: Boolean(job.retryable), failure_code: job.failure_code }, 409);

    const mode = job.failed_mode === "upscale" ? "upscale" : (job.failed_mode === "generate" ? "generate" : null);
    if (!mode) return json({ detail: "Failed job has no recoverable pipeline mode" }, 409);
    if (mode === "upscale" && !job.raw_r2_key) return json({ detail: "Upscale retry requires the raw artifact" }, 409);

    const t = now();
    const stage = mode === "upscale" ? "RETRYING_UPSCALE" : "RETRYING_GENERATION";
    const changes = mode === "generate"
      ? await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,event_id=NULL,raw_r2_key=NULL,final_r2_key=NULL,artifact_sha256=NULL,result_json=NULL,error=NULL,retryable=0,failure_code=NULL,failed_mode=?,generation_attempts=generation_attempts+1,last_workflow_id=NULL,last_workflow_created_at=NULL,updated_at=? WHERE id=? AND status='failed' AND retryable=1 AND failed_mode='generate'`).bind("retrying", stage, "generate", t, jobId).run()
      : await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,final_r2_key=NULL,artifact_sha256=NULL,result_json=?,error=NULL,retryable=0,failure_code=NULL,failed_mode=?,upscale_attempts=upscale_attempts+1,last_workflow_id=NULL,last_workflow_created_at=NULL,updated_at=? WHERE id=? AND status='failed' AND retryable=1 AND failed_mode='upscale'`).bind("retrying", stage, JSON.stringify({ provider: "hf-zerogpu", raw_r2_key: job.raw_r2_key, raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`, retry: true }), "upscale", t, jobId).run();
    if (Number(changes.meta?.changes || 0) !== 1) {
      const current = await env.DB.prepare(`SELECT status,retryable FROM jobs_sf WHERE id=?`).bind(jobId).first();
      return json({ detail: "Retry claim was lost", current }, 409);
    }

    await recordEvent(env, jobId, "retry_claim", stage, "retrying", `Retry claim acquired for ${mode}.`, { mode });
    const workflowResponse = await env.STOCKFORGE_WORKFLOW.fetch(new Request("https://stockforge-pipeline/start", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ job_id: jobId, mode }),
    }));
    if (!workflowResponse.ok) {
      const detail = await workflowResponse.text();
      await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,failure_code=?,failed_mode=?,retryable=?,updated_at=? WHERE id=? AND status='retrying'`).bind("failed", mode === "upscale" ? "FAILED_UPSCALE_RETRY_DISPATCH" : "FAILED_GENERATION_RETRY_DISPATCH", detail.slice(0, 2000), "DISPATCH_ERROR", mode, 1, now(), jobId).run();
      await recordEvent(env, jobId, "retry_dispatch_failed", mode === "upscale" ? "FAILED_UPSCALE_RETRY_DISPATCH" : "FAILED_GENERATION_RETRY_DISPATCH", "failed", "Retry workflow could not be started.", { detail: detail.slice(0, 2000) });
      return json({ detail: "Unable to start retry pipeline", error: detail, retryable: true }, 502);
    }

    const workflow = await workflowResponse.json();
    const instanceId = String(workflow.workflow_instance_id || "");
    if (!instanceId) throw new Error("Retry pipeline returned no workflow_instance_id");
    const current = await env.DB.prepare(`SELECT result_json,asset_token,raw_r2_key FROM jobs_sf WHERE id=?`).bind(jobId).first();
    const previous = parseResult(current || job);
    const result = mode === "upscale"
      ? { ...previous, finalization: { mode: "upscale", workflow_instance_id: instanceId, status: "queued" } }
      : { provider: "hf-zerogpu", workflow_instance_id: instanceId, asset_token: job.asset_token };
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,result_json=?,last_workflow_id=?,last_workflow_created_at=?,updated_at=? WHERE id=? AND status='retrying'`)
      .bind(mode === "upscale" ? "upscale_submitted" : "submitted", mode === "upscale" ? "UPSCALING" : "SUBMITTED", JSON.stringify(result), instanceId, now(), jobId).run();
    await recordEvent(env, jobId, "retry_workflow_created", mode === "upscale" ? "UPSCALING" : "SUBMITTED", mode === "upscale" ? "upscale_submitted" : "submitted", `Retry workflow created for ${mode}.`, { workflow_instance_id: instanceId });
    return json({ job_id: jobId, status: mode === "upscale" ? "upscale_submitted" : "submitted", mode, pipeline_instance_id: instanceId, retry: true });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
