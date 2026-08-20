"""
Generate alight.terminal (macOS Terminal.app profile) from schemes/alight.yml.

Usage:
    uv run scripts/export_terminal_app.py

Then in Terminal.app: double-click the output file (or `open` it) to import
it as a new profile, and set it as default under
Terminal > Settings > Profiles > Default.
"""

from __future__ import annotations

from pathlib import Path
import plistlib
import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
TEMPLATE_FILE = (
    BASE_DIR / "terminal" / "terminal-app" / "alight.terminal"
)  # existing file = base/skeleton
OUTPUT_FILE = (
    BASE_DIR / "terminal" / "terminal-app" / "alight.terminal"
)  # overwritten in place; use git diff to review

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


def build(yaml_data: dict, base: dict) -> dict:
    out = dict(base)  # shallow copy: preserves every key alight.yml doesn't own

    palette = yaml_data["palette"]
    ansi = yaml_data["ansi"]
    window = yaml_data.get("window", {})
    font = yaml_data.get("font", {})

    bg_alpha = window.get("background_opacity")
    out["BackgroundColor"] = hex_to_nscolor_archive(
        palette["background"], alpha=bg_alpha
    )
    out["TextColor"] = hex_to_nscolor_archive(palette["foreground"])
    out["SelectionColor"] = hex_to_nscolor_archive(palette["selection"])
    out["CursorColor"] = hex_to_nscolor_archive(palette["cursor"])
    out["TextBoldColor"] = hex_to_nscolor_archive(palette["bold"])

    for ansi_key, plist_key in ANSI_KEY_MAP.items():
        out[plist_key] = hex_to_nscolor_archive(ansi[ansi_key])

    if "background_blur" in window:
        out["BackgroundBlur"] = float(window["background_blur"])
    if "line_spacing" in font:
        out["FontHeightSpacing"] = float(font["line_spacing"])

    return out


def diff_report(old: dict, new: dict) -> list[str]:
    return [k for k in sorted(set(old) | set(new)) if old.get(k) != new.get(k)]


def self_verify(yaml_data: dict, written: dict) -> bool:
    pairs = [
        ("TextColor", yaml_data["palette"]["foreground"]),
        ("SelectionColor", yaml_data["palette"]["selection"]),
        ("CursorColor", yaml_data["palette"]["cursor"]),
        ("TextBoldColor", yaml_data["palette"]["bold"]),
        ("BackgroundColor", yaml_data["palette"]["background"]),
    ] + [
        (plist_key, yaml_data["ansi"][ansi_key])
        for ansi_key, plist_key in ANSI_KEY_MAP.items()
    ]

    print("\nSelf-verification (written file -> decoded hex -> alight.yml):")
    ok = True
    for plist_key, expected_hex in pairs:
        got_hex = nscolor_archive_to_hex(written[plist_key])
        match = got_hex.upper() == expected_hex.upper()
        ok &= match
        print(
            f"  {plist_key:22s} expected={expected_hex:8s} got={got_hex:8s} [{'OK' if match else 'MISMATCH'}]"
        )
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

    new_plist = build(yaml_data, base)
    changed = diff_report(base, new_plist)
    print("Keys regenerated from alight.yml:")
    for key in changed:
        print(f"  {key}")

    with open(OUTPUT_FILE, "wb") as f:
        plistlib.dump(new_plist, f, fmt=plistlib.FMT_XML)
    print(f"\nWrote {OUTPUT_FILE}")

    with open(OUTPUT_FILE, "rb") as f:
        written = plistlib.load(f)
    ok = self_verify(yaml_data, written)
    print(
        "\nALL MATCH -- safe to import"
        if ok
        else "\nMISMATCHES FOUND -- do not import yet"
    )
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
