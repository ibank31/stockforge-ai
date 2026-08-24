"""Safe project-local portfolio plan loading and brief selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PortfolioPlanError(ValueError):
    """Raised when a persisted portfolio plan cannot safely drive generation."""


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
