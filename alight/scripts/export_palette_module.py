"""
Generate a small, dependency-free palette.py for a consuming tool, from
schemes/alight.yml (semantic roles) + identity.yml (that tool's own
accent color).

This is the "Option B" pattern the branding discussion settled on:
alight.yml stays the single hand-authored source of truth, and tools
don't depend on the `alight` package at runtime (no PyYAML pulled in,
no coupling to alight's own release cycle) -- they get a flat, static,
committed file instead. Re-run this to pick up a palette change; nothing
imports `alight` itself.

Usage:
    uv run scripts/export_python.py <tool-name> <output-path>

Example:
    uv run scripts/export_python.py wildfire \\
        ../wildfire/src/wildfire/palette.py
"""
from __future__ import annotations

import sys
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
IDENTITY_FILE = BASE_DIR / "identity.yml"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(1)
    tool_name, output_path = sys.argv[1], Path(sys.argv[2])

    scheme = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    identity = yaml.safe_load(IDENTITY_FILE.read_text(encoding="utf-8"))

    named = scheme["named"]
    semantic = scheme["semantic"]

    tool_spec = identity.get("tools", {}).get(tool_name)
    if tool_spec is None:
        raise SystemExit(
            f"'{tool_name}' has no entry under identity.yml's tools: block."
        )
    accent_name = tool_spec["color"]
    if accent_name not in named:
        raise SystemExit(
            f"identity.yml: tools.{tool_name}.color = '{accent_name}' "
            f"is not in alight.yml's named palette."
        )
    accent_hex = named[accent_name]

    lines = [
        f"# Generated from alight/schemes/alight.yml + alight/identity.yml",
        f"# for '{tool_name}'. Do not edit by hand -- re-run:",
        f"#   uv run scripts/export_python.py {tool_name} <this-path>",
        "",
        "SEMANTIC = {",
    ]
    for role, hexval in semantic.items():
        lines.append(f'    "{role}": "{hexval}",')
    lines += [
        "}",
        "",
        f'ACCENT = "{accent_hex}"  # {tool_name}\'s own identity color ({accent_name})',
        "",
    ]

    content = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote {output_path}")

    # self-verify: exec the generated module in isolation and confirm
    # every value matches alight.yml/identity.yml
    namespace: dict = {}
    exec(output_path.read_text(encoding="utf-8"), namespace)

    ok = True
    for role, expected in semantic.items():
        got = namespace["SEMANTIC"].get(role)
        match = got is not None and got.upper() == expected.upper()
        ok &= match
        if not match:
            print(f"  MISMATCH SEMANTIC[{role!r}]: expected={expected} got={got}")
    if namespace["ACCENT"].upper() != accent_hex.upper():
        ok = False
        print(f"  MISMATCH ACCENT: expected={accent_hex} got={namespace['ACCENT']}")

    print("ALL MATCH -- safe to import" if ok else "MISMATCHES FOUND")


if __name__ == "__main__":
    main()
