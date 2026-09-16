const MODEL = "@cf/bytedance/stable-diffusion-xl-lightning";
const PREFIX = "gradio-fallback";

function base64(bytes) {
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) binary += String.fromCharCode(...bytes.subarray(i, Math.min(i + chunk, bytes.length)));
  return btoa(binary);
}

function mime(bytes) {
  if (bytes.length >= 8 && bytes[0] === 137 && bytes[1] === 80 && bytes[2] === 78 && bytes[3] === 71) return "image/png";
  if (bytes.length >= 3 && bytes[0] === 255 && bytes[1] === 216 && bytes[2] === 255) return "image/jpeg";
  if (bytes.length >= 12 && bytes[0] === 82 && bytes[1] === 73 && bytes[2] === 70 && bytes[8] === 87 && bytes[9] === 69 && bytes[10] === 66 && bytes[11] === 80) return "image/webp";
  return "application/octet-stream";
}

function eventId() { return `${PREFIX}-${crypto.randomUUID().replaceAll("-", "")}`; }
function artifactKey(id) { return `${PREFIX}/${id}.bin`; }
function artifactUrl(request, id) { return `${new URL(request.url).origin}/gradio_api/artifacts/${encodeURIComponent(id)}`; }

async function generate(env, request, id, data) {
  const prompt = String(data?.[0] || "").trim();
  if (!prompt) return Response.json({ detail: "Prompt is required" }, { status: 400 });
  const seed = data?.[4] ? Number(data[4]) : Math.floor(Math.random() * 0x7fffffff);
  const response = await env.AI.run(MODEL, {
    prompt: `commercial stock asset, clean composition, high visual quality, no text, no logos, no watermark, ${prompt}`,
    negative_prompt: "text, letters, logo, watermark, signature, UI, screenshot, frame, border, blurry, distorted, duplicate subject",
    width: 2048,
    height: 2048,
    num_steps: 4,
    guidance: 7.5,
    seed,
  });
  const bytes = new Uint8Array(await new Response(response).arrayBuffer());
  if (!bytes.length) throw new Error("Workers AI returned an empty image");
  await env.ASSET_STORE.put(artifactKey(id), bytes, { httpMetadata: { contentType: mime(bytes), cacheControl: "private, max-age=300" } });
  return Response.json({ event_id: id, provider: "cloudflare-workers-ai", model: MODEL, dimensions: [2048, 2048], bytes: bytes.length });
}

async function finalize(env, request, id, data) {
  const sourceUrl = String(data?.[0] || "");
  if (!sourceUrl) return Response.json({ detail: "Source URL is required" }, { status: 400 });
  const source = await fetch(sourceUrl);
  if (!source.ok) throw new Error(`Source fetch failed: HTTP ${source.status}`);
  const sourceBytes = new Uint8Array(await source.arrayBuffer());
  const response = await env.AI.run(MODEL, {
    prompt: "Preserve the source artwork subject and composition as closely as possible. Improve clarity and clean small artifacts. Do not add text, logos, watermark, border, or new objects. Keep the commercial stock-art appearance.",
    negative_prompt: "text, letters, logo, watermark, signature, UI, screenshot, border, new objects, altered subject identity",
    image_b64: base64(sourceBytes),
    width: 2048,
    height: 2048,
    num_steps: 4,
    strength: 0.12,
    guidance: 5,
    seed: Math.floor(Math.random() * 0x7fffffff),
  });
  const bytes = new Uint8Array(await new Response(response).arrayBuffer());
  if (!bytes.length) throw new Error("Workers AI finalization returned an empty image");
  await env.ASSET_STORE.put(artifactKey(id), bytes, { httpMetadata: { contentType: "image/jpeg", cacheControl: "private, max-age=300" } });
  return Response.json({ event_id: id, provider: "cloudflare-workers-ai", model: MODEL, dimensions: [2048, 2048], bytes: bytes.length });
}

export async function onRequestPost(context) {
  const path = Array.isArray(context.params.path) ? context.params.path : [context.params.path];
  const apiName = path[0];
  const data = (await context.request.json())?.data || [];
  const id = eventId();
  try {
    if (apiName === "generate_remote") await generate(context.env, context.request, id, data);
    else if (apiName === "upscale_remote") await finalize(context.env, context.request, id, data);
    else return Response.json({ detail: `Unknown compute API: ${apiName}` }, { status: 404 });
    return Response.json({ event_id: id });
  } catch (error) {
    return Response.json({ detail: error instanceof Error ? error.message : String(error) }, { status: 502 });
  }
}

export async function onRequestGet(context) {
  const path = Array.isArray(context.params.path) ? context.params.path : [context.params.path];
  const apiName = path[0];
  const id = path[1];
  if (!apiName || !id) return Response.json({ detail: "event_id is required" }, { status: 400 });
  const object = await context.env.ASSET_STORE.head(artifactKey(id));
  if (!object) return new Response("event: pending\ndata: null\n\n", { headers: { "content-type": "text/event-stream", "cache-control": "no-store" } });
  const values = apiName === "generate_remote"
    ? [{ url: artifactUrl(context.request, id) }, 0, 0]
    : [{ url: artifactUrl(context.request, id) }, 1, 2048, 2048];
  const body = `event: complete\ndata: ${JSON.stringify(values)}\n\n`;
  return new Response(body, { headers: { "content-type": "text/event-stream", "cache-control": "no-store" } });
}
