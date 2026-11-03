# Atlas chrome: the WolOS tokens on the browser

Rule of the HIG (hig.md section 2): colours, spacing, radius, type and icon sizes are tokens, never literals. Atlas adds no token and no colour. This file says which token paints which part of the browser. The frames `atlas-newtab` and `atlas-firstrun` (this folder) are drawn from it with the values of the two built-in themes (`crates/core/src/theme/builtin/wol-light.json` and `wol-dark.json`); `tools/brand/atlas_check.py` fails when the constants in the generator drift from those files.

## 1. The tokens in use

The 13 theme tokens (`shared::theme::TOKENS`), their CSS variables (kebab-case, `--accent-text`), and what they resolve to in the built-in themes:

| Token | Variable | Light (`wol-light`) | Dark (`wol-dark`) |
|---|---|---|---|
| `surface` | `--surface` | `#F3F1F8` | `#1B1924` |
| `sidebar` | `--sidebar` | `rgba(233,231,241,0.92)` | `rgba(39,37,49,0.92)` |
| `card` | `--card` | `#FFFFFF` | `#2A2834` |
| `line` | `--line` | `rgba(34,27,54,0.10)` | `rgba(237,232,255,0.10)` |
| `text` | `--text` | `#181521` | `#F6F5FB` |
| `dim` | `--dim` | `#686575` | `#AAA7B6` |
| `accent` | `--accent` | `#7C5CFF` | `#8B6CFF` |
| `accentText` | `--accent-text` | `#FFFFFF` | `#FFFFFF` |
| `glass` | `--glass` | `rgba(245,244,251,0.84)` | `rgba(35,33,45,0.84)` |
| `control` | `--control` | `#E9E9F3` | `#393647` |
| `success` | `--success` | `#1C9A6E` | `#5BE3B0` |
| `warning` | `--warning` | `#D9541E` | `#FF8A55` |
| `danger` | `--danger` | `#CF3A68` | `#F2678F` |

Fixed scales (not themable): spacing 4, 8, 12, 16, 24 (`--space-1` to `--space-6`); radius 6 controls, 10 cards, 14 large, 20 extra large (`--radius-s/m/l/xl`); the window is 12 (`--window-radius`); type Inter 13 body, 11 secondary, 15 heading, 26 large title (hig.md section 2; `shared::theme::scaffold`); motion 150, 250, 400 ms (`--motion-fast/normal/slow`). Selection, from the design palette (`tokens/colors.json`), is `accent` at 22% (light) and 30% (dark).

Two places the tokens reach, and how:

- Native chrome (toolbar, sidebar, omnibox, menus). Today the browser follows the theme through the system GTK theme `WolOS-<id>`, light/dark and the accent preset from the settings portal, and the window buttons from the compositor (crates/core/src/theme, the browser generator). That carries window colours only. The rest of this file is the target look; how each row reaches the browser is for the people who build it.
- Internal pages (new tab, first run, error pages, settings, history). These are web pages Atlas serves itself, so they use the theme CSS variables above directly (the same `:root` block `ThemeCatalog::css()` writes) and never a hex value. A page built this way follows a theme change with no extra code.

## 2. Window and toolbar

| Part | Size | Fill | Other |
|---|---|---|---|
| Compositor strip | 28 px | shell (`menubar` of the design palette) | Not Atlas's: Atlas shows its menus here (File, Edit, View, History, Bookmarks, Window). |
| Window | radius 12 | `surface` | 1 px `line` hairline inside; the shadow is the compositor's. |
| Toolbar | 36 px, draggable | `glass` | 1 px `line` below. Order, left to right: sidebar toggle, back, forward, reload, the omnibox centred in the window, then at most four actions: privacy, bookmark, downloads, menu. Max 5 (hig.md section 1). |
| Toolbar button | glyph 16, hit area 28 x 28 | none | [hover and pressed states are a proposal: neither the HIG nor the 13 tokens define them] Symbolic icons, `text`; forward when there is nowhere to go is `dim`; hover paints `control`; pressed paints `accent` at 22%; the privacy glyph is `accent` while Do Not Track is on. Every icon-only button has a tooltip and an accessible name. |
| Sidebar toggle | 16 | `text` | `sidebar-show-symbolic`; shortcut Super+Alt+S (hig.md section 1). |

Icons (all from the theme's symbolic set, 16 px grid, `currentColor`): `sidebar-show`, `go-previous`, `go-next`, `view-refresh`, `preferences-system-privacy`, `starred` / `non-starred`, `folder-download`, `open-menu`, `system-lock-screen`, `system-search`, `tab-new`, `web-browser`, `user-home`, `mail-unread`, `text-x-generic`, `user-bookmarks`. The brand glyph of Atlas for 16 px (menu, tab of an internal page, notification) is a follow-up; until the lead picks a direction `web-browser-symbolic` stands in.

## 3. Tabs

Default: the sidebar of the HIG. The tab list is a navigation list, which is what a sidebar is for (hig.md section 1): 220 px, collapsible with Super+Alt+S, remembered per window.

| Part | Size | Token |
|---|---|---|
| Sidebar | 220 px wide | `sidebar`; 1 px `line` on its right edge |
| Section header (Pinned, Today, a group's name) | 11 px, 600, small caps | `dim` |
| Tab row | 28 px high, 8 px inset, radius 6 | none (idle); `text` title 13 px, `dim` for a group's collapsed summary |
| Tab icon | 16 | the page's favicon, or the symbolic `web-browser`; `dim` when idle |
| Selected tab | row | accent tint pill (`accent` at 22% / 30%), title weight 500, icon `accent`; never `dim` text on the pill (3.9:1 in light) |
| Loading | icon replaced by a 16 px Spinner after 150 ms (hig.md section 1) | `accent` |
| Playing audio | speaker glyph right of the title | `dim`; `accent` when this tab is the one playing |
| Close | `window-close-symbolic`, 16, shown on hover and on the selected row | `dim`, `text` on hover |
| New tab | footer row, 28 px, `tab-new` + "New tab" + "Ctrl T" in 11 px `dim` | separated by a `line` rule |

Fallback for a window under 720 px wide, or with the sidebar collapsed and the person asking for tabs on top: a strip of 28 px under the toolbar, tabs 28 px high with radius 6, minimum width 96 px, the selected tab `card` with `text`, others `glass` with `dim`, a 1 px `line` under the strip, close and new-tab glyphs as above. The strip is a fallback, not a second design: same tokens, same rows.

## 4. Omnibox

| State | Look |
|---|---|
| Idle | 26 px high, radius 6 (`--radius-s`), `control` fill, 1 px `line`, centred in the toolbar, 560 px wide and shrinking to the room; leading glyph 16 `dim` (`system-search`, or `system-lock-screen` on a secure page); text 13 px `text`, placeholder `dim`: "Search or enter an address". |
| Hover | border unchanged, fill one step toward `card`. |
| Focus | 2 px ring in `accent` at 90%, 2 px outside the field; the text selects. Ring contrast against the toolbar is 3.6:1 light, 3.2:1 dark (target 3:1). |
| Loading | a 2 px bar along the bottom edge in `accent`, linear, driven by the value; indeterminate after 150 ms is a Spinner in the glyph slot, never a shimmer. |
| Secure page | the lock glyph `dim`, the host in `text` and the rest of the address in `dim`. |
| Not secure | `security-low-symbolic` in `warning` and the words "Not secure" in `text` (colour never alone; `warning` on `card` is 4.0:1 light, so the word is not coloured). |
| Do Not Track | the privacy button, `preferences-system-privacy` in `accent`, tooltip "Do Not Track is on". Do Not Track asks sites not to follow the person; they can ignore it, so no text near it says "blocked". |
| Suggestions | a popover under the field, `card`, radius 10, the field's width, rows 28 px, the selected row the accent pill; popover blur is 30 px (`blur.popover`). |

## 5. New tab page (frame: `atlas-newtab.svg`)

An internal page on `surface`, centred column, nothing it does not need. Spacing from the scale only.

| Part | Spec | Token |
|---|---|---|
| Badge | the Atlas badge at 72 px, 120 px below the toolbar | brand asset |
| Title | "Atlas", 26 px bold, centred | `text` |
| Search field | 560 x 40, radius 10, leading `system-search` 16 | `card` with 1 px `line`; placeholder `dim`. It takes focus, so the toolbar's omnibox shows the focus ring. |
| Pinned | heading 15 px 600; cards 96 x 88, 16 px gap, radius 10; a 32 px tile in the category colour of the target (`icon.categories`: web, talk, files, media, store, system) with a white 16 px symbolic glyph; label 11 px | `card`, `line`, `dim` |
| Pick up where you left off | heading 15 px 600; cards 320 x 64, radius 10; glyph `accent`, title 13 px 600, line 11 px | `card`, `line`, `text`, `dim` |
| Status line | 24 px, centred, 11 px: "Do Not Track is on" | `dim`; a quiet fact, no action (hig.md section 1, Status bar) |

Empty state (no history yet): the pinned row and the status line stay; "Pick up where you left off" is replaced by the `EmptyState` pattern: icon, 22 px semibold title, one-line hint, one action. No promotions, no news, no suggested sites, no wallpaper chooser on this page.

## 6. First run (frame: `atlas-firstrun.svg`)

Three choices, one primary action, skippable. Sidebar hidden (nothing to list), toolbar present so the window already looks like Atlas.

| Part | Spec | Token |
|---|---|---|
| Badge | 96 px | brand asset |
| Title | "Welcome to Atlas", 26 px bold | `text` |
| Hint | "Three choices. Each one can be changed later in Settings.", 13 px | `dim` |
| Card | 520 wide, radius 10, rows 56 px, rules `line` inset 16 | `card` |
| Row | glyph 16 `accent`, title 13 px 600, hint 11 px `dim`, control right-aligned 16 px from the edge | `text`, `dim` |
| Row 1 | Do Not Track: "Sites are asked not to follow you. On by default." Toggle, on. | `accent` track, `accentText` knob |
| Row 2 | Bring your bookmarks: "From another browser on this PC. Nothing leaves it." Button "Choose…" | `control`, `text` |
| Row 3 | Search: "Pick the search you want in the address bar." Button "Choose…" | `control`, `text` |
| Primary action | "Start browsing", 140 x 36, radius 6, bottom right of the card | `accent` fill, `accentText` label (see section 7) |
| Secondary line | "You can skip this and decide later." 11 px, bottom left, under the card | `dim` |

Copy rules (selling-skill.md section 3, hig.md section 3): sentence case, no exclamation marks, "…" when the action asks for more input, the person as the subject, no marketing adjective. The mocks' texts are illustrations; the strings that ship go through the string review. Nothing on this page names another browser: row 2 says "another browser".

## 7. Contrast, measured on the theme tokens

Computed by `tools/brand/atlas_chrome.py` helpers on the composited colours (glass over `surface`, sidebar over `surface`, the selection pill over the sidebar). Bars: 4.5:1 text, 3:1 glyphs and ring.

| Pair | Light | Dark |
|---|---|---|
| `text` on `surface` / `glass` / `sidebar` | 16.1 / 16.5 / 14.8 | 16.0 / 14.8 / 14.1 |
| `dim` on `surface` / `glass` / `sidebar` | 5.1 / 5.2 / 4.7 | 7.4 / 6.8 / 6.5 |
| `dim` on `card` / `control` | 5.7 / 4.7 | 6.1 / 5.0 |
| `text` on the selection pill | 11.5 | 8.6 |
| `dim` on the selection pill | 3.9 (fails: not used) | 4.5 (not used) |
| `accent` glyph on `sidebar` | 3.6 | 4.1 |
| `accent` ring on `control` | 3.6 | 3.2 |
| `accentText` on `accent` (primary button, toggle knob) | **4.35 (fails 4.5 for 13 px)** | **3.69 (fails 4.5; meets 3:1 for large text only)** |
| `accent` as text on `card` (a link) | 4.35 (needs an underline) | 3.9 (needs an underline) |
| `success` / `warning` / `danger` on `card` | 3.6 / 4.0 / 4.7 | 9.0 / 6.2 / 4.9 |
| `line` on `surface` / `card` (boundaries) | 1.2 / 1.2 | 1.3 / 1.3 |

What follows from it:

1. The primary button label (`accentText` on `accent`) is 4.35:1 in light and 3.69:1 in dark, under the 4.5:1 bar for 13 px text. That is the system's token pair, used by every WolOS app; Atlas does not work round it with a literal. Proposed for the CTO: darken `accent` for filled controls (the app-icon violet `#6A4DF4` gives white 5.3:1) or add a filled-control token. Until then the first-run button shows the gap, and the mock draws it as the system does.
2. `success` and `warning` text on `card` in light is under 4.5:1: status words stay in `text` with the colour on the glyph only.
3. Boundaries of cards and fields are 1.2 to 1.3:1 by default. The omnibox is identified by its fill, glyph, placeholder and the focus ring; under `@contrast` `line` becomes `text` at 55%, which is 3.9:1 (light) and 5.6:1 (dark) against `surface`.

## 8. Not in the frames, decided here

- Private window: same chrome, with the omnibox leading glyph `view-conceal-symbolic` and the words "Private window" in the toolbar title slot in `dim`; no extra colour. [proposal]
- Error pages: `EmptyState` pattern, one sentence of what happened and one of what to do (hig.md section 3), one action.
- Menus and popovers: `card`, radius 10, blur 30 px; rows 28 px.
- Find in page (Super+F): a 36 px bar under the toolbar in `glass`, the field in `control`; the match count in 11 px `dim`.
- Downloads: the toolbar button gets a 16 px progress ring in `accent` while a download runs; no popup unless clicked.
