"""
Ask the terminal what colors it's ACTUALLY using.

Usage:
    uv run scripts/live_verify_colors.py [hard|medium|soft]

Defaults to medium if no contrast level is given.
"""

from __future__ import annotations

import re
import select
import sys
import termios
import time
import tty
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).parent.parent  # scripts/ -> alight/ root
SCHEME_FILE = BASE_DIR / "schemes" / "alight.yml"

ANSI_INDEX_MAP = {
    0: "black",
    1: "red",
    2: "green",
    3: "yellow",
    4: "blue",
    5: "magenta",
    6: "cyan",
    7: "white",
    8: "bright_black",
    9: "bright_red",
    10: "bright_green",
    11: "bright_yellow",
    12: "bright_blue",
    13: "bright_magenta",
    14: "bright_cyan",
    15: "bright_white",
}

REPLY_RE = re.compile(
    r"\x1b\](\d+);(?:(\d+);)?rgb:([0-9a-fA-F]{2,4})/([0-9a-fA-F]{2,4})/([0-9a-fA-F]{2,4})"
)


def to8(h: str) -> int:
    v = int(h, 16)
    maxval = (16 ** len(h)) - 1
    return round(v / maxval * 255)


def query_all(seqs: list[str], timeout: float = 0.5) -> dict[str, str]:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    results: dict[str, str] = {}
    try:
        tty.setraw(fd)
        termios.tcflush(fd, termios.TCIFLUSH)  # drop any stale bytes first
        sys.stdout.write("".join(seqs))
        sys.stdout.flush()

        buf = ""
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            ready, _, _ = select.select([fd], [], [], remaining)
            if not ready:
                break
            buf += sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    for m in REPLY_RE.finditer(buf):
        osc_num, ansi_index, r, g, b = m.groups()
        hexval = f"#{to8(r):02X}{to8(g):02X}{to8(b):02X}"
        key = f"osc{osc_num}" if ansi_index is None else f"ansi{ansi_index}"
        results[key] = hexval
    return results


def main():
    contrast = sys.argv[1] if len(sys.argv) > 1 else "medium"
    valid_levels = ("hard", "medium", "soft")
    if contrast not in valid_levels:
        print(f"Unknown contrast '{contrast}' -- expected one of {valid_levels}")
        raise SystemExit(1)

    yaml_data = yaml.safe_load(SCHEME_FILE.read_text(encoding="utf-8"))
    ansi = yaml_data["ansi"]
    palette = yaml_data["palette"]
    surface = yaml_data["contrast"][contrast]["surface"]

    seqs = ["\x1b]10;?\x07", "\x1b]11;?\x07", "\x1b]12;?\x07"]
    seqs += [f"\x1b]4;{i};?\x07" for i in ANSI_INDEX_MAP]

    checks = [
        ("foreground", "osc10", palette["foreground"]),
        (f"background ({contrast})", "osc11", surface["base"]),
        ("cursor", "osc12", palette["cursor"]),
    ]
    for index, key in ANSI_INDEX_MAP.items():
        checks.append((f"ansi[{index}] {key}", f"ansi{index}", ansi[key]))

    got = query_all(seqs, timeout=1.5)

    print(f"{'slot':24s} {'expected':10s} {'reported':10s} status")
    print("-" * 60)
    for label, result_key, expected in checks:
        reported = got.get(result_key)
        if reported is None:
            status = "no response"
        elif reported.upper() == expected.upper():
            status = "OK"
        else:
            status = "MISMATCH"
        print(f"{label:24s} {expected:10s} {reported or '?':10s} {status}")

    if not got:
        print(
            "\nNo responses at all -- this terminal (or session, e.g. "
            "tmux/screen) likely doesn't support OSC color queries. Try "
            "running this directly in a fresh Terminal.app window."
        )


if __name__ == "__main__":
    main()
