from pathlib import Path

from PIL import Image, ImageDraw

from stockforge.reference_to_concept import build_reference_concept_plan


def _payload():
    return {
        "marketplace": "adobe_stock",
        "query": "sustainable packaging metaphor",
        "demand_score": 82,
        "growth_score": 76,
        "saturation_score": 38,
        "buyer_fit_score": 84,
        "visual_differentiation_score": 79,
        "variation_score": 72,
        "commercial_clarity_score": 86,
        "asset_family": "surreal_concept",
        "asset_type": "illustration",
        "evidence": [{
            "source": "manual_research",
            "url": "https://example.invalid/research",
            "observed_at": "2026-09-13T00:00:00Z",
            "signal": "supply proxy",
            "value": "candidate niche",
            "confidence": "medium",
        }],
    }


def _reference(path: Path):
    image = Image.new("RGB", (160, 100), "white")
    ImageDraw.Draw(image).rectangle((10, 10, 80, 80), fill=(10, 80, 160))
    image.save(path)


def test_reference_pipeline_combines_market_and_reference_constraints(tmp_path: Path):
    path = tmp_path / "reference.png"
    _reference(path)
    plan = build_reference_concept_plan(_payload(), path)

    assert plan.reference.orientation == "landscape"
    assert plan.assets
    asset = plan.assets[0]
    assert asset.asset_spec.layout_mode == "portrait"
    assert "Reference-derived differentiation contract:" in asset.asset_spec.extra_constraints
    assert "reference-derived lighting change" in asset.asset_spec.originality_levers
    assert "Change the primary light direction" in asset.prompt_package.prompt


def test_reference_pipeline_allows_explicit_target_layout(tmp_path: Path):
    path = tmp_path / "reference.png"
    _reference(path)
    plan = build_reference_concept_plan(_payload(), path, target_layout="square")
    assert all(asset.asset_spec.layout_mode == "square" for asset in plan.assets)
