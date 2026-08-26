import sys

from wildfire.handlers import RunResult, run


def test_run_with_no_args_returns_prompt(corpus):
    result = run([], corpus)
    assert result.text == "No thoughts at all?"


def test_run_with_text_appends_and_confirms(corpus):
    result = run(["testing", "the", "cli"], corpus)
    assert "testing the cli" in result.text
    assert len(corpus.today().entries) == 1


def test_run_with_blank_text_returns_message(corpus):
    result = run([""], corpus)
    assert "blank" in result.text.lower()
    assert len(corpus.today().entries) == 0


def test_run_note_creates_spark(corpus):
    result = run(["--note", "Type", "Design", "Notes"], corpus)
    assert "created" in result.text.lower()
    assert corpus.get_note("Type Design Notes").exists


def test_run_note_on_existing_spark(corpus):
    corpus.create_note("fonts")
    result = run(["--note", "fonts"], corpus)
    assert "already exists" in result.text.lower()


def test_run_search_with_query(corpus):
    corpus.append_entry("Dreaming about Hendrik Van den Keere")
    result = run(["--search", "Van den Keere"], corpus)
    assert "van den keere" in result.text.lower()


def test_run_backlinks_for_name(corpus):
    corpus.append_entry("Dreaming up a new [[typeface]]")
    result = run(["--backlinks", "typeface"], corpus)
    assert "typeface" in result.text.lower()


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
    assert "Mono" in result.text


def test_run_stdin_mode_strips_trailing_newline(monkeypatch):
    import io

    monkeypatch.setattr("sys.stdin", io.StringIO("no trailing content issues\n"))
    text = sys.stdin.readline().strip()
    assert not text.endswith("\n")


# *~~ parsing tests ~~*


def test_run_catch_latest(corpus):
    corpus.append_entry("Reading up on Database Internal")
    result = run(["--catch-latest", "Database Internals"], corpus)
    assert "Database" in result.text or "database" in result.text.lower()
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
    assert "--as" in result.text


def test_run_catch_no_matches(corpus):
    result = run(["--catch", "nonexistent", "--as", "Fancy title"], corpus)
    assert "no wisp found" in result.text.lower()


# ~~ test --delete ~~


def test_run_delete_shows_backlinks_without_confirm(corpus):
    corpus.create_note("Old Spark")
    corpus.append_entry("Remember to check [[Old Spark]] later")
    result = run(["--delete", "Old Spark"], corpus)
    assert "check" in result.text.lower()
    assert "--confirm" in result.text
    assert corpus.get_note("Old Spark").exists


def test_run_delete_with_confirm_removes_spark(corpus):
    corpus.create_note("Old Spark")
    result = run(["--delete", "Old Spark", "--confirm"], corpus)
    assert "deleted" in result.text.lower()
    assert not corpus.get_note("Old Spark").exists


def test_run_delete_on_ghost_name(corpus):
    result = run(["--delete", "Nonexistent"], corpus)
    assert "nothing there." in result.text.lower()


def test_run_delete_with_no_backlinks(corpus):
    corpus.create_note("Orphan Spark")
    result = run(["--delete", "Orphan Spark"], corpus)
    assert "no backlinks" in result.text.lower()
    assert corpus.get_note("Orphan Spark").exists


# ~~ --show tests ~~


def test_run_show_on_ghost_name(corpus):
    result = run(["--show", "nonexistent spark"], corpus)
    assert "nonexistent spark" in result.text.lower()
    assert "--open" in result.text


def test_run_show_prints_note_content(corpus):
    corpus.create_note("Real Spark")
    result = run(["--show", "Real Spark"], corpus)
    assert "Real Spark" in result.text


def test_run_show_with_no_name_returns_usage(corpus):
    result = run(["--show"], corpus)
    assert "Try:" in result.text
    assert "--show" in result.text


# ~~ --open tests ~~


def test_run_open_creates_and_repoerts_closed(monkeypatch, corpus):
    def fake_run(*args, **kwargs):
        return None

    monkeypatch.setattr("subprocess.run", fake_run)
    result = run(["--open", "Freshly Sparked"], corpus)
    assert corpus.get_note("Freshly Sparked").exists
    assert "Closed: freshly sparked" in result.text


def test_run_open_missing_editor_binary(monkeypatch, corpus):
    def fake_run(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr("subprocess.run", fake_run)
    result = run(["--open", "Some Spark"], corpus)
    assert "Couldn't launch editor" in result.text


# ~~ --list tests ~~


def test_run_list_shows_both_sections(corpus):
    corpus.append_entry("test wisp")
    corpus.create_note("test spark")
    result = run(["--list"], corpus)
    assert "test wisp" in result.text
    assert "test spark" in result.text


def test_run_list_wisps_only_excludes_sparks(corpus):
    corpus.append_entry("test wisp")
    corpus.create_note("Test spark")
    result = run(["--list-wisps"], corpus)
    assert "test wisp" in result.text
    assert "sparks:" not in result.text.lower()


def test_run_list_sparks_only_excludes_wisps(corpus):
    corpus.append_entry("test wisp")
    corpus.create_note("Test Spark")
    result = run(["--list-sparks"], corpus)
    assert "test spark" in result.text
    assert "wisps:" not in result.text.lower()


def test_run_list_on_empty_corpus_shows_both_empty_messages(corpus):
    result = run(["--list"], corpus)
    assert "no wisps created yet" in result.text.lower()
    assert "no sparks created yet" in result.text.lower()


# ~~ test fuzzy_backlinks ~~


def test_run_backlinks_fuzzy_catches_typo(corpus):
    corpus.append_entry("Thinking about [[type deisgn]] today")
    exact = run(["--backlinks", "type design"], corpus)
    fuzzy = run(["--backlinks", "type design", "--fuzzy"], corpus)
    assert "no links" in exact.text.lower()
    assert "type deisgn" in fuzzy.text.lower()


def test_run_backlinks_fuzzy_no_match(corpus):
    result = run(["--backlinks", "nonexistent topic", "--fuzzy"], corpus)
    assert "no matches found." in result.text.lower()


# ~~ RunResult.role -- the point of the handlers/coloring split ~~


def test_run_returns_runresult_and_str_still_works(corpus):
    # print(run(...)) and f"{run(...)}" must keep working unchanged
    result = run(["--list"], corpus)
    assert isinstance(result, RunResult)
    assert str(result) == result.text


def test_delete_role_is_error_when_missing(corpus):
    assert run(["--delete", "Nonexistent"], corpus).role == "error"


def test_delete_role_is_warning_when_unconfirmed(corpus):
    corpus.create_note("Old Spark")
    assert run(["--delete", "Old Spark"], corpus).role == "warning"


def test_delete_role_is_success_when_confirmed(corpus):
    corpus.create_note("Old Spark")
    result = run(["--delete", "Old Spark", "--confirm"], corpus)
    assert result.role == "success"


def test_quick_add_role_is_success(corpus):
    assert run(["a new wisp"], corpus).role == "success"


def test_quick_add_role_is_error_when_blank(corpus):
    assert run([""], corpus).role == "error"


def test_note_created_role_is_success(corpus):
    assert run(["--note", "Fresh Spark"], corpus).role == "success"


def test_note_already_exists_role_is_none(corpus):
    corpus.create_note("Existing Spark")
    assert run(["--note", "Existing Spark"], corpus).role is None


def test_list_role_is_none(corpus):
    assert run(["--list"], corpus).role is None


def test_no_args_role_is_none(corpus):
    assert run([], corpus).role is None


def test_help_role_is_banner(corpus):
    assert run(["--help"], corpus).role == "banner"
    assert run(["-h"], corpus).role == "banner"
