"""
wildfire.tui
~~~~~~~~~~~~
Interactive session shell: overview, drill in, act — three views, one screen.

This is a placeholder shell. All data below is fake, generated in-process;
nothing here touches Corpus yet. The point is to get the feel of the thing
right — layout, keybindings, theming — before wiring it to real wisps and
sparks. See `_fake_rows()` for the one function that'll get swapped out.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import ClassVar

from rich.text import Text
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.theme import Theme
from textual.widgets import Footer, Input, Markdown, OptionList, Static
from textual.widgets.option_list import Option

from . import identity
from .models import Entry, Note

# Presentation-only, scoped to this file: whether a wisp's full text is a
# bare URL, so it can be colored like a link in the nav list. Real corpus-
# level URL capture/follow (--urls) is a separate, not-yet-built feature —
# this just anticipates it visually.
_URL = re.compile(r"^https?://\S+$")


class VimOptionList(OptionList):
    """OptionList with vim-style navigation layered on top of the defaults.

    Arrow keys, home/end, and enter still work — this only adds j/k/g/G.
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("g", "first", "First", show=False),
        Binding("shift+g", "last", "Last", show=False),
    ]


@dataclass
class Row:
    """One line in the nav list: either a group header or a real item."""

    option_id: str
    prompt: str
    kind: str  # "header" | "wisp" | "spark"
    payload: Entry | Note | None = None


def _fake_rows() -> list[Row]:
    """Placeholder corpus snapshot — swap this for real Corpus data later.

    Everything downstream (grouping, rendering, act) is written against
    Row/Entry/Note, so wiring the real thing in should mean replacing this
    one function, not touching the app.
    """
    today = date.today()

    wisps_today = [
        Entry(time="09:14", text="check the [[wildfire tui]] feel today", date=today),
        Entry(time="11:02", text="rust ownership finally clicked", date=today),
        Entry(time="14:29", text="https://mitchellh.com/writing", date=today),
    ]
    wisps_week = [
        Entry(
            time="16:40",
            text="wildfire's accent should stay [[blaze]], not alight's default",
            date=today - timedelta(days=2),
        ),
    ]
    wisps_older = [
        Entry(time="08:05", text="ghost link test: [[future spark]]", date=today - timedelta(days=19)),
    ]
    sparks = [
        Note(name="rust-ownership", path=Path("rust-ownership.md"), links=["future spark"]),
        Note(name="wildfire-tui", path=Path("wildfire-tui.md"), links=["blaze"]),
    ]

    rows: list[Row] = []

    def add_group(label: str, key: str, entries: list[Entry]) -> None:
        rows.append(Row(f"header:{key}", label, "header"))
        for i, entry in enumerate(entries):
            rows.append(Row(f"wisp:{key}:{i}", f" ∘ {entry.time}  {entry.text}", "wisp", entry))

    add_group("TODAY", "today", wisps_today)
    add_group("THIS WEEK", "week", wisps_week)
    add_group("OLDER", "older", wisps_older)

    rows.append(Row("header:sparks", "SPARKS", "header"))
    for i, note in enumerate(sparks):
        rows.append(Row(f"spark:{i}", f" ✦ {note.title}", "spark", note))

    return rows


def _detail_markdown(row: Row | None) -> str:
    if row is None or row.payload is None:
        return "*Nothing selected.*"
    if isinstance(row.payload, Entry):
        entry = row.payload
        lines = [f"**wisp** — {entry.date.isoformat()} {entry.time}", "", entry.text]
        if entry.links:
            lines += ["", f"links: {', '.join(entry.links)}"]
        if entry.contexts:
            lines += ["", f"tags: {', '.join('@' + c for c in entry.contexts)}"]
        return "\n".join(lines)
    note = row.payload
    return f"# {note.title}\n\n*(fake data — real content comes from `{note.path.name}` once wired)*"


class WildfireApp(App):
    """Overview, drill in, act — the interactive wildfire shell.

    Placeholder data throughout (see `_fake_rows`). Scope is wildfire's own
    wisps and sparks, not general file/folder browsing — that's flint's job.
    """

    TITLE = "wildfire"

    CSS = """
    #wordmark {
        color: $primary;
        text-style: bold;
        padding: 1 2 0 2;
    }

    #tagline {
        color: $text-muted;
        text-style: italic;
        padding: 0 2 1 2;
    }

    #nav-pane {
        width: 40%;
        border: round $primary;
        padding: 0 1;
    }

    #search {
        display: none;
    }

    /* nav-pane (the Vertical wrapper) carries the border and title;
       the OptionList itself stays borderless so there's only one box,
       not a nested double border. */
    #nav {
        height: 1fr;
        border: none;
        background: transparent;
        padding: 0;
    }

    #nav > .option-list--option-highlighted {
        background: transparent;
        color: $primary;
        text-style: bold;
    }

    #nav:focus > .option-list--option-highlighted {
        background: transparent;
        color: $primary;
        text-style: bold;
    }

    /* Detail pane deliberately has no border — a filled, recessed surface
       instead, so focused-vs-passive reads as shape (bordered list vs
       borderless preview), not color alone. */
    #detail {
        width: 1fr;
        padding: 1 2;
        background: $surface;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("o", "act('open')", "Open"),
        Binding("u", "act('urls')", "URLs"),
        Binding("b", "act('backlinks')", "Backlinks"),
        Binding("c", "act('catch')", "Catch"),
        Binding("slash", "focus_search", "Search", key_display="/"),
        Binding("escape", "clear_search", "Clear search", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._all_rows: list[Row] = _fake_rows()
        self._current_rows: list[Row] = []
        # Resolved once in on_mount; None means "no identity file, stay plain"
        self._link_hex: str | None = None
        self._accent_hex: str | None = None

    def compose(self) -> ComposeResult:
        yield Static("wildfire", id="wordmark")
        yield Static("turn a fleeting thought into a spark worth keeping", id="tagline")
        with Horizontal():
            with Vertical(id="nav-pane"):
                yield Input(placeholder="/ to filter", id="search")
                yield VimOptionList(id="nav")
            yield Markdown(id="detail")
        yield Footer()

    def on_mount(self) -> None:
        # Pulls wildfire's accent + alight's semantic roles at runtime, same
        # source the CLI's own banner/role rendering already reads from.
        # alight stays the one place a color is ever defined; if it's
        # missing (no identity file, NO_COLOR set), Textual's own default
        # theme is used instead — same graceful-degradation contract as
        # cli.py's _render(). This has to happen in on_mount, not
        # get_css_variables: that's called mid-way through App.__init__,
        # before the app's own reactive/CSS bookkeeping exists yet, and
        # setting self.theme that early crashes on the first watcher it
        # triggers.
        accent = identity.resolve_accent("wildfire")
        colors = identity.resolve_colors()
        if accent and colors:
            self.register_theme(
                Theme(
                    name="wildfire",
                    primary=accent,
                    accent=colors.get("accent", accent),
                    warning=colors.get("warning", accent),
                    error=colors.get("error", accent),
                    success=colors.get("success", accent),
                    dark=True,
                )
            )
            self.theme = "wildfire"
            self._link_hex = colors.get("link")
            self._accent_hex = colors.get("accent", accent)
        self.query_one("#search", Input).display = False
        self._render_options(self._all_rows)
        self.query_one("#nav", VimOptionList).focus()

    def _build_visual(self, row: Row, query: str = "") -> str | Text:
        """Turn a Row into what OptionList actually displays.

        Deliberately builds a plain rich.Text and applies color/bold via
        .stylize(start, end) rather than embedding markup tags in an
        f-string. Wisp/spark text can contain literal [[wikilinks]], and
        Rich's markup parser treats stray square brackets as tag syntax —
        an f-string like f"[{color}]{row.prompt}[/]" will silently mangle
        or, worse, hard-crash the whole app the moment a highlighted
        match sits directly next to a literal bracket. stylize() never
        parses the string at all, so this is the only safe way to color
        untrusted/corpus-derived text here.
        """
        if row.kind == "header":
            return row.prompt

        text = Text(row.prompt)

        is_bare_url = isinstance(row.payload, Entry) and bool(_URL.fullmatch(row.payload.text.strip()))
        if is_bare_url and self._link_hex:
            text.stylize(self._link_hex, 0, len(text))

        if query:
            match = re.search(re.escape(query), row.prompt, re.IGNORECASE)
            if match:
                accent = self._accent_hex or "bold"
                text.stylize(f"bold {accent}", match.start(), match.end())

        if row.payload and row.payload.links:
            # Leading, not trailing — lazygit/gitui put their per-row status
            # glyph at the start of the line for a reason: a long wisp can
            # wrap in a narrow pane, and a trailing marker wraps with it,
            # landing on a disconnected second line instead of staying
            # scannable at a glance.
            #
            # The style has to be set as an explicit span on the marker
            # (via stylize), not as the marker Text's base `style=`. Text.__add__
            # carries the LEFT operand's base style onto the *entire* combined
            # Text with no span to bound it — concatenating a style="X" marker
            # with plain body text colors the whole row X, not just the marker.
            # Confirmed by direct inspection of the resulting Text's .spans
            # before shipping this.
            marker = Text("→ ")
            marker.stylize(self._link_hex or "dim", 0, len(marker))
            text = marker + text

        return text

    def _render_options(self, rows: list[Row], query: str = "") -> None:
        # Deliberately doesn't touch focus — this runs mid-keystroke while
        # filtering, and grabbing focus here would yank it off the search
        # box after the first character typed.
        nav = self.query_one("#nav", VimOptionList)
        nav.clear_options()
        for row in rows:
            nav.add_option(
                Option(self._build_visual(row, query), id=row.option_id, disabled=(row.kind == "header"))
            )
        self._current_rows = rows

        sparks = sum(1 for r in self._all_rows if r.kind == "spark")
        wisps = len(self._all_rows) - sparks - sum(1 for r in self._all_rows if r.kind == "header")
        self.query_one("#nav-pane", Vertical).border_title = f"wildfire · {wisps} wisps · {sparks} sparks"

    def _row_for(self, option_id: str | None) -> Row | None:
        if option_id is None:
            return None
        return next((r for r in self._current_rows if r.option_id == option_id), None)

    @on(OptionList.OptionHighlighted, "#nav")
    def _on_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        detail = self.query_one("#detail", Markdown)
        detail.update(_detail_markdown(self._row_for(event.option_id)))

    def action_focus_search(self) -> None:
        search = self.query_one("#search", Input)
        search.display = True
        search.focus()

    def action_clear_search(self) -> None:
        search = self.query_one("#search", Input)
        if search.display:
            search.value = ""
            search.display = False
            self._render_options(self._all_rows)
            self.query_one("#nav", VimOptionList).focus()

    @on(Input.Changed, "#search")
    def _on_filter_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        if not query:
            self._render_options(self._all_rows)
            return
        matches = [r for r in self._all_rows if r.kind != "header" and query.lower() in r.prompt.lower()]
        self._render_options(matches, query)

    @on(Input.Submitted, "#search")
    def _on_filter_submitted(self, event: Input.Submitted) -> None:
        search = self.query_one("#search", Input)
        search.display = False
        self.query_one("#nav", VimOptionList).focus()

    def action_act(self, verb: str) -> None:
        nav = self.query_one("#nav", VimOptionList)
        highlighted = nav.highlighted_option
        row = self._row_for(highlighted.id if highlighted else None)
        if row is None or row.kind == "header":
            self.notify("Nothing selected.", severity="warning")
            return
        # Placeholder — real wiring calls the matching Corpus method instead.
        self.notify(f"would {verb}: {row.prompt.strip()}", title=verb)


def run() -> None:
    WildfireApp().run()


if __name__ == "__main__":
    run()