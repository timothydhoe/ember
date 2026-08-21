"""
wildfire.identity
~~~~~~~~~~~~~~~~~
Reads the shared ember identity file alight publishes.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

IDENTITY_FILE = Path.home() / ".ember-hearth" / "identity" / "identity.yml"


def resolve_colors() -> dict[str, str] | None:
    if os.environ.get("NO_COLOR") or not IDENTITY_FILE.exists():
        return None
    try:
        return yaml.safe_load(IDENTITY_FILE.read_text())["semantic"]
    except (yaml.YAMLError, KeyError, OSError):
        return None


def resolve_accent(tool: str = "wildfire") -> str | None:
    if os.environ.get("NO_COLOR") or not IDENTITY_FILE.exists():
        return None
    try:
        data = yaml.safe_load(IDENTITY_FILE.read_text(encoding="utf-8"))
        return data["tools"][tool]
    except (yaml.YAMLError, KeyError, OSError):
        return None
