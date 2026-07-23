"""
wildfire.cli
~~~~~~~~~~~~
Entry point for the `wildfire` command.

    wildfire "your text"    -> quick-add
"""

from __future__ import annotations

import sys

from .config import Config
from .corpus import Corpus


def run(args: list[str], corpus: Corpus) -> str:
    if not args:
        return "No thoughts at all?"

    text = " ".join(args)
    try:
        entry = corpus.append_entry(text)
    except ValueError:
        return "Your mind can't be blank, right?"
    return f" -> {entry.time} {entry.text}"


def main() -> None:
    config = Config.load()
    corpus = Corpus(config)
    print(run(sys.argv[1:], corpus))
