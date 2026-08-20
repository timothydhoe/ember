"""
Generate an alight Ghostty config fragment from schemes/alight.yml.

Usage:
    uv run scripts/export_ghostty.py

Then either add to ~/.config/ghostty/config or paste its contents directly into your config.
"""

from __future__ import annotations

from pathlib import Path
import re
import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_FILE = BASE_DIR / "terminal" / "ghostty" /"alight.conf"

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


def main() -> bool:
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    palette, ansi = data["palette"], data["ansi"]

    lines = [
        "# Generated from alight.yml -- do not edit by hand, re-run export_ghostty.py"
    ]
    for i, key in enumerate(ANSI_ORDER):
        lines.append(f"palette = {i}={ansi[key]}")
    lines += [
        f"background = {palette['background']}",
        f"foreground = {palette['foreground']}",
        f"cursor-color = {palette['cursor']}",
        f"cursor-text = {palette['background']}",
        f"selection-background = {palette['selection']}",
        f"selection-foreground = {palette['foreground']}",
    ]

    content = "\n".join(lines) + "\n"
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")

    # self-verify against alight.yml
    written = OUTPUT_FILE.read_text(encoding="utf-8")
    palette_lines = dict(re.findall(r"palette = (\d+)=(#[0-9A-Fa-f]{6})", written))
    kv = dict(re.findall(r"^(\S[\w-]*) = (#[0-9A-Fa-f]{6})$", written, re.MULTILINE))

    checks = [(palette_lines[str(i)], ansi[key]) for i, key in enumerate(ANSI_ORDER)]
    checks += [
        (kv["background"], palette["background"]),
        (kv["foreground"], palette["foreground"]),
        (kv["cursor-color"], palette["cursor"]),
        (kv["selection-background"], palette["selection"]),
    ]
    ok = all(got.upper() == expected.upper() for got, expected in checks)
    print("ALL MATCH -- safe to use" if ok else "MISMATCHES FOUND")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
