from pathlib import Path
from wildfire.models import Note


def test_title_converts_dashes_and_underscores():
    spark = Note(name="type-design_notes", path=Path("roland-serif"), links=[])
    assert spark.title == "type design notes"


def test_from_path_on_missing_file(tmp_path):
    # tmp_path is a pytest fixture: a real, empty, throwaway directory that's deleted automatically after the test. Ask for it as a paramter and pytest hands it to you, this is why the file argument is here.
    missing_path = tmp_path / "no-file.md"
    spark = Note.from_path(missing_path)
    assert spark.exists is False
    assert spark.links == []


def test_from_path_extracts_links(tmp_path):
    real_file = tmp_path / "test.md"
    real_file.write_text("relates to [[fonts]] and [[type systems]]")
    spark = Note.from_path(real_file)
    assert spark.links == ["fonts", "type systems"]


def test_write_refresh_links(tmp_path):
    real_file = tmp_path / "test.md"
    real_file.write_text(
        "[[Nicolas Cage]] created a highly legible Roman typeface in [[1480]]."
    )
    spark = Note.from_path(real_file)
    spark.write("[[Nicolas Jenson]] created a legible Roman typeface in [[1470]].")
    assert spark.links == ["Nicolas Jenson", "1470"]
    # Build or load a Note, call .write() with new content containing a different [[link]] than it started with, then check that note.links reflect the NEW content, not the old.
