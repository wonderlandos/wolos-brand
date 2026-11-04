# Brand screens: the layout of the installer, Setup, the Kit, the Store, Settings, the lock screen and the login window

Status: proposal for the shell worker (branch `wave3/brand`; nothing installed reads it). Date: 2026-11-04.
Lead order 08:28Z: rewrite the layout of every screen on the calculus, improve and do not redo, balance and no extremes.

Read first: `brand-calculus.md` (the calculus), `brand-rules-pack.md` (formulas, layout-tree format). The sibling `brand-ui.md` (DESIGN-ui) owns the symbolic icons, the Dock and the Control Center; this file owns the Kit tokens and the six screens below. Where a Kit value touches the Dock or the Control Center, the Kit value here wins and `brand-ui.md` quotes it.

## 0. How each screen was measured and scored

1. **Measure.** The shell source (`crates/shell/src`: `kit/kit.css`, `kit/assistant.rs`, `kit/widgets.rs`, `ui/installer.rs`, `ui/setup.rs`, `ui/lock.rs`, `login.rs`, `ui/store.rs`, `ui/settings/mod.rs`) gives the CSS values; the golden PNGs (`crates/shell/tests/golden/*.png`: installer and Setup 1280 x 800, lock, login, Settings and Store 900 x 600) give the real pixels.
2. **Draw both with one function.** `tools/screens/scene.py` draws an SVG mock and writes the layout tree (rules-pack format) from the same calls. The current screen is drawn from measured numbers, the proposal from named lengths, so a score compares like with like. The backdrop is the shell's own lock backdrop (cut from `lock-light/dark.png`, `tools/screens/backdrop.py`).
3. **Score.** `tools/brand/score.py --kind screen --tree TREE.json` (eight rules, total = mean). Every board prints the scores of the current mock and the proposal. The golden PNG scored with the same tree is printed on the board as a reference.
4. **Calibration.** Over the 14 screens with a golden (28 light and dark pairs) the mock of the current screen differs from the real golden, scored with the same tree, by +0.1 on average and 2.0 in absolute value (worst +8.3 and -5.7). The scorer's own noise (k-means regions of the wallpaper) is about +-3 on a one-pixel change. A difference under 3 points is not a signal; compare mock against mock, and read the per-rule table, not the total.
5. **Boards.** `screens/NAME/board.png` (current left, proposal right, light above dark, scores at the right). Rebuild: `python3 -I tools/screens/build.py NAME`; send: `python3 .claude/v012/brand/send_screens.py NAME`.

Rules used on every page (rules-pack A-B): 1 fen = 4 px; named lengths 4 8 12 16 24 40 60 84 120 168 240 336 576; door-light ruler 576 (bands of 72; good: cai 0-72, yi 216-288, guan 288-360, ben 504-576); type lines on the fen (11/16 13/20 16/24 24/36 27/40 40/60); one light upper left, shadows at dx:dy = 1:2; planes 21 : 15 : 6; accent (ke) at most 1/7 of a frame; entry at the upper left, landing (the primary action) at the lower right, at least 7:5 heavier than the next mass, with one turn between.

<a id="kit"></a>
## 1. Kit (global tokens, they cascade)

The Kit is `kit.css` plus `kit/widgets.rs` constants plus the theme scale (`shared/src/theme.rs`). Everything in section 1.1 changes once and every screen follows. Section 1.2 lists what stays per screen.

### 1.1 Global (change in `:root`, `SCALE`, `widgets.rs`)

**Colour tokens** (the 13-token contract, values from `tokens/tokens-brand.json`; the accent is derived from the base `#7C5CFF`, k = -1 on the value ruler, 4.9:1 under white):

| token | light now | light new | dark now | dark new |
|---|---|---|---|---|
| surface | #f3f1f8 | #F1F1FA | #1b1924 | #15151D |
| sidebar | rgba(233,231,241,.92) | rgba(235,235,243,.92) | rgba(39,37,49,.92) | rgba(32,32,42,.92) |
| card | #ffffff | #FFFFFF | #2a2834 | #292932 |
| line | rgba(34,27,54,.10) | rgba(21,21,32,.12) | rgba(237,232,255,.10) | rgba(248,248,252,.12) |
| text | #181521 | #151520 | #f6f5fb | #F8F8FC |
| dim | #686575 | #565563 | #aaa7b6 | #B4B4BB |
| accent (fill) | #7c5cff | #7452F5 | #8b6cff | #7452F5 |
| accentText (on the fill) | #ffffff | #FFFFFF | #ffffff | #FFFFFF |
| glass | rgba(245,244,251,.84) | rgba(241,241,250,.84) | rgba(35,33,45,.84) | rgba(41,41,50,.84) |
| control | #e9e9f3 | #EBEBF3 | #393647 | #383741 |
| success | #1c9a6e | #00863C | #5be3b0 | #6BC681 |
| warning | #d9541e | #C06400 | #ff8a55 | #F2944C |
| danger | #cf3a68 | #BB3F27 | #f2678f | #EE7E66 |

Open point for @main (no API change made here): the dark accent now serves two jobs. As a fill (buttons, switches, selection) it is `#7452F5` in both modes; as text or glyph on a dark ground (`button.btn-plain`, `list.sidebar row image`, `.tone-accent`, `.toast button`, `image.accent-icon`) it must be `#9181FF` (4.5:1 on the dark card; the fill would be 2.9:1). Light: fill `#7452F5`, ink `#6D48EB`. Proposal: one derived, non-themable variable `--accent-ink` that the theme generator computes from `accent` (first shade holding 4.5:1 on `card`), used wherever kit.css writes `color: var(--accent)` for text or glyphs. `accentText` on `danger` in dark is the ink `#151520` (white on `#EE7E66` is 2.6:1).

**Spacing** (`widgets.rs` S1..S8, `--space-*` in `SCALE`): 4 8 12 16 24 stay (S1 S2 S3 S4 S6). `S8` = 32 is retired; new `S10` = 40 and `S15` = 60, `S21` = 84. Every use of 32 becomes 40 (page and card insets, empty-state padding, login power row) or 24 (compact). `--inset` 12 and the sheet padding 16 stay.

**Radius** (`SCALE --radius-s/m/l/xl`, `--glass-radius*`; nested radius = outer - padding):

| token / selector | now | new |
|---|---|---|
| --radius-s (controls, menu items, hit rows, sidebar rows, tooltips, thumbs) | 6 | 8 |
| --radius-m / --glass-radius-s (cards, sheets, popovers, lists, modules) | 10 | 12 |
| --radius-l / --glass-radius-m (glass panels, notifications) | 14 / 16 | 16 |
| --radius-xl / --glass-radius (assistant card, widget cards, dock shelf) | 20 / 24 | 24 |
| window | 12 | 12 |
| segmented container / button | 6 / 4 | 8 / 4 (pad 4) |
| switcher strip / ring | 28 / 20 | 24 / 16 |
| capture bar, overview desktop, capture thumb | 14, 10, 10 | 16, 12, 12 |
| pills (switch, badge, toast, lock pill) | 999 | 999 |

**Controls** (three heights, all named: 16, 24, 40):

| control | now | new |
|---|---|---|
| button, entry, dropdown, segmented button (`button.btn`, `entry.*`, `dropdown`) | 24 high, pad 0 12 | 24 high, pad 0 12 (r 8) |
| assistant, login and lock controls (`.assistant-card button.btn`, `.assistant-form-row entry`, `.lock-field`) | 28 | 40 (fields 32 on dense forms: see 3.2) |
| primary action in a foot (Continue, Install, Get Started) | 28, min width by text | 40 high, 168 wide (the landing) |
| switch | 30 x 18, thumb 14, pad 2 | 36 x 24, thumb 20, pad 2 (3:2); compact (`.detail-head`) 24 x 16, thumb 12 |
| slider (`scale.slider`) | trough 4, thumb 16 | trough 4, thumb 16 (unchanged, both named) |
| segmented | container 24 (pad 2, button 20) | container 32 (pad 4, button 24) |
| badge (`label.badge`) | 18 | 16, pad 0 8 |
| list row (`.list-row`) | 40 | 40; `choice-row` 44 -> 40; `hero-row` 64 -> 60; assistant row 36 -> 40 |
| sidebar row (`list.sidebar row`) | 28, pad 0 8 | 24 high with 4 gap (pitch 28), pad 0 8 |
| sidebar width (`SIDEBAR_WIDTH`, scaffold) | 220 | 240 |
| toolbar (`.toolbar`, `KIT_TOOLBAR_HEIGHT`) | 36 | 40 |
| status bar | 24 | 24 |
| icon in a row | 16 | 16; header art 48 -> 40 (symbolic) or 60 (A2) |

**Type** (line on the fen, size = 2/3 line; Inter stays):

| role | now | new |
|---|---|---|
| caption / secondary | 11 | 11 / 16 |
| body | 13 | 13 / 20 |
| heading (`label.heading`) | 15 / 600 | 16 / 24 / 600 |
| title-2 (empty state, searchbar text) | 22 | 24 / 36 / 600 |
| large title (`label.large-title`) | 26 / 700, ls -0.5 | 27 / 40 / 700, ls -0.5 |
| widget figure (`label.display`) | 34 | 35 / 52 / 600 |
| hero title (Setup welcome) | 60 | 56 / 84 / 700 |
| lock clock (`label.lock-time`) | 96 | 80 / 120 / 600 |
| lock date | 22 | 24 / 36 / 500 |

**Light and elevation** (replaces `--glass-shadow`; one light upper left, offsets 1:2, the shadow tint is the ink, never black):

| var | value light | value dark | used by |
|---|---|---|---|
| --elev-1 | 1px 2px 4px rgba(21,21,32,.14) | 1px 2px 4px rgba(2,2,6,.25) | `.module`, `.square-tile`, `.toggle-tile`, `.card-list`, selected segment, switch thumb, slider thumb, primary button |
| --elev-2 | 2px 4px 12px rgba(21,21,32,.18) | 2px 4px 12px rgba(2,2,6,.32) | `.sheet`, menus and popovers, `.glass-panel`, toast, notifications, banners, widget cards |
| --elev-3 | 3px 6px 24px rgba(21,21,32,.24) | 3px 6px 24px rgba(2,2,6,.43) | the assistant card, approval, overview windows, capture thumb, a dragged widget |
| --glass-rim | rgba(255,255,255,.50) top and left only | same at .20 | `inset 1px 1px 0 var(--glass-rim)` replaces `inset 0 1px 0` (gloss on the lit rim only) |

**Sidebar glyph tints** (replace `--tint-wolos/files/web/talk/media/store`; one per group, five phases, fire only for errors): `--tint-water` #007B9E (dark #35BEEE), `--tint-earth` #B07A0C (dark #FFD189), `--tint-base` #6D48EB (dark #9181FF), `--tint-wood` #00863C (dark #6BC681), `--tint-fire` #BB3F27 (dark #EE7E66). The old classes stay as aliases until the panes move: wolos -> base, files -> wood, web -> water, store and media -> earth, talk -> fire.

**List separators.** `.card-list > * { border-top: 1px }` adds a pixel to every row (pitch 41). Replace it by an inset hairline inside the row, 12 px from each side, so the pitch is 40: `background: linear-gradient(var(--line), var(--line)) center top / calc(100% - 24px) 1px no-repeat`, none on the first child. Same for `button.choice-row + button.choice-row`, `button.nav-row` and `.assistant-choice`.

**Hairlines never reach the frame edge** (sha: a straight rule into the border is an arrow): `.toolbar` bottom rule and the `list.sidebar` right rule are inset 12 / 8 as in 6.2; `label.status-bar` top rule inset 12.

Rules: a front plane is never darker than the plane of the same material behind it; no border-and-shadow doubling on cards in light mode (the 1 px line stays, at 12%); separators are inset by 12 and end before the frame edge.

**Measure of a panel** (door-light bands, `calculus.band`; openings of 72 px and more must land in cai, yi, guan or ben on both sides):

| constant (`widgets.rs`) | now | band now | new | band new |
|---|---|---|---|---|
| assistant card, visible (`assistant::CARD` minus the 24 margin) | 552 x 492 (grows to 522) | ben x hai | 576 x 540 | cai x ben |
| default app window `APP_SIZE` | 900 x 600 | guan x cai | unchanged | |
| `SEARCHBAR_WIDTH` | 680 | bing | 576 | cai |
| `FORCE_QUIT` | 360 x 240 | jie x yi | 336 x 240 | guan x yi |
| `ABOUT_WIDTH` | 280 | yi | unchanged | |
| `CONTROL_CENTER_WIDTH` | 320 | guan | unchanged (DESIGN-ui owns the Control Center) | |
| `SHEET_WIDTH` | 360 | jie | 336 | guan |
| `STORE_TILE` | 196 | li | 192 is li too: use 240 x 84 rows (see 7) | |
| `HERO_ICON` (Store details) | 128 | not an opening | 120 | |

### 1.2 Per screen (not global)

Layout, order, alignment, the step label and the door mark are per screen. See sections 2 to 7.

<a id="installer"></a>
## 2. Installer (and the assistant card both assistants share)

Status: APPROVED by the lead, 2026-11-04 08:52Z ("much better"; "approve all proposals, with improvements"). Treat the tables of sections 1.1, 2 and 3 as rules. Later screens follow this form.

Source: `kit/assistant.rs` `Card::build`, `Card::moment`, `CARD`, `ROW`, `ART`; `ui/installer.rs`; `kit.css` "Assistants" block. Goldens `installer-*-1280-*.png`. Mocks and trees: `screens/installer-*/`, drawn by `tools/screens/assistant.py` (`P_CUR` = measured, `P_NEW` = proposal).

### 2.1 What is wrong today (measured)

1. Everything sits on one centred axis: icon, title, subtitle, form, buttons. The entry is the middle of the card and the reading path is a straight line down (no turn).
2. The card is 552 x 492 visible (`CARD` 600 x 540 minus the 24 margin): 492 is in the hai (harm) band, and the account and language pages grow it to 522 and 560, so Back and Continue move between pages although the code says they do not.
3. Radii 6 / 10 / 24, padding 32, control height 28, row 36, bar 6 and gaps 8 / 16 / 24 are off the named lengths (28, 32, 36 are whole fen, unnamed).
4. The primary action is a 28 px chip the same weight as the Back chip; the shadow is black and falls straight down.
5. Nothing says where the person is in the sequence.

### 2.2 The proposal

Keep the glass card, the page order, the copy and the cross-fade. Change the grid inside it.

**Flow.** Entry: the door mark at the screen's upper left, then the app icon and the title at the card's upper left. First turn: the step label at the upper right and the art (or the list) answering at the right. Landing: Continue / Install, 168 x 40 at the card's lower right, the only filled accent control on the page (7:5 over the next mass). Back is a quiet default chip at the lower left.

**Screen chrome (new).** Door mark `brand/wolos-mark(.svg|-on-dark.svg)` 40 x 40 at (60, 60), the word "WolOS" 16/24 600 at x = 112 (60 + 40 + 12), 80% opacity. It is a `GtkPicture` + `GtkLabel` in the assistant window overlay, `halign=start valign=start`, margin 60. It disappears below 640 px width.

**The card.**

| item | now | new |
|---|---|---|
| visible size | 552 x 492 (grows) | 576 x 540, fixed on every question page (cai x ben); the account, language and key pages fit by the body pitch below |
| `CARD` request (with the 24 margin) | (600, 540) | (624, 588) |
| position | centred | centred (the optical centre was tried at 0.45 H and scored lower: the lit lower half of the wallpaper darkens the "shadow side" test; centred is also the calm middle of the nine zones) |
| radius | 24 | 24 |
| padding | 32 | 40 all sides |
| fill, border, rim | glass .84, 1 px hairline, rim top | glass .86, 1 px white 60% (dark 22%), rim on the top and left edge |
| shadow | 0 6 18 .24 + 0 1 4 .16 black | `--elev-3` (3, 6, 24) ink-tinted |
| header layout | centred: icon 48 symbolic, title 26/34 centred, subtitle 13/16 centred | left: app icon 40 (A2, the same on every page of one assistant) at (40, 40); title 27/40 700 at x = 96; step label 11/16 500 dim right-aligned to the content edge, vertically centred on the title row; subtitle 13/20 dim at y = 88 under the icon, 496 wide |
| gaps | icon-title 8, title-subtitle 8, header-body 16..24 | icon-title 16, title row to subtitle 8, header to body 24 |
| body | vertically centred in the free room | vertically centred in the free room (kept), start no earlier than header + 24 |
| foot | pad 32, chips 28 high, gap 8 | pad 40, 40 high; Back 96 wide (left); extra action ("Not Now") 96 wide, plain, 12 left of the primary; primary 168 wide (right); status text between, 13/20 dim |
| foot buttons radius | 6 | 8 |
| primary shadow | none | `--elev-1` |

**Form rows (account, key, language keyboard).**

| item | now | new |
|---|---|---|
| label column | right-aligned, 96 + 8 | left-aligned, 120 + 12 (fields start at x = 40 + 132 = 172) |
| field | 30 high, r 6 | 32 high, r 8, 12 side padding |
| row pitch | 38 | 40 (gap 8) |
| password-hint | 12/16, centred, under the fields | 11/16 dim, left, aligned to the field column, 36 tall block |
| switch row | label then 36 x 22 switch beside it | label left, switch 36 x 24 right-aligned on the content edge |

**List pages (disk, language, Wi-Fi).** Card-list r 12 (was 10), rows 40 (was 36), divider inset 12 each side (was edge to edge), `--elev-1` and a 1 px line at 12%; leading glyph 16 dim at x = 12; text at x = 36; secondary text right; check glyph 16 accent-ink at x = width - 28. Five rows show (`ROWS` = 5), 200 high.

**Moment pages (welcome, installing, done).** Art no longer sits centred above the title. The title row is the entry (icon + title, upper left), a 232 x 232 art tile sits at the right edge of the content (top y = 96), the words stand in a 232 px column at the left under the title (13/20 dim, wrapped by the label), and the foot as above. The progress bar is 8 high, r 4 (was 6, r 3), full content width, with the verb on the left (13/20 500) and the remaining time on the right (13/20 dim), 28 above the bar; the footnote 11/16 dim under it.

**Colour on the card.** Tokens of 1.1 only: card ground `glass`, list ground `card`, field ground `control`, text `text`, labels `dim`, accent used for the primary fill, the check, the focus ring and the progress fill (accent-ink for text and glyphs). No gold or cinnabar on these cards; the only accent is the violet landing (at most 1/7 of the frame).

### 2.3 Length table (px; every one a named length or a whole fen)

| box | x | y | w | h | band / note |
|---|---|---|---|---|---|
| card (visible) | (W-576)/2 | (H-540)/2 | 576 | 540 | cai x ben |
| door mark | 60 | 60 | 40 | 40 | |
| header icon | 40 | 40 | 40 | 40 | |
| title | 96 | 40 | 376 | 40 | 27/40 |
| step label | 472 | 40 | 64 | 40 | 11/16, right |
| subtitle | 40 | 88 | 496 | 20 per line | 13/20 |
| list | 40 | centred | 496 | 40 per row | r 12 |
| field label | 40 | row | 120 | 32 | 13/20 |
| field | 172 | row | 364 | 32 | r 8 |
| switch | 500 | row | 36 | 24 | thumb 20, pad 2 |
| Back | 40 | 460 | 96 | 40 | r 8 |
| Continue | 368 | 460 | 168 | 40 | r 8, elev-1 |
| art tile | 304 | 96 | 232 | 232 | moment pages |
| progress bar | 40 | 412 | 496 | 8 | r 4 |

### 2.4 Pages measured

Begin, language, disk, account and installing are drawn and scored (section 8). The others follow the same card: method / replace / alongside / extras / protect / secure-boot are list pages (2.2 list), edit is a form page, modules is a list page with check rows, done / failed use the moment layout with `keyhole` art at the right.

### 2.5 For the shell worker

`kit/assistant.rs`: `CARD` -> (624, 588); `ROW` 36 -> 40; `ART` 96 -> 40 (header icon, A2 app icon via `w::icon("wolos-installer", 40)`); `ART_L` 160 -> 232 (moment art tile); `Card::build`: head becomes an `hbox` (icon, title, step label with `hexpand` spacer) over the subtitle, `halign=start`; foot buttons `width_request` 96 / 168; `Card::moment`: stage art goes to an `Overlay` child at the right, words in a 232 px column. `kit.css`: `.glass-panel.assistant-card { padding: 40px; box-shadow: var(--elev-3), inset 1px 1px 0 var(--glass-rim); }`, `.assistant-card button.btn { min-height: 40px }`, `.assistant-form-row entry ... { min-height: 32px }`, `.assistant-progress ... { min-height: 8px; border-radius: 4px }`, `button.assistant-choice .list-row.assistant-row { min-height: 40px }`, `label.assistant-step { font-size: 11px; font-weight: 500; color: var(--dim) }`. The step counts come from `Step`/`STEPS` in `setup.rs` and the installer's own step list.

<a id="setup"></a>
## 3. Setup

Status: APPROVED by the lead, 2026-11-04 (with the installer, same card).

Source: `ui/setup.rs`, `kit/assistant.rs` `welcome`, goldens `setup-*-1280-*.png`. Setup uses the same card; section 2 applies in full, with these differences.

| item | now | new |
|---|---|---|
| header icon | symbolic glyph per page | the door mark (40) on every card of Setup (the installer uses the installer icon) |
| steps | none | "N of 6" |
| welcome title | 60/ (72 line) 700, left margin 72 | 56 / 84 700, left margin 84 (`.hero-column { margin-left: 84px }`, `HERO_COLUMN` 520 -> 480) |
| welcome subtitle | 18 | 16/24 at 86% |
| welcome action | pill 36 high, pad 0 28, 14 px | pill 40 high, 168 wide, 14 px, `--elev-1`; stays on the left under the words |
| welcome chrome | none | door mark + "WolOS" at (60, 60) |
| Wi-Fi rows | 36 | 40, lock glyph 16 dim at the right, check at the far right |
| appearance previews | 112 x 78, r 6, gap 20 / 28 | 120 x 84 (7:5), r 8, column gap 28, row gap 40, selected ring 3 px accent at 3 px off |
| done | stage art centred, "Get Started" 100 x 28 | moment layout (art right, words left), "Get Started" 168 x 40 at the lower right |

Welcome keeps the full-bleed art and anchors it as today (cover, bottom right): the art is the entry and the answer, the words sit on its calm left.

<a id="lock"></a>
## 4. Lock screen

Status: proposal (board sent 2026-11-04; lead said "approve all proposals, with improvements", so build it; same form as sections 2 and 3).

Source: `ui/lock.rs` (`body`, `lock_screen`), `kit/widgets.rs` (`clock_header`, `UserPanel`, `AVATAR_XL`, `LOCK_FIELD_*`), `kit.css` "Lock / login". Goldens `lock-*.png` (900 x 600). Mocks: `screens/lock/` (`tools/screens/lockscreen.py`).

### 4.1 What is wrong today

The clock, the avatar and the pill are all on the centre axis (x = 450 of 900): a straight vertical shot with the entry in the middle top, and a gap of 170 px between the date and the avatar. The pill (200 x 28) is the smallest, weakest mass on the page although it is the one action. The shadows are black and fall straight down.

### 4.2 The proposal

Same elements, anchored on the diagonal. Entry: the clock and date at the upper left, 84 from the edges. Landing: the user panel (avatar, name, pill) at the lower right, 84 from the right edge and 60 from the bottom. The wallpaper between them is the calm centre of the nine zones.

| item | now (900 x 600) | new |
|---|---|---|
| `.lock-body` padding | 56 0 32 0, everything centred | 60 84 60 84; clock `halign=start valign=start`; user panel `halign=end valign=end` |
| clock `label.lock-time` | 96 / 600, ls -2, digits 78 tall, centred, top of digits y = 75 | 80 / 120 line, 600, ls -2, left, line box y = 60..180 |
| date `label.lock-date` | 22 / 500, centred, y = 174 | 24 / 36, 500, left, line box y = 180..216 |
| avatar (`AVATAR_XL`) | 96, centre x = 450, y = 377 | 84 (zucai), centre x = W - 84 - 120 = 696, y = 348 |
| avatar to name gap | 12 (S3) | 12 (S3) |
| name `label.lock-name` | 15 / 600 | 16 / 24 / 600, line box y = 444..468, width 240 |
| pill (`LOCK_FIELD_WIDTH` x `LOCK_FIELD_HEIGHT`) | 200 x 28, `.lock-pill` min-height 28, padding 0 4 0 12 | 240 x 40 (r 20), min-height 40, padding 0 6 0 16, at y = 476..516 |
| submit disc (`button.lock-submit`) | 20 | 28 (a 6 px ring inside the pill) |
| peek glyph to disc (`LOCK_PILL_GAP`) | 6 | 8 |
| pill ground | light white 62% / dark white 14%, border white 85% / 30% | light white 70% / dark white 14%, border white 90% / 30% |
| pill shadow | 0 4 16 rgba(40,30,90,.16) | `--elev-2` |
| message `label.lock-message` | 13 / 500, min-height 18 | 13 / 20, y = 520..540 under the pill |
| text colours | light #1c1838 / dark white, black text-shadow | light `text` #151520 / dark `text` #F8F8FC; shadow only in dark, `1px 2px 8px rgba(2,2,6,.30)` |
| scrim | light white 22%, dark vertical 18% / 0 / 22% | unchanged |
| avatar tones | `avatar-tone-*` gradients | unchanged |

Restart row (`lock_screen_with_restart`): under the message, same right edge, 40 high plain chip.

<a id="login"></a>
## 5. Login window

Status: proposal (same message as the lock screen).

Source: `ui/lock.rs` `Login`, `login.rs`, goldens `login-*.png`. Mocks: `screens/login/`.

| item | now | new |
|---|---|---|
| clock and date | centred | as the lock screen (upper left) |
| user tiles `hbox(S8)` | centred, avatar 96, pitch 160 (tile 128 + gap 32), tile padding 12 16, name 15 / 600 | right-aligned (`halign=end`, last tile ends 84 from the edge), avatar 84, tile `min-width: 120`, padding 16, gap 24 (S6), pitch 144, name 16 / 24 / 600; the tile row top y = 348 |
| tile radius / hover | 16 / white 12% | 16 / white 12% (unchanged) |
| password view (after a pick) | the pill under the avatar, centred | the lock panel of section 4.2, same place as the tile row's last tile |
| power row `.login-power` | centred, `hbox(S8)`, margin-top 32, circles 32 (`lock-round`), caption 11 | lower left (`halign=start`, margin-left 84, bottom 60), `hbox(S10)` (gap 40), circles 40 with `--elev-1`, caption 11 / 16 under, circle y = 476..516, captions y = 524..544 |
| refusal caption under the row | centred | left, same column |
| `.empty-state` (no accounts) | 32 padding | 40 padding |

<a id="settings"></a>
## 6. Settings shell (sidebar and pane frame)

Status: proposal (board sent 2026-11-04; "approve all proposals, with improvements": build it).

Source: `ui/settings/mod.rs` (`SIDEBAR`, `build`), `kit/widgets.rs` `AppWindow` (`sidebar_search`, `source-gap`), `kit.css` `.toolbar`, `list.sidebar`, `.page`, `.card-list`, `.list-row`, `label.large-title`. Goldens `settings-*-wide-*.png` (900 x 600). Mocks: `screens/settings-shell/` (`tools/screens/settingspages.py`, the Sound pane as the sample). The panes themselves keep their order and copy; this is the frame every pane inherits.

### 6.1 What is wrong today (measured on `settings-sound-wide-light.png`)

1. The sidebar border and the toolbar border run edge to edge: two long straight lines into the frame edge (sha: arrows).
2. Cards fill the pane (621 px at 900): a width in the bing/jie region of the ruler; at 1280 the rows run 1000 px, too long to scan.
3. Rows 41 px apart (40 + a 1 px border that adds to the height), section headings 15, large title 26: all off the fen.
4. Six saturated hues down the sidebar (pink, gold, violet, teal, blue, orange): the eye has no group to read, and fire/earth hues exceed the 1/7 accent share in a column of 17.
5. The search field is 28 high (an unnamed length), radii 6 and 10.

### 6.2 The proposal (px at 900 x 600; the shell scales by layout, not by number)

| item | now | new |
|---|---|---|
| toolbar `.toolbar` / `KIT_TOOLBAR_HEIGHT` | 36, border-bottom full width | 40; hairline inset 12 each side (a gradient strip `background-size: calc(100% - 24px) 1px; background-position: center bottom`) |
| sidebar width (`SIDEBAR_WIDTH`, scaffold) | 220 (+8 padding: 228 on screen) | 240 total, 1 px hairline at its right edge inset 8 from the toolbar and from the bottom (gradient strip, no `border-right`) |
| `list.sidebar` padding | 8 | 12 |
| sidebar search entry | 28 high, x 8..220 | 32 high, r 8, x 12..228, glyph 16 accent-ink at x = 10, placeholder at x = 34 |
| sidebar row (`list.sidebar row`) | min-height 28, margin 0, r 6, padding 0 8 | min-height 24, `margin: 0 0 4px`, r 8, padding 0 8 (pitch stays 28, so the density of the list does not change; the hover and selected pills are 24 high with 4 between) |
| row glyph / gap | 16 / 8 | 16 / 8 |
| group gap (`.source-gap`) | 12 | 16 (pitch 28 + 12 extra = 40 -> 28 + 16 - 4 = 40: the group step stays 40) |
| selected row | accent 18%, text colour, label 400 | accent 18%, r 8, label 500 |
| glyph tints | `--tint-wolos/files/web/talk/media/store` per row (6 hues) | one tint per group, four phases: connect = water, alerts = earth, system = base violet, safety and power = wood. Light: water #007B9E, earth #B07A0C, base #6D48EB, wood #00863C. Dark: water #35BEEE, earth #FFD189, base #9181FF, wood #6BC681. New classes `tint-water`, `tint-earth`, `tint-base`, `tint-wood`; `tint-talk` (fire #BB3F27 light, #EE7E66 dark) is kept for errors only and does not appear in the sidebar |
| pane column | full width minus 24 each side | `min(pane - 48, 576)`, centred in the pane (576 = one ruler, cai band); at 900 this is 576 wide at x = 281 |
| page padding `.page` | 8 24 24 24 | 4 24 24 24 above the title; title box 40 high |
| page title `label.large-title` | 26 / 700 | 27 / 40 / 700, box y = 44..84 |
| title to first card | 17 | 16 |
| section heading `label.heading` | 15 / 600, 22 line | 16 / 24 / 600; 24 above (after a card), 8 below |
| card `.card-list` | r 10, 1 px line, no shadow | r 12, 1 px line, `--elev-1` |
| row separator | `border-top: 1px` (adds 1 px: pitch 41) | gradient hairline inset 12 each side inside the row (pitch 40): `.card-list > * { background: linear-gradient(var(--line), var(--line)) center top / calc(100% - 24px) 1px no-repeat }`, none on the first |
| row heights | 40; two-line 51; slider 54 | 40; two-line 48 (13/20 + 11/16 + 6 + 6); slider 60 (label 20, track, captions 16) |
| row inset | glyph x 12, text x 40 (unchanged), value right 12 | unchanged |
| switch | 30 x 18 | 36 x 24 |
| slider | trough 4, thumb 16, shadow black 0 1 3 | trough 4, thumb 16, `--elev-1` |

Narrow window (< `NARROW` 640): sidebar collapses as today; the column becomes `pane - 48`.

### 6.3 Length table at 900 x 600 (px)

| box | x | y | w | h | band |
|---|---|---|---|---|---|
| toolbar | 0 | 0 | 900 | 40 | |
| sidebar | 0 | 40 | 240 | 560 | |
| search | 12 | 48 | 216 | 32 | |
| first row | 12 | 92 | 216 | 24 | pitch 28 |
| title | 281 | 44 | 400 | 40 | |
| card 1 | 281 | 100 | 576 | 80 | cai x bing (two 40 rows; under a full opening, so not tested) |
| heading "Output" | 281 | 204 | 300 | 24 | |
| card 2 | 281 | 236 | 576 | 240 | cai x yi (both good bands; 240 is a named length) |

<a id="store"></a>
## 7. Store

Status: proposal (board sent 2026-11-04; build it with the same rules as the approved screens).

Source: `ui/store.rs` (`discover`, `hero`, `grid`, `shelf`), `ui/store/details.rs`, `kit/widgets.rs` (`AppTile`, `hero_banner`, `STORE_TILE`, `HERO_ICON`, `wrap_row`), `kit.css` "App Store". Goldens `store-discover-wide-*.png`, `store-details-native-wide-*.png` (900 x 600). Mocks: `screens/store-discover/`, `screens/store-details/` (`tools/screens/storepages.py`; content uses WolOS's own apps with Type A2 icons). The window frame, sidebar and column are section 6.

### 7.1 What is wrong today (measured)

1. Hero 623 x 190 (bing x jie, unnamed), padding 28 / 32, radius 10; the headline is the same 26 as the page title above it, so two titles compete; the Get pill (80 x 24) is the landing but it is small and white on a busy art.
2. Tiles 304 wide at pitch 320 (the 196 minimum plus a 16 gap): not on a name; the Get pill is 80 x 24 and its text weight 700 pulls as much as the app name.
3. Section heading is the 13 px bold `title` role (same size as the tile names); the hierarchy is carried by position only.
4. The sidebar uses six hues (see 6.1).
5. The detail page has the app icon at 128, the Get pill is a quiet chip although it is the only action on the page.

### 7.2 The proposal

| item | now | new |
|---|---|---|
| frame, sidebar, toolbar, title | section 6 | section 6 (same numbers) |
| sidebar glyph tints | per row (6 hues) | per group: categories (Discover, Create, Work, Play, Develop) earth `#B07A0C` / dark `#FFD189` (the Store's own phase, as its A2 icon); Kits and Plugins base violet; Updates wood; Community water |
| column | pane - 48 (623 at 900) | `min(pane - 48, 840)`, centred; 576 at 900 (the ruler, cai); 840 when the window is wide (yi) so 3 tiles fit |
| hero `.hero-banner` | 623 x 190, r `glass-radius-s` 10, padding 28 32 | 576 x 216 (cai x yi), r 16, padding 24 40, content centred vertically; at 840 wide it is 840 x 216 (yi x yi) |
| hero gradient | 135deg, app colour 1 -> 2 | 135deg, light end at the upper left (the light) -> deep end at the lower right; the pair comes from the app's two colours, snapped to the phase: water lake #007B9E -> #1C3A8A for Photos |
| hero text | eyebrow 11/600 .4, headline `large-title` 26, subhead 13, Get 80 x 24 | eyebrow 11/16 600 ls .4 at 80%, headline 27/40 700, subhead 13/20 at 92% in a 340 px column, Get white pill 120 x 40 (r 20, text ink 13/600, `--elev-1`) = the landing |
| hero art | `HERO_ICON` 128 | 120 at the right, 40 from the edge, vertically centred |
| shelf heading | `title` 13/600 | `label.heading` 16/24 600; 24 above, 8 below |
| tile grid `wrap_row(S4, 3)` | gap 16, tiles stretch (304 at 900) | gap 24 (S6); `STORE_TILE` (minimum width) 196 -> 264: a 576 column fits 2 tiles (276 each), an 840 column fits 3 (264 each) |
| tile | icon 48, name 13/600, summary 11, Get 80 x 24, no padding, pitch 80 | icon 48 at x = 0, name 13/20 600 at x = 60, summary 11/16 dim, Get pill 60 x 24 (r 12), text 13/600 accent-ink; tile box 72 high, pitch 80 |
| Get pill `button.get-button` | min-width 56, text 700 | 60 x 24, text 600, ground `control` |
| detail page icon | 128 | 120 at x = 0, title block at x = 144 (120 + 24) |
| detail page Get | quiet chip 80 x 24 | primary pill 120 x 40, accent, `--elev-1` (it is the only action) |
| detail info card | r 10, rows 41 | r 12, `--elev-1`, rows 40, inset hairline (section 6.2) |
| detail section heading | 15/600 | 16/24 600 |

### 7.3 Length table at 900 x 600 (px)

| box | x | y | w | h | band |
|---|---|---|---|---|---|
| column | 281 | 44 | 576 | | cai |
| title | 281 | 44 | 400 | 40 | 27/40 |
| hero | 281 | 100 | 576 | 216 | cai x yi |
| hero Get | 321 | 256 | 120 | 40 | |
| hero art | 697 | 148 | 120 | 120 | |
| heading "Essentials" | 281 | 340 | 300 | 24 | |
| tile 1 | 281 | 372 | 276 | 72 | yi |
| tile 2 | 581 | 372 | 276 | 72 | |
| tile row pitch | | | | 80 | |
| tile Get | tile x + 216 | tile y + 24 | 60 | 24 | |

Wide (>= 888): the column is 840 and the tiles 264 x 72 in 3 columns (gap 24); below 576 the grid is one column.

### 7.4 For the shell worker

`widgets.rs`: `STORE_TILE` 196 -> 264 (min width), `HERO_ICON` 128 -> 120, `wrap_row` gap S4 -> S6 for the Store grids; `hero_banner`: hbox spacing S4 -> S6, text column `width_request(340)`, action `min-height 40`; `AppTile::new`: icon box 48, `hbox(S3)`, summary `set_lines(2)` stays; `kit.css`: `.hero-banner { border-radius: 16px; padding: 24px 40px }`, `.hero-banner button.get-button { min-height: 40px; min-width: 120px; border-radius: 20px }`, `button.get-button { min-width: 60px; min-height: 24px; border-radius: 12px }`, `button.get-button label { font-weight: 600 }`, `.store-grid { margin-top: -8px }` stays. The column clamp (576 / 840) is the same clamp as the Settings pane (6.2).

<a id="scores"></a>
## 8. Scores (mock of the current screen -> proposal; `tools/screens/report.py`)

Totals, mean of the eight rules, kind screen, with the layout tree. Golden = the real PNG scored with the mock's tree.

| screen | light: now | light: proposal | light: golden | dark: now | dark: proposal | dark: golden |
|---|---|---|---|---|---|---|
| installer-account | 76.2 | 78.6 | 81.9 | 75.0 | 79.3 | 76.2 |
| installer-begin | 78.6 | 85.4 | 75.2 | 78.5 | 80.2 | 75.2 |
| installer-disk | 82.2 | 82.1 | 81.2 | 76.6 | 78.7 | 75.3 |
| installer-installing | 77.6 | 80.6 | 77.3 | 77.9 | 82.9 | 76.0 |
| installer-language | 81.3 | 86.2 | 82.3 | 77.0 | 79.3 | 76.1 |
| kit | 78.3 | 79.4 | - | 82.6 | 82.6 | - |
| lock | 77.9 | 80.4 | 78.0 | 82.9 | 81.2 | 83.4 |
| login | 82.2 | 83.0 | 79.5 | 83.6 | 82.4 | 84.0 |
| settings-shell | 68.5 | 74.5 | 67.1 | 67.6 | 73.0 | 66.6 |
| setup-appearance | 74.8 | 80.2 | 76.4 | 76.9 | 80.8 | 76.2 |
| setup-done | 81.8 | 83.6 | 73.5 | 77.8 | 76.8 | 80.8 |
| setup-welcome | 76.0 | 78.0 | 74.4 | 76.0 | 78.8 | 74.7 |
| setup-wifi | 77.4 | 82.2 | 79.9 | 76.5 | 77.8 | 75.3 |
| store-details | 66.5 | 66.4 | 69.0 | 70.5 | 75.0 | 74.9 |
| store-discover | 59.7 | 69.0 | 61.5 | 75.0 | 79.1 | 76.9 |
| **mean** | 75.9 | 79.3 | | 77.0 | 79.2 | |

Reading it:

- **proportion** rises on 28 of 30 (mean +18 points: tree lengths on named fen, openings on the good bands); it is the rule the layout changes most. Two do not: the lock screen in dark (equal) and the Settings shell in light (59 > 52: the 281 px column offset and the 216 / 32 sidebar widths are whole fen, not named).
- **density** rises on 22 of 30 (ground / second / first plane nearer 21 : 15 : 6, fewer off-name gaps).
- **forms** and **qi** are mostly equal or up; the Store's Discover page loses qi in light (the hero is a deep mass in the middle: entry 0) and the details page loses forms.
- **light** falls on 21 of 30 where the proposal swaps the shipped black `0 6 18` shadow for the brand elevations (1:2, ink-tinted, 4/12/24 blur): the pixel test looks for a darker band 25 px below the plane, and the softer shadow gives less. The offset 1:2 is the brand's own rule; the eye decides, and the shadows are the ones the lead approved on the installer.
- **sha** stays near 77 on card pages (the card's straight edges longer than half the frame count as cuts: structural) and near 0-20 on window screens (long card edges, rows): the inset hairlines lift it by 17-23 points on the Settings shell.
- **palette** is 100 on every screen.

Per rule (now > proposal):

| screen | mode | qi | sha | forms | zones | palette | light | proportion | density | total |
|---|---|---|---|---|---|---|---|---|---|---|
| installer-account | light | 96 > 96 | 77 > 77 | 73 > 77 | 97 > 96 | 100 > 100 | 60 > 55 | 41 > 57 | 66 > 71 | 76.2 > 78.6 |
| installer-account | dark | 100 > 100 | 78 > 78 | 77 > 88 | 78 > 78 | 100 > 100 | 60 > 58 | 45 > 64 | 62 > 69 | 75.0 > 79.3 |
| installer-begin | light | 86 > 96 | 79 > 77 | 97 > 74 | 94 > 95 | 100 > 100 | 60 > 80 | 31 > 70 | 82 > 92 | 78.6 > 85.4 |
| installer-begin | dark | 100 > 100 | 79 > 78 | 87 > 84 | 97 > 98 | 100 > 100 | 58 > 33 | 35 > 70 | 71 > 78 | 78.5 > 80.2 |
| installer-disk | light | 100 > 96 | 78 > 78 | 94 > 93 | 97 > 96 | 100 > 100 | 73 > 52 | 35 > 63 | 81 > 78 | 82.2 > 82.1 |
| installer-disk | dark | 100 > 100 | 79 > 79 | 88 > 88 | 78 > 77 | 100 > 100 | 62 > 57 | 34 > 66 | 73 > 63 | 76.6 > 78.7 |
| installer-installing | light | 100 > 100 | 78 > 78 | 84 > 77 | 95 > 96 | 100 > 100 | 56 > 54 | 34 > 64 | 74 > 75 | 77.6 > 80.6 |
| installer-installing | dark | 100 > 100 | 79 > 79 | 80 > 86 | 97 > 97 | 100 > 100 | 60 > 59 | 36 > 63 | 71 > 78 | 77.9 > 82.9 |
| installer-language | light | 96 > 96 | 78 > 78 | 85 > 88 | 97 > 96 | 100 > 100 | 65 > 79 | 45 > 61 | 85 > 92 | 81.3 > 86.2 |
| installer-language | dark | 100 > 100 | 78 > 79 | 76 > 88 | 77 > 77 | 100 > 100 | 60 > 47 | 47 > 66 | 77 > 78 | 77.0 > 79.3 |
| kit | light | 96 > 96 | 98 > 98 | 89 > 89 | 76 > 76 | 100 > 100 | 82 > 73 | 35 > 47 | 51 > 57 | 78.3 > 79.4 |
| kit | dark | 100 > 96 | 98 > 98 | 85 > 77 | 77 > 77 | 100 > 100 | 82 > 79 | 44 > 46 | 75 > 88 | 82.6 > 82.6 |
| lock | light | 96 > 100 | 99 > 99 | 55 > 80 | 88 > 72 | 100 > 100 | 64 > 73 | 46 > 52 | 76 > 68 | 77.9 > 80.4 |
| lock | dark | 100 > 100 | 99 > 99 | 80 > 82 | 94 > 77 | 100 > 100 | 61 > 60 | 50 > 49 | 80 > 82 | 82.9 > 81.2 |
| login | light | 97 > 100 | 99 > 99 | 95 > 85 | 92 > 93 | 88 > 88 | 59 > 67 | 52 > 60 | 77 > 72 | 82.2 > 83.0 |
| login | dark | 94 > 96 | 99 > 99 | 94 > 88 | 95 > 96 | 88 > 88 | 75 > 49 | 57 > 60 | 68 > 84 | 83.6 > 82.4 |
| settings-shell | light | 92 > 96 | 0 > 17 | 88 > 85 | 97 > 97 | 100 > 100 | 80 > 85 | 59 > 52 | 31 > 63 | 68.5 > 74.5 |
| settings-shell | dark | 96 > 96 | 0 > 23 | 85 > 88 | 77 > 77 | 100 > 100 | 63 > 59 | 60 > 67 | 59 > 74 | 67.6 > 73.0 |
| setup-appearance | light | 78 > 96 | 79 > 79 | 78 > 87 | 92 > 92 | 100 > 100 | 68 > 54 | 24 > 59 | 80 > 75 | 74.8 > 80.2 |
| setup-appearance | dark | 93 > 92 | 79 > 79 | 100 > 100 | 93 > 94 | 100 > 100 | 58 > 56 | 25 > 55 | 68 > 71 | 76.9 > 80.8 |
| setup-done | light | 100 > 96 | 80 > 79 | 84 > 76 | 91 > 91 | 100 > 100 | 81 > 82 | 42 > 72 | 78 > 73 | 81.8 > 83.6 |
| setup-done | dark | 83 > 79 | 80 > 79 | 89 > 87 | 96 > 96 | 100 > 100 | 61 > 35 | 42 > 67 | 71 > 71 | 77.8 > 76.8 |
| setup-welcome | light | 75 > 75 | 98 > 98 | 100 > 100 | 78 > 78 | 88 > 88 | 69 > 54 | 43 > 63 | 57 > 69 | 76.0 > 78.0 |
| setup-welcome | dark | 75 > 75 | 98 > 98 | 100 > 100 | 78 > 78 | 88 > 88 | 69 > 68 | 44 > 62 | 56 > 62 | 76.0 > 78.8 |
| setup-wifi | light | 96 > 96 | 79 > 79 | 86 > 92 | 96 > 95 | 100 > 100 | 56 > 55 | 32 > 62 | 74 > 78 | 77.4 > 82.2 |
| setup-wifi | dark | 100 > 100 | 79 > 79 | 88 > 77 | 77 > 76 | 100 > 100 | 59 > 57 | 36 > 70 | 73 > 63 | 76.5 > 77.8 |
| store-details | light | 96 > 96 | 18 > 38 | 64 > 49 | 92 > 76 | 100 > 100 | 73 > 62 | 54 > 58 | 34 > 51 | 66.5 > 66.4 |
| store-details | dark | 100 > 100 | 18 > 23 | 76 > 72 | 73 > 91 | 100 > 100 | 75 > 81 | 56 > 61 | 66 > 72 | 70.5 > 75.0 |
| store-discover | light | 81 > 70 | 37 > 68 | 26 > 35 | 94 > 94 | 100 > 100 | 44 > 62 | 45 > 54 | 51 > 69 | 59.7 > 69.0 |
| store-discover | dark | 100 > 94 | 38 > 52 | 78 > 81 | 97 > 96 | 100 > 100 | 67 > 71 | 50 > 67 | 70 > 72 | 75.0 > 79.1 |

