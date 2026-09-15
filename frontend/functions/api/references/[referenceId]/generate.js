function now() { return new Date().toISOString(); }
function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }
function id(prefix) { return `${prefix}_${crypto.randomUUID().replaceAll("-", "")}`; }
function token() { return crypto.randomUUID().replaceAll("-", ""); }

function parseResult(job) {
  try { return job.result_json ? JSON.parse(job.result_json) : {}; }
  catch (_) { return {}; }
}

async function recordEvent(env, jobId, type, stage, status, message, details = null) {
  await env.DB.prepare(`INSERT INTO job_events_sf(job_id,event_type,stage,status,message,details_json,created_at) VALUES(?,?,?,?,?,?,?)`)
    .bind(jobId, type, stage || null, status || null, message || null, details ? JSON.stringify(details) : null, now()).run();
}

async function reuseJob(env, referenceId, job) {
  const parsed = parseResult(job);
  const workflowRow = await env.DB.prepare(`SELECT id FROM workflows_sf WHERE reference_id=?`).bind(referenceId).first();
  return json({
    workflow_id: workflowRow?.id || null,
    job_id: job.id,
    status: job.status,
    provider: "hf-zerogpu",
    pipeline_instance_id: parsed.workflow_instance_id || parsed.finalization?.workflow_instance_id || null,
    idempotent_reuse: true,
  });
}

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.STOCKFORGE_WORKFLOW) return json({ detail: "Pages control-plane bindings are missing" }, 500);
    const referenceId = String(params.referenceId || "");
    const reference = await env.DB.prepare(`SELECT * FROM references_sf WHERE id=?`).bind(referenceId).first();
    if (!reference) return json({ detail: "Reference not found" }, 404);
    const planRow = await env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(referenceId).first();
    if (!planRow) return json({ detail: "Create a creative plan before generation" }, 409);
    const plan = JSON.parse(planRow.plan_json);

    const failed = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE reference_id=? AND type='generation' AND status='failed' ORDER BY created_at DESC LIMIT 1`).bind(referenceId).first();
    if (failed && Number(failed.retryable) === 1) {
      return json({ detail: "A retryable generation failure already exists. Use the retry endpoint instead of creating another GPU job.", job_id: failed.id, retryable: true, failure_code: failed.failure_code, retry_endpoint: `/api/jobs/${failed.id}/retry` }, 409);
    }

    const reusable = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE reference_id=? AND type='generation' AND status IN ('queued','dispatching','submitted','generating','ready_upscale','upscale_submitted','succeeded','approved') ORDER BY created_at DESC LIMIT 1`)
      .bind(referenceId).first();
    if (reusable) return reuseJob(env, referenceId, reusable);

    const jobId = id("job");
    const assetToken = token();
    const t = now();
    await env.DB.prepare(`INSERT INTO jobs_sf (id,reference_id,type,status,stage,prompt,width,height,steps,seed,randomize_seed,event_id,asset_token,result_json,created_at,updated_at,generation_attempts,upscale_attempts,failed_mode,failure_code,retryable,last_workflow_id,last_workflow_created_at) SELECT ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,? WHERE NOT EXISTS (SELECT 1 FROM jobs_sf WHERE reference_id=? AND type='generation' AND status IN ('queued','dispatching','submitted','generating','ready_upscale','upscale_submitted','succeeded','approved'))`)
      .bind(jobId, referenceId, "generation", "queued", "QUEUED", plan.generation_prompt, plan.generation.width, plan.generation.height, plan.generation.steps, plan.generation.seed || 0, plan.generation.randomize_seed ? 1 : 0, null, assetToken, JSON.stringify({ provider: "hf-zerogpu", workflow: "cloudflare-workflow" }), t, t, 0, 0, null, null, 0, null, null, referenceId)
      .run();

    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE reference_id=? AND type='generation' AND status IN ('queued','dispatching','submitted','generating','ready_upscale','upscale_submitted','succeeded','approved') ORDER BY created_at DESC LIMIT 1`)
      .bind(referenceId).first();
    if (!job) return json({ detail: "Generation job could not be created" }, 500);
    if (job.id !== jobId) return reuseJob(env, referenceId, job);

    const claim = await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,generation_attempts=generation_attempts+1,error=NULL,retryable=0,failed_mode=NULL,failure_code=NULL,updated_at=? WHERE id=? AND status='queued'`)
      .bind("dispatching", "DISPATCHING", t, jobId).run();
    const claimed = Number(claim.meta?.changes || 0) > 0;
    if (!claimed) {
      const current = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(jobId).first();
      return current ? reuseJob(env, referenceId, current) : json({ detail: "Generation dispatch claim was lost" }, 409);
    }
    await recordEvent(env, jobId, "dispatch_claim", "DISPATCHING", "dispatching", "Generation dispatch claim acquired.");

    await env.DB.prepare(`UPDATE workflows_sf SET status=?,stage=?,progress=?,message=?,updated_at=? WHERE reference_id=?`)
      .bind("running", "QUEUED", 5, "Durable StockForge pipeline accepted the generation job.", t, referenceId).run();

    const workflowResponse = await env.STOCKFORGE_WORKFLOW.fetch(new Request("https://stockforge-pipeline/start", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ job_id: jobId, mode: "generate" }),
    }));
    if (!workflowResponse.ok) {
      const detail = await workflowResponse.text();
      await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,error=?,failure_code=?,failed_mode=?,retryable=?,updated_at=? WHERE id=? AND status='dispatching'`)
        .bind("failed", "FAILED_DISPATCH", detail.slice(0, 2000), "DISPATCH_ERROR", "generate", 1, now(), jobId).run();
      await recordEvent(env, jobId, "dispatch_failed", "FAILED_DISPATCH", "failed", "Unable to start durable generation workflow.", { detail: detail.slice(0, 2000) });
      return json({ detail: "Unable to start durable pipeline", error: detail, retryable: true, job_id: jobId }, 502);
    }

    const workflow = await workflowResponse.json();
    const instanceId = String(workflow.workflow_instance_id || "");
    if (!instanceId) throw new Error("Durable generation workflow returned no workflow_instance_id");
    await env.DB.prepare(`UPDATE jobs_sf SET status=?,stage=?,result_json=?,last_workflow_id=?,last_workflow_created_at=?,updated_at=? WHERE id=? AND status='dispatching'`)
      .bind("submitted", "SUBMITTED", JSON.stringify({ provider: "hf-zerogpu", workflow_instance_id: instanceId, asset_token: assetToken }), instanceId, now(), now(), jobId).run();
    await recordEvent(env, jobId, "workflow_created", "SUBMITTED", "submitted", "Cloudflare durable generation workflow created.", { workflow_instance_id: instanceId });

    const workflowRow = await env.DB.prepare(`SELECT id FROM workflows_sf WHERE reference_id=?`).bind(referenceId).first();
    return json({ workflow_id: workflowRow?.id || null, job_id: jobId, status: "submitted", provider: "hf-zerogpu", pipeline_instance_id: instanceId });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
