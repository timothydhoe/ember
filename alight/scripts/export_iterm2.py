"""
export_iterm2
~~~~~~~~~~~~~

Usage:
    uv run scripts/export_iterm2.py

Then in iTerm2: Settings -> Profiles -> Colors -> Color Presets... ->
Import..., select the variant you want, then choose it from that same
menu -- each shows up under its own name (alight-hard, alight-medium,
alight-soft).
"""

from __future__ import annotations

import plistlib
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_DIR = BASE_DIR / "terminal" / "iterm2"

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


def hex_to_component_dict(hex_value: str) -> dict:
    hex_value = hex_value.lstrip("#")
    r = int(hex_value[0:2], 16) / 255
    g = int(hex_value[2:4], 16) / 255
    b = int(hex_value[4:6], 16) / 255
    return {
        "Color Space": "sRGB",
        "Red Component": r,
        "Green Component": g,
        "Blue Component": b,
    }


def component_dict_to_hex(d: dict) -> str:
    r, g, b = (round(d[f"{c} Component"] * 255) for c in ("Red", "Green", "Blue"))
    return f"#{r:02X}{g:02X}{b:02X}"


def build(palette: dict, ansi: dict, surface: dict) -> dict:
    background = surface["base"]
    out = {}
    for i, key in enumerate(ANSI_ORDER):
        out[f"Ansi {i} Color"] = hex_to_component_dict(ansi[key])

    out["Background Color"] = hex_to_component_dict(background)
    out["Foreground Color"] = hex_to_component_dict(palette["foreground"])
    out["Cursor Color"] = hex_to_component_dict(palette["cursor"])
    out["Cursor Text Color"] = hex_to_component_dict(background)
    out["Selection Color"] = hex_to_component_dict(palette["selection"])
    out["Selected Text Color"] = hex_to_component_dict(palette["foreground"])
    out["Bold Color"] = hex_to_component_dict(palette["bold"])
    return out


def self_verify(written: dict, palette: dict, ansi: dict, surface: dict) -> bool:
    checks = [(f"Ansi {i} Color", ansi[key]) for i, key in enumerate(ANSI_ORDER)]
    checks += [
        ("Background Color", surface["base"]),
        ("Foreground Color", palette["foreground"]),
        ("Cursor Color", palette["cursor"]),
        ("Selection Color", palette["selection"]),
        ("Bold Color", palette["bold"]),
    ]
    ok = True
    for key, expected in checks:
        got = component_dict_to_hex(written[key])
        match = got.upper() == expected.upper()
        ok &= match
        if not match:
            print(f"    MISMATCH {key}: expected={expected} got={got}")
    return ok


def main() -> bool:
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    palette, ansi = data["palette"], data["ansi"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for level in CONTRAST_LEVELS:
        surface = data["contrast"][level]["surface"]
        out_dict = build(palette, ansi, surface)
        out_path = OUTPUT_DIR / f"alight-{level}.itermcolors"
        with open(out_path, "wb") as f:
            plistlib.dump(out_dict, f, fmt=plistlib.FMT_XML)
        print(f"Wrote {out_path}")

        with open(out_path, "rb") as f:
            written = plistlib.load(f)
        level_ok = self_verify(written, palette, ansi, surface)
        ok &= level_ok
        print(f"  {level}: {'ALL MATCH' if level_ok else 'MISMATCHES FOUND'}")

    print("ALL MATCH -- safe to import" if ok else "MISMATCHES FOUND")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
