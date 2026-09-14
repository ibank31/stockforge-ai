from pathlib import Path
from PIL import Image

from stockforge.creative_opportunity import build_creative_opportunity
from stockforge.generation_brief import build_generation_brief
from stockforge.generation_integration import execute_generation
from stockforge.reference_intelligence import CreativeDistancePlan, profile_reference_image


class FakeTransport:
    def __init__(self): self.calls = []
    def generate(self, prompt, *, negative_prompt, parameters):
        self.calls.append((prompt, negative_prompt, parameters))
        return "/tmp/generated.png"


def test_generation_integration_preserves_v2_traceability(tmp_path: Path):
    source = tmp_path / "ref.png"
    Image.new("RGB", (24, 24), "white").save(source)
    profile = profile_reference_image(source, subject="old vase")
    opportunity = build_creative_opportunity(
        profile, opportunity_id="run-001", market_intent="home decor",
        proposed_subject="modern ceramic planter", proposed_composition="offset hero composition",
        proposed_viewpoint="high three-quarter angle", proposed_color_direction="muted terracotta",
        proposed_context="minimal interior shelf", proposed_use_case="editorial",
        differentiation_rationale=("new subject", "new context", "new composition"),
        creative_distance=CreativeDistancePlan(),
    )
    brief = build_generation_brief(profile, opportunity)
    transport = FakeTransport()
    result = execute_generation(brief, model_id="z-image-turbo", transport=transport)
    assert result.artifact_path == "/tmp/generated.png"
    assert transport.calls[0][2]["stockforge_v2_brief_id"] == "run-001"
    assert transport.calls[0][2]["stockforge_v2_reference_sha256"] == profile.visual.sha256
