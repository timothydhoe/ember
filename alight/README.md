# Alight

[![ember tool](https://img.shields.io/static/v1?label=&message=ember%20tool&color=0B162D&style=flat-square)](https://github.com/timothydhoe/ember)

Alight is ember's source of truth for brand colours and its identity.
`schemes/alight.yml` generates a colour scheme for six terminal apps. Everything else in this repo is disposable output regenerated from that source file.

## ember palette

![ember palette](/exports/palette-swatch.svg)

---

# Installing

```bash
git clone https://github.com/timothydhoe/ember
cd ember/alight
uv sync
```

The terminal files this produces are already commited, so you don't need to run anything to use them. **Just pick your app:**

| App          | Setup                                                                |
| ------------ | -------------------------------------------------------------------- |
| Ghostty      | [`terminal/ghostty/README.md`](terminal/ghostty/README.md)           |
| iTerm2       | [`terminal/iterm2/README.md`](terminal/iterm2/README.md)             |
| Alacritty    | [`terminal/alacritty/README.md`](terminal/alacritty/README.md)       |
| Terminal.app | [`terminal/terminal-app/README.md`](terminal/terminal-app/README.md) |
| tmux         | [`terminal/tmux/README.md`](terminal/tmux/README.md)                 |
| Vim          | [`terminal/vim/README.md`](terminal/vim/README.md)                   |
| Neovim       | [`terminal/nvim/README.md`](terminal/nvim/README.md)                 |

Point your app's config at the file that's already sitting in this repo.

## If you're changing the palette instead

```bash
uv run scripts/generate_all.py
```

This regenerates all six terminal files and `exports/` from `schemes/alight.yml`.

---

## source files

`schemes/alight.yml`: named colours, ANSI mapping, palette roles and semantic roles.
`identity.yml`: typography, logo asset paths, logo references and which tool gets assigned which colour accent.

---

## scripts

`export_*.py`: one per terminal app, and write into `terminal/<app>/`

`export_palette_module.py`: takes a tool name and output path as arguments and writes into a different repo _(eg. `wildfire/src/wildfire/palette.py)`_. It's not a part of `generate_all.py`.

`validate_identity.py`: checks `identity.yml` against `schemes/alight.yml` and `assets/`, no output file.

**status**: functional, actively maintained -- `uv run scripts/generate_all.py` runs end-to-end; no packaged CLI yet.
