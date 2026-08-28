"""
alight.install_identity

Publish dist/identity.yml to the live path other ember rools read:
    ~/.ember-hearth/identity/identity.yml

Usage:
    uv run scripts/install_identity.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

import export_identity

LIVE_FILE = Path.home() / ".ember-hearth" / "identity" / "identity.yml"


def main() -> bool:
    ok = export_identity.main()
    if not ok:
        print("export_identity reported a mismatch. Not installing.")
        return False

    LIVE_FILE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(export_identity.OUTPUT_FILE, LIVE_FILE)
    print(f"Installed -> {LIVE_FILE}")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
