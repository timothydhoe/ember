# Ghostty

```bash
mkdir -p ~/.config/ghostty/themes
cp alight.conf ~/.config/ghostty/themes/alight
echo 'theme = alight' >> ~/.config/ghostty/config
```

Reload: `cmd+shift+,` on macOS, `ctrl+shift+,` on Linux. Or just start up a new session.

Verify: `uv run scripts/live_show_swatches.py` from `alight/`
