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
