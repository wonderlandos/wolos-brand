# SPDX-License-Identifier: GPL-2.0-or-later
"""The registry: every full-colour icon of the theme, its context, its finish and how it is drawn.

D2 "crafted objects" for the 26 apps (a lit material object on the soft card, crafted_a/b.py);
D1 "pressed paper" for the long tail (13 places, 2 devices, 11 mimetypes, paper_set.py). Each icon
has a FULL variant (the scalable SVG, the 128 and 512 px PNGs) and a SMALL variant (the 48 px PNG
and the previews up to 64 px): the same drawing, simplified, the glyph scaled up to fill about
70% of the tile, lighter ramps on dark tiles."""
from dataclasses import dataclass
from typing import Callable

import crafted_a as A
import crafted_b as B
import paper_set as P
from svgk import Cv

# glyph scale about the optical centre: (full, small[, centre y])
SCALE = {
    "settings": (1.0, 1.0), "software": (1.0, 1.12), "files": (1.0, 1.0), "terminal": (1.0, 1.0),
    "browser": (1.0, 1.0), "music": (.96, .95), "mail": (1.0, .96), "installer": (1.0, 1.0),
    "plugin-maker": (1.15, 1.15), "control-center": (1.1, 1.1),
    "kit-ai": (1.28, 1.32), "kit-codecs": (1.15, 1.2), "kit-gaming": (1.2, 1.25),
}
KITS = ("kit-ai", "kit-codecs", "kit-craft-suite", "kit-creative", "kit-dev", "kit-gaming")


@dataclass
class Icon:
    name: str
    ctx: str                       # apps | places | devices | mimetypes
    level: str                     # D2 | D1
    draw: Callable[[Cv], None]     # draws the tile and the glyph on the canvas
    tile: bool = True              # the glyph sits on a container (apps) rather than being an object itself
    glyph: bool = True             # False for a plain object (a folder, a basket)

    def scale(self, small):
        s = SCALE.get(self.name, (1.0, 1.0))
        return s[1] if small else s[0]

    def cy(self):
        return 600 if self.name in KITS else 512

    def svg(self, small=False, tile_only=False):
        cv = Cv(small)
        self.draw(cv)
        return cv.svg(self.name, self.scale(small), self.cy(), tile_only)


APPS = [
    ("settings", A.settings), ("software", A.store), ("files", A.files), ("terminal", A.terminal),
    ("browser", A.browser), ("music", A.music), ("mail", A.mail), ("installer", A.installer),
    ("calculator", B.calculator), ("calendar", B.calendar), ("control-center", B.control_center),
    ("launcher", B.launcher), ("plugin-maker", B.plugin_maker), ("notes", B.notes), ("photos", B.photos),
    ("system-monitor", B.system_monitor), ("text-editor", B.text_editor), ("games", B.games), ("trash", B.trash),
    ("kit-ai", B.kit_ai), ("kit-codecs", B.kit_codecs), ("kit-craft-suite", B.kit_craft_suite),
    ("kit-creative", B.kit_creative), ("kit-dev", B.kit_dev), ("kit-gaming", B.kit_gaming),
]


def all_icons():
    out = [Icon(n, "apps", "D2", f) for n, f in APPS]
    out += [Icon(n, "places", "D1", lambda cv, b=b, e=e: P.place(cv, b, e), tile=False, glyph=e is not None) for n, b, e in P.PLACES]
    out += [Icon("user-trash", "places", "D1", lambda cv: P.basket(cv, False), tile=False, glyph=False),
            Icon("user-trash-full", "places", "D1", lambda cv: P.basket(cv, True), tile=False, glyph=False)]
    out += [Icon("drive-harddisk", "devices", "D1", P.drive_harddisk, tile=False),
            Icon("drive-removable-media", "devices", "D1", P.drive_removable, tile=False)]
    out += [Icon(n, "mimetypes", "D1", lambda cv, c=c, g=g: P.mime(cv, c, g), tile=False) for n, c, g in P.MIMES]
    return out
