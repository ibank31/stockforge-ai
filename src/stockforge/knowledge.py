"""Load structured domain knowledge packs into reality contracts."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .reality import RealityRules, RealityScene, ToolAffordance

_KNOWLEDGE_DIR = Path(__file__).with_name("knowledge")

def _scene(payload: dict[str, Any], item: dict[str, Any]) -> RealityScene:
    affordance = dict(item["affordance"])
    # Knowledge packs store the tool at workflow level; hydrate the runtime
    # contract here so existing packs remain valid without duplicated fields.
    affordance.setdefault("tool", item["tool"])
    return RealityScene(
        domain=payload["domain"], task=item["task"], problem=item["problem"], object=item["object"], tool=item["tool"],
        affordance=ToolAffordance(**affordance), human_action=item["human_action"], environment=item["environment"],
        buyer_job=item["buyer_job"], rules=RealityRules(tuple(item.get("must", ())), tuple(item.get("should", ())), tuple(item.get("must_not", ()))),
        visual_evidence=tuple(item.get("visual_evidence", ())),
    )

def load_construction_v1() -> list[RealityScene]:
    payload = json.loads((_KNOWLEDGE_DIR / "construction_v1.json").read_text(encoding="utf-8"))
    return [_scene(payload, item) for item in payload["workflows"]]

def get_construction_task(task_id: str) -> RealityScene:
    payload = json.loads((_KNOWLEDGE_DIR / "construction_v1.json").read_text(encoding="utf-8"))
    for item in payload["workflows"]:
        if item["id"] == task_id:
            return _scene(payload, item)
    raise KeyError(f"unknown construction task: {task_id}")
