# Brand-east rules pack: the rules, the formulas, the tools, a worked example

For the main agent and any worker who applies the east calculus: icons, the site, the UI (0.13). The reasoning and the history are in `brand-east.md`; this is the working copy. The lead's line on how to apply it (2026-11-04 07:22Z): **balance, never extreme either way, always follow the flow.** The rules are gates, not a style to exaggerate. Where a score and the lead's eye disagree, the eye decides, and the score only stops regressions.

## A. The numbers (`tools/east/calculus.py`)

| what | value |
|---|---|
| fen (module) | `U` = 4 px = 0.25 rem (Tailwind 1) |
| named lengths (fen) | 1 2 3 4 6 10 15 21 30 42 60 84 144 → px 4 8 12 16 24 40 60 84 120 168 240 336 576 |
| sections (Yingzao fashi) | cai 15 × 10, zhi 6 × 4, zucai 21 = cai + zhi |
| ratios | 1:1, 3:2 (cai), 7:5 (zucai), 2:1 |
| door-light ruler | 144 fen = 576 px, 8 bands of 72 px: cai bing li yi guan jie hai ben; good = cai, yi, guan, ben; applies to boxes ≥ 72 px |
| type | line on the fen, size = 2/3 line: 11/16, 13/20, 16/24, 24/36, 27/40, 40/60 (UI); the site keeps its sizes on fen lines |
| light | upper left, `LIGHT` = (-1, -2)/√5; shadows at dx:dy = 1:2; elevation e → offset (e, 2e) px, blur 4e..8e |
| planes | ground : second : first = 21 : 15 : 6 (of 42) |
| accent share | a ke (overcoming) colour ≤ 6/42 = 1/7 of a frame |

**Colour derivation.**

```
derive(k, c, hue) = oklch(ladder(L0, k), C0 · c / 21, hue)
ladder(L0, k)     = L0 + (1 − L0) · k / 21     (k ≥ 0)
                    L0 · (1 + k / 21)          (k < 0)
```

- `L0`, `C0` and `h0` are the OKLCH values of `#7C5CFF`.
- Hue anchors: cinnabar (fire) 33.2°, gamboge (earth) 78.4°, malachite (wood) 150.2°, azurite (water) 226.6°.
- Elements by hue: wood 130-215, water 215-330 (violet zi counts as water), earth 55-130, fire elsewhere. Low chroma (< 0.035) is metal when light, water when dark.
- Relations: sheng (generating) is wood → fire → earth → metal → water → wood. Ke (overcoming) is wood → earth → water → fire → metal → wood.

## B. The eight rules (`tools/east/score.py`, each 0-100, total = mean)

**Measures used below.** Salience is the OKLab distance to a blurred local ground, plus 0.5 × chroma. Masses are the connected top-15% salience regions, heaviest first. The ground field is a quadratic fit (on the card ring for icons).

1. **qi** (attention path) = 0.25 entry + 0.25 landing + 0.2 turn + 0.15 (100 − 34·stagnant) + 0.15 (100 − 25·dead).
   - entry = 100·clip(0.5 + (tl − (tr + bl)/2)/0.06), and 0 if tl < 8%.
   - landing = 100·clip((m1/m2 − 1)/0.4).
   - turn = 100 if the entry → landing path bends ≥ 25° once, else 50.
   - stagnant: a corner zone over 1.5/9 of the weight that the path never visits.
   - dead: a reversal > 135°.
2. **sha** = 100 − 15·arrows − 10·cuts − min(30, 300·aimed).
   - arrows: straight edges > 1/3 of the frame running into its border.
   - cuts: straight edges > 1/2 of the frame inside it, with weight on both sides within 3 fen.
   - aimed: sharp corners weighted by closeness to the landing, per fen².
3. **forms** = 0.4 mountain + 0.3 support + 0.3 water.
   - mountain: lower half holds 45-65% of the weight.
   - support: no mass more than 2× heavier sitting over another.
   - water: path steps ≤ 1/3 of the diagonal.
4. **zones** (3 × 3) = 100 − 8·empty(w < 0.2/9) − 12·over(w > 3/9) − 150·mean|w − mean(neighbours)| − 20·(centre < 1/9).
5. **palette**: across adjacent regions, weighted by boundary length.
   - same or sheng = 1;
   - ke = 1 if the smaller region is ≤ 1/7 of the frame, falling linearly to 0 at 3/7.
6. **light** = 0.45 shading + 0.3 shadow side + 0.25 order.
   - shading = 50 + 50·cos(slope, LIGHT), on the ground field and inside objects.
   - order: the same material, across an edge, is not darker in front than behind.
7. **proportion**.
   - icons (canvas 24 fen, art box 21) = 35 fill + 25 ratio + 40 module;
   - marks: ink bands and gaps in named-fen ratios;
   - screens = 70 module + 30 door bands;
   - layout tree: exact lengths, insets and radii.
8. **density** = mean of four parts:
   - gravity: within 0.25 of (0.5, 0.45);
   - planes: shares vs 21 : 15 : 6;
   - rhythm: 1 − CV of band gaps (tree: sibling gaps on ≤ 2 values);
   - breathing: ground between 1/3 and 3/5.

**With a layout tree** (`--tree`), proportion, palette and density are blended 50/50 or 75/25 with the exact tree measures, and sha loses 5 points per line that touches the frame.

## C. Icon craft (`tools/east/craft.py`, pass or fail)

| check | fails when |
|---|---|
| overflow | anything on the canvas edge |
| holes | a card's core is see-through (cardless objects exempt) |
| refs | an unresolved `url(#)`, or an empty clip or mask |
| layers | a shadow is drawn last, or a shadow is orphaned |
| contrast | below 3:1 at 16 px (measured on the small variant when one exists) |
| centring | a piece inside a hole is more than 0.15 fen off its centre |
| near miss | two pieces closer than 0.6 fen without touching |

**Shadow rules S1-S6** for icons:

| rule | |
|---|---|
| S1 elevation | card 0.8, glyph 1, accent 1/2; offset = elevation × (0.3, 0.6) fen |
| S2 cast colour | the card's hue, never grey |
| S3 form gradient | toward a tint of the card hue |
| S4 holes | shaded on their upper-left inner edge |
| S5 contact | an occlusion line, never across a glyph |
| S6 margin | the card shadow stays inside the 1.5 fen margin |

## D. Tools and CLI

| task | command |
|---|---|
| score a picture | `python3 -I design/tools/east/score.py FILE.svg\|png --kind icon\|mark\|screen\|wallpaper [--tree TREE.json] [--json]` |
| craft checks | `python3 -I design/tools/east/craft.py FILE.svg ...` (exit 1 on any failure) |
| token scores | `python3 -I design/tools/east/score_tokens.py [colors.json tokens-east.json]` |
| tokens | `python3 -I design/tools/east/tokens_east.py [--check]` → `tokens/tokens-east.json` |
| icon set | `python3 -I design/tools/east/types.py --a2`; `fullset.py N --sheet OUT.png` (batches 1-5) |
| boards | `board.py`, `boards.py`, `dir_sheets.py`; `.claude/v012/brand-east/send_preview.py SET_DIR -m "..."` (score, render and post to the lead in one call) |
| page capture | `node .claude/v012/brand-east/site/capture.mjs URL OUT [maxH]` → OUT.png + OUT.json (box tree); `wire.py` draws wireframes from trees |
| fork/join | `tools/east/par.py` `fanout(fn, items[, threads])`: rules run on threads, files on processes |

**Layout tree format:**

```
{"frame": [w, h], "nodes": [{"id", "rect": [x, y, w, h], "role": "opening|box|text|line|control",
 "fill": "#hex", "parent": id, "group": id, "radius": r}]}
```

Dependencies: numpy, scipy and Pillow for `tools/east` only; rsvg-convert for rendering. Not part of `build.py` or CI.

## E. Worked example: scoring a web page layout

The site home page, proposed version (`.claude/v012/brand-east/site/`):

```
node capture.mjs http://127.0.0.1:8711/ home-current 2600     # the live page: PNG + box tree
python3 -I wire.py                                            # wireframes for current and proposed
python3 -I design/tools/east/score.py home-proposed-wire.png --kind screen --tree home-proposed-tree.json
```

Output (abridged):

```
qi          100.0  entry 100, landing 100, turns [80, 31, 72, 107], stagnant 0, dead ends 0
sha          99.7  arrows 0, cuts 0
forms        78.0  lower half 0.56, heavy over light 2, jumps 2
zones        93.6  [[.21 .07 .03] [.12 .13 .11] [.14 .11 .09]]
palette      87.5
light        72.3  back not brighter 5/5
proportion   49.8  pixels: module 29, bands 0 | tree: module 70.5, door bands 100
density      58.0  gravity (0.41, 0.52), planes [.71 .21 .07]
total        79.9          (current page: 77.3)
```

How to read it:

- **qi** is full: the entry is upper left, Download is the clear landing, and the path turns.
- **forms** loses on two heavy-over-light pairs and two long jumps. The jumps are the gap between the hero and the proofs, and the gap to the closing band. Pull those sections closer, or add a bridge, before shipping.
- **proportion** in pixels is low because the pixel side measures the rendered wireframe bars, not real boxes. The tree's exact lengths (70.5 on module, 100 on door bands) are the real measure for a page.
- **density**: the ground share is 0.71, on the empty side. For a landing page that is fine (Korean breathing), but a dense page should land nearer 0.5.

**Practice:** change one thing, recapture, rescore, compare with the current version, and show the lead the side-by-side board with the score sheet.
