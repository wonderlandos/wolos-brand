# The WolOS icon language

Every full-colour icon of the `WolOS` theme speaks one language with two finishes: **crafted objects** (D2, the apps) and **pressed paper** (D1, places, devices and mimetypes). Nothing here is drawn by hand: `design/tools/icons/` generates every SVG, checks it, and renders the PNGs. This file states the rules the generator implements; a number here is the number in the code (file and name in brackets).

Rejected, and not to come back: flat white-on-colour marks, pixel art, gloss sweeps, window dots, a platform's system colours (`checks.BANNED`).

## 1. Light (one rule for every icon)

- One key light, straight above and a little in front. It is never coloured and never moves between icons.
- Everything the light touches gets, in this order: a lit top edge, a body ramp from light (top) to deep (bottom), an occlusion band where it meets another surface, and a soft cast shadow straight down (`dx = 0`).
- The lit lip: a white stroke on the inside of the edge, 80-90% at the top, gone by 35% of the height (`svgk.rimlight`, 3-7 units wide).
- Emissive things (a prompt, a door light, a play mark, an indicator) get a bloom under the sharp shape (blur 10-30, 45-60%) and a pale core. They are the only things lighter than the top light.
- Glass and metal get a specular (a white ellipse or crescent, 40-85%). Matte things (paper, wood, rope) get none.

## 2. Shadow

- Shadows are never grey: they are the object's own darkest tone (the card's `edge` colour) at 45-65%.
- Two per raised object (`svgk.shadows`): ambient (offset 26-34 down, blur 20-26, 55-62%) and contact (offset 8-14, blur 6-10, 40-50%).
- The card has the same pair: offset 26 / blur 26 at 42%, offset 8 / blur 6 at 50% (`svgk.container`).
- D1 objects: ambient 16% (22% on the small variant) at offset 20 / blur 30, plus a contact line at offset 6 / blur 4, 55% (`paper_set.pobj`).

## 3. Grid and container

- Canvas: `viewBox="0 0 1024 1024"` for every full-colour icon (`checks.static`).
- **The soft card** (apps only): 824 x 824 body from (100, 100) to (924, 924), a 100-unit margin for the shadows. Corners are superellipse arcs of exponent **3.1** (continuous curvature): top-left and bottom-right radius 236, top-right and bottom-left 150 (`svgk.CARD`).
- Card body: a vertical ramp `top -> bot`; a radial glow from the top centre (24-40%, `glow_op`); a bottom darkening to 22%; an inner rim stroke of 7 units clipped inside (white 70% at the top, 0 by 45%, 16% at the very bottom as bounce); a 2-unit outer hairline in the `edge` tone at 38%.
- Kits carry a lid: a seam across the top fifth (y 262), the band above it 10% lighter, the glyph centred at y 600 instead of 512 (`families.KITS`).
- **Live area**: the glyph spans about **68%** of the card width. Checked on the render: 0.56-0.86 for the full drawing at 128 px, 0.62-0.84 for the small drawing at 48 px, both 0.06 lower for the Kits (`checks.LIVE_FULL`, `LIVE_SMALL`).
- Optical centre: round or heavy objects sit 0-8 units above (512, 512); bottom-heavy ones (a bag, an envelope, a crate) have their visual centre near y 530.

## 4. Families and materials

The families table is `families.FAMILIES`: it gives each context its finish. Inside a family each icon has one main material, at most two (the object and one fitting), and **one pop**: a single accent of another hue.

| family | finish | materials in use |
|---|---|---|
| apps | D2, crafted object on the soft card | brushed steel, brass, aluminium, dark glass, lacquer, kraft paper, paper and wax, vinyl, cedar, enamel, leather, ivory |
| places | D1, pressed paper: the folder or the basket | lacquered paper folder, steel-mesh basket |
| devices | D1, pressed paper: the device slab | a matte slab in the `dev` tone, a paper label |
| mimetypes | D1, pressed paper: the page with a type band | paper page, a band in the category hue |

Metals are fixed ramps (`BRASS #FFF0B3 -> #E5A93B -> #8A5A12`, `METAL #FFFFFF -> #D5D9E2 -> #8B93A6`); paper is `#FFFAF0 -> #E1C8A2` on objects and `icon.paper` `#FFF6EA` on emblems. Whites are never pure except a specular spot or a lit lip.

## 5. Colour roles

- **Card** (`container(top, bot, glow, edge)`): one hue family per app. `top` is 8-14% lighter than the base hue, `bot` 35-45% darker, `glow` a pale tint of the same hue, `edge` its near-black. Every shadow inside the card uses `edge`.
- **Object**: a neutral material (steel, paper, ivory, vinyl) or one hue that contrasts the card by luminance; its tones come from its own ramp.
- **Pop**: one accent per icon, from the brand set: violet `#7C5CFF`/`#6A4DF4` (the WolOS accent), gold `#FFC94A`/`#F0A81E`, wine `#C2416B`, mint `#39E0A8`. Where the brand motif means something, the pop carries it: the keyhole (Settings, Software, the crate's hasp), the lit door (Installer, Launcher, the clock's twelve).
- **D1 categories** come from `design/tokens/colors.json` `icon.categories` (`wolos`, `system`, `dev`, `files`, `web`, `talk`, `media`, `store`: `body`, `tint`, `pop`). Emblems on a body use `icon.paper`; on paper they use the category body when it holds 3:1 against paper, else `icon.ink` (`paper_set.tone`).
- Dark cards (lum(`bot`) < 0.05) are lifted on the small variant (16% / 20% toward white, glow +6%) so a dark glyph still separates.

## 6. Building a glyph

1. Silhouette first: the object must read as a flat black shape at 48 px. If it does not, simplify before adding detail.
2. Then light it: silhouette, side wall (if extruded), top face ramp, occlusion, lip, shadows. Never a flat mark with an effect on top.
3. Volume by an offset copy (extrusion), a 3-7 unit lit lip (thickness), or a radial gradient (roundness).
4. Nothing below 12 units except texture. At 48 px only shapes of 25 units and more survive: the silhouette, the light/dark split and the pop.
5. One brand motif per icon, only where it means something.

## 7. The D1 finish (pressed paper)

- A single object, not a tile: a +-3.5% lightness ramp with no hue shift, a 6-unit inner highlight at 18% (up to 40% on slabs), matte, no rim, no gloss.
- The emblem is raised by one emboss filter (`paper_set.emb`: a small drop, one unit of top light, one of bottom shade). The small variant drops the filter.
- Folders: a back plane with the tab on the right, a paper sheet, a front plane with a lit lip. Pages: dog-ear on the big top-left corner, a 7-unit hairline, the type band 170 units high in the category hue.
- Devices: a slab in `shade(dev, +20%)`, a paper label or lit screen as the emblem, an indicator in the `dev` pop.

## 8. Sizes and variants

- **Full** (`Icon.svg(False)`): the scalable SVG and the 128 and 512 px PNGs.
- **Small** (`Icon.svg(True)`, `design/icons/apps/small/`): the source of the 48 px PNG and every render up to 64 px. Same drawing, the glyph scaled about its optical centre (`families.SCALE`), no grain, no emboss, lighter ramps on dark cards.
- Under 32 px the symbolic icon is used (16 grid, `currentColor`, `design/tools/icons.py`), never a shrunk colour icon.

## 9. What every renderer must draw

The theme is drawn by three renderers: `rsvg-convert` (the PNGs and the checks), the GTK 4 icon renderer, and `QtSvg` (Qt apps load the same theme). An icon ships only when all three draw it alike.

- Allowed elements: paths and basic shapes, linear and radial gradients, masks, filters made of the safe primitives only (`checks.SAFE_FILTER`: blur, offset, flood, composite, merge, colour matrix, turbulence, blend). No lighting primitives (GTK draws them black), no `<image>`, `<text>`, `<style>`, `<use>`, scripts or foreign content. Under 40 KB.
- No `clip-path`: QtSvg ignores it. The generator writes each clip as the same shape in a white luminance mask (`svgk.qt_safe`).
- Every filtered element opens with a canvas-sized empty rect (`svgk.gtk_safe`, `svgk.PAD`): GTK sizes a filter from the geometry it filters.
- A soft ring is a radial gradient (`svgk.soft_ring`), not a blurred stroke.
- No shape is drawn only by a filter: with every filter ignored an icon stays within RMSE 0.08 of its render. Paper grain is an invisible shape whose noise is masked to it (`svgk.grained`).

## 10. Checks (nothing is written when one fails)

| check | where | bar |
|---|---|---|
| static rules of section 9, banned colours, ids unique and resolved | `checks.static` | none may fail |
| live area, legibility at 48 px (median glyph contrast >= 1.35:1, >= 55% of pixels at 1.3:1), edge ring >= 1.3:1 on the light `#F3F1F8` and dark `#191720` ground | `checks.raster` | both variants |
| alias rows name a drawing; no name claimed twice | `build.alias_errors` | none may fail |
| SVGs, small drawings and alias tables are what the generator writes | `build.py --check` | byte for byte |
| overlay PNGs (48, 128, 512) are renders of the SVGs, one grid | `overlay.py --check` | 12 per channel on 0.2% of pixels |
| GTK draws like `rsvg-convert` | `gtkcheck/check.sh` | RMSE <= 0.02 at 48 and 128 px |
| QtSvg draws like `rsvg-convert` | `qtcheck/check.sh` | RMSE <= 0.03 at 48 and 128 px |
| filters ignored, silhouettes on both grounds, PNG sizes | `crates/shell/tests/icons_v2.rs` | RMSE <= 0.08; 1.3:1 |

## 11. Adding an icon

1. Draw it in the module of its family (`crafted_a.py`, `crafted_b.py`, `crafted_c.py` for apps; `paper_set.py`, `paper_more.py` for the long tail) with the helpers of `svgk.py`.
2. Add one row to `families.py` (apps: `APPS` or `APPS_SHIPPED`; long tail: the module's `DEVICES` or `MIMES`) and its other names to `build.py` `ALIASES` or `PLACE_ALIASES`.
3. `python3 -I design/tools/icons.py` (symbolic set, then this set, the aliases and the PNGs), then `python3 -I design/tools/icons/sheet.py OUT --names <name>` and look at it at 128 and 48 on both grounds.
4. Run the checks of section 10.
