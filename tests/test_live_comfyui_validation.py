"""Contract tests for optional live ComfyUI validation.

These tests validate configuration and skip safely unless an explicit live endpoint
is provided. CI must never pretend that a mocked provider proves a real ComfyUI run.
"""

from __future__ import annotations

import os

import pytest

from stockforge.comfyui import ComfyUIConfig


@pytest.mark.skipif(not os.getenv("STOCKFORGE_COMFYUI_URL"), reason="live ComfyUI endpoint not configured")
def test_live_comfyui_endpoint_is_configured() -> None:
    url = os.environ["STOCKFORGE_COMFYUI_URL"].strip()
    config = ComfyUIConfig(base_url=url)
    assert config.base_url == url.rstrip("/")


def test_live_validation_is_opt_in() -> None:
    # A live network test must never be silently enabled in normal CI.
    assert os.getenv("STOCKFORGE_LIVE_COMFYUI", "0") in {"0", "1"}
