"""Platform-aware metadata and discoverability safeguards.

This module does not scrape, rank, or manipulate marketplace search results. It
projects one canonical visual inventory into platform-specific metadata limits
and rejects obvious irrelevance, duplicates, trademark-like terms, and keyword
spam patterns before human review.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Literal


Platform = Literal["adobe_stock", "shutterstock", "freepik", "creative_market", "etsy"]


@dataclass(frozen=True, slots=True)
class PlatformMetadataPolicy:
    platform: Platform
    title_max_chars: int
    min_keywords: int
    max_keywords: int
    preferred_keywords: int
    first_keywords_prioritized: bool
    category_required: bool
    category_max: int
    ai_label_supported: bool


POLICIES: dict[Platform, PlatformMetadataPolicy] = {
    "adobe_stock": PlatformMetadataPolicy("adobe_stock", 70, 5, 50, 10, True, True, 1, True),
    "shutterstock": PlatformMetadataPolicy("shutterstock", 2048, 7, 50, 15, False, True, 2, True),
    "freepik": PlatformMetadataPolicy("freepik", 1_000, 8, 50, 18, True, False, 0, True),
    "creative_market": PlatformMetadataPolicy("creative_market", 120, 5, 10, 8, False, True, 1, True),
    "etsy": PlatformMetadataPolicy("etsy", 140, 13, 13, 13, False, True, 1, True),
}


@dataclass(frozen=True, slots=True)
class MetadataValidationReport:
    platform: Platform
    title: str
    keywords: tuple[str, ...]
    category: str | None
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    removed_keywords: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _clean(value: str) -> str:
    return " ".join(value.strip().split())


def _token_stems(value: str) -> tuple[str, ...]:
    tokens = re.findall(r"[a-z0-9]+", value.casefold())
    return tuple(token[:-1] if len(token) > 4 and token.endswith("s") else token for token in tokens)


def _spam_stems(keywords: tuple[str, ...]) -> tuple[str, ...]:
    counts: dict[str, int] = {}
    for keyword in keywords:
        for stem in set(_token_stems(keyword)):
            counts[stem] = counts.get(stem, 0) + 1
    # Common category nouns such as "icon" may legitimately recur in varied
    # compounds. Only flag an extreme concentration across one metadata list;
    # exact duplicates are handled separately and remain an error signal.
    threshold = max(4, int(len(keywords) * 0.75 + 0.999))
    return tuple(sorted(stem for stem, count in counts.items() if count >= threshold))


def _platform(value: str) -> Platform:
    key = value.strip().casefold()
    if key not in POLICIES:
        supported = ", ".join(POLICIES)
        raise ValueError(f"Unsupported metadata platform {value!r}; choose one of: {supported}.")
    return key  # type: ignore[return-value]


def project_metadata(
    platform: str,
    *,
    title: str,
    keywords: tuple[str, ...] | list[str],
    category: str | None = None,
) -> MetadataValidationReport:
    """Validate and conservatively project canonical metadata to one platform.

    The function never invents keywords. It keeps first occurrence order, drops
    empty and exact-duplicate entries, and reports every removal or policy
    problem for human review.
    """
    selected = _platform(platform)
    policy = POLICIES[selected]
    clean_title = _clean(title)
    kept: list[str] = []
    removed: list[str] = []
    seen: set[str] = set()
    for raw in keywords:
        item = _clean(str(raw))
        if not item:
            continue
        folded = item.casefold()
        if folded in seen:
            removed.append(item)
            continue
        seen.add(folded)
        kept.append(item)
    errors: list[str] = []
    warnings: list[str] = []
    if not clean_title:
        errors.append("title is required")
    if len(clean_title) > policy.title_max_chars:
        errors.append(f"title exceeds {policy.title_max_chars} characters for {selected}")
    if len(kept) < policy.min_keywords:
        errors.append(f"at least {policy.min_keywords} keywords are required for {selected}")
    if len(kept) > policy.max_keywords:
        errors.append(f"at most {policy.max_keywords} keywords are allowed for {selected}")
    if policy.category_required and not _clean(category or ""):
        errors.append(f"a relevant category is required for {selected}")
    if policy.category_max and category and len([part for part in category.split(",") if _clean(part)]) > policy.category_max:
        errors.append(f"at most {policy.category_max} category is allowed for {selected}")
    if len(kept) > policy.preferred_keywords:
        warnings.append(f"keyword count exceeds the preferred {policy.preferred_keywords}; keep only defensible terms")
    repeated = _spam_stems(tuple(kept))
    if repeated:
        errors.append("repeated keyword stems suggest spam: " + ", ".join(repeated))
    title_stems = _token_stems(clean_title)
    if len(title_stems) != len(set(title_stems)):
        errors.append("title contains repeated word stems")
    if any("brand" in item.casefold() or "trademark" in item.casefold() for item in kept):
        errors.append("brand/trademark metadata requires manual rights review")
    if removed:
        warnings.append("exact duplicate keywords were removed")
    if policy.first_keywords_prioritized and kept:
        warnings.append(f"the first {min(10, len(kept))} keywords should carry the strongest visual relevance")
    return MetadataValidationReport(
        platform=selected,
        title=clean_title,
        keywords=tuple(kept),
        category=_clean(category) if category else None,
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        removed_keywords=tuple(removed),
    )


def rank_canonical_keywords(
    keywords: tuple[str, ...] | list[str],
    *,
    visible_terms: tuple[str, ...] | list[str],
    buyer_job_terms: tuple[str, ...] | list[str],
) -> tuple[str, ...]:
    """Rank existing keywords by visible evidence before buyer-job context.

    This is a deterministic relevance ordering, not a popularity or ranking
    prediction. Terms absent from the canonical candidate list are never added.
    """
    visible = {term.casefold() for term in visible_terms}
    buyer = {term.casefold() for term in buyer_job_terms}
    unique: list[str] = []
    seen: set[str] = set()
    for raw in keywords:
        item = _clean(str(raw))
        folded = item.casefold()
        if item and folded not in seen:
            unique.append(item)
            seen.add(folded)
    return tuple(sorted(unique, key=lambda item: (
        0 if item.casefold() in visible else 1 if item.casefold() in buyer else 2,
        unique.index(item),
    )))
