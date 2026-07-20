from pathlib import Path
from wildfire.config import Config


def test_config_defaults():
    cfg = Config()
    assert cfg.wildfire_dir == Path("~/Wildfire").expanduser()
    assert cfg.wisps_dir == Path("~/Wildfire/wisps").expanduser()
    assert cfg.sparks_dir == Path("~/Wildfire/sparks").expanduser()


def test_resolve_editor_falls_back_to_vim(monkeypatch):
    monkeypatch.delenv("VISUAL", raising=False)
    monkeypatch.delenv("EDITOR", raising=False)
    cfg = Config()
    assert cfg.resolve_editor() == "vim"


def test_resolve_editor_prefers_configured_value(monkeypatch):
    monkeypatch.setenv("EDITOR", "nano")
    cfg = Config(editor="nvim")
    assert cfg.resolve_editor() == "nvim"
