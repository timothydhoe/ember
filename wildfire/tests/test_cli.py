import pytest
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
    assert "Created" in result
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
