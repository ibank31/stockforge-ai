function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}

export async function onRequestGet(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    const workflowId = String(params.workflowId || "");
    if (!workflowId) return json({ detail: "Workflow id is required" }, 400);

    const wf = await env.DB.prepare(`SELECT * FROM workflows_sf WHERE id=?`).bind(workflowId).first();
    if (!wf) return json({ detail: "Workflow not found" }, 404);
    const job = await env.DB.prepare(`SELECT id,type,status,stage,raw_r2_key,final_r2_key,updated_at FROM jobs_sf WHERE reference_id=? ORDER BY created_at DESC LIMIT 1`).bind(wf.reference_id).first();

    return json({
      id: wf.id,
      reference_id: wf.reference_id,
      status: wf.status,
      current_stage: wf.stage,
      progress: wf.progress,
      message: wf.message,
      updated_at: wf.updated_at,
      job: job ? {
        id: job.id,
        type: job.type,
        status: job.status,
        stage: job.stage,
        raw_ready: Boolean(job.raw_r2_key),
        final_ready: Boolean(job.final_r2_key),
        updated_at: job.updated_at,
      } : null,
      stuck: false,
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
