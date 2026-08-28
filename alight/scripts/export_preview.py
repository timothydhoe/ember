"""
Generate preview.html (a browser mockup of alight's colors applied to a wildfire-shaped CLI transcript) from schemes/alight.yml.

Shows the medium contrast variant.

Usage:
    uv run scripts/export_preview.py
"""

import re
from pathlib import Path
from string import Template

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
TEMPLATE_FILE = BASE_DIR / "templates" / "preview.html.tmpl"
OUTPUT_FILE = BASE_DIR / "exports" / "preview.html"

PREVIEW_CONTRAST = "medium"


def build_preview_context(yaml_data: dict) -> dict[str, str]:
    context = {}

    # Palette metadata
    for key, val in yaml_data.get("palette", {}).items():
        context[f"palette_{key}" if key == "name" else key] = str(val)

    context["background"] = yaml_data["contrast"][PREVIEW_CONTRAST]["surface"]["base"]

    # ANSI colors
    for key, val in yaml_data.get("ansi", {}).items():
        context[f"ansi_{key}"] = str(val)

    # Semantic tokens
    for key, val in yaml_data.get("semantic", {}).items():
        context[f"semantic_{key}"] = str(val)

    # Font properties
    for key, val in yaml_data.get("font", {}).items():
        context[f"font_{key}"] = str(val)

    return context


def main() -> bool:
    if not SCHEME_FILE.exists():
        raise FileNotFoundError(f"Missing scheme file: {SCHEME_FILE}")

    with open(SCHEME_FILE, "r", encoding="utf-8") as f:
        theme_data = yaml.safe_load(f)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = Template(f.read())

    context = build_preview_context(theme_data)
    rendered_html = template.safe_substitute(context)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"Generated HTML preview: {OUTPUT_FILE}")

    written = OUTPUT_FILE.read_text(encoding="utf-8")
    round_trip_ok = written == rendered_html

    leftover = re.findall(r"\$[a-zA-Z_]+", written)
    no_leftovers_ok = not leftover
    if leftover:
        print(f"  UNRESOLVED PLACEHOLDERS: {sorted(set(leftover))}")

    ok = round_trip_ok and no_leftovers_ok
    print(
        "ALL MATCH -- safe to open"
        if ok
        else "MISMATCH -- do not treat as safe to open"
    )
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
