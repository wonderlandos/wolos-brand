# SPDX-License-Identifier: GPL-2.0-or-later
"""Contact sheets for the UI symbolic set: current (icons/symbolic) against proposed (ui/symbolic)."""
import io
import os
import re
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "brand"))
import board as B  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(D, "ui", "symbolic")
CUR = os.path.join(D, "icons", "symbolic")
LIGHT = {"bg": (241, 241, 250), "ink": "#151520"}
DARK = {"bg": (21, 21, 29), "ink": "#F8F8FC"}


def raster(path, px, ink):
    src = open(path, encoding="utf-8").read()
    src = re.sub(r'style="color:#[0-9a-fA-F]+"', f'style="color:{ink}"', src)
    out = subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px), "-"], input=src.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(out)).convert("RGBA")


def pasteon(im, ic, xy):
    im.paste(ic, xy, ic)


def contact(names, out, cols=6, big=64):
    """cell = current big | proposed big, then proposed 24 and 16 px on light and dark, current 16 for reference"""
    cw, ch = 2 * big + 30 + 8, big + 62
    rows = (len(names) + cols - 1) // cols
    W, H = cols * cw + 24, rows * ch + 50
    im = Image.new("RGB", (W, H), B.BG)
    dr = ImageDraw.Draw(im)
    dr.text((12, 8), "symbolic: left = current, right = proposed; below: proposed 24/16 light, 24/16 dark, current 16", font=B.font(16, True), fill=B.INK)
    f = B.font(10)
    for i, n in enumerate(names):
        x0, y0 = 12 + (i % cols) * cw, 40 + (i // cols) * ch
        cur = os.path.join(CUR, f"{n}-symbolic.svg")
        new = os.path.join(OUT, "24", f"{n}-symbolic.svg")
        new16 = os.path.join(OUT, "16", f"{n}-symbolic.svg")
        if os.path.exists(cur):
            pasteon(im, raster(cur, big, LIGHT["ink"]), (x0, y0))
        if os.path.exists(new):
            pasteon(im, raster(new, big, LIGHT["ink"]), (x0 + big + 10, y0))
        y = y0 + big + 4
        x = x0
        for pth, px, th in ((new, 24, LIGHT), (new16, 16, LIGHT), (new, 24, DARK), (new16, 16, DARK), (cur, 16, LIGHT)):
            if not os.path.exists(pth):
                continue
            dr.rectangle([x, y, x + px + 7, y + px + 7], fill=th["bg"])
            pasteon(im, raster(pth, px, th["ink"]), (x + 4, y + 4))
            x += px + 14
        dr.text((x0, y + 36), n[:30], font=f, fill=B.DIM)
    im.save(out)
    return out


def large(names, out, cols=6, px=96):
    cw = px + 40
    rows = (len(names) + cols - 1) // cols
    im = Image.new("RGB", (cols * cw + 20, rows * (px + 36) * 2 + 20), B.BG)
    dr = ImageDraw.Draw(im)
    for i, n in enumerate(names):
        x, y = 10 + (i % cols) * cw, 10 + (i // cols) * (px + 36) * 2
        for row, p in enumerate((os.path.join(CUR, f"{n}-symbolic.svg"), os.path.join(OUT, "24", f"{n}-symbolic.svg"))):
            if os.path.exists(p):
                pasteon(im, raster(p, px, "#151520"), (x + 8, y + row * (px + 18)))
        dr.text((x, y + 2 * px + 16 + 4), n[:20], font=B.font(10), fill=B.DIM)
    im.save(out)
