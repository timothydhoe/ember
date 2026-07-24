"""
wildfire.corpus
~~~~~~~~~~~~~~~
The point of access for ~/Wildfire/

Also defines the result types: Backlinks, SearchResults, CatchResults, and Linksuggestions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from wildfire.config import Config
from wildfire.models import DailyLog, Entry, Note, slugify, tokenize


@dataclass
class Backlinks:
    entries: list[Entry] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)


@dataclass
class CatchResult:
    note: Note
    suggestions: list[LinkSuggestion] = field(default_factory=list)


@dataclass
class LinkSuggestion:
    note: Note
    score: int


@dataclass
class SearchResults:
    entries: list[Entry] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)


class Corpus:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.config.ensure_dirs()

    def daily_path(self, log_date: date | None = None) -> Path:
        log_date = log_date or date.today()
        return self.config.entries_dir / f"{log_date.isoformat()}.md"

    def today(self) -> DailyLog:
        return self.load_daily(date.today())

    def load_daily(self, log_date: date) -> DailyLog:
        path = self.daily_path(log_date)
        if not path.exists():
            return DailyLog(date=log_date, path=path, entries=[])
        return DailyLog.from_path(path)

    def backlinks(self, name: str) -> Backlinks:
        target = slugify(name)
        matching_entries = [
            entry
            for entry in self.all_entries()
            if any(slugify(link) == target for link in entry.links)
        ]
        matching_notes = [
            note
            for note in self.list_notes()
            if any(slugify(link) == target for link in note.links)
        ]
        return Backlinks(entries=matching_entries, notes=matching_notes)

    # ~~~ Entries/wisps ~~~
    def append_entry(self, text: str, log_date: date | None = None) -> Entry:
        log_date = log_date or date.today()
        path = self.daily_path(log_date)
        now = datetime.now().strftime("%H:%M")
        if not text.strip():
            raise ValueError("wisp text cannot be empty")
        line = f"- {now} {text}"

        with open(path, "a", encoding="utf-8") as f:
            # write line + add newline
            f.write(line + "\n")

        entry = Entry(time=now, text=text, date=log_date)
        return entry

    def all_entries(self) -> list[Entry]:
        entries = []
        for path in sorted(self.config.entries_dir.glob("????-??-??.md")):
            log = DailyLog.from_path(path)
            entries.extend(log.entries)
        return entries

    # ~~~ Notes/sparks ~~~
    def note_path(self, name: str) -> Path:
        return self.config.notes_dir / f"{slugify(name)}.md"

    def get_note(self, name: str) -> Note:
        return Note.from_path(self.note_path(name))

    def create_note(self, title: str) -> Note:
        path = self.note_path(title)
        if not path.exists():
            path.write_text(f"# {title}\n\n", encoding="utf-8")
        return Note.from_path(path)

    def list_notes(self) -> list[Note]:
        paths = sorted(self.config.notes_dir.glob("*.md"))
        return [Note.from_path(path) for path in paths]

    def search(self, query: str) -> SearchResults:
        query = query.lower()
        matching_entries = [
            entry for entry in self.all_entries() if query in entry.text.lower()
        ]
        matching_notes = [
            note for note in self.list_notes() if query in note.read().lower()
        ]

        return SearchResults(entries=matching_entries, notes=matching_notes)

    # ~~ Catch ~~
    def _suggest_links(
        self, entry: Entry, exclude: Note | None = None
    ) -> list[LinkSuggestion]:
        entry_tokens = tokenize(entry.text)
        suggestions = []
        for note in self.list_notes():
            if exclude is not None and note.path == exclude.path:
                continue
            note_tokens = tokenize(note.title)
            score = len(entry_tokens & note_tokens)
            if score >= 1:
                suggestions.append(LinkSuggestion(note=note, score=score))
        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions

    def catch(self, entry: Entry, title: str) -> CatchResult:
        note = self.create_note(title)
        if entry.text not in note.read():
            note.append(entry.text)
        suggestions = self._suggest_links(entry, exclude=note)
        return CatchResult(note=note, suggestions=suggestions)
