import json

import pytest
from typer.testing import CliRunner

from stockforge.cli import app
from stockforge.portfolio import PortfolioError, build_brief, lane_for, list_lanes, plan_batch


runner = CliRunner()


def test_all_priority_lanes_build_a_safe_seed_brief():
    lanes = list_lanes()

    assert len(lanes) == 10
    assert {lane.tier for lane in lanes} == {"first", "secondary", "experimental"}
    for lane in lanes:
        brief = build_brief(lane.key, lane.concepts[0].key)

        assert brief.asset_spec.market_opportunity_id == lane.opportunity_id
        assert brief.asset_spec.background_policy == "white"
        assert brief.asset_spec.isolation_policy == "isolated"
        assert brief.asset_spec.text_policy == "none"
        assert brief.metadata.created_using_generative_ai is True
        assert brief.metadata.status == "human_review_required"
        assert brief.metadata.human_review_required is True
        assert brief.metadata.marketplace_transaction_data == "DATA NOT PUBLICLY AVAILABLE"
        assert "readable text" in brief.prompt_package.negative_prompt
        assert "human review" in " ".join(brief.asset_spec.quality_gates).lower()


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
