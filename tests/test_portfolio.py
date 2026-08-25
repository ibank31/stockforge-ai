import json

import pytest
from typer.testing import CliRunner

from stockforge.cli import app
from stockforge.portfolio import PortfolioError, build_brief, lane_for, list_lanes, plan_batch
from stockforge.portfolio_io import jpeg_metadata_preflight, preview_preflight, recommended_canvas


runner = CliRunner()


def test_all_priority_lanes_build_a_safe_seed_brief():
    lanes = list_lanes()

    assert len(lanes) == 17
    assert {lane.tier for lane in lanes} == {"first", "secondary", "experimental"}
    for lane in lanes:
        brief = build_brief(lane.key, lane.concepts[0].key)

        assert brief.asset_spec.market_opportunity_id == lane.opportunity_id
        assert brief.asset_spec.background_policy in {"white", "transparent"}
        if lane.key == "native_vector_utility_sets":
            assert brief.asset_spec.isolation_policy == "cluster"
        else:
            assert brief.asset_spec.isolation_policy == "isolated"
        assert brief.asset_spec.delivery_format in {"jpeg", "png", "svg"}
        assert brief.asset_spec.text_policy == "none"
        assert brief.metadata.created_using_generative_ai is True
        assert brief.metadata.status == "human_review_required"
        assert brief.metadata.human_review_required is True
        assert brief.metadata.marketplace_transaction_data == "DATA NOT PUBLICLY AVAILABLE"
        assert "readable text" in brief.prompt_package.negative_prompt
        assert "human review" in " ".join(brief.asset_spec.quality_gates).lower()


def test_technical_mechanical_component_lane_is_one_candidate_jpeg_with_specific_identity():
    brief = build_brief("technical_mechanical_component_illustrations", "rotor-armature")

    assert brief.brief_id == "technical_mechanical_component_illustrations--rotor-armature"
    assert brief.asset_spec.delivery_format == "jpeg"
    assert brief.asset_spec.product_kind == "raster_illustration"
    assert brief.asset_spec.isolation_policy == "isolated"
    assert "electromechanical" in brief.asset_spec.micro_niche
    assert "axial" in brief.asset_spec.identity_signature.lower()
    assert "dimension" in brief.prompt_package.negative_prompt.lower()
    assert brief.metadata.created_using_generative_ai is True
    assert brief.metadata.human_review_required is True


def test_seed_starting_tray_lane_is_one_candidate_isolated_jpeg_with_horticultural_identity():
    brief = build_brief("seed_starting_tray_propagation", "seed-tray")

    assert brief.brief_id == "seed_starting_tray_propagation--seed-tray"
    assert brief.asset_spec.delivery_format == "jpeg"
    assert brief.asset_spec.product_kind == "raster_illustration"
    assert brief.asset_spec.layout_mode == "square"
    assert brief.asset_spec.background_policy == "white"
    assert brief.asset_spec.isolation_policy == "isolated"
    assert "seed-starting tray" in brief.asset_spec.micro_niche
    assert "propagation tray" in brief.asset_spec.identity_signature
    assert "brand seed packet" in brief.prompt_package.negative_prompt
    assert brief.metadata.title == "Indoor Seed-Starting Tray with Emerging Seedlings"
    assert brief.metadata.created_using_generative_ai is True
    assert brief.metadata.human_review_required is True


def test_pet_enrichment_lane_is_one_candidate_isolated_jpeg_with_pet_care_identity():
    brief = build_brief("pet_enrichment_object_illustrations", "puzzle-feeder")

    assert brief.brief_id == "pet_enrichment_object_illustrations--puzzle-feeder"
    assert brief.asset_spec.delivery_format == "jpeg"
    assert brief.asset_spec.product_kind == "raster_illustration"
    assert brief.asset_spec.layout_mode == "square"
    assert brief.asset_spec.background_policy == "white"
    assert brief.asset_spec.isolation_policy == "isolated"
    assert "puzzle feeder" in brief.asset_spec.micro_niche
    assert "treat-puzzle" in brief.asset_spec.identity_signature
    assert "animal face" in brief.prompt_package.negative_prompt
    assert "readable text" in brief.prompt_package.negative_prompt
    assert brief.metadata.title == "Interactive Treat Puzzle Feeder for Pet Enrichment"
    assert brief.metadata.created_using_generative_ai is True
    assert brief.metadata.human_review_required is True


def test_sewing_craft_clipart_lane_is_one_candidate_isolated_jpeg_with_tool_set_identity():
    brief = build_brief("sewing_craft_tool_clipart", "beginner-kit")

    assert brief.brief_id == "sewing_craft_tool_clipart--beginner-kit"
    assert brief.asset_spec.delivery_format == "jpeg"
    assert brief.asset_spec.product_kind == "raster_illustration"
    assert brief.asset_spec.layout_mode == "square"
    assert brief.asset_spec.background_policy == "white"
    assert brief.asset_spec.isolation_policy == "isolated"
    assert "sewing" in brief.asset_spec.micro_niche
    assert "sewing and textile-craft tools" in brief.asset_spec.identity_signature
    assert "Adobe logo" in brief.prompt_package.negative_prompt
    assert "human hand" in brief.prompt_package.negative_prompt
    assert "readable text" in brief.prompt_package.negative_prompt
    assert brief.metadata.title == "Colorful Beginner Sewing and Textile Craft Tool Set"
    assert brief.metadata.created_using_generative_ai is True
    assert brief.metadata.human_review_required is True


def test_explicit_layout_mode_selects_hero_landscape_while_other_products_stay_square():
    directional = build_brief("tactile_material_atmospheres", "fiber-arch").to_dict()
    square = build_brief("ai_governance", "review-gate").to_dict()

    assert recommended_canvas(directional) == "hero-landscape"
    assert recommended_canvas(square) == "square"

    # Copy-space words cannot override an explicit square product contract.
    square["asset_spec"]["composition"] = "object on the left with copy space right"
    square["asset_spec"]["negative_space"] = "large clean copy space on the right"
    assert recommended_canvas(square) == "square"


def test_jpeg_metadata_preflight_projects_existing_terms_without_upload_or_category_guess():
    brief = build_brief("tactile_material_atmospheres", "fiber-arch").to_dict()
    plan = {"lane": brief["lane"], "briefs": [brief]}

    report = jpeg_metadata_preflight(plan, brief, category="Graphic Resources")

    assert report["delivery_format"] == "jpeg"
    assert report["upload_performed"] is False
    assert set(report["canonical_keywords"]) == set(brief["metadata"]["keywords"])
    assert len(report["canonical_keywords"]) == len(brief["metadata"]["keywords"])
    assert report["platform_reports"]["adobe_stock"]["valid"] is True
    assert report["platform_reports"]["shutterstock"]["valid"] is True
    assert report["platform_reports"]["creative_market"]["valid"] is False
    assert any("at most 10" in error for error in report["platform_reports"]["creative_market"]["errors"])
    assert report["platform_reports"]["etsy"]["valid"] is False
    assert any("at least 13" in error for error in report["platform_reports"]["etsy"]["errors"])


def test_priority_lane_seeds_only_send_verified_raster_products_to_gpu():
    for lane in list_lanes():
        brief = build_brief(lane.key, lane.concepts[0].key).to_dict()
        report = preview_preflight({"lane": brief["lane"], "briefs": [brief]}, brief)

        assert report["recommended_canvas"] in {"square", "hero-landscape", "vector-artboard"}
        if lane.key == "human_made_collage_elements":
            assert report["gpu_eligible"] is False
            assert any("alpha producer" in blocker for blocker in report["blockers"])
        elif lane.key in {"native_vector_elements", "native_vector_patterns", "native_vector_utility_sets"}:
            assert report["gpu_eligible"] is False
            assert any("local native-vector" in blocker for blocker in report["blockers"])
        else:
            assert report["gpu_eligible"] is True, (lane.key, report["blockers"])
            assert all(item["status"] == "pass" for item in report["checks"])


def test_plan_rejects_count_larger_than_registered_distinct_concepts():
    lane = lane_for("ai_governance")

    with pytest.raises(PortfolioError, match="materially distinct seed concepts"):
        plan_batch(lane.key, len(lane.concepts) + 1)


def test_plan_rejects_count_above_lane_test_cap():
    lane = lane_for("human_made_collage_elements")

    with pytest.raises(PortfolioError, match="initial test cap"):
        plan_batch(lane.key, lane.test_cap + 1)


def test_portfolio_plan_cli_outputs_ai_disclosure_and_no_remote_call():
    result = runner.invoke(
        app,
        ["portfolio", "plan", "--lane", "tactile_material_atmospheres", "--count", "2"],
    )

    assert result.exit_code == 0, result.output
    output = json.loads(result.output)
    assert output["status"] == "planned"
    assert output["human_review_required"] is True
    assert len(output["briefs"]) == 2
    assert output["briefs"][0]["metadata"]["created_using_generative_ai"] is True
    assert "remote" not in output


def test_portfolio_metadata_preflight_cli_is_report_only(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / "home"))

    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0
    created = runner.invoke(
        app,
        ["portfolio", "create-batch", "--project", "demo", "--lane", "tactile_material_atmospheres", "--count", "1"],
    )
    assert created.exit_code == 0, created.output
    batch = json.loads(created.output)

    result = runner.invoke(
        app,
        [
            "portfolio", "metadata-preflight", "--project", "demo",
            "--plan", batch["path"], "--brief", batch["brief_ids"][0],
            "--category", "Graphic Resources",
        ],
    )

    assert result.exit_code == 0, result.output
    report = json.loads(result.output)
    assert report["upload_performed"] is False
    assert report["platform_reports"]["adobe_stock"]["valid"] is True
    assert "provider" not in result.output.lower()


def test_portfolio_create_and_list_batch_in_project(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("STOCKFORGE_HOME", str(tmp_path / "home"))

    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["project", "create", "demo"]).exit_code == 0

    created = runner.invoke(
        app,
        [
            "portfolio", "create-batch", "--project", "demo",
            "--lane", "ai_governance", "--count", "2",
        ],
    )

    assert created.exit_code == 0, created.output
    created_output = json.loads(created.output)
    assert created_output["status"] == "planned"
    assert len(created_output["brief_ids"]) == 2

    listed = runner.invoke(app, ["portfolio", "list", "--project", "demo", "--json"])
    assert listed.exit_code == 0, listed.output
    plans = json.loads(listed.output)
    assert len(plans) == 1
    assert plans[0]["lane"] == "ai_governance"
    assert plans[0]["brief_count"] == 2
