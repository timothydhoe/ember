"""
export_terminal_app.py
~~~~~~~~~~~~~~~~~~~~~~

Usage:
    uv run scripts/export_terminal_app.py

Then in Terminal.app: double-click the profile you want (or `open` it)
to import it, and set it as default under
Terminal > Settings > Profiles > Default.
"""

from __future__ import annotations

import plistlib
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
TEMPLATE_FILE = BASE_DIR / "terminal" / "terminal-app" / "alight.terminal"
OUTPUT_DIR = BASE_DIR / "terminal" / "terminal-app"

CONTRAST_LEVELS = ["hard", "medium", "soft"]

ANSI_KEY_MAP = {
    "black": "ANSIBlackColor",
    "red": "ANSIRedColor",
    "green": "ANSIGreenColor",
    "yellow": "ANSIYellowColor",
    "blue": "ANSIBlueColor",
    "magenta": "ANSIMagentaColor",
    "cyan": "ANSICyanColor",
    "white": "ANSIWhiteColor",
    "bright_black": "ANSIBrightBlackColor",
    "bright_red": "ANSIBrightRedColor",
    "bright_green": "ANSIBrightGreenColor",
    "bright_yellow": "ANSIBrightYellowColor",
    "bright_blue": "ANSIBrightBlueColor",
    "bright_magenta": "ANSIBrightMagentaColor",
    "bright_cyan": "ANSIBrightCyanColor",
    "bright_white": "ANSIBrightWhiteColor",
}


def hex_to_nscolor_archive(hex_value: str, alpha: float | None = None) -> bytes:
    """Build the exact NSKeyedArchiver blob macOS's own NSColor archiving produces."""
    hex_value = hex_value.lstrip("#")
    r = int(hex_value[0:2], 16) / 255
    g = int(hex_value[2:4], 16) / 255
    b = int(hex_value[4:6], 16) / 255
    parts = [r, g, b] + ([alpha] if alpha is not None else [])
    rgb_str = " ".join(f"{c:.10g}" for c in parts) + "\x00"

    inner = {
        "$archiver": "NSKeyedArchiver",
        "$objects": [
            "$null",
            {
                "$class": plistlib.UID(2),
                "NSColorSpace": 1,
                "NSRGB": rgb_str.encode("ascii"),
            },
            {"$classes": ["NSColor", "NSObject"], "$classname": "NSColor"},
        ],
        "$top": {"root": plistlib.UID(1)},
        "$version": 100000,
    }
    return plistlib.dumps(inner, fmt=plistlib.FMT_BINARY)


def nscolor_archive_to_hex(blob: bytes) -> str:
    """Inverse of the above -- used only for self-verification below."""
    inner = plistlib.loads(blob)
    rgb = inner["$objects"][1]["NSRGB"].rstrip(b"\x00").decode("ascii")
    parts = [float(x) for x in rgb.split()]
    r, g, b = (round(c * 255) for c in parts[:3])
    return f"#{r:02X}{g:02X}{b:02X}"


def build(yaml_data: dict, base: dict, surface: dict) -> dict:
    out = dict(base)  # shallow copy: preserves every key alight.yml doesn't own

    palette = yaml_data["palette"]
    ansi = yaml_data["ansi"]
    window = yaml_data.get("window", {})
    font = yaml_data.get("font", {})
    background = surface["base"]

    bg_alpha = window.get("background_opacity")
    out["BackgroundColor"] = hex_to_nscolor_archive(background, alpha=bg_alpha)
    out["TextColor"] = hex_to_nscolor_archive(palette["foreground"])
    out["SelectionColor"] = hex_to_nscolor_archive(
        palette["selection"], alpha=window.get("selection_opacity")
    )
    out["CursorColor"] = hex_to_nscolor_archive(palette["cursor"])
    out["TextBoldColor"] = hex_to_nscolor_archive(palette["bold"])

    for ansi_key, plist_key in ANSI_KEY_MAP.items():
        out[plist_key] = hex_to_nscolor_archive(ansi[ansi_key])

    if "background_blur" in window:
        out["BackgroundBlur"] = float(window["background_blur"])
    if "line_spacing" in font:
        out["FontHeightSpacing"] = float(font["line_spacing"])

    return out


def self_verify(yaml_data: dict, written: dict, surface: dict) -> bool:
    pairs = [
        ("TextColor", yaml_data["palette"]["foreground"]),
        ("SelectionColor", yaml_data["palette"]["selection"]),
        ("CursorColor", yaml_data["palette"]["cursor"]),
        ("TextBoldColor", yaml_data["palette"]["bold"]),
        ("BackgroundColor", surface["base"]),
    ] + [
        (plist_key, yaml_data["ansi"][ansi_key])
        for ansi_key, plist_key in ANSI_KEY_MAP.items()
    ]

    ok = True
    for plist_key, expected_hex in pairs:
        got_hex = nscolor_archive_to_hex(written[plist_key])
        match = got_hex.upper() == expected_hex.upper()
        ok &= match
        if not match:
            print(f"    MISMATCH {plist_key}: expected={expected_hex} got={got_hex}")
    return ok


def main() -> bool:
    if not SCHEME_FILE.exists():
        raise FileNotFoundError(f"Missing scheme file: {SCHEME_FILE}")
    if not TEMPLATE_FILE.exists():
        raise FileNotFoundError(
            f"Missing base template: {TEMPLATE_FILE}. Need one existing .terminal "
            "file once, to carry over window/behavior settings alight.yml doesn't model."
        )

    yaml_data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    with open(TEMPLATE_FILE, "rb") as f:
        base = plistlib.load(f)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for level in CONTRAST_LEVELS:
        surface = yaml_data["contrast"][level]["surface"]
        new_plist = build(yaml_data, base, surface)
        out_path = OUTPUT_DIR / f"alight-{level}.terminal"

        with open(out_path, "wb") as f:
            plistlib.dump(new_plist, f, fmt=plistlib.FMT_XML)
        print(f"Wrote {out_path}")

        with open(out_path, "rb") as f:
            written = plistlib.load(f)
        level_ok = self_verify(yaml_data, written, surface)
        ok &= level_ok
        print(f"  {level}: {'ALL MATCH' if level_ok else 'MISMATCHES FOUND'}")

    print(
        "ALL MATCH -- safe to import" if ok else "MISMATCHES FOUND -- do not import yet"
    )
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
