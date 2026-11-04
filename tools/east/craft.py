# SPDX-License-Identifier: GPL-2.0-or-later
"""Craft checks for an icon SVG: the bugs a score does not see.

  python3 -I design/tools/east/craft.py FILE.svg [...]      exit 1 on any failure

  overflow  nothing touches the canvas edge (a clipped shadow or glyph shows as a cut line):
            max alpha in the outer 1 % ring of a 512 px render < 0.02
  holes     inside the card, nothing is see-through (a hole must show the card, not the desktop):
            min alpha in the card's core (silhouette eroded by 1 fen) >= 0.99
  refs      every url(#id) is defined; every clipPath and mask has drawable content
  layers    a blurred shadow is never the last thing drawn (it would sit on top of what casts it),
            and every shadow is followed by an unfiltered shape
  contrast  at 16 px the glyph holds 3:1 against the card (brightest vs dominant colour)
  nearmiss  two pieces of the glyph closer than 0.6 fen that do not touch (a handle that stops
            short of its bag reads as an error): every such pair fails
  centring  a piece inside a hole or a disc (the keyhole in the gear hub, the mark in a seal) has
            its ink-box centre on the centre of that hole within 0.15 fen (1/24 of the canvas = 1 fen)
"""
import io
import re
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage


def render(path, size):
    out = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), path], check=True, capture_output=True).stdout
    return np.asarray(Image.open(io.BytesIO(out)).convert("RGBA")).astype(float) / 255


def lum(rgb):
    c = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return c @ np.array([0.2126, 0.7152, 0.0722])


def centring(path, size=480, tol_fen=0.15):
    """Render without filters (shadows would shift the ink). Card-coloured pixels are those near
    the card's fitted ground (score.Px field); a hole is a card-coloured region enclosed by glyph;
    the ink inside it (a filled glyph region within the hole's outline) must be centred on it."""
    src = open(path, encoding="utf-8").read()
    flat = re.sub(r'<path[^>]*filter="url\([^)]*\)"[^>]*/>', "", src)
    flat = re.sub(r'<path class="shade"[^>]*/>', "", flat)      # shadow strokes are not ink
    import os
    import tempfile
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import score as SC
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as t:
        t.write(flat)
    try:
        p = SC.Px(SC.load(t.name, size), "icon")
    finally:
        os.unlink(t.name)
    fen = size / 24
    cardish = p.mask & (p.de < 0.08)
    glyph = p.mask & ~cardish
    glyph_filled = ndimage.binary_fill_holes(glyph)
    holes, hn = ndimage.label(cardish & glyph_filled)
    worst, where = 0.0, ""
    for j in range(1, hn + 1):
        h = holes == j
        if h.sum() < (fen * 1.0) ** 2:
            continue
        outline = ndimage.binary_fill_holes(h | ndimage.binary_dilation(h, iterations=1) & ~glyph)
        outline = ndimage.binary_fill_holes(h)
        inner = ndimage.binary_fill_holes(h) & ~h
        # the ink inside: glyph pixels enclosed by this hole
        lab, n = ndimage.label(glyph)
        ink = np.zeros_like(h)
        hole_hull = ndimage.binary_fill_holes(h | ink)
        for i in range(1, n + 1):
            comp = lab == i
            ring = ndimage.binary_dilation(comp, iterations=2) & ~comp
            if ring.any() and (h[ring].mean() > 0.6):
                ink |= comp
        if ink.sum() < (fen * 0.5) ** 2:
            continue
        hy, hx = np.nonzero(h | ink)
        iy, ix = np.nonzero(ink)
        dc = np.hypot((hx.min() + hx.max()) / 2 - (ix.min() + ix.max()) / 2,
                      (hy.min() + hy.max()) / 2 - (iy.min() + iy.max()) / 2) / fen
        if dc > worst:
            worst, where = dc, f"hole at ({hx.mean() / fen:.1f}, {hy.mean() / fen:.1f}) fen"
    return worst <= tol_fen, f"worst offset {worst:.2f} fen {where}".strip()


def _flat(path, size):
    import os
    import tempfile
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import score as SC
    src = open(path, encoding="utf-8").read()
    flat = re.sub(r'<path[^>]*filter="url\([^)]*\)"[^>]*/>', "", src)
    flat = re.sub(r'<path class="shade"[^>]*/>', "", flat)
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as t:
        t.write(flat)
    try:
        return SC.Px(SC.load(t.name, size), "icon")
    finally:
        os.unlink(t.name)


def nearmiss(path, size=480, gap_fen=0.6):
    p = _flat(path, size)
    fen = size / 24
    glyph = p.mask & (p.de >= 0.08)
    lab, n = ndimage.label(glyph)
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    keep = [i + 1 for i, s in enumerate(sizes) if s >= (0.4 * fen) ** 2]
    misses = []
    for i in keep:
        d = ndimage.distance_transform_edt(lab != i)
        for j in keep:
            if j <= i:
                continue
            m = d[lab == j].min()
            if 1.5 < m <= gap_fen * fen:          # 1.5 px: anti-aliasing seam, not a gap
                ys, xs = np.nonzero(lab == j)
                misses.append(f"{m / fen:.2f} fen near ({xs.mean() / fen:.1f}, {ys.mean() / fen:.1f})")
    return not misses, ("none" if not misses else "; ".join(misses[:3]))


def check(path):
    res = {}
    a = render(path, 512)
    al = a[..., 3]
    ring = max(2, round(512 * 0.01))
    edge = np.concatenate([al[:ring].ravel(), al[-ring:].ravel(), al[:, :ring].ravel(), al[:, -ring:].ravel()])
    res["overflow"] = (edge.max() < 0.02, f"edge alpha max {edge.max():.3f}")
    solid = al > 0.98
    lab, n = ndimage.label(solid)
    if n:
        big = lab == (np.argmax(ndimage.sum(solid, lab, range(1, n + 1))) + 1)
        filled = ndimage.binary_fill_holes(big)
        core = ndimage.binary_erosion(filled, iterations=round(512 / 24))
        mn = al[core].min() if core.any() else 1.0
        res["holes"] = (mn >= 0.99, f"core alpha min {mn:.3f}")
    else:
        res["holes"] = (False, "no opaque card")
    src = open(path, encoding="utf-8").read()
    ids = set(re.findall(r'\bid="([^"]+)"', src))
    used = set(re.findall(r'url\(#([^)]+)\)', src))
    missing = sorted(used - ids)
    empty = [m for m in re.findall(r'<(?:clipPath|mask) id="([^"]+)">(.*?)</(?:clipPath|mask)>', src)
             if not re.search(r'<(path|rect|circle|ellipse)[^>]*(d="[^"]+"|width=)', m[1])]
    res["refs"] = (not missing and not empty, f"missing {missing} empty {[e[0] for e in empty]}")
    body = src[src.find("</defs>") + 7:] if "</defs>" in src else src
    els = re.findall(r'<(?:path|rect|circle|ellipse|g)\b[^>]*>', body)
    shadows = [i for i, e in enumerate(els) if 'filter="url(' in e]
    last_is_shadow = bool(els) and 'filter="url(' in els[-1]
    orphan = [i for i in shadows if not any('filter="url(' not in e for e in els[i + 1:])]
    res["layers"] = (not last_is_shadow and not orphan, f"{len(shadows)} shadows, orphan {len(orphan)}")
    res["centring"] = centring(path)
    res["nearmiss"] = nearmiss(path)
    # 16 px is drawn from the small variant when one exists (icons/apps/small, east/*/small)
    import os as _os
    sib = _os.path.join(_os.path.dirname(path), "small", _os.path.basename(path))
    s16 = render(sib if _os.path.exists(sib) else path, 16)
    m = s16[..., 3] > 0.9
    L = lum(s16[..., :3])[m]
    if L.size:
        dom = np.median(L)
        hi = np.quantile(L, 0.97)
        lo = np.quantile(L, 0.03)
        cr = max((hi + 0.05) / (dom + 0.05), (dom + 0.05) / (lo + 0.05))
        res["contrast"] = (cr >= 3.0, f"16px {cr:.2f}:1")
    else:
        res["contrast"] = (False, "empty at 16 px")
    return res


def main(argv):
    bad = 0
    import os as _os
    sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
    from par import fanout
    results = fanout(check, argv)      # fork/join over files
    for p, r in zip(argv, results):
        fails = [k for k, (ok, _) in r.items() if not ok]
        bad += bool(fails)
        print(f"{'PASS' if not fails else 'FAIL'} {p}")
        for k, (ok, why) in r.items():
            print(f"   {'ok ' if ok else 'BAD'} {k:9s} {why}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
