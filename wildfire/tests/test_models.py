from datetime import date
from pathlib import Path
from wildfire.models import DailyLog, Entry, Note

# ---
# DailyLog test


def test_daily_log_loads_entries(tmp_path):
    log_path = tmp_path / "2026-07-20.md"
    log_path.write_text(
        "# Monday, 20th July\n"
        "- 08:32 fix the serif on \\n and \\h @type-design\n"
        "- 09:01 study Ascendonica punches from [[Van den Keere]].\n"
    )
    log = DailyLog.from_path(log_path)

    assert log.date == date(2026, 7, 20)
    assert len(log.entries) == 2
    assert log.entries[0].contexts == ["type-design"]
    assert log.entries[1].links == ["Van den Keere"]


def test_daily_log_skips_blank_lines(tmp_path):
    log_path = tmp_path / "2026-07-20.md"
    log_path.write_text("- 08:32 first wisp\n\n- 09:01 second wisp\n")
    log = DailyLog.from_path(log_path)

    assert len(log.entries) == 2


def test_daily_log_empty_file_has_no_entries(tmp_path):
    log_path = tmp_path / "2026-07-20.md"
    log_path.write_text("")
    log = DailyLog.from_path(log_path)

    assert log.entries == []


# ---
# Entry tests


def test_entry_extracts_context_tags_only():
    wisp = Entry(
        time="08:40",
        text="Claude Garamont was a French @type-designer, @publisher and @punchcutter based in Paris.",
        date=date.today(),
    )
    assert wisp.contexts == ["type-designer", "publisher", "punchcutter"]
    assert wisp.links == []


def test_entry_extracts_links_only():
    wisp = Entry(
        time="08:59",
        text="Garamont worked as an engraver of [[punches]], and the masters used to stamp [[matrices]].",
        date=date.today(),
    )
    assert wisp.contexts == []
    assert wisp.links == ["punches", "matrices"]


def test_entry_with_no_tags_or_links():
    wisp = Entry(
        time="09:01",
        text="Garamont was one of the first independent punchcutters specialising in type design and punchcutting as a service.",
        date=date.today(),
    )
    assert wisp.contexts == []
    assert wisp.links == []


def test_entry_link_ignores_word_boundaries():
    wisp = Entry(
        time="09:04",
        text="His career helped to define the future of commercial [[print]]ing with [[type]]founding as a distinct industry to printing books.",
        date=date.today(),
    )
    assert wisp.contexts == []
    assert wisp.links == ["print", "type"]


# ---
# Note tests


def test_title_converts_dashes_and_underscores():
    spark = Note(name="type-design_notes", path=Path("roland-serif"), links=[])
    assert spark.title == "type design notes"


def test_from_path_on_missing_file(tmp_path):
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
