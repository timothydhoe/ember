import io
import sys

from wildfire.cli import _render, main
from wildfire.config import Config
from wildfire.handlers import RunResult


def test_render_plain_when_not_a_tty(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    result = RunResult("done", role="success")
    assert _render(result) == "done"


def test_render_plain_when_role_is_none(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    result = RunResult("just some text", role=None)
    assert _render(result) == "just some text"


def test_render_plain_when_no_identity_file(monkeypatch):
    from wildfire import identity as identity_module

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(identity_module, "resolve_colors", lambda: None)
    result = RunResult("uh oh", role="error")
    assert _render(result) == "uh oh"


def test_render_colors_when_tty_and_identity_present(monkeypatch):
    from wildfire import identity as identity_module

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(identity_module, "resolve_colors", lambda: {"error": "#E89292"})
    result = RunResult("uh oh", role="error")
    rendered = _render(result)
    assert rendered == "\x1b[38;2;232;146;146muh oh\x1b[0m"


def test_render_plain_when_role_missing_from_identity(monkeypatch):
    from wildfire import identity as identity_module

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(
        identity_module, "resolve_colors", lambda: {"success": "#40E888"}
    )
    result = RunResult("uh oh", role="error")
    assert _render(result) == "uh oh"


def test_render_banner_styles_tagline_and_headers(monkeypatch):
    from wildfire import identity as identity_module

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(
        identity_module, "resolve_colors", lambda: {"accent": "#F8D860"}
    )
    monkeypatch.setattr(identity_module, "resolve_accent", lambda: "#D66666")
    text = "wildfire — tagline\n\nHEADER\n  --flag <x>   does a thing\n"
    rendered = _render(RunResult(text, role="banner"))
    lines = rendered.splitlines()
    assert lines[0] == "\x1b[1m\x1b[38;2;214;102;102mwildfire — tagline\x1b[0m"
    assert lines[2] == "\x1b[1m\x1b[38;2;248;216;96mHEADER\x1b[0m"
    assert lines[3] == "  --flag <x>   does a thing"  # untouched


def test_render_banner_falls_back_to_shared_accent_when_no_wildfire_accent(monkeypatch):
    from wildfire import identity as identity_module

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(
        identity_module, "resolve_colors", lambda: {"accent": "#F8D860"}
    )
    monkeypatch.setattr(identity_module, "resolve_accent", lambda: None)
    rendered = _render(RunResult("wildfire tagline\n", role="banner"))
    assert rendered.startswith("\x1b[1m\x1b[38;2;248;216;96m")


def test_render_banner_plain_when_no_identity_file(monkeypatch):
    from wildfire import identity as identity_module

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr(identity_module, "resolve_colors", lambda: None)
    text = "wildfire — tagline\n\nHEADER\n  --flag <x>   does a thing\n"
    assert _render(RunResult(text, role="banner")) == text


def test_main_stdin_mode_reads_and_prints_one_line(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        Config, "load", staticmethod(lambda: Config(wildfire_dir=tmp_path / "Wildfire"))
    )
    monkeypatch.setattr(sys, "argv", ["wildfire", "-"])
    monkeypatch.setattr(sys, "stdin", io.StringIO("a wisp via stdin\n"))
    main()
    assert "a wisp via stdin" in capsys.readouterr().out


def test_main_normal_args_quick_add(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(
        Config, "load", staticmethod(lambda: Config(wildfire_dir=tmp_path / "Wildfire"))
    )
    monkeypatch.setattr(sys, "argv", ["wildfire", "a", "normal", "wisp"])
    main()
    assert "a normal wisp" in capsys.readouterr().out
