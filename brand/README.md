# WolOS brand

The mark is four nested doors on one floor line: the small door into Wonderland, with light coming through. Flat fills only, no gradients, no strokes. Colours come from `../tokens/colors.json`: accent `#7C5CFF` (light) and `#8B6CFF` (dark), plus three steps of the same hue for depth (`#4B2FD6`, `#33208A`; on dark `#5E3FE6`, `#36209A`) and the tint `#E9E3FF` for the lit door. The wordmark is drawn (one round-capped stroke weight, expanded to outlines), so it needs no font. `text` is `#1C1C1E` on light and `#F5F5F7` on dark.

Everything here is generated: `python3 -I design/tools/brand/build.py design` (from the repository root; needs `rsvg-convert`, and `convert` for the site favicon).

| File | viewBox | Use |
|---|---|---|
| `wolos-mark.svg` | 64 | Full mark on light grounds. 24 px and up. About page, notifications. Installed as the `wolos-mark` app icon. |
| `wolos-mark-on-dark.svg` | 64 | Full mark on dark grounds (#1C1C1E, black). |
| `wolos-mark-mono.svg` | 64 | One colour (`#1C1C1E`), true cut-outs: print, embossing, one-ink places. |
| `wolos-mark-mono-white.svg` | 64 | The same in white, for photos and dark grounds. |
| `wolos-mark-16.svg` | 16 | Two doors drawn on whole pixels. Use at 16-23 px on light grounds; never scale the full mark down to 16. |
| `wolos-mark-16-on-dark.svg` | 16 | The same for dark grounds. |
| `wolos-glyph-symbolic.svg` | 16 | Menubar glyph: one path, `currentColor`, GTK recolours it. Icon theme names `wolos-glyph-symbolic` and `wolos-logo-symbolic`. |
| `wolos-wordmark.svg` | 360x96 | Mark and "WolOS" for light grounds. At least 96 px wide. |
| `wolos-wordmark-dark.svg` | 360x96 | The same for dark grounds. |
| `wolos-boot.svg` | 1920x1080 | Boot splash: the mark on black with the progress bar. |
| `wolos-splash.png` | 256x256 | Kernel and plymouth splash: the mark on black, 8-bit RGBA. Installed to `/boot/images/wolos.png` and the plymouth theme. |
| `os_wolos.png` | 128x128 | Raster `wolos-mark.svg`, transparent. |

Rules
- Clear space around the lockup is half the cap height of the wordmark; around the mark alone, one fifth of its width.
- Below 96 px wide use the mark alone. Below 24 px use `wolos-mark-16*.svg` or the glyph.
- Do not recolour the doors, add a gradient or a shadow, stretch it, or put it on a busy photo (use `-mono-white`).

(c) 2026 Julia Klee. Wonderland Brand License 1.0 (`LicenseRef-Wonderland-Brand-1.0`, see `../LICENSE`).
