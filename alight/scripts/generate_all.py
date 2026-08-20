"""
alight.generate_all
~~~~~~~~~~~~~~~~~
Regenerates every terminal export from schemes/alight.yml in one pass.

Usage:
    uv run scripts/generate_all.py
"""

from __future__ import annotations

import validate_identity
import export_ghostty
import export_iterm2
import export_alacritty
import export_terminal_app
import export_preview


def main() -> bool:
    print("== validating identity.yml references ==")
    validate_identity.main()
    print()

    results: list[tuple[str, bool]] = []

    for name, module in [
        ("ghostty", export_ghostty),
        ("iterm2", export_iterm2),
        ("alacritty", export_alacritty),
        ("terminal_app", export_terminal_app),
    ]:
        print(f"== {name} ==")
        results.append((name, module.main()))
        print()

    print("== preview (writes preview.html) ==")
    export_preview.main()
    results.append(("preview", True))
    print()

    print("== Summary ==")
    ok = True
    for name, passed in results:
        print(f" {name:14s} {'OK' if passed else 'MISMATCH'}")
        ok &= passed
    if not ok:
        print(
            "\nOne or more exports did not verify. Do not treat outputs as safe to use."
        )
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
