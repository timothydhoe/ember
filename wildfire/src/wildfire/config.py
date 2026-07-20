"""
wildfire.config
~~~~~~~~~~~~~~~
Read and writes ~/.ember-hearth/wildfire/config.toml
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import tomlkit

CONFIG_DIR = Path.home() / ".ember-hearth" / "wildfire"
CONFIG_FILE = CONFIG_DIR / "config.toml"


@dataclass
class Config:
    config_version: int = 1
    name: str = ""
    wildfire_dir: Path = field(default_factory=lambda: Path("~/Wildfire").expanduser())
    editor: str = ""

    @property
    def wisps_dir(self) -> Path:
        return self.wildfire_dir / "wisps"

    @property
    def sparks_dir(self) -> Path:
        return self.wildfire_dir / "sparks"

    @classmethod
    def load(cls) -> Config:
        if not CONFIG_FILE.exists():
            cfg = cls()
            cfg.save()
            return cfg
        doc = tomlkit.parse(CONFIG_FILE.read_text(encoding="utf-8"))
        return cls(
            config_version=doc.get("config_version", 1),
            name=doc.get("name", ""),
            wildfire_dir=Path(doc.get("wildfire_dir", "~/Wildfire")).expanduser(),
            editor=doc.get("editor", ""),
        )

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        if CONFIG_FILE.exists():
            doc = tomlkit.parse(CONFIG_FILE.read_text(encoding="utf-8"))
        else:
            doc = tomlkit.document()

        doc["config_version"] = self.config_version
        doc["name"] = self.name
        doc["wildfire_dir"] = str(self.wildfire_dir).replace(str(Path.home()), "~")
        doc["editor"] = self.editor

        CONFIG_FILE.write_text(tomlkit.dumps(doc), encoding="utf-8")

        return None

    def resolve_editor(self) -> str:
        import os

        return (
            self.editor
            or os.environ.get("VISUAL", "")
            or os.environ.get("EDITOR", "")
            or "vim"
        )

    def ensure_dirs(self) -> None:
        self.wisps_dir.mkdir(parents=True, exist_ok=True)
        self.sparks_dir.mkdir(parents=True, exist_ok=True)
