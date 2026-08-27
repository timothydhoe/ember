return {
    {
        "stevearc/conform.nvim",
        event = { "BufWritePre" },
        cmd = { "ConformInfo" },
        opts = {
            formatters_by_ft = {
                python = { "ruff_format", "ruff_organize_imports" }, -- both run, in order
                javascript = { "prettier" },
                typescript = { "prettier" },
                javascriptreact = { "prettier" },
                typescriptreact = { "prettier" },
                html = { "prettier" },
                css = { "prettier" },
                json = { "prettier" },
                yaml = { "prettier" },
                sh = { "shfmt" },
                markdown = { "prettier" },
                lua = { "stylua" },
            },
            default_format_opts = {
                lsp_format = "fallback", -- filetypes with no formatter above fall back to the LSP server's own formatting
            },
            format_on_save = {
                timeout_ms = 500,
            },
        },
    },
}
