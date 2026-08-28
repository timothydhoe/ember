# Wildfire • Architecture

How wildfire is being built, and why. This document assumes you already know what the tool does. To get more familiar with the idea behind _wildfire_ see [README.md](./README.md)

This document exists so a future contributor, or future-me more likely, doesn't have to pull their hair out reading my wonky codebase.

---

## The model

Capture an idea or thought quickly; a _wisp_. If it's worth keeping, turn it into a _spark_, a permanent and linkable note. Anything can reference a spark by writing `[[file name]]`.

Right now, [[links]] are detected, resolved and are queryable via `--backlinks` (`fuzzy` for typo-tolerant matches).
`catch` turns a wisp into a spark. `--open` jumps straight to a spark by name, creating it first if it doesn't exist yet.

---

## Codemap

**`models.py`**
**The datatypes:** `Entry` (wisp), `Note` (spark), `DailyLog` (collection of day's wisps), and string-transform helpers: `slugify()` and `tokenize()`.

Each type knows how to parse and represent itself:

- `Entry` extracts its own tags/links from one line.
- `Note` reads its own file.

_Depends only on the standard library_

**`config.py`**
**Dataclass for configuration** found in `~/.ember-hearth/wildfire/config.toml`

Owns loading, saving (round-trip-safe), and resolving which editor to use.

**`corpus.py`**
**Point of access for `~/Wildfire/`**, no other code touches the filesystem directly.
Globbing directories, building filenames from config + `slugify()` all happens here.
The first file to import both the above and where `Config` and the models meet.

Executes every cross-file operation:

- reading all daily logs at once (`all_entries()`)
- matching across both wisps and sparks (`backlinks()`, `search()`)
- actual wisp-to-spark workflow (`catch()`)

Also defines four small result types: `Backlinks`, `SearchResults`, `CatchResult`, `LinkSuggestion`.

**`handlers.py`**
One `_handle_` per flag. `RunResult.role` tells `cli.py` what colour to use.

**`cli.py`**
**Entry point for the `wildfire` command.**
The only file touching `sys.argv`/`sys.stdin`/`print` directly.

---

## Core constraints

Notes must be readable and editable without wildfire. That's why we're using plain markdown. Config and data live in separate folder for the same reason.

Wisps are immutable anywhere in `Corpus` on purpose. Sparks are allowed to change and even be removed,but destruction always requires a second, explicit step (`--delete <name> --confirm`).

---

## Directory structure

```bash
~/Wildfire/                 ← wildfire_dir (configurable via ~/.ember-hearth/wildfire/config.toml)
├── wisps/
│   └── 2026-07-17.md       ← daily log of wisps
└── sparks/
    └── fonts.md            ← durable, linkable note
```

---

## Vocabulary: wisp and spark

wildfire's core is that ideas link. Ideas are _sparks_ of the mind, and _wisps_ can be caught.

| Concept                                | user-facing | code    |
| -------------------------------------- | ----------- | ------- |
| Quick, timestamped, disposable capture | wisp        | `Entry` |
| Durable, linkable, curated idea        | spark       | `Note`  |

**The vocabulary stops at the disk/CLI/docs layer and doesn't reach into code.**
Readability over cleverness. Let's keep branding and engineering separate on this one.

`catch` is the verb for turning a wisp/_Entry_ into a spark/_Note_ in the CLI:

- `--catch-latest <title>`
- `--catch <query> --as <title>`

Wisps stay immutable forever. Sparks can be deleted (`--delete <name>`) but only behind a two-step process. First call shows what backlinks would break, second is to run the same command with `--confirm` appended.

---

## Config

- `wildfire_dir/`: the root folder for wisps and sparks.
- Using `tomlkit` as it actually respects round-trip formatting so hand-edited comments survive a save..

Keeping our `toml` lean and clean:

```toml
config_version = 1
name           = ""
wildfire_dir   = "~/Wildfire"
editor         = ""
```

`entries_dir = wildfire_dir/wisps`
`notes_dir = wildfire_dir/sparks`

---

## Linking

**Resolution: filename-first**: `[[best idea ever]]` runs through the same `slugify` used for creating sparks, and look for a matching filename stem.

**The syntax: [[wikilinks]]**: I weighed (mentally, that is) regular Markdown links `[like this](spark.md)` and custom sigils like `@` or `+`. I believe that _sparks_ usually will have multi-word titles, and forcing you to mentally slugify a phrase while you're mid-thought seems like an awful idea.

**Backlinks**: full-corpus scan with no cache. `backlinks()` rescan every wisp/_Entry_ and spark/_Note_ on each call. Matches the "any index is a rebuildable cache, and never authoritative" principle.

**Fuzzy Backlinks**: `--backlinks --fuzzy` shows results that plain `--backlinks` misses.
Scored via `rapidfuzz`'s `fuzz.ratio`, with treshold gate and exact matches excluded.

**Ghost linking**: [[future spark]] pointing nowhere is a placeholder _(credit goes to Foam)_.
`catch` resolves a ghost link by turning a matching wisp into the spark it points to; `--open` resolves one more directly, creating the spark on the spot if it doesn't exist yet.

**eager parsing**: A spark's links are read the moment it's loaded. Same rule for `Entry` follows.

**CLI dispatch**: flag-based.

- Capture: quick-add without flag, stdin mode (`wildfire -`)
- Today: `--today` shows today's wisps only, in order
- Sparks: `--note`, `--show`, `--open`, `--delete [--confirm]`
- Catching: `--catch <query> --as <title>`, `--catch-latest`
- Finding: `--search`, `backlinks [--fuzzy]`, `--list` / `--list-wisps` / `--list-sparks`

---

## Good ideas we're not building yet

- **Onboarding demo**: `wildfire --demo` or a first-run walkthrough. A nice idea and fun feature.
