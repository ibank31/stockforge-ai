from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
paths = {
    "global": ROOT / "data/research/global_traditional_food_asset_catalog.csv",
    "indonesia": ROOT / "data/research/indonesia_regional_food_asset_candidates.csv",
}

summary = {}
for name, path in paths.items():
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    priority_key = "priority_tier" if name == "global" else "priority"
    required = {priority_key, "country" if name == "global" else "region_or_city", "anchor_food_candidate" if name == "global" else "candidate_food", "validation_status", "confidence"}
    missing = sorted(required - set(rows[0])) if rows else sorted(required)
    priorities = Counter(row[priority_key] for row in rows)
    confidences = Counter(row["confidence"] for row in rows)
    summary[name] = {
        "path": str(path.relative_to(ROOT)),
        "row_count": len(rows),
        "missing_required_columns": missing,
        "priority_counts": dict(sorted(priorities.items())),
        "confidence_counts": dict(sorted(confidences.items())),
    }

out = ROOT / "data/research/food_catalog_summary.json"
out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
