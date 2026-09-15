function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }

export async function onRequestGet(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    const jobId = String(params.jobId || "");
    const job = await env.DB.prepare(`SELECT id,status,stage,reference_id FROM jobs_sf WHERE id=?`).bind(jobId).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    const rows = await env.DB.prepare(`SELECT id,event_type,stage,status,message,details_json,created_at FROM job_events_sf WHERE job_id=? ORDER BY id ASC`).bind(jobId).all();
    return json({
      job_id: job.id,
      status: job.status,
      stage: job.stage,
      events: (rows.results || []).map((row) => ({
        id: row.id,
        event_type: row.event_type,
        stage: row.stage,
        status: row.status,
        message: row.message,
        details: row.details_json ? JSON.parse(row.details_json) : null,
        created_at: row.created_at,
      })),
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
