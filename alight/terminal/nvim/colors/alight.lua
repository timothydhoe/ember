-- alight.lua -- generated from schemes/alight.yml by export_nvim.py
-- do not hand-edit; change the source palette or the role mapping
-- in export_nvim.py instead, then regenerate.

if vim.g.colors_name then
  vim.cmd("hi clear")
end
vim.o.background = "dark"
vim.g.colors_name = "alight"

-- contrast variants: set vim.g.alight_contrast to "hard", "medium",
-- or "soft" before :colorscheme alight loads. Falls back to "medium".
local CONTRAST = {
  hard = { base = "#101319", raised = "#1A1F29", guide = "#22262C" },
  medium = { base = "#161A22", raised = "#202631", guide = "#292D36" },
  soft = { base = "#1C212B", raised = "#262D3A", guide = "#2F353F" },
}
local surface = CONTRAST[vim.g.alight_contrast] or CONTRAST["medium"]

-- base ui --------------------------------------------------------------
vim.api.nvim_set_hl(0, "Normal", { fg = "#E5DCD8", bg = surface.base })
vim.api.nvim_set_hl(0, "NormalFloat", { fg = "#F6ECE8", bg = surface.raised })
vim.api.nvim_set_hl(0, "FloatBorder", { fg = "#9E9B9A", bg = surface.raised })
vim.api.nvim_set_hl(0, "NonText", { fg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "SpecialKey", { fg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "CursorLine", { bg = surface.raised })
vim.api.nvim_set_hl(0, "CursorLineNr", { fg = "#ABCE41", bg = surface.raised })
vim.api.nvim_set_hl(0, "LineNr", { fg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "SignColumn", { bg = surface.base })
vim.api.nvim_set_hl(0, "FoldColumn", { fg = "#9E9B9A", bg = surface.base })
vim.api.nvim_set_hl(0, "Folded", { fg = "#9E9B9A", bg = surface.raised })
vim.api.nvim_set_hl(0, "WinSeparator", { fg = "#9E9B9A", bg = surface.base })
vim.api.nvim_set_hl(0, "VertSplit", { link = "WinSeparator" })
vim.api.nvim_set_hl(0, "StatusLine", { fg = "#ABCE41", bg = surface.raised, bold = true })
vim.api.nvim_set_hl(0, "StatusLineNC", { fg = "#9E9B9A", bg = surface.raised })
vim.api.nvim_set_hl(0, "TabLine", { fg = "#9E9B9A", bg = surface.raised })
vim.api.nvim_set_hl(0, "TabLineSel", { fg = surface.base, bg = "#ABCE41" })
vim.api.nvim_set_hl(0, "TabLineFill", { bg = surface.raised })
vim.api.nvim_set_hl(0, "WildMenu", { fg = surface.base, bg = "#ABCE41" })
vim.api.nvim_set_hl(0, "Pmenu", { fg = "#F6ECE8", bg = surface.raised })
vim.api.nvim_set_hl(0, "PmenuSel", { fg = surface.base, bg = "#ABCE41" })
vim.api.nvim_set_hl(0, "PmenuSbar", { bg = surface.raised })
vim.api.nvim_set_hl(0, "PmenuThumb", { bg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "Cursor", { fg = surface.base, bg = "#47EB8E" })
vim.api.nvim_set_hl(0, "Visual", { bg = "#2A4B5A" })
vim.api.nvim_set_hl(0, "Search", { fg = surface.base, bg = "#EB9970" })
vim.api.nvim_set_hl(0, "IncSearch", { fg = surface.base, bg = "#E3E2B5" })
vim.api.nvim_set_hl(0, "CurSearch", { link = "IncSearch" })
vim.api.nvim_set_hl(0, "MatchParen", { fg = "#E3E2B5", bold = true })
vim.api.nvim_set_hl(0, "Directory", { fg = "#7E86AA" })
vim.api.nvim_set_hl(0, "Title", { fg = "#B18FC2", bold = true })
vim.api.nvim_set_hl(0, "ErrorMsg", { fg = "#F6663C", bold = true })
vim.api.nvim_set_hl(0, "WarningMsg", { fg = "#ABCE41" })

-- diff ------------------------------------------------------------------
vim.api.nvim_set_hl(0, "DiffAdd", { fg = "#47EB8E", bg = surface.raised })
vim.api.nvim_set_hl(0, "DiffChange", { fg = "#7E86AA", bg = surface.raised })
vim.api.nvim_set_hl(0, "DiffDelete", { fg = "#F6663C", bg = surface.raised })
vim.api.nvim_set_hl(0, "DiffText", { fg = "#8193CB", bg = surface.raised, bold = true })

-- diagnostics (:h diagnostic-highlights) ---------------------------------
vim.api.nvim_set_hl(0, "DiagnosticError", { fg = "#F6663C" })
vim.api.nvim_set_hl(0, "DiagnosticWarn", { fg = "#ABCE41" })
vim.api.nvim_set_hl(0, "DiagnosticInfo", { fg = "#7E86AA" })
vim.api.nvim_set_hl(0, "DiagnosticHint", { fg = "#89BABE" })
vim.api.nvim_set_hl(0, "DiagnosticOk", { fg = "#47EB8E" })
vim.api.nvim_set_hl(0, "DiagnosticUnderlineError", { sp = "#F6663C", undercurl = true })
vim.api.nvim_set_hl(0, "DiagnosticUnderlineWarn", { sp = "#ABCE41", undercurl = true })
vim.api.nvim_set_hl(0, "DiagnosticUnderlineInfo", { sp = "#7E86AA", undercurl = true })
vim.api.nvim_set_hl(0, "DiagnosticUnderlineHint", { sp = "#89BABE", undercurl = true })
vim.api.nvim_set_hl(0, "DiagnosticVirtualTextError", { fg = "#F6663C" })
vim.api.nvim_set_hl(0, "DiagnosticVirtualTextWarn", { fg = "#ABCE41" })
vim.api.nvim_set_hl(0, "DiagnosticVirtualTextInfo", { fg = "#7E86AA" })
vim.api.nvim_set_hl(0, "DiagnosticVirtualTextHint", { fg = "#89BABE" })
vim.api.nvim_set_hl(0, "LspInlayHint", { fg = "#9E9B9A", italic = true })

-- preferred syntax groups (see :help group-name) -------------------------
vim.api.nvim_set_hl(0, "Comment", { fg = "#9E9B9A", italic = true })
vim.api.nvim_set_hl(0, "Constant", { fg = "#EB9970" })
vim.api.nvim_set_hl(0, "String", { fg = "#AFAC6A" })
vim.api.nvim_set_hl(0, "Character", { link = "String" })
vim.api.nvim_set_hl(0, "Number", { link = "Constant" })
vim.api.nvim_set_hl(0, "Boolean", { link = "Constant" })
vim.api.nvim_set_hl(0, "Float", { link = "Number" })
vim.api.nvim_set_hl(0, "Identifier", { fg = "#E5DCD8" })
vim.api.nvim_set_hl(0, "Function", { link = "Identifier" })
vim.api.nvim_set_hl(0, "Statement", { fg = "#AC93B9", italic = true })
vim.api.nvim_set_hl(0, "Conditional", { link = "Statement" })
vim.api.nvim_set_hl(0, "Repeat", { link = "Statement" })
vim.api.nvim_set_hl(0, "Label", { link = "Statement" })
vim.api.nvim_set_hl(0, "Operator", { fg = "#E5DCD8" })
vim.api.nvim_set_hl(0, "Keyword", { link = "Statement" })
vim.api.nvim_set_hl(0, "Exception", { link = "Statement" })
vim.api.nvim_set_hl(0, "PreProc", { fg = "#70E59B" })
vim.api.nvim_set_hl(0, "Include", { link = "Statement" })
vim.api.nvim_set_hl(0, "Define", { link = "PreProc" })
vim.api.nvim_set_hl(0, "Macro", { link = "PreProc" })
vim.api.nvim_set_hl(0, "PreCondit", { link = "PreProc" })
vim.api.nvim_set_hl(0, "Type", { fg = "#89BABE" })
vim.api.nvim_set_hl(0, "StorageClass", { link = "Type" })
vim.api.nvim_set_hl(0, "Structure", { link = "Identifier" })
vim.api.nvim_set_hl(0, "Typedef", { link = "Type" })
vim.api.nvim_set_hl(0, "Special", { link = "String" })
vim.api.nvim_set_hl(0, "SpecialChar", { link = "Special" })
vim.api.nvim_set_hl(0, "Tag", { fg = "#8193CB", underline = true })
vim.api.nvim_set_hl(0, "Delimiter", { link = "String" })
vim.api.nvim_set_hl(0, "SpecialComment", { fg = "#9E9B9A", italic = true })
vim.api.nvim_set_hl(0, "Debug", { fg = "#F6663C" })
vim.api.nvim_set_hl(0, "Underlined", { fg = "#7E86AA", underline = true })
vim.api.nvim_set_hl(0, "Ignore", { fg = surface.base, bg = surface.base })
vim.api.nvim_set_hl(0, "Error", { fg = surface.base, bg = "#F6663C", bold = true })
vim.api.nvim_set_hl(0, "Todo", { fg = "#ABCE41", bg = surface.raised, bold = true })

vim.api.nvim_set_hl(0, "Added", { link = "DiffAdd" })
vim.api.nvim_set_hl(0, "Changed", { link = "DiffChange" })
vim.api.nvim_set_hl(0, "Removed", { link = "DiffDelete" })

-- treesitter refinements (most @captures link to groups above already) --
vim.api.nvim_set_hl(0, "@variable", { fg = "#E5DCD8" })
vim.api.nvim_set_hl(0, "@variable.builtin", { fg = "#89BABE", italic = true })
vim.api.nvim_set_hl(0, "@function", { fg = "#2BC275" })
vim.api.nvim_set_hl(0, "@function.method", { fg = "#2BC275" })
vim.api.nvim_set_hl(0, "@function.call", { link = "@function" })
vim.api.nvim_set_hl(0, "@function.method.call", { link = "@function" })
vim.api.nvim_set_hl(0, "@variable.parameter", { link = "Identifier" })
vim.api.nvim_set_hl(0, "@string.documentation", { fg = "#9E9B9A", italic = true })
vim.api.nvim_set_hl(0, "@lsp.typemod.string.documentation", { fg = "#9E9B9A", italic = true })
vim.api.nvim_set_hl(0, "@property", { fg = "#E5DCD8" })
vim.api.nvim_set_hl(0, "@constructor", { fg = "#89BABE" })
vim.api.nvim_set_hl(0, "@module", { fg = "#89BABE" })
vim.api.nvim_set_hl(0, "@punctuation.bracket", { fg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "@punctuation.delimiter", { fg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "@punctuation.special", { fg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "@markup.heading", { fg = "#B18FC2", bold = true })
vim.api.nvim_set_hl(0, "@markup.strong", { bold = true })
vim.api.nvim_set_hl(0, "@markup.italic", { italic = true })
vim.api.nvim_set_hl(0, "@markup.link.label", { fg = "#7E86AA", underline = true })
vim.api.nvim_set_hl(0, "@markup.link.url", { fg = "#7E86AA", underline = true })

-- gitsigns.nvim -----------------------------------------------------------
vim.api.nvim_set_hl(0, "GitSignsAdd", { fg = "#47EB8E" })
vim.api.nvim_set_hl(0, "GitSignsChange", { fg = "#7E86AA" })
vim.api.nvim_set_hl(0, "GitSignsDelete", { fg = "#F6663C" })
vim.api.nvim_set_hl(0, "GitSignsTopdelete", { link = "GitSignsDelete" })
vim.api.nvim_set_hl(0, "GitSignsChangedelete", { link = "GitSignsChange" })

-- snacks.nvim indent (structural nesting cues) -----------------------------
vim.api.nvim_set_hl(0, "SnacksIndent", { fg = surface.guide })
vim.api.nvim_set_hl(0, "SnacksIndentScope", { fg = "#AC93B9" })

-- blink.cmp -----------------------------------------------------------
vim.api.nvim_set_hl(0, "BlinkCmpMenu", { fg = "#F6ECE8", bg = surface.raised })
vim.api.nvim_set_hl(0, "BlinkCmpMenuBorder", { fg = "#9E9B9A", bg = surface.raised })
vim.api.nvim_set_hl(0, "BlinkCmpMenuSelection", { fg = surface.base, bg = "#ABCE41" })
vim.api.nvim_set_hl(0, "BlinkCmpLabel", { fg = "#E5DCD8" })
vim.api.nvim_set_hl(0, "BlinkCmpLabelMatch", { fg = "#ABCE41", bold = true })
vim.api.nvim_set_hl(0, "BlinkCmpKind", { fg = "#9E9B9A" })
vim.api.nvim_set_hl(0, "BlinkCmpKindFunction", { link = "Function" })
vim.api.nvim_set_hl(0, "BlinkCmpKindVariable", { link = "Identifier" })
vim.api.nvim_set_hl(0, "BlinkCmpKindKeyword", { link = "Keyword" })
vim.api.nvim_set_hl(0, "BlinkCmpKindModule", { link = "Type" })
vim.api.nvim_set_hl(0, "BlinkCmpKindClass", { link = "Type" })
vim.api.nvim_set_hl(0, "BlinkCmpDoc", { fg = "#F6ECE8", bg = surface.raised })
vim.api.nvim_set_hl(0, "BlinkCmpDocBorder", { fg = "#9E9B9A", bg = surface.raised })
