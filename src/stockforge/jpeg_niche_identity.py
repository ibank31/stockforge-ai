"""Niche-specific visual identity contracts for JPEG portfolio lanes.

These are art-direction hypotheses, not sales claims.  They make each lane's
visual grammar explicit before generation and remain subject to human review.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class JpegNicheIdentity:
    lane_key: str
    signature: str
    lighting: str
    framing: str
    context: str
    distinctness: tuple[str, ...]
    prohibited_shorthand: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


JPEG_NICHE_IDENTITIES: dict[str, JpegNicheIdentity] = {
    "ai_governance": JpegNicheIdentity(
        lane_key="ai_governance",
        signature="calm oversight system with a visible source-to-review-to-release hierarchy",
        lighting="cool soft key light with one restrained muted-amber control accent",
        framing="precise three-quarter product-study framing with deliberate spacing between system layers",
        context="quiet white editorial studio; the metaphor must remain abstract and non-interface",
        distinctness=("nested transparent gates", "review-stage hierarchy", "controlled release relationship"),
        prohibited_shorthand=("padlock", "shield", "robot", "hologram", "dashboard", "checkmark badge"),
    ),
    "playful_surreal_product_metaphors": JpegNicheIdentity(
        lane_key="playful_surreal_product_metaphors",
        signature="one witty impossible material interaction that reads as a single visual sentence",
        lighting="soft directional daylight with one playful but physically plausible cast shadow",
        framing="editorial three-quarter framing that protects the silhouette and leaves intentional campaign space when requested",
        context="warm minimal studio with tactile paper, ceramic, or soft-rubber behavior; no corporate set dressing",
        distinctness=("unexpected material relationship", "one memorable action", "friendly asymmetry"),
        prohibited_shorthand=("lightbulb", "trophy", "generic rocket", "corporate handshake", "fake interface", "hologram"),
    ),
    "tactile_material_atmospheres": JpegNicheIdentity(
        lane_key="tactile_material_atmospheres",
        signature="material-first sensory composition where surface behavior carries the concept",
        lighting="raking side light that reveals fiber, translucency, grain, or relief without harsh glare",
        framing="wide functional hero framing with a stable focal form and genuinely usable copy field",
        context="quiet neutral material studio with controlled depth and no decorative clutter",
        distinctness=("specific surface response", "measured relief or translucency", "copy-safe compositional rhythm"),
        prohibited_shorthand=("generic gradient", "plastic blob", "marble luxury backdrop", "neon glow", "busy texture collage"),
    ),
    "synthetic_media_trust": JpegNicheIdentity(
        lane_key="synthetic_media_trust",
        signature="source-to-verification containment that communicates provenance without literal news imagery",
        lighting="calm directional light that separates transparent layers and preserves a clear origin-to-check relationship",
        framing="open editorial composition with a readable source path and protected headline space where requested",
        context="paper-and-acrylic studio language; thoughtful, quiet, and non-alarmist rather than sensational",
        distinctness=("transparent source container", "verification sequence", "open end state"),
        prohibited_shorthand=("breaking-news scene", "broadcast microphone", "face collage", "seal", "checkmark badge", "fake phone screen"),
    ),
    "returns_recommerce": JpegNicheIdentity(
        lane_key="returns_recommerce",
        signature="visible product-state loop from return through assessment, recovery, or resale",
        lighting="warm neutral operational light with clear separation of parcel material and recovery path",
        framing="orderly three-quarter system-object framing; the loop must read without a warehouse scene or labels",
        context="small clean tabletop logistics study using unbranded kraft, recycled plastic, and ceramic forms",
        distinctness=("reverse route", "state change", "retained value after return"),
        prohibited_shorthand=("barcode", "scanner", "warehouse aisle", "delivery logo", "generic cardboard pile", "tracking label"),
    ),
    "digital_accessibility": JpegNicheIdentity(
        lane_key="digital_accessibility",
        signature="multiple clear participation paths represented by a calm tactile system with no literal interface",
        lighting="even diffuse light with strong but natural material contrast and no distracting glare",
        framing="front three-quarter view with generous separation, low clutter, and immediate path legibility",
        context="respectful neutral editorial studio; communicate adaptability, never legal compliance or a disability stereotype",
        distinctness=("multiple equivalent paths", "tactile hierarchy", "adaptable open mechanism"),
        prohibited_shorthand=("compliance badge", "wheelchair symbol", "person stereotype", "screen reader UI", "keyboard close-up", "checkmark seal"),
    ),
    "retro_tech_developer_metaphors": JpegNicheIdentity(
        lane_key="retro_tech_developer_metaphors",
        signature="brand-free retro-future artifact that suggests systems thinking without depicting real hardware",
        lighting="soft phosphor-like rim light controlled by a neutral key, never neon spectacle or screen glow",
        framing="low or three-quarter artifact study with a complete fictional silhouette and restrained negative space",
        context="quiet retro-future studio using matte plastic and translucent acrylic; no readable interfaces or period-logo cues",
        distinctness=("fictional modular artifact", "analog-digital material tension", "gentle retro-future restraint"),
        prohibited_shorthand=("computer monitor", "keyboard", "cassette", "floppy disk", "terminal text", "operating-system logo"),
    ),
    "circular_packaging_systems": JpegNicheIdentity(
        lane_key="circular_packaging_systems",
        signature="refill or return relationship made visible through nested unbranded container geometry",
        lighting="clean daylight product study with soft material shadows and no greenwash color cast",
        framing="three-quarter system framing that shows the container relationship and open material-flow route",
        context="minimal packaging-material studio with recycled kraft, ceramic, and clear recycled plastic",
        distinctness=("refill relationship", "returnable outer form", "material circulation without symbols"),
        prohibited_shorthand=("recycling triangle", "eco certification mark", "green leaf logo", "food label", "brand package", "regulatory seal"),
    ),
    "software_supply_chain_integrity": JpegNicheIdentity(
        lane_key="software_supply_chain_integrity",
        signature="dependency provenance path with a controlled handoff from source components to trusted build",
        lighting="cool precise side light with measured electric-blue accents and clean translucent separation",
        framing="axial horizontal system study where component order and handoff remain readable at thumbnail size",
        context="minimal technical studio using graphite ceramic, clear acrylic, and matte paper; no cybercrime spectacle",
        distinctness=("ordered dependency chain", "transparent provenance bridge", "controlled build release"),
        prohibited_shorthand=("padlock", "shield", "hooded hacker", "code screen", "server rack", "certification badge", "dashboard"),
    ),
}


def identity_for(lane_key: str) -> JpegNicheIdentity:
    try:
        return JPEG_NICHE_IDENTITIES[lane_key]
    except KeyError as exc:
        raise KeyError(f"No JPEG niche identity registered for {lane_key!r}.") from exc
