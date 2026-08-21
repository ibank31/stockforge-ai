"""Reality-aware scene compiler for StockForge.

This module intentionally does not claim to replace professional standards. It
encodes conservative scene constraints so prompts describe a coherent physical
workflow before GPU generation is requested.
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Workflow:
    task: str
    tool: str
    target: str
    action: str
    evidence: str
    environment: str
    must: tuple[str, ...]
    should: tuple[str, ...]
    must_not: tuple[str, ...]


WORKFLOWS: Dict[str, Workflow] = {
    "wall_moisture_inspection": Workflow(
        task="investigate suspected moisture in a building material",
        tool="a suitable building-material moisture meter",
        target="the affected wall or other building material surface",
        action="place or scan the meter against the material according to the instrument design while examining the reading",
        evidence="a plausible damp or stained area and clear contact between the instrument and the material",
        environment="an authentic building interior undergoing inspection",
        must=("the meter interacts with the wall/material", "the inspector attends to the measurement", "the target is a plausible building material"),
        should=("subtle water staining or discoloration", "clipboard or inspection notes", "natural site imperfections"),
        must_not=("floating meter", "meter pointed into empty air", "holographic moisture graphics", "unrelated futuristic interface"),
    ),
    "room_dimensional_measurement": Workflow(
        task="measure a room dimension for construction or documentation",
        tool="a handheld laser distance meter",
        target="a physically plausible opposite wall or defined measurement point",
        action="aim the distance meter from the measurement origin toward the intended target",
        evidence="clear geometric relationship between inspector, device, room and target wall",
        environment="a real interior room under construction, renovation or documentation",
        must=("device aims toward a measurable target", "room geometry supports the measurement", "human position is physically plausible"),
        should=("architectural notes or clipboard", "clean copy space", "natural construction context"),
        must_not=("random laser direction", "device aimed at a person", "use as a total station", "floating dimensions or HUD"),
    ),
    "door_window_measurement": Workflow(
        task="verify a door or window opening dimension",
        tool="a laser distance meter or tape measure appropriate to the measurement",
        target="the actual jamb, sill, head or opposite edge of the opening being measured",
        action="measure directly across the physical opening",
        evidence="the tool is visibly related to the opening geometry",
        environment="a real construction or renovation site",
        must=("opening is visible", "tool is physically related to the measured span"),
        should=("installation materials", "measurement notes"),
        must_not=("tool disconnected from opening", "random measuring pose", "floating geometry"),
    ),
    "concrete_crack_inspection": Workflow(
        task="inspect a visible crack in a concrete element",
        tool="an appropriate crack gauge, ruler, flashlight or inspection aid",
        target="the actual crack on a concrete surface",
        action="align the inspection aid with the defect and examine or document it",
        evidence="crack and inspection aid share the same physical surface",
        environment="an authentic concrete structure or construction site",
        must=("crack is physically attached to concrete", "inspection aid targets the defect"),
        should=("inspection notes", "natural concrete texture"),
        must_not=("floating crack", "unrelated tool", "digital crack overlay"),
    ),
    "rebar_scanning": Workflow(
        task="scan concrete to locate embedded reinforcement",
        tool="a concrete rebar or cover scanner",
        target="the surface of a reinforced concrete element",
        action="move the scanner across or against the concrete surface according to its design",
        evidence="scanner and concrete surface have a clear physical relationship",
        environment="a real structural concrete construction or renovation site",
        must=("scanner is on/near concrete", "structural element is visible"),
        should=("grid marks or notes where appropriate", "realistic structural context"),
        must_not=("scanner floating in air", "scanner used like a generic camera", "holographic reinforcement overlay"),
    ),
    "concrete_cover_measurement": Workflow(
        task="inspect or estimate reinforcement cover depth in concrete",
        tool="an appropriate cover meter or rebar locator",
        target="a reinforced concrete surface",
        action="position and scan the instrument across the concrete surface",
        evidence="concrete element and instrument interaction are visible",
        environment="a real structural inspection setting",
        must=("instrument interacts with concrete", "task concerns embedded reinforcement"),
        should=("inspection notes", "professional QA/QC context"),
        must_not=("exposed rebar treated as the instrument target without context", "floating scanner"),
    ),
    "thermal_inspection": Workflow(
        task="investigate a justified thermal anomaly in a building or equipment context",
        tool="a handheld thermal imaging camera",
        target="a wall, ceiling, electrical component, HVAC component, pipe or other justified target",
        action="aim the thermal camera toward the target from a plausible inspection position",
        evidence="camera, inspector and target form a coherent inspection relationship",
        environment="an authentic building or equipment inspection environment",
        must=("camera aims at a real target", "target is relevant to thermal inspection"),
        should=("professional inspection context", "subtle environmental cues"),
        must_not=("camera aimed randomly", "decorative thermal graphics", "sci-fi interface"),
    ),
    "floor_level_check": Workflow(
        task="check floor or construction element level",
        tool="a laser level or appropriate leveling instrument",
        target="a physical wall, floor or construction reference",
        action="position the instrument to establish a plausible level reference",
        evidence="reference line/surface has a believable relationship to the instrument",
        environment="an authentic construction or renovation site",
        must=("instrument has a physical reference", "scene communicates leveling rather than distance measurement"),
        should=("floor installation context", "construction notes"),
        must_not=("laser level used as a distance meter", "arbitrary glowing geometry"),
    ),
    "concrete_surface_inspection": Workflow(
        task="visually inspect concrete surface condition or workmanship",
        tool="an appropriate visual inspection aid such as flashlight, ruler or camera",
        target="the actual concrete surface or detail",
        action="direct attention and the inspection aid toward the surface",
        evidence="inspector and surface are physically connected by the inspection action",
        environment="an authentic construction or maintenance setting",
        must=("inspection target is visible", "action targets the surface"),
        should=("subtle normal concrete variation", "professional documentation context"),
        must_not=("unexplained defects", "floating inspection tools"),
    ),
    "construction_safety_inspection": Workflow(
        task="inspect construction-site safety conditions",
        tool="a checklist, clipboard, camera or appropriate inspection aid",
        target="real site conditions such as access routes, barriers, PPE, housekeeping or work areas",
        action="observe and document a specific site condition",
        evidence="inspector is visibly evaluating a real safety condition",
        environment="an active but controlled construction site",
        must=("a specific safety observation exists", "inspector action relates to that observation"),
        should=("appropriate PPE", "real barriers and signage"),
        must_not=("dangerous behavior staged for drama", "unrelated equipment"),
    ),
}


def reality_preflight(task_id: str) -> Workflow:
    """Return a validated workflow or raise a clear error before GPU use."""
    key = str(task_id).strip().lower()
    if key not in WORKFLOWS:
        raise ValueError(f"Unknown reality workflow: {task_id}")
    workflow = WORKFLOWS[key]
    if not workflow.tool or not workflow.target or not workflow.action:
        raise ValueError(f"Incomplete reality workflow: {task_id}")
    return workflow


def compile_prompt(user_prompt: str, task_id: str = "wall_moisture_inspection") -> str:
    """Compile a user concept with deterministic physical-reality constraints."""
    workflow = reality_preflight(task_id)
    base = str(user_prompt or "").strip()
    if not base:
        raise ValueError("Prompt is required")

    must = "; ".join(workflow.must)
    should = "; ".join(workflow.should)
    must_not = "; ".join(workflow.must_not)

    return f"""{base}

REALITY-ANCHORED PROFESSIONAL WORKFLOW:
Task: {workflow.task}.
Tool: {workflow.tool}.
Target: {workflow.target}.
Human action: {workflow.action}.
Visible evidence: {workflow.evidence}.
Environment: {workflow.environment}.
Required physical cues: {must}.
Preferred supporting cues: {should}.
Do not depict: {must_not}.

Everything visible must be physically coherent. The tool must interact with its intended target in a way consistent with the stated task. The person must be performing the task rather than merely posing with equipment. Avoid decorative technology that is not required by the physical workflow. Photographic realism and commercial stock usability are required."""
