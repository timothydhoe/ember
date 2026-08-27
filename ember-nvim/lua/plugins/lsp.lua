return {
	{
		"mason-org/mason-lspconfig.nvim",
		opts = {
			ensure_installed = { "vtsls", "html", "cssls", "bashls", "marksman", "lua_ls", "sqlls" },
		},
		dependencies = {
			{ "mason-org/mason.nvim", opts = {} },
			"neovim/nvim-lspconfig",
		},
	},
	{
		"neovim/nvim-lspconfig",
		config = function()
			vim.lsp.enable({ "ty", "ruff" })
		end,
	},
}
