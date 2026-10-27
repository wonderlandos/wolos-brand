# WolOS illustrations

The cast of Wonderland, each with a job in the system. Source SVGs here, PNG exports in `png/` (`@1x` at the use size, `@2x` for HiDPI). Apps load the PNGs: the SVGs use filters (soft shadows, glow).

| Character | File | Used in | Personality |
|---|---|---|---|
| The White Rabbit | `white-rabbit.svg`, `png/white-rabbit@{1x,2x}.png` (256) | About, guide moments | Curious, quick, always late, a little mad. |
| The Keyhole | `keyhole.svg`, `png/keyhole@{1x,2x}.png` (256) | About This Computer, sign-in | The small door into Wonderland. Light comes through. |
| The Cheshire Cat | `cheshire.svg`, `png/cheshire@{1x,2x}.png` (160) | Loading and thinking states (rotate it: he is a ring) | Grins while the work happens. Tail first, he vanishes. |
| The Pocket Watch | `pocket-watch.svg`, `png/pocket-watch@{1x,2x}.png` (160) | Software Update, progress | Opens up and shows you the gears turning. |
| The Teacup | `teacup.svg`, `png/teacup@{1x,2x}.png` (160) | Empty states ("Nothing here yet") | Clean, empty, still warm. Pour something in. |
| Welcome scene | `setup-welcome.svg`, `png/setup-welcome@{1x,2x}.png` (480x320) | Setup Assistant welcome hero; left 55 % kept calm for the title | Dusk at the garden hedge: the keyhole door stands ajar, its light thrown across the grass. The Rabbit is late. |
| Rabbit peek | `lock-peek.svg`, `png/lock-peek@{1x,2x}.png` (320x200) | Lock screen easter egg, from the bottom edge | "Oh, it's you." |
| Character sheet | `character-sheet.svg`, `png/character-sheet@{1x,2x}.png` (1600x1000) | Decks, press | All five together. Links the SVGs beside it. |

Art direction: one light rig everywhere (warm key top-left, violet rim back-right), violet `#7C5CFF` as the only accent, brass and porcelain as warm neutrals, transparent backgrounds that hold on light and dark.

Regenerate (needs `rsvg-convert`): `python3 -I design/tools/illus/build.py [OUT_DIR] [name...]`. Keep each SVG under 300 KB.

© 2026 Julia Klee. Wonderland Brand License 1.0 (`LicenseRef-Wonderland-Brand-1.0`, see `../LICENSE`); `tools/illus/` is BSD-2-Clause.
