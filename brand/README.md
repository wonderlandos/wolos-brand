# WolOS brand

The mark is four nested doors on one floor line: the small door into Wonderland, with light coming through. Flat fills only, no gradients, no strokes. Colours come from `../tokens/colors.json`: accent `#7C5CFF` (light) and `#8B6CFF` (dark), plus three steps of the same hue for depth (`#4B2FD6`, `#33208A`; on dark `#5E3FE6`, `#36209A`) and the tint `#E9E3FF` for the lit door. The wordmark is drawn (one round-capped stroke weight, expanded to outlines), so it needs no font. The ink is the WolOS neutral ramp from the same tokens (`light.text` `#181521` on light, `dark.text` `#F6F5FB` on dark); the generator reads it, so a token retune reaches the brand on the next build.

Everything here is generated: `python3 -I design/tools/brand/build.py design` (from the repository root; needs `rsvg-convert`, and `convert` for the site favicon). The `-ja` files are the exception: the katakana is outlined once from Noto Sans CJK JP (SIL OFL 1.1, no font embedded) by the CJK brand tool (`.claude/brand/cjk/src/final.py` in the product checkout); `build.py` does not rebuild them.

| File | viewBox | Use |
|---|---|---|
| `wolos-mark.svg` | 64 | Full mark on light grounds. 24 px and up. About page, notifications. Installed as the `wolos-mark` app icon. |
| `wolos-mark-on-dark.svg` | 64 | Full mark on dark grounds (`dark.bg` `#191720`, black). |
| `wolos-mark-mono.svg` | 64 | One colour (the ink, `#181521`), true cut-outs: print, embossing, one-ink places. |
| `wolos-mark-mono-white.svg` | 64 | The same in white, for photos and dark grounds. |
| `wolos-mark-16.svg` | 16 | Two doors drawn on whole pixels. Use at 16-23 px on light grounds; never scale the full mark down to 16. |
| `wolos-mark-16-on-dark.svg` | 16 | The same for dark grounds. |
| `wolos-glyph-symbolic.svg` | 16 | Menubar glyph: one path, `currentColor`, GTK recolours it. Icon theme names `wolos-glyph-symbolic` and `wolos-logo-symbolic`. |
| `wolos-wordmark.svg` | 360x96 | Mark and "WolOS" for light grounds. At least 96 px wide. |
| `wolos-wordmark-dark.svg` | 360x96 | The same for dark grounds. |
| `wolos-boot.svg` | 1920x1080 | Boot splash: the white mono mark on black with the progress bar. |
| `wolos-splash.png` | 256x256 | Kernel and plymouth splash: the white mono mark on black, 8-bit RGBA. Installed to `/boot/images/wolos.png` and the plymouth theme. |
| `os_wolos.png` | 128x128 | Raster `wolos-mark.svg`, transparent. |
| `wolos-wordmark-ja.svg` | 6254x1834 (1x 218x64) | Japanese mark: ウォロス alone, Noto Sans CJK JP Black, centred, transparent, for light grounds. No door, no Chinese. Japanese pages, store listing, merch. At least 18 px ink height. |
| `wolos-wordmark-ja-dark.svg` | 6254x1834 | The same for dark grounds. |
| `wolos-wordmark-ja-boot.svg` | 2129x990.34 (1x 480x223) | WolOS over ウォルOS (Noto Sans CJK JP Medium), centred, transparent, for light grounds. Boot and start screens. At least 320 px wide (the ウォルOS line is then about 15 px tall). |
| `wolos-wordmark-ja-boot-dark.svg` | 2129x990.34 | The same for dark grounds (the boot one). |
| `wolos-boot-ja.svg` | 1920x1080 | Japanese boot splash 16:9: `wolos-wordmark-ja-boot-dark` centred on `dark.bg` `#191720`, letters 640 px wide. |
| `wolos-boot-ja-2560x1600.svg` | 2560x1600 | The same at 16:10 (letters 853 px wide). |
| `wolos-splash-ja.png` | 480x190 | Plymouth-ready: the boot lockup in `dark.text` on transparent, 8-bit RGBA; the theme script draws the background. |

Rules
- Clear space around the lockup is half the cap height of the wordmark; around the mark alone, one fifth of its width.
- Japanese marks: clear space is half the ink height around `wolos-wordmark-ja`, half the WolOS cap height around the boot lockup (both are built into the artboards). Never set ウォロス or ウォルOS in a live font, re-track it, add the door mark or a Chinese line to it.
- Below 96 px wide use the mark alone. Below 24 px use `wolos-mark-16*.svg` or the glyph.
- Do not recolour the doors, add a gradient or a shadow, stretch it, or put it on a busy photo (use `-mono-white`).

(c) 2026 Julia Klee. Wonderland Brand License 1.0 (`LicenseRef-Wonderland-Brand-1.0`, see `../LICENSE`).
