"""
wildfire.handlders
~~~~~~~~~~~~~~~~~~
"""

from __future__ import annotations

import shlex
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from .corpus import CatchResult, Corpus
from .models import Entry, Note

Role = Literal["error", "warning", "success", "banner"]


@dataclass
class RunResult:
    text: str
    role: Role | None = None

    def __str__(self) -> str:
        return self.text


def _format_lists(
    entries: list[Entry] | None = None, notes: list[Note] | None = None
) -> str:
    lines = []
    if entries is not None:
        if entries:
            lines.append("Wisps:")
            for entry in entries:
                lines.append(f" ∘ {entry.date.isoformat()} {entry.time} {entry.text}")
        else:
            lines.append("No wisps created yet.")
    if notes is not None:
        if notes:
            lines.append("Sparks:")
            for note in notes:
                lines.append(f" ✦ {note.title}")
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
            lines.append(f" ✦ {note.title}")
    return "\n".join(lines)


def _format_catch_result(
    result: CatchResult, caught_entry: Entry, match_count: int | None = None
) -> str:
    lines = [
        f"Wisp caught into: {result.note.title}",
        f' "{caught_entry.text}"',
    ]
    if match_count is not None and match_count > 1:
        lines.append(f"(most recent of {match_count} matches)")
    if result.suggestions:
        lines.append("suggested links:")
        for suggestion in result.suggestions:
            lines.append(
                f" {suggestion.note.title} • shares {suggestion.score}) word(s)"
            )
    return "\n".join(lines)


# ~~~
# HANDLERS, PER FLAG -> RunResult
# ~~~


def _handle_backlinks(rest: list[str], corpus: Corpus) -> RunResult:
    fuzzy = "--fuzzy" in rest
    name = " ".join(word for word in rest if word != "--fuzzy")
    if fuzzy:
        result = corpus.fuzzy_backlinks(name)
        return RunResult(
            _format_matches(result.entries, result.notes, "No matches found.")
        )
    result = corpus.backlinks(name)
    return RunResult(
        _format_matches(result.entries, result.notes, "No links here yet.")
    )


def _handle_catch(rest: list[str], corpus: Corpus) -> RunResult:
    if "--as" not in rest:
        return RunResult("Try: --catch <query> --as <title>", role="error")
    split_index = rest.index("--as")
    query = " ".join(rest[:split_index])
    title = " ".join(rest[split_index + 1 :])
    if not query.strip() or not title.strip():
        return RunResult("Try: --catch <query> --as <title>", role="error")
    matches = corpus.search(query).entries
    if not matches:
        return RunResult(f"No wisp found matching '{query}'.", role="error")
    entry = matches[-1]
    result = corpus.catch(entry, title)
    text = _format_catch_result(result, entry, match_count=len(matches))
    return RunResult(text, role="success")


def _handle_catch_latest(rest: list[str], corpus: Corpus) -> RunResult:
    title = " ".join(rest)
    if not title.strip():
        return RunResult("Try: --catch-latest <title>", role="error")
    entries = corpus.all_entries()
    if not entries:
        return RunResult("No wisps have been found.", role="error")
    last_entry = entries[-1]
    result = corpus.catch(last_entry, title)
    return RunResult(_format_catch_result(result, last_entry), role="success")


def _handle_delete(rest: list[str], corpus: Corpus) -> RunResult:
    confirm = "--confirm" in rest
    name = " ".join(word for word in rest if word != "--confirm")
    if not name.strip():
        return RunResult("Try: --delete <name>", role="error")
    note = corpus.get_note(name)
    if not note.exists:
        return RunResult("Nothing there. Are you sure it exists?", role="error")
    backlinks = corpus.backlinks(name)
    if not backlinks.entries and not backlinks.notes:
        warning = f"'{note.title}' has no backlinks."
    else:
        preview = _format_matches(
            backlinks.entries, backlinks.notes, "Nothing links here yet"
        )
        warning = f"Deleting '{note.title}' will break these backlinks:\n{preview}"
    if not confirm:
        return RunResult(
            f"{warning}\nRun again with --confirm to proceed.", role="warning"
        )
    note.delete()
    return RunResult(f"{note.title} has been deleted.", role="success")


def _handle_help(rest: list[str], corpus: Corpus) -> RunResult:
    return RunResult(
        """wildfire — catch your wisps, turn them into sparks

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
        """,
        role="banner",
    )


def _handle_list(rest: list[str], corpus: Corpus) -> RunResult:
    return RunResult(
        _format_lists(entries=corpus.all_entries(), notes=corpus.list_notes())
    )


def _handle_list_wisps(rest: list[str], corpus: Corpus) -> RunResult:
    return RunResult(_format_lists(entries=corpus.all_entries()))


def _handle_list_sparks(rest: list[str], corpus: Corpus) -> RunResult:
    return RunResult(_format_lists(notes=corpus.list_notes()))


def _handle_note(rest: list[str], corpus: Corpus) -> RunResult:
    title = " ".join(rest)
    if not title.strip():
        return RunResult("Try: --note <title>", role="error")
    existed = corpus.get_note(title).exists
    note = corpus.create_note(title)
    if existed:
        return RunResult(f"Spark already exists: {note.title}")
    return RunResult(f"✦ Spark created: {note.title}", role="success")


def _handle_open(rest: list[str], corpus: Corpus) -> RunResult:
    name = " ".join(rest)
    if not name.strip():
        return RunResult("Try: --open <name>", role="error")
    note = corpus.create_note(name)
    editor_cmd = corpus.config.resolve_editor()
    try:
        subprocess.run(shlex.split(editor_cmd) + [note.path])
    except FileNotFoundError:
        return RunResult(
            f"Couldn't launch editor: '{editor_cmd}'. Set EDITOR, or 'editor' in config.toml.",
            role="error",
        )
    return RunResult(f"Closed: {note.title}", role="success")


def _handle_search(rest: list[str], corpus: Corpus) -> RunResult:
    query = " ".join(rest)
    if not query:
        return RunResult("Query is missing. Cannot find emptiness.", role="error")
    results = corpus.search(query)
    return RunResult(_format_matches(results.entries, results.notes, "No matches."))


def _handle_show(rest: list[str], corpus: Corpus) -> RunResult:
    name = " ".join(rest)
    if not name.strip():
        return RunResult("Try: --show <name>", role="error")
    note = corpus.get_note(name)
    if not note.exists:
        return RunResult(
            f"No spark called '{name}' yet. --open will create it.", role="error"
        )
    return RunResult(note.read())


def _handle_quick_add(args: list[str], corpus: Corpus) -> RunResult:
    text = " ".join(args)
    try:
        entry = corpus.append_entry(text)
    except ValueError:
        return RunResult("Your mind can't be blank, right?", role="error")
    return RunResult(f" ∘ {entry.time} {entry.text}", role="success")


HANDLERS: dict[str, Callable[[list[str], Corpus], RunResult]] = {
    "--backlinks": _handle_backlinks,
    "--catch": _handle_catch,
    "--catch-latest": _handle_catch_latest,
    "--delete": _handle_delete,
    "--help": _handle_help,
    "-h": _handle_help,
    "--list": _handle_list,
    "--list-wisps": _handle_list_wisps,
    "--list-sparks": _handle_list_sparks,
    "--note": _handle_note,
    "--open": _handle_open,
    "--search": _handle_search,
    "--show": _handle_show,
}


def run(args: list[str], corpus: Corpus) -> RunResult:
    if not args:
        return RunResult("No thoughts at all?")

    first, *rest = args
    handler = HANDLERS.get(first)

    if handler is None:
        return _handle_quick_add(args, corpus)
    return handler(rest, corpus)
