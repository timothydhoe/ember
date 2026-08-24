# Alacritty

Add to `~/.config/alacritty/alacritty.toml`:

```toml
[general]
import = ["/absolute/path/to/alight.toml"]
```

Verify: `uv run scripts/live_show_swatches.py` from `alight/`
