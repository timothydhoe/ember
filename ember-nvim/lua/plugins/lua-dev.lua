return {
	{
		"folke/lazydev.nvim",
		ft = "lua",
		opts = {
			library = {
				-- load vim.uv/libuv types when that API is actually used
				{ path = "${3rd}/luv/library", words = { "vim%.uv" } },
			},
		},
	},
}
