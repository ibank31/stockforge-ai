"""Shared metadata rules for portfolio drafts and upload copies."""

from __future__ import annotations

NONVISUAL_METADATA_KEYWORDS = frozenset({
    "website hero background",
    "website background",
    "presentation cover",
    "brand system",
    "generative ai",
    "marketing landing page",
    "saas launch",
    "agency presentation",
    "social media element",
    "small business social",
})


def filter_visual_keywords(keywords: tuple[str, ...] | list[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return visual-only keywords and removed workflow/use-case terms."""
    kept: list[str] = []
    removed: list[str] = []
    seen: set[str] = set()
    for keyword in keywords:
        clean = keyword.strip()
        if not clean:
            continue
        folded = clean.casefold()
        if folded in NONVISUAL_METADATA_KEYWORDS:
            removed.append(clean)
        elif folded not in seen:
            kept.append(clean)
            seen.add(folded)
    return tuple(kept), tuple(removed)
