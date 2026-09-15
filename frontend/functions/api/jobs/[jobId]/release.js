function json(data, status = 200) { return Response.json(data, { status, headers: { "cache-control": "no-store" } }); }

const CATEGORY_MAP = [
  [1, "Animals", /(animal|bird|dog|cat|pet|wildlife|insect)/i],
  [2, "Buildings and architecture", /(building|architecture|interior|office|home|house|temple|factory|urban)/i],
  [3, "Business", /(business|finance|corporate|meeting|office|marketing|money|planning|startup)/i],
  [4, "Drinks", /(coffee|tea|drink|beverage|cocktail|wine|beer)/i],
  [5, "The environment", /(environment|climate|sustainability|weather|nature|ecology)/i],
  [6, "States of mind", /(emotion|creative|creativity|meditation|mental|calm|stress)/i],
  [7, "Food", /(food|meal|cooking|recipe|ingredient|culinary|dining)/i],
  [8, "Graphic resources", /(background|texture|pattern|icon|vector|ui|graphic|digital asset)/i],
  [9, "Hobbies and leisure", /(hobby|craft|leisure|recreation|knitting|model building|relaxation)/i],
  [10, "Industry", /(industry|manufacturing|construction|steel|automotive|production|energy|mechanical)/i],
  [11, "Landscape", /(landscape|cityscape|scenic|vista|mountain|beach|city view)/i],
  [12, "Lifestyle", /(lifestyle|family|home life|daily life|social|personal moment)/i],
  [13, "People", /(person|people|woman|man|child|portrait|human|couple|worker)/i],
  [14, "Plants and flowers", /(plant|flower|botanical|garden|leaf|floral)/i],
  [15, "Culture and religion", /(culture|religion|tradition|festival|heritage|ceremony)/i],
  [16, "Science", /(science|laboratory|medical|research|technology|innovation|microscope)/i],
  [17, "Social issues", /(social issue|poverty|inequality|politics|activism|awareness)/i],
  [18, "Sports", /(sport|fitness|football|basketball|yoga|training|athletic|running)/i],
  [19, "Technology", /(technology|computer|smartphone|software|vr|connectivity|digital)/i],
  [20, "Transport", /(transport|car|bus|train|plane|highway|logistics|vehicle|infrastructure)/i],
  [21, "Travel", /(travel|tourism|destination|adventure|journey|landmark|vacation)/i],
];

function cleanText(value) {
  return String(value || "").replace(/[\u0000-\u001f]+/gu, " ").replace(/\s+/gu, " ").trim();
}

function safeFilename(title, jobId) {
  const stem = cleanText(title).toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "_").replace(/^_+|_+$/gu, "").slice(0, 18) || "stockforge_asset";
  const suffix = `_${jobId.slice(-5)}.jpg`;
  return `${stem}${suffix}`.slice(0, 30);
}

function uniqueKeywords(values) {
  const out = [];
  const seen = new Set();
  for (const raw of Array.isArray(values) ? values : []) {
    const word = cleanText(raw).toLowerCase().replace(/,/gu, "");
    if (!word || seen.has(word)) continue;
    if (word.length > 80) continue;
    seen.add(word);
    out.push(word);
    if (out.length >= 49) break;
  }
  return out;
}

function fallbackMetadata(concept) {
  const source = [concept.subject, concept.use_case, concept.composition, concept.context, concept.color, concept.viewpoint].filter(Boolean);
  const fallbackWords = source.flatMap((value) => cleanText(value).toLowerCase().split(/[^\p{L}\p{N}]+/u)).filter((word) => [...word].length >= 3);
  const title = cleanText(concept.subject || "Commercial stock asset").replace(/[,;:]+/gu, " ").replace(/[^\p{L}\p{N}\s-]/gu, "").replace(/\s+/gu, " ").slice(0, 70).trim();
  return { title: title || "Commercial stock asset", keywords: uniqueKeywords(fallbackWords), source: "deterministic-fallback" };
}

function pickCategory(concept, metadata) {
  const corpus = [concept.subject, concept.use_case, concept.composition, concept.context, metadata.title, ...(metadata.keywords || [])].join(" ");
  for (const [number, name, matcher] of CATEGORY_MAP) if (matcher.test(corpus)) return { number, name, source: "deterministic-map" };
  return { number: 8, name: "Graphic resources", source: "safe-default-human-review" };
}

function metadataRisk(metadata) {
  const corpus = `${metadata.title} ${(metadata.keywords || []).join(" ")}`.toLowerCase();
  const blockedPatterns = [
    /\b(in the style of|style of|inspired by|influenced by|based on the work of)\b/i,
    /\b(logo|trademark|brand name|copyrighted character|fictional character)\b/i,
    /\b(actual news|breaking news|news event|generative ai)\b/i,
  ];
  return blockedPatterns.some((pattern) => pattern.test(corpus));
}

async function generateMetadata(env, concept, summary) {
  const fallback = fallbackMetadata(concept);
  if (!env.AI) return fallback;
  try {
    const response = await env.AI.run("@cf/meta/llama-3.2-1b-instruct", {
      messages: [
        { role: "system", content: "Create conservative Adobe Stock metadata. Return JSON only with title and keywords. Title must be an accurate concise visual description, max 70 characters, plain text with no commas. Return up to 49 unique keywords, most important first. Do not invent brands, artist names, people, locations, fictional characters, government agencies, news events, or third-party intellectual property. Do not mention generative AI or technical prompt parameters." },
        { role: "user", content: JSON.stringify({ concept, visual_summary: summary }) },
      ],
      max_tokens: 500,
      temperature: 0.2,
    });
    const text = response?.response || response?.result || JSON.stringify(response);
    const parsed = JSON.parse(String(text).match(/\{[\s\S]*\}/)?.[0] || text);
    const title = cleanText(parsed?.title).replace(/[,;:]+/gu, " ").replace(/[^\p{L}\p{N}\s-]/gu, "").replace(/\s+/gu, " ").slice(0, 70).trim();
    const keywords = uniqueKeywords(parsed?.keywords);
    if (!title || !keywords.length) return fallback;
    return { title, keywords, source: "workers-ai-llama-3.2-1b" };
  } catch (_) {
    return fallback;
  }
}

function xmlEscape(value) {
  return cleanText(value).replace(/&/gu, "&amp;").replace(/</gu, "&lt;").replace(/>/gu, "&gt;").replace(/"/gu, "&quot;").replace(/'/gu, "&apos;");
}

function buildCsv(filename, metadata, category) {
  const csvTitle = metadata.title.replace(/,/gu, " ");
  return `Filename,Keywords,Title,Category\n${filename},"${metadata.keywords.join(",")}","${csvTitle}",${category.number}\n`;
}

function buildXmp(metadata, category) {
  const keywords = metadata.keywords.map((v) => `        <rdf:li>${xmlEscape(v)}</rdf:li>`).join("\n");
  return `<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>\n<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="StockForge">\n <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n  <rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/" xmlns:xmp="http://ns.adobe.com/xap/1.0/">\n   <dc:title><rdf:Alt><rdf:li xml:lang="x-default">${xmlEscape(metadata.title)}</rdf:li></rdf:Alt></dc:title>\n   <dc:subject><rdf:Bag>\n${keywords}\n   </rdf:Bag></dc:subject>\n   <photoshop:Category>${category.number}</photoshop:Category>\n   <xmp:CreatorTool>StockForge AI</xmp:CreatorTool>\n  </rdf:Description>\n </rdf:RDF>\n</x:xmpmeta>\n<?xpacket end="w"?>`;
}

function buildChecklist(metadata, category, result, job) {
  const peopleOrProperty = /(person|people|woman|man|child|human|portrait|building|house|office|interior|landmark|property)/i.test(`${metadata.title} ${metadata.keywords.join(" ")}`);
  return [
    "# StockForge Adobe review checklist",
    "",
    `- AI-generated disclosure: REQUIRED`,
    `- Category suggestion: ${category.number} — ${category.name} (human verification required)`,
    `- Title: ${metadata.title}`,
    `- Keywords: ${metadata.keywords.length}`,
    `- Human visual review: REQUIRED`,
    `- People/property release review: ${peopleOrProperty ? "REVIEW REQUIRED" : "not triggered by metadata heuristic"}`,
    `- Exact duplicate gate: ${result.similarity_gate?.automated_duplicate || "UNKNOWN"}`,
    `- Technical QA: ${result.technical_qa?.status || "UNKNOWN"}`,
    `- Marketplace submission: manual only`,
    "",
    "## Mandatory portal checks",
    "- Select Created using generative AI tools when uploading.",
    "- Verify title, keywords, category, language, and any required releases in the Adobe Stock Contributor Portal.",
    "- Do not submit until visual, rights, and metadata review is complete.",
    `- Source job: ${job.id}`,
  ].join("\n");
}

export async function onRequestPost(context) {
  try {
    const { env, params } = context;
    if (!env.DB || !env.ASSET_STORE) return json({ detail: "D1/R2 bindings are missing" }, 500);
    const job = await env.DB.prepare(`SELECT * FROM jobs_sf WHERE id=?`).bind(String(params.jobId || "")).first();
    if (!job) return json({ detail: "Job not found" }, 404);
    if (job.status !== "approved") return json({ detail: "Explicit human approval is required before release" }, 409);
    const result = job.result_json ? JSON.parse(job.result_json) : {};
    if (result.technical_qa?.status === "FAIL") return json({ detail: "Technical QA failed" }, 409);
    if (result.similarity_gate?.automated_duplicate === "BLOCK") return json({ detail: "Duplicate gate is blocking this asset" }, 409);
    const planRow = await env.DB.prepare(`SELECT plan_json FROM plans_sf WHERE reference_id=?`).bind(job.reference_id).first();
    const plan = JSON.parse(planRow?.plan_json || "{}");
    const concept = plan.concept || {};
    const metadata = await generateMetadata(env, concept, plan.reference_summary || "");
    const category = pickCategory(concept, metadata);
    const riskFlag = metadataRisk(metadata);
    if (riskFlag) return json({ detail: "Metadata contains a policy-risk phrase and must be corrected before release", metadata, category }, 422);

    const filename = safeFilename(metadata.title, job.id);
    const csv = buildCsv(filename, metadata, category);
    const xmp = buildXmp(metadata, category);
    const checklist = buildChecklist(metadata, category, result, job);
    const manifest = {
      schema_version: 4,
      status: "READY_UPLOAD_ADOBE",
      asset: { ...(result.final || result), filename },
      metadata: {
        ...metadata,
        ai_generated: true,
        ai_disclosure_required: true,
        human_metadata_review_required: true,
        category,
        csv_filename: filename,
        language_review_required: true,
      },
      provenance: { generation_provider: "hf-zerogpu", generation_model: result.model || "Z-Image-Turbo", upscale_provider: "hf-zerogpu", upscale_model: result.final?.model || "RealESRGAN_x4plus", workflow_job_id: job.id },
      gates: { technical: result.technical_qa, duplicate: result.similarity_gate, human_approval: result.human_review || null },
      release_review: { people_or_property_review_required: true, signed_release_files: [] },
      package: { csv: `/api/manifest/${job.id}?kind=csv`, xmp: `/api/manifest/${job.id}?kind=xmp`, checklist: `/api/manifest/${job.id}?kind=checklist` },
      marketplace_submission: "manual_only",
      human_review_required: true,
    };

    const manifestKey = `artifacts/${job.id}/manifest.json`;
    const csvKey = `artifacts/${job.id}/adobe-metadata.csv`;
    const xmpKey = `artifacts/${job.id}/${filename.replace(/\.jpg$/iu, ".xmp")}`;
    const checklistKey = `artifacts/${job.id}/review-checklist.md`;
    const aiKey = `artifacts/${job.id}/ai-disclosure.txt`;
    await env.ASSET_STORE.put(manifestKey, JSON.stringify(manifest, null, 2), { httpMetadata: { contentType: "application/json" } });
    await env.ASSET_STORE.put(csvKey, csv, { httpMetadata: { contentType: "text/csv; charset=utf-8" } });
    await env.ASSET_STORE.put(xmpKey, xmp, { httpMetadata: { contentType: "application/rdf+xml" } });
    await env.ASSET_STORE.put(checklistKey, checklist, { httpMetadata: { contentType: "text/markdown; charset=utf-8" } });
    await env.ASSET_STORE.put(aiKey, "Created using generative AI tools: REQUIRED PORTAL DISCLOSURE\nPeople and Property are fictional: VERIFY BASED ON THE ACTUAL ASSET BEFORE SUBMISSION.\n", { httpMetadata: { contentType: "text/plain; charset=utf-8" } });
    return json({ status: "READY_UPLOAD_ADOBE", download_url: result.final?.final_asset_url || null, manifest_url: `/api/manifest/${job.id}`, manifest, package: { csv_url: `/api/manifest/${job.id}?kind=csv`, xmp_url: `/api/manifest/${job.id}?kind=xmp`, checklist_url: `/api/manifest/${job.id}?kind=checklist`, ai_disclosure_url: `/api/manifest/${job.id}?kind=ai-disclosure` } });
  } catch (error) { return json({ detail: error instanceof Error ? error.message : String(error) }, 500); }
}
