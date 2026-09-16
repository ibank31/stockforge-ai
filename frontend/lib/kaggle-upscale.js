const KAGGLE_API = "https://www.kaggle.com/api/v1";
const WORKER_RAW = "https://raw.githubusercontent.com/ibank31/stockforge-ai/main/deploy/kaggle-finalizer/worker.py";

function auth(env) {
  const token = String(env.KAGGLE_API_TOKEN || "").trim();
  if (!token) throw new Error("KAGGLE_API_TOKEN is not configured");
  return { Authorization: `Bearer ${token}`, Accept: "application/json" };
}

async function kaggle(env, path, options = {}) {
  const response = await fetch(`${KAGGLE_API}${path}`, {
    ...options,
    headers: { ...auth(env), ...(options.headers || {}) },
  });
  if (!response.ok) throw new Error(`Kaggle API ${path} failed: HTTP ${response.status} ${await response.text()}`);
  return response;
}

function base64Bytes(bytes) {
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) binary += String.fromCharCode(...bytes.subarray(i, Math.min(i + chunk, bytes.length)));
  return btoa(binary);
}

export async function submitKaggleUpscale(env, sourceUrl, stockforgeJobId) {
  const owner = String(env.KAGGLE_KERNEL_OWNER || "iqbalteguh").trim();
  const slug = String(env.KAGGLE_KERNEL_SLUG || "stockforge-finalizer").trim();
  const sourceResponse = await fetch(sourceUrl, { headers: { "user-agent": "StockForge-Kaggle-Provider/1.0" } });
  if (!sourceResponse.ok) throw new Error(`Unable to fetch raw asset for Kaggle: HTTP ${sourceResponse.status}`);
  const sourceBytes = new Uint8Array(await sourceResponse.arrayBuffer());
  if (sourceBytes.byteLength < 1024) throw new Error("Raw asset is unexpectedly small");

  const workerResponse = await fetch(WORKER_RAW, { headers: { "cache-control": "no-cache" } });
  if (!workerResponse.ok) throw new Error(`Unable to load StockForge Kaggle finalizer worker: HTTP ${workerResponse.status}`);
  const worker = await workerResponse.text();
  const sourceB64 = base64Bytes(sourceBytes);
  const request = {
    schema_version: 1,
    kind: "stockforge.master_finalizer_request",
    request_id: stockforgeJobId,
    status: "prepared_no_gpu",
    source: { relative_path: "source.jpg" },
    target: { mode: "ai_upscale", scale: 4, format: "jpeg", color_space: "sRGB" },
    destination: `masters/${stockforgeJobId}-master.jpg`,
  };
  const injected = `import base64 as _sf_b64\nREQUEST_B64 = ${JSON.stringify(btoa(unescape(encodeURIComponent(JSON.stringify(request)))))}\nSOURCE_NAME = "source.jpg"\nSOURCE_B64 = ${JSON.stringify(sourceB64)}\n`;
  const script = injected + worker;

  const payload = {
    slug,
    newTitle: "StockForge Finalizer",
    text: script,
    language: "python",
    kernelType: "script",
    isPrivate: true,
    enableGpu: true,
    enableInternet: true,
    machineShape: String(env.KAGGLE_MACHINE_SHAPE || "NvidiaTeslaT4"),
  };
  const response = await kaggle(env, "/kernels/push", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
  const result = await response.json();
  return { owner, slug, provider_job_id: `${owner}/${slug}`, version_number: result.versionNumber ?? result.version_number ?? null, ref: result.ref || `${owner}/${slug}` };
}

export async function getKaggleStatus(env, providerJobId) {
  const [owner, slug] = String(providerJobId || "").split("/");
  if (!owner || !slug) throw new Error("Invalid Kaggle provider job id");
  const response = await kaggle(env, `/kernels/status?userName=${encodeURIComponent(owner)}&kernelSlug=${encodeURIComponent(slug)}`);
  return await response.json();
}

export async function downloadKaggleOutput(env, providerJobId, fileName) {
  const [owner, slug] = String(providerJobId || "").split("/");
  const response = await kaggle(env, `/kernels/output/download/${encodeURIComponent(owner)}/${encodeURIComponent(slug)}/${encodeURIComponent(fileName)}`, { headers: { Accept: "*/*" } });
  return response;
}
