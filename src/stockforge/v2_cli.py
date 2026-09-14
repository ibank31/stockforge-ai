"""StockForge V2 command surface.

These commands expose the active Reference Intelligence → Creative Opportunity
→ Generation Plan bridge without pretending that semantic vision is automatic.
They produce a reviewable plan; provider execution remains a separate explicit step.
"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from .auto_crop import AutoCropError, CropBox, crop_reference, suggest_crop_candidates
from .creative_opportunity import CreativeOpportunityError, build_creative_opportunity
from .reference_intelligence import CreativeDistancePlan, ReferenceIntelligenceError, profile_reference_image
from .v2_pipeline import V2PipelineError, build_v2_generation_plan

app = typer.Typer(help="StockForge V2 reference intelligence and creative planning.")


def _json(value: object) -> None:
    typer.echo(json.dumps(value, indent=2, ensure_ascii=False))


@app.command("autocrop")
def autocrop(
    reference: Path = typer.Option(..., "--reference", exists=True, readable=True),
    limit: int = typer.Option(5, "--limit", min=1, max=10),
) -> None:
    """Suggest visually distinct crop regions from a screenshot; human confirmation is required."""
    try:
        candidates = suggest_crop_candidates(reference, limit=limit)
    except AutoCropError as exc:
        raise typer.BadParameter(str(exc)) from exc
    _json({
        "reference": str(reference.resolve()),
        "decision": "REVIEW_REQUIRED",
        "candidates": [candidate.to_dict() for candidate in candidates],
        "notice": "Auto-crop is a visual heuristic, not semantic object detection. Confirm or adjust before analysis.",
    })


@app.command("crop")
def crop(
    reference: Path = typer.Option(..., "--reference", exists=True, readable=True),
    destination: Path = typer.Option(..., "--output"),
    left: int = typer.Option(..., "--left", min=0),
    top: int = typer.Option(..., "--top", min=0),
    right: int = typer.Option(..., "--right", min=1),
    bottom: int = typer.Option(..., "--bottom", min=1),
) -> None:
    """Apply one human-confirmed crop while preserving the original screenshot."""
    try:
        output = crop_reference(reference, destination, CropBox(left, top, right, bottom))
    except AutoCropError as exc:
        raise typer.BadParameter(str(exc)) from exc
    _json({
        "reference": str(reference.resolve()),
        "crop": CropBox(left, top, right, bottom).to_dict(),
        "output": str(output),
        "decision": "CROP_CONFIRMED",
    })



@app.command("profile")
def profile(
    reference: Path = typer.Option(..., "--reference", exists=True, readable=True),
    subject: str | None = typer.Option(None, "--subject"),
    category: str | None = typer.Option(None, "--category"),
    commercial_intent: str | None = typer.Option(None, "--commercial-intent"),
    buyer_relevance: str | None = typer.Option(None, "--buyer-relevance"),
) -> None:
    """Inspect a reference safely and return measurable facts plus explicit semantics."""
    try:
        result = profile_reference_image(
            reference,
            subject=subject,
            category=category,
            commercial_intent=commercial_intent,
            buyer_relevance=buyer_relevance,
        )
    except ReferenceIntelligenceError as exc:
        raise typer.BadParameter(str(exc)) from exc
    _json(result.to_dict())


@app.command("plan")
def plan(
    reference: Path = typer.Option(..., "--reference", exists=True, readable=True),
    opportunity_id: str = typer.Option(..., "--opportunity-id"),
    market_intent: str = typer.Option(..., "--market-intent"),
    proposed_subject: str = typer.Option(..., "--proposed-subject"),
    proposed_composition: str = typer.Option(..., "--proposed-composition"),
    proposed_viewpoint: str = typer.Option(..., "--proposed-viewpoint"),
    proposed_color_direction: str = typer.Option(..., "--proposed-color-direction"),
    proposed_context: str = typer.Option(..., "--proposed-context"),
    proposed_use_case: str = typer.Option(..., "--proposed-use-case"),
    differentiation: list[str] = typer.Option(..., "--differentiate"),
    subject: str | None = typer.Option(None, "--subject"),
    category: str | None = typer.Option(None, "--category"),
    commercial_intent: str | None = typer.Option(None, "--commercial-intent"),
    buyer_relevance: str | None = typer.Option(None, "--buyer-relevance"),
    change_subject: bool = typer.Option(True, "--change-subject/--keep-subject"),
    change_composition: bool = typer.Option(True, "--change-composition/--keep-composition"),
    change_viewpoint: bool = typer.Option(True, "--change-viewpoint/--keep-viewpoint"),
    change_color_direction: bool = typer.Option(True, "--change-color-direction/--keep-color-direction"),
    change_context: bool = typer.Option(True, "--change-context/--keep-context"),
    change_use_case: bool = typer.Option(True, "--change-use-case/--keep-use-case"),
) -> None:
    """Build a reviewable anti-similarity generation plan from one reference."""
    try:
        profile_result = profile_reference_image(
            reference,
            subject=subject,
            category=category,
            commercial_intent=commercial_intent,
            buyer_relevance=buyer_relevance,
        )
        distance = CreativeDistancePlan(
            change_subject=change_subject,
            change_composition=change_composition,
            change_viewpoint=change_viewpoint,
            change_color_direction=change_color_direction,
            change_context=change_context,
            change_use_case=change_use_case,
        )
        opportunity = build_creative_opportunity(
            profile_result,
            opportunity_id=opportunity_id,
            market_intent=market_intent,
            proposed_subject=proposed_subject,
            proposed_composition=proposed_composition,
            proposed_viewpoint=proposed_viewpoint,
            proposed_color_direction=proposed_color_direction,
            proposed_context=proposed_context,
            proposed_use_case=proposed_use_case,
            differentiation_rationale=tuple(differentiation),
            creative_distance=distance,
        )
        generation_plan = build_v2_generation_plan(profile_result, opportunity)
    except (ReferenceIntelligenceError, CreativeOpportunityError, V2PipelineError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    _json(generation_plan.to_dict())


@app.command("generate")
def generate(
    project: str = typer.Option(..., "--project", "-p"),
    reference: Path = typer.Option(..., "--reference", exists=True, readable=True),
    opportunity_id: str = typer.Option(..., "--opportunity-id"),
    market_intent: str = typer.Option(..., "--market-intent"),
    proposed_subject: str = typer.Option(..., "--proposed-subject"),
    proposed_composition: str = typer.Option(..., "--proposed-composition"),
    proposed_viewpoint: str = typer.Option(..., "--proposed-viewpoint"),
    proposed_color_direction: str = typer.Option(..., "--proposed-color-direction"),
    proposed_context: str = typer.Option(..., "--proposed-context"),
    proposed_use_case: str = typer.Option(..., "--proposed-use-case"),
    differentiation: list[str] = typer.Option(..., "--differentiate"),
    provider: str | None = typer.Option(None, "--provider"),
    profile_name: str = typer.Option("z-image-turbo", "--profile"),
    canvas: str = typer.Option("square", "--canvas"),
    seed: int | None = typer.Option(None, "--seed"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    subject: str | None = typer.Option(None, "--subject"),
    category: str | None = typer.Option(None, "--category"),
    commercial_intent: str | None = typer.Option(None, "--commercial-intent"),
    buyer_relevance: str | None = typer.Option(None, "--buyer-relevance"),
) -> None:
    """Generate through the existing durable job queue from a V2 anti-similarity plan."""
    try:
        profile_result = profile_reference_image(reference, subject=subject, category=category, commercial_intent=commercial_intent, buyer_relevance=buyer_relevance)
        opportunity = build_creative_opportunity(profile_result, opportunity_id=opportunity_id, market_intent=market_intent, proposed_subject=proposed_subject, proposed_composition=proposed_composition, proposed_viewpoint=proposed_viewpoint, proposed_color_direction=proposed_color_direction, proposed_context=proposed_context, proposed_use_case=proposed_use_case, differentiation_rationale=tuple(differentiation))
        generation_plan = build_v2_generation_plan(profile_result, opportunity)
        from .cli import _run_one_generation
        result = _run_one_generation(project=project, prompt=generation_plan.prompt, negative_prompt=generation_plan.negative_prompt, provider=provider, profile=profile_name, seed=seed, canvas=canvas, dry_run=dry_run, portfolio_context={"v2": generation_plan.to_dict(), "lane_key": "v2_reference_intelligence", "buyer_job": opportunity.market_intent, "brief_id": opportunity.opportunity_id, "asset_spec": generation_plan.asset_spec.to_dict(), "metadata": {"title": opportunity.proposed_subject}})
    except (ReferenceIntelligenceError, CreativeOpportunityError, V2PipelineError, ValueError) as exc:
        raise typer.BadParameter(str(exc)) from exc
    _json({"plan": generation_plan.to_dict(), "generation": result})
