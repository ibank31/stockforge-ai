"""Prepare manual Adobe Stock Contributor upload folders without submitting them."""

from __future__ import annotations

import html
import json
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .adobe_gate import inspect_image
from .database import Database
from .metadata_policy import NONVISUAL_METADATA_KEYWORDS


class AdobeUploadBundleError(RuntimeError):
    """Raised when a selected master cannot safely enter an Adobe upload folder."""


# Values follow Adobe's published category numbering. A lane without a clear
# category must require an explicit user-reviewed category rather than guess.
ADOBE_CATEGORY_BY_LANE = {
    "tactile_material_atmospheres": 8,  # Graphic resources
    "playful_surreal_product_metaphors": 8,  # Graphic resources
    "technical_mechanical_component_illustrations": 10,  # Industry
}

CSV_HEADER = ("Filename", "Title", "Keywords", "Category", "Releases")
MAX_FILENAME_CHARS = 30
MAX_TITLE_CHARS = 70
MAX_KEYWORDS = 49
MANUAL_FILE_TYPE = "MANUAL_REVIEW_REQUIRED"

# These phrases describe workflow, buyer use, or the generation method rather
# than visible subject matter.  They must never be embedded in an Adobe upload
# JPEG, even if they appeared in an earlier portfolio draft.
NONVISUAL_UPLOAD_KEYWORDS = NONVISUAL_METADATA_KEYWORDS


@dataclass(frozen=True, slots=True)
class AdobeUploadBundle:
    """A batch root containing one Android-friendly folder per final asset."""

    path: Path
    asset_dirs: tuple[Path, ...]
    metadata_path: Path
    manifest_path: Path
    artifact_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "asset_dirs": [str(item) for item in self.asset_dirs],
            "metadata_path": str(self.metadata_path),
            "manifest_path": str(self.manifest_path),
            "artifact_ids": list(self.artifact_ids),
            "status": "manual_portal_upload_prepared_not_submitted",
        }


def _safe_filename(artifact_id: str) -> str:
    name = f"sf-{artifact_id[:8]}.jpg"
    if len(name) > MAX_FILENAME_CHARS:
        raise AdobeUploadBundleError("Generated Adobe filename exceeds the portal limit.")
    return name


def _asset_dir_name(artifact_id: str) -> str:
    return f"asset-{artifact_id[:8]}"


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
    removed = [item for item in normalized if item.casefold() in NONVISUAL_UPLOAD_KEYWORDS]
    upload_keywords = [item for item in normalized if item.casefold() not in NONVISUAL_UPLOAD_KEYWORDS]
    if len({item.casefold() for item in upload_keywords}) != len(upload_keywords):
        raise AdobeUploadBundleError("Reviewed visual metadata contains duplicate Adobe keywords.")
    if len(upload_keywords) < 5:
        raise AdobeUploadBundleError("Visual upload metadata needs at least five retained keywords.")
    if not metadata.get("created_using_generative_ai"):
        raise AdobeUploadBundleError("This workflow accepts only masters truthfully marked as Generative AI.")
    if not metadata.get("human_review_required"):
        raise AdobeUploadBundleError("A human-review marker is required before preparing an upload folder.")
    return {
        **metadata,
        "title": title.strip(),
        "keywords": upload_keywords,
        "removed_nonvisual_keywords": removed,
    }


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


def _xmp_packet(title: str, keywords: list[str]) -> bytes:
    """Build a compact standards-based XMP packet that Adobe apps can read."""
    subject = "".join(f"<rdf:li>{html.escape(keyword)}</rdf:li>" for keyword in keywords)
    safe_title = html.escape(title)
    payload = (
        '<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        '<rdf:Description rdf:about="" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" '
        'xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/" '
        'xmlns:xmp="http://ns.adobe.com/xap/1.0/">\n'
        f'<dc:title><rdf:Alt><rdf:li xml:lang="x-default">{safe_title}</rdf:li></rdf:Alt></dc:title>\n'
        f'<dc:description><rdf:Alt><rdf:li xml:lang="x-default">{safe_title}</rdf:li></rdf:Alt></dc:description>\n'
        f'<dc:subject><rdf:Bag>{subject}</rdf:Bag></dc:subject>\n'
        '<photoshop:Credit>StockForge AI</photoshop:Credit>\n'
        '<xmp:CreatorTool>StockForge AI</xmp:CreatorTool>\n'
        '</rdf:Description>\n</rdf:RDF>\n</x:xmpmeta>\n'
        '<?xpacket end="w"?>'
    )
    return payload.encode("utf-8")


def _embed_xmp_metadata(jpeg_path: Path, *, title: str, keywords: list[str]) -> None:
    """Insert XMP in an APP1 JPEG segment without re-encoding image pixels."""
    original = jpeg_path.read_bytes()
    if not original.startswith(b"\xff\xd8"):
        raise AdobeUploadBundleError("Cannot embed metadata: upload copy is not a JPEG.")
    xmp = b"http://ns.adobe.com/xap/1.0/\x00" + _xmp_packet(title, keywords)
    segment_length = len(xmp) + 2
    if segment_length > 0xFFFF:
        raise AdobeUploadBundleError("Embedded upload metadata exceeds JPEG APP1 capacity.")
    app1 = b"\xff\xe1" + segment_length.to_bytes(2, "big") + xmp
    jpeg_path.write_bytes(original[:2] + app1 + original[2:])


def _write_asset_metadata_folder(asset_dir: Path, record: dict[str, Any]) -> Path:
    """Write a click-open metadata summary beside a JPEG with embedded XMP."""
    metadata_path = asset_dir / "UPLOAD_METADATA.txt"
    metadata_path.write_text(
        "STOCKFORGE — ADOBE STOCK UPLOAD METADATA\n"
        "==========================================\n\n"
        f"JPEG TO UPLOAD: {record['filename']}\n\n"
        "GOOD NEWS\n"
        "Title and keywords are embedded in this JPEG as XMP metadata.\n"
        "Upload the JPEG only; do not use a CSV on Android.\n\n"
        f"TITLE\n{record['title']}\n\n"
        f"CATEGORY\n{record['category']} — verify the closest accurate Adobe category\n\n"
        "KEYWORDS EMBEDDED IN JPEG\n"
        f"{', '.join(record['keywords'])}\n\n"
        "PORTAL SETTINGS (MANUAL — VERIFY IN ADOBE)\n"
        f"- File type: {record['adobe_file_type']}\n"
        f"- Category: {record['category']} — verify against the visual\n\n"
        "REQUIRED PORTAL DECLARATIONS\n"
        "- Created using generative AI tools: YES\n"
        "- Confirm people/property declaration truthfully from the visual review.\n\n"
        "ANDROID / ADOBE STEPS\n"
        "1. In Adobe Browse, choose the JPEG above from this folder.\n"
        "2. Verify Adobe has read the embedded title and keywords.\n"
        "3. Select the accurate Adobe file type and category for the visual; do not assume either value.\n"
        "4. Review declarations, Terms and Conditions, and CAPTCHA yourself before submit.\n",
        encoding="utf-8",
    )
    return metadata_path


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
    """Build manual per-asset upload folders; this function never uploads or submits."""
    root = Path(project_root).resolve()
    if not execution_ids:
        raise AdobeUploadBundleError("Select at least one finalized-master execution.")
    if len(set(execution_ids)) != len(execution_ids):
        raise AdobeUploadBundleError("Each selected master execution must be unique.")
    if not approved_by_user:
        raise AdobeUploadBundleError("Pass explicit user approval after visual review before preparing upload files.")

    output_root = Path(destination_root).resolve() if destination_root is not None else root / "adobe-upload-bundles"
    bundle_root = output_root / _bundle_name(execution_ids)
    bundle_root.mkdir(parents=True, exist_ok=False)
    records: list[dict[str, Any]] = []
    asset_dirs: list[Path] = []

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
            raise AdobeUploadBundleError("Adobe upload folder requires a local JPEG master.")
        technical = inspect_image(source).to_dict()
        if not technical.get("ready"):
            raise AdobeUploadBundleError("Master did not pass the local Adobe technical gate.")
        portfolio = execution.parameters.get("portfolio")
        if not isinstance(portfolio, dict):
            raise AdobeUploadBundleError("Finalized master has no portfolio lineage.")
        metadata = _validated_metadata(portfolio.get("metadata"))
        adobe_category = _category_for(portfolio, category)
        filename = _safe_filename(artifact.id)
        asset_dir = bundle_root / _asset_dir_name(artifact.id)
        asset_dir.mkdir()
        upload_copy = asset_dir / filename
        shutil.copy2(source, upload_copy)
        record = {
            "artifact_id": artifact.id,
            "execution_id": execution.id,
            "source_file": artifact.relative_path,
            "folder": asset_dir.name,
            "filename": filename,
            "title": metadata["title"],
            "keywords": metadata["keywords"],
            "category": adobe_category,
            "adobe_file_type": MANUAL_FILE_TYPE,
            "technical_gate": technical,
            "generative_ai_declaration_required": True,
            "removed_nonvisual_keywords": metadata["removed_nonvisual_keywords"],
            "fictional_people_or_property_declaration_required": False,
            "reviewer_checklist": metadata.get("reviewer_checklist", []),
        }
        _embed_xmp_metadata(upload_copy, title=record["title"], keywords=record["keywords"])
        embedded_technical = inspect_image(upload_copy).to_dict()
        if not embedded_technical.get("ready"):
            raise AdobeUploadBundleError("JPEG with embedded upload metadata did not pass the Adobe technical gate.")
        record["technical_gate"] = embedded_technical
        _write_asset_metadata_folder(asset_dir, record)
        records.append(record)
        asset_dirs.append(asset_dir)

    manifest = {
        "schema_version": 3,
        "kind": "stockforge.adobe_android_manual_upload_bundle",
        "status": "manual_portal_upload_prepared_not_submitted",
        "created_at": datetime.now(UTC).isoformat(),
        "marketplace": "adobe_stock_contributor",
        "approved_by_user": True,
        "submission_requires_explicit_portal_confirmation": True,
        "files": records,
        "folder_contract": "Each asset folder contains one JPEG upload master with embedded XMP metadata and UPLOAD_METADATA.txt.",
        "portal_steps": [
            "In Adobe Browse, open an asset folder and select its JPEG only.",
            "Verify Adobe reads the embedded title and keywords; set the reviewed category if Adobe leaves it blank.",
            "Review the final portal metadata and complete declarations, Terms and Conditions, and CAPTCHA personally.",
        ],
    }
    manifest_path = bundle_root / "BATCH_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (bundle_root / "README.txt").write_text(
        "STOCKFORGE ADOBE ANDROID UPLOAD BATCH\n\n"
        "Open one asset-* folder at a time. Each contains exactly one final JPEG\n"
        "with embedded XMP metadata and a click-open UPLOAD_METADATA.txt guide.\n"
        "Choose the JPEG in Adobe Browse; no CSV is required on Android.\n"
        "Do not submit until you have completed Adobe declarations, Terms, and CAPTCHA.\n",
        encoding="utf-8",
    )
    return AdobeUploadBundle(
        path=bundle_root,
        asset_dirs=tuple(asset_dirs),
        metadata_path=asset_dirs[0] / "UPLOAD_METADATA.txt",
        manifest_path=manifest_path,
        artifact_ids=tuple(record["artifact_id"] for record in records),
    )
