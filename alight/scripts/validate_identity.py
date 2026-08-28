"""
validate_identity
~~~~~~~~~~~~~~~~~

Check that every colour name referenced in identity.yml actually exists in schemes/alight.yml's named palette

Usage:
    uv run scripts/validate_identity.py

output:
    <programme-name> -> <associated-brand-colour>
"""

from __future__ import annotations

from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
IDENTITY_FILE = BASE_DIR / "identity.yml"


def main() -> None:
    scheme = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    identity = yaml.safe_load(IDENTITY_FILE.read_text(encoding="utf-8"))

    if "named" not in scheme:
        raise ValueError(f"{SCHEME_FILE} is missing its 'named' block")

    valid_names = set(scheme["named"].keys())
    tools = identity.get("tools", {})
    brand = identity.get("brand", {})
    errors: list[str] = []

    for tool, spec in tools.items():
        color = spec.get("color")
        if color not in valid_names:
            errors.append(
                f"tools.{tool}.color = '{color}' -- not in alight.yml's named palette"
            )

    for scope, spec in brand.items():
        for color in spec.get("gradient", []):
            if color not in valid_names:
                errors.append(
                    f"brand.{scope}.gradient contains '{color}' -- not in alight.yml's named palette"
                )

    asset_paths: dict[str, str] = {}
    for tool, spec in tools.items():
        for kind, path in spec.get("assets", {}).items():
            asset_paths[f"tools.{tool}.assets.{kind}"] = path
    for scope, spec in brand.items():
        for variant, kinds in spec.get("assets", {}).items():
            for kind, path in kinds.items():
                asset_paths[f"brand.{scope}.assets.{variant}.{kind}"] = path

    for label, rel_path in asset_paths.items():
        if not (BASE_DIR / rel_path).exists():
            errors.append(f"{label} = '{rel_path}' -- file does not exist")

    if errors:
        print("FAILED:")
        for e in errors:
            print(f"  {e}")
        raise SystemExit(1)

    print(f"OK -- {len(tools)} tool color reference(s) all resolve correctly")
    for tool, spec in tools.items():
        hexval = scheme["named"][spec["color"]]
        print(f"  {tool:12s} -> {spec['color']} ({hexval})")

    print(f"OK -- {len(brand)} brand gradient reference(s) all resolve correctly")
    for scope, spec in brand.items():
        hexvals = [scheme["named"][c] for c in spec.get("gradient", [])]
        print(f"  {scope:12s} -> {spec['gradient']} ({', '.join(hexvals)})")

    print(f"OK -- {len(asset_paths)} asset path reference(s) point to real files")


if __name__ == "__main__":
    main()
