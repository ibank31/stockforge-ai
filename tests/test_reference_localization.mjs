import test from "node:test";
import assert from "node:assert/strict";
import { locatePrimaryAsset } from "../frontend/lib/reference-localization.js";

function env() {
  const calls = [];
  return { calls, AI: { async run(model, input) {
    calls.push({ model, input });
    if (input.task === "query") return { answer: "green travel mug" };
    if (input.task === "detect") return { objects: [{ x_min: 0.27, y_min: 0.31, x_max: 0.51, y_max: 0.73 }] };
    throw new Error("unexpected task");
  } };
}

test("Moondream dynamically identifies and localizes the primary asset", async () => {
  const e = env();
  const result = await locatePrimaryAsset(e, Uint8Array.from([1,2,3]).buffer, "image/png");
  assert.equal(result.stage, "ASSET_LOCALIZATION");
  assert.equal(result.primary_asset.label, "green travel mug");
  assert.deepEqual(result.localization.primary_bbox, { x: 0.27, y: 0.31, width: 0.24, height: 0.42 });
  assert.equal(result.localization.method, "moondream_query_detect");
  assert.equal(e.calls[0].model, "@cf/moondream/moondream3.1-9B-A2B");
  assert.equal(e.calls[0].input.task, "query");
  assert.match(e.calls[0].input.image, /^data:image\/png;base64,/);
  assert.equal(e.calls[1].input.task, "detect");
  assert.equal(e.calls[1].input.target, "green travel mug");
});

test("localization fails closed when detection returns no objects", async () => {
  const e = { AI: { async run(_model, input) { if (input.task === "query") return { answer: "camera" }; return { objects: [] }; } } };
  await assert.rejects(() => locatePrimaryAsset(e, Uint8Array.from([1]).buffer, "image/png"), /ASSET_LOCALIZATION_FAILED/);
});

test("detection coordinates are normalized to the image contract", async () => {
  const e = { AI: { async run(_model, input) { if (input.task === "query") return { answer: "backpack" }; return { objects: [{ x_min: 0, y_min: 0.1, x_max: 1, y_max: 1 }] }; } } };
  const result = await locatePrimaryAsset(e, Uint8Array.from([1]).buffer, "image/webp");
  assert.deepEqual(result.primary_asset.bbox_normalized, { x: 0, y: 0.1, width: 1, height: 0.9 });
});
