local opt = vim.opt

opt.termguicolors = true

opt.number = true
opt.relativenumber = true
opt.signcolumn = "yes"
opt.scrolloff = 8
opt.updatetime = 250
opt.timeoutlen = 300
opt.splitright = true
opt.splitbelow = true
opt.mouse = "a"
opt.clipboard = "unnamedplus"
opt.undofile = true

opt.expandtab = true
opt.shiftwidth = 4
opt.tabstop = 4

-- QoL -----------------------------------------------------------------
opt.cursorline = true -- :help cursorline

opt.linebreak = true -- :help linebreak
opt.breakindent = true -- :help breakindent

opt.ignorecase = true -- :help ignorecase
opt.smartcase = true -- :help smartcase

opt.inccommand = "split" -- :help inccommand

opt.pumheight = 10 -- :help pumheight

opt.confirm = true -- :help confirm

opt.equalalways = false -- :help equalalways
