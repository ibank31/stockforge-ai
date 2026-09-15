function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}

export async function onRequestGet(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    let result = null;
    try { result = job.result_json ? JSON.parse(job.result_json) : null; } catch (_) { result = { raw_result_json: job.result_json }; }
    const events = await env.DB.prepare(`SELECT id,event_type,stage,status,message,created_at FROM job_events_sf WHERE job_id=? ORDER BY id DESC LIMIT 25`).bind(job.id).all();
    return json({
      id: job.id,
      reference_id: job.reference_id,
      type: job.type,
      status: job.status,
      stage: job.stage,
      retryable: Boolean(job.retryable),
      failure_code: job.failure_code,
      failed_mode: job.failed_mode,
      attempts: { generation: Number(job.generation_attempts || 0), upscale: Number(job.upscale_attempts || 0) },
      last_workflow_id: job.last_workflow_id,
      last_workflow_created_at: job.last_workflow_created_at,
      result,
      error: job.error,
      events: (events.results || []).reverse(),
      created_at: job.created_at,
      updated_at: job.updated_at,
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
