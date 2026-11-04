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
- `--out DIR` writes them to DIR instead (the image build stages them: wolos-pkgbuilds `wolos-system/PKGBUILD`
  `_east_walls_build`, installed to `/usr/share/wolos/wallpapers/themes/`).

## The parameter set (the desktop's transition)
`python3 -I tools/east/walls.py gate --params [--theme ID] [--out FILE]` prints the Moon Gate's parameters as
JSON: the ring (centre, radius, squash, width, twist) and the sun (centre, radius) from `walls_sig3d.GATE`, x as
a share of the frame width and y and lengths as shares of its height, and for day and night the ring light,
ribbon dye and sun colours `calculus.derive()` gives them (`--theme`: that theme's dye). The image ships it as
`/usr/share/wolos/wallpapers/wolos-gate.params.json`; on a day/night or theme change the shell moves the ring
light, the ribbon dye and the sun from the old picture to the new one over 600 ms instead of a cross-fade
(wolos-shell `src/kit/gate.rs`, which falls back to the same values built in).

## Other forms in this directory
`sigjuzhe-*` (the lifted eave) and `sigfold-*` (the screen fold) are variations of the same renderer;
`pouso-*`, `veil-*`, `bloom-*`, `dunes-*`, `juzhe-*` and the places (`cachoeira`, `brasilia`, `estaiada`,
`rioniteroi`) are earlier studies and are not shipped. `scores.json` holds `score.py --kind wallpaper` totals
for the early forms (the 3D forms were judged by eye).

## Design rules in one place
`docs/adr/brand-east.md` sections 4-7 (flow, density, palette, light) and
`.claude/v012/brand-east/wallpaper-brief.md` ("Why our wallpaper").
