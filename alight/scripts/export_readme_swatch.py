"""
alight.export_readme_swatch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generate exports/palette-swatch.svg -- a full visual + text reference
of every color alight defines or derives: for READMEs, and for pulling
exact hex codes into other tools (logos, artwork, etc).

Five sections:
  1. ANSI       -- the 16 terminal slots
  2. Named      -- schemes/alight.yml's `named:` block
  3. Contrast   -- schemes/alight.yml's `contrast:` block: hard/medium/
                   soft, base + raised each. This is real source-of-
                   truth content now (see export_nvim.py's docstring),
                   not a derived value -- shown here for the same
                   reason Named and Semantic are.
  4. Semantic   -- schemes/alight.yml's `semantic:` block
  5. Neovim     -- computed only inside export_nvim.py, not present in
                   alight.yml itself. Imported from there rather than
                   re-implemented, since this script's entire job is to
                   report what the other exporters actually produce --
                   duplicating that math would risk silent drift if the
                   constants in export_nvim.py ever change. `guide` is
                   shown once per contrast level (it's the one nvim-
                   derived value that's background-dependent); the rest
                   don't vary by level, so they're shown once.

Usage:
    uv run scripts/export_readme_swatch.py

Embed in markdown:
    ![alight palette](alight/exports/palette-swatch.svg)
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml
from export_nvim import (
    CONTRAST_LEVELS,
    build_inks,
    build_roles,
    build_surfaces,
    compute_derived,
)

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_FILE = BASE_DIR / "exports" / "palette-swatch.svg"

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

SWATCH = 48
CELL_W = 100
COLS = 5
HEADER_H = 24
NAME_LABEL_H = 13
HEX_LABEL_H = 12
ROW_GAP = 6
ROW_H = SWATCH + NAME_LABEL_H + HEX_LABEL_H + ROW_GAP
SECTION_GAP = 26
PAD = 18


def contrast_items(scheme: dict) -> list[tuple[str, str]]:
    surfaces = build_surfaces(scheme)
    items: list[tuple[str, str]] = []
    for level in CONTRAST_LEVELS:
        items.append((f"contrast.{level}.base", surfaces[level]["base"]))
        items.append((f"contrast.{level}.raised", surfaces[level]["raised"]))
    return items


def neovim_derived(scheme: dict) -> list[tuple[str, str]]:
    g = build_inks(scheme)
    p = build_roles(scheme, "palette")
    sem = build_roles(scheme, "semantic")
    d = compute_derived(g, p, sem)
    surfaces = build_surfaces(scheme)

    items = [
        ("nvim.elevated_fg", d["elevated_fg"]),
        ("nvim.tag", d["tag"]),
        ("nvim.string", d["vivid_string"]),
        ("nvim.keyword", d["chalky_keyword"]),
        ("nvim.function", d["vivid_function"]),
    ]
    for level in CONTRAST_LEVELS:
        items.append((f"nvim.guide.{level}", surfaces[level]["guide"]))
    return items


def render_section(
    title: str, items: list[tuple[str, str]], x0: int, y0: int, fg: str, muted: str
) -> tuple[list[str], int]:
    parts = [
        f'<text x="{x0}" y="{y0 + 14}" font-family="monospace" font-size="13" '
        f'font-weight="bold" fill="{fg}">{title}</text>'
    ]
    y = y0 + HEADER_H
    rows = -(-len(items) // COLS)  # ceil division
    for i, (label, hexval) in enumerate(items):
        row, col = divmod(i, COLS)
        cell_x = x0 + col * CELL_W
        swatch_x = cell_x + (CELL_W - SWATCH) / 2
        text_x = cell_x + CELL_W / 2
        yy = y + row * ROW_H
        parts.append(
            f'<rect x="{swatch_x}" y="{yy}" width="{SWATCH}" height="{SWATCH}" rx="6" fill="{hexval}"/>'
        )
        parts.append(
            f'<text x="{text_x}" y="{yy + SWATCH + NAME_LABEL_H}" '
            f'font-family="monospace" font-size="9" fill="{fg}" text-anchor="middle">{label}</text>'
        )
        parts.append(
            f'<text x="{text_x}" y="{yy + SWATCH + NAME_LABEL_H + HEX_LABEL_H}" '
            f'font-family="monospace" font-size="8" fill="{muted}" text-anchor="middle">{hexval}</text>'
        )
    return parts, HEADER_H + rows * ROW_H


def build_svg(scheme: dict) -> str:
    palette = scheme["palette"]
    named = scheme["named"]
    semantic = scheme["semantic"]
    fg = palette["foreground"]
    muted = named.get("ash", fg)
    canvas_bg = scheme["contrast"]["medium"]["surface"]["base"]

    sections = [
        ("ANSI", [(key, scheme["ansi"][key]) for key in ANSI_ORDER]),
        ("Named", list(named.items())),
        ("Contrast (hard / medium / soft)", contrast_items(scheme)),
        ("Semantic", list(semantic.items())),
        ("Neovim-derived (not in alight.yml)", neovim_derived(scheme)),
    ]

    width = PAD * 2 + COLS * CELL_W
    y = PAD
    body_parts: list[str] = []
    for title, items in sections:
        parts, used_h = render_section(title, items, PAD, y, fg, muted)
        body_parts += parts
        y += used_h + SECTION_GAP
    height = y

    header = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="{canvas_bg}"/>',
    ]
    return "\n".join(header + body_parts + ["</svg>"])


def self_verify(scheme: dict, svg_text: str) -> bool:
    expected: list[str] = (
        [scheme["ansi"][key] for key in ANSI_ORDER]
        + [v for _, v in scheme["named"].items()]
        + [v for _, v in contrast_items(scheme)]
        + [v for _, v in scheme["semantic"].items()]
        + [v for _, v in neovim_derived(scheme)]
    )
    found = re.findall(r'<rect[^>]*fill="(#[0-9A-Fa-f]{6})"', svg_text)[1:]

    print("\nSelf-verification (written file -> extracted fill -> source):")
    ok = True
    for i, exp in enumerate(expected):
        got = found[i] if i < len(found) else None
        match = got is not None and got.upper() == exp.upper()
        ok &= match
        if not match:
            print(f"  [{i}] expected={exp} got={got or '?'} MISMATCH")
    print(
        "ALL MATCH -- safe to embed" if ok else "MISMATCHES FOUND -- do not embed yet"
    )
    return ok


def main() -> bool:
    if not SCHEME_FILE.exists():
        raise FileNotFoundError(f"Missing scheme file: {SCHEME_FILE}")

    scheme = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    svg_text = build_svg(scheme)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(svg_text, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")

    return self_verify(scheme, OUTPUT_FILE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
