function json(data, status = 200) {
  return Response.json(data, { status, headers: { "cache-control": "no-store" } });
}

export async function onRequestGet(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    return json({
      id: job.id,
      reference_id: job.reference_id,
      type: job.type,
      status: job.status,
      stage: job.stage,
      result: job.result_json ? JSON.parse(job.result_json) : null,
      error: job.error,
      created_at: job.created_at,
      updated_at: job.updated_at,
    });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
