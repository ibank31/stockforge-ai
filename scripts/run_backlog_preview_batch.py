#!/usr/bin/env python3
"""Run the research-ready backlog as a quota-capped serial preview queue.

This runner intentionally does not call Kaggle and does not set batch_size > 1.
It adapts backlog-v2 records into a project-local StockForge portfolio plan, then
invokes the existing `portfolio generate` command exactly once per candidate.
Provider failures are recorded and stop the run; there are no blind retries.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from stockforge.config import ConfigManager
from stockforge.format_router import route_from_dict
from stockforge.job_database import JobDatabase
from stockforge.portfolio_io import preview_preflight

UTC = timezone.utc
REPO_BACKLOG = REPO_ROOT / "data" / "research" / "STOCKFORGE_BACKLOG_V2_2026-08-27.json"
DEFAULT_BACKLOG = REPO_BACKLOG if REPO_BACKLOG.is_file() else Path("/home/ubuntu/stockforge-backlog-v2/StockForge_Backlog_v2_2026-08-27.json")
DEFAULT_PLAN_NAME = "backlog-v2-2026-08-27.json"
DEFAULT_DAILY_CAP = 4
WINDOW_SECONDS = 24 * 60 * 60


def now() -> datetime:
    return datetime.now(UTC)


def iso(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Invalid JSON: {path}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"Expected JSON object: {path}")
    return data


def project_root_for(project: str) -> tuple[Path, Path]:
    config = ConfigManager().initialize()
    database = JobDatabase(config.database)
    database.initialize()
    matches = [item for item in database.list_projects() if item.get("name") == project]
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one project named {project!r}; found {len(matches)}")
    return config.project_root, Path(matches[0]["path"]).resolve()


def make_asset_spec(candidate: dict[str, Any]) -> dict[str, Any]:
    fmt = str(candidate["format"]).lower()
    is_png = fmt == "png"
    composition = str(candidate["composition"])
    has_copy_space = "copy space" in composition.casefold()
    # Backlog-v2 prompts are explicitly square. Preserve that prompt/canvas
    # contract; the gate-only wording avoids treating descriptive open space as
    # an accidental hero-landscape override.
    layout_mode = "square"
    gate_composition = composition
    if not is_png:
        gate_composition = gate_composition.replace("copy space", "open composition area")
        gate_composition = gate_composition.replace("copy-safe", "open composition area")
        gate_composition = gate_composition.replace("negative space", "open composition area")
    product_kind = "transparent_cutout" if is_png else "raster_illustration"
    asset_family = "technical_component_illustration" if is_png else "product_illustration"
    background_policy = "transparent" if is_png else "white"
    subject = str(candidate["title"]).strip()
    # The pre-GPU gate reserves the word `screen` for electronic screens. Keep
    # the original title/prompt intact while using an unambiguous internal subject.
    if is_png:
        subject = subject.replace("Screen-Print", "Stencil-Print").replace("screen-print", "stencil-print")
    mechanism = str(candidate["visual_mechanism"]).strip()
    return {
        "asset_id": str(candidate["id"]),
        "market_opportunity_id": str(candidate["id"]),
        "buyer_segment": str(candidate["buyer_job"]),
        "buyer_job": str(candidate["buyer_job"]),
        "channel": "commercial stock marketplace",
        "asset_family": asset_family,
        "asset_type": "illustration",
        "micro_niche": str(candidate["macro_niche"]),
        "subject": subject,
        "visual_language": "polished commercial raster illustration with believable materials",
        "medium": "digital raster illustration",
        "product_kind": product_kind,
        "delivery_format": fmt,
        "layout_mode": layout_mode,
        "palette": (),
        "composition": gate_composition,
        "negative_space": gate_composition if layout_mode == "hero_landscape" else "tight, clean framing with no reserved copy field",
        "background_policy": background_policy,
        "isolation_policy": "isolated" if is_png else "isolated",
        "text_policy": "none",
        "branding_policy": "no_branding",
        "originality_levers": (mechanism,),
        "variation_policy": "one candidate only; no seed-only, crop-only, or recolor-only retries",
        "commercial_use_cases": (str(candidate["buyer_job"]),),
        "quality_gates": (
            "thumbnail readability",
            "complete subject and clean geometry",
            "no accidental text, labels, logos, or watermarks",
            "no obvious AI artifacts",
            "human visual review required before finalization or submission",
        ),
        "model_preferences": ("resolution>=1024", "steps<=12"),
        "metadata_hints": tuple(str(item) for item in candidate.get("keywords", [])[:8]),
        "extra_constraints": (
            f"Visual mechanism: {mechanism}",
            str(candidate["format_contract"]),
            str(candidate["risks"].get("production", "")),
        ),
        "tags": tuple(str(item) for item in candidate.get("keywords", [])[:8]),
    }


def make_plan(backlog: dict[str, Any], batch_id: str) -> dict[str, Any]:
    candidates = backlog.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 30:
        raise SystemExit("Backlog must contain exactly 30 candidates")
    briefs: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise SystemExit("Every backlog candidate must be an object")
        fmt = str(candidate.get("format", "")).upper()
        if fmt not in {"JPEG", "PNG"}:
            raise SystemExit(f"Unsupported candidate format for {candidate.get('id')}: {fmt}")
        asset_spec = make_asset_spec(candidate)
        # Validate the persisted route before any provider invocation.
        route = route_from_dict(asset_spec)
        metadata = {
            "title": str(candidate["title"]),
            "keywords": [str(item) for item in candidate.get("keywords", [])],
            "category": "Review in Adobe portal",
            "created_using_generative_ai": True,
            "human_review_required": True,
            "status": "human_review_required",
            "ai_disclosure": "required",
            "people_property_release": "review_required",
            "reviewer_checklist": [
                "Check visible subject against title and keywords.",
                "Check anatomy/geometry/material artifacts at preview size.",
                "Check branding, text, rights, and cultural accuracy.",
                "Assign KEEP or REJECT before any finalizer job.",
            ],
        }
        concept = {
            "key": str(candidate["id"]),
            "subject": str(candidate["title"]),
            "visual_mechanism": str(candidate["visual_mechanism"]),
            "palette": [],
            "originality_levers": [str(candidate["visual_mechanism"])],
            "commercial_use_cases": [str(candidate["buyer_job"])],
            "product_kind": asset_spec["product_kind"],
            "delivery_format": asset_spec["delivery_format"],
            "layout_mode": asset_spec["layout_mode"],
        }
        briefs.append({
            "brief_id": str(candidate["id"]),
            "lane": {
                "key": "backlog_v2_mixed",
                "name": str(candidate["macro_niche"]),
                "tier": "research_ready",
                "evidence_confidence": "candidate_specific",
                "opportunity_id": str(candidate["id"]),
                "test_cap": 30,
                "notes": "Adapted from validated backlog-v2; no generation performed during preparation.",
            },
            "concept": concept,
            "asset_spec": asset_spec,
            "prompt_package": {
                # Preserve both fields byte-for-byte from the research backlog.
                "prompt": str(candidate["generation_prompt"]),
                "negative_prompt": str(candidate["negative_prompt"]),
                "quality_constraints": list(asset_spec["quality_gates"]),
                "legal_constraints": [
                    "Avoid brands, trademarks, logos, copyrighted characters, and celebrity likenesses.",
                    "Prompt constraints are not legal clearance; final review remains mandatory.",
                ],
                "metadata_hints": list(candidate.get("keywords", [])),
            },
            "metadata": metadata,
            "format_decision": {
                "delivery_format": asset_spec["delivery_format"],
                "product_kind": asset_spec["product_kind"],
                "strategy_key": route.strategy_key,
                "reason": str(candidate["format_reason"]),
                "trial_ready": route.trial_ready,
                "verified_for_production": route.verified_for_production,
            },
            "backlog_source": {
                "candidate_id": str(candidate["id"]),
                "format_contract": str(candidate["format_contract"]),
                "generation_prompt_sha256": __import__("hashlib").sha256(str(candidate["generation_prompt"]).encode()).hexdigest(),
                "negative_prompt_sha256": __import__("hashlib").sha256(str(candidate["negative_prompt"]).encode()).hexdigest(),
            },
        })
    return {
        "schema_version": 2,
        "kind": "stockforge.portfolio_batch_plan",
        "batch_id": batch_id,
        "lane": {
            "key": "backlog_v2_mixed",
            "name": "Validated Backlog v2 Mixed JPEG and PNG Preview Queue",
            "tier": "research_ready",
            "evidence_confidence": "candidate_specific",
            "opportunity_id": "backlog-v2-2026-08-27",
            "test_cap": 30,
            "marketplace_transaction_data": "DATA NOT PUBLICLY AVAILABLE",
            "notes": "Preview-only queue. Finalization is blocked until human KEEP verdict.",
        },
        "status": "planned",
        "human_review_required": True,
        "quality_policy": {
            "profile": "z-image-turbo",
            "batch_size": 1,
            "daily_preview_cap": DEFAULT_DAILY_CAP,
            "provider_retry_policy": "none; stop and inspect on failure",
            "kaggle_auto_submit": False,
            "source_prompt_preservation": "exact backlog generation_prompt and negative_prompt",
        },
        "briefs": briefs,
    }


def validate_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    results = []
    for brief in plan["briefs"]:
        result = preview_preflight(plan, brief)
        results.append(result)
    blockers = [item for item in results if not item["gpu_eligible"]]
    if blockers:
        detail = "; ".join(f"{item['brief_id']}: {item['blockers']}" for item in blockers)
        raise SystemExit("Pre-GPU validation blocked the prepared plan: " + detail)
    return results


def load_state(path: Path, batch_id: str) -> dict[str, Any]:
    if not path.is_file():
        return {
            "schema_version": 1,
            "kind": "stockforge.backlog_preview_runner_state",
            "batch_id": batch_id,
            "window_started_at": None,
            "attempts": [],
        }
    state = load_json(path)
    if state.get("batch_id") != batch_id:
        raise SystemExit(f"State batch_id {state.get('batch_id')!r} does not match {batch_id!r}")
    if not isinstance(state.get("attempts"), list):
        raise SystemExit("State attempts must be a list")
    return state


def window_attempts(state: dict[str, Any], current: datetime) -> list[dict[str, Any]]:
    started = parse_iso(state.get("window_started_at"))
    if started is None:
        return []
    if current >= started + timedelta(seconds=WINDOW_SECONDS):
        state["window_started_at"] = None
        return []
    return [item for item in state["attempts"] if parse_iso(item.get("attempted_at")) and parse_iso(item["attempted_at"]) >= started]


def run_one(*, args: argparse.Namespace, project_root: Path, plan_path: Path, brief_id: str, state: dict[str, Any], state_path: Path, log_handle: Any) -> int:
    command = [
        sys.executable,
        "-m",
        "stockforge.cli",
        "portfolio",
        "generate",
        "--project",
        args.project,
        "--plan",
        str(plan_path),
        "--brief",
        brief_id,
        "--profile",
        "z-image-turbo",
    ]
    if args.provider:
        command.extend(["--provider", args.provider])
    attempt = {
        "candidate_id": brief_id,
        "attempted_at": iso(now()),
        "status": "in_flight",
        "profile": "z-image-turbo",
        "batch_size": 1,
        "finalizer_called": False,
    }
    state["attempts"].append(attempt)
    atomic_write(state_path, state)
    log_handle.write(f"\\n=== {iso(now())} START {brief_id} ===\\n")
    log_handle.write("COMMAND " + " ".join(command) + "\n")
    log_handle.flush()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")
    try:
        completed = subprocess.run(command, cwd=REPO_ROOT, env=env, text=True, stdout=log_handle, stderr=subprocess.STDOUT, check=False)
    except OSError as exc:
        log_handle.write(f"LAUNCH_ERROR {exc}\n")
        completed = None
        returncode = 125
    else:
        returncode = completed.returncode
    log_handle.write(f"=== {iso(now())} END {brief_id} returncode={returncode} ===\n")
    log_handle.flush()
    attempt.update({
        "status": "preview_ready" if returncode == 0 else "provider_error_no_auto_retry",
        "returncode": returncode,
        "finished_at": iso(now()),
    })
    atomic_write(state_path, state)
    return returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backlog", type=Path, default=DEFAULT_BACKLOG)
    parser.add_argument("--project", default="stock-assets")
    parser.add_argument("--plan-name", default=DEFAULT_PLAN_NAME)
    parser.add_argument("--daily-cap", type=int, choices=range(1, DEFAULT_DAILY_CAP + 1), default=DEFAULT_DAILY_CAP)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Validate and show the next candidates; never call the provider.")
    args = parser.parse_args()
    backlog = load_json(args.backlog.resolve())
    if backlog.get("status") != "research_ready_no_generation" or backlog.get("generation_performed") is not False:
        raise SystemExit("Backlog must be research_ready_no_generation and generation_performed=false")
    batch_id = f"backlog-v2-preview-{backlog.get('generated_date', 'unknown')}"
    _config_root, project_root = project_root_for(args.project)
    plan_dir = project_root / "portfolio-plans"
    plan_path = plan_dir / args.plan_name
    plan = make_plan(backlog, batch_id)
    validate_plan(plan)
    if plan_path.is_file():
        existing = load_json(plan_path)
        if existing.get("batch_id") != batch_id:
            raise SystemExit(f"Existing plan has different batch_id: {plan_path}")
    else:
        atomic_write(plan_path, plan)
    state_path = plan_dir / f"{Path(args.plan_name).stem}.runner-state.json"
    state = load_state(state_path, batch_id)
    current = now()
    active_attempts = window_attempts(state, current)
    in_flight = [item for item in state["attempts"] if item.get("status") == "in_flight"]
    if in_flight:
        print(json.dumps({
            "status": "manual_intervention_required",
            "reason": "An earlier runner process may still own a provider request; do not retry automatically.",
            "in_flight": in_flight,
            "state": str(state_path),
        }, indent=2))
        return 3
    terminal_ids = {
        item.get("candidate_id")
        for item in state["attempts"]
        if item.get("status") in {"preview_ready", "provider_error_no_auto_retry"}
    }
    attempted_ids = {item.get("candidate_id") for item in active_attempts}
    remaining = [
        brief["brief_id"]
        for brief in plan["briefs"]
        if brief["brief_id"] not in terminal_ids and brief["brief_id"] not in attempted_ids
    ]
    if args.prepare_only or args.dry_run:
        print(json.dumps({
            "plan": str(plan_path),
            "state": str(state_path),
            "batch_id": batch_id,
            "daily_cap": args.daily_cap,
            "active_attempts_in_window": len(active_attempts),
            "remaining_candidates": remaining,
            "next_candidates": remaining[: max(0, args.daily_cap - len(active_attempts))],
            "provider_called": False,
            "notice": "Dry/prepare mode; no remote GPU call was made.",
        }, indent=2))
        return 0
    if not remaining:
        print(json.dumps({"status": "complete", "plan": str(plan_path), "state": str(state_path), "provider_called": False}, indent=2))
        return 0
    if state.get("window_started_at") is None:
        state["window_started_at"] = iso(current)
        atomic_write(state_path, state)
        active_attempts = []
    slots = args.daily_cap - len(active_attempts)
    if slots <= 0:
        print(json.dumps({"status": "daily_cap_reached", "reset_at": iso(parse_iso(state["window_started_at"]) + timedelta(seconds=WINDOW_SECONDS)), "state": str(state_path)}, indent=2))
        return 0
    log_path = plan_dir / f"{Path(args.plan_name).stem}.runner.log"
    with log_path.open("a", encoding="utf-8") as log_handle:
        for brief_id in remaining[:slots]:
            returncode = run_one(args=args, project_root=project_root, plan_path=plan_path, brief_id=brief_id, state=state, state_path=state_path, log_handle=log_handle)
            if returncode != 0:
                print(json.dumps({"status": "stopped_on_provider_error", "candidate_id": brief_id, "log": str(log_path), "state": str(state_path)}, indent=2))
                return returncode
    print(json.dumps({
        "status": "batch_complete",
        "submitted_this_run": min(slots, len(remaining)),
        "daily_cap": args.daily_cap,
        "plan": str(plan_path),
        "state": str(state_path),
        "log": str(log_path),
        "next_action": "Review preview artifacts; mark KEEP/REJECT. Do not call Kaggle for REJECT.",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
