# SPDX-License-Identifier: GPL-2.0-or-later
"""The rules every full-colour icon is held to before anything is written (design/icons/LANGUAGE.md sections 3, 9 and 10).

Static, on the SVG text: parses; the 1024 canvas; no <image>, <text>, <script>, <style>, <use> or
foreign content; filters from the rsvg-safe primitives only (the same list as
crates/shell/tests/icons_v2.rs SAFE_FILTER, a test keeps them equal); no banned system colour; every url(#id)
resolves and ids are unique; no gloss sweep; under 40 KB.

Raster, on what rsvg-convert draws (the renderer GTK loads SVG with), for BOTH variants:
  - live area: the glyph (pixels that differ from the same icon without its glyph) spans the
    tile by LIVE_SMALL / LIVE_FULL (fractions of the tile's width);
  - legibility at 48 px: the glyph separates from the tile under it, by luminance contrast
    (median over the glyph pixels) and by the share of pixels that carry at least 1.3:1;
  - silhouette: the ring of pixels along the edge holds EDGE_MIN:1 against the light and the dark
    ground (the rim light and the hairline count, as they do on screen);
  - the 16 px symbolic derivative exists where the theme expects one (build.py)."""
import re
import tempfile
import xml.etree.ElementTree as ET

from palette import GROUND_DARK, GROUND_LIGHT
from raster import contrast_lum, decode_png, rel_lum, render_text

MAX_BYTES = 40 * 1024
SAFE_FILTER = {"filter", "feGaussianBlur", "feOffset", "feFlood", "feComposite", "feMerge", "feMergeNode",
               "feColorMatrix", "feTurbulence", "feBlend"}   # no lighting: GTK 4 draws it black (gtkcheck)
FORBIDDEN = {"image", "text", "script", "style", "use", "foreignObject", "a", "animate", "set", "tspan"}
# Colours the set left behind (INVENTORY.md): never again in a shipped icon.
BANNED = {"#FF3B30", "#FF9500", "#FFCC00", "#34C759", "#007AFF", "#FF453A", "#FF9F0A", "#FFD60A",
          "#30D158", "#0A84FF", "#FF5F57", "#FEBC2E", "#28C840", "#FF2D55", "#5AC8FA", "#8E8E93"}

LIVE_SMALL = (0.62, 0.84)     # glyph span / tile width at 48 px (target about 0.70)
LIVE_FULL = (0.56, 0.86)
LEGIBLE_MEDIAN = 1.35         # median contrast of glyph pixels against the tile under them
LEGIBLE_SHARE = 0.55          # share of glyph pixels with at least 1.3:1
EDGE_MIN = 1.30               # edge ring against each ground (lit lip, hairline and rim included)


def static(icon, svg):
    err = []
    n = icon.name
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        return [f"{n}: does not parse: {e}"]
    if root.get("viewBox") != "0 0 1024 1024":
        err.append(f"{n}: not on the 1024 canvas")
    tags = [el.tag.split("}")[-1] for el in root.iter()]
    for t in set(tags):
        if t in FORBIDDEN:
            err.append(f"{n}: <{t}>")
    prim = {t for t in tags if t.startswith("fe")} | ({"filter"} if "filter" in tags else set())
    for t in sorted(prim - SAFE_FILTER):
        err.append(f"{n}: filter primitive <{t}> is not in the safe list")
    if "gloss" in svg or "mix-blend-mode" in svg:
        err.append(f"{n}: gloss sweep or blend mode")
    for c in set(re.findall(r"#[0-9A-Fa-f]{6}\b", svg)):
        if c.upper() in BANNED:
            err.append(f"{n}: banned colour {c}")
    ids = re.findall(r' id="([^"]+)"', svg)
    if len(ids) != len(set(ids)):
        err.append(f"{n}: duplicate ids")
    for ref in set(re.findall(r"url\(#([^)]+)\)", svg)):
        if ref not in ids:
            err.append(f"{n}: url(#{ref}) has no target")
    if len(svg.encode()) > MAX_BYTES:
        err.append(f"{n}: {len(svg.encode()) // 1024} KB (over {MAX_BYTES // 1024})")
    return err


def _px(png):
    return decode_png(png)


def _lum(p):
    return rel_lum(p)


def raster(icon, small, size, tmp):
    """-> (errors, metrics) for one variant at `size` px."""
    n = icon.name + (" (small)" if small else "")
    w, h, f = _px(render_text(icon.svg(small), size, tmp))
    _, _, b = _px(render_text(icon.svg(small, tile_only=True), size, tmp))
    err, m = [], {}
    # the tile: where the icon without its glyph is opaque
    xs = [x for y in range(h) for x in range(w) if b[y][x][3] > .85]
    if not xs:
        return [f"{n}: nothing drawn"], m
    tw = max(xs) - min(xs) + 1
    # glyph mask: pixels that differ from the icon without the glyph (soft shadows fall below the threshold)
    mask = []
    for y in range(h):
        for x in range(w):
            a, c = f[y][x], b[y][x]
            if a[3] < .85 or c[3] < .85:
                continue
            if max(abs(a[i] - c[i]) for i in range(3)) > 0.16:
                mask.append((x, y))
    if not mask and not icon.glyph:
        mask = [(w // 2, h // 2)]          # a plain object (a folder): no glyph to read
    if not mask:
        return [f"{n}: no glyph found"], m
    gx = [x for x, y in mask]
    gy = [y for x, y in mask]
    live = max(max(gx) - min(gx) + 1, max(gy) - min(gy) + 1) / tw
    m["live"] = live
    lo, hi = LIVE_SMALL if small else LIVE_FULL
    if icon.name.startswith("kit-"):
        lo = lo - 0.06                      # the lid takes the top of the card
    if icon.tile and not (lo <= live <= hi):
        err.append(f"{n}: glyph spans {live:.2f} of the tile (want {lo}..{hi})")
    cs = sorted(contrast_lum(_lum(f[y][x][:3]), _lum(b[y][x][:3])) for x, y in mask)
    med = cs[len(cs) // 2]
    share = sum(1 for c in cs if c >= 1.3) / len(cs)
    m["median"], m["share"] = med, share
    if small and icon.glyph and (med < LEGIBLE_MEDIAN or share < LEGIBLE_SHARE):
        err.append(f"{n}: glyph barely separates from the tile (median {med:.2f}:1, {share:.0%} of pixels >= 1.3:1)")
    # edge ring: opaque pixels with a transparent neighbour (the silhouette's own edge). Its lit lip,
    # hairline or rim count, so the test is the 75th percentile of the ring's per-pixel contrast.
    ring = []
    for y in range(h):
        for x in range(w):
            if f[y][x][3] < .9:
                continue
            if any((f[y + dy][x + dx][3] if 0 <= y + dy < h and 0 <= x + dx < w else 0.0) < .3
                   for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                ring.append(_lum(f[y][x][:3]))
    if ring:
        for g, ground in (("light", GROUND_LIGHT), ("dark", GROUND_DARK)):
            gl = _lum(tuple(int(ground.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)))
            cr = sorted(contrast_lum(p, gl) for p in ring)
            m[f"edge/{g}"] = cr[int(len(cr) * .75)]
        worst = min(m["edge/light"], m["edge/dark"])
        if worst < EDGE_MIN:
            err.append(f"{n}: edge holds only {worst:.2f}:1 against the {'light' if m['edge/light'] < m['edge/dark'] else 'dark'} ground")
    return err, m


def check(icon, deep=True):
    """-> (errors, metrics) for one icon; deep renders and reads pixels."""
    errs, rows = [], {}
    for small in (False, True):
        errs += static(icon, icon.svg(small))
    if deep:
        with tempfile.TemporaryDirectory() as t:
            for small, size in ((False, 128), (True, 48)):
                e, m = raster(icon, small, size, t)
                errs += e
                rows["small" if small else "full"] = m
    return errs, rows
