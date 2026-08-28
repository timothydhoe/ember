"""
alight.generate_all
~~~~~~~~~~~~~~~~~
Regenerates every terminal export from schemes/alight.yml in one pass.

Usage:
    uv run scripts/generate_all.py
"""

from __future__ import annotations

import export_alacritty
import export_ghostty
import export_iterm2
import export_nvim
import export_readme_swatch
import export_terminal_app
import export_tmux
import export_vim
import install_identity
import validate_identity
from _ansi import bold, cyan, green, red


def section(name: str) -> None:
    print(cyan(bold(f"== {name} ==")))


def main() -> bool:
    section("validating identity.yml references")
    validate_identity.main()
    print()

    results: list[tuple[str, bool]] = []

    for name, module in [
        ("ghostty", export_ghostty),
        ("iterm2", export_iterm2),
        ("alacritty", export_alacritty),
        ("terminal_app", export_terminal_app),
        ("tmux", export_tmux),
        ("vim", export_vim),
        ("nvim", export_nvim),
        ("install_identity", install_identity),
        ("readme_swatch", export_readme_swatch),
    ]:
        section(name)
        results.append((name, module.main()))
        print()

    section("Summary")
    ok = True
    for name, passed in results:
        tag = green("OK") if passed else red("MISMATCH")
        print(f" {name:17s} {tag}")
        ok &= passed
    if not ok:
        print(
            bold(
                red(
                    "\nOne or more exports did not verify. Do not treat outputs as safe to use."
                )
            )
        )
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
