# Ghostty

Three files, one per contrast level — pick the one you want:

```bash
mkdir -p ~/.config/ghostty/themes
cp alight-medium.conf ~/.config/ghostty/themes/alight  # or alight-hard.conf / alight-soft.conf
echo 'theme = alight' >> ~/.config/ghostty/config
```

Reload: `cmd+shift+,` on macOS, `ctrl+shift+,` on Linux. Or just start up a new session.

Verify: `uv run scripts/live_show_swatches.py` from `alight/`
