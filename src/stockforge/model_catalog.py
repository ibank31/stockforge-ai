"""Evidence-backed image-model catalog for StockForge routing.

A catalog entry is not a promise that a model can run on every configured
provider.  It records the commercial-license evidence and the local readiness
boundary so the CLI never labels a token, billing, or unverified worker path as
"free production".
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


ModelReadiness = Literal["verified_free", "conditional", "research_only"]


@dataclass(frozen=True, slots=True)
class ImageModelRecord:
    profile: str
    model_id: str
    model_version: str
    readiness: ModelReadiness
    license_id: str
    primary_use: str
    expected_steps: int
    free_path: str
    activation_requirements: tuple[str, ...]
    limitations: tuple[str, ...]
    source_url: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


IMAGE_MODEL_CATALOG: tuple[ImageModelRecord, ...] = (
    ImageModelRecord(
        profile="z-image-turbo",
        model_id="z-image-turbo",
        model_version="2025-11-27",
        readiness="verified_free",
        license_id="Apache-2.0",
        primary_use="Default single-concept preview on the verified StockForge ZeroGPU worker.",
        expected_steps=8,
        free_path="Existing Hugging Face ZeroGPU Space; daily usage remains quota-limited.",
        activation_requirements=(),
        limitations=(
            "Turbo is optimized for speed rather than maximum diversity.",
            "It is preview-only until technical, distinctness, and human review pass.",
        ),
        source_url="https://huggingface.co/Tongyi-MAI/Z-Image-Turbo",
    ),
    ImageModelRecord(
        profile="qwen-image",
        model_id="qwen-image",
        model_version="2025-08-04",
        readiness="conditional",
        license_id="Apache-2.0",
        primary_use="High-control text and layout experimentation only after a compatible worker is benchmarked.",
        expected_steps=50,
        free_path="Potential Kaggle or separate ZeroGPU worker; no verified active StockForge worker.",
        activation_requirements=(
            "A compatible worker with sufficient model storage and memory.",
            "A bounded benchmark proving latency, disk use, and output quality.",
        ),
        limitations=(
            "The official example uses 50 inference steps, so it is not a quota-efficient default.",
            "The existing Qwen profile must not be routed to a worker that only advertises Z-Image.",
        ),
        source_url="https://huggingface.co/Qwen/Qwen-Image",
    ),
    ImageModelRecord(
        profile="flux-1-schnell",
        model_id="flux-1-schnell",
        model_version="2026-01-02",
        readiness="conditional",
        license_id="Apache-2.0",
        primary_use="Fast alternate-model benchmark after access terms and a dedicated worker are explicitly completed.",
        expected_steps=4,
        free_path="Potential self-hosted ZeroGPU or Kaggle worker; no active StockForge deployment.",
        activation_requirements=(
            "The model host requires the account holder to accept access conditions and share contact information.",
            "A separate compatible worker and a reproducible quality benchmark.",
        ),
        limitations=(
            "Do not activate automatically because the model files are access-gated.",
            "No public third-party API is treated as free or commercially cleared by this catalog.",
        ),
        source_url="https://huggingface.co/black-forest-labs/FLUX.1-schnell",
    ),
)


def list_image_models() -> tuple[ImageModelRecord, ...]:
    """Return all catalog records in stable production-review order."""
    return IMAGE_MODEL_CATALOG


def model_record(profile: str) -> ImageModelRecord:
    normalized = str(profile).strip().lower()
    for record in IMAGE_MODEL_CATALOG:
        if record.profile == normalized:
            return record
    supported = ", ".join(record.profile for record in IMAGE_MODEL_CATALOG)
    raise KeyError(f"Unknown image-model profile {profile!r}. Supported: {supported}")
