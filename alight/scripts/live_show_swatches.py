"""
Print every color alight.yml actually puts on screen, labeled, using only
what Terminal.app can genuinely render: the 16 indexed ANSI slots (0-15).

Run this AFTER importing alight.terminal and setting it as the active
profile for this window -- otherwise you're just looking at whatever
profile was already active.

    uv run scripts/live_show_swatches.py
"""

from __future__ import annotations

from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"

RESET = "\x1b[0m"

ANSI_ORDER = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white",
]


def swatch(index: int, label: str) -> str:
    block = f"\x1b[48;5;{index}m    {RESET}"
    return f"{block} {index:2d}  {label}"


def main():
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    named = data["named"]
    ansi = data["ansi"]
    semantic = data.get("semantic", {})

    hex_to_name = {v.upper(): k for k, v in named.items()}
    hex_to_ansi_index = {ansi[key].upper(): i for i, key in enumerate(ANSI_ORDER)}

    print("== The 16 ANSI slots Terminal.app actually renders ==\n")
    for i, key in enumerate(ANSI_ORDER):
        hexval = ansi[key]
        name = hex_to_name.get(hexval.upper(), "?")
        print(swatch(i, f"ansi.{key:15s} = {name:10s} {hexval}"))

    print("\n== Plain text, no codes -- this is your real foreground/background ==\n")
    print("  The quick brown fox jumps over the lazy dog.")

    print("\n== Semantic roles -- shown via their ANSI slot where one exists ==\n")
    for role, hexval in semantic.items():
        name = hex_to_name.get(hexval.upper(), "?")
        index = hex_to_ansi_index.get(hexval.upper())
        if index is not None:
            print(swatch(index, f"semantic.{role:10s} = {name:10s} {hexval}"))
        else:
            print(
                f"  (no ANSI slot) semantic.{role:10s} = {name:10s} {hexval}  "
                f"-- not wired to any of the 16, can't render exactly here"
            )

    print("\n== Not shown: selection & cursor ==")
    print("  Those aren't swatchable via SGR codes -- select some text, and")
    print("  look at your actual cursor, to check those two by eye.")


if __name__ == "__main__":
    main()
