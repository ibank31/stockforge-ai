function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }

const KIND_MAP = {
  manifest: { key: "manifest.json", type: "application/json" },
  csv: { key: "adobe-metadata.csv", type: "text/csv; charset=utf-8" },
  checklist: { key: "review-checklist.md", type: "text/markdown; charset=utf-8" },
  "ai-disclosure": { key: "ai-disclosure.txt", type: "text/plain; charset=utf-8" },
};

export async function onRequestGet(context) {
  try {
    const { env, params, request } = context;
    if (!env.DB || !env.ASSET_STORE) return json({ detail: "D1/R2 bindings are missing" }, 500);
    const jobId = String(params.jobId || "");
    const job = await env.DB.prepare(`SELECT id,asset_token,status FROM jobs_sf WHERE id=?`).bind(jobId).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    const url = new URL(request.url);
    const suppliedToken = url.searchParams.get("token");
    if (job.status !== "approved" && suppliedToken !== job.asset_token) return json({ detail: "Manifest not found" }, 404);
    const kind = url.searchParams.get("kind") || "manifest";
    const selected = KIND_MAP[kind];
    if (!selected) return json({ detail: "Unknown manifest artifact" }, 400);
    const object = await env.ASSET_STORE.get(`artifacts/${jobId}/${selected.key}`);
    if (!object) return json({ detail: "Manifest artifact not found" }, 404);
    return new Response(object.body, { headers: { "content-type": object.httpMetadata?.contentType || selected.type, "cache-control": "private,max-age=3600" } });
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : String(error) }, 500);
  }
}
