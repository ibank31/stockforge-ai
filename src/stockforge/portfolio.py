"""Research-aligned, deterministic portfolio planning for StockForge.

This module contains no marketplace-sales claims and no automatic submission
behaviour.  It converts the evidence-selected portfolio lanes into small,
reviewable AssetSpec and PromptPackage records that can be generated through
the existing Termux-controlled one-candidate path.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Literal

from .asset_prompt_compiler import compile_asset_prompt
from .jpeg_niche_identity import identity_for
from .asset_spec import AssetSpec
from .prompt_compiler import PromptPackage
from .metadata_policy import filter_visual_keywords


Tier = Literal["first", "secondary", "experimental"]
Confidence = Literal["medium", "low"]


class PortfolioError(ValueError):
    """Raised when a portfolio lane, plan, or metadata draft is unsafe."""


@dataclass(frozen=True, slots=True)
class LaneConcept:
    """One materially distinct commercial visual answer inside a portfolio lane."""

    key: str
    subject: str
    visual_mechanism: str
    composition: str
    negative_space: str
    palette: tuple[str, ...]
    originality_levers: tuple[str, ...]
    product_kind: str = "raster_illustration"
    delivery_format: str = "jpeg"
    layout_mode: str = "square"
    background_policy: str = "white"
    isolation_policy: str = "isolated"


@dataclass(frozen=True, slots=True)
class PortfolioLane:
    """A research-selected lane with an explicit small-batch limit."""

    key: str
    name: str
    tier: Tier
    evidence_confidence: Confidence
    opportunity_id: str
    buyer_segment: str
    buyer_job: str
    channel: str
    asset_family: str
    asset_type: str
    micro_niche: str
    visual_language: str
    medium: str
    commercial_use_cases: tuple[str, ...]
    keywords: tuple[str, ...]
    test_cap: int
    concepts: tuple[LaneConcept, ...]
    notes: str


@dataclass(frozen=True, slots=True)
class PortfolioMetadataDraft:
    """Accurate, non-final metadata for a generated portfolio asset."""

    title: str
    keywords: tuple[str, ...]
    created_using_generative_ai: bool
    people_or_property: str
    status: str
    human_review_required: bool
    marketplace_transaction_data: str
    reviewer_checklist: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PortfolioBrief:
    """Generation-ready brief plus review metadata for one lane concept."""

    brief_id: str
    lane: PortfolioLane
    concept: LaneConcept
    asset_spec: AssetSpec
    prompt_package: PromptPackage
    metadata: PortfolioMetadataDraft

    def to_dict(self) -> dict[str, object]:
        return {
            "brief_id": self.brief_id,
            "lane": {
                "key": self.lane.key,
                "name": self.lane.name,
                "tier": self.lane.tier,
                "evidence_confidence": self.lane.evidence_confidence,
                "opportunity_id": self.lane.opportunity_id,
                "test_cap": self.lane.test_cap,
                "notes": self.lane.notes,
            },
            "concept": asdict(self.concept),
            "asset_spec": self.asset_spec.to_dict(),
            "prompt_package": self.prompt_package.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


REVIEWED_CONCEPT_METADATA: dict[tuple[str, str], dict[str, object]] = {
    ("tactile_material_atmospheres", "fiber-arch"): {
        "title": "Recycled Fiber Paper Arch with Sage Green Inner Layer",
        "keywords": (
            "recycled paper",
            "paper arch",
            "fiber texture",
            "sage green",
            "tactile material",
            "abstract paper sculpture",
            "copy space",
            "minimal design",
            "isolated object",
            "white background",
            "neutral palette",
        ),
    },
    ("retro_tech_developer_metaphors", "cloud-module"): {
        "title": "Translucent Modular Tower With Cloud-Shaped Opening",
        "keywords": (
            "translucent module",
            "modular tower",
            "cloud-shaped opening",
            "clear acrylic",
            "matte plastic",
            "pastel colors",
            "soft glow",
            "isolated object",
            "white background",
            "minimal sculpture",
            "abstract 3d object",
            "copy space",
        ),
    },
    ("ai_governance", "review-gate"): {
        "title": "Translucent Review Gate With Stacked Tokens",
        "keywords": ("translucent gate", "stacked tokens", "clear acrylic", "matte ceramic", "layered object", "isometric view", "minimal sculpture", "copy space", "white background", "ink blue", "muted amber"),
    },
    ("playful_surreal_product_metaphors", "zipper-cloud"): {
        "title": "Soft Paper Cloud With Unbranded Zipper",
        "keywords": ("paper cloud", "soft cloud", "unbranded zipper", "folded paper", "surreal object", "minimal sculpture", "warm cream", "cobalt blue", "coral accent", "isolated object", "white background", "copy space"),
    },
    ("synthetic_media_trust", "source-capsule"): {
        "title": "Transparent Source Capsule in Paper Cradle",
        "keywords": ("transparent capsule", "paper cradle", "clear acrylic", "ink blue", "matte ceramic", "layered object", "editorial illustration", "isolated object", "white background", "copy space", "minimal sculpture"),
    },
    ("returns_recommerce", "return-arc"): {
        "title": "Reusable Parcel Form With Circular Return Arc",
        "keywords": ("reusable parcel", "circular arc", "kraft paper", "recycled plastic", "matte ceramic", "isometric object", "unlabelled package", "isolated object", "white background", "copy space", "minimal 3d"),
    },
    ("digital_accessibility", "input-hub"): {
        "title": "Modular Access Hub With Three Clear Paths",
        "keywords": ("modular hub", "clear paths", "matte ceramic", "clear acrylic", "paper element", "abstract object", "centered composition", "isolated object", "white background", "copy space", "minimal illustration"),
    },
    ("human_made_collage_elements", "woven-loop"): {
        "title": "Woven Fibre Loop With Paper Tab",
        "keywords": ("woven fibre", "paper tab", "woven loop", "uncoated paper", "handmade texture", "cut paper element", "editorial craft", "isolated object", "white background", "minimal collage", "copy space"),
    },
    ("circular_packaging_systems", "refill-capsule"): {
        "title": "Blank Refill Capsule With Reusable Outer Form",
        "keywords": ("refill capsule", "reusable form", "blank container", "recycled kraft", "matte ceramic", "clear recycled plastic", "isometric object", "isolated object", "white background", "copy space", "minimal 3d"),
    },
    ("software_supply_chain_integrity", "component-chain"): {
        "title": "Modular Component Chain With Transparent Path",
        "keywords": ("modular components", "transparent path", "graphite ceramic", "clear acrylic", "matte paper", "connected modules", "horizontal object", "isolated object", "white background", "copy space", "minimal 3d"),
    },
    ("seed_starting_tray_propagation", "seed-tray"): {
        "title": "Indoor Seed-Starting Tray with Emerging Seedlings",
        "keywords": (
            "seed starting tray",
            "indoor seed starting",
            "seedling tray",
            "emerging seedlings",
            "plant propagation",
            "home gardening",
            "horticulture",
            "seed sowing",
            "garden tutorial",
            "growing guide",
            "cell tray",
            "peat-free compost",
            "plant nursery",
            "germination",
            "gardening education",
        ),
    },
    ("sewing_craft_tool_clipart", "beginner-kit"): {
        "title": "Colorful Beginner Sewing and Textile Craft Tool Set",
        "keywords": (
            "sewing tools",
            "textile craft",
            "craft tool set",
            "fabric scissors",
            "thread spool",
            "measuring tape",
            "thimble",
            "pincushion",
            "seam ripper",
            "beginner sewing",
            "needlework",
            "sewing tutorial",
            "handmade craft",
            "tailoring supplies",
            "isolated clip art",
        ),
    },
    ("pet_enrichment_object_illustrations", "puzzle-feeder"): {
        "title": "Interactive Treat Puzzle Feeder for Pet Enrichment",
        "keywords": (
            "pet enrichment toy",
            "interactive puzzle feeder",
            "treat puzzle",
            "pet care illustration",
            "dog enrichment",
            "cat enrichment",
            "food puzzle",
            "foraging toy",
            "mental stimulation",
            "companion animal",
            "pet accessory",
            "veterinary handout",
            "animal welfare",
            "indoor pet activity",
            "enrichment board",
        ),
    },
    ("animal_adoption_foster_helper_characters", "rescue-foster-helpers"): {
        "title": "Original Animal Adoption and Foster Community Helper Trio",
        "keywords": (
            "animal adoption",
            "pet foster",
            "animal rescue",
            "animal welfare",
            "shelter campaign",
            "community helpers",
            "fictional animal characters",
            "animal mascot",
            "volunteer campaign",
            "pet care education",
            "social media campaign",
            "adoption event",
            "friendly animal illustration",
            "original character",
            "isolated illustration",
        ),
    },
    ("technical_mechanical_component_illustrations", "rotor-armature"): {
        "title": "Conceptual Electromechanical Rotor Armature Component Illustration",
        "keywords": ("electromechanical component", "rotor armature", "mechanical component", "technical illustration", "industrial technology", "engineering documentation", "conceptual machine part", "copper metal", "graphite housing", "isolated object", "white background", "clean silhouette"),
    },
    ("technical_cable_entry_fitting_illustrations", "cable-gland"): {
        "title": "Unbranded Cable Gland Strain Relief Fitting with Generic Cable",
        "keywords": (
            "cable gland",
            "cable entry fitting",
            "strain relief",
            "threaded connector",
            "electrical enclosure",
            "industrial wiring",
            "cable management",
            "interconnect component",
            "seal insert",
            "cap nut",
            "locknut",
            "technical illustration",
            "isolated object",
            "white background",
            "product illustration",
            "industrial technology",
        ),
    },
    ("native_vector_elements", "modular-ribbon"): {
        "title": "Editable Modular Ribbon Vector Element",
        "keywords": ("editable vector", "modular ribbon", "SVG paths", "geometric element", "connected shapes", "flat illustration", "isolated graphic", "transparent background", "design component", "abstract vector"),
    },
    ("native_vector_elements", "technical-badge"): {
        "title": "Editable Technical Badge Vector Element",
        "keywords": ("editable vector", "technical badge", "SVG paths", "geometric badge", "radial connection", "flat illustration", "isolated graphic", "white background", "design component", "abstract vector"),
    },
    ("native_vector_elements", "folder-upload"): {
        "title": "Editable Folder Upload Icon for File Management",
        "keywords": ("folder upload icon", "file management", "cloud workflow", "editable SVG", "native vector", "upload arrow", "folder symbol", "digital file storage", "web UI icon", "mobile UI icon", "bold geometric icon"),
    },
    ("native_vector_utility_sets", "file-flow-micro-set"): {
        "title": "File Management Utility Icon Set for Web and Cloud Workflows",
        "keywords": ("file management icons", "file flow icon set", "upload download icons", "folder icon", "cloud storage icon", "sync icon", "archive icon", "file sharing icon", "editable SVG icons", "web UI icon set", "mobile UI icons", "bold geometric icons"),
    },
    ("native_vector_patterns", "pattern-tile"): {
        "title": "Editable Geometric Repeat Pattern Tile",
        "keywords": ("seamless pattern", "repeat background", "editable SVG pattern", "geometric tile", "decorative vector", "pattern design", "repeatable background", "native vector", "abstract geometry", "surface pattern"),
    },
}


_BANNED_METADATA_PHRASES = (
    "artist style",
    "in the style of",
    "celebrity",
    "public figure",
    "real person",
    "brand name",
    "logo",
    "trademark",
    "copyrighted",
    "government agency",
    "news event",
)


def _slug(value: str) -> str:
    """Normalize user input while preserving the registry's underscore keys."""
    value = re.sub(r"[^a-z0-9_]+", "_", value.lower()).strip("_")
    return value or "asset"


def _concept(
    key: str,
    subject: str,
    mechanism: str,
    composition: str,
    negative_space: str,
    palette: tuple[str, ...],
    levers: tuple[str, ...],
    *,
    product_kind: str = "raster_illustration",
    delivery_format: str = "jpeg",
    layout_mode: str = "square",
    background_policy: str = "white",
    isolation_policy: str = "isolated",
) -> LaneConcept:
    if layout_mode == "square" and isolation_policy == "isolated":
        composition = "single centered object with tight square product framing"
        negative_space = "minimal clean surrounding margin; no reserved copy space"
    return LaneConcept(
        key=key,
        subject=subject,
        visual_mechanism=mechanism,
        composition=composition,
        negative_space=negative_space,
        palette=palette,
        originality_levers=levers,
        product_kind=product_kind,
        delivery_format=delivery_format,
        layout_mode=layout_mode,
        background_policy=background_policy,
        isolation_policy=isolation_policy,
    )


PALETTES = {
    "governance": ("deep navy", "soft ivory", "muted amber"),
    "playful": ("warm cream", "cobalt blue", "coral accent"),
    "tactile": ("warm white", "sand", "sage green"),
    "trust": ("ink blue", "paper white", "transparent aqua"),
    "returns": ("kraft brown", "recommerce green", "soft charcoal"),
    "access": ("deep blue", "warm white", "clear yellow"),
    "retro": ("dusty lilac", "warm beige", "soft teal"),
    "collage": ("uncoated cream", "brick red", "cobalt blue"),
    "circular": ("recycled kraft", "moss green", "ceramic white"),
    "integrity": ("graphite", "clean white", "electric blue"),
}


PORTFOLIO_LANES: tuple[PortfolioLane, ...] = (
    PortfolioLane(
        key="seed_starting_tray_propagation",
        name="Seed-starting tray and indoor propagation illustrations",
        tier="first",
        evidence_confidence="medium",
        opportunity_id="C61",
        buyer_segment="gardening_content_teams",
        buyer_job="recognizable seed-starting tray for gardening tutorials, horticulture education, and growing guides",
        channel="web",
        asset_family="organic_motif",
        asset_type="illustration",
        micro_niche="indoor seed-starting tray and early seedling propagation",
        visual_language="recognizable editorial horticultural illustration with material clarity and restrained natural color",
        medium="recycled tray plastic, peat-free compost, terracotta, and soft green seedlings with warm daylight",
        commercial_use_cases=("gardening tutorial", "horticulture education", "seed supplier article", "seasonal growing guide"),
        keywords=("seed starting tray", "indoor seed starting", "seedling tray", "emerging seedlings", "plant propagation", "home gardening", "horticulture", "seed sowing", "garden tutorial", "growing guide", "cell tray", "peat-free compost", "plant nursery", "germination", "gardening education"),
        test_cap=1,
        concepts=(
            _concept(
                "seed-tray",
                "one recognizable modular seed-starting tray with a few emerging seedlings in separate cells and no labels",
                "cell geometry and seedling stage make indoor propagation immediately legible",
                "single three-quarter isolated tray study with full silhouette readable at thumbnail size",
                "minimal clean surrounding margin; no reserved copy space",
                ("recycled tray plastic", "peat-free compost", "terracotta", "soft green"),
                ("cell-tray geometry", "seedling-stage clarity", "propagation-specific silhouette", "moisture-and-compost material relationship"),
            ),
        ),
        notes="Evidence-bound first-sale hypothesis from exact-object Adobe supply proxy and public horticulture education guides; demand, approval, ranking, and sales remain unproven.",
    ),
    PortfolioLane(
        key="sewing_craft_tool_clipart",
        name="Beginner sewing and textile-craft tool clip-art",
        tier="first",
        evidence_confidence="medium",
        opportunity_id="C63",
        buyer_segment="craft_content_teams",
        buyer_job="compact sewing-tool clip-art for beginner lessons, pattern tutorials, textile workshops, handmade-business social content, and craft packaging",
        channel="web",
        asset_family="product_illustration",
        asset_type="illustration",
        micro_niche="beginner sewing and textile-craft tool mini-set",
        visual_language="cheerful hand-drawn clip-art with bold consistent outline, bright flat color, compact spacing, and clear object separation",
        medium="clean ink outline, flat cobalt, coral, sunny yellow, teal, warm cream, and subtle paper-grain texture",
        commercial_use_cases=("beginner sewing lesson", "sewing pattern tutorial", "craft blog article", "textile workshop handout", "handmade-business social graphic", "unbranded craft-store packaging"),
        keywords=("sewing tools", "textile craft", "craft tool set", "fabric scissors", "thread spool", "measuring tape", "thimble", "pincushion", "seam ripper", "beginner sewing", "needlework", "sewing tutorial", "handmade craft", "tailoring supplies", "isolated clip art"),
        test_cap=1,
        concepts=(
            _concept(
                "beginner-kit",
                "one compact controlled cluster of unbranded sewing and textile-craft tools: fabric scissors, colorful thread spool, soft measuring tape, thimble, pincushion, and a seam-ripper-like tool",
                "recognizable sewing-tool silhouettes and compact object spacing make the beginner craft kit immediately legible",
                "tight square clip-art cluster with balanced spacing, complete outer silhouette, and no human or interface elements",
                "minimal clean surrounding margin; no reserved copy space",
                ("cobalt blue", "coral pink", "sunny yellow", "teal", "warm cream", "charcoal"),
                ("sewing-tool specificity", "compact mini-set rhythm", "bold outline hierarchy", "friendly flat-color contrast"),
            ),
        ),
        notes="Evidence-bound illustration hypothesis guided by the user's anecdotal best-seller screenshot, Adobe exact-query supply proxies, and public beginner sewing-tool guidance; screenshot revenue, demand, approval, ranking, and sales remain unverified.",
    ),
    PortfolioLane(
        key="pet_enrichment_object_illustrations",
        name="Interactive pet enrichment object illustrations",
        tier="first",
        evidence_confidence="medium",
        opportunity_id="C62",
        buyer_segment="pet_care_content_teams",
        buyer_job="recognizable interactive puzzle feeder for pet-care education, humane-rescue content, veterinary clinic handouts, and pet-accessory packaging",
        channel="web",
        asset_family="product_illustration",
        asset_type="illustration",
        micro_niche="indoor companion-animal treat-puzzle feeder and enrichment board",
        visual_language="polished editorial product illustration with a clear object silhouette and tactile material hierarchy",
        medium="matte molded rubber, recycled polymer, muted teal, coral, cream, and soft gray",
        commercial_use_cases=("pet-care article", "humane-rescue education", "veterinary clinic handout", "pet-accessory packaging", "companion-animal enrichment guide"),
        keywords=("pet enrichment toy", "interactive puzzle feeder", "treat puzzle", "pet care illustration", "dog enrichment", "cat enrichment", "food puzzle", "foraging toy", "mental stimulation", "companion animal", "pet accessory", "veterinary handout", "animal welfare", "indoor pet activity", "enrichment board"),
        test_cap=1,
        concepts=(
            _concept(
                "puzzle-feeder",
                "one modern interactive treat-puzzle feeder board with rounded compartments and a few generic treat pieces, without an animal or text",
                "compartment geometry and visible treat-reward interaction make pet enrichment immediately legible",
                "single three-quarter isolated product study with a complete silhouette and a clear interaction surface",
                "minimal clean surrounding margin; no reserved copy space",
                ("muted teal", "coral", "cream", "soft gray"),
                ("treat-puzzle geometry", "foraging cue", "single-object pet-care silhouette", "rounded compartment hierarchy"),
            ),
        ),
        notes="Evidence-bound illustration hypothesis using ASPCA/RSPCA pet-enrichment guidance and a narrow Adobe exact-query supply proxy; safety claims, demand, approval, ranking, and sales remain unproven.",
    ),
    PortfolioLane(
        key="animal_adoption_foster_helper_characters",
        name="Animal adoption and foster community-helper character illustrations",
        tier="first",
        evidence_confidence="low",
        opportunity_id="C65",
        buyer_segment="animal_welfare_content_teams",
        buyer_job="original friendly animal characters for shelter adoption campaigns, foster recruitment, volunteer education, and animal-welfare social content",
        channel="web",
        asset_family="product_illustration",
        asset_type="illustration",
        micro_niche="original fictional animal adoption and foster community-helper trio",
        visual_language="bright editorial character illustration with distinct animal silhouettes, plain volunteer styling, warm expressions, and controlled group hierarchy",
        medium="warm cream, coral red, teal blue, sunny yellow, charcoal, and soft green with clean color-block clothing and restrained paper texture",
        commercial_use_cases=("shelter adoption campaign", "foster recruitment post", "animal-welfare social graphic", "volunteer education", "community outreach article"),
        keywords=("animal adoption", "pet foster", "animal rescue", "animal welfare", "shelter campaign", "community helpers", "fictional animal characters", "animal mascot", "volunteer campaign", "pet care education", "social media campaign", "adoption event", "friendly animal illustration", "original character", "isolated illustration"),
        test_cap=1,
        concepts=(
            _concept(
                "rescue-foster-helpers",
                "one compact trio of original fictional animal community helpers with three distinct species silhouettes, plain color-block volunteer vests, simple bandanas, warm expressions, and no emblem or text",
                "distinct animal silhouettes and plain volunteer styling create a readable adoption and foster support group",
                "single centered three-quarter isolated character trio with complete silhouettes, clear focal hierarchy, and compact controlled spacing",
                "minimal clean surrounding margin; no reserved copy space",
                ("warm cream", "coral red", "teal blue", "sunny yellow", "charcoal", "soft green"),
                ("animal-welfare campaign utility", "role-based trio silhouette", "plain volunteer styling", "original species contrast"),
            ),
        ),
        notes="Evidence-bound first character-lane hypothesis from the user's anecdotal screenshot signal, ASPCA/Best Friends campaign resources, AVMA pet-care education topics, and Adobe supply proxies; no demand, approval, ranking, download, conversion, revenue, or sales claim.",
    ),
    PortfolioLane(
        key="technical_mechanical_component_illustrations",
        name="Technical mechanical component illustrations",
        tier="first",
        evidence_confidence="medium",
        opportunity_id="C60",
        buyer_segment="editorial_content_teams",
        buyer_job="conceptual electromechanical component for engineering documentation and industrial explainer content",
        channel="web",
        asset_family="technical_component_illustration",
        asset_type="illustration",
        micro_niche="conceptual electromechanical rotor armature component",
        visual_language="precision-friendly stylized technical illustration with readable axial geometry",
        medium="copper, brass, graphite, and muted steel with controlled dimensional shading",
        commercial_use_cases=("engineering documentation", "repair and maintenance explainer", "technical education", "industrial technology article"),
        keywords=("electromechanical component", "rotor armature", "mechanical component", "technical illustration", "industrial technology", "engineering documentation", "conceptual machine part", "copper metal", "graphite housing", "isolated object", "white background", "clean silhouette"),
        test_cap=1,
        concepts=(
            _concept(
                "rotor-armature",
                "one conceptual electromechanical rotor-armature component with copper winding, graphite housing, and a clear axial shaft",
                "recognizable axial construction and material relationship communicate a mechanical component without false technical specification",
                "single three-quarter isolated component study, large enough for thumbnail recognition with a quiet neutral margin",
                "clean neutral surrounding space; no reserved copy field or unrelated props",
                ("copper", "brass", "graphite", "muted steel"),
                ("axial construction", "recognizable component silhouette", "material relationship", "purposeful edge hierarchy"),
            ),
        ),
        notes="Evidence-bound first-sale hypothesis from recurring historical mechanical-component screenshots and Adobe STEM/technology content guidance; not proven demand or engineering accuracy.",
    ),
    PortfolioLane(
        key="technical_cable_entry_fitting_illustrations",
        name="Cable-entry strain-relief fitting illustrations",
        tier="first",
        evidence_confidence="low",
        opportunity_id="C64",
        buyer_segment="industrial_content_teams",
        buyer_job="generic cable-entry fitting for enclosure-installation articles, interconnect explainers, technical education, and product communication",
        channel="web",
        asset_family="technical_component_illustration",
        asset_type="illustration",
        micro_niche="unbranded cable gland and strain-relief fitting with generic cable stub",
        visual_language="precision-friendly isolated product illustration with a compact threaded silhouette and clear seal/strain-relief hierarchy",
        medium="neutral graphite or brass-toned body, dark elastomer seal, muted steel locknut, and one restrained generic cable color",
        commercial_use_cases=("enclosure installation article", "industrial wiring explainer", "interconnect education", "technical product communication"),
        keywords=("cable gland", "cable entry fitting", "strain relief", "threaded connector", "electrical enclosure", "industrial wiring", "cable management", "interconnect component", "seal insert", "cap nut", "locknut", "technical illustration", "isolated object", "white background", "industrial technology"),
        test_cap=1,
        concepts=(
            _concept(
                "cable-gland",
                "one generic unbranded cable gland with threaded gland body, cap nut, visible dark elastomer compression insert, locknut, and a short neutral cable stub",
                "threaded entry, cap nut, seal, and cable stub make cable-entry strain relief immediately legible without claiming a standard or exact specification",
                "single centered three-quarter isolated fitting study with a complete silhouette and enough separation to read at thumbnail size",
                "minimal clean surrounding margin; no reserved copy space",
                ("graphite", "muted brass", "steel", "dark elastomer", "restrained cable blue"),
                ("threaded cable-entry silhouette", "seal-and-strain-relief cue", "non-rotating product identity", "compact material hierarchy"),
                product_kind="raster_illustration",
                delivery_format="jpeg",
                layout_mode="square",
                background_policy="white",
                isolation_policy="isolated",
            ),
        ),
        notes="Evidence-bound first-sale hypothesis from user-provided generic component signal, official cable-gland installation guidance, and Adobe exact-query supply proxy; no demand, approval, ranking, download, conversion, revenue, or sales claim.",
    ),
    PortfolioLane(
        key="ai_governance",
        name="AI governance visual systems",
        tier="first",
        evidence_confidence="medium",
        opportunity_id="C01",
        buyer_segment="web_product_teams",
        buyer_job="AI governance explainer and compliance landing page",
        channel="web",
        asset_family="ui_3d_metaphor",
        asset_type="3d",
        micro_niche="responsible AI oversight and traceability",
        visual_language="restrained conceptual 3D system object",
        medium="frosted glass, matte ceramic, and translucent layers",
        commercial_use_cases=("B2B SaaS landing page", "policy explainer", "training presentation"),
        keywords=("AI governance", "responsible AI", "AI transparency", "AI oversight", "model risk", "AI audit", "algorithm accountability", "human review", "traceable AI", "model documentation", "compliance software", "enterprise AI", "risk management", "policy training", "B2B SaaS"),
        test_cap=20,
        concepts=(
            _concept("review-gate", "a translucent approval gate with three stacked review tokens", "human oversight without people", "single centered object, isometric front view", "clean copy space on the right", PALETTES["governance"], ("review mechanism", "transparent layering", "clear silhouette")),
            _concept("trace-path", "a clear glass pathway connecting a source capsule to a release capsule", "traceability from input to release", "single horizontal object with modular path", "clean copy space above", PALETTES["governance"], ("source-to-release route", "modular system", "open end state")),
            _concept("audit-lens", "a matte ceramic lens framing a translucent record tile", "auditability and evidence review", "centered object with shallow shadow", "clean copy space left", PALETTES["governance"], ("review lens", "tactile material", "editorial readability")),
            _concept("oversight-balance", "a balanced pair of translucent input and outcome blocks on a minimal bridge", "controlled decision balance", "front-facing symmetric object", "clean copy space above", PALETTES["governance"], ("balanced control", "modular blocks", "policy-friendly abstraction")),
            _concept("documentation-container", "a layered transparent document container with non-readable internal tabs", "documentation without fake text", "vertical object, slight three-quarter view", "clean copy space right", PALETTES["governance"], ("document metaphor", "no typography", "transparent material")),
        ),
        notes="Current policy-driven buyer-need hypothesis; public marketplace transaction data is unavailable.",
    ),
    PortfolioLane(
        key="playful_surreal_product_metaphors",
        name="Playful-surreal product metaphors",
        tier="first",
        evidence_confidence="medium",
        opportunity_id="C42",
        buyer_segment="brand_marketing_teams",
        buyer_job="brand campaign and product-benefit hero",
        channel="web",
        asset_family="surreal_concept",
        asset_type="3d",
        micro_niche="playful commercial benefit metaphor",
        visual_language="minimal, tactile, witty editorial 3D",
        medium="matte ceramic, paper, and soft rubber",
        commercial_use_cases=("campaign hero", "SaaS landing page", "social advertising"),
        keywords=("surreal product concept", "playful 3D object", "creative business metaphor", "abstract campaign visual", "impossible object", "whimsical minimalism", "conceptual illustration", "brand storytelling", "marketing landing page", "SaaS launch", "creative brief", "agency presentation", "product benefit", "copy space", "isolated object"),
        test_cap=20,
        concepts=(
            _concept("zipper-cloud", "a soft paper cloud opening with a smooth unbranded zipper", "uncovering a simple benefit", "centered single object with a gentle diagonal", "clean copy space on the left", PALETTES["playful"], ("unexpected material relationship", "one visual sentence", "campaign-ready silhouette")),
            _concept("seed-switch", "a rounded ceramic switch growing one simple paper leaf", "activation and sustainable growth", "front-facing standalone object", "clean copy space on the right", PALETTES["playful"], ("product-benefit metaphor", "organic contrast", "controlled simplicity")),
            _concept("magnet-bridge", "two soft modular shapes joined by a floating magnetic bridge", "connection without interface screens", "isometric single-cluster object", "clean copy space above", PALETTES["playful"], ("connection metaphor", "clear modules", "no device shorthand")),
            _concept("folded-portal", "a folded paper portal revealing a clean soft-color interior", "easy transition and discovery", "vertical centered object", "clean copy space left", PALETTES["playful"], ("transformation", "paper construction", "thumbnail clarity")),
            _concept("balance-pebble", "one floating ceramic pebble balanced on a curved flexible base", "stable simplicity under change", "single object, side view", "clean copy space above", PALETTES["playful"], ("balance metaphor", "gravity variation", "minimal silhouette")),
        ),
        notes="Design-direction evidence supports a test; no public Adobe download evidence is asserted.",
    ),
    PortfolioLane(
        key="tactile_material_atmospheres",
        name="Tactile material atmospheres",
        tier="first",
        evidence_confidence="medium",
        opportunity_id="C41",
        buyer_segment="web_product_teams",
        buyer_job="web hero background and brand-system material study",
        channel="web",
        asset_family="material_atmosphere",
        asset_type="texture",
        micro_niche="functional tactile material composition",
        visual_language="soft-neutral material study with intentional copy field",
        medium="recycled fiber paper, frosted glass, porcelain, and organic foam",
        commercial_use_cases=("website hero background", "presentation cover", "brand-system component"),
        keywords=("tactile design", "material texture", "soft neutral background", "abstract material study", "frosted glass", "recycled paper", "ceramic surface", "organic foam", "tactile web hero", "copy space", "minimal product background", "translucent layers", "website background", "presentation cover", "brand system"),
        test_cap=20,
        concepts=(
            _concept("fiber-arch", "a thick recycled-fiber paper arch with one controlled fold", "tactile focal form and usable copy field", "wide horizontal composition", "large clean copy space on the right", PALETTES["tactile"], ("fiber specificity", "hero composition", "restrained accent"), layout_mode="hero_landscape"),
            _concept("frosted-stack", "three frosted glass panels with generous separation", "transparent layering without UI", "wide, lightly isometric composition", "large clean copy space on the left", PALETTES["tactile"], ("translucent material", "controlled depth", "clean typography field")),
            _concept("porcelain-pebbles", "a small set of matte porcelain pebbles with one paper base", "soft tactile balance", "centered low-profile composition", "clean copy space above", PALETTES["tactile"], ("ceramic material", "low visual noise", "thumbnail readability")),
            _concept("foam-horizon", "a single soft organic foam horizon with shallow relief", "calm dimensional background", "wide frontal material study", "large clean copy space in the upper half", PALETTES["tactile"], ("soft material", "copy-safe field", "controlled relief")),
            _concept("paper-valley", "folded uncoated paper forming one smooth valley", "directional visual flow", "horizontal close material study", "clean copy space on the upper left", PALETTES["tactile"], ("paper geometry", "directional layout", "non-generic texture")),
        ),
        notes="The broad phrase is visibly supplied; every asset must earn its place through a functional layout, not generic texture alone.",
    ),
    PortfolioLane(
        key="synthetic_media_trust",
        name="Trust in synthetic media",
        tier="secondary",
        evidence_confidence="medium",
        opportunity_id="C59",
        buyer_segment="editorial_content_teams",
        buyer_job="media-literacy editorial illustration and trust explainer",
        channel="web",
        asset_family="ui_3d_metaphor",
        asset_type="illustration",
        micro_niche="synthetic media verification and provenance",
        visual_language="clear editorial conceptual object",
        medium="transparent acrylic, paper, and matte ink-blue ceramic",
        commercial_use_cases=("article header", "media literacy lesson", "trust and safety page"),
        keywords=("synthetic media trust", "media literacy", "content provenance", "AI verification", "responsible sharing", "manipulated media", "source transparency", "digital trust", "content disclosure", "misinformation literacy", "editorial header", "trust and safety", "education campaign", "technology policy", "responsible AI"),
        test_cap=15,
        concepts=(
            _concept("source-capsule", "a transparent source capsule held by one folded paper cradle", "traceable origin without a seal", "object positioned on the left third with a full silhouette", "at least one third of the right side is clean white copy space", PALETTES["trust"], ("transparent containment", "paper cradle", "no news imagery")),
            _concept("evidence-frames", "three nested translucent frames with one clear connection thread", "layered verification", "vertical object with open center", "clean copy space left", PALETTES["trust"], ("verification sequence", "open structure", "editorial clarity")),
            _concept("clarity-lens", "a simple clear lens revealing a clean abstract layer beneath", "careful checking before sharing", "front-facing isolated object", "clean copy space above", PALETTES["trust"], ("review action", "no faces", "calm visual language")),
            _concept("share-gate", "a paper path passing through a transparent choice gate", "responsible sharing decision", "horizontal low-profile object", "clean copy space on the upper right", PALETTES["trust"], ("decision point", "source path", "no fake interface")),
            _concept("uncertainty-prism", "a faceted translucent prism separating one clear and one diffuse beam", "uncertainty before verification", "centered object with controlled shadow", "clean copy space left", PALETTES["trust"], ("uncertainty metaphor", "light behavior", "non-literal editorial")),
        ),
        notes="Avoid faces, actual news, broadcasters, checkmarks, seals, and fake phone interfaces.",
    ),
    PortfolioLane(
        key="returns_recommerce",
        name="Returns management and recommerce",
        tier="secondary",
        evidence_confidence="medium",
        opportunity_id="C26",
        buyer_segment="small_business_commerce",
        buyer_job="retail operations and reverse-logistics explainer",
        channel="web",
        asset_family="ui_3d_metaphor",
        asset_type="3d",
        micro_niche="returns, recovery, refurbishment, and resale workflow",
        visual_language="friendly operational conceptual 3D",
        medium="kraft paper, recycled plastic, and matte ceramic",
        commercial_use_cases=("retail SaaS page", "returns policy explainer", "sustainability report"),
        keywords=("returns management", "reverse logistics", "recommerce", "product return", "resale workflow", "returnable packaging", "refurbishment process", "circular retail", "ecommerce return loop", "value recovery", "retailer returns", "retail SaaS", "logistics platform", "sustainability report", "post holiday returns"),
        test_cap=15,
        concepts=(
            _concept("return-arc", "a reusable unlabelled parcel form following one clean circular return arc", "return flow without warehouse scene", "isometric standalone system object", "clean copy space right", PALETTES["returns"], ("reverse route", "no barcode", "operational clarity")),
            _concept("condition-sort", "three abstract condition tokens moving into distinct recovery paths", "condition assessment and routing", "centered modular object", "clean copy space left", PALETTES["returns"], ("state sorting", "color-coded without labels", "recommerce logic")),
            _concept("repair-bridge", "two material blocks joined by a small repair bridge", "refurbishment and retained value", "front-facing low profile object", "clean copy space above", PALETTES["returns"], ("recovery metaphor", "material continuity", "single visual mechanism")),
            _concept("resale-stack", "a balanced stack of recovered-value blocks with one circular route", "value recovery before disposal", "vertical centered object", "clean copy space right", PALETTES["returns"], ("retained value", "stacked hierarchy", "no retail branding")),
            _concept("return-tote", "a minimalist reusable tote shape forming a closed loop", "returnable container program", "side-view isolated object", "clean copy space left", PALETTES["returns"], ("reusable container", "simple silhouette", "no package label")),
        ),
        notes="This is intentionally a narrow alternative to generic workers, scanners, boxes, labels, and warehouse scenes.",
    ),
    PortfolioLane(
        key="digital_accessibility",
        name="Digital accessibility",
        tier="secondary",
        evidence_confidence="medium",
        opportunity_id="C37",
        buyer_segment="web_product_teams",
        buyer_job="inclusive design and adaptable access explainer",
        channel="web",
        asset_family="ui_3d_metaphor",
        asset_type="illustration",
        micro_niche="adaptable digital access and inclusive interaction",
        visual_language="respectful, calm conceptual editorial object",
        medium="matte ceramic, clear acrylic, and paper",
        commercial_use_cases=("public-service web page", "accessibility product education", "inclusive design training"),
        keywords=("digital accessibility", "inclusive design", "web accessibility", "accessible technology", "adaptable interface", "assistive technology concept", "equitable access", "keyboard navigation", "inclusive digital experience", "accessible product design", "flexible input mode", "information hierarchy", "public service website", "accessibility SaaS", "web design training"),
        test_cap=15,
        concepts=(
            _concept("input-hub", "a central adaptable hub with three clear raised paths", "multiple ways to participate without a literal interface", "object positioned on the left third with a full silhouette", "at least one third of the right side is clean white copy space", PALETTES["access"], ("adaptable paths", "raised material contrast", "respectful abstraction")),
            _concept("clear-route", "a clear raised path passing through a simple open arch", "findable navigation", "horizontal low-profile object", "clean copy space above", PALETTES["access"], ("navigation clarity", "spatial metaphor", "no icon shorthand")),
            _concept("contrast-layers", "three tactile layers with distinct material separation", "readable hierarchy and distinction", "front-facing stack", "clean copy space left", PALETTES["access"], ("clear hierarchy", "material contrast", "no compliance claim")),
            _concept("open-portal", "a quiet open portal with adjustable side elements", "access that adapts to different needs", "vertical centered object", "clean copy space right", PALETTES["access"], ("adaptability", "open participation", "no token symbols")),
            _concept("flexible-handle", "an abstract flexible handle joining interchangeable modules", "different interaction methods", "three-quarter standalone object", "clean copy space left", PALETTES["access"], ("interchangeability", "inclusive mechanism", "clear silhouette")),
        ),
        notes="An image cannot demonstrate accessibility compliance; involve affected users before expanding this lane.",
    ),
    PortfolioLane(
        key="retro_tech_developer_metaphors",
        name="Retro-tech developer metaphors",
        tier="experimental",
        evidence_confidence="medium",
        opportunity_id="C43",
        buyer_segment="web_product_teams",
        buyer_job="developer relations and coding editorial hero",
        channel="web",
        asset_family="retro_tech_nostalgia",
        asset_type="3d",
        micro_niche="brand-free retro computing metaphor",
        visual_language="gentle retro-future editorial 3D",
        medium="matte plastic, translucent acrylic, and soft phosphor glow",
        commercial_use_cases=("developer blog", "coding course", "software newsletter"),
        keywords=("retro tech", "lo-fi computing", "developer metaphor", "nostalgic technology", "fictional computer object", "analog digital", "retro future", "creative coding illustration", "retro developer visual", "lo-fi technology hero", "software concept object", "developer relations", "SaaS blog", "coding course", "technology newsletter"),
        test_cap=15,
        concepts=(
            _concept("cloud-module", "a single translucent modular tower with one cloud-shaped cutout opening", "portable developer ideas without a literal device", "object positioned on the left third with a full silhouette and a wide clean copy field on the right", "at least one third of the right side is clean white copy space", PALETTES["retro"], ("cloud-shaped cutout", "modular tower", "no device silhouette")),
            _concept("signal-antenna", "a small abstract antenna sculpture emitting three non-text signal ribbons", "connection and discovery", "vertical standalone object", "clean copy space left", PALETTES["retro"], ("analog signal", "no brand silhouette", "gentle energy")),
            _concept("module-tower", "a stack of blank retro-future modules with one transparent connector", "modular software building", "front-facing object", "clean copy space above", PALETTES["retro"], ("modularity", "blank surfaces", "developer relevance")),
            _concept("disk-garden", "three circular fictional storage forms growing from a minimal ceramic base", "maintained software ecosystem", "isometric isolated object", "clean copy space right", PALETTES["retro"], ("storage metaphor", "organic contrast", "no trademark shape")),
            _concept("command-block", "one keyboardless retro command block with a soft glowing slot", "simple developer control", "side-view single object", "clean copy space left", PALETTES["retro"], ("control metaphor", "no readable code", "retro-future finish")),
        ),
        notes="No real hardware silhouettes, logos, operating systems, readable code, keyboard layouts, or terminal text.",
    ),
    PortfolioLane(
        key="human_made_collage_elements",
        name="Human-made collage elements",
        tier="experimental",
        evidence_confidence="medium",
        opportunity_id="C44",
        buyer_segment="editorial_content_teams",
        buyer_job="editorial layout component and small-brand social accent",
        channel="social",
        asset_family="craft_element",
        asset_type="graphic",
        micro_niche="handmade abstract collage component",
        visual_language="cohesive tactile cut-paper editorial craft",
        medium="uncoated paper, woven fibre, and simple stitch-like texture",
        commercial_use_cases=("editorial layout", "small-brand social graphic", "presentation accent"),
        keywords=("collage element", "cut paper illustration", "handmade graphic", "editorial texture", "torn paper", "imperfect craft", "scrapbook style", "zine aesthetic", "isolated cut paper", "editorial asset", "tactile collage shape", "social media element", "editorial design", "small business social", "brand toolkit"),
        test_cap=10,
        concepts=(
            _concept("woven-loop", "a woven fibre loop with a single paper tab", "connection element for layouts", "single isolated craft element with a complete silhouette", "tight transparent framing with minimal clear margin", PALETTES["collage"], ("woven material", "reusable component", "clean silhouette"), product_kind="transparent_cutout", delivery_format="png", background_policy="transparent"),
            _concept("torn-arch", "one torn uncoated-paper arch with clear fibrous edge", "friendly editorial frame without border", "centered isolated component", "clean white surrounding space", PALETTES["collage"], ("edge specificity", "component utility", "no handwriting")),
            _concept("paper-burst", "one irregular paper burst with no lettering or symbol", "visual emphasis element", "centered isolated component", "clean white surrounding space", PALETTES["collage"], ("torn edge", "controlled irregularity", "no logo-like form")),
            _concept("folded-ribbon", "a folded paper ribbon bridge without text", "directional layout connector", "horizontal isolated component", "clean white surrounding space", PALETTES["collage"], ("paper fold", "directional composition", "non-verbal accent")),
            _concept("material-badge", "a blank material badge made of paper and woven fibre", "spotlight component without a symbol", "centered isolated component", "clean white surrounding space", PALETTES["collage"], ("blank badge", "material contrast", "no icon or seal")),
        ),
        notes="Do not imitate identifiable artists, handwriting, signatures, cultural insignia, or logo-like marks.",
    ),
    PortfolioLane(
        key="circular_packaging_systems",
        name="Circular packaging systems",
        tier="experimental",
        evidence_confidence="medium",
        opportunity_id="C21",
        buyer_segment="small_business_commerce",
        buyer_job="refill and reuse packaging-system explainer",
        channel="web",
        asset_family="ui_3d_metaphor",
        asset_type="3d",
        micro_niche="refill, return, and packaging material-flow system",
        visual_language="clean sustainable operational conceptual 3D",
        medium="recycled kraft fibre, matte ceramic, and clear recycled plastic",
        commercial_use_cases=("CPG sustainability page", "retail operations explainer", "circular economy report"),
        keywords=("circular packaging", "reusable packaging", "refill system", "packaging waste", "returnable container", "recycled material", "refill retail", "sustainable packaging concept", "packaging reuse loop", "ecommerce empty space", "recyclable material flow", "CPG sustainability", "retail operations", "packaging consultancy", "circular economy"),
        test_cap=10,
        concepts=(
            _concept("refill-capsule", "a blank refill capsule flowing into a reusable outer form", "refill without package claims", "isometric single system object", "clean copy space right", PALETTES["circular"], ("refill route", "unlabelled geometry", "material loop")),
            _concept("return-container", "three nested returnable container forms connected by one circular path", "return and reuse program", "centered modular object", "clean copy space left", PALETTES["circular"], ("nested containers", "reusable form", "no recycling icon")),
            _concept("material-ribbon", "a recycled-fibre ribbon looping through three blank material tiles", "material circulation", "wide low-profile object", "clean copy space above", PALETTES["circular"], ("material flow", "non-text system", "functional layout")),
            _concept("compact-parcel", "a minimal unlabelled parcel form nested tightly inside a protective shell", "reduced empty delivery space", "three-quarter isolated object", "clean copy space right", PALETTES["circular"], ("space reduction", "unbranded parcel", "no label")),
            _concept("recovery-bridge", "a paper-to-ceramic bridge joining two circular modules", "recovery before disposal", "front-facing object", "clean copy space left", PALETTES["circular"], ("recovery mechanism", "tactile materials", "no regulatory claim")),
        ),
        notes="No labels, recycling codes, environmental certification symbols, food claims, or brand packaging.",
    ),
    PortfolioLane(
        key="software_supply_chain_integrity",
        name="Software supply-chain integrity",
        tier="experimental",
        evidence_confidence="medium",
        opportunity_id="C08",
        buyer_segment="web_product_teams",
        buyer_job="DevSecOps integrity and dependency explainer",
        channel="web",
        asset_family="ui_3d_metaphor",
        asset_type="3d",
        micro_niche="software dependencies, verification, and trusted build flow",
        visual_language="precise conceptual technical 3D without cyber cliches",
        medium="graphite ceramic, clear acrylic, and matte paper",
        commercial_use_cases=("DevSecOps landing page", "developer training", "B2B cybersecurity report"),
        keywords=("software supply chain", "code integrity", "secure development", "SBOM concept", "dependency management", "build verification", "software provenance", "DevSecOps", "secure dependency chain", "software component verification", "trusted build pipeline", "cybersecurity SaaS", "developer education", "B2B report", "cyber resilience"),
        test_cap=10,
        concepts=(
            _concept("component-chain", "five clean modular components joined by a transparent integrity path", "dependency relationship without code", "wide horizontal object", "clean copy space above", PALETTES["integrity"], ("modular dependency", "no lock or shield", "build flow")),
            _concept("build-gate", "a paper-and-acrylic build path passing through one clear verification gate", "controlled build release", "isometric standalone object", "clean copy space right", PALETTES["integrity"], ("verification point", "source-to-release path", "no UI")),
            _concept("provenance-lattice", "a small lattice of blank source tiles connected by one clear route", "component provenance", "front-facing object", "clean copy space left", PALETTES["integrity"], ("source graph", "transparent connection", "no code text")),
            _concept("maintenance-route", "a simple route updating one central component from a neutral support module", "secure maintenance", "horizontal low-profile object", "clean copy space above", PALETTES["integrity"], ("maintenance concept", "clear update path", "no cyber shorthand")),
            _concept("integrity-bridge", "two stable graphite modules linked by a translucent bridge", "trusted handoff", "centered isolated object", "clean copy space right", PALETTES["integrity"], ("trusted connection", "material contrast", "clear silhouette")),
        ),
        notes="No padlocks, shields, hooded people, fingerprints, code text, dashboards, certification claims, or brand references.",
    ),
    PortfolioLane(
        key="native_vector_patterns",
        name="Native vector repeat patterns",
        tier="experimental",
        evidence_confidence="low",
        opportunity_id="V02",
        buyer_segment="design_and_content_teams",
        buyer_job="repeatable decorative background and editable pattern tile",
        channel="web",
        asset_family="generic",
        asset_type="graphic",
        micro_niche="repeatable geometric SVG pattern",
        visual_language="controlled geometric tile with editable repeated structure",
        medium="SVG pattern definitions and native geometry",
        commercial_use_cases=("decorative background", "packaging pattern study", "presentation texture"),
        keywords=("seamless pattern", "repeat background", "editable SVG pattern", "geometric tile", "decorative vector", "pattern design", "repeatable background", "native vector", "abstract geometry", "surface pattern"),
        test_cap=1,
        concepts=(
            _concept(
                "pattern-tile",
                "a repeatable geometric tile with alternating circles and a diamond path",
                "edge continuity without a visible border",
                "full square repeat field",
                "no copy space; pattern is the product",
                ("#164E63", "#F8FAFC", "#F59E0B"),
                ("repeatable tile", "edge continuity", "editable pattern geometry"),
                product_kind="native_vector",
                delivery_format="svg",
                background_policy="white",
            ),
        ),
        notes="Experimental tile lane; structural repeatability is tested locally, while visual utility and marketplace acceptance remain human review tasks.",
    ),
    PortfolioLane(
        key="native_vector_utility_sets",
        name="Native vector file-flow utility sets",
        tier="secondary",
        evidence_confidence="medium",
        opportunity_id="V02",
        buyer_segment="web_product_teams",
        buyer_job="coherent file-management action icon set for web, mobile UI, documentation, and presentations",
        channel="web",
        asset_family="generic",
        asset_type="icon_set",
        micro_niche="file-flow utility micro-set for upload, storage, and transfer actions",
        visual_language="bold geometric duotone utility icon system with consistent proportions",
        medium="editable SVG compound shapes and outlined strokes in one organized icon sheet",
        commercial_use_cases=("web and mobile UI", "file-management workflow", "cloud-storage documentation", "product onboarding", "presentation diagram system"),
        keywords=("file management icons", "file flow icon set", "upload download icons", "folder icon", "cloud storage icon", "sync icon", "archive icon", "file sharing icon", "editable SVG icons", "web UI icon set", "mobile UI icons", "bold geometric icons"),
        test_cap=1,
        concepts=(
            _concept(
                "file-flow-micro-set",
                "a compact set of eight distinct file-management action icons: folder, upload, download, cloud storage, sync, archive, file, and share",
                "consistent icon geometry communicates a complete file-flow workflow without text or brand references",
                "organized square icon sheet with eight clearly separated icons and consistent spacing",
                "transparent negative space between each icon; no reserved copy space",
                ("#164E63", "#F8FAFC", "#F59E0B"),
                ("coherent utility family", "eight distinct file actions", "consistent geometry", "editable compound shapes", "thumbnail readability"),
                product_kind="native_vector",
                delivery_format="svg",
                background_policy="transparent",
                isolation_policy="cluster",
            ),
        ),
        notes="Higher-value micro-set hypothesis grounded in marketplace signals about coverage, consistency, separate utility, and immediate reuse; one local icon-sheet trial only.",
    ),
    PortfolioLane(
        key="native_vector_elements",
        name="Native vector utility elements",
        tier="secondary",
        evidence_confidence="medium",
        opportunity_id="V01",
        buyer_segment="design_and_content_teams",
        buyer_job="file management and cloud workflow icon for web and mobile interfaces",
        channel="web",
        asset_family="generic",
        asset_type="icon",
        micro_niche="single recognizable folder upload action icon",
        visual_language="bold geometric functional icon with restrained hyper-minimal structure",
        medium="editable SVG paths, compound shapes, and outlined strokes",
        commercial_use_cases=("web and mobile UI", "file management workflow", "cloud storage documentation", "presentation diagram element"),
        keywords=("folder upload icon", "file management", "cloud workflow", "editable SVG", "native vector", "upload arrow", "folder symbol", "digital file storage", "web UI icon", "mobile UI icon", "bold geometric icon"),
        test_cap=1,
        concepts=(
            _concept(
                "folder-upload",
                "a single recognizable folder icon with one upward upload arrow integrated into the folder front",
                "folder silhouette and upward arrow clearly communicate a file upload action",
                "single centered icon with tight square product framing",
                "tight transparent margin with no reserved copy space",
                ("#164E63", "#F8FAFC", "#F59E0B"),
                ("recognizable folder silhouette", "integrated upload arrow", "bold geometric contrast", "thumbnail readability"),
                product_kind="native_vector",
                delivery_format="svg",
                background_policy="transparent",
            ),
            _concept(
                "modular-ribbon",
                "three modular geometric forms joined by one continuous ribbon",
                "connection and flow without interface or text",
                "single centered vector object",
                "clean surrounding margin",
                ("#164E63", "#F8FAFC", "#F59E0B"),
                ("editable path system", "clear silhouette", "non-generic rhythm"),
                product_kind="native_vector",
                delivery_format="svg",
                background_policy="transparent",
            ),
            _concept(
                "technical-badge",
                "a rounded technical badge with four radial connection lines and one central module",
                "structured system relationship without symbols or text",
                "single centered vector object",
                "clean surrounding margin",
                ("#164E63", "#F8FAFC", "#F59E0B"),
                ("radial structure", "editable geometry", "no typography"),
                product_kind="native_vector",
                delivery_format="svg",
                background_policy="white",
            ),
        ),
        notes="Deterministic SVG lane led by one buyer-legible folder-upload icon; abstract legacy concepts remain only for historical comparison and are not the default trial.",
    ),
)


def list_lanes() -> tuple[PortfolioLane, ...]:
    """Return the immutable initial lane registry in research priority order."""
    return PORTFOLIO_LANES


def lane_for(key: str) -> PortfolioLane:
    """Find a lane by its stable CLI key."""
    normalized = _slug(key)
    for lane in PORTFOLIO_LANES:
        if lane.key == normalized:
            return lane
    supported = ", ".join(lane.key for lane in PORTFOLIO_LANES)
    raise PortfolioError(f"Unsupported portfolio lane: {key}. Supported lanes: {supported}")


def validate_metadata_draft(metadata: PortfolioMetadataDraft) -> None:
    """Reject draft metadata that violates the machine-checkable policy boundary."""
    values = (metadata.title, *metadata.keywords)
    if not metadata.created_using_generative_ai:
        raise PortfolioError("Portfolio metadata must declare generative-AI creation.")
    if metadata.status != "human_review_required" or not metadata.human_review_required:
        raise PortfolioError("Portfolio metadata must require human review before submission.")
    if len(metadata.title.strip()) < 12:
        raise PortfolioError("Metadata title is too short to identify the asset accurately.")
    if len(metadata.keywords) < 8:
        raise PortfolioError("Metadata needs at least eight accurate keyword candidates.")
    lowered = " ".join(values).lower()
    if any(phrase in lowered for phrase in _BANNED_METADATA_PHRASES):
        raise PortfolioError("Metadata includes an unsafe phrase for marketplace submission.")
    if len(set(item.lower() for item in metadata.keywords)) != len(metadata.keywords):
        raise PortfolioError("Metadata keywords must not contain duplicate terms.")


def metadata_from_dict(value: object) -> PortfolioMetadataDraft:
    """Validate a reviewed metadata object before it can enter a master package."""
    if not isinstance(value, dict):
        raise PortfolioError("Reviewed metadata must be a JSON object.")
    keywords = value.get("keywords")
    checklist = value.get("reviewer_checklist")
    if not isinstance(keywords, (list, tuple)) or not all(isinstance(item, str) and item.strip() for item in keywords):
        raise PortfolioError("Reviewed metadata keywords must be non-empty strings.")
    if not isinstance(checklist, (list, tuple)) or not all(isinstance(item, str) and item.strip() for item in checklist):
        raise PortfolioError("Reviewed metadata checklist must contain non-empty strings.")
    required_strings = ("title", "people_or_property", "status", "marketplace_transaction_data")
    if any(not isinstance(value.get(key), str) or not value[key].strip() for key in required_strings):
        raise PortfolioError("Reviewed metadata has incomplete required text fields.")
    if not isinstance(value.get("created_using_generative_ai"), bool) or not isinstance(value.get("human_review_required"), bool):
        raise PortfolioError("Reviewed metadata requires explicit GenAI and human-review booleans.")
    draft = PortfolioMetadataDraft(
        title=value["title"].strip(),
        keywords=tuple(item.strip() for item in keywords),
        created_using_generative_ai=value["created_using_generative_ai"],
        people_or_property=value["people_or_property"].strip(),
        status=value["status"].strip(),
        human_review_required=value["human_review_required"],
        marketplace_transaction_data=value["marketplace_transaction_data"].strip(),
        reviewer_checklist=tuple(item.strip() for item in checklist),
    )
    validate_metadata_draft(draft)
    return draft


def _metadata_for(lane: PortfolioLane, concept: LaneConcept) -> PortfolioMetadataDraft:
    reviewed = REVIEWED_CONCEPT_METADATA.get((lane.key, concept.key), {})
    title = str(reviewed.get("title") or f"{lane.name}: {concept.subject}")
    raw_keywords = reviewed.get("keywords")
    raw_keyword_candidates = (
        tuple(raw_keywords)
        if isinstance(raw_keywords, tuple)
        else tuple(dict.fromkeys((*lane.keywords, *concept.originality_levers, lane.asset_type)))
    )
    keywords, _removed_nonvisual = filter_visual_keywords(raw_keyword_candidates)
    metadata = PortfolioMetadataDraft(
        title=title,
        keywords=keywords,
        created_using_generative_ai=True,
        people_or_property="none depicted; human review required to confirm",
        status="human_review_required",
        human_review_required=True,
        marketplace_transaction_data="DATA NOT PUBLICLY AVAILABLE",
        reviewer_checklist=(
            "Confirm the title and every retained keyword accurately describe the visible asset.",
            "Confirm no readable text, brand, logo, watermark, real person, or protected work appears.",
            "Confirm the visual does not make a legal, compliance, environmental, accessibility, medical, or security guarantee.",
            "Confirm the asset is materially distinct from already selected portfolio assets.",
            "Complete the marketplace-specific AI disclosure and any people/property fields truthfully.",
        ),
    )
    validate_metadata_draft(metadata)
    return metadata


def build_brief(lane_key: str, concept_key: str) -> PortfolioBrief:
    """Build one valid, standalone-first brief from an approved lane concept."""
    lane = lane_for(lane_key)
    normalized_concept = str(concept_key).strip().lower()
    try:
        concept = next(item for item in lane.concepts if item.key == normalized_concept)
    except StopIteration as exc:
        supported = ", ".join(item.key for item in lane.concepts)
        raise PortfolioError(f"Unsupported concept {concept_key!r} for {lane.key}. Supported concepts: {supported}") from exc

    brief_id = f"{lane.key}--{concept.key}"
    identity = identity_for(lane.key) if concept.delivery_format == "jpeg" else None
    quality_gates = (
        "one complete primary object or controlled system only",
        "no readable text, letters, numbers, labels, logos, trademarks, watermarks, stamps, or postmarks",
        "no people, hands, faces, bodies, screens, phones, computers, tools, devices, cables, or unrelated props",
        "no actual compliance, accessibility, environmental, security, medical, or legal guarantee",
        "marketplace metadata must match visible content",
        "human review is required before submission",
    )
    if lane.key == "animal_adoption_foster_helper_characters":
        quality_gates = (
            "one complete controlled trio of fictional animal characters only",
            "no readable text, letters, numbers, labels, logos, trademarks, watermarks, stamps, or postmarks",
            "no real people, human hands, human faces, human bodies, screens, phones, computers, tools, devices, or unrelated props",
            "no actual adoption, rescue, medical, safety, legal, or outcome guarantee",
            "marketplace metadata must match visible content",
            "human review is required before submission",
        )
    asset_spec = AssetSpec(
        asset_id=brief_id,
        market_opportunity_id=lane.opportunity_id,
        buyer_segment=lane.buyer_segment,
        buyer_job=lane.buyer_job,
        channel=lane.channel,
        asset_family=lane.asset_family,
        asset_type=lane.asset_type,
        micro_niche=lane.micro_niche,
        subject=concept.subject,
        visual_language=lane.visual_language,
        medium=lane.medium,
        product_kind=concept.product_kind,
        delivery_format=concept.delivery_format,
        layout_mode=concept.layout_mode,
        palette=concept.palette,
        composition=concept.composition,
        negative_space=concept.negative_space,
        background_policy=concept.background_policy,
        isolation_policy=concept.isolation_policy,
        text_policy="none",
        branding_policy="no_branding",
        originality_levers=concept.originality_levers,
        variation_policy="retain only materially distinct concepts; seed-only, crop-only, and color-only variants are rejected",
        commercial_use_cases=lane.commercial_use_cases,
        quality_gates=quality_gates,
        model_preferences=("resolution>=1024",),
        metadata_hints=(lane.key, lane.tier, concept.key, "generative_ai_disclosure_required"),
        extra_constraints=(
            f"Visual mechanism: {concept.visual_mechanism}.",
            "Do not add a scene, frame, border, interface, packaging label, dashboard, infographic, or decorative text.",
            "Honor the explicit product format and layout contract; do not add copy space unless the asset is sold as a hero or background product.",
        ),
        tags=(lane.key, concept.key, lane.tier),
        identity_signature=identity.signature if identity else "",
        identity_lighting=identity.lighting if identity else "",
        identity_framing=identity.framing if identity else "",
        identity_context=identity.context if identity else "",
        identity_distinctness=identity.distinctness if identity else (),
        identity_prohibited_shorthand=identity.prohibited_shorthand if identity else (),
    )
    prompt_package = compile_asset_prompt(asset_spec)
    metadata = _metadata_for(lane, concept)
    return PortfolioBrief(
        brief_id=brief_id,
        lane=lane,
        concept=concept,
        asset_spec=asset_spec,
        prompt_package=prompt_package,
        metadata=metadata,
    )


def plan_batch(lane_key: str, count: int) -> tuple[PortfolioBrief, ...]:
    """Return a bounded initial test plan using only distinct registered concepts."""
    lane = lane_for(lane_key)
    if count < 1:
        raise PortfolioError("Portfolio batch count must be at least one.")
    if count > lane.test_cap:
        raise PortfolioError(
            f"{lane.key} has an initial test cap of {lane.test_cap}; request a smaller batch before scaling."
        )
    if count > len(lane.concepts):
        raise PortfolioError(
            f"{lane.key} currently has {len(lane.concepts)} materially distinct seed concepts. "
            "Generate and review these before expanding with variation axes."
        )
    return tuple(build_brief(lane.key, concept.key) for concept in lane.concepts[:count])


def plan_manifest(lane_key: str, count: int) -> dict[str, object]:
    """Serialize a bounded batch plan for a project-local audit record."""
    lane = lane_for(lane_key)
    briefs = plan_batch(lane.key, count)
    return {
        "schema_version": 1,
        "kind": "stockforge.portfolio_batch_plan",
        "lane": {
            "key": lane.key,
            "name": lane.name,
            "tier": lane.tier,
            "evidence_confidence": lane.evidence_confidence,
            "opportunity_id": lane.opportunity_id,
            "test_cap": lane.test_cap,
            "marketplace_transaction_data": "DATA NOT PUBLICLY AVAILABLE",
            "notes": lane.notes,
        },
        "status": "planned",
        "human_review_required": True,
        "briefs": [brief.to_dict() for brief in briefs],
    }
