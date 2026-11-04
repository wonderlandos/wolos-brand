# SPDX-License-Identifier: GPL-2.0-or-later
"""A family board: several pages of one surface, rows = pages, columns = current (light), proposed (light), proposed (dark).
  python3 -I family.py NAME OUT.png KEY [KEY ...]     (each KEY already built by build.py)"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "east"))
import board as EB  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

OUT = os.path.normpath(os.path.join(HERE, "..", "..", "screens"))


def family(title, keys, out, labels=None, thumb_w=440, sub=""):
    rows = []
    for k in keys:
        sc = json.load(open(os.path.join(OUT, k, "scores.json")))
        rows.append((k, sc))
    first = Image.open(os.path.join(OUT, keys[0], "cur-light.png"))
    th = round(thumb_w * first.height / first.width)
    pad, top, tab = 16, 64, 330
    W = pad + 3 * (thumb_w + pad) + tab
    H = top + len(rows) * (th + 30) + 16
    im = Image.new("RGB", (W, H), EB.BG)
    dr = ImageDraw.Draw(im)
    dr.text((pad, 10), title, font=EB.font(22, True), fill=EB.INK)
    dr.text((pad, 38), sub, font=EB.font(13), fill=EB.DIM)
    heads = ("Atual, claro", "Proposto, claro", "Proposto, escuro")
    x0 = pad + 3 * (thumb_w + pad)
    dr.text((x0, top - 4), "claro / escuro: atual -> proposto", font=EB.font(13, True), fill=EB.INK)
    for r, (k, sc) in enumerate(rows):
        y = top + r * (th + 30)
        for c, f in enumerate(("cur-light", "new-light", "new-dark")):
            x = pad + c * (thumb_w + pad)
            img = Image.open(os.path.join(OUT, k, f + ".png")).convert("RGB").resize((thumb_w, th), Image.LANCZOS)
            im.paste(img, (x, y + 18))
            dr.text((x, y), (labels or {}).get(k, sc["title"]) + " | " + heads[c], font=EB.font(12, True), fill=EB.INK)
        yy = y + 18
        dr.text((x0, yy), (labels or {}).get(k, sc["title"]), font=EB.font(13, True), fill=EB.INK)
        for i, m in enumerate(("light", "dark")):
            a, b = sc[m]["cur"]["total"], sc[m]["new"]["total"]
            dr.text((x0, yy + 20 + i * 20), "claro " if m == "light" else "escuro", font=EB.font(13), fill=EB.DIM)
            dr.text((x0 + 70, yy + 20 + i * 20), f"{a:5.1f}  ->  ", font=EB.font(13), fill=EB.INK)
            dr.text((x0 + 150, yy + 20 + i * 20), f"{b:5.1f}", font=EB.font(13, True), fill=EB.GOOD if b > a else EB.BAD)
    im.save(out)
    return out


if __name__ == "__main__":
    family(sys.argv[1], sys.argv[3:], sys.argv[2])
