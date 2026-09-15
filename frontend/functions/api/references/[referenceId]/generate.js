function now() { return new Date().toISOString(); }
function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
function id(prefix) { return `${prefix}_${crypto.randomUUID().replaceAll("-", "")}`; }
function token() { return crypto.randomUUID().replaceAll("-", ""); }

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.STOCKFORGE_WORKFLOW) return json({ detail: "Pages control-plane bindings are missing" }, 500);
    const referenceId = String(params.referenceId || "");
    const reference = await env.DB.prepare(`SELECT * FROM references_sf WHERE id=?`).bind(referenceId).first();
    if (!reference) return json({ detail: "Reference not found" }, 404);
    const planRow = await env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(referenceId).first();
    if (!planRow) return json({ detail: "Create a creative plan before generation" }, 409);

    const jobId = id("job");
    const assetToken = token();
    const plan = JSON.parse(planRow.plan_json);
    const t = now();
    await env.DB.prepare(`INSERT INTO jobs_sf (id,reference_id,type,status,stage,prompt,width,height,steps,seed,randomize_seed,event_id,asset_token,result_json,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)`)
      .bind(jobId, referenceId, "generation", "queued", "QUEUED", plan.generation_prompt, plan.generation.width, plan.generation.height, plan.generation.steps, plan.generation.seed || 0, plan.generation.randomize_seed ? 1 : 0, null, assetToken, JSON.stringify({ provider: "hf-zerogpu", workflow: "cloudflare-workflow" }), t, t)
      .run();
    await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
      .bind("running", "QUEUED", 5, "Durable StockForge pipeline accepted the generation job.", t, referenceId)
      .run();

    const workflowResponse = await env.STOCKFORGE_WORKFLOW.fetch(new Request("https://stockforge-pipeline/start", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ job_id: jobId }),
    }));
    if (!workflowResponse.ok) {
      const detail = await workflowResponse.text();
      await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,updated_at=? WHERE id=?`)
        .bind("failed", "FAILED", detail.slice(0, 2000), now(), jobId)
        .run();
      return json({ detail: "Unable to start durable pipeline", error: detail }, 502);
    }
    const workflow = await workflowResponse.json();
    await env.DB.prepare(`UPDATE jobs_sf SET result_json=?,updated_at=? WHERE id=?`)
      .bind(JSON.stringify({ provider: "hf-zerogpu", workflow_instance_id: workflow.workflow_instance_id, asset_token: assetToken }), now(), jobId)
      .run();
    return json({ workflow_id: (await env.DB.prepare(`SELECT id FROM workflows_sf WHERE reference_id=?`).bind(referenceId).first()).id, job_id: jobId, status: "queued", provider: "hf-zerogpu", pipeline_instance_id: workflow.workflow_instance_id });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
