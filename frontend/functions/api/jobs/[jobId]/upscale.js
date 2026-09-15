function now() { return new Date().toISOString(); }
function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
function parseResult(job) { try { return job.result_json ? JSON.parse(job.result_json) : {}; } catch (_) { return {}; } }
async function recordEvent(env, jobId, type, stage, status, message, details = null) { await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`).bind(jobId, type, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, now()).run(); }
const PIPELINE_URL = "https://stockforge-pipeline.iqbalteguh01.workers.dev";
export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "Pages control-plane D1 binding is missing" }, 500);
    const jobId = String(params.jobId || "");
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (!job.raw_r2_key) return json({ detail: "Raw generated asset is not ready" }, 409);
    if (job.status === "upscale_submitted") return json({ job_id: jobId, status: job.status, idempotent_reuse: true, pipeline_instance_id: parseResult(job).finalization?.workflow_instance_id || null });
    if (job.status === "upscaling") return json({ job_id: jobId, status: job.status, idempotent_reuse: true, pipeline_instance_id: parseResult(job).finalization?.workflow_instance_id || null });
    if (job.status === "succeeded" || job.status === "approved") return json({ detail: "Final master already exists for this job", status: job.status }, 409);
    if (job.status !== "ready_upscale") return json({ detail: `Job is not ready for finalization: ${job.status}` }, 409);
    const t = now();
    const claim = await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=NULL,retryable=0,failed_mode=NULL,failure_code=NULL,upscale_attempts=upscale_attempts+1,updated_at=? WHERE id=? AND status='ready_upscale'`).bind("upscale_submitted", "UPSCALING", t, jobId).run();
    const claimed = Number(claim.meta?.changes || 0) > 0;
    if (!claimed) {
      const current = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
      if (!current) return json({ detail: "Job disappeared during finalization claim" }, 409);
      return json({ job_id: jobId, status: current.status, idempotent_reuse: true, pipeline_instance_id: parseResult(current).finalization?.workflow_instance_id || null });
    }
    await recordEvent(env, jobId, "upscale_claim", "UPSCALING", "upscale_submitted", "Finalization claim acquired.");
    const payload = JSON.stringify({ job_id: jobId, mode: "upscale" });
    let workflowResponse;
    try {
      workflowResponse = await fetch(`${PIPELINE_URL}/start`, { method: "POST", headers: { "content-type": "application/json" }, body: payload });
    } catch (dispatchError) {
      const detail = dispatchError instanceof Error ? dispatchError.message : String(dispatchError);
      await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,failure_code=?,failed_mode=?,retryable=?,updated_at=? WHERE id=? AND status='upscale_submitted'`).bind("failed", "FAILED_DISPATCH", detail.slice(0, 2000), "DISPATCH_NETWORK", "upscale", 1, now(), jobId).run();
      await recordEvent(env, jobId, "upscale_dispatch_network_failed", "FAILED_DISPATCH", "failed", detail, { pipeline_url: PIPELINE_URL });
      return json({ detail: "Unable to reach finalization pipeline", error: detail, pipeline_url: PIPELINE_URL, retryable: true }, 502);
    }
    if (!workflowResponse.ok) {
      const detail = await workflowResponse.text();
      await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,failure_code=?,failed_mode=?,retryable=?,updated_at=? WHERE id=? AND status='upscale_submitted'`).bind("failed", "FAILED_DISPATCH", detail.slice(0, 2000), "DISPATCH_ERROR", "upscale", 1, now(), jobId).run();
      await recordEvent(env, jobId, "upscale_dispatch_failed", "FAILED_DISPATCH", "failed", "Unable to start finalization workflow.", { detail: detail.slice(0, 2000) });
      return json({ detail: "Unable to start finalization pipeline", error: detail, retryable: true }, 502);
    }
    const workflow = await workflowResponse.json();
    const instanceId = String(workflow.workflow_instance_id || "");
    if (!instanceId) throw new Error("Durable upscale workflow returned no workflow_instance_id");
    const existing = parseResult(job);
    const result = { ...existing, provider: "hf-zerogpu", raw_r2_key: job.raw_r2_key, raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`, finalization: { mode: "upscale", workflow_instance_id: instanceId, status: "queued" } };
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,result_json=?,last_workflow_id=?,last_workflow_created_at=?,updated_at=? WHERE id=? AND status='upscale_submitted'`).bind("upscale_submitted", "UPSCALING", JSON.stringify(result), instanceId, now(), jobId).run();
    await recordEvent(env, jobId, "workflow_created", "UPSCALING", "upscale_submitted", "Cloudflare durable upscale workflow created.", { workflow_instance_id: instanceId });
    const wf = await env.DB.prepare(`SELECT id FROM workflows_sf WHERE reference_id=?`).bind(job.reference_id).first();
    return json({ workflow_id: wf?.id || null, job_id: jobId, status: "upscale_submitted", provider: "hf-zerogpu", pipeline_instance_id: instanceId, mode: "upscale" });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
