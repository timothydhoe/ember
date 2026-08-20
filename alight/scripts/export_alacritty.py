"""
Generate alight.toml (Alacritty color config) from schemes/alight.yml.

Usage:
    uv run scripts/export_alacritty.py

Either import it from your main alacritty.toml:
    [general]
    import = ["/path/to/alight.toml"]
or paste the [colors...] tables directly into your config.
"""

from __future__ import annotations

from pathlib import Path
import re
import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_FILE = BASE_DIR / "terminal" / "alacritty" /"alight.toml"

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


def main() -> bool:
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    palette, ansi = data["palette"], data["ansi"]

    lines = [
        "# Generated from alight.yml -- do not edit by hand, re-run export_alacritty.py",
        "",
        "[colors.primary]",
        f'background = "{palette["background"]}"',
        f'foreground = "{palette["foreground"]}"',
        "",
        "[colors.cursor]",
        f'text = "{palette["background"]}"',
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

    content = "\n".join(lines) + "\n"
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")

    # self-verify: parse the TOML-ish output back out with a regex (avoids
    # adding a tomllib dependency for a format this flat/quotable) and
    # confirm every value matches alight.yml
    written = OUTPUT_FILE.read_text(encoding="utf-8")
    sections = {}
    current = None
    for line in written.splitlines():
        m = re.match(r"\[colors\.(\w+)\]", line)
        if m:
            current = m.group(1)
            sections[current] = {}
            continue
        m = re.match(r'(\w+) = "(#[0-9A-Fa-f]{6})"', line)
        if m and current:
            sections[current][m.group(1)] = m.group(2)

    checks = [
        (sections["primary"]["background"], palette["background"]),
        (sections["primary"]["foreground"], palette["foreground"]),
        (sections["cursor"]["cursor"], palette["cursor"]),
        (sections["selection"]["background"], palette["selection"]),
    ]
    checks += [(sections["normal"][k], ansi[k]) for k in ANSI_ORDER]
    checks += [(sections["bright"][k], ansi[f"bright_{k}"]) for k in ANSI_ORDER]

    ok = all(got.upper() == expected.upper() for got, expected in checks)
    print("ALL MATCH -- safe to import" if ok else "MISMATCHES FOUND")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
