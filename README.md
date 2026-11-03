# WolOS design

Wonderland theme: rabbit-eared keyhole (looking-glass). One accent: violet `#7C5CFF` (dark `#9B85FF`). macOS-like neutrals.

| Path | Content | Installs to |
|---|---|---|
| `brand/wolos-mark.svg` | Logo mark, 64 viewBox, legible at 16px | `/usr/local/share/wolos/brand/` |
| `brand/wolos-wordmark{,-dark}.svg` | Mark + "WolOS" (Inter) | `/usr/local/share/wolos/brand/` |
| `brand/wolos-glyph-symbolic.svg` | Monochrome menubar glyph | icon theme `wolos-logo-symbolic` |
| `brand/wolos-boot.svg` | Boot splash 1920x1080 | `/usr/local/share/wolos/brand/` |
| `brand/wolos-splash.png` | Kernel splash: the mark of `wolos-boot.svg`, 256x256 8-bit RGBA (the loader reads PNG only) | `/boot/images/wolos.png` |
| `tokens/colors.{css,json,sh}` | Light/dark palette, radii, blur, fonts | `/usr/local/share/wolos/tokens/` |
| `icons/apps/wolos-*.svg` | App and Kit tiles, 24-cell pixel grid (`tools/icons.py`; PNG 48/128/512 in `desktop/overlay/usr/share/icons/WolOS`) | `/usr/share/icons/WolOS/scalable/apps/` |
| `icons/symbolic/*-symbolic.svg` | Symbolic set: 16 grid, 1.5 px lines as filled outlines, 2 px radius, currentColor (`tools/icons.py`) | `/usr/share/icons/WolOS/symbolic/status/` |
| `icons/index.theme`, `aliases.tsv` | Theme `WolOS`, `Inherits=Adwaita,hicolor`; alias map | `/usr/local/share/icons/WolOS/` |
| `wallpapers/wonderland-{day,night,dusk}.svg` | 3840x2160 | `/usr/local/share/wolos/wallpapers/` |
| `cursors/README.md` | Port cursor choice | n/a |

Install icons: `sh design/icons/install.sh [dest]` (copies SVGs, symlinks aliases like `firefox`, `utilities-terminal`, `org.gnome.Nautilus`, runs `gtk-update-icon-cache`).
Tokens: source `colors.sh` (`WOL_THEME=dark` selects dark), import `colors.css` in GTK/Waybar/swaync CSS.
Fonts (ports): `x11-fonts/inter`, `x11-fonts/jetbrains-mono`, `x11-fonts/noto-basic`.
Rules: SVG only (except `brand/wolos-splash.png` and the PNGs `tools/icons.py` renders); every icon comes from `python3 tools/icons.py [--sheet out.png]`; symbolic icons are fill-only `currentColor` (GTK recolors them for light and dark).

License: art is under the Wonderland Brand License 1.0 (`LICENSE`, `LicenseRef-Wonderland-Brand-1.0`); `tools/` is GPL-2.0-or-later; `icons/store/` keeps each icon's own license. WolOS, the WolOS logo and the WolOS characters are reserved marks of Julia Klee. © 2026 Julia Klee.
