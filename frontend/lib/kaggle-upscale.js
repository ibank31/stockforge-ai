const KAGGLE_API = "https://www.kaggle.com/api/v1";
const WORKER_RAW = "https://raw.githubusercontent.com/ibank31/stockforge-ai/main/deploy/kaggle-finalizer/worker.py";

function auth(env) {
  const token = String(env.KAGGLE_API_TOKEN || "").trim();
  if (!token) throw new Error("KAGGLE_API_TOKEN is not configured");
  return { Authorization: `Bearer ${token}`, Accept: "application/json" };
}
async function kaggle(env, path, options = {}) {
  const response = await fetch(`${KAGGLE_API}${path}`, { ...options, headers: { ...auth(env), ...(options.headers || {}) } });
  if (!response.ok) throw new Error(`Kaggle API ${path} failed: HTTP ${response.status} ${await response.text()}`);
  return response;
}
function base64Bytes(bytes) {
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) binary += String.fromCharCode(...bytes.subarray(i, Math.min(i + chunk, bytes.length)));
  return btoa(binary);
}
async function sha256Hex(bytes) {
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map(v => v.toString(16).padStart(2, "0")).join("");
}

export async function submitKaggleUpscale(env, sourceUrl, stockforgeJobId, width, height) {
  const configured = String(env.KAGGLE_KERNEL_SLUG || "stockforge-finalizer").trim();
  const configuredParts = configured.split("/").filter(Boolean);
  const configuredOwner = String(env.KAGGLE_KERNEL_OWNER || (configuredParts.length > 1 ? configuredParts[configuredParts.length - 2] : "iqbalteguh")).trim();
  const configuredSlug = configuredParts[configuredParts.length - 1] || "stockforge-finalizer";
  const suffix = String(stockforgeJobId || "job").replace(/[^a-z0-9-]/gi, "-").toLowerCase().slice(-10);
  const slug = `${configuredSlug}-${suffix}`.slice(0, 50).replace(/-+$/g, "");
  const fullSlug = `${configuredOwner}/${slug}`;
  const sourceResponse = await fetch(sourceUrl, { headers: { "user-agent": "StockForge-Kaggle-Provider/1.0" } });
  if (!sourceResponse.ok) throw new Error(`Unable to fetch raw asset for Kaggle: HTTP ${sourceResponse.status}`);
  const sourceBytes = new Uint8Array(await sourceResponse.arrayBuffer());
  if (sourceBytes.byteLength < 1024) throw new Error("Raw asset is unexpectedly small");
  const workerResponse = await fetch(WORKER_RAW, { headers: { "cache-control": "no-cache" } });
  if (!workerResponse.ok) throw new Error(`Unable to load StockForge Kaggle finalizer worker: HTTP ${workerResponse.status}`);
  const worker = await workerResponse.text();
  const request = {
    schema_version: 1,
    kind: "stockforge.master_finalizer_request",
    request_id: stockforgeJobId,
    status: "prepared_no_gpu",
    source: { relative_path: "source.jpg", sha256: await sha256Hex(sourceBytes), width: Number(width), height: Number(height), format: "JPEG", color_mode: "RGB" },
    target: { mode: "ai_upscale", scale: 4, format: "jpeg", color_space: "sRGB", expected_width: Number(width) * 4, expected_height: Number(height) * 4, minimum_megapixels: Math.max(6, (Number(width) * 4 * Number(height) * 4) / 1000000) },
    destination: `masters/${stockforgeJobId}-master.jpg`,
  };
  const injected = `REQUEST_B64 = ${JSON.stringify(base64Bytes(new TextEncoder().encode(JSON.stringify(request))))}\nSOURCE_NAME = "source.jpg"\nSOURCE_B64 = ${JSON.stringify(base64Bytes(sourceBytes))}\n`;
  const script = injected + worker;
  const title = slug.replace(/[-_]+/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  const payload = { slug: fullSlug, newTitle: title, text: script, language: "python", kernelType: "script", isPrivate: true, enableGpu: true, enableInternet: true, machineShape: String(env.KAGGLE_MACHINE_SHAPE || "NvidiaTeslaT4") };
  const response = await kaggle(env, "/kernels/push", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(payload) });
  const result = await response.json();
  if (result.error) throw new Error(`Kaggle push rejected: ${result.error}`);
  const invalid = ["invalidDatasetSources", "invalidCompetitionSources", "invalidKernelSources", "invalidModelSources"].flatMap(key => Array.isArray(result[key]) && result[key].length ? [`${key}: ${JSON.stringify(result[key])}`] : []);
  if (invalid.length) throw new Error(`Kaggle push rejected invalid sources: ${invalid.join("; ")}`);
  const ref = String(result.ref || "");
  const parts = ref.split("/").filter(Boolean);
  if (parts.length < 2) throw new Error(`Kaggle push returned invalid ref: ${ref || "<empty>"}`);
  const owner = parts[parts.length - 2];
  const actualSlug = parts[parts.length - 1];
  return { owner, slug: actualSlug, provider_job_id: `${owner}/${actualSlug}`, version_number: result.versionNumber ?? result.version_number ?? null, ref };
}

export async function getKaggleStatus(env, providerJobId) {
  const [owner, slug] = String(providerJobId || "").split("/");
  if (!owner || !slug) throw new Error("Invalid Kaggle provider job id");
  const response = await kaggle(env, `/kernels/status?userName=${encodeURIComponent(owner)}&kernelSlug=${encodeURIComponent(slug)}`);
  return await response.json();
}
export async function downloadKaggleOutput(env, providerJobId, fileName) {
  const [owner, slug] = String(providerJobId || "").split("/");
  if (!owner || !slug) throw new Error("Invalid Kaggle provider job id");
  return await kaggle(env, `/kernels/output/download/${encodeURIComponent(owner)}/${encodeURIComponent(slug)}/${encodeURIComponent(fileName)}`, { headers: { Accept: "*/*" } });
}
