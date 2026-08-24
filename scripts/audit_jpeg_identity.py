from __future__ import annotations

import json
from collections import Counter

from stockforge.portfolio import build_brief, list_lanes


JPEG_LANES = [lane for lane in list_lanes() if lane.concepts and lane.concepts[0].delivery_format == "jpeg"]

rows: list[dict[str, object]] = []
material_counts: Counter[str] = Counter()
palette_counts: Counter[str] = Counter()
composition_counts: Counter[str] = Counter()
policy_counts: Counter[str] = Counter()

for lane in JPEG_LANES:
    brief = build_brief(lane.key, lane.concepts[0].key)
    concept = brief.concept
    material_counts[lane.medium] += 1
    palette_counts[" / ".join(concept.palette)] += 1
    composition_counts[concept.composition] += 1
    policy_counts[f"{concept.delivery_format}/{concept.layout_mode}/{concept.isolation_policy}/{concept.background_policy}"] += 1
    rows.append(
        {
            "lane": lane.key,
            "tier": lane.tier,
            "evidence_confidence": lane.evidence_confidence,
            "buyer_job": lane.buyer_job,
            "visual_language": lane.visual_language,
            "medium": lane.medium,
            "palette": list(concept.palette),
            "first_concept": concept.key,
            "first_subject": concept.subject,
            "first_mechanism": concept.visual_mechanism,
            "first_composition": concept.composition,
            "first_negative_space": concept.negative_space,
            "originality_levers": list(concept.originality_levers),
            "prompt_isolation_policy": concept.isolation_policy,
            "prompt_background_policy": concept.background_policy,
            "prompt_negative_policy": "scene" if concept.isolation_policy == "scene" else "standalone",
        }
    )

print(
    json.dumps(
        {
            "jpeg_lane_count": len(rows),
            "lanes": rows,
            "shared_medium_count": dict(material_counts),
            "shared_palette_count": dict(palette_counts),
            "shared_first_composition_count": dict(composition_counts),
            "policy_count": dict(policy_counts),
            "notice": "Registry audit only; no generation, provider call, marketplace action, or sales inference.",
        },
        indent=2,
        sort_keys=True,
    )
)
