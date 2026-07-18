# Wildfire • Architecture

How wildfire is being build, and why. This document assumes you already know what the tool does. To get more familiar with the idea behind *wildfire* see [README.md](./README.md)

This document exists so a future contributor, or future-me more likely, doesn't have to pull their hair out reading my wonky codebase.

---
## The model

Capture an idea or thought quickly; a *wisp*. It it's worth keeping, turn it into a *spark*, a permanent and linkable note. Anything can reference a spark by writing `[[file name]]`.

Right now `[[links]] are only detected and looked up. There's no CLI to open or follow one yet. But it's on the todo list.

---
## Core constraints

Notes must be readable and editable without wildfire. That's why we're using plain markdown. Config and data live in separate folder for the same reason.

---
## Directory structure
```bash
~/Wildfire/                 ← wildfire_dir (configurable through ~/.wildfire)
├── wisps/
│   └── 2026-07-17.md       ← daily log of wisps
└── sparks/
    └── fonts.md            ← durable, linkable note
 ```

---
## Vocabulary: wisp and spark

wildfire's core is that ideas link. Ideas are *sparks* of the mind, and *wisps* can be caught.

| Concept | user-facing | code |
|---------|-------------|------|
| Quick, timestamped, disposable capture | wisp | `Entry` 
| Durable, linkable, curated idea | spark | `Note`

**The vocabulary stops at the disk/CLI/docs layer and doesn't reach into code.**
Readability over cleverness. Let's keep branding and engineering separate on this one.
It's not implemented yet.

`catch` is reserved as the verb for turning a wisp into a spark. Not implemented yet.

---
## Config

- `wildfire_dir/`: the root folder for *wisps* and *sparks*.
- Using `tomlkit` as it actually respects round-trip formatting so hand-edited comments survive a save..

Keeping our `toml` lean and clean:
```toml
config_version = 1
name           = ""
wildfire_dir   = "~/Wildfire"
editor         = ""
```

`wisps_dir = wildfire_dir/wisps` `sparks_dir = wildfire_dir/sparks`

---
## Linking

**Resolution: filename-first**: `[[best idea ever]]` runs through the  same `slugify` used for creating sparks, and look for a matching filename stem.

**The syntax: [[wikilinks]]**: I weighed (mentally, that is) regular Markdown links `[like this](spark.md)` and custom sigils like `@` or `+`. I believe that *sparks* usually will have multi-word titles, and forcing you to mentally slugify a phrase while you're mid-thought seems like an awful idea.

**Ghost linking**: [[future spark]] pointing nowhere is a placeholder *(credit goes to Foam)*. This gives `catch` another purpose, namely following a ghost link to create the spark it points to.

**eager parsing**: A spark's links are read the moment it's loaded. Same rule for `Entry` follows.


---
## Good ideas we're not building yet

- **Onboarding demo**: `wildfire --demo` or a first-run walkthrough. A nice idea and fun feature.

---
## Future-me problems

- **Regex Wizardry**: Still figuaring out the exact parsing mechanics.
- **backlinks:** full-corpus scan every call with no cache? vs an index?
- What does "following" a link actually do once there's a CLI? print the target? open in $EDITOR?
- what does `catch()` walk through for a ghost link?
