"""
Generate preview.html (a browser mockup of alight's colors applied to a
wildfire-shaped CLI transcript) from schemes/alight.yml.

Usage:
    uv run scripts/export_preview.py
"""

from pathlib import Path
from string import Template
import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
TEMPLATE_FILE = BASE_DIR / "templates" / "preview.html.tmpl"
OUTPUT_FILE = BASE_DIR / "preview.html"


def build_preview_context(yaml_data: dict) -> dict[str, str]:
    context = {}

    # Palette metadata
    for key, val in yaml_data.get("palette", {}).items():
        context[f"palette_{key}" if key == "name" else key] = str(val)

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


def main() -> None:
    if not SCHEME_FILE.exists():
        raise FileNotFoundError(f"Missing scheme file: {SCHEME_FILE}")

    with open(SCHEME_FILE, "r", encoding="utf-8") as f:
        theme_data = yaml.safe_load(f)

    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        template = Template(f.read())

    context = build_preview_context(theme_data)
    rendered_html = template.safe_substitute(context)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"Generated HTML preview: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
