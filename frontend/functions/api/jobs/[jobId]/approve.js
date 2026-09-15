function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (!["succeeded", "approved"].includes(job.status)) return json({ detail: "Job is not ready for human approval" }, 409);
    const result = job.result_json ? JSON.parse(job.result_json) : {};
    if (result.similarity_gate?.automated_duplicate === "BLOCK") return json({ detail: "Duplicate gate is blocking this asset" }, 409);
    if (result.technical_qa?.status === "FAIL") return json({ detail: "Technical QA failed" }, 409);
    const approvedAt = new Date().toISOString();
    result.human_review = { approved: true, approved_at: approvedAt, reviewer: "human", visual_quality_reviewed: true, rights_and_release_reviewed: true, ai_disclosure_reviewed: true };
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,result_json=?,updated_at=? WHERE id=?`)
      .bind("approved", "APPROVED", JSON.stringify(result), approvedAt, job.id)
      .run();
    await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
      .bind("ready", "APPROVED", 100, "Human review approved the asset for package creation; marketplace upload remains manual.", approvedAt, job.reference_id)
      .run();
    return json({ status: "approved", human_review: result.human_review, marketplace_submission: "manual_only" });
  } catch (error) { return json({ detail: error instanceof Error ? error.message : String(error) }, 500); }
}
