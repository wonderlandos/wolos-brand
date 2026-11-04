# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""Atlas (the WolOS browser): three logo directions and the contact sheet.  Fill-only SVG, no strokes,
no filters, no clip-paths, no text.  Stdlib only; the PNG needs rsvg-convert.

  python3 -I atlas.py <design dir>            write brand/atlas/directions/*.svg and contact-sheet.png
  python3 -I atlas.py <design dir> --check    fail when a file on disk is not what the generator writes

Each direction is a flat single-glyph badge in the family of the Cryswol gem: one white glyph in three
facet tones (95 / 75 / 50 %), one gold pop, on a card.  The card is the WolOS soft card (icons/LANGUAGE.md
section 3), the colours are the tokens (tokens/colors.json).  A drawing exists at three sizes:
512 (full), 128 (mid: no fine detail) and 48 (small: the silhouette, the light/dark split, the pop).
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "icons"))
from svgk import CARD, rr_path  # noqa: E402  (the soft card path of the icon language)

DESIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
_T = json.load(open(os.path.join(DESIGN, "tokens", "colors.json"), encoding="utf-8"))
GOLD, GOLD_D = "#FFC94A", "#F0A81E"          # tokens icon.categories pop / language ramp
LIGHT_G, DARK_G = _T["light"]["bg"], _T["dark"]["bg"]
INK_L, INK_D = _T["light"]["text"], _T["dark"]["text"]
SIZES = (512, 128, 48)


def n(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def poly(pts):
    return "M" + "L".join(f"{n(x)} {n(y)}" for x, y in pts) + "Z"


def circ(cx, cy, r):
    return f"M{n(cx - r)} {n(cy)}a{n(r)} {n(r)} 0 1 0 {n(2 * r)} 0a{n(r)} {n(r)} 0 1 0 {n(-2 * r)} 0Z"


def lin(gid, stops, x1=0, y1=0, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a < 1 else "") + "/>"
                for o, c, a in stops)
    return f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rad(gid, stops, cx=.5, cy=.5, r=.5, fx=None, fy=None):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a < 1 else "") + "/>"
                for o, c, a in stops)
    f = f' fx="{fx}" fy="{fy}"' if fx is not None else ""
    return f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'


# the rim: the card's edge minus the card inset by 7 units, as one even-odd path (no stroke)
INSET = rr_path(107, 107, 917, 917, 229, 143, 229, 143, n_=3.1)


def card(uid, top, bot, edge):
    """The soft card: ramp, top glow, bottom darkening, lit rim (white 70% at the top, gone by 45%, 16% at the
    very bottom), in fills only.  `edge` is the near-black of the hue; it darkens the bottom."""
    defs = (lin(f"{uid}r", [(0, top, 1), (1, bot, 1)]) +
            rad(f"{uid}g", [(0, "#FFFFFF", .26), (1, "#FFFFFF", 0)], .5, 0, .75) +
            lin(f"{uid}d", [(.55, edge, 0), (1, edge, .30)]) +
            lin(f"{uid}l", [(0, "#FFFFFF", .70), (.12, "#FFFFFF", .30), (.45, "#FFFFFF", 0),
                            (.78, "#FFFFFF", 0), (1, "#FFFFFF", .16)]))
    body = (f'<path d="{CARD}" fill="url(#{uid}r)"/>'
            f'<path d="{CARD}" fill="url(#{uid}g)"/>'
            f'<path d="{CARD}" fill="url(#{uid}d)"/>'
            f'<path d="{CARD}{INSET}" fill="url(#{uid}l)" fill-rule="evenodd"/>')
    return defs, body


def gold_ball(uid, cx, cy, r, detail):
    """A gold sphere: ramp light top-left to deep bottom-right; at detail >= 1 a pale lit crescent."""
    defs = rad(f"{uid}b", [(0, "#FFF0B3", 1), (.5, GOLD, 1), (1, GOLD_D, 1)], .38, .32, .85)
    body = f'<path d="{circ(cx, cy, r)}" fill="url(#{uid}b)"/>'
    if detail >= 1:
        body += (f'<path d="{circ(cx - r * .28, cy - r * .34, r * .22)}" fill="#FFFFFF" fill-opacity=".85"/>')
    return defs, body


# ------------------------------------------------------------------------------------------ A: Bearer
# The letter A as two legs with a gold world wedged where the crossbar would be: Atlas carries it.
# Legs lean 19.1 deg (slope .347), flat apex 120 wide, leg width 150; the ball touches both inner edges.
def glyph_bearer(uid, level):
    sin_t = .327                                          # sin of the leg lean: inner edges meet at 2 x 19.1 deg
    apex_l, apex_r, top = 452, 572, 200
    foot_ol, foot_or, foot_il, foot_ir, base = 230, 794, 380, 644, 840
    cy_in = 460                                           # where the inner edges meet
    r = 84
    if level == 0:      # small: legs a little heavier so the A holds at 48 px
        apex_l, apex_r, foot_ol, foot_or, foot_il, foot_ir, cy_in = 442, 582, 220, 804, 402, 622, 440
        r = 90
    ball_cy = cy_in + r / sin_t * (1 if level else .97)   # the ball rests against both inner edges
    left = [(apex_l, top), (512, top), (512, cy_in), (foot_il, base), (foot_ol, base)]
    right = [(512, top), (apex_r, top), (foot_or, base), (foot_ir, base), (512, cy_in)]
    defs, ball = gold_ball(uid, 512, ball_cy, r, level)
    body = (f'<path d="{poly(left)}" fill="#fff" fill-opacity=".95"/>'
            f'<path d="{poly(right)}" fill="#fff" fill-opacity=".62"/>' + ball)
    return defs, body


# ------------------------------------------------------------------------------------------ B: Folio
# A map folded in three (a Z-fold seen in perspective: the ridges nearer the eye are taller), with
# the gold "you are here" mark on the middle panel and, at full size, a short route towards it.
def glyph_folio(uid, level):
    xs = (200, 408, 616, 824)
    tops = (276, 206, 276, 206)
    bots = (748, 838, 748, 838)
    if level == 0:
        xs = (190, 405, 619, 834)
    panels = []
    for i, op in enumerate((.95, .58, .95)):
        a, b = i, i + 1
        pts = [(xs[a], tops[a]), (xs[b], tops[b]), (xs[b], bots[b]), (xs[a], bots[a])]
        panels.append(f'<path d="{poly(pts)}" fill="#fff" fill-opacity="{op}"/>')
    mx, my = 512, 540
    defs, ball = gold_ball(uid, mx, my, 74 if level else 84, 0)   # the white core is its highlight
    body = "".join(panels)
    if level >= 1:      # a white core (the place) inside a gold ring
        body += f'<path d="{circ(mx, my, 74 + 30)}" fill="{GOLD}" fill-opacity=".30"/>'
    body += ball
    if level >= 1:
        body += f'<path d="{circ(mx, my, 24)}" fill="#fff"/>'
    if level >= 2:      # the route: a dotted curve from the lower left panel to the mark, dots getting larger
        for k in range(5):
            t = k / 5
            x = 262 + (mx - 262) * t - 40 * math.sin(math.pi * t)
            y = 700 + (my + 90 - 700) * t + 20 * math.sin(math.pi * t)
            body += f'<path d="{circ(x, y, 10 + 3 * k)}" fill="{GOLD_D}" fill-opacity="{.55 + .09 * k:.2f}"/>'
    return defs, body


# ------------------------------------------------------------------------------------------ C: Threshold
# The Atlas mountains with the WolOS door in their foot: light comes through.  A single peak, a ridge
# splitting a lit face from a shaded one, the door an arch (the mark's door proportions 640 x 700).
def glyph_threshold(uid, level):
    apex = (472, 190)
    bl, br = (180, 840), (852, 840)
    ridge = (660, 840)
    saddle, peak2 = (596, 470), (724, 340)
    left = [apex, ridge, bl]
    right = [apex, saddle, peak2, br, ridge]               # the shaded side, with the lesser peak
    dx0, dx1 = 392, 552                                   # door, 160 wide
    dh = 350 if level else 380
    if level == 0:
        dx0, dx1 = 380, 564
    r = (dx1 - dx0) / 2
    top = 840 - dh
    door = f"M{dx0} 840V{n(top + r)}A{n(r)} {n(r)} 0 0 1 {dx1} {n(top + r)}V840Z"
    defs = lin(f"{uid}k", [(0, "#FFF6D6", 1), (1, GOLD, 1)])
    body = (f'<path d="{poly(right)}" fill="#fff" fill-opacity=".58"/>'
            f'<path d="{poly(left)}" fill="#fff" fill-opacity=".95"/>')
    if level >= 1:      # the lesser peak's lit side
        body += f'<path d="{poly([saddle, peak2, (684, 600)])}" fill="#fff" fill-opacity=".80"/>'
    body += f'<path d="{door}" fill="url(#{uid}k)"/>'
    if level >= 1:      # light spilling out of the door onto the floor
        defs += lin(f"{uid}s", [(0, GOLD, .55), (1, GOLD, 0)])
        body += f'<path d="{poly([(dx0, 840), (dx1, 840), (dx1 + 56, 902), (dx0 - 56, 902)])}" fill="url(#{uid}s)"/>'
    if level >= 2:      # an inner door: the light has a depth (the nested doors of the mark)
        ir = r * .52
        ix0, ix1 = 472 - ir, 472 + ir
        itop = 840 - dh * .55
        idoor = f"M{n(ix0)} 840V{n(itop + ir)}A{n(ir)} {n(ir)} 0 0 1 {n(ix1)} {n(itop + ir)}V840Z"
        body += f'<path d="{idoor}" fill="#fff" fill-opacity=".85"/>'
    return defs, body


DIRECTIONS = [
    # key, name, glyph, card top, card bottom, edge (near-black of the hue)
    ("a", "Bearer", glyph_bearer, "#4D3F96", "#241B4E", "#120C2C"),
    ("b", "Folio", glyph_folio, "#3C8DDF", "#14508F", "#071F3D"),
    ("c", "Threshold", glyph_threshold, "#8F72FF", "#4B2FD6", "#1A0F5E"),
]


def badge(key, level, uid=None):
    """(defs, body) of direction `key` at level 0 (48), 1 (128) or 2 (512), on its card."""
    k, name, glyph, top, bot, edge = next(d for d in DIRECTIONS if d[0] == key)
    uid = uid or f"{k}{level}"
    cd, cb = card(uid, top, bot, edge)
    gd, gb = glyph(uid, level)
    return cd + gd, cb + gb


def svg_file(key, px):
    level = {48: 0, 128: 1, 512: 2}[px]
    name = next(d[1] for d in DIRECTIONS if d[0] == key)
    defs, body = badge(key, level)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" '
            f'width="{px}" height="{px}"><title>Atlas, direction {key.upper()}: {name}</title>'
            '<!-- SPDX-License-Identifier: LicenseRef-Wonderland-Brand-1.0. (c) 2026 Julia Klee. Atlas brand. -->'
            f'<defs>{defs}</defs>{body}</svg>\n')


# ------------------------------------------------------------------------------------------ the sheet
def sheet_svg():
    """Contact sheet: three directions across, light ground on top, dark below; each cell shows the
    512 drawing at 256 px (half), the 128 at 128 px and the 48 at 48 px, all as drawn for that size."""
    colw, rowh, pad, head = 540, 400, 40, 90
    W, H = colw * 3 + pad * 2, head + rowh * 2
    out, defs = [], []
    for ri, (gname, ground, ink) in enumerate((("light", LIGHT_G, INK_L), ("dark", DARK_G, INK_D))):
        y0 = head + ri * rowh
        out.append(f'<rect x="0" y="{y0}" width="{W}" height="{rowh}" fill="{ground}"/>')
    out.append(f'<rect x="0" y="0" width="{W}" height="{head}" fill="{LIGHT_G}"/>')
    out.append(f'<text x="{pad}" y="56" font-family="Inter" font-size="30" font-weight="700" fill="{INK_L}">'
               'Atlas: three logo directions</text>')
    out.append(f'<text x="{W - pad}" y="56" font-family="Inter" font-size="14" text-anchor="end" fill="{_T["light"]["text-2"]}">'
               '512 shown at 50%, 128 and 48 at true size; each size is its own drawing</text>')
    for ci, (key, name, *_rest) in enumerate(DIRECTIONS):
        x0 = pad + ci * colw
        for ri, (gname, ground, ink) in enumerate((("light", LIGHT_G, INK_L), ("dark", DARK_G, INK_D))):
            y0 = head + ri * rowh
            sub = _T["light" if ri == 0 else "dark"]["text-2"]
            if ri == 0:
                out.append(f'<text x="{x0}" y="{y0 + 40}" font-family="Inter" font-size="20" font-weight="600" fill="{ink}">'
                           f'{key.upper()}  {name}</text>')
            for px, (dx, dy) in zip(SIZES, ((0, 70), (276, 70 + 64), (276 + 128 + 36, 70 + 64 + 40))):
                level = {48: 0, 128: 1, 512: 2}[px]
                d, b = badge(key, level, f"{key}{level}{gname[0]}")
                defs.append(d)
                # the 512 drawing is shown at 256 px, the others at their size; the canvas is 1024 units
                out.append(f'<g transform="translate({x0 + dx} {y0 + dy}) scale({(px if px != 512 else 256) / 1024:.6g})">{b}</g>')
            out.append(f'<text x="{x0}" y="{y0 + rowh - 28}" font-family="Inter" font-size="12" fill="{sub}">'
                       f'{gname} ground {ground}</text>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<defs>{"".join(defs)}</defs>{"".join(out)}</svg>\n')


def png(svg_path, out, px=None):
    cmd = ["rsvg-convert", svg_path, "-o", out]
    if px:
        cmd[1:1] = ["-w", str(px)]
    subprocess.run(cmd, check=True)


def files():
    f = {}
    for key, name, *_ in DIRECTIONS:
        for px in SIZES:
            f[f"brand/atlas/directions/atlas-{key}-{name.lower()}-{px}.svg"] = svg_file(key, px)
    f["brand/atlas/directions/contact-sheet.svg"] = sheet_svg()
    return f


def build(design, check=False):
    design = os.path.abspath(design)
    bad = []
    for rel, text in files().items():
        p = os.path.join(design, rel)
        if check:
            if not os.path.isfile(p) or open(p, encoding="utf-8").read() != text:
                bad.append(rel)
            continue
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(text)
    sheet = os.path.join(design, "brand/atlas/directions/contact-sheet.svg")
    out = os.path.join(design, "brand/atlas/directions/contact-sheet.png")
    if check:
        if not os.path.isfile(out):
            bad.append("brand/atlas/directions/contact-sheet.png")
        return bad
    png(sheet, out)
    return bad


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    chk = "--check" in sys.argv
    bad = build(args[0] if args else DESIGN, check=chk)
    if bad:
        print("atlas: out of date or missing:\n  " + "\n  ".join(bad))
        sys.exit(1)
    print("atlas: ok" if chk else "atlas: written")
