"""
wildfire.cli
~~~~~~~~~~~~
Entry point for the `wildfire` command.

    wildfire your thought right here    -> quick-add
    wildfire --note "Title"             -> create a spark (Note)
    wildfire --search <query>           -> substring search
    wildfire --backlinks <name>         -> what links here
    wildfire                            -> ??? (future TUI?)
"""

from __future__ import annotations

import sys

from .config import Config
from .corpus import Corpus
from .models import Entry, Note


def _format_matches(entries: list[Entry], notes: list[Note], empty_message: str) -> str:
    if not entries and not notes:
        return empty_message
    lines = []
    if entries:
        lines.append("Wisps:")
        for entry in entries:
            lines.append(f"  {entry.date.isoformat()} {entry.time} {entry.text}")
    if notes:
        lines.append("Sparks:")
        for note in notes:
            lines.append(f" {note.name}")
    return "\n".join(lines)


def run(args: list[str], corpus: Corpus) -> str:
    if not args:
        return "No thoughts at all?"

    first, *rest = args

    if first == "--note":
        title = " ".join(rest)
        existed = corpus.get_note(title).exists
        note = corpus.create_note(title)
        if existed:
            return f"Spark already exists: {note.title}"
        return f"Created spark: {note.title}"
    elif first == "--search":
        query = " ".join(rest)
        if not query:
            return "Query is missing. Cannot find emptiness."
        results = corpus.search(query)
        return _format_matches(results.entries, results.notes, "No matches.")
    elif first == "--backlinks":
        name = " ".join(rest)
        result = corpus.backlinks(name)
        return _format_matches(result.entries, result.notes, "No links here yet.")

    # not a recognised flag -> quick-add
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
