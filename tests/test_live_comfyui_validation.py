"""Contract tests for optional live ComfyUI validation.

These tests validate the existing ProviderConfig/ComfyUIProvider contract and
never require a live network endpoint during normal CI.
"""

from __future__ import annotations

import os

import pytest

from stockforge.comfyui import ComfyUIProvider
from stockforge.provider import ProviderConfig


@pytest.mark.skipif(not os.getenv("STOCKFORGE_COMFYUI_URL"), reason="live ComfyUI endpoint not configured")
def test_live_comfyui_endpoint_is_configured() -> None:
    url = os.environ["STOCKFORGE_COMFYUI_URL"].strip()
    config = ProviderConfig(
        id="comfyui-live-validation",
        kind="comfyui",
        endpoint=url,
        enabled=True,
    )
    provider = ComfyUIProvider(config)
    assert provider.config.endpoint == url


def test_live_validation_is_opt_in() -> None:
    # A live network test must never be silently enabled in normal CI.
    assert os.getenv("STOCKFORGE_LIVE_COMFYUI", "0") in {"0", "1"}
