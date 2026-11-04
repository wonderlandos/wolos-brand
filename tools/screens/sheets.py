# SPDX-License-Identifier: GPL-2.0-or-later
"""Score screens (tools/east/score.py, kind screen, with the layout tree) and compose current-vs-proposed boards.

  scored(png, tree)  -> {"rules": {...}, "total": x}
  compose(title, rows, out, notes)   rows = [(label, golden_png_or_None, cur_png, new_png, scores...)]"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
EAST = os.path.normpath(os.path.join(HERE, "..", "east"))
sys.path.insert(0, EAST)
import board as EB  # noqa: E402  (fonts, colours, scored)
import score as SC  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

RULES = SC.RULES


def scored(png, tree_json=None):
    s = EB.scored(png, "screen", tree_json)
    return s


def fmt(v):
    return f"{v:.1f}"


def compose(title, panels, out, scores, caption_lines=(), thumb_w=640, sub=""):
    """panels: list of rows; each row = list of (label, png) shown left to right (thumb_w wide).
    scores: dict label -> score dict (from scored) for the table at the right: first = base, last = proposed."""
    cols = max(len(r) for r in panels)
    ims = []
    for row in panels:
        ims.append([(lab, Image.open(p).convert("RGB")) for lab, p in row])
    th = round(thumb_w * ims[0][0][1].height / ims[0][0][1].width)
    pad, top, tab = 16, 64, 380
    W = pad + cols * (thumb_w + pad) + tab
    H = top + len(panels) * (th + 34) + 20
    im = Image.new("RGB", (W, H), EB.BG)
    dr = ImageDraw.Draw(im)
    dr.text((pad, 12), title, font=EB.font(22, True), fill=EB.INK)
    if sub:
        dr.text((pad, 40), sub, font=EB.font(13), fill=EB.DIM)
    for r, row in enumerate(ims):
        y = top + r * (th + 34)
        for c, (lab, img) in enumerate(row):
            x = pad + c * (thumb_w + pad)
            im.paste(img.resize((thumb_w, th), Image.LANCZOS), (x, y + 22))
            dr.text((x, y), lab, font=EB.font(13, True), fill=EB.INK)
            dr.rectangle((x - 1, y + 21, x + thumb_w, y + 22 + th), outline=EB.LINE)
    # score table (base -> proposed) for each mode
    x0 = pad + cols * (thumb_w + pad)
    y = top
    for key, (a, b, lab) in scores.items():
        dr.text((x0, y), lab, font=EB.font(14, True), fill=EB.INK)
        y += 22
        y = EB.score_lines(dr, x0, y, a, b, 13) + 10
    im.save(out)
    return out


def run_scores(jobs):
    """jobs: list of (png, tree_or_None); parallel."""
    with ThreadPoolExecutor(max_workers=4) as ex:
        return list(ex.map(lambda j: scored(*j), jobs))
