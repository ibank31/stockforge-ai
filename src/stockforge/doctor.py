"""Environment diagnostics."""

from __future__ import annotations

import platform
import shutil
import sys
from dataclasses import dataclass

from .config import ConfigManager


@dataclass(slots=True)
class Check:
    name: str
    ok: bool
    detail: str


def run_doctor() -> list[Check]:
    config = ConfigManager().load()
    checks = [
        Check("Python", sys.version_info >= (3, 10), platform.python_version()),
        Check("Git", shutil.which("git") is not None, shutil.which("git") or "not found"),
        Check("Workspace", config.workspace.exists(), str(config.workspace)),
        Check("Database", config.database.exists(), str(config.database)),
    ]
    return checks
