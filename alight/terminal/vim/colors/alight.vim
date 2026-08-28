" alight.vim -- generated from schemes/alight.yml by export_vim.py
" do not hand-edit; change the source palette or the role mapping
" in export_vim.py instead, then regenerate.

hi clear
if exists("syntax_on")
  syntax reset
endif
set background=dark
let g:colors_name = "alight"

" contrast variants: set g:alight_contrast to "hard", "medium", or
" "soft" before `colorscheme alight` loads. Falls back to "medium".
let s:contrast = {
\ 'hard': {'base': '#101319', 'raised': '#1A1F29'},
\ 'medium': {'base': '#161A22', 'raised': '#202631'},
\ 'soft': {'base': '#1C212B', 'raised': '#262D3A'},
\ }
let s:level = get(g:, 'alight_contrast', 'medium')
if !has_key(s:contrast, s:level)
  let s:level = 'medium'
endif
let s:base = s:contrast[s:level].base
let s:raised = s:contrast[s:level].raised

" register named colors (Vim 9.1+) so users can override before
" `colorscheme alight` loads
if exists('v:colornames')
  call extend(v:colornames, {'alight_hearth': '#141924'}, 'keep')
  call extend(v:colornames, {'alight_chalk': '#FBF7F5'}, 'keep')
  call extend(v:colornames, {'alight_chalk-dim': '#E5DCD8'}, 'keep')
  call extend(v:colornames, {'alight_beacon': '#89BABE'}, 'keep')
  call extend(v:colornames, {'alight_ash': '#9E9B9A'}, 'keep')
  call extend(v:colornames, {'alight_coal': '#0E1D39'}, 'keep')
  call extend(v:colornames, {'alight_alight': '#ABCE41'}, 'keep')
  call extend(v:colornames, {'alight_flare': '#F6663C'}, 'keep')
  call extend(v:colornames, {'alight_kindling': '#EB9970'}, 'keep')
  call extend(v:colornames, {'alight_verdigris': '#47EB8E'}, 'keep')
  call extend(v:colornames, {'alight_foxfire': '#2E8B57'}, 'keep')
  call extend(v:colornames, {'alight_spark': '#F6FCFA'}, 'keep')
  call extend(v:colornames, {'alight_smolder': '#B0936D'}, 'keep')
  call extend(v:colornames, {'alight_pilot': '#5D668D'}, 'keep')
  call extend(v:colornames, {'alight_pilot-tint': '#7E86AA'}, 'keep')
  call extend(v:colornames, {'alight_dusk': '#8E7FC7'}, 'keep')
  call extend(v:colornames, {'alight_fuel': '#2A4B5A'}, 'keep')
  call extend(v:colornames, {'alight_fuel-tint': '#5191AD'}, 'keep')
  call extend(v:colornames, {'alight_ember-dark': '#992929'}, 'keep')
  call extend(v:colornames, {'alight_ember-light': '#F9A851'}, 'keep')
  call extend(v:colornames, {'alight_cinder': '#0E0E18'}, 'keep')
  call extend(v:colornames, {'alight_bunsen': '#7284BB'}, 'keep')
  call extend(v:colornames, {'alight_amethyst': '#B18FC2'}, 'keep')
  call extend(v:colornames, {'alight_phosphor': '#67413C'}, 'keep')
  call extend(v:colornames, {'alight_smoke': '#222425'}, 'keep')
  call extend(v:colornames, {'alight_blaze': '#C27370'}, 'keep')
  call extend(v:colornames, {'alight_witchlight': '#E3E2B5'}, 'keep')
endif

" -- base ui --------------------------------------------------------------
execute 'hi Normal ctermfg=NONE guifg=#E5DCD8 ctermbg=NONE guibg=' . s:base . ' cterm=NONE gui=NONE'
hi NonText ctermfg=8 guifg=#9E9B9A cterm=NONE gui=NONE
hi SpecialKey ctermfg=8 guifg=#9E9B9A cterm=NONE gui=NONE
execute 'hi CursorLine ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi CursorLineNr ctermfg=11 guifg=#ABCE41 ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
hi LineNr ctermfg=8 guifg=#9E9B9A cterm=NONE gui=NONE
execute 'hi SignColumn ctermbg=NONE guibg=' . s:base . ' cterm=NONE gui=NONE'
execute 'hi FoldColumn ctermfg=8 guifg=#9E9B9A ctermbg=NONE guibg=' . s:base . ' cterm=NONE gui=NONE'
execute 'hi Folded ctermfg=8 guifg=#9E9B9A ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi VertSplit ctermfg=8 guifg=#9E9B9A ctermbg=NONE guibg=' . s:base . ' cterm=NONE gui=NONE'
execute 'hi StatusLine ctermfg=NONE guifg=' . s:base . ' ctermbg=11 guibg=#ABCE41 cterm=bold gui=bold'
execute 'hi StatusLineNC ctermfg=8 guifg=#9E9B9A ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi TabLine ctermfg=8 guifg=#9E9B9A ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi TabLineSel ctermfg=NONE guifg=' . s:base . ' ctermbg=11 guibg=#ABCE41 cterm=NONE gui=NONE'
execute 'hi WildMenu ctermfg=NONE guifg=' . s:base . ' ctermbg=11 guibg=#ABCE41 cterm=NONE gui=NONE'
execute 'hi Pmenu ctermfg=NONE guifg=#E5DCD8 ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi PmenuSel ctermfg=NONE guifg=' . s:base . ' ctermbg=11 guibg=#ABCE41 cterm=NONE gui=NONE'
execute 'hi Cursor ctermfg=NONE guifg=' . s:base . ' ctermbg=10 guibg=#47EB8E cterm=NONE gui=NONE'
hi Visual ctermbg=NONE guibg=#2A4B5A cterm=NONE gui=NONE
execute 'hi Search ctermfg=NONE guifg=' . s:base . ' ctermbg=3 guibg=#EB9970 cterm=NONE gui=NONE'
execute 'hi IncSearch ctermfg=NONE guifg=' . s:base . ' ctermbg=NONE guibg=#E3E2B5 cterm=NONE gui=NONE'
hi MatchParen ctermfg=NONE guifg=#E3E2B5 cterm=bold gui=bold
hi Directory ctermfg=NONE guifg=#7E86AA cterm=NONE gui=NONE
hi Title ctermfg=5 guifg=#B18FC2 cterm=bold gui=bold

" -- diff ------------------------------------------------------------------
execute 'hi DiffAdd ctermfg=10 guifg=#47EB8E ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi DiffChange ctermfg=NONE guifg=#7E86AA ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi DiffDelete ctermfg=9 guifg=#F6663C ctermbg=NONE guibg=' . s:raised . ' cterm=NONE gui=NONE'
execute 'hi DiffText ctermfg=13 guifg=#8193CB ctermbg=NONE guibg=' . s:raised . ' cterm=bold gui=bold'

" -- preferred syntax groups (see :help group-name) ------------------------
hi Comment ctermfg=8 guifg=#9E9B9A cterm=italic gui=italic
hi Constant ctermfg=3 guifg=#EB9970 cterm=NONE gui=NONE
hi String ctermfg=NONE guifg=#B0936D cterm=NONE gui=NONE
hi! link Character String
hi! link Number Constant
hi! link Boolean Constant
hi! link Float Number
hi Identifier ctermfg=NONE guifg=#E5DCD8 cterm=NONE gui=NONE
hi! link Function Identifier
hi Statement ctermfg=5 guifg=#B18FC2 cterm=bold gui=bold
hi! link Conditional Statement
hi! link Repeat Statement
hi! link Label Statement
hi Operator ctermfg=NONE guifg=#E5DCD8 cterm=NONE gui=NONE
hi! link Keyword Statement
hi! link Exception Statement
hi PreProc ctermfg=10 guifg=#70E59B cterm=NONE gui=NONE
hi! link Include Statement
hi! link Define PreProc
hi! link Macro PreProc
hi! link PreCondit PreProc
hi Type ctermfg=14 guifg=#89BABE cterm=NONE gui=NONE
hi! link StorageClass Type
hi! link Structure Identifier
hi! link Typedef Type
hi! link Special String
hi! link SpecialChar Special
hi Tag ctermfg=13 guifg=#8193CB cterm=underline gui=underline
hi! link Delimiter String
hi SpecialComment ctermfg=8 guifg=#9E9B9A cterm=italic,bold gui=italic,bold
hi Debug ctermfg=9 guifg=#F6663C cterm=NONE gui=NONE
hi Underlined ctermfg=NONE guifg=#7E86AA cterm=underline gui=underline
execute 'hi Ignore ctermfg=NONE guifg=' . s:base . ' ctermbg=NONE guibg=' . s:base . ' cterm=NONE gui=NONE'
execute 'hi Error ctermfg=NONE guifg=' . s:base . ' ctermbg=9 guibg=#F6663C cterm=bold gui=bold'
execute 'hi Todo ctermfg=11 guifg=#ABCE41 ctermbg=NONE guibg=' . s:raised . ' cterm=bold gui=bold'

hi! link Added DiffAdd
hi! link Changed DiffChange
hi! link Removed DiffDelete
