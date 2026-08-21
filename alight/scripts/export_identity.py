"""
alight.export_identity
~~~~~~~~~~~~~~~~~~~~~~
Resolve schemes/alight.yml + identity.yml into a flat, self-contained projection any ember tool can read without depending on alight's own repo layout.

Writes dist/identity.yml that's safe to regenerate on every run. Publishing that file so other tools actually read it is install_identity.py's job.

usage:
    uv run scripts/export_identity.py
"""

from __future__ import annotations

from pathlib import Path
import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
IDENTITY_FILE = BASE_DIR / "identity.yml"
OUTPUT_FILE = BASE_DIR / "exports" / "identity.yml"


def main() -> bool:
    scheme = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    identity = yaml.safe_load(IDENTITY_FILE.read_text(encoding="utf-8"))

    named = scheme["named"]
    semantic = scheme["semantic"]  # already resolved to hex via YAML aliases
    tools = {
        tool: named[spec["color"]] for tool, spec in identity.get("tools", {}).items()
    }
    brand = {
        scope: {"gradient": [named[c] for c in spec.get("gradient", [])]}
        for scope, spec in identity.get("brand", {}).items()
    }

    resolved = {"semantic": semantic, "tools": tools, "brand": brand}

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Generated from schemes/alight.yml + identity.yml -- "
        "do not edit by hand, re-run export_identity.py\n"
    )
    body = yaml.dump(resolved, sort_keys=False, default_flow_style=False)
    OUTPUT_FILE.write_text(header + body, encoding="utf-8")
    print(f"Wrote {OUTPUT_FILE}")

    # self-verify against source, same pattern as the other exporters
    written = yaml.safe_load(OUTPUT_FILE.read_text(encoding="utf-8"))
    ok = (
        written.get("semantic") == semantic
        and written.get("tools") == tools
        and written.get("brand") == brand
    )
    print("ALL MATCH -- safe to use" if ok else "MISMATCHES FOUND")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
