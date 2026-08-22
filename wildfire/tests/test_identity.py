from pathlib import Path
from wildfire import identity


def test_resolve_colors_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(identity, "IDENTITY_FILE", tmp_path / "nope.yml")
    assert identity.resolve_colors() is None


def test_resolve_colors_reads_semantic_block(monkeypatch, tmp_path):
    f = tmp_path / "identity.yml"
    f.write_text("semantic:\n  error: '#E89292'\ntools:\n  wildfire: '#D66666'\n")
    monkeypatch.setattr(identity, "IDENTITY_FILE", f)
    assert identity.resolve_colors() == {"error": "#E89292"}


def test_no_color_env_short_circuits(monkeypatch, tmp_path):
    f = tmp_path / "identity.yml"
    f.write_text("semantic:\n  error: '#E89292'\n")
    monkeypatch.setattr(identity, "IDENTITY_FILE", f)
    monkeypatch.setenv("NO_COLOR", "1")
    assert identity.resolve_colors() is None


def test_resolve_colors_malformed_yaml(monkeypatch, tmp_path):
    f = tmp_path / "identity.yml"
    f.write_text("semantic: [1, 2")  # unclosed flow sequence -> yaml.YAMLError
    monkeypatch.setattr(identity, "IDENTITY_FILE", f)
    assert identity.resolve_colors() is None


def test_resolve_colors_missing_semantic_key(monkeypatch, tmp_path):
    f = tmp_path / "identity.yml"
    f.write_text("tools:\n  wildfire: '#D66666'\n")  # valid YAML, no "semantic" key
    monkeypatch.setattr(identity, "IDENTITY_FILE", f)
    assert identity.resolve_colors() is None


def test_resolve_accent_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(identity, "IDENTITY_FILE", tmp_path / "nope.yml")
    assert identity.resolve_accent() is None


def test_resolve_accent_reads_tools_block(monkeypatch, tmp_path):
    f = tmp_path / "identity.yml"
    f.write_text("semantic:\n  error: '#E89292'\ntools:\n  wildfire: '#D66666'\n")
    monkeypatch.setattr(identity, "IDENTITY_FILE", f)
    assert identity.resolve_accent() == "#D66666"


def test_resolve_accent_no_color_env(monkeypatch, tmp_path):
    f = tmp_path / "identity.yml"
    f.write_text("tools:\n  wildfire: '#D66666'\n")
    monkeypatch.setattr(identity, "IDENTITY_FILE", f)
    monkeypatch.setenv("NO_COLOR", "1")
    assert identity.resolve_accent() is None


def test_resolve_accent_unknown_tool(monkeypatch, tmp_path):
    f = tmp_path / "identity.yml"
    f.write_text("semantic:\n  error: '#E89292'\ntools:\n  wildfire: '#D66666'\n")
    monkeypatch.setattr(identity, "IDENTITY_FILE", f)
    assert identity.resolve_accent("flint") is None

def test_identity_file_default_path():
    assert identity.IDENTITY_FILE == (
            Path.home() / ".ember-hearth" / "identity" / "identity.yml"
    )
