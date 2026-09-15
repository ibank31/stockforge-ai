function now() { return new Date().toISOString(); }
function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.STOCKFORGE_WORKFLOW) return json({ detail: "Pages control-plane bindings are missing" }, 500);

    const jobId = String(params.jobId || "");
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (!job.raw_r2_key) return json({ detail: "Raw generated asset is not ready" }, 409);
    if (["queued", "submitted", "upscale_submitted", "upscaling"].includes(job.status)) {
      return json({ detail: "A generation/finalization workflow is already running", status: job.status }, 409);
    }
    if (job.status === "succeeded" || job.status === "approved") {
      return json({ detail: "Final master already exists for this job", status: job.status }, 409);
    }
    if (job.status !== "ready_upscale") return json({ detail: `Job is not ready for finalization: ${job.status}` }, 409);

    const t = now();
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,updated_at=? WHERE id=?`)
      .bind("upscale_submitted", "UPSCALING", null, t, jobId)
      .run();
    await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
      .bind("running", "UPSCALING", 70, "4x finalization accepted; GPU work is running separately from generation.", t, job.reference_id)
      .run();

    const workflowResponse = await env.STOCKFORGE_WORKFLOW.fetch(new Request("https://stockforge-pipeline/start", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ job_id: jobId, mode: "upscale" }),
    }));
    if (!workflowResponse.ok) {
      const detail = await workflowResponse.text();
      await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,updated_at=? WHERE id=?`)
        .bind("ready_upscale", "READY_UPSCALE", detail.slice(0, 2000), now(), jobId)
        .run();
      await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
        .bind("ready", "READY_UPSCALE", 55, "Upscale start was rejected. The raw asset remains available for retry.", now(), job.reference_id)
        .run();
      return json({ detail: "Unable to start finalization pipeline", error: detail }, 502);
    }

    const workflow = await workflowResponse.json();
    const existing = job.result_json ? JSON.parse(job.result_json) : {};
    await env.DB.prepare(`UPDATE jobs_sf SET result_json=?,updated_at=? WHERE id=?`)
      .bind(JSON.stringify({
        ...existing,
        provider: "hf-zerogpu",
        raw_r2_key: job.raw_r2_key,
        raw_asset_url: `/api/assets/${jobId}?kind=raw&token=${job.asset_token}`,
        finalization: { mode: "upscale", workflow_instance_id: workflow.workflow_instance_id, status: "queued" },
      }), now(), jobId)
      .run();

    const wf = await env.DB.prepare(`SELECT id FROM workflows_sf WHERE reference_id=?`).bind(job.reference_id).first();
    return json({
      workflow_id: wf?.id || null,
      job_id: jobId,
      status: "upscale_submitted",
      provider: "hf-zerogpu",
      pipeline_instance_id: workflow.workflow_instance_id,
      mode: "upscale",
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
