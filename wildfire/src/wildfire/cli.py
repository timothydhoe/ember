"""
wildfire.cli
~~~~~~~~~~~~
Entry point for the `wildfire` command.

    wildfire your thought right here        -> quick-add
    wildfire -                              -> quick-add from stdin
    wildfire --note "Title"                 -> create a spark (Note)
    wildfire --search <query>               -> substring search
    wildfire --backlinks <name>             -> show what links to <name>
    wildfire --catch-latest "Title"         -> catch the most recent wisp
    wildfire --catch <query> --as "Title"   -> catch a matched wisp
    wildfire                                -> ??? (future TUI?)
"""

from __future__ import annotations

import shlex
import subprocess
import sys

from .config import Config
from .corpus import CatchResult, Corpus
from .models import Entry, Note


def _format_lists(
    entries: list[Entry] | None = None, notes: list[Note] | None = None
) -> str:
    lines = []
    if entries is not None:
        if entries:
            lines.append("Wisps:")
            for entry in entries:
                lines.append(f" {entry.date.isoformat()} {entry.time} {entry.text}")
        else:
            lines.append("No wisps created yet.")
    if notes is not None:
        if notes:
            lines.append("Sparks:")
            for note in notes:
                lines.append(f" {note.name}")
        else:
            lines.append("No sparks created yet.")
    return "\n".join(lines)


def _format_matches(entries: list[Entry], notes: list[Note], empty_message: str) -> str:
    if not entries and not notes:
        return empty_message
    lines = []
    if entries:
        lines.append("Wisps:")
        for entry in entries:
            lines.append(f" ∘ {entry.date.isoformat()} {entry.time} {entry.text}")
    if notes:
        lines.append("Sparks:")
        for note in notes:
            lines.append(f" ✦ {note.name}")
    return "\n".join(lines)


def _format_catch_result(
    result: CatchResult, caught_entry: Entry, match_count: int | None = None
) -> str:
    lines = [
        f"Wisp caught into: {result.note.name}",
        f' "{caught_entry.text}"',
    ]
    if match_count is not None and match_count > 1:
        lines.append(f"(most recent of {match_count} matches)")
    if result.suggestions:
        lines.append("suggested links:")
        for suggestion in result.suggestions:
            lines.append(
                f" {suggestion.note.name} • shares {suggestion.score}) word(s)"
            )
    return "\n".join(lines)


def run(args: list[str], corpus: Corpus) -> str:
    if not args:
        return "No thoughts at all?"

    first, *rest = args

    if first == "--backlinks":
        fuzzy = "--fuzzy" in rest
        name = " ".join(word for word in rest if word != "--fuzzy")
        if fuzzy:
            result = corpus.fuzzy_backlinks(name)
            return _format_matches(result.entries, result.notes, "No matches found.")
        result = corpus.backlinks(name)
        return _format_matches(result.entries, result.notes, "No links here yet.")

    elif first == "--catch":
        if "--as" not in rest:
            return "Try: --catch <query> --as <title>"
        split_index = rest.index("--as")
        query = " ".join(rest[:split_index])
        title = " ".join(rest[split_index + 1 :])
        if not query.strip() or not title.strip():
            return "Try: --catch <query> --as <title>"
        matches = corpus.search(query).entries
        if not matches:
            return f"No wisp found matching '{query}'."
        entry = matches[-1]
        result = corpus.catch(entry, title)
        return _format_catch_result(result, entry, match_count=len(matches))

    elif first == "--catch-latest":
        title = " ".join(rest)
        if not title.strip():
            return "Try: --catch-latest <title>"
        entries = corpus.all_entries()
        if not entries:
            return "No wisps have been found."
        last_entry = entries[-1]
        result = corpus.catch(last_entry, title)
        return _format_catch_result(result, last_entry)

    elif first == "--delete":
        confirm = "--confirm" in rest
        name = " ".join(word for word in rest if word != "--confirm")
        if not name.strip():
            return "Try: --delete <name>"
        note = corpus.get_note(name)
        if not note.exists:
            return "Nothing there. Are you sure it exists?"
        backlinks = corpus.backlinks(name)
        if not backlinks.entries and not backlinks.notes:
            warning = f"'{note.name}' has no backlinks."
        else:
            preview = _format_matches(
                backlinks.entries, backlinks.notes, "Nothing links here yet"
            )
            warning = f"Deleting '{note.name}' will break these backlinks:\n{preview}"
        if not confirm:
            return f"{warning}\nRun again with --confirm to proceed."
        note.delete()
        return f"{note.name} has been deleted."

    elif first == "--help" or first ==  "-h":
        return """wildfire — catch your wisps, turn them into sparks

USAGE
  wildfire <text>                quick-add a wisp
  wildfire -                     read a wisp from stdin

SPARKS
  --note <title>                 create or open a spark by title
  --show <name>                  print a spark's contents
  --open <name>                  jump to a spark, creating it if it doesn't exist
  --delete <name>                show what backlinks would break
  --delete <name> --confirm      actually delete

CATCHING
  --catch <query> --as <title>   turn a matching wisp into a spark
  --catch-latest <title>         turn the most recent wisp into a spark

FINDING
  --search <query>               search wisps and sparks
  --backlinks <name>             show what links to a spark
  --backlinks <name> --fuzzy     ...typo-tolerant
  --list, --list-wisps, --list-sparks

  -h, --help                     show this text
        """

    elif first == "--list":
        return _format_lists(entries=corpus.all_entries(), notes=corpus.list_notes())
    elif first == "--list-wisps":
        return _format_lists(entries=corpus.all_entries())
    elif first == "--list-sparks":
        return _format_lists(notes=corpus.list_notes())

    elif first == "--note":
        title = " ".join(rest)
        if not title.strip():
            return "Try: --note <title>"
        existed = corpus.get_note(title).exists
        note = corpus.create_note(title)
        if existed:
            return f"Spark already exists: {note.name}"
        return f"✦ Spark created: {note.name}"

    elif first == "--open":
        name = " ".join(rest)
        if not name.strip():
            return "Try: --open <name>"
        note = corpus.create_note(name)
        editor_cmd = corpus.config.resolve_editor()
        try:
            result = subprocess.run(shlex.split(editor_cmd) + [note.path])
        except FileNotFoundError:
            return f"Couldn't launch editor: '{editor_cmd}'. Set EDITOR, or 'editor' in config.toml."
        return f"Closed: {note.name}"

    elif first == "--search":
        query = " ".join(rest)
        if not query:
            return "Query is missing. Cannot find emptiness."
        results = corpus.search(query)
        return _format_matches(results.entries, results.notes, "No matches.")

    elif first == "--show":
        name = " ".join(rest)
        if not name.strip():
            return "Try: --show <name>"
        note = corpus.get_note(name)
        if not note.exists:
            return f"No spark called '{name}' yet. --open will create it."
        return note.read()

    # not a recognised flag -> quick-add
    text = " ".join(args)
    try:
        entry = corpus.append_entry(text)
    except ValueError:
        return "Your mind can't be blank, right?"
    return f" ∘ {entry.time} {entry.text}"


def main() -> None:
    config = Config.load()
    corpus = Corpus(config)

    args = sys.argv[1:]
    if args == ["-"]:
        text = sys.stdin.readline().strip()
        print(run([text], corpus))
    else:
        print(run(args, corpus))
