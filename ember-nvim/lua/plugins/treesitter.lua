return {
  {
    "nvim-treesitter/nvim-treesitter",
    branch = "main", -- old `master` is frozen; `main` is a ground-up rewrite
    lazy = false, -- this plugin explicitly doesn't support lazy-loading
    build = ":TSUpdate",
    config = function()
      require("nvim-treesitter").install({
        "python", "javascript", "typescript", "tsx",
        "bash", "html", "css", "json", "yaml",
        "lua", "markdown", "markdown_inline",
        "turtle", "sparql",
      })

      -- Neovim doesn't know these extensions by default
      vim.filetype.add({
        extension = {
          ttl = "turtle",
          trig = "turtle", -- TriG (named-graph Turtle) -- close enough for highlighting; flag if it looks wrong on real files
          jsonld = "json", -- JSON-LD is syntactically JSON; no dedicated grammar needed
        },
      })

      -- highlighting is opt-in per-filetype now, not automatic
      vim.api.nvim_create_autocmd("FileType", {
        pattern = "*",
        callback = function()
          pcall(vim.treesitter.start)
        end,
      })
    end,
  },
}
