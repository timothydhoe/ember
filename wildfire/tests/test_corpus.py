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
