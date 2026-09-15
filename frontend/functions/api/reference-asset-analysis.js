import { analyzeReferenceAsset } from "../../lib/reference-asset-analysis.js";
const MAX=8*1024*1024;
const TYPES=new Set(["image/jpeg","image/png","image/webp"]);
function json(data,status=200){return Response.json(data,{status,headers:{"cache-control":"no-store"}})}
export async function onRequestPost({request,env}){try{const f=(await request.formData()).get("file");if(!(f instanceof File))return json({detail:"file is required"},400);if(!TYPES.has(f.type))return json({detail:"Only JPG, PNG and WebP references are accepted"},400);if(f.size>MAX)return json({detail:"Reference exceeds 8 MB"},413);return json({filename:f.name||"reference",...(await analyzeReferenceAsset(env,await f.arrayBuffer(),f.type))})}catch(e){const m=e instanceof Error?e.message:String(e);return json({detail:m},/FAILED/.test(m)?422:500)}}
