# ADR brand-east: the east design calculus

Status: proposal (study on design branch `wave3/brand-east`; nothing installed reads it).
Date: 2026-11-04. Lead direction: a Western entry point, Chinese harmony first and Korean density second. Change the geometry, not just the finish. Identity stays: tokens, keyhole, Folio, type, and the katakana ウォルOS as a small centred element at the bottom of the mark. Every step proves itself side by side with a score.

Code: `tools/east/` (calculus `calculus.py`, colour `colour.py`, geometry `geom.py`, scorer `score.py`, token scorer `score_tokens.py`, boards `board.py`, `boards.py`, `dir_sheets.py`). Studies: `east/` (icons, directions, types, marks, wallpapers). Token proposal: `tokens/tokens-east.json`.

## 1. Proportion: the construction ruler

**Module (cai-fen, Yingzao fashi, 1103).** A building is measured in *fen*, the 1/15 part of the height of the standard timber section (*cai*). The named sections, in fen:

| name | section | here |
|---|---|---|
| cai | 15 high x 10 wide | 60 x 40 px |
| zhi (filler block) | 6 high x 4 thick | 24 x 16 px |
| zucai = cai + zhi | 21 | 84 px |

1 fen = `U` = 4 px = 0.25 rem (`calculus.py`). Named lengths (`NAMED`), in fen: 1, 2, 3, 4, 6, 10, 15, 21, 30, 42, 60, 84, 144. In px: 4, 8, 12, 16, 24, 40, 60, 84, 120, 168, 240, 336, 576. `module_fit` scores 1.0 on a named length, 0.6 on any whole fen, and 0 off the module.

Allowed ratios (`RATIOS`): 1:1, cai 3:2 (15:10), zucai 7:5 (21:15, close to the square root of 2), 2:1, zhi 3:2.

Type: line height on the module, size = 2/3 of the line (the cai section 10:15). caption 11/16, body 13/20, heading 16/24, title-2 24/36, title 27/40, display 40/60 (`type_scale`).

**Door-light ruler (menguang chi, Lu Ban ruler).** It is 1.44 chi long, in eight bands: cai (wealth), bing (illness), li (parting), yi (duty), guan (office), jie (loss), hai (harm), ben (root). Openings were sized so that each dimension, modulo the ruler, ends in cai, yi, guan or ben. Here the ruler is 144 fen = 576 px, one band 72 px (`band`). It applies to openings of 72 px and more (windows, panels, cards, hero, boot lockup). Example: the boot lockup width of 576 px is exactly one ruler.

## 2. Five-phase palette (wuxing), derived from the base

Generating (sheng): wood -> fire -> earth -> metal -> water -> wood. Overcoming (ke): wood -> earth -> water -> fire -> metal -> wood (`colour.py`).

Classification (OKLCH): chroma below 0.035 is metal when L > 0.55 (white) and water when darker (black). Hues 130-215 are wood, 215-330 are water (azurite blue up to violet), 55-130 are earth, everything else is fire. The base violet `#7C5CFF` is *zi*, the intermediate colour of the north (black over cinnabar), so it counts as water.

Consequences for the base:
- metal (white grounds) is its mother: sheng, any area;
- wood (jade) is its child: sheng, any area, and it is the companion colour;
- water (blue, ink) is kin: same element, any area;
- fire (cinnabar, rose) and earth (gold) are ke: accents only, at most `ACCENT_SHARE` = 6/42 = 1/7 of a frame.

Derivation (`derive`, `east_palette`). Every colour is `from_oklch(ladder(L0, k), C0 * c / 21, hue)`:
- `L0`, `C0`, `h0` are the base's own OKLCH values;
- `ladder` is the value ruler: 21 fen from the base to white and 21 fen from the base to black;
- chroma is counted in 21sts of the base chroma;
- hue is either the base hue or an element anchor, the OKLCH hue of the traditional pigment (cinnabar `#FF461F`, gamboge `#FFB61E`, malachite `#16A951`, azurite `#1685A9`; anchor values come from the zhongguose table and should be checked against a pigment reference).

Results:
- accent: the first shade that holds 4.5:1 under white, `#7452F5` (k = -1). This answers QA D-06: today `#7C5CFF` gives 4.35 and `#8B6CFF` 3.69.
- neutrals sit on the base hue with chroma 1-2/21.

## 3. Light

- One source, upper left and steep. `LIGHT` points toward it, `SHADOW` = dx:dy = 1:2. The eye and the light enter through the same gate.
- Gloss sits on the lit rim only. Lit gradients run along 1:2. Elevations use offsets (1,2), (2,4), (3,6).
- A plane in front is never darker than the plane behind it.
- A recess is not drawn lit from below: the scorer reads every plane as raised.

## 4-7. Flow (feng shui) and density (Korean), as computable scores

The scorer is `score.py`. An SVG is rendered with rsvg-convert and measured as pixels; a layout tree (JSON boxes) adds exact lengths. Each rule scores 0-100; the total is the mean of eight.

Measures used below:
- **salience**: OKLab distance to a blurred local ground, plus 0.5 x chroma;
- **masses**: connected components of the top 15% of salience, heaviest first;
- **ground**: a quadratic fit of the ground colour. For an icon it is fitted on the card ring 0.6-1.6 fen inside the silhouette.

1. **qi** (`r_qi`) = 0.25 entry + 0.25 landing + 0.2 turn + 0.15 (100 - 34 stagnant) + 0.15 (100 - 25 dead ends).
   - entry = 100 clip(0.5 + (tl - (tr + bl)/2) / 0.06), and 0 if tl < 8%. tl, tr, bl are the salience shares of the quadrants.
   - landing = 100 clip((m1/m2 - 1) / 0.4): one primary mass, heavier by 7:5.
   - turn = 100 if the path from entry to landing (greedy nearest mass) bends at least 25 degrees once, else 50. This is the spirit screen: qi meanders.
   - stagnant = a corner zone with more than 1.5/9 of the weight that the path never visits.
   - dead end = a reversal of more than 135 degrees.
2. **sha** (`r_sha`) = 100 - 15 arrows - 10 cuts - min(30, 300 aimed).
   - arrows: straight edges longer than 1/3 of the frame that run into its border.
   - cuts: straight edges longer than 1/2 of the frame, with weight on both sides within 3 fen (a dividing line through content).
   - aimed: sharp corners (minimum eigenvalue of the structure tensor, at a quarter-fen scale), each weighted by closeness to the landing (1 - d/0.5), per fen squared.
3. **forms** (`r_forms`) = 0.4 mountain + 0.3 support + 0.3 water.
   - mountain: the lower half carries 45-65% of the weight, -4 per point outside that range.
   - support: share of masses that are not heavy over light (a mass above another, columns overlapping, more than 2x heavier).
   - water: share of path steps no longer than 1/3 of the diagonal.
4. **zones** (`r_zones`, the nine-square luoshu grid) = 100 - 8 empty - 12 overloaded - 150 mean|w - neighbours| - 20 (if the centre holds less than 1/9).
   - empty: w < 0.2/9. Icon card corners are exempt.
   - overloaded: w > 3/9.
5. **palette** (`r_palette`): k-means regions (k = 8). For each adjacent pair, weighted by boundary length: same or sheng scores 1. ke scores 1 if the smaller region is at most 1/7 of the frame, falling linearly to 0 at 3/7.
6. **light** (`r_light`) = 0.45 shading + 0.3 shadow side + 0.25 order.
   - shading = the mean of the ground field slope and the slope inside objects, each 50 + 50 cos against `LIGHT`.
   - shadow side: just outside each plane, the side away from the light is darker.
   - order: a plane inside another plane's box is not darker than it by more than 0.02 L.
7. **proportion** (`r_proportion`).
   - Icons: canvas 24 fen, art box 21 fen. Score = 35 fill (1 - |L - 21|/4) + 25 ratio + 40 module (sides of planes on named or whole fen).
   - Marks: ink band and gap heights stand in named-fen ratios, within 4%.
   - Screens: 70 module + 30 door bands.
   - Layout trees (`tree_scores`): exact lengths, insets and radii; openings on the ruler; sibling gaps on at most two values (rhythm); lines that touch the frame.
8. **density** (`r_density`, Korean layered) = mean of four parts:
   - gravity: within 0.25 of (0.5, 0.47) for icons and marks, (0.5, 0.45) otherwise.
   - planes: ground, second and first plane shares (OKLab distance to ground < 0.04, 0.04-0.18, > 0.18) against zucai : cai : zhi = 21 : 15 : 6 out of 42.
   - rhythm: 1 - CV of the gaps between salience bands.
   - breathing: ground share between 1/3 and 3/5.

Token-level rules (`score_tokens.py`):
- proportion: px values on the module, and type size = 2/3 of the line.
- palette: contrast floors, neutrals on the base hue within 6 degrees, large surfaces same or sheng with the accent.
- light: a declared direction, with elevations at 1:2.
- density: distinct planes and gentle spacing steps.

Flow needs a layout, so tokens are not scored on it.

## 8. Icons

- **First redraw** (`east/icons`, `tools/east/icons_east.py`): the shipped card, juzhe slopes, one light. The lead rejected it as a restyle.
- **Three directions** (`east/directions`, `tools/east/directions.py`):
  - wuxing: the silhouette is the phase shape;
  - strata: jogakbo patches;
  - gate: a battered wall with the meaning as an opening of light.
  Each has construction sheets. The lead found them too extreme: "nem chineses fazem ícones dessa forma".
- **Three types in the Chinese app grammar** (`east/types`, `tools/east/types.py`):
  - A bold glyph;
  - B traditional motif (ruyi gear, coin-sealed bag, scroll, seal, longevity peach, luopan Folio);
  - C jianzhi paper-cut.
  These wait for the lead's pick.

**juzhe** (`geom.juzhe`, roof raise-and-fold): a slope from the ridge to the eave. The first purlin drops H/10 under the straight line, and each next one drops half as much under the line from the previous folded purlin to the eave.

## 9. Marks

The zucai stack (`tools/east/marks_east.py`, `east/marks`):
- the WolOS letters are the cai (15 fen);
- under them sits the zhi: a 2 fen gap and 4 fen of ウォルOS;
- the katakana is tracked with equal ink gaps to 2/3 of the letters' width;
- the door mark is 21 fen tall, 6 fen from the letters.

Variants:
- boot: 576 px wide (one ruler) on the optical centre (0.45 H);
- release lockup: "WolOS 0.13 Qíjiā" at a zhi-high cap, the 齐家 seal in cinnabar (a ke accent, under 1/7), and "Put the house in order" 6 fen below.

The lead approved the mark and the release banner on 2026-11-04 at 06:49Z.

## 10. Wallpapers

`tools/east/wallpapers_east.py`: shanshui in three planes. The light at the upper left is the entry. The river turns twice and lands in a pool at a lit door in the lower-right third, and a mountain anchors the lower left. The lead put these on hold until an icon is approved. He also said wallpapers may follow qi more freely, because that reads as architecture.

## Honest limits

- The scorer was written alongside the art, so it measures fit to these rules, not beauty. The side-by-side sheets are the proof.
- Palette scores 100 on almost every icon, current or new, so on icons that rule does not discriminate.
- On flat brand marks the light rule is close to neutral.
- The gate direction's bright plinth reads as light from below.
- The wallpaper studies do not beat the current ones (day 75.8 -> 75.5, night 79.4 -> 76.4).
