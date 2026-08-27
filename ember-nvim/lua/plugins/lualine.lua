local function hex(color_num)
	if not color_num then
		return nil
	end
	return string.format("#%06x", color_num)
end

local function get_hl(name)
	local ok, h = pcall(vim.api.nvim_get_hl, 0, { name = name, link = false })
	if not ok then
		return {}
	end
	return h
end

-- "a" sections used to fill with a solid accent-colored block per mode.
-- Same issue we already fixed once on the plain statusline: reserve the
-- loud color for text, not backgrounds. Every mode now shares the same
-- calm "elevated" background and differs only by bold, colored text.
local function alight_theme()
	local fg = hex(get_hl("Normal").fg)
	local elevated = hex(get_hl("StatusLineNC").bg)
	local accent = hex(get_hl("StatusLine").fg)
	local muted = hex(get_hl("LineNr").fg)

	local function mode(color)
		return { bg = elevated, fg = color, gui = "bold" }
	end

	local b = { bg = elevated, fg = fg }
	local c = { bg = elevated, fg = muted }

	return {
		normal = { a = mode(accent), b = b, c = c },
		insert = { a = mode(hex(get_hl("String").fg)), b = b, c = c },
		visual = { a = mode(hex(get_hl("Type").fg)), b = b, c = c },
		replace = { a = mode(hex(get_hl("DiagnosticError").fg)), b = b, c = c },
		command = { a = mode(hex(get_hl("DiagnosticWarn").fg)), b = b, c = c },
		inactive = { a = c, b = c, c = c },
	}
end

local function lsp_clients()
	local clients = vim.lsp.get_clients({ bufnr = 0 })
	if #clients == 0 then
		return "no lsp"
	end
	local names = {}
	for _, client in ipairs(clients) do
		table.insert(names, client.name)
	end
	return table.concat(names, ", ")
end

return {
	{
		"nvim-lualine/lualine.nvim",
		dependencies = { "nvim-mini/mini.icons" },
		event = "VeryLazy",
		keys = {
			{
				"<leader>li",
				function()
					vim.notify(lsp_clients(), vim.log.levels.INFO, { title = "LSP Clients" })
				end,
				desc = "Show Attached LSP Clients",
			},
		},
		opts = function()
			local diag_colors = {
				error = { fg = hex(get_hl("DiagnosticError").fg) },
				warn = { fg = hex(get_hl("DiagnosticWarn").fg) },
				info = { fg = hex(get_hl("DiagnosticInfo").fg) },
				hint = { fg = hex(get_hl("DiagnosticHint").fg) },
			}
			local diff_colors = {
				added = { fg = hex(get_hl("GitSignsAdd").fg) },
				modified = { fg = hex(get_hl("GitSignsChange").fg) },
				removed = { fg = hex(get_hl("GitSignsDelete").fg) },
			}

			return {
				options = {
					theme = alight_theme(),
					component_separators = "",
					section_separators = "",
					globalstatus = true,
				},
				sections = {
					lualine_a = {
						{
							"mode",
							fmt = function(str)
								return str:lower()
							end,
						},
					},
					lualine_b = {
						"branch",
						{ "diff", diff_color = diff_colors },
						{ "diagnostics", diagnostics_color = diag_colors },
					},
					lualine_c = { "filename" },
					lualine_y = { "progress" },
					lualine_z = { "location" },
				},
			}
		end,
	},
}
