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
    "seed_starting_tray_propagation": JpegNicheIdentity(
        lane_key="seed_starting_tray_propagation",
        signature="recognizable modular propagation tray with a small number of healthy seedlings and visible horticultural material relationships",
        lighting="soft warm window daylight with gentle moisture highlights and no dramatic studio gloss",
        framing="top-front three-quarter isolated tabletop study with the full tray silhouette readable at thumbnail size",
        context="quiet neutral horticultural workspace using peat-free compost tones, terracotta, recycled tray plastic, and restrained green seedlings",
        distinctness=("cell-tray geometry", "seedling-stage clarity", "moisture-and-compost material relationship", "propagation-specific silhouette"),
        prohibited_shorthand=("brand seed packet", "readable label", "named cultivar", "garden-tool pile", "greenhouse clutter", "certification badge", "eco claim", "botanical pattern", "generic plant pot"),
    ),
    "sewing_craft_tool_clipart": JpegNicheIdentity(
        lane_key="sewing_craft_tool_clipart",
        signature="compact cheerful cluster of unbranded sewing and textile-craft tools with bold consistent outlines and clear object separation",
        lighting="even bright illustration light with a small restrained offset shadow and no glossy product-ad glare",
        framing="tight square clip-art cluster with a complete silhouette, balanced spacing, and immediate thumbnail recognition",
        context="clean warm-white paper-like background using cobalt, coral, sunny yellow, teal, cream, and charcoal outline",
        distinctness=("sewing-tool specificity", "compact mini-set rhythm", "bold outline hierarchy", "friendly flat-color contrast"),
        prohibited_shorthand=("Adobe logo", "email interface", "button", "dollar amount", "brand logo", "readable text", "human face", "human hand", "construction wrench", "power drill", "gear", "spark plug", "generic hardware pile", "copyrighted character"),
    ),
    "pet_enrichment_object_illustrations": JpegNicheIdentity(
        lane_key="pet_enrichment_object_illustrations",
        signature="single recognizable interactive treat-puzzle feeder with rounded compartments and a clear enrichment function",
        lighting="soft warm daylight with restrained material highlights and no glossy pet-product ad glare",
        framing="three-quarter isolated product study with a complete silhouette and clear interaction surface",
        context="quiet warm-white editorial studio using muted teal, coral, cream, and natural-rubber accents",
        distinctness=("treat-puzzle geometry", "foraging and enrichment cue", "single-object pet-care silhouette", "rounded compartment hierarchy"),
        prohibited_shorthand=("brand logo", "product label", "readable text", "animal face", "animal body", "medical claim", "safety certification", "sharp exposed parts", "loose hazardous components", "generic toy pile"),
    ),
    "animal_adoption_foster_story_vignettes": JpegNicheIdentity(
        lane_key="animal_adoption_foster_story_vignettes",
        signature="original animal-adoption story vignette with one visible transition action, triangular helper hierarchy, and tactile first-day-home care cues",
        lighting="bright soft daylight with a warm focal key on the transitioning animal and restrained material separation for fabric and carrier surfaces",
        framing="tight square three-quarter vignette with a diagonal carrier-to-helper movement, one clear focal animal, two supporting species, and complete readable silhouettes",
        context="warm-white editorial campaign studio with a small unbranded carrier and care props; no literal shelter, poster, logo, or rescue-event scene",
        distinctness=("visible transition action", "three-species silhouette contrast", "tactile care-prop storytelling", "triangular focal hierarchy"),
        prohibited_shorthand=("superhero", "comic book", "cape", "mask", "lightning bolt", "shield emblem", "royal costume", "sports team", "brand logo", "named shelter", "adopt me", "slogan", "readable text", "celebrity", "artist style", "copyrighted character", "human face", "human hand", "real rescue event", "medical claim", "generic mascot lineup", "generic character sheet"),
    ),
    "animal_adoption_foster_helper_characters": JpegNicheIdentity(
        lane_key="animal_adoption_foster_helper_characters",
        signature="friendly original animal-helper trio with distinct species silhouettes and practical volunteer styling for adoption and foster communication",
        lighting="bright soft daylight with warm facial readability, clean color-block separation, and no cinematic superhero glow",
        framing="tight square three-quarter group framing with one focal animal and two supporting silhouettes, complete feet and ears, and compact thumbnail readability",
        context="warm-white editorial campaign studio; community-helper energy without a literal shelter, poster, logo, or rescue-event scene",
        distinctness=("role-based animal trio", "plain volunteer styling", "original species contrast", "adoption-and-foster campaign utility"),
        prohibited_shorthand=("superhero", "comic book", "cape", "mask", "lightning bolt", "shield emblem", "royal costume", "sports team", "brand logo", "named shelter", "adopt me", "slogan", "readable text", "celebrity", "artist style", "copyrighted character", "human face", "human hand", "real rescue event", "medical claim"),
    ),
    "technical_mechanical_component_illustrations": JpegNicheIdentity(
        lane_key="technical_mechanical_component_illustrations",
        signature="precision-friendly conceptual mechanical component with readable axial geometry and one clear functional silhouette",
        lighting="controlled studio key light with restrained copper, brass, graphite, and steel separation; no glossy product-ad spectacle",
        framing="three-quarter or orthographic-like isolated component study, large enough for thumbnail recognition with quiet surrounding margin",
        context="clean neutral technical illustration studio; conceptual engineering language without CAD screens, workshop clutter, or false specification",
        distinctness=("axial construction", "material relationship", "recognizable component silhouette", "purposeful edge hierarchy"),
        prohibited_shorthand=("CAD screenshot", "blueprint", "dimension line", "model number", "manufacturer mark", "logo", "brand-specific housing", "certification symbol", "spark plug", "motorcycle engine", "tool cluster"),
    ),
    "technical_cable_entry_fitting_illustrations": JpegNicheIdentity(
        lane_key="technical_cable_entry_fitting_illustrations",
        signature="compact non-rotating cable-entry fitting where threaded body, cap nut, seal insert, and short cable stub form one readable product silhouette",
        lighting="controlled neutral studio light with graphite, muted brass, steel, dark elastomer, and one restrained cable-color separation; no glossy catalog glare",
        framing="centered three-quarter isolated fitting study with complete silhouette, visible entry axis, and enough margin for thumbnail recognition",
        context="clean white technical illustration studio; generic enclosure-installation language without an enclosure scene, tools, labels, or specification sheet",
        distinctness=("threaded cable-entry silhouette", "seal-and-strain-relief hierarchy", "non-rotating connector identity", "compact cable stub cue"),
        prohibited_shorthand=("CAD screenshot", "blueprint", "dimension line", "model number", "manufacturer mark", "logo", "brand-specific housing", "readable label", "numeric marking", "IP rating", "UL mark", "IEC mark", "ATEX badge", "IECEx badge", "certification seal", "pressure gauge", "rotor", "armature", "winding", "coil", "gear", "spark plug", "motor housing", "axial shaft", "wheel", "valve handle", "plumbing scene", "wrench", "drill", "human hand", "hardware pile"),
    ),
}


def identity_for(lane_key: str) -> JpegNicheIdentity:
    try:
        return JPEG_NICHE_IDENTITIES[lane_key]
    except KeyError as exc:
        raise KeyError(f"No JPEG niche identity registered for {lane_key!r}.") from exc
