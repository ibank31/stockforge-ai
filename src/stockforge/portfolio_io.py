"""Safe project-local portfolio plan loading and brief selection."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class PortfolioPlanError(ValueError):
    """Raised when a persisted portfolio plan cannot safely drive generation."""


# Lane-specific terms whose positive use makes an isolated asset too likely to
# resemble a real device or a familiar branded/product silhouette.  The checks
# are intentionally local and deterministic: a failed gate costs no GPU time.
_LANE_BLOCKED_SUBJECT_TERMS: dict[str, tuple[str, ...]] = {
    "retro_tech_developer_metaphors": (
        "audio cassette",
        "cassette",
        "tape reel",
        "reel",
        "floppy",
        "diskette",
        "keyboard",
        "monitor",
        "terminal",
        "computer",
        "device",
        "hardware",
        "screen",
    ),
}


def _project_plan_directory(project_root: Path) -> Path:
    return (Path(project_root).resolve() / "portfolio-plans").resolve()


def resolve_project_plan(project_root: Path, plan_path: str | Path) -> Path:
    """Resolve a plan path and ensure it is a JSON file inside the project plan directory."""
    root = Path(project_root).resolve()
    directory = _project_plan_directory(root)
    candidate = Path(plan_path).expanduser()
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        candidate.relative_to(directory)
    except ValueError as exc:
        raise PortfolioPlanError("Portfolio plan must be stored inside this project's portfolio-plans directory.") from exc
    if candidate.suffix.lower() != ".json":
        raise PortfolioPlanError("Portfolio plan must be a JSON file.")
    if not candidate.is_file():
        raise PortfolioPlanError(f"Portfolio plan file not found: {candidate}")
    return candidate


def load_project_plan(project_root: Path, plan_path: str | Path) -> tuple[Path, dict[str, Any]]:
    """Load and validate a persisted project-local portfolio batch plan."""
    path = resolve_project_plan(project_root, plan_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PortfolioPlanError(f"Portfolio plan is not valid JSON: {path}") from exc
    if not isinstance(data, dict) or data.get("kind") != "stockforge.portfolio_batch_plan":
        raise PortfolioPlanError("File is not a StockForge portfolio batch plan.")
    if data.get("status") != "planned":
        raise PortfolioPlanError("Only portfolio plans in planned status can start a new generation.")
    if not isinstance(data.get("batch_id"), str) or not data["batch_id"].strip():
        raise PortfolioPlanError("Portfolio plan has no batch_id.")
    lane = data.get("lane")
    briefs = data.get("briefs")
    if not isinstance(lane, dict) or not isinstance(lane.get("key"), str) or not lane["key"].strip():
        raise PortfolioPlanError("Portfolio plan has no valid lane key.")
    if not isinstance(briefs, list) or not briefs:
        raise PortfolioPlanError("Portfolio plan has no briefs.")
    return path, data


def select_brief(plan: dict[str, Any], brief_id: str) -> dict[str, Any]:
    """Select one unique, policy-complete brief from a validated plan."""
    requested = str(brief_id).strip()
    if not requested:
        raise PortfolioPlanError("A portfolio brief ID is required.")
    matches = [item for item in plan["briefs"] if isinstance(item, dict) and item.get("brief_id") == requested]
    if len(matches) != 1:
        raise PortfolioPlanError(f"Portfolio brief not found or duplicated: {requested}")
    brief = matches[0]
    prompt_package = brief.get("prompt_package")
    metadata = brief.get("metadata")
    if not isinstance(prompt_package, dict) or not isinstance(prompt_package.get("prompt"), str) or not prompt_package["prompt"].strip():
        raise PortfolioPlanError("Portfolio brief has no valid generation prompt.")
    if not isinstance(metadata, dict):
        raise PortfolioPlanError("Portfolio brief has no metadata draft.")
    if metadata.get("created_using_generative_ai") is not True:
        raise PortfolioPlanError("Portfolio brief must declare generative-AI creation.")
    if metadata.get("human_review_required") is not True or metadata.get("status") != "human_review_required":
        raise PortfolioPlanError("Portfolio brief must require human review before submission.")
    if not isinstance(metadata.get("title"), str) or not metadata["title"].strip():
        raise PortfolioPlanError("Portfolio brief metadata requires an accurate title draft.")
    if not isinstance(metadata.get("keywords"), list) or not metadata["keywords"]:
        raise PortfolioPlanError("Portfolio brief metadata requires keyword candidates.")
    return brief


def preview_preflight(plan: dict[str, Any], brief: dict[str, Any]) -> dict[str, Any]:
    """Return a local, deterministic decision before a portfolio brief may use GPU.

    This is deliberately a conservative gate.  It rejects known lane conflicts,
    contradictory subject wording, and briefs whose isolation/copy-space contract
    cannot be checked from the persisted plan.  It is not a substitute for the
    post-generation human visual review.
    """
    lane = plan.get("lane")
    asset_spec = brief.get("asset_spec")
    concept = brief.get("concept")
    if not isinstance(lane, dict) or not isinstance(asset_spec, dict) or not isinstance(concept, dict):
        raise PortfolioPlanError("Portfolio brief lacks the structure required for the local pre-GPU gate.")

    lane_key = str(lane.get("key", "")).strip()
    subject = str(asset_spec.get("subject", "")).strip()
    composition = str(asset_spec.get("composition", "")).strip()
    negative_space = str(asset_spec.get("negative_space", "")).strip()
    blockers: list[str] = []
    checks: list[dict[str, str]] = []

    required_policies = {
        "background_policy": "white",
        "isolation_policy": "isolated",
        "text_policy": "none",
        "branding_policy": "no_branding",
    }
    wrong_policies = [
        f"{field} must be {expected!r}"
        for field, expected in required_policies.items()
        if asset_spec.get(field) != expected
    ]
    if wrong_policies:
        blockers.extend(wrong_policies)
    checks.append({
        "name": "standalone-policy",
        "status": "pass" if not wrong_policies else "fail",
        "detail": "All standalone policies are explicit." if not wrong_policies else "; ".join(wrong_policies),
    })

    lower_subject = subject.casefold()
    forbidden = [
        term for term in _LANE_BLOCKED_SUBJECT_TERMS.get(lane_key, ())
        if re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", lower_subject)
    ]
    if forbidden:
        blockers.append(
            "subject conflicts with the lane's no-real-device rule: " + ", ".join(forbidden)
        )
    checks.append({
        "name": "lane-subject-risk",
        "status": "pass" if not forbidden else "fail",
        "detail": "No blocked real-device silhouette term is present." if not forbidden else ", ".join(forbidden),
    })

    lower_composition = f"{composition} {negative_space}".casefold()
    has_copy_space = "copy space" in lower_composition
    has_position = bool(re.search(r"\b(left|right|above|upper|lower)\b", lower_composition))
    if not has_copy_space or not has_position:
        blockers.append("composition must specify copy space and a directional placement")
    checks.append({
        "name": "composition-contract",
        "status": "pass" if has_copy_space and has_position else "fail",
        "detail": "Copy space and placement are explicit." if has_copy_space and has_position else "Missing directional copy-space contract.",
    })

    # "Holding" causes the model to stack a second subject on top unless the
    # containment relation is constrained in the same brief.  Reject it rather
    # than spending a retry on an ambiguous two-object composition.
    ambiguous_holding = "holding" in lower_subject and not any(
        term in lower_subject for term in ("inside", "contained", "within", "cutout", "opening")
    )
    if ambiguous_holding:
        blockers.append("subject uses ambiguous 'holding' instead of an explicit containment or cutout relation")
    checks.append({
        "name": "spatial-contract",
        "status": "pass" if not ambiguous_holding else "fail",
        "detail": "No ambiguous two-object holding relation." if not ambiguous_holding else "Use inside, contained, or cutout/opening instead of holding.",
    })

    if not subject:
        blockers.append("subject is required")
    if not str(concept.get("visual_mechanism", "")).strip():
        blockers.append("visual mechanism is required")

    return {
        "version": 1,
        "gpu_eligible": not blockers,
        "lane_key": lane_key,
        "brief_id": brief.get("brief_id"),
        "checks": checks,
        "blockers": blockers,
        "notice": "Local pre-GPU decision only; human visual review remains required after generation.",
    }


def portfolio_snapshot(plan: dict[str, Any], brief: dict[str, Any], plan_path: Path) -> dict[str, Any]:
    """Return the minimal immutable portfolio context persisted with one execution."""
    lane = plan["lane"]
    metadata = brief["metadata"]
    return {
        "schema_version": 1,
        "batch_id": plan["batch_id"],
        "plan_file": plan_path.name,
        "brief_id": brief["brief_id"],
        "lane_key": lane["key"],
        "lane_name": lane.get("name", lane["key"]),
        "tier": lane.get("tier", "experimental"),
        "evidence_confidence": lane.get("evidence_confidence", "low"),
        "metadata": metadata,
        "reviewer_checklist": metadata.get("reviewer_checklist", []),
        "human_review_required": True,
    }
