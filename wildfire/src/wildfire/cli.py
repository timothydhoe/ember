"""
wildfire.cli
~~~~~~~~~~~~
Entry point for the `wildfire` command. Run `wildfire --help` for the full flag reference.
"""

from __future__ import annotations

import sys

from . import identity
from .config import Config
from .corpus import Corpus
from .handlers import RunResult, run, run_stdin


def _hex_to_rgb(hexval: str) -> tuple[int, int, int]:
    hexval = hexval.lstrip("#")
    return int(hexval[0:2], 16), int(hexval[2:4], 16), int(hexval[4:6], 16)


def _render(result: RunResult) -> str:
    if result.role is None or not sys.stdout.isatty():
        return result.text
    colors = identity.resolve_colors()
    if colors is None:
        return result.text
    if result.role == "banner":
        return _render_banner(result.text, colors)
    if result.role not in colors:
        return result.text
    r, g, b = _hex_to_rgb(colors[result.role])
    return f"\x1b[38;2;{r};{g};{b}m{result.text}\x1b[0m"


def _render_banner(text: str, colors: dict[str, str]) -> str:
    accent = colors.get("accent")
    wildfire_accent = identity.resolve_accent() or accent
    lines = text.splitlines()
    out = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i == 0 and stripped and wildfire_accent:
            r, g, b = _hex_to_rgb(wildfire_accent)
            out.append(f"\x1b[1m\x1b[38;2;{r};{g};{b}m{line}\x1b[0m")
        elif stripped and stripped.isupper() and stripped.isalpha and accent:
            r, g, b = _hex_to_rgb(accent)
            out.append(f"\x1b[1m\x1b[38;2;{r};{g};{b}m{line}\x1b[0m")
        else:
            out.append(line)
    return "\n".join(out)


def main() -> None:
    config = Config.load()
    corpus = Corpus(config)

    args = sys.argv[1:]
    if args == ["-"]:
        result = run_stdin(sys.stdin.read().splitlines(), corpus)
    else:
        result = run(args, corpus)
    print(_render(result))
