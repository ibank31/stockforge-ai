"""Conservative generation feedback planner.

Turns persisted deterministic critique observations into explicit constraints for
the next generation. It does not claim semantic, aesthetic, legal, originality,
or marketplace knowledge and never auto-approves an asset.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .learning_loop import AutoCritique, load_memory

_FAILURE_DIRECTIVES = {
    "sharpness": "Increase edge clarity and avoid motion blur or soft-focus rendering.",
    "saturation": "Reduce extreme saturation and preserve commercially neutral color relationships.",
    "brightness": "Rebalance exposure and preserve readable highlight and shadow detail.",
    "contrast": "Avoid crushed shadows and clipped highlights.",
}


@dataclass(frozen=True, slots=True)
class FeedbackPlan:
    critique_id: str
    decision: str
    regenerate: bool
    prompt_constraints: tuple[str, ...]
    recurring_failures: tuple[str, ...]
    unresolved_limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_feedback_plan(critique: AutoCritique, *, project_root: str | None = None) -> FeedbackPlan:
    constraints: list[str] = []
    failures: list[str] = []
    for signal in critique.signals:
        if signal.status == "FAIL":
            failures.append(signal.name)
            constraints.append(_FAILURE_DIRECTIVES.get(
                signal.name.casefold(),
                f"Correct deterministic technical failure: {signal.name}. {signal.reason}",
            ))
        elif signal.status == "REVIEW":
            constraints.append(f"Review-sensitive technical constraint: {signal.name}. {signal.reason}")

    recurring: list[str] = []
    if project_root:
        memory = load_memory(project_root)
        for record in memory.get("records", {}).values():
            if not isinstance(record, dict):
                continue
            if record.get("lane_key") != critique.lane_key:
                continue
            for name, count in record.get("technical_failures", {}).items():
                if isinstance(count, int) and count >= 2:
                    recurring.append(f"{name} repeated {count} times; prioritize prevention before another generation.")

    if not constraints:
        constraints.append(
            "No deterministic technical failure was observed; change concept or composition only through an explicit human-reviewed hypothesis."
        )
    constraints.extend([
        "Do not treat this feedback as semantic, aesthetic, originality, legal, or marketplace approval.",
        "Do not regenerate as a seed-only, crop-only, or color-only variation.",
    ])
    return FeedbackPlan(
        critique_id=critique.critique_id,
        decision=critique.decision,
        regenerate=critique.decision == "FAIL_TECHNICAL",
        prompt_constraints=tuple(dict.fromkeys(constraints)),
        recurring_failures=tuple(dict.fromkeys(recurring)),
        unresolved_limitations=critique.limitations,
    )
