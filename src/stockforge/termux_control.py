"""Termux-first control-plane helpers for remote StockForge generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .generation import GenerationRequest
from .provider_config import ProviderConfig, ProviderConfigError, ProviderConfigStore
from .provider_orchestration import ProviderCandidate, ProviderCapabilities, ProviderRouter
from .remote_gradio import RemoteGradioProvider


class TermuxControlError(ValueError):
    """Raised when a Termux generation command is not safe to submit."""


_STANDALONE_PROMPT_POLICY = (
    "Create exactly one standalone commercial visual asset for flexible web, marketing, "
    "product, editorial, and presentation use. The stated subject is the only primary object. "
    "Show the complete object, centered and clearly separated, on a pure clean white studio background "
    "with generous empty surrounding space. No scene, no environment, no collage, no frame, and no border. "
    "No people, hands, fingers, faces, bodies, tools, measuring instruments, devices, phones, computers, "
    "screens, cables, packaging, labels, numbers, letters, readable text, typography, logo, trademark, "
    "watermark, stamp, postmark, dashboard, or unrelated props. Prioritize a clean silhouette, believable "
    "material, restrained palette, and immediate thumbnail recognition."
)


def standalone_prompt(subject: str) -> str:
    """Wrap a subject in the mandatory single-asset policy for direct Termux generation."""
    cleaned = str(subject).strip()
    if not cleaned:
        raise TermuxControlError("A standalone asset subject is required.")
    return f"{_STANDALONE_PROMPT_POLICY} Subject: {cleaned}"


@dataclass(frozen=True, slots=True)
class GenerationProfile:
    """A bounded, reproducible model profile for quota-constrained workers."""

    name: str
    model_id: str
    model_version: str
    width: int
    height: int
    steps: int
    guidance_scale: float
    estimated_gpu_seconds: int

    def __post_init__(self) -> None:
        if not self.name or not self.model_id or not self.model_version:
            raise TermuxControlError("Profile name, model ID, and model version must be non-empty.")
        if self.width < 1 or self.height < 1:
            raise TermuxControlError("Profile dimensions must be positive.")
        if not 4 <= self.steps <= 12:
            raise TermuxControlError("Free provider profiles must use between 4 and 12 steps.")
        if self.guidance_scale < 0:
            raise TermuxControlError("Guidance scale must be non-negative.")
        if self.estimated_gpu_seconds < 1:
            raise TermuxControlError("Estimated GPU seconds must be positive.")

    def request(self, prompt: str, *, seed: int | None = None) -> GenerationRequest:
        return GenerationRequest(
            prompt=standalone_prompt(prompt),
            width=self.width,
            height=self.height,
            steps=self.steps,
            guidance_scale=self.guidance_scale,
            seed=seed,
            batch_size=1,
            model_id=self.model_id,
            model_version=self.model_version,
            parameters={
                "profile": self.name,
                "estimated_gpu_seconds": self.estimated_gpu_seconds,
                "quota_policy": "single-candidate",
                "asset_policy": "standalone_single_subject_v1",
            },
        )


FREE_PROFILES: dict[str, GenerationProfile] = {
    "z-image-turbo": GenerationProfile(
        name="z-image-turbo",
        model_id="z-image-turbo",
        model_version="2025-11-27",
        width=1024,
        height=1024,
        steps=8,
        guidance_scale=0.0,
        estimated_gpu_seconds=55,
    ),
    "qwen-image": GenerationProfile(
        name="qwen-image",
        model_id="qwen-image",
        model_version="2025-08-04",
        width=1024,
        height=1024,
        steps=8,
        guidance_scale=1.0,
        estimated_gpu_seconds=55,
    ),
}


def profile_for(name: str) -> GenerationProfile:
    try:
        return FREE_PROFILES[name]
    except KeyError as exc:
        supported = ", ".join(sorted(FREE_PROFILES))
        raise TermuxControlError(f"Unsupported generation profile: {name}. Supported profiles: {supported}") from exc


def provider_store(workspace: Path) -> ProviderConfigStore:
    return ProviderConfigStore(Path(workspace) / "providers.json")


def configure_remote_provider(
    *,
    workspace: Path,
    provider_id: str,
    endpoint: str,
    secret_env: str | None = None,
    timeout_seconds: int = 300,
    profile_names: tuple[str, ...] = ("qwen-image",),
    score: float = 0.0,
) -> ProviderConfig:
    """Persist one remote worker configuration without writing its secret value."""
    parsed = urlparse(endpoint)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise TermuxControlError("Provider endpoint must be an absolute http(s) URL.")
    models = tuple(profile_for(name).model_id for name in profile_names)
    config = ProviderConfig(
        provider_id=provider_id,
        endpoint=endpoint.rstrip("/"),
        enabled=True,
        timeout_seconds=timeout_seconds,
        capabilities=("image.generate", "image.generate.remote"),
        secret_env=secret_env,
        metadata={"models": list(models), "score": float(score), "control_plane": "termux"},
    )
    store = provider_store(workspace)
    existing = {item.provider_id: item for item in store.load_all()}
    existing[provider_id] = config
    store.save_all([existing[key] for key in sorted(existing)])
    return config


def remote_candidate(
    *,
    config: ProviderConfig,
    output_dir: Path,
) -> ProviderCandidate:
    """Create a routing candidate from non-secret local configuration."""
    if not config.enabled:
        raise TermuxControlError(f"Provider {config.provider_id!r} is disabled.")
    if not config.endpoint:
        raise TermuxControlError(f"Provider {config.provider_id!r} has no endpoint.")
    if "image.generate" not in config.capabilities:
        raise TermuxControlError(f"Provider {config.provider_id!r} lacks image.generate capability.")
    raw_models = config.metadata.get("models", [])
    if not isinstance(raw_models, list) or not all(isinstance(model, str) and model for model in raw_models):
        raise TermuxControlError(f"Provider {config.provider_id!r} has invalid model metadata.")
    raw_score = config.metadata.get("score", 0.0)
    if not isinstance(raw_score, (int, float)):
        raise TermuxControlError(f"Provider {config.provider_id!r} has invalid routing score.")
    provider = RemoteGradioProvider(
        provider_id=config.provider_id,
        base_url=config.endpoint,
        output_dir=output_dir,
        token=config.resolve_secret(),
        timeout_seconds=float(config.timeout_seconds),
        capabilities=frozenset(config.capabilities),
    )
    capabilities = ProviderCapabilities(
        provider_id=config.provider_id,
        available=True,
        generation=True,
        max_width=1024,
        max_height=1024,
        max_batch_size=1,
        models=frozenset(raw_models),
    )
    return ProviderCandidate(provider=provider, capabilities=capabilities, score=float(raw_score))


def route_remote_generation(
    *,
    workspace: Path,
    request: GenerationRequest,
    output_dir: Path,
    provider_id: str | None = None,
) -> ProviderCandidate:
    """Route a bounded request through configured remote workers only."""
    configs = provider_store(workspace).load_all()
    if provider_id is not None:
        configs = [config for config in configs if config.provider_id == provider_id]
    candidates = [remote_candidate(config=config, output_dir=output_dir) for config in configs]
    if not candidates:
        target = provider_id or "configured providers"
        raise TermuxControlError(f"No enabled remote provider found for {target}.")
    return ProviderRouter(candidates).select(request)


def provider_names(workspace: Path) -> tuple[str, ...]:
    return tuple(config.provider_id for config in provider_store(workspace).load_all())
