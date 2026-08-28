"""
export_ghostty
~~~~~~~~~~~~~~

Usage:
    uv run scripts/export_ghostty.py

Then either add the one you want to ~/.config/ghostty/config or paste
its contents directly into your config.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_DIR = BASE_DIR / "terminal" / "ghostty"

CONTRAST_LEVELS = ["hard", "medium", "soft"]

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


def build(palette: dict, ansi: dict, surface: dict) -> str:
    background = surface["base"]
    lines = [
        "# Generated from alight.yml -- do not edit by hand, re-run export_ghostty.py"
    ]
    for i, key in enumerate(ANSI_ORDER):
        lines.append(f"palette = {i}={ansi[key]}")
    lines += [
        f"background = {background}",
        f"foreground = {palette['foreground']}",
        f"cursor-color = {palette['cursor']}",
        f"cursor-text = {background}",
        f"selection-background = {palette['selection']}",
        f"selection-foreground = {palette['foreground']}",
    ]

    return "\n".join(lines) + "\n"


def self_verify(content: str, palette: dict, ansi: dict, surface: dict) -> bool:
    palette_lines = dict(re.findall(r"palette = (\d+)=(#[0-9A-Fa-f]{6})", content))
    kv = dict(re.findall(r"^(\S[\w-]*) = (#[0-9A-Fa-f]{6})$", content, re.MULTILINE))

    checks = [(palette_lines[str(i)], ansi[key]) for i, key in enumerate(ANSI_ORDER)]
    checks += [
        (kv["background"], surface["base"]),
        (kv["foreground"], palette["foreground"]),
        (kv["cursor-color"], palette["cursor"]),
        (kv["selection-background"], palette["selection"]),
    ]
    return all(got.upper() == expected.upper() for got, expected in checks)


def main() -> bool:
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    palette, ansi = data["palette"], data["ansi"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for level in CONTRAST_LEVELS:
        surface = data["contrast"][level]["surface"]
        content = build(palette, ansi, surface)
        out = OUTPUT_DIR / f"alight-{level}.conf"
        out.write_text(content, encoding="utf-8")
        print(f"Wrote {out}")

        written = out.read_text(encoding="utf-8")
        level_ok = self_verify(written, palette, ansi, surface)
        ok &= level_ok
        print(f"  {level}: {'ALL MATCH' if level_ok else 'MISMATCHES FOUND'}")

    print("ALL MATCH -- safe to use" if ok else "MISMATCHES FOUND")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
