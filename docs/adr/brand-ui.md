# ADR brand-ui: the interface on the Brand calculus

Status: proposal (design branch `wave3/brand`; nothing installed reads it). Date: 2026-11-04. Author: DESIGN-ui.
Lead direction: improve, do not redo; balance, never extreme; every number derived from the calculus.

The calculus, the scorer and the A2 icons are in `docs/adr/brand-calculus.md` and `docs/adr/brand-rules-pack.md` (existing paths). This ADR applies them to the shell: the symbolic icons, the kit primitives, the Dock and the Control Center. Everything here is measured from `crates/shell` (kit.css, widgets.rs, ui/dock.rs, ui/control_center/mod.rs, tests/golden) and proposed next to it; the shell worker implements from the tables in sections 2 to 4.

Code: `tools/ui/` (`pen.py` stroke grammar, `glyphs.py` the icons, `symbolic.py` generator, `check.py` craft and score, `primitives.py`, `dock.py`, `cc.py`, `boards.py`, `sheet.py`). Output: `ui/symbolic/{16,24}/`, `ui/primitives/`, `ui/dock/`, `ui/control-center/`, `ui/scores.json`. Boards sent to the lead: `.claude/v012/brand/renders/ui-*.png`. Units: 1 fen = 4 px; named lengths 1 2 3 4 6 10 15 21 30 42 60 84 144 fen = 4 8 12 16 24 40 60 84 120 168 240 336 576 px.

## 1. Symbolic icons: one stroke grammar from the A2 geometry

131 of the 132 symbolic names the shell requests (`"name-symbolic"` literals in `crates/shell/src`, the list `tests/symbolic_icons.rs` checks) are drawn; the 132nd, `wolos-glyph`, is the mark and is copied unchanged. Generator `tools/ui/symbolic.py`; output `ui/symbolic/16/` and `ui/symbolic/24/`, fill-only outlines in `currentColor` with `style="color:#2e3436"`, like `icons/symbolic` (GTK 4.20 draws stroked symbolics as blobs; no file here contains `stroke`). The other 194 names of `icons/symbolic` stay as they are.

| rule | value | derived from |
|---|---|---|
| G1 stroke | 2 fen at 24 px, 1.5 px at 16 px (optical size: the small size is relatively heavier). Round caps and joins | A2 details are 0.9 to 1.4 fen on a 15-fen glyph; a symbolic glyph fills 21, so x 21/15 = 1.3 to 2.0. 1.5 px at 16 is the shipped weight |
| G2 module | master grid 24 fen, art box 21 (1.5 to 22.5) hinted to 22 px at 24 and 14 px at 16 (14 = 21 x 2/3 exactly). Boxes are given by outer edges on named fen (21 15 10 6 4 3 2); dots are 4 fen across; a gap between strokes is one stroke | calculus `NAMED`, A2 card 21 of 24 |
| G3 corners | outer radius 3 fen from 12 fen wide, 2 below, a pill when the height is 6 fen or less | A2 keys 1.6, pills h/2, folder 1.2 |
| G4 juzhe | a slope with a ridge and an eave is a juzhe curve (`geom.juzhe`): the shield's shoulders, the folder tab, the bell's flare, the eye's lids | A2 roofs and folder tab |
| G5 one light | upper left, 1:2: gaps and openings face the lower right (refresh, update-urgent), the one solid mass sits lower right (the lock of `network-wireless-encrypted`, the badge of `software-update-urgent`), rain falls along the shadow vector | S1 to S6, `LIGHT`, `SHADOW` |
| G6 leaf | a second leaf (an inactive signal level, a battery being charged) is the same glyph at opacity 0.35 | A2 `leaf` is a tint, never grey |

Hinting (`pen.py`): at 24 px strokes snap to whole pixels (both edges crisp); at 16 px to n+0.25 or n+0.75 (one edge crisp); outer edges of boxes snap to whole px. Curve samples are never snapped. A pass fits an icon that leaves the art box and centres it; volume levels share the fit of `audio-volume-high` so the speaker does not move.

Craft check at 16 px (`tools/ui/check.py`, pass or fail per icon, current set measured the same way):

| check | current | proposed |
|---|---|---|
| margin: no ink on the outer pixel ring | 119/131 | 130/131 |
| clog: no gap narrower than 0.8 px that is not a seam | 114/131 | 124/131 |
| thin: no stroke under 1.0 px | 128/131 | 129/131 |
| centre: ink box within 1 px of the cell centre (volume levels exempt, aligned on purpose) | 129/131 | 131/131 |
| edge softness (share of non-crisp edge pixels, lower is better) | 0.65 | 0.62 |

Known failures, not hidden: `battery-full`, `battery-full-charged`, `camera-photo`, `edit-delete`, `input-keyboard`, `keyboard-brightness`, `wolos-control-center` (gaps of 0.5 to 0.8 px at 16 px), `battery-caution-charging`, `battery-low-charging` (the bolt's thin tips), `wolos-restore` (arrow head 0.1 alpha on the edge ring).

Score (`tools/brand/score.py`, kind icon, the 24 px glyph at 15 fen on a white 21-fen tile, current drawn the same way; mean over 131): current 79.94, proposed 79.97; wins 65/131. Per rule current to proposed: qi 85.8 to 85.9, sha 86.4 to 88.3, forms 98.5 to 97.5, zones 86.5 to 86.4, palette 100 to 100, light 48.7 to 47.6, proportion 78.1 to 78.6, density 55.6 to 55.3. Honest reading: a monochrome line icon on a tile barely moves the eight rules, so the score only says the new set does not regress; the gains are the craft checks above and the shared grammar, not the number.

## 2. Primitives (kit.css)

Specimen `ui/primitives/{current,proposed}-{light,dark}.svg` and layout trees; score of the specimen (screen, with tree): current 74.0, proposed 73.7 (proportion 34.0 to 45.1, sha 88.3 to 98.2, forms 80.9 to 73.1, density 46.4 to 51.6). A first run with the control circle at 24 scored 77.3; the circle stays 28 (below), which costs 3.6 points.

| primitive | current (kit.css) | proposed | fen |
|---|---|---|---|
| control height (button, entry, dropdown) | 24 | 24 | 6, zhi |
| radius button, entry, dropdown, menu item, row | 6 | 8 | 2 |
| radius card (`--glass-radius-s`, `.module`) | 10 | 12 | 3 |
| radius panel (`--glass-radius-m`) | 16 | 16 | 4 |
| radius shelf and big panel (`--glass-radius`) | 24 | 24 | 6 |
| switch | 30 x 18, padding 2, knob 14 | 40 x 24, padding 2, knob 20 | 10 x 6 |
| compact switch (detail head) | 28 x 12 | 24 x 16 | 6 x 4 |
| slider trough / knob | 4 / 16 | 4 / 16 | 1 / 4 |
| fat slider | 24 | 24 | 6 |
| control circle | 28 | 28 (kept: the 16 px glyph needs 6 px of air; the one size left off the named list) | 7 |
| segmented | h 20, r 4, padding 8 | h 24, r 6, padding 8 | 6 |
| list row | 40 | 40 | 10 |
| toggle tile | min-height 76 | 84 | 21 |
| spacing | 4 8 12 16 24 32 | 4 8 12 16 24 (32 stays for page margins) | 1 2 3 4 6 (8) |
| shadows | `0 1px 2px rgba(0,0,0,.08)`, `0 6px 18px rgba(0,0,0,.24)`: straight down, black | elevation e is (e, 2e) px: `1px 2px 4px`, `2px 4px 12px`, `3px 6px 24px`, in the ink of the surface (`#151520` light, `#020206` dark; opacity .12/.16/.22 by day, double by night), never black | |

CSS shape of the shadow tokens (same names as the site guidance `--wol-elev-*`): `--elev-1: 1px 2px 4px alpha(var(--ink), .12); --elev-2: 2px 4px 12px alpha(var(--ink), .16); --elev-3: 3px 6px 24px alpha(var(--ink), .22);` with `--ink` set per scheme next to `--text`.

## 3. Dock

Measured from the shell (px) and proposed. Board: `ui/dock/*.png` (1x and 2x, light and dark, with the A2 icons in both so the geometry, light and motion are isolated from the art). Scores (screen, with the shelf tree): light current 75.7, proposed 77.0; dark current 80.0, proposed 79.8. In the light board qi falls (85.6 to 80.3) because thirteen tiles weigh the same, so no landing exists; in return proportion, zones and density rise. The dark board is a tie.

| item | current | where | proposed | fen |
|---|---|---|---|---|
| tile (icon canvas) | 56; Size slider 32..96, default 56 | `kit/widgets.rs:25` `DOCK_TILE`; `core/src/prefs.rs:60` `TILE_SIZE = (32, 96, 56)` | 60 (range unchanged, default 60) | 15, cai |
| gap | 8 | `ui/dock.rs:500` `gtk::Box::new(.., S2)` | 8 | 2 |
| shelf padding | 4 top, 8 sides, 0 bottom | `kit/kit.css:82` `.dock-shelf` | 4 top, 12 sides, 4 bottom | 1, 3, 1 |
| running dot | 4 x 4 in its own row: margin 2 + 4 + 2 = 8 | `kit.css:96` `.running-dot`; `widgets.rs:911` | 4 x 4 drawn over the tile's bottom 4 px (the A2 canvas keeps 1.5 fen of air there): `margin: -4px 0 0 0` (kit.css already uses negative margins, line 170) | 1 |
| focused app | same dot | none | a pill 12 x 4 in the accent (`.running-dot.focused`) | 3 x 1 |
| shelf height | 68 = 4 + 56 + 8; `exclusive_zone` test uses 24 + 4 + 64 + 8 | `ui/dock.rs:1039` | 68 = 4 + 60 + 4; the test numbers do not change | 17, band cai |
| shelf width, 13 pins | 851 (golden dock-light.png) | | 911 = 13 x 60 + 13 x 8 + 1 + 24 + 2 | |
| visible gap between cards (A2, 87.5% of the canvas) | 8 + 7 = 15 | | 8 + 7.5 = 15.5; edge inset 12 + 3.75 = 15.75: one rhythm | 4 |
| radius | 24 | `--glass-radius` | 24, concentric with the A2 card | 6 |
| margins | lift 24, sides 32, bottom 8 | `dock.rs:198` `SHELF_LIFT`; kit.css:82 | unchanged | 6, 8, 2 |
| separator | 1 px, margin 8 top / 12 bottom | `kit.css:97` | 1 px, margin 10 / 10 (40 px, centred on the art) | 10 |
| shadow | `0 6px 18px rgba(0,0,0,.24), 0 1px 4px rgba(0,0,0,.16)` | `--glass-shadow` | `3px 6px 24px alpha(ink,.22), 1px 2px 4px alpha(ink,.16)` (night: double) | e3, e1 |
| rim | `inset 0 1px 0 rgba(255,255,255,.5)`: the whole top edge | `--glass-rim` | `inset 1px 1px 0 rgba(255,255,255,.5)`: upper-left edge only (gloss sits on the lit rim) | |
| glass | flat 50% | `kit.css:82` | same tint, `linear-gradient(153deg, +16% alpha, -16% alpha)`: 153 deg is the 1:2 direction | |
| hover magnify | 1.15 under the pointer, spring `SNAPPY` 320/30 | `dock.rs:265` `MAGNIFY` | 68/60 = 1.133 (the tile grows 1 fen on each side); the two neighbours 64/60 = 1.067 (half a fen): same spring. The neighbour falloff needs `Magnify::hover` to scale i +- 1 (optional) | +2, +1 |
| bounce (launch, attention) | 16 px, 640 ms ease-in-out | kit.css:90 | 16 px (4 fen), 640 ms: unchanged | 4 |
| focus ring | 2 px accent, offset 2 | kit.css:95 | unchanged | |

Motion rules (derived): a lift is a whole fen (4 px) or a whole fen of growth; elevation steps 1 to 2 on hover (the icon art carries its own shadow, the shelf shadow does not move); the pointer never makes anything smaller than the rest state; reduce motion stills hover and bounce, as today.

Shell worker, in order: `DOCK_TILE` and `TILE_SIZE` default 56 to 60 and the `prefs.rs:663-665` default assertions; `.dock-shelf` padding/shadow/rim/gradient and `.running-dot` in kit.css; `MAGNIFY` const (and kit.css:88, whose 1.15 the spring overrides); separator margins; regenerate `dock-*.png` and `motion-dock-hover-*.png` goldens. The user's saved Size is kept (only the default changes).

## 4. Control Center

Measured from `tests/golden/controlcenter-all-light.png` (368 x 706: panel 320 x 658 inside 24 px margins) and kit.css, drawn again by `tools/ui/cc.py` with the same renderer for both versions (the redrawn current panel is 320 x 658, equal to the golden). Board `ui/control-center/cc-*.png`. Scores (screen, with the layout tree, same desktop crop): light current 71.0, proposed 75.3; dark 60.5 to 66.3. Proportion 35.5 to 65.7 (light), forms 72.5 to 73.2, density 67.6 to 69.3; sha is low for both (56.6 and 55.9 by day, 0.0 and 7.3 by night) because card edges read as long straight cuts, and qi is a little lower at night (78.8 to 71.7).

Layout, panel coordinates in px (the padding is 12, so content starts at (12, 12)):

| module | current | proposed (x, y, w, h) | fen |
|---|---|---|---|
| panel | 320 x 658; padding 12 + 1 px border (content 294) | 336 x 600; padding 12; hairline as `box-shadow: inset 0 0 0 1px` so content is 312 | 84 x 150; bands guan, cai |
| top row: connectivity (Wi-Fi, Bluetooth) | 143 x 92 | (12, 12, 152, 84); rows of circle 28 every 32 | 38 x 21 |
| top row: modes (Focus, Dark Mode) | 143 x 92 | (172, 12, 152, 84) | 38 x 21 |
| Sound | 294 x 72, below Display | (12, 104, 312, 64) | 78 x 16 |
| Now Playing (art 40) | 294 x 72 | (12, 176, 312, 64) | 78 x 16 |
| Display | 294 x 72, first | (12, 248, 312, 64) | 78 x 16 |
| tile rows 1, 2, 3 | 68 x 92 at x 0, 76, 152, 227 (67.5 wide: the border takes 2 px) | 72 x 84 at x 12, 92, 172, 252; rows at y 320, 412, 504 | 18 x 21 |
| gaps | 8 and 8 | 8 and 8 | 2 |
| radii | panel 16, card 10 | panel 24, card 12 (concentric: 12 + padding 12) | 6, 3 |
| content height | 632 (golden y 37 to 669) | 576 = 84 + 3 x 64 + 3 x 84 + 6 x 8: one ruler | 144 |

Inside the modules: a slider module (64 high) has its title at the top (13 px, 600, line 16), the fat slider (24) at `y + 28`, the chevron 16 at the right; the tile (84 high) puts the circle 28 at 12 px from the top (no longer centred with the label, so a one-line label does not drop the circle), the label from `y + 52`, two lines of 16.

Five-phase order, top to bottom (generating cycle water, wood, fire, earth, metal, back to water; neighbours are always same or generating, never overcoming):

| group (phase) | content | why |
|---|---|---|
| water: connect | Wi-Fi, Bluetooth; Focus, Dark Mode (metal feeds water) | entry, upper left: the first control a user reaches |
| wood: sound and media | Sound, Now Playing | the quiet middle band |
| fire: light | Display, Night Shift, Keyboard Brightness | light and heat |
| earth: ground | Battery, Stay Awake | power holds the machine |
| metal: tools | Screenshot, Record, Zoom, Increase Contrast, Reduce Motion | precision and access |
| water: loop | Screen Mirroring (last tile) | metal feeds water: the page ends where it began |

Tile order, row-major: Night Shift, Keyboard Brightness, Battery, Stay Awake / Screenshot, Record, Zoom, Increase Contrast / Reduce Motion, Screen Mirroring, then plugin tiles (`tiles::TileSource`). Module order: Sound, Now Playing, Display (today Display, Sound, Now Playing). Colour does not code the groups: the on-state stays the accent; only the order, the nine zones and the spacing carry the meaning.

Nine zones (thirds of the panel): entry in the upper-left third, the centre third holds Now Playing (no accent bar) and the start of Display, weight sits low in the tile rows (mountain). Light: panel shadow `3px 6px 24px`, cards `1px 2px 4px`, knobs `1px 2px 3px`, in the ink of the surface; the panel keeps a 1 px rim on the upper-left edge only; the on-circles and slider fills get a 153-degree gradient, lighter at the upper left.

Shell worker, in order: `kit/widgets.rs:29` `CONTROL_CENTER_WIDTH` 320 to 336 (`NARROW_WIDTH` 288 and the three-column fallback stay; `width_for` tests keep passing); `.controlcenter .glass-panel` (kit.css:100) padding 12, `border: none`, the hairline as inset shadow, radius 24 (a Control Center override, the generic `.glass-panel` stays 16); `--glass-radius-s` 10 to 12 (global: regenerate all goldens); top cards `min-height: 84px` with rows at 32; `SliderModule` and `NowPlayingCard::compact` `min-height: 64px`; `button.toggle-tile` (kit.css:129) `min-height: 84px; padding: 12px 2px 4px` with the circle `valign: start` and a two-line label slot; `mod.rs:686-721` append Sound, Now Playing, Display; the tile order in `mod.rs` (the `toggles`/`Grid` block around 740-810); `tiles::columns` (tiles.rs:59) keeps 4 at 336. Regenerate `controlcenter-*.png`.

## 5. What the numbers say, and do not

- Every proposed length is a whole fen and most are named; the Control Center's content height is exactly one ruler (576) and its panel and the Dock shelf sit in good bands. This is derivation, not decoration.
- The scorer measured fit to the rules, not beauty. Wins: Control Center (both modes), primitives proportion, Dock light, craft at 16 px. Ties: symbolic tile score, Dock dark. Losses to read as warnings: Dock qi (equal tiles have no landing; the focused pill is a start, a bolder landing was left out as an extreme), Control Center night qi and sha.
- The wallpaper behind the glass changes the light and ground terms: all boards use one desktop crop per mode for both versions.

## 6. Open for the lead

1. Dock tile default 56 to 60 and panel 320 to 336: both grow the shell by a few percent; the alternative that keeps today's widths is a 4 x 68 tile row and 56 tiles (68 is 17 fen, whole but unnamed).
2. `--glass-radius-s` 10 to 12 is global (cards everywhere, goldens). The site guidance leaves 10 or 12 to the lead.
3. Whether the 194 symbolic names the shell does not request are redrawn on this grammar next, or left until the shell uses them.
