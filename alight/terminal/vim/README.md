# Vim

```bash
mkdir -p ~/.vim/colors
cp colors/alight.vim ~/.vim/colors/
echo 'colorscheme alight' >> ~/.vimrc
```

Targets both Vim and Neovim's `:colorscheme` loader directly (legacy `:hi` commands, `cterm`+`gui` pairs, `v:colornames` registration on Vim 9.1+). If you're on Neovim specifically, prefer [`terminal/nvim/README.md`](../nvim/README.md) instead — same palette, but native `nvim_set_hl()`, Treesitter captures, LSP diagnostics, and plugin-specific highlight groups this file doesn't cover.

Contrast: set `g:alight_contrast` to `"hard"`, `"medium"`, or `"soft"` before `colorscheme alight` loads. Defaults to `"medium"` if unset.

```vim
let g:alight_contrast = "soft"
colorscheme alight
```

Verify: `uv run scripts/live_show_swatches.py` from `alight/`
