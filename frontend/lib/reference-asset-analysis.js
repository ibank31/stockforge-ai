import { locatePrimaryAsset } from "./reference-localization.js";
import { runReferenceForensics } from "./reference-forensics.js";
export async function analyzeReferenceAsset(env, bytes, mime) {
  const localization = await locatePrimaryAsset(env, bytes, mime);
  const forensics = await runReferenceForensics(env, bytes, mime);
  return { schema_version: 1, stage: "REFERENCE_ASSET_ANALYSIS", localization, forensics, generation_reference: { source_asset: localization.primary_asset.label, source_bbox_normalized: localization.primary_asset.bbox_normalized, asset_dna: forensics.asset_dna, target: { format: "PNG", background: "transparent", alpha: true }, redesign: ["silhouette", "proportions", "details", "palette", "viewpoint", "composition"], exclude: ["UI", "source text", "usernames", "brands", "watermarks", "exact copied artwork"] } };
}
