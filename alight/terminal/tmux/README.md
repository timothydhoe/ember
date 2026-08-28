# tmux

Three files, one per contrast level — source the one you want from `~/.tmux.conf`:

```bash
source-file /absolute/path/to/alight-medium.tmux.conf  # or alight-hard.tmux.conf / alight-soft.tmux.conf
```

Reload: `tmux source-file ~/.tmux.conf`, or `prefix + :source-file ~/.tmux.conf`.

Verify: `uv run scripts/live_show_swatches.py` from `alight/`
