"""Pre-generation trial authorization without calling a provider."""

from __future__ import annotations

from dataclasses import dataclass, asdict

from .asset_selector import AssetTypePolicy, select_asset_type


class TrialGateError(ValueError):
    """Raised when a trial request is incomplete."""


@dataclass(frozen=True, slots=True)
class TrialReadiness:
    asset_type: str
    delivery_format: str
    readiness: str
    hypothesis: str
    purpose: str
    single_candidate_only: bool
    trial_allowed: bool
    provider_call_allowed: bool
    blockers: tuple[str, ...]
    next_step: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        return data


def _text(value: str, field: str, *, minimum: int = 12, maximum: int = 500) -> str:
    clean = value.strip()
    if len(clean) < minimum:
        raise TrialGateError(f"{field} must contain at least {minimum} characters.")
    if len(clean) > maximum:
        raise TrialGateError(f"{field} must not exceed {maximum} characters.")
    return clean


def assess_trial_readiness(*, asset_type: str, hypothesis: str, purpose: str) -> TrialReadiness:
    """Return a conservative authorization state; this function never runs work."""
    policy: AssetTypePolicy = select_asset_type(asset_type)
    hypothesis_text = _text(hypothesis, "hypothesis", minimum=20)
    purpose_text = _text(purpose, "purpose")
    blockers = list(policy.blockers)
    if policy.readiness == "BLOCKED":
        status = "BLOCKED"
        trial_allowed = False
        provider_allowed = False
        next_step = policy.next_step
    elif policy.readiness == "REVIEW_REQUIRED":
        status = "REVIEW_REQUIRED"
        trial_allowed = False
        provider_allowed = False
        next_step = policy.next_step
    else:
        status = "READY_FOR_TRIAL"
        trial_allowed = True
        provider_allowed = policy.execution_mode != "local_native_vector_build"
        next_step = (
            "Build exactly one local candidate only after the human confirms this hypothesis and the selected brief preflight passes."
            if not provider_allowed
            else "Run exactly one remote candidate only after the human confirms this hypothesis and the selected brief preflight passes."
        )
    return TrialReadiness(
        asset_type=policy.key,
        delivery_format=policy.delivery_format,
        readiness=status,
        hypothesis=hypothesis_text,
        purpose=purpose_text,
        single_candidate_only=True,
        trial_allowed=trial_allowed,
        provider_call_allowed=provider_allowed,
        blockers=tuple(blockers),
        next_step=next_step,
    )
