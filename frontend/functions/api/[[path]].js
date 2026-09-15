const DEFAULT_CONTROL_PLANE = "https://ibank31-stockforge-control.hf.space";

export async function onRequest(context) {
  const requestUrl = new URL(context.request.url);
  const controlPlane = (context.env.STOCKFORGE_CONTROL_PLANE_URL || DEFAULT_CONTROL_PLANE).replace(/\/$/, "");
  const target = new URL(controlPlane + requestUrl.pathname + requestUrl.search);

  // The browser uses /api/health for the status badge while the FastAPI
  // control plane exposes deployment health at /health.
  if (requestUrl.pathname === "/api/health") {
    target.pathname = "/health";
  }

  const headers = new Headers(context.request.headers);
  headers.delete("host");
  headers.set("x-stockforge-front-door", "cloudflare-pages");

  const init = {
    method: context.request.method,
    headers,
    redirect: "follow",
  };

  if (context.request.method !== "GET" && context.request.method !== "HEAD") {
    init.body = context.request.body;
  }

  try {
    const response = await fetch(new Request(target.toString(), init));
    const out = new Response(response.body, response);
    out.headers.set("cache-control", "no-store");
    out.headers.set("x-stockforge-control-plane", controlPlane);
    return out;
  } catch (error) {
    return Response.json(
      {
        detail: "StockForge control plane is unreachable.",
        error: error instanceof Error ? error.message : String(error),
        control_plane: controlPlane,
      },
      { status: 502, headers: { "cache-control": "no-store" } },
    );
  }
}
