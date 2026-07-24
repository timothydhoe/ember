import pytest
import sys
from wildfire.cli import run
from wildfire.config import Config
from wildfire.corpus import Corpus


@pytest.fixture
def corpus(tmp_path):
    cfg = Config(wildfire_dir=tmp_path / "Wildfire")
    return Corpus(cfg)


def test_run_with_no_args_returns_prompt(corpus):
    result = run([], corpus)
    assert result == "No thoughts at all?"


def test_run_with_text_appends_and_confirms(corpus):
    result = run(["testing", "the", "cli"], corpus)
    assert "testing the cli" in result
    assert len(corpus.today().entries) == 1


def test_run_with_blank_text_returns_message(corpus):
    result = run([""], corpus)
    assert "blank" in result.lower()
    assert len(corpus.today().entries) == 0


def test_run_note_creates_spark(corpus):
    result = run(["--note", "Type", "Design", "Notes"], corpus)
    assert "created" in result.lower()
    assert corpus.get_note("Type Design Notes").exists


def test_run_note_on_existing_spark(corpus):
    corpus.create_note("fonts")
    result = run(["--note", "fonts"], corpus)
    assert "already exists" in result.lower()


def test_run_search_with_query(corpus):
    corpus.append_entry("Dreaming about Hendrik Van den Keere")
    result = run(["--search", "Van den Keere"], corpus)
    assert "van den keere" in result.lower()


def test_run_backlinks_for_name(corpus):
    corpus.append_entry("Dreaming up a new [[typeface]]")
    result = run(["--backlinks", "typeface"], corpus)
    assert "typeface" in result.lower()


def test_run_plain_text_starting_with_flag_word_is_not_a_command(corpus):
    result = run(["search", "this", "is", "just", "a", "wisp"], corpus)
    assert len(corpus.today().entries) == 1
    assert corpus.today().entries[0].text == "search this is just a wisp"


# ~~ stdin tests ~~


def test_run_stdin_mode_reads_one_line(monkeypatch, corpus):
    import io

    monkeypatch.setattr(
        "sys.stdin", io.StringIO("I prefer to use JetBrains [[Mono]] in the terminal\n")
    )
    text = sys.stdin.readline().strip()
    result = run([text], corpus)
    assert "Mono" in result


def test_run_stdin_mode_strips_trailing_newline(monkeypatch):
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("no trailing content issues\n"))
    text = sys.stdin.readline().strip()
    assert not text.endswith("\n")


# *~~ parsing tests ~~*


def test_run_catch_latest(corpus):
    corpus.append_entry("Reading up on Database Internal")
    result = run(["--catch-latest", "Database Internals"], corpus)
    assert "Database" in result or "database" in result.lower()
    assert corpus.get_note("Database Internals").exists


def test_run_catch_with_search(corpus):
    corpus.append_entry("Storage Engines")
    corpus.append_entry(
        "Distributed database systems are an integral part of most businesses."
    )
    result = run(["--catch", "businesses", "--as", "Database Internals"], corpus)
    assert corpus.get_note("Database Internals").exists


def test_run_catch_missing_as_returns_usage_message(corpus):
    result = run(["--catch", "database internals", "database notes"], corpus)
    assert "--as" in result


def test_run_catch_no_matches(corpus):
    result = run(["--catch", "nonexistent", "--as", "Fancy title"], corpus)
    assert "no wisp found" in result.lower()
