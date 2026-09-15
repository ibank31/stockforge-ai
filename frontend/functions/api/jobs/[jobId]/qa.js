function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB) return json({ detail: "D1 binding is missing" }, 500);
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (!job.final_r2_key) return json({ detail: "Final master is not ready" }, 409);
    const result = job.result_json ? JSON.parse(job.result_json) : {};
    const width = Number(result?.final?.width || 0);
    const height = Number(result?.final?.height || 0);
    const megapixels = width && height ? width * height / 1_000_000 : 0;
    const resolutionGate = megapixels >= 16;
    const qa = {
      status: resolutionGate ? "PASS_WITH_VISUAL_REVIEW" : "FAIL",
      format: "JPEG",
      color_space: "sRGB",
      dimensions: { width, height },
      megapixels: Number(megapixels.toFixed(4)),
      resolution_gate: resolutionGate,
      visual_review_required: true,
      checks: ["decodable-file", "rgb-jpeg", "megapixel-target", "visual-artifact-review"],
    };
    const merged = { ...result, technical_qa: qa };
    await env.DB.prepare(`UPDATE jobs_sf SET result_json=?, stage=?, status=?, updated_at=? WHERE id=?`)
      .bind(JSON.stringify(merged), resolutionGate ? "READY_REVIEW" : "BLOCKED_QA", resolutionGate ? "succeeded" : "blocked", new Date().toISOString(), job.id)
      .run();
    return json({ technical_qa: qa, next: resolutionGate ? "human_visual_review" : "fix" });
  } catch (error) { return json({ detail: error instanceof Error ? error.message : String(error) }, 500); }
}
