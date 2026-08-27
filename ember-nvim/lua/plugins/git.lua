return {
  {
    "lewis6991/gitsigns.nvim",
    event = { "BufReadPre", "BufNewFile" },
    opts = {
      on_attach = function(bufnr)
        local gitsigns = require("gitsigns")

        local function map(mode, lhs, rhs, desc)
          vim.keymap.set(mode, lhs, rhs, { buffer = bufnr, desc = desc })
        end

        -- navigation
        map("n", "]c", function()
          if vim.wo.diff then
            vim.cmd.normal({ "]c", bang = true })
          else
            gitsigns.nav_hunk("next")
          end
        end, "Next Hunk")
        map("n", "[c", function()
          if vim.wo.diff then
            vim.cmd.normal({ "[c", bang = true })
          else
            gitsigns.nav_hunk("prev")
          end
        end, "Prev Hunk")

        -- actions
        map("n", "<leader>hs", gitsigns.stage_hunk, "Stage Hunk")
        map("n", "<leader>hr", gitsigns.reset_hunk, "Reset Hunk")
        map("n", "<leader>hp", gitsigns.preview_hunk, "Preview Hunk")
        map("n", "<leader>hb", function() gitsigns.blame_line({ full = true }) end, "Blame Line")
      end,
    },
  },
  {
    "dlyongemallo/diffview.nvim", -- maintained fork; see note above
    cmd = { "DiffviewOpen", "DiffviewClose", "DiffviewFileHistory" },
    keys = {
      { "<leader>gd", "<cmd>DiffviewOpen<cr>", desc = "Diff View (working tree)" },
      { "<leader>gh", "<cmd>DiffviewFileHistory %<cr>", desc = "File History (current file)" },
    },
  },
}
