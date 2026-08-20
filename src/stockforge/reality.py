"""Domain-neutral reality contracts and deterministic preflight rules."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class ToolAffordance:
    tool: str
    purpose: str
    target: str
    contact_required: bool = False
    orientation: str = "task-appropriate"
    human_action: str = "use tool on target"
    evidence: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class RealityRules:
    must: tuple[str, ...] = ()
    should: tuple[str, ...] = ()
    must_not: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class RealityScene:
    domain: str
    task: str
    problem: str
    object: str
    tool: str
    affordance: ToolAffordance
    human_action: str
    environment: str
    buyer_job: str
    rules: RealityRules = field(default_factory=RealityRules)
    visual_evidence: tuple[str, ...] = ()

@dataclass(frozen=True, slots=True)
class PreflightResult:
    passed: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

def reality_preflight(scene: RealityScene) -> PreflightResult:
    errors: list[str] = []
    warnings: list[str] = []
    required = {
        "domain": scene.domain, "task": scene.task, "problem": scene.problem,
        "object": scene.object, "tool": scene.tool, "human_action": scene.human_action,
        "environment": scene.environment, "buyer_job": scene.buyer_job,
        "affordance.purpose": scene.affordance.purpose,
        "affordance.target": scene.affordance.target,
        "affordance.human_action": scene.affordance.human_action,
    }
    for name, value in required.items():
        if not str(value).strip():
            errors.append(f"missing:{name}")
    if scene.affordance.target.strip().lower() != scene.object.strip().lower():
        errors.append("affordance_target_must_match_scene_object")
    if scene.affordance.contact_required and "contact" not in scene.affordance.human_action.lower():
        warnings.append("contact_required_but_action_does_not_explicitly_describe_contact")
    if not scene.visual_evidence:
        warnings.append("no_visual_evidence_declared")
    if not scene.rules.must:
        warnings.append("no_must_rules_declared")
    if not scene.rules.must_not:
        warnings.append("no_must_not_rules_declared")
    return PreflightResult(not errors, tuple(errors), tuple(warnings))

def compile_reality_constraints(scene: RealityScene) -> tuple[str, ...]:
    result: list[str] = []
    result.extend(f"must show {item}" for item in scene.rules.must)
    result.extend(f"prefer {item}" for item in scene.rules.should)
    result.extend(f"do not show {item}" for item in scene.rules.must_not)
    result.extend(f"physically show {scene.affordance.human_action}")
    result.extend(f"tool interacts with {scene.affordance.target}")
    result.extend(scene.visual_evidence)
    return tuple(result)
