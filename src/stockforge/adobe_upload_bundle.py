"""Prepare official-schema Adobe Stock Contributor upload batches without submitting them."""

from __future__ import annotations

import csv
import json
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .adobe_gate import inspect_image
from .database import Database


class AdobeUploadBundleError(RuntimeError):
    """Raised when a selected master cannot safely enter an Adobe upload batch."""


# Values follow Adobe's published category numbering.  A lane without a clear
# category must require an explicit user-reviewed category rather than guess.
ADOBE_CATEGORY_BY_LANE = {
    "tactile_material_atmospheres": 8,  # Graphic resources
    "playful_surreal_product_metaphors": 8,  # Graphic resources
}

CSV_HEADER = ("Filename", "Title", "Keywords", "Category", "Releases")
MAX_FILENAME_CHARS = 30
MAX_TITLE_CHARS = 70
MAX_KEYWORDS = 50


@dataclass(frozen=True, slots=True)
class AdobeUploadBundle:
    """Manual-upload publication folder plus a separate metadata reference folder."""

    path: Path
    image_dir: Path
    reference_dir: Path
    csv_path: Path
    manifest_path: Path
    artifact_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "image_dir": str(self.image_dir),
            "reference_dir": str(self.reference_dir),
            "csv_path": str(self.csv_path),
            "manifest_path": str(self.manifest_path),
            "artifact_ids": list(self.artifact_ids),
            "status": "manual_portal_upload_prepared_not_submitted",
        }


def _safe_filename(artifact_id: str) -> str:
    name = f"sf-{artifact_id[:8]}.jpg"
    if len(name) > MAX_FILENAME_CHARS:
        raise AdobeUploadBundleError("Generated Adobe filename exceeds the portal limit.")
    return name


def _validated_metadata(metadata: object) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise AdobeUploadBundleError("Master has no reviewed portfolio metadata.")
    title = metadata.get("title")
    keywords = metadata.get("keywords")
    if not isinstance(title, str) or not title.strip():
        raise AdobeUploadBundleError("Reviewed metadata title is required.")
    if len(title) > MAX_TITLE_CHARS:
        raise AdobeUploadBundleError("Reviewed metadata title exceeds Adobe's 70-character limit.")
    if "," in title:
        raise AdobeUploadBundleError("Reviewed metadata title contains a comma and is not CSV-safe for Adobe.")
    if not isinstance(keywords, list) or not keywords or not all(isinstance(item, str) and item.strip() for item in keywords):
        raise AdobeUploadBundleError("Reviewed metadata requires a non-empty keyword list.")
    if len(keywords) > MAX_KEYWORDS:
        raise AdobeUploadBundleError("Reviewed metadata exceeds Adobe's 50-keyword limit.")
    normalized = [item.strip() for item in keywords]
    if len({item.casefold() for item in normalized}) != len(normalized):
        raise AdobeUploadBundleError("Reviewed metadata contains duplicate Adobe keywords.")
    if not metadata.get("created_using_generative_ai"):
        raise AdobeUploadBundleError("This workflow accepts only masters truthfully marked as Generative AI.")
    if not metadata.get("human_review_required"):
        raise AdobeUploadBundleError("A human-review marker is required before preparing an upload batch.")
    return {**metadata, "title": title.strip(), "keywords": normalized}


def _category_for(portfolio: dict[str, Any], explicit_category: int | None) -> int:
    if explicit_category is not None:
        if not 1 <= explicit_category <= 21:
            raise AdobeUploadBundleError("Adobe category must be a number from 1 to 21.")
        return explicit_category
    lane_key = portfolio.get("lane_key")
    if not isinstance(lane_key, str) or lane_key not in ADOBE_CATEGORY_BY_LANE:
        raise AdobeUploadBundleError(
            "This portfolio lane has no safe automatic Adobe category; pass an explicitly reviewed category."
        )
    return ADOBE_CATEGORY_BY_LANE[lane_key]


def _bundle_name(execution_ids: tuple[str, ...]) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    seed = "-".join(item[:8] for item in execution_ids)
    return f"adobe-{stamp}-{seed}"


def latest_finalized_master_execution_id(*, database: Database, project_id: str) -> str:
    """Return the newest registered finalized-master execution for a project."""
    for artifact in database.list_artifacts(project_id):
        if artifact.kind != "finalized-master":
            continue
        for provenance in database.list_provenance(artifact_id=artifact.id):
            if provenance.operation != "image.upscale_and_finalize" or not provenance.execution_id:
                continue
            execution = database.get_execution(provenance.execution_id)
            if execution and execution.project_id == project_id and execution.operation == "image.finalize_master" and execution.state == "succeeded":
                return execution.id
    raise AdobeUploadBundleError("No finalized master is available for this project.")


def prepare_adobe_upload_bundle(
    *,
    database: Database,
    project_id: str,
    project_root: Path,
    execution_ids: tuple[str, ...],
    approved_by_user: bool,
    category: int | None = None,
    destination_root: Path | None = None,
) -> AdobeUploadBundle:
    """Build a portal-ready Adobe upload folder; this function never uploads or submits."""
    root = Path(project_root).resolve()
    if not execution_ids:
        raise AdobeUploadBundleError("Select at least one finalized-master execution.")
    if len(set(execution_ids)) != len(execution_ids):
        raise AdobeUploadBundleError("Each selected master execution must be unique.")
    if not approved_by_user:
        raise AdobeUploadBundleError("Pass explicit user approval after visual review before preparing upload files.")

    # The Android-ready folder is intentionally JPEG-only.  Metadata, CSV, and
    # audit records are written next to it in METADATA_REFERENCE so a mobile
    # file picker cannot accidentally select a non-upload document.
    output_root = Path(destination_root).resolve() if destination_root is not None else root / "adobe-upload-bundles"
    bundle_name = _bundle_name(execution_ids)
    bundle_root = output_root / bundle_name
    image_dir = bundle_root
    reference_dir = output_root.parent / "METADATA_REFERENCE" / bundle_name
    image_dir.mkdir(parents=True, exist_ok=False)
    reference_dir.mkdir(parents=True, exist_ok=False)
    records: list[dict[str, Any]] = []

    for execution_id in execution_ids:
        execution = database.get_execution(execution_id)
        if execution is None or execution.project_id != project_id:
            raise AdobeUploadBundleError(f"Master execution not found in project: {execution_id}")
        if execution.state != "succeeded" or execution.operation != "image.finalize_master":
            raise AdobeUploadBundleError(f"Execution is not a succeeded finalized master: {execution_id}")
        if len(execution.artifact_ids) != 1:
            raise AdobeUploadBundleError("Each finalized master execution must contain exactly one master artifact.")
        artifact = database.get_artifact(execution.artifact_ids[0])
        if artifact is None or artifact.project_id != project_id or artifact.kind != "finalized-master":
            raise AdobeUploadBundleError("Finalized master artifact is missing or invalid.")
        source = (root / artifact.relative_path).resolve()
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise AdobeUploadBundleError("Master path escapes the project workspace.") from exc
        if not source.is_file() or source.suffix.lower() not in {".jpg", ".jpeg"}:
            raise AdobeUploadBundleError("Adobe upload bundle requires a local JPEG master.")
        technical = inspect_image(source).to_dict()
        if not technical.get("ready"):
            raise AdobeUploadBundleError("Master did not pass the local Adobe technical gate.")
        portfolio = execution.parameters.get("portfolio")
        if not isinstance(portfolio, dict):
            raise AdobeUploadBundleError("Finalized master has no portfolio lineage.")
        metadata = _validated_metadata(portfolio.get("metadata"))
        adobe_category = _category_for(portfolio, category)
        filename = _safe_filename(artifact.id)
        destination = image_dir / filename
        shutil.copy2(source, destination)
        records.append({
            "artifact_id": artifact.id,
            "execution_id": execution.id,
            "source_file": artifact.relative_path,
            "filename": filename,
            "title": metadata["title"],
            "keywords": metadata["keywords"],
            "category": adobe_category,
            "technical_gate": technical,
            "generative_ai_declaration_required": True,
            "fictional_people_or_property_declaration_required": False,
            "reviewer_checklist": metadata.get("reviewer_checklist", []),
        })

    csv_path = reference_dir / "adobe_metadata.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(CSV_HEADER)
        for record in records:
            writer.writerow([
                record["filename"],
                record["title"],
                ", ".join(record["keywords"]),
                record["category"],
                "",
            ])

    manifest = {
        "schema_version": 2,
        "kind": "stockforge.adobe_manual_upload_bundle",
        "status": "manual_portal_upload_prepared_not_submitted",
        "created_at": datetime.now(UTC).isoformat(),
        "marketplace": "adobe_stock_contributor",
        "approved_by_user": True,
        "submission_requires_explicit_portal_confirmation": True,
        "ready_to_upload_dir": str(bundle_root),
        "metadata_reference_dir": str(reference_dir),
        "files": records,
        "portal_steps": [
            "Open Adobe Contributor Portal > Uploaded Files.",
            "Use Browse to select only JPEG files from READY_TO_UPLOAD.",
            "For each uploaded JPEG, copy the reviewed title, keywords, and category from UPLOAD_REFERENCE.md.",
            "Truthfully mark Created using generative AI tools and the fictional people/property declaration where applicable.",
            "Review the final batch, complete Adobe Terms and Conditions yourself, and explicitly submit only after approval.",
        ],
    }
    manifest_path = reference_dir / "UPLOAD_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    reference_path = reference_dir / "UPLOAD_REFERENCE.md"
    reference_lines = [
        "# Adobe Stock — Metadata Reference (Do Not Upload)",
        "",
        "This folder is deliberately separate from `READY_TO_UPLOAD`. Select JPEGs only from the ready folder in Adobe's Browse dialog.",
        "",
    ]
    for index, record in enumerate(records, start=1):
        reference_lines.extend([
            f"## {index}. {record['filename']}",
            "",
            f"- **Title:** {record['title']}",
            f"- **Category:** {record['category']} (Graphic Resources)",
            f"- **Keywords:** {', '.join(record['keywords'])}",
            "- **Required declaration:** Created using generative AI tools.",
            "- **Required review:** Confirm no visible IP, people, or real recognizable property before submission.",
            "",
        ])
    reference_path.write_text("\n".join(reference_lines), encoding="utf-8")
    checklist_path = reference_dir / "PORTAL_STEPS.md"
    checklist_path.write_text(
        "# Adobe Contributor — Manual Android Steps\n\n"
        "1. In **Uploaded Files**, select **Browse** and choose JPEG files only from `READY_TO_UPLOAD`.\n"
        "2. Use `UPLOAD_REFERENCE.md` in this metadata folder to enter each reviewed title, keyword list, and category.\n"
        "3. Mark **Created using generative AI tools** truthfully and complete any applicable people/property declaration.\n"
        "4. Complete Adobe's Terms and Conditions yourself, then press **Submit** only if you approve the batch.\n",
        encoding="utf-8",
    )
    return AdobeUploadBundle(
        path=bundle_root,
        image_dir=image_dir,
        reference_dir=reference_dir,
        csv_path=csv_path,
        manifest_path=manifest_path,
        artifact_ids=tuple(record["artifact_id"] for record in records),
    )
