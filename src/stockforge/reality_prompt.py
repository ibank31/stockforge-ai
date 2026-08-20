"""Compile validated RealityScene objects into conservative visual prompts."""
from __future__ import annotations
from .reality import RealityScene, compile_reality_constraints, reality_preflight

def compile_reality_prompt(scene: RealityScene) -> str:
    result = reality_preflight(scene)
    if not result.passed:
        raise ValueError("Reality preflight failed: " + ", ".join(result.errors))
    constraints = compile_reality_constraints(scene)
    lines = [
        "photorealistic professional stock photography",
        f"{scene.domain} professional scene",
        f"task: {scene.task}",
        f"problem/context: {scene.problem}",
        f"target object: {scene.object}",
        f"tool: {scene.tool}",
        f"physical action: {scene.human_action}",
        f"tool affordance: {scene.affordance.human_action}",
        f"environment: {scene.environment}",
        f"commercial buyer job: {scene.buyer_job}",
        "observable evidence: " + "; ".join(scene.visual_evidence),
        "reality constraints: " + "; ".join(constraints),
        "natural anatomy, credible hand placement, physically plausible equipment placement, realistic materials, restrained professional styling",
        "no logos or visible brand identity unless explicitly required",
    ]
    return ". ".join(p for p in lines if p.strip()) + "."
