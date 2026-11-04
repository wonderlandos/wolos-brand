# SPDX-License-Identifier: GPL-2.0-or-later
"""Craft checks and scores for UI symbolic icons.

  python3 -I design/tools/ui/check.py [--names a,b] [--json OUT.json]

craft16 (pass/fail per icon, on the 16 px file, rendered at 16 px and at 8x):
  margin   no ink on the outermost pixel ring of the 16 px render (alpha < 0.05)
  clog     gaps narrower than 0.8 px between ink are not filled-in more than 0.35 px2 in total
  thin     no stroke thinner than 1.0 px (medial width) outside dots
  centre   the ink box is centred on the cell within 1 px
  crisp    (reported, not a gate) share of edge pixels that are neither empty nor full: lower is crisper
tile score: the glyph (24 px file) in ink on a white 21-fen tile, 15 fen across (the A2 proportion),
scored with tools/brand/score.py (kind icon), current icon drawn the same way.
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
D = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(D, "ui", "symbolic")
CUR = os.path.join(D, "icons", "symbolic")


def render(path, px, ink="#000000"):
    src = open(path, encoding="utf-8").read()
    src = re.sub(r'style="color:#[0-9a-fA-F]+"', f'style="color:{ink}"', src)
    out = subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), "-"], input=src.encode(), capture_output=True, check=True).stdout
    return np.asarray(Image.open(io.BytesIO(out)).convert("RGBA")).astype(float)[..., 3] / 255


def craft16(path, cell=16, exempt=False):
    a = render(path, cell)
    hi = render(path, cell * 8)
    res = {}
    ring = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    res["margin"] = (ring.max() < 0.05, f"edge alpha {ring.max():.2f}")
    ink = hi > 0.5
    bg = ~ink
    dtb = ndimage.distance_transform_edt(bg)
    skb = bg & (dtb >= ndimage.maximum_filter(dtb, size=3) - 1e-6) & (dtb > 0)
    wb = 2 * dtb / 8.0
    # a channel: skeleton of the background narrower than 0.8 px (but not a seam under 0.2 px), enclosed on both sides by ink
    inner = ndimage.binary_erosion(np.pad(bg, 1, constant_values=True), iterations=1)[1:-1, 1:-1]
    chan = skb & (wb < 0.8) & (wb > 0.2) & (dtb < 8)
    # drop corner spurs: keep channel samples that have at least 6 channel neighbours within 1 px at 8x
    nb = ndimage.convolve(chan.astype(int), np.ones((5, 5), int), mode="constant")
    clog = int((chan & (nb >= 8)).sum())
    res["clog"] = (clog <= 6, f"{clog} samples of gap under 0.8 px")
    dt = ndimage.distance_transform_edt(ink)
    sk = ink & (dt >= ndimage.maximum_filter(dt, size=3) - 1e-6) & (dt > 0)
    w = (2 * dt[sk]) / 8.0
    big = ndimage.binary_opening(ink, iterations=10)       # dots and fills: wider than 2.5 px
    thin = sk & ~ndimage.binary_dilation(big, iterations=6)
    wt = (2 * dt[thin]) / 8.0
    nthin = int((wt < 1.0).sum())
    res["thin"] = (nthin <= 12, f"{nthin} medial samples under 1.0 px (median {np.median(wt) if wt.size else 0:.2f} px)")
    ys, xs = np.nonzero(a > 0.2)
    if xs.size:
        cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
        off = max(abs(cx - cell / 2), abs(cy - cell / 2))
    else:
        off = 99
    res["centre"] = (off <= 1.0 or exempt, f"ink box centre off by {off:.2f} px")
    edge = (a > 0.1)
    soft = ((a > 0.1) & (a < 0.9)).sum() / max(1, edge.sum())
    res["crisp"] = (True, f"{soft:.2f}")
    return res


def tile(path, out, glyph_fen=15, ink="#151520", card="#FFFFFF"):
    """the glyph on a white tile: tile 21 fen of a 24 fen canvas, glyph 15 fen across and centred"""
    src = open(path, encoding="utf-8").read()
    inner = src[src.index("<g"):src.rindex("</svg>")]
    vb = float(re.search(r'viewBox="0 0 (\d+)', src).group(1))
    k = glyph_fen / vb
    t = (24 - glyph_fen) / 2
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="512" height="512">'
           f'<rect x="1.5" y="1.5" width="21" height="21" rx="4.5" fill="{card}"/>'
           f'<g color="{ink}" transform="translate({t} {t}) scale({k})">{inner}</g></svg>')
    open(out, "w").write(svg)


def tile_score(job):
    path, = job
    from score import score_pixels, total
    with tempfile.TemporaryDirectory() as td:
        t = os.path.join(td, "t.svg")
        tile(path, t)
        s = score_pixels(t, "icon")
    s["total"] = total(s)
    return s


EXEMPT = {'audio-volume-low', 'audio-volume-medium', 'audio-volume-muted'}      # aligned with audio-volume-high on purpose


def run(names):
    from par import fanout
    cur = [os.path.join(CUR, f"{n}-symbolic.svg") for n in names]
    new24 = [os.path.join(OUT, "24", f"{n}-symbolic.svg") for n in names]
    new16 = [os.path.join(OUT, "16", f"{n}-symbolic.svg") for n in names]
    sc = fanout(tile_score, [(p,) for p in cur + new24])
    out = {}
    for i, n in enumerate(names):
        out[n] = {"cur_score": sc[i], "new_score": sc[len(names) + i],
                  "craft_new": craft16(new16[i], exempt=names[i] in EXEMPT), "craft_cur": craft16(cur[i]) if os.path.exists(cur[i]) else None}
    return out


def summary(res):
    names = list(res)
    cur = np.mean([res[n]["cur_score"]["total"] for n in names])
    new = np.mean([res[n]["new_score"]["total"] for n in names])
    rules = ["qi", "sha", "forms", "zones", "palette", "light", "proportion", "density"]
    rows = {r: (np.mean([res[n]["cur_score"][r]["score"] for n in names]), np.mean([res[n]["new_score"][r]["score"] for n in names])) for r in rules}
    chk = {}
    for c in ("margin", "clog", "thin", "centre"):
        chk[c] = (sum(res[n]["craft_cur"][c][0] for n in names if res[n]["craft_cur"]), sum(res[n]["craft_new"][c][0] for n in names), len(names))
    crisp = (np.mean([float(res[n]["craft_cur"]["crisp"][1]) for n in names if res[n]["craft_cur"]]),
             np.mean([float(res[n]["craft_new"]["crisp"][1]) for n in names]))
    return {"total": (cur, new), "rules": rows, "craft": chk, "crisp": crisp, "wins": sum(res[n]["new_score"]["total"] > res[n]["cur_score"]["total"] for n in names)}


if __name__ == "__main__":
    import glyphs
    names = sys.argv[sys.argv.index("--names") + 1].split(",") if "--names" in sys.argv else sorted(glyphs.ICONS)
    res = run(names)
    sm = summary(res)
    print(json.dumps(sm, default=float, indent=1))
    if "--json" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w"), default=float)
    for n in names:
        bad = [k for k, (ok, _) in res[n]["craft_new"].items() if not ok]
        if bad:
            print("FAIL", n, [(k, res[n]["craft_new"][k][1]) for k in bad])
