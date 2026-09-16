import test from "node:test";
import assert from "node:assert/strict";
import { locatePrimaryAsset } from "../frontend/lib/reference-localization.js";

function forensicEnv() {
  const calls = [];
  return { calls, AI: { async run(model, input) {
    calls.push({ model, input });
    return { choices: [{ message: { content: JSON.stringify({
      reference_type: "marketplace_screenshot",
      primary_asset: {
        label: "illustrated mountain landscape",
        confidence: 0.96,
        bbox_normalized: { x: 0.31, y: 0.51, width: 0.35, height: 0.18 },
        medium: "digital_illustration",
        realism: "stylized",
        visual_style: "clean hand-drawn stock illustration with outlined shapes",
        composition: "compact centered artwork isolated inside a white marketplace card",
        materials: ["illustrated landscape"],
        colors: ["blue", "green", "brown", "white"],
        distinctive_features: ["mountains", "trees", "water"]
      },
      asset_candidates: [],
      presentation_elements: [
        { type: "logo", description: "Adobe Stock branding" },
        { type: "text", description: "Congratulations and earnings text" },
        { type: "button", description: "More best sellers button" },
        { type: "watermark", description: "social account watermark" }
      ],
      evidence_elements: [
        { type: "marketplace", description: "Adobe Stock marketplace context", verified: false },
        { type: "earnings", description: "visible earnings claim", verified: false },
        { type: "best_seller_claim", description: "best seller claim", verified: false }
      ]
    }) } }] };
  } } };
}

function assertNear(actual, expected, epsilon = 1e-9) {
  assert.ok(Math.abs(actual - expected) <= epsilon, `${actual} is not within ${epsilon} of ${expected}`);
}
function assertBbox(actual, expected) {
  for (const key of ["x", "y", "width", "height"]) assertNear(actual[key], expected[key]);
}

test("Gemma visual forensics isolates the embedded marketplace asset and preserves medium", async () => {
  const e = forensicEnv();
  const result = await locatePrimaryAsset(e, Uint8Array.from([1,2,3]).buffer, "image/png");
  assert.equal(result.stage, "ASSET_LOCALIZATION");
  assert.equal(result.reference_type, "marketplace_screenshot");
  assert.equal(result.primary_asset.label, "illustrated mountain landscape");
  assert.equal(result.primary_asset.medium, "digital_illustration");
  assert.equal(result.primary_asset.realism, "stylized");
  assertBbox(result.localization.primary_bbox, { x: 0.31, y: 0.51, width: 0.35, height: 0.18 });
  assert.equal(result.localization.method, "gemma_vision_forensics");
  assert.equal(result.localization.annotation_aware, true);
  assert.equal(result.presentation_elements.length, 4);
  assert.equal(result.evidence_elements.length, 3);
  assert.equal(e.calls[0].model, "@cf/google/gemma-4-26b-a4b-it");
  assert.equal(e.calls[0].input.response_format.type, "json_object");
  const parts = e.calls[0].input.messages[0].content;
  assert.equal(parts[0].type, "image_url");
  assert.match(parts[0].image_url.url, /^data:image\/png;base64,[A-Za-z0-9+/]+=*$/);
});

test("Gemma forensic candidates reject generic labels and oversized screenshot boxes", async () => {
  const e = { AI: { async run() { return { choices: [{ message: { content: JSON.stringify({
    reference_type: "social_media_screenshot",
    primary_asset: { label: "object", confidence: 0.99, bbox_normalized: { x: 0, y: 0, width: 1, height: 1 } },
    asset_candidates: [{ label: "orange backpack", confidence: 0.82, bbox_normalized: { x: 0.25, y: 0.55, width: 0.35, height: 0.22 } }]
  }) } }] }; } } };
  const result = await locatePrimaryAsset(e, Uint8Array.from([1]).buffer, "image/jpeg");
  assert.equal(result.primary_asset.label, "orange backpack");
  assertBbox(result.primary_asset.bbox_normalized, { x: 0.25, y: 0.55, width: 0.35, height: 0.22 });
});

test("Moondream remains a fallback when forensic vision is unavailable", async () => {
  const calls = [];
  const e = { AI: { async run(model, input) {
    calls.push({ model, input });
    if (model === "@cf/google/gemma-4-26b-a4b-it") throw new Error("Gemma unavailable");
    if (input.task === "query") return { answer: "green travel mug" };
    if (input.task === "detect") return { objects: [{ x_min: 0.27, y_min: 0.31, x_max: 0.51, y_max: 0.73 }] };
    throw new Error("unexpected task");
  } } };
  const result = await locatePrimaryAsset(e, Uint8Array.from([1,2,3]).buffer, "image/png");
  assert.equal(result.primary_asset.label, "green travel mug");
  assertBbox(result.localization.primary_bbox, { x: 0.27, y: 0.31, width: 0.24, height: 0.42 });
  assert.equal(result.localization.method, "moondream_query_detect");
});

test("Gemma fallback still localizes when both forensic and Moondream paths fail", async () => {
  const calls = [];
  const e = { AI: { async run(model, input) {
    calls.push({ model, input });
    if (model === "@cf/google/gemma-4-26b-a4b-it") {
      if (calls.length === 1) throw new Error("forensics unavailable");
      return { choices: [{ message: { content: JSON.stringify({ primary_asset: { label: "green travel mug", confidence: 0.91, bbox_normalized: { x: 0.2, y: 0.2, width: 0.5, height: 0.6 } } }) } }] };
    }
    throw new Error("Moondream unavailable");
  } } };
  const result = await locatePrimaryAsset(e, Uint8Array.from([1,2,3]).buffer, "image/png");
  assert.equal(result.localization.method, "gemma_vision_fallback");
  assert.equal(result.primary_asset.label, "green travel mug");
});
