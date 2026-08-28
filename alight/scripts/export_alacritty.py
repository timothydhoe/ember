"""
export_alacritty
~~~~~~~~~~~~~~~~

Usage:
    uv run scripts/export_alacritty.py

Either import the one you want from your main alacritty.toml:
    [general]
    import = ["/path/to/alight-medium.toml"]
or paste its [colors...] tables directly into your config.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_DIR = BASE_DIR / "terminal" / "alacritty"

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
]


def build(palette: dict, ansi: dict, surface: dict) -> str:
    background = surface["base"]
    lines = [
        "# Generated from alight.yml -- do not edit by hand, re-run export_alacritty.py",
        "",
        "[colors.primary]",
        f'background = "{background}"',
        f'foreground = "{palette["foreground"]}"',
        "",
        "[colors.cursor]",
        f'text = "{background}"',
        f'cursor = "{palette["cursor"]}"',
        "",
        "[colors.selection]",
        f'text = "{palette["foreground"]}"',
        f'background = "{palette["selection"]}"',
        "",
        "[colors.normal]",
    ]
    for key in ANSI_ORDER:
        lines.append(f'{key} = "{ansi[key]}"')
    lines += ["", "[colors.bright]"]
    for key in ANSI_ORDER:
        lines.append(f'{key} = "{ansi[f"bright_{key}"]}"')

    return "\n".join(lines) + "\n"


def self_verify(content: str, palette: dict, ansi: dict, surface: dict) -> bool:
    sections = {}
    current = None
    for line in content.splitlines():
        m = re.match(r"\[colors\.(\w+)\]", line)
        if m:
            current = m.group(1)
            sections[current] = {}
            continue
        m = re.match(r'(\w+) = "(#[0-9A-Fa-f]{6})"', line)
        if m and current:
            sections[current][m.group(1)] = m.group(2)

    checks = [
        (sections["primary"]["background"], surface["base"]),
        (sections["primary"]["foreground"], palette["foreground"]),
        (sections["cursor"]["cursor"], palette["cursor"]),
        (sections["selection"]["background"], palette["selection"]),
    ]
    checks += [(sections["normal"][k], ansi[k]) for k in ANSI_ORDER]
    checks += [(sections["bright"][k], ansi[f"bright_{k}"]) for k in ANSI_ORDER]

    return all(got.upper() == expected.upper() for got, expected in checks)


def main() -> bool:
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    palette, ansi = data["palette"], data["ansi"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for level in CONTRAST_LEVELS:
        surface = data["contrast"][level]["surface"]
        content = build(palette, ansi, surface)
        out = OUTPUT_DIR / f"alight-{level}.toml"
        out.write_text(content, encoding="utf-8")
        print(f"Wrote {out}")

        written = out.read_text(encoding="utf-8")
        level_ok = self_verify(written, palette, ansi, surface)
        ok &= level_ok
        print(f"  {level}: {'ALL MATCH' if level_ok else 'MISMATCHES FOUND'}")

    print("ALL MATCH -- safe to import" if ok else "MISMATCHES FOUND")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
