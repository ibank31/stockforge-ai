import test from "node:test";
import assert from "node:assert/strict";
import { locatePrimaryAsset } from "../frontend/lib/reference-localization.js";

test("dynamic primary asset localization", async () => {
  const env = { AI: { async run() { return { response: JSON.stringify({ reference_type: "SOCIAL_MEDIA_POST", confidence: 0.96, presentation_elements: ["social chrome"], evidence_elements: ["caption"], asset_candidates: [{ label: "green travel mug", confidence: 0.94, bbox_normalized: { x: 0.27, y: 0.31, width: 0.24, height: 0.42 }, why_asset: "standalone reusable object" }], primary_asset: { label: "green travel mug", confidence: 0.94, bbox_normalized: { x: 0.27, y: 0.31, width: 0.24, height: 0.42 }, why_asset: "most salient reusable asset" }, primary_asset_candidate: "green travel mug" }) }; } } };
  const result = await locatePrimaryAsset(env, Uint8Array.from([1,2,3]).buffer, "image/png");
  assert.equal(result.stage, "ASSET_LOCALIZATION");
  assert.equal(result.primary_asset.label, "green travel mug");
  assert.deepEqual(result.localization.primary_bbox, { x: 0.27, y: 0.31, width: 0.24, height: 0.42 });
});

test("missing bbox fails closed", async () => {
  const env = { AI: { async run() { return { response: JSON.stringify({ reference_type: "RAW_ASSET", confidence: 0.9, asset_candidates: [], primary_asset: { label: "thing", confidence: 0.9, bbox_normalized: null } }) }; } } };
  await assert.rejects(() => locatePrimaryAsset(env, Uint8Array.from([1]).buffer, "image/png"), /ASSET_LOCALIZATION_FAILED/);
});

test("valid primary asset remains usable when candidate list is omitted", async () => {
  const env = { AI: { async run() { return { response: JSON.stringify({
    reference_type: "EMAIL_SCREENSHOT",
    confidence: 0.35,
    asset_candidates: [],
    primary_asset: {
      label: "illustrated school backpack",
      confidence: 0.91,
      bbox_normalized: { x: 0.31, y: 0.24, width: 0.36, height: 0.49 },
      why_asset: "the reusable visual subject",
    },
  }) }; } } };
  const result = await locatePrimaryAsset(env, Uint8Array.from([1]).buffer, "image/png");
  assert.equal(result.primary_asset.label, "illustrated school backpack");
  assert.equal(result.asset_candidates.length, 1);
  assert.deepEqual(result.localization.primary_bbox, { x: 0.31, y: 0.24, width: 0.36, height: 0.49 });
});
