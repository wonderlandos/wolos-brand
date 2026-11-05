# SPDX-License-Identifier: GPL-2.0-or-later
"""The Type A2 drawings of the full-colour set: the bridge from tools/icons/build.py to the brand
generators in tools/brand (docs/adr/brand-calculus.md section 8.2).

Who draws what (build.py --check proves it byte for byte):
  tools/brand/types.py       a2_settings, a2_store, a2_files, a2_console, a2_atlas  -> the apps
                              settings, software, files, terminal, browser (APP_FROM_TYPES)
  tools/brand/fullset.py     BATCHES 1-5 (the other apps, the kits, the places, the devices and the
                              eleven mimetypes it covers)
  tools/icons/crafted_*.py,  everything the registry (families.py) lists that no A2 function draws:
  paper_*.py                  the Atlas Folio app icon (wolos-atlas), clock, documents, videos,
                              archive, disk-usage and the paper mimetypes and devices A2 does not cover

The finish the installed set adds on top of a brand generator's output, in one place:
  1. svgk.qt_safe: every clipPath becomes the same shape in a luminance mask (QtSvg ignores clip-path);
  2. svgk.gtk_safe: every filtered element draws inside a group that opens with svgk.PAD (GTK 4 sizes a
     filter's source from the filtered geometry; gtkcheck, README); librsvg draws it the same
     (RMSE <= 0.002 at 48 and 128 px on all of them);
  3. RIM: the faint rim on the page chips of the mimetypes and on the trash card so they read on the
     light desktop (full drawing only; the small drawings have none).
The brand generators are pure: same code, same bytes (no read of the installed icons; the card is
svgk.CARD). Stdlib only, like the rest of build.py."""
import os
import re
import sys
import types  # noqa: F401  first: tools/brand/types.py must never shadow the stdlib module (HERE leads sys.path there)

import svgk
from families import Icon

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND_TOOLS = os.path.normpath(os.path.join(HERE, "..", "brand"))

# registry app name -> the title tools/brand/types.py gives its A2 function
APP_FROM_TYPES = {"settings": "Settings", "software": "Store", "files": "Files", "terminal": "Console", "browser": "Atlas Folio"}
# icons that get the rim (full drawing): the trash card and every A2 mimetype page
RIM_COLOUR = "#BDBBD0"
RIM_APPS = {"trash"}


def _modules():
    if BRAND_TOOLS not in sys.path:
        sys.path.append(BRAND_TOOLS)
    import fullset
    return fullset, fullset.T


def rim(svg):
    """svg with the rim path right after the card or page body (the element that follows the first
    shade): the same outline (and transform), no fill, a 4 px stroke centred on the edge."""
    m = re.search(r'<path class="shade"[^>]*/>(<path d="([^"]+)"([^>]*)/>)', svg)
    if not m or 'fill="url(#' not in m.group(3):
        raise ValueError("a2.rim: no card or page body after the shade")
    tr = re.search(r' transform="[^"]*"', m.group(3))
    r = f'<path class="rim" d="{m.group(2)}"{tr.group(0) if tr else ""} fill="none" stroke="{RIM_COLOUR}" stroke-width="8" stroke-linejoin="round"/>'
    return svg[:m.end()] + r + svg[m.end():]


class A2Icon(Icon):
    """An icon drawn by a brand generator. It has no tile-only drawing (the A2 card and glyph are one
    construction), so build.py holds it to the static rules (checks.static) and the byte-for-byte
    lock, not to the old raster rules."""
    static_only = True

    def __init__(self, base, fn):
        super().__init__(base.name, base.ctx, base.level, None, tile=base.tile, glyph=base.glyph)
        self.fn = fn
        self.rim = (base.ctx == "mimetypes") or (base.ctx == "apps" and base.name in RIM_APPS)

    def svg(self, small=False, tile_only=False):
        if tile_only:
            raise ValueError(f"{self.name}: an A2 icon has no tile-only drawing")
        out = self.fn(small)
        if self.rim and not small:
            out = rim(out)
        return svgk.gtk_safe(svgk.qt_safe(out))


def drawings():
    """-> {(ctx, name) or ("apps", name): fn(small) -> svg} is built by upgrade(); this lists the
    brand generators' functions by registry name: ({name: fn} from types, {name: fn} from fullset)."""
    fullset, T = _modules()
    titles = {title: fn for title, fn in T.A2}
    from_types = {name: titles[title] for name, title in APP_FROM_TYPES.items()}
    from_fullset = {name: fn for batch in sorted(fullset.BATCHES) for name, fn in fullset.BATCHES[batch]}
    return from_types, from_fullset


def upgrade(icons):
    """icons with every entry a brand generator draws replaced by its A2Icon. Fails loudly when a
    generator names an icon the registry does not have, or two generators draw the same one."""
    from_types, from_fullset = drawings()
    both = set(from_types) & set(from_fullset)
    if both:
        raise ValueError(f"a2: drawn by types.py and fullset.py both: {sorted(both)}")
    want = {**from_types, **from_fullset}
    by_name = {}
    for ic in icons:
        by_name.setdefault(ic.name, []).append(ic)
    missing = sorted(n for n in want if n not in by_name)
    if missing:
        raise ValueError(f"a2: the brand generators draw {missing}, which the registry (families.py) does not list")
    dup = sorted(n for n in want if len(by_name[n]) != 1)
    if dup:
        raise ValueError(f"a2: the registry lists {dup} more than once; a generator names an icon by name only")
    out = []
    for ic in icons:
        fn = want.get(ic.name)
        out.append(A2Icon(ic, fn) if fn else ic)
    return out
