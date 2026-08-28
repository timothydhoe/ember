"""
alight.export_tmux
~~~~~~~~~~~~~~~~~~~

    uv run scripts/export_tmux.py
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"
OUTPUT_DIR = BASE_DIR / "terminal" / "tmux"

CONTRAST_LEVELS = ["hard", "medium", "soft"]


def build(p: dict, sem: dict, surface: dict) -> str:
    base, raised = surface["base"], surface["raised"]

    lines = [
        "# Generated from alight.yml -- do not edit by hand, re-run export_tmux.py",
        "",
        "# -- status bar: baseline (mirrors vim's StatusLineNC/raised chrome) --",
        f'set -g status-style "fg={p["foreground"]},bg={raised}"',
        "",
        "# -- window tabs: active vs inactive --",
        "# active: bg=accent, fg=base, bold -- mirrors vim's StatusLine",
        f'set -g window-status-current-style "fg={base},bg={sem["accent"]},bold"',
        "# inactive: fg=muted, bg=raised -- mirrors vim's StatusLineNC",
        f'set -g window-status-style "fg={sem["muted"]},bg={raised}"',
        "",
        "# -- pane borders --",
        f'set -g pane-border-style "fg={sem["muted"]}"',
        f'set -g pane-active-border-style "fg={sem["accent"]}"',
        "",
        "# -- messages / command prompt: mirrors vim's WildMenu/PmenuSel --",
        f'set -g message-style "fg={base},bg={sem["accent"]}"',
        f'set -g message-command-style "fg={base},bg={sem["accent"]}"',
        "",
        "# -- copy mode selection: mirrors vim's Visual (bg only, no fg override) --",
        f'set -g mode-style "bg={p["selection"]}"',
        "",
        "# -- clock mode --",
        f'set -g clock-mode-colour "{sem["accent"]}"',
        "",
    ]

    return "\n".join(lines) + "\n"


def self_verify(content: str, p: dict, sem: dict, surface: dict) -> bool:
    expected_hexes = {
        p["foreground"],
        p["selection"],
        sem["accent"],
        sem["muted"],
        surface["base"],
        surface["raised"],
    }
    found_hexes = set(re.findall(r"#[0-9A-Fa-f]{6}", content))
    return found_hexes == expected_hexes


def main() -> bool:
    data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    p, sem = data["palette"], data["semantic"]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for level in CONTRAST_LEVELS:
        surface = data["contrast"][level]["surface"]
        content = build(p, sem, surface)
        out = OUTPUT_DIR / f"alight-{level}.tmux.conf"
        out.write_text(content, encoding="utf-8")
        print(f"Wrote {out}")

        written = out.read_text(encoding="utf-8")
        level_ok = self_verify(written, p, sem, surface)
        ok &= level_ok
        status = "ALL MATCH" if level_ok else "MISMATCH"
        print(f"  {level}: {status}")

    print("ALL MATCH -- safe to use" if ok else "MISMATCHES FOUND")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
