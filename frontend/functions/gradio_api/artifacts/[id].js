export async function onRequestGet(context) {
  const id = String(context.params.id || "");
  if (!id || !/^[A-Za-z0-9_-]+$/.test(id)) return new Response("Not Found", { status: 404 });
  const object = await context.env.ASSET_STORE.get(`gradio-fallback/${id}.bin`);
  if (!object) return new Response("Not Found", { status: 404 });
  return new Response(object.body, {
    headers: {
      "content-type": object.httpMetadata?.contentType || "application/octet-stream",
      "cache-control": "private, max-age=300",
    },
  });
}
