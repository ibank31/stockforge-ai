"""Build a bounded Termux-downloadable package from one successful execution."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .adobe_gate import inspect_image
from .adobe_png_gate import inspect_transparent_png
from .database import Database
from .native_vector import inspect_native_svg
from .portfolio_review import evaluate_portfolio_candidate


class ReleasePackageError(RuntimeError):
    """Raised when an execution cannot safely be released for download."""


def _technical_report_for(source: Path) -> dict[str, object]:
    """Choose a local technical gate from the delivered format, not its origin."""
    suffix = source.suffix.casefold()
    if suffix in {".jpg", ".jpeg"}:
        return inspect_image(source).to_dict()
    if suffix == ".png":
        return inspect_transparent_png(source).to_dict()
    if suffix == ".svg":
        return inspect_native_svg(source).to_dict()
    raise ReleasePackageError(f"No technical gate is registered for delivery format: {source.suffix or 'unknown'}")


def _portfolio_review_for(*, source: Path, project_root: Path, current_artifact_id: str, project_artifacts: list[object]) -> dict[str, object]:
    """Avoid running raster perceptual QA against an editable SVG document."""
    if source.suffix.casefold() == ".svg":
        return {
            "decision": "REVIEW",
            "reason": "Native SVG passed structural vector checks; human review must still assess visual utility, distinctness, and marketplace metadata.",
            "raster_quality_check": "not_applicable",
        }
    return evaluate_portfolio_candidate(
        source,
        project_root=project_root,
        current_artifact_id=current_artifact_id,
        project_artifacts=project_artifacts,
    ).to_dict()


@dataclass(frozen=True, slots=True)
class ReleasePackage:
    """A zip package containing only generated image outputs and provenance."""

    path: Path
    execution_id: str
    artifact_ids: tuple[str, ...]
    status: str = "review_ready"

    def to_dict(self) -> dict[str, object]:
        return {
            "path": str(self.path),
            "execution_id": self.execution_id,
            "artifact_ids": list(self.artifact_ids),
            "status": self.status,
        }


def build_release_package(
    *,
    database: Database,
    project_id: str,
    project_root: Path,
    execution_id: str,
    destination_dir: Path | None = None,
) -> ReleasePackage:
    """Package one successful generation without including logs or raw worker data."""
    root = Path(project_root).resolve()
    execution = database.get_execution(execution_id)
    if execution is None:
        raise ReleasePackageError(f"Execution not found: {execution_id}")
    if execution.project_id != project_id:
        raise ReleasePackageError("Execution does not belong to the requested project.")
    if execution.state != "succeeded":
        raise ReleasePackageError("Only succeeded executions can be packaged for download.")
    if not execution.artifact_ids:
        raise ReleasePackageError("Execution has no generated artifacts.")

    artifacts = []
    for artifact_id in execution.artifact_ids:
        artifact = database.get_artifact(artifact_id)
        if artifact is None:
            raise ReleasePackageError(f"Execution artifact is missing: {artifact_id}")
        if artifact.project_id != project_id or artifact.kind not in {"generated-image", "finalized-master", "native-vector"}:
            raise ReleasePackageError(f"Execution artifact is not an eligible delivery artifact: {artifact_id}")
        source = (root / artifact.relative_path).resolve()
        try:
            source.relative_to(root)
        except ValueError as exc:
            raise ReleasePackageError("Artifact path escapes the project workspace.") from exc
        if not source.is_file():
            raise ReleasePackageError(f"Generated artifact file is missing: {artifact.relative_path}")
        artifacts.append((artifact, source))

    def package_file(artifact, source: Path) -> str:
        directory = "masters" if artifact.kind == "finalized-master" else ("vectors" if artifact.kind == "native-vector" else "images")
        return f"{directory}/{artifact.id}{source.suffix.lower()}"

    target_dir = Path(destination_dir or root / "deliveries").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    package_path = target_dir / f"stockforge-{execution.id}.zip"
    portfolio = execution.parameters.get("portfolio")
    if portfolio is not None and not isinstance(portfolio, dict):
        raise ReleasePackageError("Execution portfolio context is invalid.")
    technical_reports = []
    portfolio_reviews = []
    if portfolio is not None:
        project_artifacts = database.list_artifacts(project_id)
        for artifact, source in artifacts:
            report = _technical_report_for(source)
            technical_reports.append({
                "artifact_id": artifact.id,
                "file": package_file(artifact, source),
                "report": report,
            })
            portfolio_reviews.append({
                "artifact_id": artifact.id,
                "file": package_file(artifact, source),
                "review": _portfolio_review_for(
                    source=source,
                    project_root=root,
                    current_artifact_id=artifact.id,
                    project_artifacts=project_artifacts,
                ),
            })
    manifest = {
        "schema_version": 4,
        "status": "review_ready",
        "notice": "This package contains generated outputs that passed execution persistence. It is not a marketplace acceptance guarantee; human compliance review remains required.",
        "execution": execution.to_dict(),
        "portfolio": portfolio,
        "technical_reports": technical_reports,
        "portfolio_reviews": portfolio_reviews,
        "artifacts": [
            {
                "id": artifact.id,
                "sha256": artifact.sha256,
                "mime_type": artifact.mime_type,
                "size_bytes": artifact.size_bytes,
                "file": package_file(artifact, source),
            }
            for artifact, source in artifacts
        ],
    }
    readme = (
        "StockForge review-ready download package\n\n"
        "This archive contains generated image outputs, an execution manifest, and where available a portfolio metadata draft. "
        "It is not a marketplace acceptance, legal-clearance, rights-clearance, or sales guarantee. "
        "Perform full-size visual, rights, policy, distinctness, metadata, and marketplace-specific review before submission.\n"
    )
    temporary_path = package_path.with_suffix(".zip.tmp")
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for artifact, source in artifacts:
                archive.write(source, package_file(artifact, source))
            archive.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
            if portfolio is not None:
                metadata = portfolio.get("metadata")
                checklist = portfolio.get("reviewer_checklist")
                if not isinstance(metadata, dict) or not isinstance(checklist, list):
                    raise ReleasePackageError("Execution portfolio metadata is invalid.")
                archive.writestr(
                    "portfolio_metadata_draft.json",
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                )
                worksheet = io.StringIO(newline="")
                writer = csv.writer(worksheet)
                writer.writerow(["filename", "title", "keywords", "created_using_generative_ai", "people_or_property", "review_status"])
                keyword_text = ", ".join(str(item) for item in metadata.get("keywords", []))
                for artifact, source in artifacts:
                    writer.writerow([
                        package_file(artifact, source),
                        str(metadata.get("title", "")),
                        keyword_text,
                        str(metadata.get("created_using_generative_ai", True)).lower(),
                        str(metadata.get("people_or_property", "human review required")),
                        str(metadata.get("status", "human_review_required")),
                    ])
                archive.writestr("portfolio_metadata_draft.csv", worksheet.getvalue())
                archive.writestr(
                    "TECHNICAL_READINESS.json",
                    json.dumps(technical_reports, indent=2, sort_keys=True) + "\n",
                )
                archive.writestr(
                    "PORTFOLIO_REVIEW.json",
                    json.dumps(portfolio_reviews, indent=2, sort_keys=True) + "\n",
                )
                master_finalization = execution.parameters.get("master_finalization")
                if master_finalization is not None:
                    archive.writestr(
                        "MASTER_FINALIZATION.json",
                        json.dumps(master_finalization, indent=2, sort_keys=True) + "\n",
                    )
                checklist_lines = [
                    "# StockForge Portfolio Review Checklist",
                    "",
                    "**Package status:** `review_ready` only. This file does not approve marketplace submission.",
                    "- [ ] If this package contains `masters/`, inspect the JPEG at 100% and compare it with its preview before upload.",
                    "- [ ] Review `MASTER_FINALIZATION.json` where present; it records the visual transform but does not certify its quality.",
                    "",
                    "## Required human checks",
                    "",
                ]
                checklist_lines.extend(f"- [ ] {str(item)}" for item in checklist)
                checklist_lines.extend([
                    "- [ ] Review TECHNICAL_READINESS.json; finalize the file if the technical gate is REVIEW or FAIL.",
                    "- [ ] Review PORTFOLIO_REVIEW.json; a REJECT decision stops this concept, while REVIEW still requires semantic and commercial inspection.",
                    "- [ ] Verify final file format, dimensions, colour profile, and any marketplace-specific requirements.",
                    "- [ ] Verify this image is not a seed/crop/color-only duplicate of another selected portfolio asset.",
                    "- [ ] Record any rejection reason before generating a replacement.",
                    "",
                    "## Frozen portfolio lineage",
                    "",
                    f"- Batch ID: `{portfolio.get('batch_id', '-')}`",
                    f"- Brief ID: `{portfolio.get('brief_id', '-')}`",
                    f"- Lane: `{portfolio.get('lane_key', '-')}`",
                    f"- Tier: `{portfolio.get('tier', '-')}`",
                ])
                archive.writestr("REVIEW_CHECKLIST.md", "\n".join(checklist_lines) + "\n")
            archive.writestr("README.txt", readme)
        temporary_path.replace(package_path)
    finally:
        temporary_path.unlink(missing_ok=True)

    return ReleasePackage(
        path=package_path,
        execution_id=execution.id,
        artifact_ids=tuple(artifact.id for artifact, _ in artifacts),
    )
