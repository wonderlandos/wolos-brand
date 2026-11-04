# WolOS wallpapers (east): the Moon Gate

The WolOS signature wallpaper is the **moon gate** (`siggate`): a closed ring of ribbon with real volume,
four ribbons passing above and below it, the quiet gold at the lower right, and a clean empty centre where
the windows live. Day and night, 4k (3840x2160) and 16:10 (2560x1600). Pure SVG, no raster, no filters
other than feGaussianBlur. Everything is generated; nothing here is hand-drawn.

## Always shipped (4 files, in git)
| file | size |
|---|---|
| `wolos-gate-day-4k.svg` | 1.42 MB |
| `wolos-gate-night-4k.svg` | 1.62 MB |
| `wolos-gate-day-16x10.svg` | 1.41 MB |
| `wolos-gate-night-16x10.svg` | 1.61 MB |

Rebuild: `python3 -I tools/east/walls.py gate` (run from the repo root of the design tree, `wt/design-cjk`;
needs only Python 3 and the files in `tools/east/`; writes the four files above in this directory;
under 1 second).

## Per theme (generated at image build, not in git)
`east/wallpapers/themes/gate-<theme>-{day,night}-{4k,16x10}.svg`: one per built-in theme (23 themes x 2 modes
x 2 sizes = 92 files, about 1.4-1.6 MB each, 133 MB in all). Same geometry as the default; only the dye
changes. The base colour of each theme is its `accent` (lightness 0.575, chroma clamped to 0.06-0.23,
neutral accents take the violet hue: `tools/east/themesets.py: theme_base`) and every colour is then
`calculus.derive()` from that base.

Rebuild: `python3 -I tools/east/walls.py themes siggate`
- input: the theme files `crates/core/src/theme/builtin/*.json` (path in `themesets.THEMES_DIR`, override with
  the environment variable `WOLOS_THEMES`);
- output: `east/wallpapers/themes/` (created if missing; the directory is git-ignored);
- time: under 1 second (it only writes SVG text; 12 worker processes); disk: 133 MB. Rendering a file with
  rsvg-convert takes a few seconds at 4k, so a build step should NOT rasterise them.
- If the image must stay small, generate only the sizes and modes in use, or only the active theme at login.

## Other forms in this directory
`sigjuzhe-*` (the lifted eave) and `sigfold-*` (the screen fold) are variations of the same renderer;
`pouso-*`, `veil-*`, `bloom-*`, `dunes-*`, `juzhe-*` and the places (`cachoeira`, `brasilia`, `estaiada`,
`rioniteroi`) are earlier studies and are not shipped. `scores.json` holds `score.py --kind wallpaper` totals
for the early forms (the 3D forms were judged by eye).

## Design rules in one place
`docs/adr/brand-east.md` sections 4-7 (flow, density, palette, light) and
`.claude/v012/brand-east/wallpaper-brief.md` ("Why our wallpaper").
