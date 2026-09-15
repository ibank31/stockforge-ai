import { locatePrimaryAsset } from "../../lib/reference-localization.js";

const MAX_BYTES = 8 * 1024 * 1024;
const TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);
function json(data,status=200){return Response.json(data,{status,headers:{"cache-control":"no-store"}})}
export async function onRequestPost({request,env}){try{if(!env.AI)return json({detail:"Reference intelligence AI binding is missing"},500);const form=await request.formData();const file=form.get("file");if(!(file instanceof File))return json({detail:"file is required"},400);if(!TYPES.has(file.type))return json({detail:"Only JPG, PNG and WebP references are accepted"},400);if(file.size>MAX_BYTES)return json({detail:"Reference exceeds 8 MB"},413);return json({filename:file.name||"reference",...(await locatePrimaryAsset(env,await file.arrayBuffer(),file.type))})}catch(error){const message=error instanceof Error?error.message:String(error);return json({detail:message},/ASSET_LOCALIZATION_FAILED/.test(message)?422:500)}}
