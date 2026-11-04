# Site guidance: improving the WolOS site and the Hub with the brand calculus

Status: proposal for the site worker. Lead, 2026-11-04 07:30Z: improve, don't redo. Keep balance, no extremes, and always follow the flow. The rules are in `brand-calculus.md`; the formulas and the CLI are in `brand-rules-pack.md`.

Read for this: `site/src/index.css`, `site/src/kit.css`, `site/public/brand/colors.css`, `site/src/pages/Home.jsx`, and `wt/hub/site/src` (`hub.css`, `tokens.css`).

Evidence: full-page captures and DOM box trees from the built sites (`dist`, served locally, Playwright at 1440 wide). Files: `.claude/v012/brand/site/{home,hub}-current.{png,json}`, plus wireframes and trees for the proposal. Boards: `.claude/v012/brand/renders/site-{home,hub}-current-vs-proposed.png`. Scores (score.py, kind screen, with the tree): home 77.3 -> 79.9, hub 62.5 -> 73.9.

## 1. The module is already there: Tailwind's 1 = 1 fen

The site uses Tailwind, and its spacing unit (0.25 rem = 4 px) is the fen. So `p-6` is 6 fen (the zhi), `gap-10` is 10 fen (cai width), and `py-20` is 20 fen. What changes is only which numbers are allowed. Use the named lengths 1, 2, 3, 4, 6, 10, 15, 21, 30, 42, 60, 84 (in px: 4, 8, 12, 16, 24, 40, 60, 84, 120, 168, 240, 336). Any other whole fen is legal but unnamed. Use it only when a named one breaks the layout.

| used today (Home.jsx) | becomes | why |
|---|---|---|
| `py-20` (80) / `sm:py-28` (112) section rhythm | `py-[84px]` (21, zucai) / `sm:py-[120px]` (30) | named lengths; one section rhythm |
| `gap-16` (64) hero gap | `gap-15` (60, cai) | named |
| `mt-5` (20) after headings | `mt-6` (24, zhi) | named; one value for heading-to-text |
| `mt-8` (32) before actions | `mt-10` (40) | named |
| `mt-12` (48) before grids | `mt-10` (40) | named |
| `p-5 sm:p-6` card padding | `p-6` (24) everywhere | one inset |
| `gap-x-8` (32) feature grid | `gap-x-15` (60) | breathing between columns, matches the card gap |
| card grid `gap-4 / lg:gap-5` | `gap-6` (24) inside cards, `gap-15` (60) between cards at lg | see section 3 (bands) |

Containers:
- `wrap` max 72 rem (1152) is two rulers: keep it.
- `narrow` 44 rem (704) lands in the bing band. Make it 40 rem (640, cai band).
- `wrap` padding `clamp(1.25rem, 4vw, 2.5rem)` becomes `clamp(1.5rem, 4vw, 2.5rem)` (24..40, both named).

Type: put line heights on the fen, keep the sizes.

| token | today | becomes |
|---|---|---|
| `--text-xs` | 13 / 1.45 (18.9) | 13 / 20 |
| `--text-sm` | 15 / 1.55 (23.3) | 15 / 24 |
| `--text-base` | 17 / 1.65 (28.1) | 17 / 28 |
| `--text-lg` | 20 / 1.5 (30) | 20 / 32 |
| `--text-2xl` | clamp(…) / 1.12 | line `calc(1em + 4px)`, rounded to 44 at 40 px |
| `--text-3xl` | 76 / 1.02 | 76 / 80 |

Radii (`site/public/brand/colors.css`):

| token | today | becomes |
|---|---|---|
| `--wol-radius-sm` | 6 | 8 |
| `--wol-radius-md` | 10 | 12 |
| `--wol-radius-lg` | 14 | 16 |
| `--wol-radius-window` | 12 | 12 (unchanged) |
| `--wol-radius-dock` | 18 | 24 |

This also settles QA D-09 on the site side, since the GTK kit already uses 10/16/24. The open question is whether 10 or 12 is the card radius. The calculus says 12 (3 fen); the lead decides.

## 2. Light and shadows (cards, header, sheets)

One light, upper left. A shadow falls at dx:dy = 1:2, never straight down, and is coloured by the base ink, never neutral black.

```css
--wol-elev-1: 1px 2px 4px  color-mix(in oklab, #151520 12%, transparent);
--wol-elev-2: 2px 4px 12px color-mix(in oklab, #151520 16%, transparent);
--wol-elev-3: 3px 6px 24px color-mix(in oklab, #151520 22%, transparent);
```

- **Cards** (`@utility card`): `--wol-elev-1`, and `--wol-elev-2` on hover. No border-and-shadow doubling in light mode: keep the 1 px border, but at 8% instead of 12%.
- **Sheets and dialogs** (`dialog.sheet`, today `0 30px 80px -20px`): `--wol-elev-3`.
- **Tooltips and link previews** (today `0 10px 30px -12px`): `--wol-elev-2`.
- **The desktop demo** (today `shadow-[0_40px_100px_-40px_rgba(60,30,160,.5)]`): keep the violet tint, but at 1:2, e.g. `20px 40px 100px -40px`.
- **Terminal** (`.term`, today `0 20px 50px -24px`): `10px 20px 50px -24px`.
- **Header:** no shadow. Its bottom hairline is inset: it runs the width of `wrap`, not the full bleed (sha: no straight line into the frame edge).
- **Gloss:** at most an `inset 0 1px 0 rgba(255,255,255,.6)` on the top edge of raised controls, never on the bottom.

## 3. Door-light bands for the big boxes

Each dimension of an opening (card, panel, hero visual), taken modulo 576 px, should land in the cai, yi, guan or ben band (`calculus.band`). For the three-card rows in a 1152 wrap:

- 3 × 368 + 2 × 24 (today's sizes): 368 lands in jie. Avoid.
- 3 × 344 + 2 × 60: 344 lands in guan. **Use this.**

Cards 344 × 336 (guan × guan) for proofs, 344 × 288 (guan) for doors. Hero visual 576 × 324 (one ruler × guan, exactly 16:9). Closing call-to-action band 1152 × 216 (yi).

## 4. Flow map of the home page

**Today:**
- Entry is the logo, but the hero is a centred column: wordmark, title, lead, a second paragraph, then two buttons.
- The qi runs straight down the central axis through every section (centred heading, then a grid, again and again). That is a straight shot, the thing the spirit screen exists to break.
- The Download button is dark ink. It is the heaviest control, but not 7:5 over the wordmark and title above it.
- The proof (the live desktop) sits three sections down.

**Proposed** (wireframe `site-home-current-vs-proposed.png`):
1. **Entry, upper left:** logo, then the eyebrow, the pixel wordmark (21 fen tall) and the title, left-aligned in a 528-px column.
2. **First turn:** the live desktop moves into the hero, on the right (576 × 324). A Western Z: read left, look right.
3. **Landing:** Download, a 240 × 40 accent fill `#7452F5`, elevation 2, under the lead paragraph. "Try without installing" sits beside it as a quiet control. The second hero paragraph (`hero.text`) is removed: one lead is enough, which is functional breathing.
4. **Second turn:** the proofs. Heading left, three cards.
5. **Turn back:** the doors. Heading on the right half, cards across, so the path zig-zags instead of falling down the axis.
6. **Features:** 3 × 2. Each item has an inset top rule of the item's width: a rule ends where its content ends.
7. **Second landing:** a closing band with Download at the right end of the path, at the same weight as the first.

Sha found today:
- The hub's footer rule and its full-width section rules (6 cuts in the hub capture) run into the frame edges. Inset them to the wrap.
- On the home page, sharp corners are few (all radius ≥ 6). Radius 8 minimum keeps it so.

**Nine zones** (salience share; centre = content):

| | upper row | middle row | lower row |
|---|---|---|---|
| home, today | .05 .13 .03 | .13 .22 .13 | .09 .14 .07 |
| home, proposed | .21 .07 .03 | .12 .13 .11 | .14 .11 .09 |
| hub, today | .15 .27 .10 | .09 .11 .05 | .10 .08 .05 |
| hub, proposed | .19 .14 .02 | .11 .11 .09 | .13 .11 .09 |

- Today's home is a column: a heavy centre, a weak upper left, weak corners.
- The proposal moves weight to the entry (upper left) and spreads it through the middle and lower rows. The upper right stays light on purpose, so the desktop visual breathes.
- The hub's top centre (the big three-line title) is overloaded at .27. The proposal halves it.

## 5. Information organisation

**Home**, in order:

| # | block | weight | role in the flow |
|---|---|---|---|
| 1 | header (logo, nav, Ask, search) | light | entry |
| 2 | hero: eyebrow, wordmark, title, one lead, Download + Try, note; live desktop on the right | heaviest | entry → first turn → landing |
| 3 | proofs (3) | medium | second turn: the reasons |
| 4 | doors (3 audiences) | medium | turn back: who it is for |
| 5 | features (3 × 2) | light | breathing, detail |
| 6 | apps (Store, Packages links) | light | branch |
| 7 | closing Download band | heavy | second landing |
| 8 | footer | light | ground |

What moves: the desktop demo goes up into the hero. What goes: the second hero paragraph.

**Hub** (store front):

| # | block | weight | role |
|---|---|---|---|
| 1 | header | light | entry |
| 2 | title (2 lines, left), one line of lead | medium | entry |
| 3 | search, 576 × 56, white, elevation 2, with the accent search button, then the category chips | heaviest | landing |
| 4 | kinds as tabs (Apps, Plugins, Extensions): navigation, not three big cards | light | path |
| 5 | Featured, 3 × 2 cards 344 × 216 (icon 60, name, line, trust badge) | medium | the body |
| 6 | "Publish your app" band with its action at the right end | medium | second landing (for makers) |
| 7 | footer, inset rule | light | ground |

What moves: the three kind cards become tabs above Featured. The three-line title becomes two lines.

## 6. Palette and dark mode (all derived from `#7C5CFF`, `tokens/tokens-brand.json`)

| use | today | becomes | note |
|---|---|---|---|
| accent fill under white | `#7C5CFF` (4.35:1) | `#7452F5` (4.92:1) | AA |
| accent text on light ground | — | `#6D48EB` | |
| accent text on dark surfaces | — | `#9181FF` | the fill stays `#7452F5` in both modes |
| light neutrals (bg / surface-2 / text / text-2) | — | `#F1F1FA` / `#EBEBF3` / `#151520` / `#565563` | the base hue, chroma 1-2/21 |
| dark neutrals (bg / surface / surface-2 / text / text-2) | — | `#15151D` / `#292932` / `#383741` / `#F8F8FC` / `#B4B4BB` | |

- **Accents:** gold (earth) for "new" and for badges, cinnabar (fire) for errors only, each at most 1/7 of a screen.
- **Companion:** jade (wood) for success and "verified", which may sit next to violet at any size.
- **Site themes** (the warm theme in `index.css` uses accent `#C72D24`/`#F88A36`): derive them the same way from their own base, with the same value ruler and the same phase rules.

## 7. How to check a change

Capture the page (the capture script and the Playwright setup are in `.claude/v012/brand/site/capture.mjs`), then run:

```
python3 -I design/tools/brand/score.py page.png --kind screen --tree page.json
```

Use it as a gate: a page may not lose points against its current version without the lead's eye saying so.
