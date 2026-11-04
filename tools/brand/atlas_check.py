# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""Rules for the Atlas badges, held to the same bars as the icon language (icons/LANGUAGE.md sections 9, 10):

  static  parses; the 1024 canvas; no <image>, <text>, <script>, <style>, <use>, clip-path, stroke or filter
          (the brand set is fill-only); ids unique and resolved; under 40 KB
  raster  (rsvg-convert, every direction, 512 / 128 / 48) the edge ring holds 1.3:1 against the light and the
          dark ground; at 48 px the glyph separates from the card (median contrast >= 1.35:1, >= 55% of its
          pixels at 1.3:1); the glyph spans 0.45..0.86 of the card width
  tokens  every colour the mocks use is a token (checked by atlas_chrome.py itself: it reads colors.json)

  python3 -I atlas_check.py <design dir>      prints one line per drawing; exit 1 when a bar fails
"""
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "icons"))
import atlas  # noqa: E402
from raster import contrast_lum, decode_png, rel_lum, render_text  # noqa: E402

FORBIDDEN = {"image", "text", "script", "style", "use", "foreignObject", "a", "animate", "set", "tspan", "filter"}
EDGE_MIN, MEDIAN_MIN, SHARE_MIN, LIVE = 1.30, 1.35, 0.55, (0.45, 0.86)


def static(name, svg):
    err = []
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as e:
        return [f"{name}: does not parse: {e}"]
    if root.get("viewBox") != "0 0 1024 1024":
        err.append(f"{name}: not on the 1024 canvas")
    for t in {el.tag.split("}")[-1] for el in root.iter()} & FORBIDDEN:
        err.append(f"{name}: <{t}>")
    if "clip-path" in svg or 'stroke="' in svg or "stroke-width" in svg:
        err.append(f"{name}: clip-path or stroke (the set is fill-only)")
    ids = re.findall(r' id="([^"]+)"', svg)
    if len(ids) != len(set(ids)):
        err.append(f"{name}: duplicate ids")
    for ref in set(re.findall(r"url\(#([^)]+)\)", svg)):
        if ref not in ids:
            err.append(f"{name}: url(#{ref}) has no target")
    if len(svg.encode()) > 40 * 1024:
        err.append(f"{name}: over 40 KB")
    return err


def card_only(key, level):
    """The badge without its glyph (for the legibility mask)."""
    k, nm, glyph, top, bot, edge = next(d for d in atlas.DIRECTIONS if d[0] == key)
    cd, cb = atlas.card(f"{k}{level}", top, bot, edge)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">'
            f'<defs>{cd}</defs>{cb}</svg>')


def lum(p):
    return rel_lum(p[:3])


def raster(key, px, tmp):
    level = {48: 0, 128: 1, 512: 2}[px]
    w, h, f = decode_png(render_text(atlas.svg_file(key, px), px, tmp))
    _, _, b = decode_png(render_text(card_only(key, level), px, tmp))
    err, m = [], {}
    xs = [x for y in range(h) for x in range(w) if b[y][x][3] > .85]
    tw = max(xs) - min(xs) + 1
    mask = [(x, y) for y in range(h) for x in range(w)
            if f[y][x][3] > .85 and b[y][x][3] > .85 and max(abs(f[y][x][i] - b[y][x][i]) for i in range(3)) > .16]
    if not mask:
        return [f"{key}{px}: no glyph found"], m
    gx, gy = [x for x, _ in mask], [y for _, y in mask]
    live = max(max(gx) - min(gx) + 1, max(gy) - min(gy) + 1) / tw
    m["live"] = live
    if not LIVE[0] <= live <= LIVE[1]:
        err.append(f"{key}{px}: glyph spans {live:.2f} of the card (want {LIVE[0]}..{LIVE[1]})")
    cs = sorted(contrast_lum(lum(f[y][x]), lum(b[y][x])) for x, y in mask)
    m["median"], m["share"] = cs[len(cs) // 2], sum(c >= 1.3 for c in cs) / len(cs)
    if px == 48 and (m["median"] < MEDIAN_MIN or m["share"] < SHARE_MIN):
        err.append(f"{key}{px}: glyph barely separates from the card ({m['median']:.2f}:1, {m['share']:.0%})")
    ring = [lum(f[y][x]) for y in range(h) for x in range(w) if f[y][x][3] >= .9 and any(
        (f[y + dy][x + dx][3] if 0 <= y + dy < h and 0 <= x + dx < w else 0.0) < .3
        for dx in (-1, 0, 1) for dy in (-1, 0, 1))]
    for g, ground in (("light", atlas.LIGHT_G), ("dark", atlas.DARK_G)):
        gl = lum(tuple(int(ground[i:i + 2], 16) / 255 for i in (1, 3, 5)))
        cr = sorted(contrast_lum(p, gl) for p in ring)
        m[f"edge/{g}"] = cr[int(len(cr) * .75)]
        if m[f"edge/{g}"] < EDGE_MIN:
            err.append(f"{key}{px}: edge holds only {m[f'edge/{g}']:.2f}:1 against the {g} ground")
    return err, m


def tokens_in_sync(design):
    """The mocks hold the 13 theme tokens of wol-light / wol-dark as constants; when the design repo sits in
    the tree (design/../crates/core/src/theme/builtin), they must equal the shipped files."""
    import json
    import atlas_chrome
    base = os.path.join(design, "..", "crates", "core", "src", "theme", "builtin")
    out = []
    for mode in ("light", "dark"):
        p = os.path.join(base, f"wol-{mode}.json")
        if not os.path.isfile(p):
            print(f"tokens: {p} not found, not compared")
            continue
        want = json.load(open(p, encoding="utf-8"))["tokens"]
        have = {k: v.lower() if v.startswith("#") else v for k, v in atlas_chrome.THEME[mode].items()}
        want = {k: v.lower() if v.startswith("#") else v for k, v in want.items()}
        if have != want:
            out.append(f"tokens: atlas_chrome.THEME[{mode}] differs from {p}")
    return out


def main(design):
    errs = tokens_in_sync(design)
    with tempfile.TemporaryDirectory() as tmp:
        for key, name, *_ in atlas.DIRECTIONS:
            for px in atlas.SIZES:
                svg = atlas.svg_file(key, px)
                e = static(f"{key}-{name}-{px}", svg)
                e2, m = raster(key, px, tmp)
                errs += e + e2
                print(f"{key} {name:10s} {px:3d}: live {m.get('live', 0):.2f}  median {m.get('median', 0):.2f}  share {m.get('share', 0):.0%}  "
                      f"edge light {m.get('edge/light', 0):.2f} dark {m.get('edge/dark', 0):.2f}  {len(svg) // 1024 or 1} KB")
    for e in errs:
        print("FAIL", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else atlas.DESIGN)))
