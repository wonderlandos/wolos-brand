# SPDX-License-Identifier: GPL-2.0-or-later
"""Read an upstream icon before redrawing it in Type A2: what the eye gets from it.

  python3 -I design/tools/brand/read_icon.py ICON.svg|png [--sheet OUT.png]

Prints the art box in fen (24-fen canvas), the dominant colours with their phase (element),
the main parts (largest connected masses: share of the art, box, centre, colour) and the
silhouette's fill ratio; the sheet shows the icon at 256/64/32/16, its silhouette, the parts
outlined and the palette swatches. The point is to keep what makes it recognisable (the
silhouette and the 2-3 biggest parts) and to redraw everything else on the module."""
import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.cluster.vq import kmeans2

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from colour import element  # noqa: E402
from score import oklab, lab2hex, _lch  # noqa: E402


def render(path, size):
    if path.endswith(".svg"):
        data = subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), path], check=True, capture_output=True).stdout
        return Image.open(io.BytesIO(data)).convert("RGBA")
    return Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)


def read(path, size=256):
    im = render(path, size)
    a = np.asarray(im).astype(float) / 255
    mask = a[..., 3] > 0.5
    fen = size / 24
    ys, xs = np.nonzero(mask)
    box = (xs.min() / fen, ys.min() / fen, (xs.max() + 1) / fen, (ys.max() + 1) / fen)
    lab = oklab(a[..., :3])
    pts = lab[mask]
    cent, lbl = kmeans2(pts[np.random.default_rng(3).choice(len(pts), min(6000, len(pts)), replace=False)], 6, minit="++", seed=3)
    d = ((lab[..., None, :] - cent[None, None]) ** 2).sum(-1)
    lab_ = d.argmin(-1)
    lab_[~mask] = -1
    pal = []
    for c in range(len(cent)):
        share = float((lab_ == c).sum() / mask.sum())
        if share > 0.01:
            pal.append((share, lab2hex(cent[c]), sorted(element(_lch(cent[c])))[0]))
    pal.sort(reverse=True)
    parts = []
    for c in range(len(cent)):
        comp, n = ndimage.label(lab_ == c)
        for i in range(1, n + 1):
            m = comp == i
            s = m.sum() / mask.sum()
            if s > 0.03:
                yy, xx = np.nonzero(m)
                parts.append((float(s), lab2hex(cent[c]), (round(xx.min() / fen, 1), round(yy.min() / fen, 1), round((xx.max() + 1) / fen, 1), round((yy.max() + 1) / fen, 1)),
                              (round(xx.mean() / fen, 1), round(yy.mean() / fen, 1))))
    parts.sort(reverse=True)
    filled = ndimage.binary_fill_holes(mask)
    fill = filled.sum() / ((box[2] - box[0]) * (box[3] - box[1]) * fen * fen)
    return {"box_fen": tuple(round(v, 1) for v in box), "fill": round(float(fill), 2), "palette": pal, "parts": parts[:8], "mask": mask, "lab": lab_}


def sheet(path, out, r):
    W, H = 1200, 420
    sh = Image.new("RGB", (W, H), (241, 241, 250))
    dr = ImageDraw.Draw(sh)
    x = 20
    for sz in (256, 64, 32, 16):
        ic = render(path, sz)
        sh.paste(ic, (x, 40 + 256 - sz), ic)
        x += sz + 20
    sil = Image.fromarray((~r["mask"] * 255).astype("uint8")).convert("RGB")
    sh.paste(sil, (x, 40))
    dr2 = ImageDraw.Draw(sh)
    fen = 256 / 24
    for s, hx, (x0, y0, x1, y1), _ in r["parts"]:
        dr2.rectangle((x + x0 * fen, 40 + y0 * fen, x + x1 * fen, 40 + y1 * fen), outline=(224, 69, 123), width=2)
    x += 276
    for i, (s, hx, el) in enumerate(r["palette"]):
        rgb = tuple(int(hx[k:k + 2], 16) for k in (1, 3, 5))
        dr.rectangle((x, 40 + i * 44, x + 40, 76 + i * 44), fill=rgb)
        dr.text((x + 50, 48 + i * 44), f"{hx} {el} {s:.0%}", fill=(21, 21, 32))
    dr.text((20, 10), f"read_icon: {os.path.basename(path)}  art box {r['box_fen']} fen  fill {r['fill']}", fill=(21, 21, 32))
    sh.save(out)


def main(argv):
    r = read(argv[0])
    print("art box (fen):", r["box_fen"], " silhouette fill:", r["fill"])
    print("palette:", [(f"{s:.0%}", hx, el) for s, hx, el in r["palette"]])
    for p in r["parts"]:
        print("part", f"{p[0]:.0%}", p[1], "box", p[2], "centre", p[3])
    if "--sheet" in argv:
        sheet(argv[0], argv[argv.index("--sheet") + 1], r)


if __name__ == "__main__":
    main(sys.argv[1:])
