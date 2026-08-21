from stockforge.knowledge import load_construction_v1


def test_legacy_knowledge_pack_hydrates_affordance_tool():
    workflows = load_construction_v1()
    assert workflows
    assert all(scene.affordance.tool == scene.tool for scene in workflows)
