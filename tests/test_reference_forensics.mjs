import test from "node:test";
import assert from "node:assert/strict";
import { runReferenceForensics } from "../frontend/lib/reference-forensics.js";

test("reference forensics separates presentation from PNG asset contract", async () => {
  const calls = [];
  const env = {
    AI: {
      async run(model, payload) {
        calls.push({ model, payload });
        const text = calls.length === 1
          ? JSON.stringify({
              reference_type: "MARKETPLACE_SCREENSHOT",
              confidence: 0.98,
              presentation_layer_present: true,
              presentation_elements: ["Adobe Stock header", "earnings amount", "best seller label", "button"],
              evidence_layer_present: true,
              evidence_elements: ["reported earning amount", "best seller claim"],
              asset_layer_present: true,
              asset_elements: ["backpack illustration"],
              primary_asset_candidate: "single cartoon backpack illustration",
              separation_notes: ["The marketplace shell and sales proof are presentation/evidence, not the asset itself."]
            })
          : JSON.stringify({
              asset_type: "illustrated_object",
              primary_subject: "cartoon backpack",
              subject_count: "1",
              morphology: "rounded backpack silhouette with a front pocket",
              structure: "main body, shoulder straps, front pocket and side details",
              orientation: "upright front-facing",
              visual_style: "playful flat commercial illustration",
              line_style: "clean simplified outlines",
              shading: "minimal flat shading",
              material: "illustrated textile",
              colors: ["teal", "yellow", "red"],
              distinctive_features: ["compact rounded silhouette", "contrasting front pocket"],
              asset_function: ["standalone decorative illustration", "education-themed graphic element"],
              target_background: "transparent",
              text_as_asset: false,
              logo_or_brand_as_asset: false,
              target_background: "transparent",
              source_background_status: "presentation_wrapper",
              confidence: 0.95
            });
        return { choices: [{ text }] };
      }
    }
  };

  const onePixelPng = Uint8Array.from([137,80,78,71,13,10,26,10]);
  const result = await runReferenceForensics(env, onePixelPng.buffer, "image/png");

  assert.equal(result.schema_version, 2);
  assert.equal(result.stage, "REFERENCE_FORENSICS");
  assert.equal(result.reference_classification.reference_type, "MARKETPLACE_SCREENSHOT");
  assert.equal(result.reference_classification.primary_asset_candidate, "single cartoon backpack illustration");
  assert.equal(result.asset_dna.primary_subject, "cartoon backpack");
  assert.equal(result.asset_dna.target_background, "transparent");
  assert.equal(result.generation_contract.output_type, "PNG");
  assert.equal(result.generation_contract.alpha_required, true);
  assert.equal(result.generation_contract.background, "transparent");
  assert.equal(calls.length, 2);
  for (const call of calls) {
    assert.equal(call.model, "@cf/google/gemma-4-26b-a4b-it");
    assert.equal(typeof call.payload.image, "string");
    assert.match(call.payload.image, /^[A-Za-z0-9+/]+=*$/);
    assert.doesNotMatch(call.payload.image, /^data:/);
    assert.equal(typeof call.payload.messages?.[1]?.content, "string");
    assert.equal("image_url" in call.payload.messages[1], false);
  }
});
