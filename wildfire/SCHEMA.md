# wildfire • schema

The on-disk format for `~/Wildfire/`. This document states what a valid file looks like.

**Schema version** 0.1 

---
## Directory structure

```bash
~/Wildfire/             ← wildfire_dir (configurable)
├── wisps/
│   └── 2026-07-17.md
└── sparks/
    └── fonts.md
```

---
## Wisps - `wisps/YYYY-mm-dd.md`

One line per wisp:
`- HH:MM <text>`
- `-` followed by `HH:MM` marks a wisp line
- Wisps are append-only. Wildfire never rewrites a saved line by default.

---
## Sparks - `sparks/<name.md>`

Plain markdown files. For now: No enforced structure beyond the filename itself.

- Filename is a slugified title, example: `Type Design Notes` -> `type-design-notes.md`
- A spark referenced by a link that has no file yet is valid, unresolved spark.

## Tags - `@word`

- Matches `@` followed by letters, digits, `-`, or `_`. Stops at whitespace.
- Single token only: `@type-designer` works, `@type designer` does not.
- Wisps only. Sparks don't currently carry `@tags` but will do in the future.

## Links - [[phrase]]

- Matches everything between `[[` and the next `]]`.
- In contrast with `@tags`, links can contain spaces. Example: `[[This is a valid link.]]`
- No nesting: `[[this is [[NOT]] valid.]]` but might be implemented in the future.
- Fuzzy search will be introduced later.
- Valid in both *wisps* and *sparks*.


