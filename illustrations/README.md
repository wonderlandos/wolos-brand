# WolOS illustrations

The cast of Wonderland, each with a job in the system. Source SVGs here, PNG exports in `png/` (`@1x` at the use size, `@2x` for HiDPI). Apps load the PNGs. The White Rabbit is flat and fill-only (no strokes, filters or gradients); the other characters are still lit renders with filters (soft shadows, glow).

| Character | File | Used in | Personality |
|---|---|---|---|
| The White Rabbit | `white-rabbit.svg`, `png/white-rabbit@{1x,2x}.png` (256); expressions `white-rabbit-expressions.svg`, `png/white-rabbit-expressions@1x.png` (1296x760) | Setup, About, lock screen, Software Update, guide moments | Curious, quick, always late, a little mad. Geometric, in a waistcoat and bow with the pocket watch. Six states change only the ears, eyes, brows, mouth and one prop: neutral, happy, curious, late!, sleepy, surprised. |
| The Keyhole | `keyhole.svg`, `png/keyhole@{1x,2x}.png` (256) | About This Computer, sign-in, Setup and installer moment cards | The small door into Wonderland. Light comes through. The WolOS mark made as an object: four nested arched doors on a brass sill, the smallest one open. |
| The Cheshire Cat | `cheshire.svg`, `png/cheshire@{1x,2x}.png` (160) | Loading and thinking states (rotate it: he is a ring) | Grins while the work happens. Tail first, he vanishes. |
| The Pocket Watch | `pocket-watch.svg`, `png/pocket-watch@{1x,2x}.png` (160) | Software Update, progress | Opens up and shows you the gears turning. |
| The Teacup | `teacup.svg`, `png/teacup@{1x,2x}.png` (160) | Empty states ("Nothing here yet") | Clean, empty, still warm. Pour something in. |
| Welcome scene | `setup-welcome.svg`, `png/setup-welcome@{1x,2x}.png` (480x320) | Setup Assistant welcome hero; left 55 % kept calm for the title | Dusk at the garden hedge: a doorway in the hedge is the WolOS mark, four nested doors with the smallest one open, and its light falls across the grass. The Rabbit is late. |
| Rabbit peek | `lock-peek.svg`, `png/lock-peek@{1x,2x}.png` (320x200) | Lock screen easter egg, from the bottom edge | "Oh, it's you." |
| Character sheet | `character-sheet.svg`, `png/character-sheet@{1x,2x}.png` (1600x1000) | Decks, press | All five together. Links the SVGs beside it. |

Art direction: the Rabbit is flat: one 10 px ink outline (`#2B2140`, round joins) on flat fills, violet `#7C5CFF` as the only accent, the watch in `tokens` yellow, pink from the doctrine band, transparent background. The other characters keep the earlier lit rig (warm key top-left, violet rim back-right, brass and porcelain) until they are redrawn in the same flat style. `character-sheet.svg`, `setup-welcome.svg` and `lock-peek.svg` show the new Rabbit; the Keyhole and the welcome doorway follow the arched-door mark (see `../brand/README.md`); the Cheshire Cat, Pocket Watch and Teacup are still the earlier lit renders.

Regenerate (needs `rsvg-convert`): the Rabbit and its expression sheet with `python3 -I design/tools/brand/build.py design`; all illustrations (white-rabbit, lock-peek, setup-welcome, character-sheet and the rest) with `python3 -I design/tools/illus/build.py [OUT_DIR] [name...]`. Both draw the Rabbit from `design/tools/brand/mascots.py`. Keep each SVG under 300 KB.

© 2026 Julia Klee. Wonderland Brand License 1.0 (`LicenseRef-Wonderland-Brand-1.0`, see `../LICENSE`); `tools/illus/` is BSD-2-Clause.
