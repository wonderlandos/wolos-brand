# Atlas: brand brief

Atlas is the browser of WolOS. It is part of the system, the way the file manager and Settings are: it follows the theme, the icon language, the motion table and the keyboard rules of the HIG, and it is the way the person reaches everything that is not on the PC. This brief says what Atlas is called, how it should feel, what it must never look like, and the bars its identity is held to. The files it points at are generated and checked (section 8).

Status: the lead chose direction B, Folio (2026-11-03). The theme icon `wolos-atlas` and the symbolic `atlas-symbolic` are drawn from it through `tools/icons/` (section 8); the mocks wear the Folio badge. Nothing here is shipped yet: the overlay PNGs are staged under `brand/atlas/overlay/` for the product repository.

## 1. The name

An atlas is a book of maps, and the word has meant that since the late 1500s. It comes from Atlas, the Titan who carries the sky. The first bone of the neck is also called the atlas: it carries the head. The Atlas Mountains are a real range, in the north-west of Africa. All four meanings say one thing: something that carries the world so that you can look at it.

That is the job of a browser on WolOS. The web is where people read, write, play, pay and talk, and the browser holds all of it up and gets out of the way. WolOS is "Just use it": the PC disappears and what you came to do is what is left (marketing/positioning.md section 1). Atlas is the part of the PC you look through. It succeeds when the page is all you notice.

How the name sits next to the WolOS mark: the mark is a small door into Wonderland with light coming through. Atlas is what carries the world to that door. Where it helps, the identity borrows the door and the light (direction C does); it never borrows the rabbit.

## 2. Personality in five words

| Word | Means | Never |
|---|---|---|
| Quiet | The page is the loudest thing on screen. Chrome is a thin glass strip and a list; colour appears for state, not decoration. | Banners, promotions, a tour, a badge that asks to be looked at. |
| Quick | Everything answers at once; nothing waits for an animation (hig.md Motion: nothing over 400 ms, input never blocked). | A splash screen, a loading flourish, a logo that animates on launch. |
| Plain | Short sentences in sentence case, the person as the subject, no exclamation marks, no marketing adjectives (selling-skill.md section 3). | "Supercharged", "seamless", "next-gen"; a joke in an error. |
| Private | Do Not Track is on from the first run; nothing leaves the PC unless the person sends it. Said as plainly as it is true: Do Not Track is a request that sites may ignore, so the words are "asks sites not to follow you", never "blocks tracking" until something measured blocks. | A shield that promises more than the code does; fear as a selling point. |
| Crafted | One key light, real materials, a single gold accent, the same card as every other WolOS app. Made, not generated. | Gloss sweeps, rainbow gradients, clip-art. |

## 3. What the identity must be

- Recognisable in a 48 px dock and in a 16 px tab: a silhouette first (icons/LANGUAGE.md section 6), then the light.
- Of the family: same soft card and lit rim as every WolOS app icon, the WolOS palette (violet `#7452F5`, the web category blue `#1D64B0`, ink `#221B36`), one gold pop (`#FFC94A`) that carries the idea, and the Cryswol-style single white glyph in facet tones (95 percent where the light falls, 58 to 62 percent in shade).
- Honest: nothing in the identity says more than the product does.
- Calm on both grounds (`#F1F1FA` light, `#15151D` dark).

## 4. What it must never look like

- A globe with a swoosh, an orbit ring, a latitude grid or any ring of dots round a ball. The planet-and-ring has been every browser's logo for thirty years. A world is allowed only as a single plain sphere that something else carries (direction A subverts it this way).
- A round badge. The circle with a compass, a lens or a colour wheel is what the browsers of the two big desktop platforms look like; Atlas is a card like every WolOS app, so it cannot be mistaken for them in a dock.
- A compass needle or a coloured wheel in any form, an "e" or an "a" curled into a swirl, a rainbow, an animal, a spider or any web pun.
- A lock, a shield or an eye as the logo: those say "security product", not "the way in".
- Pixel art, sparkles, gloss sweeps, window dots and a platform's system colours (the rejected list of icons/LANGUAGE.md). White glyph with no light on it is also out: the three-tone facets are the light.
- A mascot. The rabbit lives in the system; the browser is a tool.

## 5. How the WolOS logo and the Cryswol badge were chosen (and how this follows)

Several directions were drawn for each, the lead looked at them and picked (WolOS: direction C, nested doors, outlined to fills; Cryswol: the white isometric gem on a warm gradient, round 3 variant 1). Atlas follows the same path: three directions, same card, same sizes, one contact sheet, the lead decides. The brief for the logo round was "simple, no useless detail, no pixel art, study the real geometry" (decisions of 2026-11-03, memory #767, #784, #769). That is why every direction here is one glyph, one gold pop and nothing else, and why each has a separate 48 px drawing with less in it.

Note for whoever draws the final icon: the lead asked for a flat single-glyph badge in the Cryswol family, so the three directions are faceted white glyphs, lit by tone, on the WolOS soft card. The theme's app icons are crafted objects (icons/LANGUAGE.md section 4); if a direction is chosen, `wolos-atlas` for the theme is redrawn through `tools/icons/` as an object, from the chosen silhouette. This file's badge stays the logo.

## 6. The three directions in one line each

| | Direction | Idea | Card |
|---|---|---|---|
| A | Bearer | The letter A as two legs carrying a gold sphere. Atlas holding up the world. | ink-indigo, gold sphere |
| B | Folio | A map folded in three with a gold "you are here" mark and a short route. The book of maps. | web blue, gold mark |
| C | Threshold | The Atlas mountains with the WolOS door in their foot, light coming through. The way in. | WolOS violet, gold door |

Rationale paragraphs, the 16 px follow-up for each and the recommendation are in `directions/README.md`; the sheet is `directions/contact-sheet.png`.

## 7. Accessibility targets

These are targets for Atlas, measured where it is marked (numbers are from the generator's checks and from `tools/brand/atlas_chrome.py` on the shipped `wol-light` / `wol-dark` tokens).

| Area | Target | State |
|---|---|---|
| Text | WCAG 2.2 AA: 4.5:1 for body, 3:1 for 18.66 px bold and up. No text below 11 px (WK-003). | Body and dim text pass on every Atlas surface. `accentText` on `accent` (the primary button) is 4.35:1 light and 3.69:1 dark: it fails for 13 px text. This is a theme token issue, not an Atlas one; see `chrome/tokens.md` section 7. |
| Icons and focus | 3:1 for glyphs and the focus ring against the surface behind them. | Focus ring (`accent`, 2 px) measures 3.60:1 light and 3.17:1 dark on the omnibox. Pass. |
| Logo | White glyph 3:1 on its card at every size; badge edge 1.3:1 against both grounds; glyph spans 0.45 to 0.86 of the card; at 48 px median glyph contrast 1.35:1 or more. | All three directions pass at 512, 128 and 48 (`tools/brand/atlas_check.py`, output in section 8). |
| Colour is never the only signal | Do Not Track on: struck-eye icon and the words "Do Not Track is on". Not secure: icon and the words. Loading: motion and a progress value. | Specified in `chrome/tokens.md`. |
| Targets | At least 24 x 24 px hit area (WCAG 2.5.8); toolbar buttons 28 x 28, sidebar rows 28 px high. | Specified. |
| Keyboard | Every control reachable and visible when focused; the shortcuts of hig.md section 3 mean the same here (Super+T new tab, Super+W close, Super+L address bar, Super+F find, Super+comma settings). | Specified. Super+T and Super+L are Atlas additions to the HIG table: [verify] with the shell team. |
| Motion | `Reduce motion` jumps to the end state; no motion carries information that the final state lacks. | `chrome/motion.md`. |
| Contrast mode | `@contrast` raises `line` to `text` at 55% (wolkit-style.md); Atlas draws no 1 px boundary the person needs that is not `line`. | Specified. Boundaries of cards and the omnibox are 1.2:1 by default; the field is identified by its icon, placeholder and focus ring, and by `@contrast`. |
| Screen readers | Icon-only buttons have an accessible name and a tooltip (hig.md section 1). The new tab page and the first run are real headings and lists, in reading order. | Specified. Not tested with a screen reader. |

## 8. Files and how to rebuild them

| Path | What |
|---|---|
| `brand/atlas/BRIEF.md` | this file |
| `brand/atlas/directions/atlas-{a-bearer,b-folio,c-threshold}-{512,128,48}.svg` | the nine badges (viewBox 1024, drawn for the size in the name) |
| `brand/atlas/directions/contact-sheet.{svg,png}` | three directions across, light ground above, dark below |
| `brand/atlas/directions/README.md` | rationale per direction, recommendation |
| `brand/atlas/chrome/tokens.md` | the WolOS tokens mapped onto the browser chrome |
| `brand/atlas/chrome/atlas-newtab.{svg,png}`, `atlas-firstrun.{svg,png}` | the two mock frames (light and dark) |
| `brand/atlas/chrome/motion.md` | the motion note |
| `icons/apps/wolos-atlas.svg`, `icons/apps/small/wolos-atlas.svg` | the theme icon: Folio as a crafted object (a folded paper map, the gold mark lit from inside), `tools/icons/crafted_c.py` `atlas` |
| `icons/symbolic/atlas-symbolic.svg` (and `wolos-atlas-symbolic.svg`, the same drawing) | the 16 px glyph: the fold outline, the mark as a dot, `tools/icons.py` |
| `icons/aliases.tsv` row `atlas` | the browser's desktop file ids that resolve to `wolos-atlas`: today's id and `org.wolos.atlas` |
| `brand/atlas/overlay/usr/share/icons/WolOS/{48x48,128x128,512x512}/apps/wolos-atlas.png` | staged overlay PNGs; they belong in the product repository at `desktop/overlay/usr/share/icons/WolOS/` (`tools/icons/overlay.py`) |
| `brand/atlas/icon/contact-sheet.png` | the theme icon at 512, 128, 48 and 16 px on both grounds (`tools/brand/atlas_icon_sheet.py`) |

```
python3 -I design/tools/brand/atlas.py design            # badges and sheet (rsvg-convert for the PNG)
python3 -I design/tools/brand/atlas_chrome.py design     # the two frames
python3 -I design/tools/brand/atlas.py design --check    # files on disk are what the generators write
python3 -I design/tools/brand/atlas_check.py design      # static and raster bars, theme tokens in step
python3 -I design/tools/icons.py                          # the theme icon, its small drawing, the symbolic, aliases.tsv
python3 -I design/tools/brand/atlas_icon_sheet.py design   # brand/atlas/icon/contact-sheet.png
```

The mocks wear direction B, the lead's choice (`KEY` in `atlas_chrome.py`); the new tab row in their sidebar shows `atlas-symbolic`.

## 9. Open questions for the lead

1. Which direction (A, B, C), or a mix. Answered 2026-11-03: B, Folio.
2. Tabs as a sidebar (the mocks) or a strip on top. The HIG favours the sidebar; a strip is specified as the fallback for narrow windows in `chrome/tokens.md` section 3.
3. Whether Atlas gets its own accent (it does not in the mocks: it uses the system accent so a theme change reaches it).
