"""
alight._ansi
~~~~~~~~~~~~~
Minimal ANSI color helpers for the reports generate_all.py
and export_nvim.py print
"""

from __future__ import annotations

import sys

_TTY = sys.stdout.isatty()


def _wrap(code: str, text: str) -> str:
    if not _TTY:
        return text
    return f"\x1b[{code}m{text}\x1b[0m"


def green(text: str) -> str:
    return _wrap("32", text)


def red(text: str) -> str:
    return _wrap("31", text)


def yellow(text: str) -> str:
    return _wrap("33", text)


def cyan(text: str) -> str:
    return _wrap("36", text)


def bold(text: str) -> str:
    return _wrap("1", text)


def dim(text: str) -> str:
    return _wrap("2", text)
