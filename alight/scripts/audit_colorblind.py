"""
alight.audit_colorblind
~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
    uv run scripts/audit_colorblind.py
"""

from __future__ import annotations

from pathlib import Path

import yaml
from _ansi import bold, dim, green, red, yellow

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"

RISK_THRESHOLD = 40.0

MATRICES = {
    "protanopia": [
        [0.567, 0.433, 0.000],
        [0.558, 0.442, 0.000],
        [0.000, 0.242, 0.758],
    ],
    "deuteranopia": [
        [0.625, 0.375, 0.000],
        [0.700, 0.300, 0.000],
        [0.000, 0.300, 0.700],
    ],
}


def srgb_to_linear(c: float) -> float:
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> int:
    c = max(0.0, min(1.0, c))
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return round(v * 255)


def simulate(hex_color: str, kind: str) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    r, g, b = srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b)
    m = MATRICES[kind]
    r2 = m[0][0] * r + m[0][1] * g + m[0][2] * b
    g2 = m[1][0] * r + m[1][1] * g + m[1][2] * b
    b2 = m[2][0] * r + m[2][1] * g + m[2][2] * b
    return "#" + "".join(f"{linear_to_srgb(c):02X}" for c in (r2, g2, b2))


def rgb_distance(hex1: str, hex2: str) -> float:
    hex1, hex2 = hex1.lstrip("#"), hex2.lstrip("#")
    r1, g1, b1 = (int(hex1[i : i + 2], 16) for i in (0, 2, 4))
    r2, g2, b2 = (int(hex2[i : i + 2], 16) for i in (0, 2, 4))
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


def build_pairs(data: dict) -> list[tuple[str, str, str]]:
    ansi, sem = data["ansi"], data["semantic"]
    return [
        ("ansi.red vs ansi.bright_red", ansi["red"], ansi["bright_red"]),
        ("ansi.green vs ansi.bright_green", ansi["green"], ansi["bright_green"]),
        ("ansi.yellow vs ansi.bright_yellow", ansi["yellow"], ansi["bright_yellow"]),
        ("ansi.blue vs ansi.bright_blue", ansi["blue"], ansi["bright_blue"]),
        (
            "ansi.magenta vs ansi.bright_magenta",
            ansi["magenta"],
            ansi["bright_magenta"],
        ),
        ("ansi.cyan vs ansi.bright_cyan", ansi["cyan"], ansi["bright_cyan"]),
        ("semantic.error vs semantic.warning", sem["error"], sem["warning"]),
        ("semantic.warning vs semantic.success", sem["warning"], sem["success"]),
        ("semantic.error vs semantic.success", sem["error"], sem["success"]),
        ("semantic.link vs semantic.type", sem["link"], sem["type"]),
        ("semantic.error vs semantic.link", sem["error"], sem["link"]),
    ]


def main() -> bool:
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    pairs = build_pairs(data)

    print(bold(f"{'pair':40s} {'normal':>7s} {'protan':>7s} {'deuter':>7s}  flag"))
    ok = True
    for label, a, b in pairs:
        normal = rgb_distance(a, b)
        protan = rgb_distance(simulate(a, "protanopia"), simulate(b, "protanopia"))
        deuter = rgb_distance(simulate(a, "deuteranopia"), simulate(b, "deuteranopia"))
        worst = min(protan, deuter)
        at_risk = worst < RISK_THRESHOLD
        already_close = normal < RISK_THRESHOLD
        ok &= not at_risk and not already_close
        if already_close:
            tag = red("<-- CLOSE EVEN NORMALLY")
        elif at_risk:
            tag = yellow("<-- COLORBLIND RISK")
        else:
            tag = dim(green("ok"))
        print(f"{label:40s} {normal:7.0f} {protan:7.0f} {deuter:7.0f}  {tag}")

    print()
    print(
        green(bold("No flags -- all checked pairs stay distinguishable"))
        if ok
        else yellow(
            bold(
                "Some pairs flagged above -- review before treating the palette as finished"
            )
        )
    )
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
