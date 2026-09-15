import test from "node:test";
import assert from "node:assert/strict";
import { analyzeReferenceAssetV2 } from "../frontend/lib/reference-analysis-v2.js";

const localization = {
  reference_type: "RAW_ASSET",
  confidence: 0.96,
  asset_candidates: [{ label: "camera", confidence: 0.95, bbox_normalized: { x: 0.1, y: 0.2, width: 0.6, height: 0.5 } }],
  primary_asset: { label: "camera", confidence: 0.95, bbox_normalized: { x: 0.1, y: 0.2, width: 0.6, height: 0.5 } },
};

const dna = {
  asset_type: "photo_object",
  primary_subject: "camera",
  subject_count: "one",
  morphology: "compact rectangular body with lens",
  structure: "body, lens, controls",
  orientation: "three-quarter front view",
  visual_style: "clean commercial product photography",
  line_style: "none",
  shading: "soft studio shading",
  material: "metal and plastic",
  colors: ["black", "silver"],
  distinctive_features: ["central lens", "control dial"],
  asset_function: ["product catalog", "technology marketing"],
  confidence: 0.94,
};

function opportunity(i) {
  const changes = ["silhouette", "details", "viewpoint", "composition"];
  return {
    id: `opp_${i}`,
    title: `Camera stock concept ${i}`,
    anchor_subject: "camera",
    subject: `camera treatment ${i}`,
    composition: `commercial composition ${i} with negative space`,
    viewpoint: `distinct viewpoint ${i}`,
    color_direction: `palette ${i}`,
    context: `technology marketing context ${i}`,
    use_case: `buyer use case ${i}`,
    mutation_recipe: { silhouette: "changed", details: "changed", quantity: "single", viewpoint: "changed", composition: "changed", material: "changed", palette: "changed" },
    differences: changes,
    relevance_score: 0.9,
    similarity_risk: 0.2,
    genericity_risk: 0.2,
    ip_risk: 0,
    commercial_score: 0.8,
    why_fit: "Keeps the camera family while creating a materially different commercial stock treatment.",
  };
}

test("reference analysis accepts object-shaped Workers AI responses and produces five opportunities", async () => {
  let calls = 0;
  const env = {
    AI: {
      async run(model, input) {
        calls += 1;
        assert.equal(model, "@cf/google/gemma-4-26b-a4b-it");
        assert.match(input.image, /^data:image\/webp;base64,/);
        if (calls === 1) return { response: localization };
        if (calls === 2) return { response: dna };
        return { response: { asset_opportunities: [1, 2, 3, 4, 5].map(opportunity) } };
      },
    },
  };
  const result = await analyzeReferenceAssetV2(env, Uint8Array.from([1, 2, 3]).buffer, "image/webp");
  assert.equal(result.stage, "REFERENCE_ANALYSIS_V2");
  assert.equal(result.asset_dna.primary_subject, "camera");
  assert.equal(result.asset_opportunities.length, 5);
  assert.equal(calls, 3);
});
