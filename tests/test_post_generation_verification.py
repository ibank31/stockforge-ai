from pathlib import Path

import pytest
from PIL import Image

from stockforge.post_generation_verification import (
    require_post_generation_distance,
    verify_generated_candidate,
)


def test_identical_candidate_is_blocked(tmp_path: Path) -> None:
    reference = tmp_path / "reference.png"
    candidate = tmp_path / "candidate.png"
    Image.new("RGB", (64, 64), "orange").save(reference)
    Image.new("RGB", (64, 64), "orange").save(candidate)

    result = verify_generated_candidate(reference, candidate)

    assert result.decision == "BLOCK"
    assert result.similarity.level == "blocked"
    with pytest.raises(ValueError):
        require_post_generation_distance(reference, candidate)


def test_distinct_candidate_requires_human_review(tmp_path: Path) -> None:
    reference = tmp_path / "reference.png"
    candidate = tmp_path / "candidate.png"
    Image.new("RGB", (64, 64), "black").save(reference)
    Image.new("RGB", (64, 64), "white").save(candidate)

    result = verify_generated_candidate(reference, candidate)

    assert result.decision == "REVIEW"
    assert result.similarity.level != "blocked"
