import pytest
from wildfire.config import Config
from wildfire.corpus import Corpus


@pytest.fixture
def corpus(tmp_path):
    cfg = Config(wildfire_dir=tmp_path / "Wildfire")
    return Corpus(cfg)


def test_append_entry_writes_and_returns(corpus):
    entry = corpus.append_entry("fix the parser @dev")
    assert entry.contexts == ["dev"]
    assert len(corpus.today().entries) == 1


def test_create_and_get_note(corpus):
    note = corpus.create_note("Type Design Notes")
    assert note.exists
    fetched = corpus.get_note("Type Design Notes")
    assert fetched.path == note.path


def test_get_note_on_nonexistent_is_a_ghost(corpus):
    ghost = corpus.get_note("nonexistent spark :(")
    assert ghost.exists is False


def test_list_notes_returns_all(corpus):
    corpus.create_note("fonts")
    corpus.create_note("type design")
    assert len(corpus.list_notes()) == 2


def test_note_links_reflect_real_content(corpus):
    note = corpus.create_note("fonts")
    note.write("relates to [[type design]]")
    assert corpus.get_note("fonts").links == ["type design"]


# ~~ Backlink tests ~~


def test_backlinks_finds_matching_entry(corpus):
    corpus.append_entry("Dreaming about [[fonts]] again.")
    result = corpus.backlinks("fonts")
    assert len(result.entries) == 1
    assert result.notes == []


def test_backlinks_finds_matching_note(corpus):
    corpus.create_note("fonts")
    note = corpus.create_note("type design")
    note.write("relates to [[fonts]]")
    result = corpus.backlinks("fonts")
    assert len(result.notes) == 1
    assert result.notes[0].name == "type-design"
    assert result.notes[0].title == "type design"


def test_backlinks_to_nonexistent_target_returns_empty(corpus):
    result = corpus.backlinks("Sadly, nothing links here...")
    assert result.entries == []
    assert result.notes == []


def test_backlinks_ordering_is_oldest_first(corpus):
    corpus.append_entry("First mention of the word [[fonts]]")
    corpus.append_entry("Second mention of the word [[fonts]]")
    result = corpus.backlinks("fonts")
    assert result.entries[0].text == "First mention of the word [[fonts]]"
    assert result.entries[1].text == "Second mention of the word [[fonts]]"


# ~~ Search tests ~~


def test_search_finds_matching_entry(corpus):
    corpus.append_entry("Thinking about lowercase letters again...")
    result = corpus.search("lowercase letters")
    assert len(result.entries) == 1
    assert result.notes == []


def test_search_is_case_insensitive(corpus):
    corpus.append_entry("Drawing uppercase letters again...")
    result = corpus.search("UPPERCASE")
    assert len(result.entries) == 1


def test_search_finds_matching_note_content(corpus):
    corpus.create_note("fonts")
    spark = corpus.get_note("fonts")
    spark.write("Garamond's punches can be studied at the Plantin-Moretus Museum")
    result = corpus.search("garamond")
    assert len(result.notes) == 1
    assert result.notes[0].name == "fonts"


def test_search_no_match_returns_empty(corpus):
    result = corpus.search("Nothing will match this!")
    assert result.entries == []
    assert result.notes == []
