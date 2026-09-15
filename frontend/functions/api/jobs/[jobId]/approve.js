function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
function clean(value) { return String(value || "").toLowerCase().trim(); }
function tokens(value) { return new Set(clean(value).split(/[^a-z0-9]+/).filter((v) => v.length >= 3)); }
function overlap(a, b) {
  const A = tokens(a), B = tokens(b);
  if (!A.size || !B.size) return 0;
  let common = 0;
  for (const item of A) if (B.has(item)) common += 1;
  return common / Math.max(A.size, B.size);
}
function referenceSimilarity(plan) {
  const ref = plan?.reference_anchor || {};
  const concept = plan?.concept || {};
  const fields = [
    ["subject", ref.subject, concept.subject],
    ["composition", ref.composition, concept.composition],
    ["viewpoint", ref.viewpoint, concept.viewpoint],
    ["color_direction", ref.color_direction, concept.color],
    ["context", ref.context, concept.context],
  ];
  const values = fields.map(([name, a, b]) => ({ field: name, score: Number(overlap(a, b).toFixed(4)) }));
  const score = values.length ? values.reduce((sum, item) => sum + item.score, 0) / values.length : 0;
  const materialChanges = values.filter((item) => item.score < 0.5).map((item) => item.field);
  const risk = score >= 0.72 && materialChanges.length < 3 ? "HIGH" : (score >= 0.52 ? "MEDIUM" : "LOW");
  return { score: Number(score.toFixed(4)), risk, fields: values, material_change_fields: materialChanges, heuristic: "textual_reference_similarity_v1" };
}

async function recordEvent(env, jobId, type, stage, status, message, details = null) {
  await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`)
    .bind(jobId, type, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, new Date().toISOString()).run();
}

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
    if (result.technical_qa?.status !== "PASS_WITH_VISUAL_REVIEW") return json({ detail: "Technical QA must pass before approval" }, 409);

    const planRow = await env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(job.reference_id).first();
    const plan = JSON.parse(planRow?.plan_json || "{}");
    const semantic = referenceSimilarity(plan);
    result.similarity_gate = {
      ...(result.similarity_gate || {}),
      automated_duplicate: result.similarity_gate?.automated_duplicate || "PASS",
      semantic_reference_similarity: semantic.score,
      semantic_reference_similarity_risk: semantic.risk,
      similarity_details: semantic,
      decision: semantic.risk === "HIGH" ? "BLOCK" : "REVIEW_REQUIRED",
      human_review_required: true,
    };
    if (semantic.risk === "HIGH") {
      await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,result_json=?,error=?,failure_code=?,retryable=?,updated_at=? WHERE id=?`).bind("blocked", "BLOCKED_REFERENCE_SIMILARITY", JSON.stringify(result), "Reference similarity heuristic is too high for automatic approval", "REFERENCE_SIMILARITY", 0, new Date().toISOString(), job.id).run();
      await recordEvent(env, job.id, "reference_similarity_block", "BLOCKED_REFERENCE_SIMILARITY", "blocked", "Approval blocked by high reference similarity heuristic.", semantic);
      return json({ detail: "Reference similarity is too high for automatic approval", similarity_gate: result.similarity_gate }, 422);
    }

    const approvedAt = new Date().toISOString();
    result.human_review = { approved: true, approved_at: approvedAt, reviewer: "human", visual_quality_reviewed: true, rights_and_release_reviewed: true, ai_disclosure_reviewed: true };
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,result_json=?,updated_at=? WHERE id=? AND status IN ('succeeded','approved')`)
      .bind("approved", "APPROVED", JSON.stringify(result), approvedAt, job.id).run();
    await recordEvent(env, job.id, "human_approval", "APPROVED", "approved", "Human review approved the asset for packaging.", { reviewer: "human", rights_and_release_reviewed: true, ai_disclosure_reviewed: true, similarity_risk: semantic.risk, similarity_score: semantic.score });
    await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
      .bind("ready", "APPROVED", 100, "Human review approved the asset for package creation; marketplace upload remains manual.", approvedAt, job.reference_id).run();
    return json({ status: "approved", human_review: result.human_review, similarity_gate: result.similarity_gate, marketplace_submission: "manual_only" });
  } catch (error) { return json({ detail: error instanceof Error ? error.message : String(error) }, 500); }
}
