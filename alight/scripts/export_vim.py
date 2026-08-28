"""
alight.export_vim
~~~~~~~~~~~~~~~~~~
Generate a Vim colorscheme (colors/alight.vim) from schemes/alight.yml.


Nothing here is meant to be hand-edited after generation -- change
schemes/alight.yml, or the mapping below, and regenerate.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from _oklch import hex_to_oklch, oklch_to_hex

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_FILE = BASE_DIR / "terminal" / "vim" / "colors" / "alight.vim"

CONTRAST_LEVELS = ["hard", "medium", "soft"]
DEFAULT_CONTRAST = "medium"

ANSI_SLOT_NAMES = [
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

HEADER = (
    '" alight.vim -- generated from schemes/alight.yml by export_vim.py\n'
    '" do not hand-edit; change the source palette or the role mapping\n'
    '" in export_vim.py instead, then regenerate.\n'
)


@dataclass(frozen=True)
class Ink:
    hex: str
    cterm: str = "NONE"


class Surface:
    def __init__(self, varname: str):
        self.varname = varname


SURFACE_BASE = Surface("s:base")
SURFACE_RAISED = Surface("s:raised")

TAG_LIFT = 0.05

ACCENT_SATURATION = 0.80


def lighten(ink: Ink, amount: float) -> Ink:
    L, c, h = hex_to_oklch(ink.hex)
    return Ink(
        hex=oklch_to_hex((max(0.0, min(1.0, L + amount)), c, h)), cterm=ink.cterm
    )


def desaturate(ink: Ink, factor: float = ACCENT_SATURATION) -> Ink:
    L, c, h = hex_to_oklch(ink.hex)
    return Ink(hex=oklch_to_hex((L, max(0.0, c * factor), h)), cterm=ink.cterm)


def load_palette(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def build_index(data: dict) -> dict[str, int]:
    named: dict[str, str] = data["named"]
    ansi: dict[str, str] = data["ansi"]
    hex_to_name = {hex_value: name for name, hex_value in named.items()}
    index: dict[str, int] = {}
    for i, slot in enumerate(ANSI_SLOT_NAMES):
        name = hex_to_name.get(ansi[slot])
        if name is not None:
            index[name] = i
    return index


def build_inks(data: dict) -> dict[str, Ink]:
    named: dict[str, str] = data["named"]
    index_of_name = build_index(data)
    return {
        name: Ink(hex=hex_value, cterm=str(index_of_name.get(name, "NONE")))
        for name, hex_value in named.items()
    }


def build_roles(data: dict, block: str) -> dict[str, Ink]:
    named: dict[str, str] = data["named"]
    hex_to_name = {v: k for k, v in named.items()}
    index_of_name = build_index(data)
    roles: dict[str, Ink] = {}
    for role, hex_value in data[block].items():
        name = hex_to_name.get(hex_value)
        cterm = str(index_of_name[name]) if name in index_of_name else "NONE"
        roles[role] = Ink(hex=hex_value, cterm=cterm)
    return roles


def build_surfaces(data: dict) -> dict[str, dict[str, str]]:
    return {
        level: dict(data["contrast"][level]["surface"]) for level in CONTRAST_LEVELS
    }


def hi(
    group: str,
    fg: Ink | Surface | None = None,
    bg: Ink | Surface | None = None,
    attrs: str | None = None,
    link: str | None = None,
) -> str:
    if link:
        return f"hi! link {group} {link}"

    style = attrs or "NONE"
    fg_dynamic = isinstance(fg, Surface)
    bg_dynamic = isinstance(bg, Surface)

    if not fg_dynamic and not bg_dynamic:
        parts = [f"hi {group}"]
        if fg:
            parts.append(f"ctermfg={fg.cterm} guifg={fg.hex}")
        if bg:
            parts.append(f"ctermbg={bg.cterm} guibg={bg.hex}")
        parts.append(f"cterm={style} gui={style}")
        return " ".join(parts)

    fg_part = ""
    if fg is not None:
        fg_part = (
            f"ctermfg=NONE guifg=' . {fg.varname} . '"
            if fg_dynamic
            else f"ctermfg={fg.cterm} guifg={fg.hex}"
        )
    bg_part = ""
    if bg is not None:
        bg_part = (
            f"ctermbg=NONE guibg=' . {bg.varname} . '"
            if bg_dynamic
            else f"ctermbg={bg.cterm} guibg={bg.hex}"
        )
    body = " ".join(p for p in (fg_part, bg_part) if p)
    return f"execute 'hi {group} {body} cterm={style} gui={style}'"


def build_colorscheme(
    g: dict[str, Ink],
    p: dict[str, Ink],
    sem: dict[str, Ink],
    surfaces: dict[str, dict[str, str]],
) -> str:
    lines: list[str] = [HEADER]
    lines += [
        "hi clear",
        'if exists("syntax_on")',
        "  syntax reset",
        "endif",
        "set background=dark",
        'let g:colors_name = "alight"',
        "",
        '" contrast variants: set g:alight_contrast to "hard", "medium", or',
        '" "soft" before `colorscheme alight` loads. Falls back to "medium".',
        "let s:contrast = {",
    ]
    for level in CONTRAST_LEVELS:
        s = surfaces[level]
        lines.append(
            f"\\ '{level}': {{'base': '{s['base']}', 'raised': '{s['raised']}'}},"
        )
    lines += [
        "\\ }",
        f"let s:level = get(g:, 'alight_contrast', '{DEFAULT_CONTRAST}')",
        "if !has_key(s:contrast, s:level)",
        f"  let s:level = '{DEFAULT_CONTRAST}'",
        "endif",
        "let s:base = s:contrast[s:level].base",
        "let s:raised = s:contrast[s:level].raised",
        "",
        '" register named colors (Vim 9.1+) so users can override before',
        '" `colorscheme alight` loads',
        "if exists('v:colornames')",
    ]
    for name, ink in g.items():
        lines.append(
            f"  call extend(v:colornames, {{'alight_{name}': '{ink.hex}'}}, 'keep')"
        )
    lines += ["endif", ""]

    tag = lighten(sem["tag"], TAG_LIFT)

    lines.append(
        '" -- base ui --------------------------------------------------------------'
    )
    lines += [
        hi("Normal", fg=p["foreground"], bg=SURFACE_BASE),
        hi("NonText", fg=sem["muted"]),
        hi("SpecialKey", fg=sem["muted"]),
        hi("CursorLine", bg=SURFACE_RAISED),
        hi("CursorLineNr", fg=sem["accent"], bg=SURFACE_RAISED),
        hi("LineNr", fg=sem["muted"]),
        hi("SignColumn", bg=SURFACE_BASE),
        hi("FoldColumn", fg=sem["muted"], bg=SURFACE_BASE),
        hi("Folded", fg=sem["muted"], bg=SURFACE_RAISED),
        hi("VertSplit", fg=sem["muted"], bg=SURFACE_BASE),
        hi("StatusLine", fg=SURFACE_BASE, bg=sem["accent"], attrs="bold"),
        hi("StatusLineNC", fg=sem["muted"], bg=SURFACE_RAISED),
        hi("TabLine", fg=sem["muted"], bg=SURFACE_RAISED),
        hi("TabLineSel", fg=SURFACE_BASE, bg=sem["accent"]),
        hi("WildMenu", fg=SURFACE_BASE, bg=sem["accent"]),
        hi("Pmenu", fg=p["foreground"], bg=SURFACE_RAISED),
        hi("PmenuSel", fg=SURFACE_BASE, bg=sem["accent"]),
        hi("Cursor", fg=SURFACE_BASE, bg=p["cursor"]),
        hi("Visual", bg=p["selection"]),
        hi("Search", fg=SURFACE_BASE, bg=g["kindling"]),
        hi("IncSearch", fg=SURFACE_BASE, bg=g["witchlight"]),
        hi("MatchParen", fg=g["witchlight"], attrs="bold"),
        hi("Directory", fg=sem["link"]),
        hi("Title", fg=sem["keyword"], attrs="bold"),
        "",
    ]

    lines.append(
        '" -- diff ------------------------------------------------------------------'
    )
    lines += [
        hi("DiffAdd", fg=sem["success"], bg=SURFACE_RAISED),
        hi("DiffChange", fg=sem["link"], bg=SURFACE_RAISED),
        hi("DiffDelete", fg=sem["error"], bg=SURFACE_RAISED),
        hi("DiffText", fg=tag, bg=SURFACE_RAISED, attrs="bold"),
        "",
    ]

    lines.append(
        '" -- preferred syntax groups (see :help group-name) ------------------------'
    )
    lines += [
        hi("Comment", fg=sem["comment"], attrs="italic"),
        hi("Constant", fg=g["kindling"]),
        hi("String", fg=g["smolder"]),
        hi("Character", link="String"),
        hi("Number", link="Constant"),
        hi("Boolean", link="Constant"),
        hi("Float", link="Number"),
        hi("Identifier", fg=p["foreground"]),
        hi("Function", link="Identifier"),
        hi("Statement", fg=sem["keyword"], attrs="bold"),
        hi("Conditional", link="Statement"),
        hi("Repeat", link="Statement"),
        hi("Label", link="Statement"),
        hi("Operator", fg=p["foreground"]),
        hi("Keyword", link="Statement"),
        hi("Exception", link="Statement"),
        hi("PreProc", fg=desaturate(g["verdigris"])),
        hi("Include", link="Statement"),
        hi("Define", link="PreProc"),
        hi("Macro", link="PreProc"),
        hi("PreCondit", link="PreProc"),
        hi("Type", fg=sem["type"]),
        hi("StorageClass", link="Type"),
        hi("Structure", link="Identifier"),
        hi("Typedef", link="Type"),
        hi("Special", link="String"),
        hi("SpecialChar", link="Special"),
        hi("Tag", fg=tag, attrs="underline"),
        hi("Delimiter", link="String"),
        hi("SpecialComment", fg=sem["muted"], attrs="italic,bold"),
        hi("Debug", fg=sem["error"]),
        hi("Underlined", fg=sem["link"], attrs="underline"),
        hi("Ignore", fg=SURFACE_BASE, bg=SURFACE_BASE),
        hi("Error", fg=SURFACE_BASE, bg=sem["error"], attrs="bold"),
        hi("Todo", fg=sem["warning"], bg=SURFACE_RAISED, attrs="bold"),
        "",
        hi("Added", link="DiffAdd"),
        hi("Changed", link="DiffChange"),
        hi("Removed", link="DiffDelete"),
    ]

    return "\n".join(lines) + "\n"


def main() -> bool:
    data = load_palette(SCHEME_FILE)
    g = build_inks(data)
    p = build_roles(data, "palette")
    sem = build_roles(data, "semantic")
    surfaces = build_surfaces(data)

    rendered = build_colorscheme(g, p, sem, surfaces)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(rendered)
    print(f"wrote {OUTPUT_FILE}")

    ok = OUTPUT_FILE.read_text() == rendered
    print("ALL MATCH -- safe to use" if ok else "MISMATCH -- write did not round-trip")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
