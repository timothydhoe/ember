from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
import re

_CONTEXT = re.compile(r"@([\w-]+)")
_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
_ENTRY_LINE = re.compile(r"^- (\d{2}:\d{2}) (.+)$")


@dataclass
class DailyLog:
    date: date
    path: Path
    entries: list[Entry]

    @classmethod
    def from_path(cls, path) -> DailyLog:
        entries = []
        log_date = date.fromisoformat(path.stem)
        for line in path.read_text(encoding="utf-8").splitlines():
            entry = Entry.parse(line, log_date)
            if entry is not None:
                entries.append(entry)

        return cls(date=log_date, path=path, entries=entries)


@dataclass
class Entry:
    time: str
    text: str
    date: date
    contexts: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.contexts = _CONTEXT.findall(self.text)
        self.links = _WIKILINK.findall(self.text)

    @classmethod
    def parse(cls, line: str, log_date: date) -> Entry | None:
        match = _ENTRY_LINE.match(line)
        if not match:
            return None
        return cls(time=match.group(1), text=match.group(2), date=log_date)


@dataclass
class Note:
    name: str
    path: Path
    links: list[str]

    @property
    def title(self) -> str:
        return self.name.replace("-", " ").replace("_", " ")

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @classmethod
    def from_path(cls, path) -> Note:
        name = path.stem
        if path.exists():
            content = path.read_text(encoding="utf-8")
            links = _WIKILINK.findall(content)
        else:
            links = []
        return cls(name=name, path=path, links=links)

    def read(self) -> str:
        if self.exists:
            return self.path.read_text(encoding="utf-8")
        return ""

    def write(self, content: str) -> None:
        self.path.write_text(content, encoding="utf-8")
        self.links = _WIKILINK.findall(content)
