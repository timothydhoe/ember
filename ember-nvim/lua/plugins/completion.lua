return {
	{
		"saghen/blink.cmp",
		version = "1.*",
		dependencies = { "rafamadriz/friendly-snippets" },
		opts = {
			keymap = { preset = "default" },
			appearance = {
				nerd_font_variant = "mono",
			},
			completion = {
				documentation = { auto_show = true },
			},
			sources = {
				default = { "lazydev", "lsp", "path", "snippets", "buffer" },
				per_filetype = {
					sql = { "dadbod", "lsp", "snippets", "buffer" },
					mysql = { "dadbod", "lsp", "snippets", "buffer" },
					plsql = { "dadbod", "lsp", "snippets", "buffer" },
				},
				providers = {
					lazydev = {
						name = "LazyDev",
						module = "lazydev.integrations.blink",
						score_offset = 100,
					},
					dadbod = {
						name = "Dadbod",
						module = "vim_dadbod_completion.blink",
					},
				},
			},
			fuzzy = { implementation = "prefer_rust_with_warning" },
		},
	},
}
