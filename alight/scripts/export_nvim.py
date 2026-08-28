"""
alight.export_nvim
~~~~~~~~~~~~~~~~~~~
Generate a native Lua Neovim colorscheme (colors/alight.lua) from
schemes/alight.yml.

This is Neovim only.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from _ansi import bold, cyan, dim, green, red
from _oklch import hex_to_oklch, oklch_to_hex

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_FILE = BASE_DIR / "terminal" / "nvim" / "colors" / "alight.lua"

CONTRAST_LEVELS = ["hard", "medium", "soft"]
DEFAULT_CONTRAST = "medium"

HEADER = (
    "-- alight.lua -- generated from schemes/alight.yml by export_nvim.py\n"
    "-- do not hand-edit; change the source palette or the role mapping\n"
    "-- in export_nvim.py instead, then regenerate.\n"
)


class Raw(str):
    """A string that's already a Lua expression (e.g. 'surface.base'),
    not a color value to be quoted. hl() renders these."""


CHROMA_CAP = 0.37


def _clamp_l(l: float) -> float:
    return max(0.0, min(1.0, l))


ACCENT_SATURATION = 0.80


def desaturate(hex_color: str, factor: float = ACCENT_SATURATION) -> str:
    L, c, h = hex_to_oklch(hex_color)
    return oklch_to_hex((L, max(0.0, c * factor), h))


ELEVATE_DELTA = 0.05
TAG_LIFT = 0.05


def lighten(hex_color: str, amount: float) -> str:
    L, c, h = hex_to_oklch(hex_color)
    return oklch_to_hex((_clamp_l(L + amount), c, h))


STRING_HUE_SHIFT = 30
STRING_VIVIFY_SATURATION = 1.35
STRING_VIVIFY_LIGHTNESS = 0.05


def saturate(hex_color: str, factor: float) -> str:
    L, c, h = hex_to_oklch(hex_color)
    return oklch_to_hex((L, min(CHROMA_CAP, c * factor), h))


def shift_hue(hex_color: str, degrees: float) -> str:
    L, c, h = hex_to_oklch(hex_color)
    return oklch_to_hex((L, c, (h + degrees) % 360))


KEYWORD_CHALK = 0.75

FUNCTION_LIGHTNESS = 0.72
FUNCTION_SATURATION = 1.4


def brighten_function(hex_color: str) -> str:
    _, c, h = hex_to_oklch(hex_color)
    return oklch_to_hex(
        (FUNCTION_LIGHTNESS, min(CHROMA_CAP, c * FUNCTION_SATURATION), h)
    )


GUIDE_LIFT = 0.08


def guide_tone(hex_color: str) -> str:
    L, c, h = hex_to_oklch(hex_color)
    return oklch_to_hex((_clamp_l(L + GUIDE_LIFT), c, h))


def load_palette(path: Path) -> dict:
    return yaml.safe_load(path.read_text())


def build_inks(data: dict) -> dict[str, str]:
    return dict(data["named"])


def build_roles(data: dict, block: str) -> dict[str, str]:
    return dict(data[block])


def build_surfaces(data: dict) -> dict[str, dict[str, str]]:
    """contrast.<level>.surface.{base,raised} straight from the YAML,
    plus guide computed per-level -- see module docstring."""
    surfaces: dict[str, dict[str, str]] = {}
    for level in CONTRAST_LEVELS:
        block = data["contrast"][level]["surface"]
        surfaces[level] = {
            "base": block["base"],
            "raised": block["raised"],
            "guide": guide_tone(block["base"]),
        }
    return surfaces


def hl(
    group: str,
    fg: str | None = None,
    bg: str | None = None,
    sp: str | None = None,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    undercurl: bool = False,
    link: str | None = None,
) -> str:
    if link:
        return f'vim.api.nvim_set_hl(0, "{group}", {{ link = "{link}" }})'

    def render(v: str) -> str:
        return v if isinstance(v, Raw) else f'"{v}"'

    parts: list[str] = []
    if fg:
        parts.append(f"fg = {render(fg)}")
    if bg:
        parts.append(f"bg = {render(bg)}")
    if sp:
        parts.append(f"sp = {render(sp)}")
    if bold:
        parts.append("bold = true")
    if italic:
        parts.append("italic = true")
    if underline:
        parts.append("underline = true")
    if undercurl:
        parts.append("undercurl = true")
    body = ", ".join(parts)
    return f'vim.api.nvim_set_hl(0, "{group}", {{ {body} }})'


def relative_luminance(hex_color: str) -> float:
    def channel(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_color[i : i + 2], 16) for i in (1, 3, 5))
    r, g, b = channel(r), channel(g), channel(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1: str, hex2: str) -> float:
    l1, l2 = relative_luminance(hex1), relative_luminance(hex2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def compute_derived(
    g: dict[str, str], p: dict[str, str], sem: dict[str, str]
) -> dict[str, str]:
    elevated_fg = lighten(p["foreground"], ELEVATE_DELTA)
    tag = lighten(sem["tag"], TAG_LIFT)
    vivid_string = lighten(
        saturate(shift_hue(g["smolder"], STRING_HUE_SHIFT), STRING_VIVIFY_SATURATION),
        STRING_VIVIFY_LIGHTNESS,
    )
    chalky_keyword = desaturate(sem["keyword"], KEYWORD_CHALK)
    vivid_function = brighten_function(g["foxfire"])
    return {
        "elevated_fg": elevated_fg,
        "tag": tag,
        "vivid_string": vivid_string,
        "chalky_keyword": chalky_keyword,
        "vivid_function": vivid_function,
    }


def build_colorscheme(
    g: dict[str, str],
    p: dict[str, str],
    sem: dict[str, str],
    surfaces: dict[str, dict[str, str]],
) -> str:
    lines: list[str] = [HEADER]
    lines += [
        "if vim.g.colors_name then",
        '  vim.cmd("hi clear")',
        "end",
        'vim.o.background = "dark"',
        'vim.g.colors_name = "alight"',
        "",
        '-- contrast variants: set vim.g.alight_contrast to "hard", "medium",',
        '-- or "soft" before :colorscheme alight loads. Falls back to "medium".',
        "local CONTRAST = {",
    ]
    for level in CONTRAST_LEVELS:
        s = surfaces[level]
        lines.append(
            f'  {level} = {{ base = "{s["base"]}", raised = "{s["raised"]}", guide = "{s["guide"]}" }},'
        )
    lines += [
        "}",
        f'local surface = CONTRAST[vim.g.alight_contrast] or CONTRAST["{DEFAULT_CONTRAST}"]',
        "",
    ]

    d = compute_derived(g, p, sem)
    elevated_fg = d["elevated_fg"]
    tag = d["tag"]
    vivid_string = d["vivid_string"]
    chalky_keyword = d["chalky_keyword"]
    vivid_function = d["vivid_function"]
    base = Raw("surface.base")
    raised = Raw("surface.raised")
    guide = Raw("surface.guide")

    lines.append(
        "-- base ui --------------------------------------------------------------"
    )
    lines += [
        hl("Normal", fg=p["foreground"], bg=base),
        hl("NormalFloat", fg=elevated_fg, bg=raised),
        hl("FloatBorder", fg=sem["muted"], bg=raised),
        hl("NonText", fg=sem["muted"]),
        hl("SpecialKey", fg=sem["muted"]),
        hl("CursorLine", bg=raised),
        hl("CursorLineNr", fg=sem["accent"], bg=raised),
        hl("LineNr", fg=sem["muted"]),
        hl("SignColumn", bg=base),
        hl("FoldColumn", fg=sem["muted"], bg=base),
        hl("Folded", fg=sem["muted"], bg=raised),
        hl("WinSeparator", fg=sem["muted"], bg=base),
        hl("VertSplit", link="WinSeparator"),
        hl("StatusLine", fg=sem["accent"], bg=raised, bold=True),
        hl("StatusLineNC", fg=sem["muted"], bg=raised),
        hl("TabLine", fg=sem["muted"], bg=raised),
        hl("TabLineSel", fg=base, bg=sem["accent"]),
        hl("TabLineFill", bg=raised),
        hl("WildMenu", fg=base, bg=sem["accent"]),
        hl("Pmenu", fg=elevated_fg, bg=raised),
        hl("PmenuSel", fg=base, bg=sem["accent"]),
        hl("PmenuSbar", bg=raised),
        hl("PmenuThumb", bg=sem["muted"]),
        hl("Cursor", fg=base, bg=p["cursor"]),
        hl("Visual", bg=p["selection"]),
        hl("Search", fg=base, bg=g["kindling"]),
        hl("IncSearch", fg=base, bg=g["witchlight"]),
        hl("CurSearch", link="IncSearch"),
        hl("MatchParen", fg=g["witchlight"], bold=True),
        hl("Directory", fg=sem["link"]),
        hl("Title", fg=sem["keyword"], bold=True),
        hl("ErrorMsg", fg=sem["error"], bold=True),
        hl("WarningMsg", fg=sem["warning"]),
        "",
    ]

    lines.append(
        "-- diff ------------------------------------------------------------------"
    )
    lines += [
        hl("DiffAdd", fg=sem["success"], bg=raised),
        hl("DiffChange", fg=sem["link"], bg=raised),
        hl("DiffDelete", fg=sem["error"], bg=raised),
        hl("DiffText", fg=tag, bg=raised, bold=True),
        "",
    ]

    lines.append(
        "-- diagnostics (:h diagnostic-highlights) ---------------------------------"
    )
    lines += [
        hl("DiagnosticError", fg=sem["error"]),
        hl("DiagnosticWarn", fg=sem["warning"]),
        hl("DiagnosticInfo", fg=sem["link"]),
        hl("DiagnosticHint", fg=sem["type"]),
        hl("DiagnosticOk", fg=sem["success"]),
        hl("DiagnosticUnderlineError", sp=sem["error"], undercurl=True),
        hl("DiagnosticUnderlineWarn", sp=sem["warning"], undercurl=True),
        hl("DiagnosticUnderlineInfo", sp=sem["link"], undercurl=True),
        hl("DiagnosticUnderlineHint", sp=sem["type"], undercurl=True),
        hl("DiagnosticVirtualTextError", fg=sem["error"]),
        hl("DiagnosticVirtualTextWarn", fg=sem["warning"]),
        hl("DiagnosticVirtualTextInfo", fg=sem["link"]),
        hl("DiagnosticVirtualTextHint", fg=sem["type"]),
        # LspInlayHint: parameter names, inferred types -- editor-
        # generated, not authored code. Reuses muted (== Comment's own
        # color, they're already identical) rather than a new derived
        # tone -- same "supplementary, not primary content" bucket as
        # punctuation. Italic marks it as hint text, not real code.
        hl("LspInlayHint", fg=sem["muted"], italic=True),
        "",
    ]

    lines.append(
        "-- preferred syntax groups (see :help group-name) -------------------------"
    )
    lines += [
        hl("Comment", fg=sem["comment"], italic=True),
        hl("Constant", fg=g["kindling"]),
        hl("String", fg=vivid_string),
        hl("Character", link="String"),
        hl("Number", link="Constant"),
        hl("Boolean", link="Constant"),
        hl("Float", link="Number"),
        hl("Identifier", fg=p["foreground"]),
        hl("Function", link="Identifier"),
        hl("Statement", fg=chalky_keyword, italic=True),
        hl("Conditional", link="Statement"),
        hl("Repeat", link="Statement"),
        hl("Label", link="Statement"),
        hl("Operator", fg=p["foreground"]),
        hl("Keyword", link="Statement"),
        hl("Exception", link="Statement"),
        hl("PreProc", fg=desaturate(g["verdigris"])),
        hl("Include", link="Statement"),
        hl("Define", link="PreProc"),
        hl("Macro", link="PreProc"),
        hl("PreCondit", link="PreProc"),
        hl("Type", fg=sem["type"]),
        hl("StorageClass", link="Type"),
        hl("Structure", link="Identifier"),
        hl("Typedef", link="Type"),
        hl("Special", link="String"),
        hl("SpecialChar", link="Special"),
        hl("Tag", fg=tag, underline=True),
        hl("Delimiter", link="String"),
        hl("SpecialComment", fg=sem["muted"], italic=True),
        hl("Debug", fg=sem["error"]),
        hl("Underlined", fg=sem["link"], underline=True),
        hl("Ignore", fg=base, bg=base),
        hl("Error", fg=base, bg=sem["error"], bold=True),
        hl("Todo", fg=sem["warning"], bg=raised, bold=True),
        "",
        hl("Added", link="DiffAdd"),
        hl("Changed", link="DiffChange"),
        hl("Removed", link="DiffDelete"),
        "",
    ]

    lines.append(
        "-- treesitter refinements (most @captures link to groups above already) --"
    )
    lines += [
        hl("@variable", fg=p["foreground"]),
        hl("@variable.builtin", fg=sem["type"], italic=True),
        hl("@function", fg=vivid_function),
        hl("@function.method", fg=vivid_function),
        hl("@function.call", link="@function"),
        hl("@function.method.call", link="@function"),
        hl("@variable.parameter", link="Identifier"),
        hl("@string.documentation", fg=sem["comment"], italic=True),
        hl("@lsp.typemod.string.documentation", fg=sem["comment"], italic=True),
        hl("@property", fg=p["foreground"]),
        hl("@constructor", fg=sem["type"]),
        hl("@module", fg=sem["type"]),
        hl("@punctuation.bracket", fg=sem["muted"]),
        hl("@punctuation.delimiter", fg=sem["muted"]),
        hl("@punctuation.special", fg=sem["muted"]),
        hl("@markup.heading", fg=sem["keyword"], bold=True),
        hl("@markup.strong", bold=True),
        hl("@markup.italic", italic=True),
        hl("@markup.link.label", fg=sem["link"], underline=True),
        hl("@markup.link.url", fg=sem["link"], underline=True),
        "",
    ]

    lines.append(
        "-- gitsigns.nvim -----------------------------------------------------------"
    )
    lines += [
        hl("GitSignsAdd", fg=sem["success"]),
        hl("GitSignsChange", fg=sem["link"]),
        hl("GitSignsDelete", fg=sem["error"]),
        hl("GitSignsTopdelete", link="GitSignsDelete"),
        hl("GitSignsChangedelete", link="GitSignsChange"),
        "",
    ]

    lines.append(
        "-- snacks.nvim indent (structural nesting cues) -----------------------------"
    )
    lines += [
        hl("SnacksIndent", fg=guide),
        hl("SnacksIndentScope", fg=chalky_keyword),
        "",
    ]

    lines.append(
        "-- blink.cmp -----------------------------------------------------------"
    )
    lines += [
        hl("BlinkCmpMenu", fg=elevated_fg, bg=raised),
        hl("BlinkCmpMenuBorder", fg=sem["muted"], bg=raised),
        hl("BlinkCmpMenuSelection", fg=base, bg=sem["accent"]),
        hl("BlinkCmpLabel", fg=p["foreground"]),
        hl("BlinkCmpLabelMatch", fg=sem["accent"], bold=True),
        hl("BlinkCmpKind", fg=sem["muted"]),
        hl("BlinkCmpKindFunction", link="Function"),
        hl("BlinkCmpKindVariable", link="Identifier"),
        hl("BlinkCmpKindKeyword", link="Keyword"),
        hl("BlinkCmpKindModule", link="Type"),
        hl("BlinkCmpKindClass", link="Type"),
        hl("BlinkCmpDoc", fg=elevated_fg, bg=raised),
        hl("BlinkCmpDocBorder", fg=sem["muted"], bg=raised),
    ]

    return "\n".join(lines) + "\n"


def wcag_audit(
    g: dict[str, str],
    p: dict[str, str],
    sem: dict[str, str],
    surfaces: dict[str, dict[str, str]],
) -> bool:
    d = compute_derived(g, p, sem)

    pairs = [
        ("Normal (body text)", p["foreground"], 4.5),
        (
            "Comment (also covers @string.documentation, now identical)",
            sem["comment"],
            4.5,
        ),
        ("String", d["vivid_string"], 4.5),
        ("Statement/Keyword", d["chalky_keyword"], 4.5),
        ("Type", sem["type"], 4.5),
        (
            "@function (also covers @function.call, now linked)",
            d["vivid_function"],
            4.5,
        ),
        ("DiagnosticError", sem["error"], 4.5),
        ("DiagnosticWarn", sem["warning"], 4.5),
        ("DiagnosticInfo", sem["link"], 4.5),
        ("DiagnosticHint", sem["type"], 4.5),
    ]

    def tag(passed: bool) -> str:
        return green("OK") if passed else red("FAIL")

    print(bold("\nWCAG contrast audit (relative luminance, not HSL lightness):"))
    ok = True
    for level in CONTRAST_LEVELS:
        base = surfaces[level]["base"]
        raised = surfaces[level]["raised"]
        guide = surfaces[level]["guide"]
        print(cyan(bold(f"  -- contrast: {level} (base={base}) --")))
        for label, fg, minimum in pairs:
            ratio = contrast_ratio(fg, base)
            passed = ratio >= minimum
            ok &= passed
            print(
                f"    {label:32s} {ratio:5.2f}:1  (need {minimum:.1f}:1)  [{tag(passed)}]"
            )
        status_ratio = contrast_ratio(sem["accent"], raised)
        status_ok = status_ratio >= 3.0
        ok &= status_ok
        print(
            f"    {'StatusLine text (bold, large)':32s} {status_ratio:5.2f}:1  (need 3.0:1)  [{tag(status_ok)}]"
        )
        elevated_fg_ratio = contrast_ratio(d["elevated_fg"], raised)
        elevated_fg_ok = elevated_fg_ratio >= 4.5
        ok &= elevated_fg_ok
        print(
            f"    {'Pmenu/NormalFloat text':32s} {elevated_fg_ratio:5.2f}:1  (need 4.5:1)  [{tag(elevated_fg_ok)}]"
        )
        scope_ratio = contrast_ratio(d["chalky_keyword"], base)
        scope_ok = scope_ratio >= 3.0
        ok &= scope_ok
        print(
            f"    {'SnacksIndentScope (thin glyph)':32s} {scope_ratio:5.2f}:1  (need 3.0:1)  [{tag(scope_ok)}]"
        )
        guide_ratio = contrast_ratio(guide, base)
        print(
            dim(
                f"    {'SnacksIndent (guide, decorative)':32s} {guide_ratio:5.2f}:1  (intentionally low -- not text)"
            )
        )
    print(
        bold(green("ALL PASS (all 3 contrast levels)"))
        if ok
        else bold(red("SOME PAIRS FALL BELOW WCAG AA -- review flagged rows above"))
    )
    return ok


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

    wcag_ok = wcag_audit(g, p, sem, surfaces)
    return ok and wcag_ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
