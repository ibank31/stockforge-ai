from stockforge.knowledge import get_construction_task, load_construction_v1
from stockforge.reality import RealityScene, ToolAffordance, reality_preflight
from stockforge.reality_prompt import compile_reality_prompt

def test_construction_pack_has_ten_workflows():
    workflows = load_construction_v1()
    assert len(workflows) == 10
    assert all(x.rules.must for x in workflows)
    assert all(x.rules.must_not for x in workflows)

def test_moisture_meter_requires_wall_relationship():
    scene = get_construction_task("construction.wall_moisture_inspection")
    assert reality_preflight(scene).passed
    assert "meter-to-wall relationship is explicit" in scene.rules.must

def test_bad_affordance_rejected_before_gpu():
    scene = RealityScene(
        domain="construction", task="measure room", problem="document dimensions", object="wall", tool="laser distance meter",
        affordance=ToolAffordance("laser distance meter", "measure distance", "ceiling", False, "aimed", "aim at ceiling"),
        human_action="measure room", environment="room", buyer_job="show measurement workflow")
    result = reality_preflight(scene)
    assert not result.passed
    assert "affordance_target_must_match_scene_object" in result.errors

def test_prompt_contains_physical_action_and_negative_rules():
    prompt = compile_reality_prompt(get_construction_task("construction.room_dimensional_measurement"))
    assert "aim the laser distance meter toward the opposite wall" in prompt
    assert "do not show laser pointed at person" in prompt
