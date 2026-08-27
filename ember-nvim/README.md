## Neovim Setup

This config replicates PyCharm-style IDE ergonomics in Neovim — LSP, completion,
Treesitter, fuzzy navigation, git integration, formatting — while staying fast
and terminal-native. Built with [lazy.nvim](https://github.com/folke/lazy.nvim),
themed with our own [`alight`](../alight) colorscheme.

### Bootstrap

| Plugin                                            | Why                                                                     |
| ------------------------------------------------- | ----------------------------------------------------------------------- |
| [`lazy.nvim`](https://github.com/folke/lazy.nvim) | Plugin manager. Handles install, lazy-loading, and update UI (`:Lazy`). |

### LSP & Language Tooling

| Plugin                                                                      | Why                                                                                                             |
| --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| [`mason.nvim`](https://github.com/mason-org/mason.nvim)                     | Installs LSP servers/formatters as sandboxed binaries — doesn't touch system Python/Node. Browse with `:Mason`. |
| [`mason-lspconfig.nvim`](https://github.com/mason-org/mason-lspconfig.nvim) | Bridges Mason's package names to Neovim's native LSP config and auto-enables installed servers.                 |
| [`nvim-lspconfig`](https://github.com/neovim/nvim-lspconfig)                | Ships default configs (how to launch each server, project-root detection) for `vim.lsp.enable()`.               |

**Servers**: `ty` + `ruff` (Python, installed via `uv tool install`, not Mason — keeps versions pinned to what `uv`/`pyproject.toml` resolve), `vtsls` (JS/TS), `html`, `cssls`, `bashls`, `marksman` (Markdown), `lua_ls` (this config itself).

Basic usage: `gd` go to definition · `gr` references · `gI` implementation · `K` hover docs · `<leader>ss` document symbols · `<leader>sS` workspace symbols · `<leader>sd` diagnostics list.

### Completion

| Plugin                                                                 | Why                                                                                             |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [`blink.cmp`](https://github.com/saghen/blink.cmp)                     | Completion engine. Pinned to `v1.*` — v2 needs a manually-installed system dependency.          |
| [`friendly-snippets`](https://github.com/rafamadriz/friendly-snippets) | Snippet collection `blink.cmp` pulls from.                                                      |
| [`lazydev.nvim`](https://github.com/folke/lazydev.nvim)                | Resolves plugin module names (`require("...")`) for completion when editing this config itself. |

Basic usage: type to trigger automatically · `Ctrl-Space` force-trigger · `Ctrl-y` accept · `Ctrl-n`/`Ctrl-p` navigate.

### Formatting

| Plugin                                                     | Why                                                                                                                                                                                                  |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`conform.nvim`](https://github.com/stevearc/conform.nvim) | Runs formatters on save. `ruff format` (Python), `prettier` (JS/TS/HTML/CSS/JSON/YAML/Markdown — prefers a project-local install over the global one automatically), `shfmt` (Bash), `stylua` (Lua). |

Basic usage: formats automatically on save · `:ConformInfo` shows which formatter ran for the current file.

### Syntax Highlighting

| Plugin                                                                                  | Why                                                                                                                                                         |
| --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`nvim-treesitter`](https://github.com/nvim-treesitter/nvim-treesitter) (`main` branch) | Real syntax-tree-based highlighting instead of regex. Covers Python, JS/TS/TSX, Bash, HTML, CSS, JSON, YAML, Lua, Markdown, **Turtle/RDF**, and **SPARQL**. |

Basic usage: automatic once a parser's installed · `:InspectTree` shows the live parse tree for the current buffer · `:TSUpdate` updates parsers.

### Navigation

| Plugin                                                                                     | Why                                                                                                                 |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------- |
| [`snacks.nvim`](https://github.com/folke/snacks.nvim) (`picker` + `explorer` modules only) | Fuzzy file/symbol/grep search and a file tree, from one actively-maintained source instead of two separate plugins. |
| [`mini.icons`](https://github.com/nvim-mini/mini.icons)                                    | File-type icons for the picker, explorer, and completion menu.                                                      |

Basic usage: `<leader><space>` smart find · `<leader>ff` find files · `<leader>fg` find git files · `<leader>fr` recent files · `<leader>fb` buffers · `<leader>/` live grep · `<leader>e` toggle file explorer.

### Git

| Plugin                                                           | Why                                                                                                                                   |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| [`gitsigns.nvim`](https://github.com/lewis6991/gitsigns.nvim)    | Inline hunk markers, staging, and blame without leaving the buffer.                                                                   |
| [`diffview.nvim`](https://github.com/dlyongemallo/diffview.nvim) | Full-tab diff review — this is the **actively-maintained fork**; the original `sindrets/diffview.nvim` has had no commits since 2024. |

Basic usage: `]c`/`[c` next/prev hunk · `<leader>hs` stage hunk · `<leader>hr` reset hunk · `<leader>hp` preview hunk · `<leader>hb` blame line · `<leader>gd` full diff view · `<leader>gh` file history.

### Markdown

| Plugin                                                                                 | Why                                                                                                                          |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| [`render-markdown.nvim`](https://github.com/MeanderingProgrammer/render-markdown.nvim) | Renders headings, tables, checkboxes, and code blocks styled in-buffer — no browser window. Directly relevant to `wildfire`. |

`marksman` (LSP, listed above) handles wiki-link completion, go-to-definition, and document symbols for notes vaults.

Basic usage: renders automatically in `.md` files · `<leader>mr` toggle rendering on/off.

### Database

| Plugin                                                                             | Why                                                                                                  |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| [`vim-dadbod`](https://github.com/tpope/vim-dadbod)                                | Run SQL directly from a buffer against a live connection.                                            |
| [`vim-dadbod-ui`](https://github.com/kristijanhusak/vim-dadbod-ui)                 | Drawer UI for managing connections and browsing schemas — PyCharm's Database tool window equivalent. |
| [`vim-dadbod-completion`](https://github.com/kristijanhusak/vim-dadbod-completion) | Live, schema-aware table/column completion, wired into `blink.cmp`.                                  |

**Server**: `sqlls` (listed with the others above) adds syntax-level SQL intelligence — hover, diagnostics — independent of any live connection. (Not `sqls`, the other well-known option: confirmed no longer maintained, not even installable via Mason anymore.)

### Vim Ergonomics

| Plugin                                                  | Why                                                                       |
| ------------------------------------------------------- | ------------------------------------------------------------------------- |
| [`vim-surround`](https://github.com/tpope/vim-surround) | Change/add/delete surrounding quotes, brackets, tags.                     |
| [`vim-repeat`](https://github.com/tpope/vim-repeat)     | Makes `.` repeat `vim-surround`'s mappings correctly.                     |
| [`vim-sleuth`](https://github.com/tpope/vim-sleuth)     | Auto-detects indentation per file instead of trusting one global setting. |

**Not installed, deliberately**: `vim-commentary` (also tpope) — Neovim 0.10+ ships built-in `gc`/`gcc` comment-toggling explicitly modeled on it, Treesitter-aware out of the box. Confirmed redundant rather than assumed.

Basic usage: `cs"'` change surrounding `"` to `'` · `ds"` delete surrounding quotes · `ys$"` wrap to end of line in quotes · `gcc` toggle comment on current line (built-in, not from a plugin).

Basic usage: `<leader>db` toggle the database drawer · `:DBUIAddConnection` add a connection · write (`:w`) inside a query buffer to execute it.

### Statusline

| Plugin                                                         | Why                                                                                                                                                  |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`lualine.nvim`](https://github.com/nvim-lualine/lualine.nvim) | Statusline. Theme is generated at runtime from `alight`'s live highlight groups — not a separate copy of the palette, so it can't drift out of sync. |

Basic usage: `<leader>li` show attached LSP clients (removed from the always-visible bar — static info doesn't need constant screen space).

### Colorscheme

|                       |                                                                                                                                                     |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`alight`](../alight) | Our own palette, generated from `schemes/alight.yml` via `scripts/export_nvim.py`. Loaded as a local `lazy.nvim` plugin pointed at `terminal/nvim`. |

---

### Prerequisites (not Neovim plugins, but required)

`tree-sitter-cli`, `fd`, `uv` (+ `ty`, `ruff` installed via `uv tool install`), a Nerd Font (`JetBrainsMono Nerd Font Mono`) — see [setup notes] if starting fresh.
