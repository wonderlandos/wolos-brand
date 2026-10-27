# Cursors

No custom build. Use an existing macOS-like theme from ports.

| Choice | Theme name | Port (verify) |
|---|---|---|
| Primary | `capitaine-cursors` | `x11-themes/capitaine-cursors` |
| Fallback | `Adwaita` | `x11-themes/adwaita-icon-theme` |

Port origin not verified here. Confirm on target: `pkg search -o cursor`.
If primary is absent, ship fallback; do not block the image.

Apply (size 24):

```sh
hyprctl setcursor capitaine-cursors 24        # Hyprland: env = XCURSOR_THEME,capitaine-cursors
gsettings set org.gnome.desktop.interface cursor-theme capitaine-cursors
```
