from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")


@dataclass
class Entry:
    time: str
    text: str
    date: date
    # context: str /regex needed
    # link: str /regex needed


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
        # if path.exists: read file, find every [[...]] match
        # else: links = []
        # return cls(name=..., path=path, links=...))

    def read(self) -> str:
        if self.exists:
            return self.path.read_text(encoding="utf-8")
        return ""

    def write(self, content: str) -> None:
        self.path.write_text(content, encoding="utf-8")
        self.links = _WIKILINK.findall(content)
