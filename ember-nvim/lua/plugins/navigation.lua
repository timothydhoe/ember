return {
	{
		"folke/snacks.nvim",
		priority = 1000,
		lazy = false, -- snacks sets up autocmds at startup; can't lazy-load
		dependencies = {
			{ "nvim-mini/mini.icons", opts = {} },
		},
		opts = {
			picker = { enabled = true },
			explorer = { enabled = true },
			indent = { enabled = true },
		},
		keys = {
			-- files & search
			{
				"<leader><space>",
				function()
					Snacks.picker.smart()
				end,
				desc = "Smart Find Files",
			},
			{
				"<leader>ff",
				function()
					Snacks.picker.files()
				end,
				desc = "Find Files",
			},
			{
				"<leader>fg",
				function()
					Snacks.picker.git_files()
				end,
				desc = "Find Git Files",
			},
			{
				"<leader>fr",
				function()
					Snacks.picker.recent()
				end,
				desc = "Recent Files",
			},
			{
				"<leader>fb",
				function()
					Snacks.picker.buffers()
				end,
				desc = "Buffers",
			},
			{
				"<leader>/",
				function()
					Snacks.picker.grep()
				end,
				desc = "Live Grep",
			},
			-- file tree
			{
				"<leader>e",
				function()
					Snacks.explorer()
				end,
				desc = "File Explorer",
			},
			-- LSP-powered navigation -- these show a picker when there's more than
			-- one result, instead of silently jumping to the first match
			{
				"gd",
				function()
					Snacks.picker.lsp_definitions()
				end,
				desc = "Goto Definition",
			},
			{
				"gr",
				function()
					Snacks.picker.lsp_references()
				end,
				nowait = true,
				desc = "References",
			},
			{
				"gI",
				function()
					Snacks.picker.lsp_implementations()
				end,
				desc = "Goto Implementation",
			},
			{
				"<leader>ss",
				function()
					Snacks.picker.lsp_symbols()
				end,
				desc = "Document Symbols",
			},
			{
				"<leader>sS",
				function()
					Snacks.picker.lsp_workspace_symbols()
				end,
				desc = "Workspace Symbols",
			},
			{
				"<leader>sd",
				function()
					Snacks.picker.diagnostics()
				end,
				desc = "Diagnostics",
			},
		},
	},
}
