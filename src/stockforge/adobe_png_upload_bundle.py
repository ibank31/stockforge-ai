"""Prepare Adobe-oriented manual upload folders for transparent PNG masters."""

from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .adobe_png_gate import inspect_transparent_png
from .adobe_upload_bundle import ADOBE_CATEGORY_BY_LANE, MANUAL_FILE_TYPE, MAX_FILENAME_CHARS, MAX_KEYWORDS, MAX_TITLE_CHARS, NONVISUAL_UPLOAD_KEYWORDS
from .database import Database
from .png_metadata import embed_png_metadata


class AdobePngUploadBundleError(ValueError):
    """Raised when a PNG master cannot safely enter the upload folder."""


def _metadata(portfolio: dict[str, Any]) -> dict[str, Any]:
    value = portfolio.get("metadata")
    if not isinstance(value, dict):
        raise AdobePngUploadBundleError("PNG master has no reviewed portfolio metadata.")
    title = value.get("title")
    keywords = value.get("keywords")
    if not isinstance(title, str) or not title.strip() or len(title) > MAX_TITLE_CHARS or "," in title:
        raise AdobePngUploadBundleError("PNG title is required, comma-free, and must be at most 70 characters.")
    if not isinstance(keywords, list) or not 5 <= len(keywords) <= MAX_KEYWORDS or not all(isinstance(k, str) and k.strip() for k in keywords):
        raise AdobePngUploadBundleError("PNG upload metadata requires 5-49 non-empty keywords.")
    clean = [k.strip() for k in keywords if k.strip() and k.casefold() not in NONVISUAL_UPLOAD_KEYWORDS]
    if len({k.casefold() for k in clean}) != len(clean):
        raise AdobePngUploadBundleError("PNG visual keywords must be unique.")
    if not value.get("created_using_generative_ai") or not value.get("human_review_required"):
        raise AdobePngUploadBundleError("PNG metadata must truthfully declare generative AI and human review.")
    return {"title": title.strip(), "keywords": clean, "reviewer_checklist": value.get("reviewer_checklist", [])}


def prepare_adobe_png_upload_bundle(*, database: Database, project_id: str, project_root: Path, execution_ids: tuple[str, ...], approved_by_user: bool, category: int | None = None, destination_root: Path | None = None) -> dict[str, Any]:
    if not execution_ids:
        raise AdobePngUploadBundleError("Select at least one finalized PNG execution.")
    if not approved_by_user:
        raise AdobePngUploadBundleError("PNG upload preparation requires explicit approval after 100% visual review.")
    root = Path(project_root).resolve()
    output_root = (Path(destination_root).resolve() if destination_root else root / "adobe-png-upload-bundles")
    bundle = output_root / f"adobe-png-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}"
    bundle.mkdir(parents=True, exist_ok=False)
    records: list[dict[str, Any]] = []
    asset_dirs: list[Path] = []
    try:
        for execution_id in execution_ids:
            execution = database.get_execution(execution_id)
            if execution is None or execution.project_id != project_id or execution.state != "succeeded" or execution.operation != "image.finalize_master" or len(execution.artifact_ids) != 1:
                raise AdobePngUploadBundleError(f"Invalid finalized PNG execution: {execution_id}")
            artifact = database.get_artifact(execution.artifact_ids[0])
            if artifact is None or artifact.project_id != project_id or artifact.kind != "finalized-master":
                raise AdobePngUploadBundleError("Finalized PNG artifact is missing or invalid.")
            source = (root / artifact.relative_path).resolve()
            source.relative_to(root)
            if source.suffix.casefold() != ".png":
                raise AdobePngUploadBundleError("PNG bundle accepts PNG masters only.")
            technical = inspect_transparent_png(source)
            if not technical.ready:
                raise AdobePngUploadBundleError("PNG master failed the true-alpha/sRGB technical gate.")
            portfolio = execution.parameters.get("portfolio")
            if not isinstance(portfolio, dict):
                raise AdobePngUploadBundleError("Finalized PNG has no portfolio lineage.")
            metadata = _metadata(portfolio)
            lane = portfolio.get("lane_key")
            chosen_category = category if category is not None else ADOBE_CATEGORY_BY_LANE.get(lane)
            if chosen_category is None or not 1 <= chosen_category <= 21:
                raise AdobePngUploadBundleError("PNG requires an explicit reviewed Adobe category.")
            asset_dir = bundle / f"asset-{artifact.id[:8]}"
            asset_dir.mkdir()
            filename = f"sf-{artifact.id[:8]}.png"
            if len(filename) > MAX_FILENAME_CHARS:
                raise AdobePngUploadBundleError("Generated PNG filename exceeds the portal limit.")
            upload = asset_dir / filename
            shutil.copy2(source, upload)
            embed_png_metadata(source=upload, title=metadata["title"], keywords=metadata["keywords"], category=str(chosen_category), ai_disclosure="required")
            embedded = inspect_transparent_png(upload)
            if not embedded.ready:
                raise AdobePngUploadBundleError("PNG with embedded metadata failed the technical gate.")
            record = {"artifact_id": artifact.id, "execution_id": execution.id, "filename": filename, "source_file": artifact.relative_path, "title": metadata["title"], "keywords": metadata["keywords"], "category": chosen_category, "adobe_file_type": MANUAL_FILE_TYPE, "technical_gate": embedded.to_dict(), "generative_ai_declaration_required": True, "reviewer_checklist": metadata["reviewer_checklist"]}
            (asset_dir / "UPLOAD_METADATA.txt").write_text("STOCKFORGE — ADOBE PNG UPLOAD\n==============================\n\nUpload the PNG only. Metadata is embedded in the PNG.\n\nTITLE\n" + metadata["title"] + "\n\nKEYWORDS\n" + ", ".join(metadata["keywords"]) + f"\n\nCATEGORY\n{chosen_category} — verify manually in Adobe\n\nDECLARATIONS\n- Generative AI: YES\n- People/property declarations: verify truthfully from the visual\n- Upload/submission remains manual\n", encoding="utf-8")
            records.append(record)
            asset_dirs.append(asset_dir)
        manifest = {"schema_version": 1, "kind": "stockforge.adobe_png_android_manual_upload_bundle", "status": "manual_portal_upload_prepared_not_submitted", "approved_by_user": True, "files": records, "folder_contract": "Each asset folder contains exactly one PNG master with embedded metadata and UPLOAD_METADATA.txt."}
        manifest_path = bundle / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return {"path": str(bundle), "asset_dirs": [str(p) for p in asset_dirs], "manifest_path": str(manifest_path), "artifact_ids": [r["artifact_id"] for r in records], "status": "manual_portal_upload_prepared_not_submitted"}
    except Exception:
        shutil.rmtree(bundle, ignore_errors=True)
        raise
