# SPDX-License-Identifier: GPL-2.0-or-later
"""Six app icons redrawn in the brand geometry (docs/adr/brand-calculus.md section 8).

  python3 -I design/tools/brand/icons_brand.py [outdir]     (default design/brand/icons)

Grid: the identity card (tokens icon.card: 52 of 64, radii 17/6, big radius upper-left and
lower-right) is 21 fen wide; the glyph lives in the 15 x 15 fen square inside it (3 fen of
breathing on every side) and its long side fills that square. Slopes are juzhe curves, light
comes from the upper left (lit gradients along dx:dy = 1:2, gloss on the lit rim, shadows to the
lower right). Colours are the derived palette (calculus.brand_palette) and the element rules:
each object neighbours its card in a sheng (generating) or same relation; ke colours stay under
1/7 of the frame. Small variants (16-32 px) drop gloss and fine lines.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calculus as K  # noqa: E402
from geom import Doc, rrect, circle, juzhe, smooth, shade, f  # noqa: E402
from colour import from_oklch, oklch  # noqa: E402

S = 1024
CARD_X = 100.0                 # the shipped card silhouette: 100..924 on the 1024 canvas
CARD = 824.0
FEN = CARD / K.ZUCAI           # 39.24 px
R_BIG, R_SMALL = 236.0, 150.0  # its corner radii (upper-left/lower-right, the other two)


def _shipped_card():
    """The card silhouette of the shipped set: the superellipse of tools/icons/svgk.py (CARD). It
    used to be read back from the installed icons/apps/wolos-settings.svg, which made the icons a
    generator input of their own output: once the A2 set was installed the read found nothing and
    every regeneration drew a different card."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("svgk_card", os.path.join(HERE, "..", "icons", "svgk.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.CARD


SHIPPED_CARD = _shipped_card()
P = K.brand_palette()
C = {k: v[0] for k, v in P.items()}
L0, C0, H0 = oklch(K.BASE)


def X(fx):
    return CARD_X + fx * FEN


def card_path():
    return SHIPPED_CARD or rrect(CARD_X, CARD_X, CARD, CARD, R_BIG, R_SMALL, R_BIG, R_SMALL)


def card(doc, body, small):
    d = card_path()
    doc.shadow(d, shade(body, -12), FEN, opacity=0.34, lift=1.3)
    doc.add(f'<path d="{d}" fill="{doc.lit(body, 3)}"/>')
    if not small:
        cid = doc.id("c")
        doc.defs.append(f'<clipPath id="{cid}"><path d="{d}"/></clipPath>')
        doc.add(f'<path d="{d}" fill="none" stroke="{doc.rim(0.55)}" stroke-width="{f(FEN * 0.5)}" clip-path="url(#{cid})"/>')


def court(doc, body, small, strength=4):
    """The second plane (the courtyard between wall and hall): a soft pool of light on the card,
    centred up and left of the glyph (toward the light), 17 fen across."""
    i = doc.id("p")
    doc.defs.append(f'<radialGradient id="{i}" cx="0.46" cy="0.42" r="0.5">'
                    f'<stop offset="0" stop-color="{shade(body, strength)}" stop-opacity="0.9"/>'
                    f'<stop offset="0.45" stop-color="{shade(body, strength)}" stop-opacity="0.55"/>'
                    f'<stop offset="0.8" stop-color="{shade(body, strength)}" stop-opacity="0.15"/>'
                    f'<stop offset="1" stop-color="{shade(body, strength)}" stop-opacity="0"/></radialGradient>')
    r = 9.2 * FEN
    doc.add(f'<path d="{circle(X(10.3), X(10.0), r)}" fill="url(#{i})"/>')


def obj(doc, d, colour, small, spread=3, lift=1.0, gloss=0.45, shadow_of=None):
    doc.shadow(d, shade(shadow_of or colour, -14), FEN, opacity=0.32, lift=lift)
    doc.add(f'<path d="{d}" fill="{doc.lit(colour, spread)}"/>')
    if not small and gloss:
        doc.add(f'<path d="{d}" fill="{doc.rim(gloss)}"/>')


def keyhole(cx, top, w):
    """The WolOS keyhole: an arched head over a tapered stem, `w` wide, top at `top`."""
    r = w / 2
    cy = top + r
    stem_top, stem_bot = cy + r * 0.55, cy + r * 2.5
    sw_t, sw_b = r * 0.42, r * 0.7
    return (circle(cx, cy, r) +
            f"M{f(cx - sw_t)} {f(stem_top - r * 0.3)}L{f(cx + sw_t)} {f(stem_top - r * 0.3)}"
            f"L{f(cx + sw_b)} {f(stem_bot)}L{f(cx - sw_b)} {f(stem_bot)}Z")


# ---------------------------------------------------------------- the six
def settings(small=False):
    doc = Doc(S, S, "settings")
    body = from_oklch(K.ladder(L0, -9), C0 * 9 / 21, H0)            # water: deep base
    card(doc, body, small)
    court(doc, body, small, strength=7)
    cx, cy = X(10.5), X(10.5)
    ro, rr = 7.5 * FEN, 5.9 * FEN       # tip radius (15 fen across) and root radius
    teeth = 8                           # the eight directions
    pts = []
    for i in range(teeth):
        a0 = (i / teeth) * 2 * math.pi - math.pi / 2
        half_tip, half_root = math.pi / teeth * 0.42, math.pi / teeth * 0.78
        # tooth flank: juzhe curve from root to tip (concave, like an eave seen from the end)
        for side in (-1, 1):
            pass
        root_l = (cx + rr * math.cos(a0 - half_root), cy + rr * math.sin(a0 - half_root))
        tip_l = (cx + ro * math.cos(a0 - half_tip), cy + ro * math.sin(a0 - half_tip))
        tip_r = (cx + ro * math.cos(a0 + half_tip), cy + ro * math.sin(a0 + half_tip))
        root_r = (cx + rr * math.cos(a0 + half_root), cy + rr * math.sin(a0 + half_root))
        pts.append(("flank", root_l, tip_l))
        pts.append(("tip", tip_l, tip_r))
        pts.append(("flank", tip_r, root_r))
        a1 = ((i + 1) / teeth) * 2 * math.pi - math.pi / 2
        pts.append(("root", root_r, (cx + rr * math.cos(a1 - half_root), cy + rr * math.sin(a1 - half_root))))
    d = f"M{f(pts[0][1][0])} {f(pts[0][1][1])}"
    for kind, a, b in pts:
        if kind == "flank":
            # juzhe in the tooth's own frame: rise along the radius, run along the tangent
            jz = juzhe(0, 0, 1, 1, purlins=3, first=0.12)
            seg = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * u) for t, u in
                   ((p[0], p[1]) for p in jz)]
            d += smooth(seg)
        elif kind == "tip":
            d += f"A{f(ro)} {f(ro)} 0 0 1 {f(b[0])} {f(b[1])}"
        else:
            d += f"A{f(rr)} {f(rr)} 0 0 1 {f(b[0])} {f(b[1])}"
    d += "Z"
    metal = from_oklch(0.86, C0 * 0.6 / 21, H0)
    obj(doc, d, metal, small, spread=5, lift=1.1, gloss=0.6, shadow_of=body)
    # hub: a raised ring, then the keyhole in the base violet (the landing)
    hub = circle(cx, cy, 4.2 * FEN)
    obj(doc, hub, shade(metal, -3), small, spread=4, lift=0.5, gloss=0.5)   # a raised boss, lit like the rest
    face = circle(cx, cy, 3.4 * FEN)
    doc.add(f'<path d="{face}" fill="{doc.lit(C["accent"], 3)}"/>')
    kh = keyhole(cx, cy - 2.0 * FEN, 1.75 * FEN)
    doc.add(f'<path d="{kh}" fill="{C["dark.bg"] if not small else "#FFFFFF"}"/>')
    if not small:
        doc.add(f'<path d="{kh}" fill="{C["earth"]}" opacity="0.0"/>')
    return doc.svg()


def store(small=False):
    doc = Doc(S, S, "store")
    body = from_oklch(K.ladder(oklch(C["earth"])[0], -4), 0.16, oklch(C["earth"])[2])  # earth card
    card(doc, body, small)
    court(doc, body, small)
    # bag: 10 wide x 15 tall glyph (cai 3:2): handle 3..7.6, body 6.6..18
    x0, x1 = X(5.5), X(15.5)
    top, bot = X(7.0), X(18.0)
    flare = 0.45 * FEN
    # body: slight taper (wider at the base: a building stands on its platform)
    bx0, bx1 = x0 - 0.25 * FEN, x1 + 0.25 * FEN
    rim = juzhe(x0 - flare, top - flare * 0.8, X(10.5), top, purlins=3, first=0.18)
    rim_r = [(2 * X(10.5) - x, y) for x, y in reversed(juzhe(x0 - flare, top - flare * 0.8, X(10.5), top, purlins=3, first=0.18))]
    r = 1.2 * FEN
    d = (f"M{f(rim[0][0])} {f(rim[0][1])}" + smooth(rim) + smooth(rim_r) +
         f"L{f(x1)} {f(top + 0.4 * FEN)}L{f(bx1)} {f(bot - r)}Q{f(bx1)} {f(bot)} {f(bx1 - r)} {f(bot)}"
         f"H{f(bx0 + r)}Q{f(bx0)} {f(bot)} {f(bx0)} {f(bot - r)}L{f(x0)} {f(top + 0.4 * FEN)}Z")
    paper = from_oklch(0.93, C0 * 2.6 / 21, oklch(C["earth"])[2])
    # handle (fire: rose; fire feeds earth) behind the bag
    hw, hh = 2.7 * FEN, 4.3 * FEN
    th = 0.8 * FEN
    hx = X(10.5)
    handle = (f"M{f(hx - hw)} {f(top + 0.3 * FEN)}V{f(top - hh + hw)}"
              f"A{f(hw)} {f(hw)} 0 0 1 {f(hx + hw)} {f(top - hh + hw)}V{f(top + 0.3 * FEN)}"
              f"H{f(hx + hw - th)}V{f(top - hh + hw)}A{f(hw - th)} {f(hw - th)} 0 0 0 {f(hx - hw + th)} {f(top - hh + hw)}"
              f"V{f(top + 0.3 * FEN)}Z")
    obj(doc, handle, C["fire"], small, spread=3, lift=0.6, gloss=0.3)
    obj(doc, d, paper, small, spread=2, lift=1.2, gloss=0.0, shadow_of=body)
    # the gusset on the shadow side (right)
    if not small:
        doc.add(f'<path d="M{f(x1)} {f(top + 0.4 * FEN)}L{f(bx1)} {f(bot - r)}Q{f(bx1)} {f(bot)} {f(bx1 - r)} {f(bot)}'
                f'H{f(x1 - 1.4 * FEN)}L{f(x1 - 1.0 * FEN)} {f(top + 0.4 * FEN)}Z" fill="{shade(paper, -3)}" opacity="0.7"/>')
    # tag at the upper left, tied to the rim: the entry of the eye
    if True:
        tx, ty = x0 + 0.3 * FEN, top + 0.9 * FEN
        tag = (f"M{f(tx)} {f(ty)}L{f(tx - 2.3 * FEN)} {f(ty + 1.9 * FEN)}L{f(tx - 1.3 * FEN)} {f(ty + 4.9 * FEN)}"
               f"L{f(tx + 1.1 * FEN)} {f(ty + 2.9 * FEN)}Z")
        obj(doc, tag, C["fire"], small, spread=3, lift=0.5, gloss=0.3)
        doc.add(f'<path d="{circle(tx - 0.6 * FEN, ty + 1.95 * FEN, 0.4 * FEN)}" fill="{paper}"/>')
    # seal: the keyhole in a violet disc (water; ke with the earth card but well under 1/7)
    cx, cy = X(10.5) - 0.3 * FEN, X(12.6)
    disc = circle(cx, cy, 2.3 * FEN)
    obj(doc, disc, C["accent"], small, spread=3, lift=0.5, gloss=0.4)
    doc.add(f'<path d="{keyhole(cx, cy - 1.45 * FEN, 1.25 * FEN)}" fill="{paper}"/>')
    return doc.svg()


def files(small=False):
    doc = Doc(S, S, "files")
    hw = oklch(C["water"])[2]
    body = from_oklch(K.ladder(L0, -6), 0.12, hw)                    # water (azurite) card
    card(doc, body, small)
    court(doc, body, small)
    x0, x1 = X(3.0), X(18.0)            # 15 wide
    top, bot = X(5.5), X(15.5)           # 10 tall (cai 3:2)
    r = 1.0 * FEN
    # back panel with a tab whose shoulder is a juzhe slope
    tab_end = X(9.0)
    slope = juzhe(tab_end, top, tab_end + 1.8 * FEN, top + 1.2 * FEN, purlins=3, first=0.15)
    back = (f"M{f(x0)} {f(top + r)}Q{f(x0)} {f(top)} {f(x0 + r)} {f(top)}H{f(tab_end)}" + smooth(slope) +
            f"H{f(x1 - r)}Q{f(x1)} {f(top + 1.2 * FEN)} {f(x1)} {f(top + 1.2 * FEN + r)}V{f(bot - r)}"
            f"Q{f(x1)} {f(bot)} {f(x1 - r)} {f(bot)}H{f(x0 + r)}Q{f(x0)} {f(bot)} {f(x0)} {f(bot - r)}Z")
    obj(doc, back, shade(body, 5), small, spread=2, lift=0.7, gloss=0.25, shadow_of=body)
    # papers (metal; metal feeds water)
    paper = from_oklch(0.985, C0 * 0.8 / 21, H0)
    for i, (dx, dy, w) in enumerate(((1.2, 2.2, 12.6), (0.6, 3.0, 13.6))):
        pd = rrect(x0 + dx * FEN, top + dy * FEN, w * FEN, 6 * FEN, 0.5 * FEN)
        obj(doc, pd, shade(paper, -2 * (1 - i)), small, spread=1, lift=0.5, gloss=0.0, shadow_of=body)
    if not small:
        for j, w in enumerate((10, 6)):  # ruled lines: cai width and zhi (rhythm 10:6)
            ly = top + (3.9 + 0.9 * j) * FEN
            doc.add(f'<path d="{rrect(x0 + 1.6 * FEN, ly, w * FEN, 0.32 * FEN, 0.16 * FEN)}" fill="{body}" opacity="0.45"/>')
    # front panel: top edge rises gently to the right (juzhe), flared corners
    ft = top + 5.0 * FEN
    edge = juzhe(x0 - 0.2 * FEN, ft + 0.35 * FEN, x1 + 0.2 * FEN, ft - 0.25 * FEN, purlins=4, first=0.2)
    front = (f"M{f(edge[0][0])} {f(edge[0][1])}" + smooth(edge) +
             f"L{f(x1)} {f(bot - r)}Q{f(x1)} {f(bot)} {f(x1 - r)} {f(bot)}H{f(x0 + r)}Q{f(x0)} {f(bot)} {f(x0)} {f(bot - r)}Z")
    front_c = from_oklch(K.ladder(L0, 6), 0.11, hw)
    obj(doc, front, front_c, small, spread=3, lift=1.0, gloss=0.5, shadow_of=body)
    # label: the gold pop (earth; ke with water, a small accent)
    lab = rrect(X(4.6), ft + 1.6 * FEN, 3.0 * FEN, 1.0 * FEN, 0.4 * FEN)
    doc.add(f'<path d="{lab}" fill="{C["earth"]}"/>')
    return doc.svg()


def console(small=False):
    doc = Doc(S, S, "console")
    body = from_oklch(K.ladder(L0, -13), C0 * 3 / 21, H0)            # water: ink
    card(doc, body, small)
    court(doc, body, small)
    x0, x1, top, bot = X(3.0), X(18.0), X(5.5), X(15.5)              # 15 x 10 (cai 3:2)
    win = rrect(x0, top, x1 - x0, bot - top, 1.6 * FEN, 0.8 * FEN, 1.6 * FEN, 0.8 * FEN)
    obj(doc, win, from_oklch(K.ladder(L0, -15), C0 * 2 / 21, H0), small, spread=2, lift=1.0, gloss=0.18, shadow_of=body)
    if not small:
        bar = rrect(x0 + 0.6 * FEN, top + 0.55 * FEN, x1 - x0 - 1.2 * FEN, 0.9 * FEN, 0.45 * FEN)
        doc.add(f'<path d="{bar}" fill="{shade(body, 5)}" opacity="0.5"/>')
    jade = from_oklch(0.80, 0.14, oklch(C["wood"])[2])               # wood: water feeds wood
    # the prompt: a chevron whose arms are juzhe slopes (the entry, upper left of the text)
    cx, cy, a = (X(4.4), X(9.0), 1.8 * FEN) if not small else (X(4.6), X(10.4), 3.0 * FEN)
    th = 0.85 * FEN if not small else 1.5 * FEN
    up = juzhe(cx, cy - a, cx + a * 1.15, cy, purlins=3, first=0.12)
    d = (f"M{f(cx)} {f(cy - a)}" + smooth(up) + f"L{f(cx)} {f(cy + a)}L{f(cx - th * 0.2)} {f(cy + a - th)}"
         f"L{f(cx + a * 1.15 - th * 1.25)} {f(cy)}L{f(cx - th * 0.2)} {f(cy - a + th)}Z")
    obj(doc, d, jade, small, spread=3, lift=0.4, gloss=0.35)
    # text lines (rhythm: 10, 6 fen) and the cursor (the landing, 2 x 3 = zhi 3:2)
    if not small:
        for j, (x, w) in enumerate(((7.4, 9.0), (4.0, 6.0))):   # rhythm: line 1 after the prompt, line 2
            doc.add(f'<path d="{rrect(X(x), X(8.7) + j * 2.4 * FEN, w * FEN, 0.6 * FEN, 0.3 * FEN)}" fill="{shade(body, 11)}" opacity="0.75"/>')
    cur = rrect(X(10.6), X(10.7), 3.0 * FEN, 2.0 * FEN, 0.35 * FEN) if not small else rrect(X(10.4), X(11.4), 4.5 * FEN, 3.0 * FEN, 0.5 * FEN)
    obj(doc, cur, jade, small, spread=3, lift=0.4, gloss=0.4)
    return doc.svg()


def doctor(small=False):
    doc = Doc(S, S, "doctor")
    body = from_oklch(K.ladder(L0, -4), 0.13, oklch(C["wood"])[2])    # wood: jade
    card(doc, body, small)
    court(doc, body, small)
    # heart 15 wide x 14.2 tall: two lobes and a point; wood feeds fire
    cx, top, w, h = X(10.5), X(3.2), 15 * FEN, 15.6 * FEN
    lr = w / 4
    ly = top + lr
    pt = (cx, top + h)
    d = (f"M{f(cx)} {f(ly - lr * 0.15)}"
         f"C{f(cx)} {f(top - lr * 0.15)} {f(cx - 2 * lr)} {f(top - lr * 0.15)} {f(cx - 2 * lr)} {f(ly + lr * 0.25)}"
         f"C{f(cx - 2 * lr)} {f(ly + 2.1 * lr)} {f(cx - 0.6 * lr)} {f(top + h - 0.9 * lr)} {f(pt[0])} {f(pt[1])}"
         f"C{f(cx + 0.6 * lr)} {f(top + h - 0.9 * lr)} {f(cx + 2 * lr)} {f(ly + 2.1 * lr)} {f(cx + 2 * lr)} {f(ly + lr * 0.25)}"
         f"C{f(cx + 2 * lr)} {f(top - lr * 0.15)} {f(cx)} {f(top - lr * 0.15)} {f(cx)} {f(ly - lr * 0.15)}Z")
    rose = from_oklch(0.66, 0.17, 18)
    obj(doc, d, rose, small, spread=3, lift=1.1, gloss=0.5, shadow_of=body)
    # pulse (earth gold: fire feeds earth); it turns and ends inside the heart
    y = X(9.6)
    xs = [X(5.2), X(8.0), X(9.2), X(10.6), X(11.8), X(13.0), X(15.8)]
    ys = [y, y, y - 2.4 * FEN, y + 2.6 * FEN, y - 1.0 * FEN, y, y]
    th = (1.0 if small else 0.8) * FEN
    pts = list(zip(xs, ys))
    # build a filled polyline outline of thickness th with round joins (offset both sides)
    left, right = [], []
    for i, (x, yy) in enumerate(pts):
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - yy
        elif i == len(pts) - 1:
            dx, dy = x - pts[i - 1][0], yy - pts[i - 1][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        n = math.hypot(dx, dy)
        nx, ny = -dy / n * th / 2, dx / n * th / 2
        left.append((x + nx, yy + ny)); right.append((x - nx, yy - ny))
    pd = f"M{f(left[0][0])} {f(left[0][1])}" + "".join(f"L{f(a)} {f(b)}" for a, b in left[1:])
    e = pts[-1]
    pd += f"A{f(th / 2)} {f(th / 2)} 0 0 0 {f(right[-1][0])} {f(right[-1][1])}"
    pd += "".join(f"L{f(a)} {f(b)}" for a, b in reversed(right[:-1]))
    pd += f"A{f(th / 2)} {f(th / 2)} 0 0 0 {f(left[0][0])} {f(left[0][1])}Z"
    doc.add(f'<path d="{pd}" fill="{C["earth"]}" stroke="{C["earth"]}" stroke-width="{f(th * 0.15)}" stroke-linejoin="round"/>')
    return doc.svg()


def atlas(small=False):
    doc = Doc(S, S, "atlas folio")
    body = from_oklch(K.ladder(L0, -5), 0.15, 258)                    # water: lake blue
    card(doc, body, small)
    court(doc, body, small)
    # three panels, 5 fen each (15), zigzag fold; total 15 tall with the 1.5 fen skew
    x = [X(3.0), X(8.0), X(13.0), X(18.0)]
    t = [X(4.5), X(3.0), X(4.5), X(3.0)]
    b = [X(16.5), X(18.0) - 0.0, X(16.5), X(18.0)]
    b = [X(16.5), X(15.0), X(16.5), X(15.0)]
    b = [y + 2.0 * FEN for y in b]
    paper = from_oklch(0.975, C0 * 0.7 / 21, H0)
    tones = (0, -3, 1)
    allp = f"M{f(x[0])} {f(t[0])}L{f(x[1])} {f(t[1])}L{f(x[2])} {f(t[2])}L{f(x[3])} {f(t[3])}L{f(x[3])} {f(b[3])}L{f(x[2])} {f(b[2])}L{f(x[1])} {f(b[1])}L{f(x[0])} {f(b[0])}Z"
    doc.shadow(allp, shade(body, -14), FEN, opacity=0.34, lift=1.1)
    for i in range(3):
        pd = f"M{f(x[i])} {f(t[i])}L{f(x[i + 1])} {f(t[i + 1])}L{f(x[i + 1])} {f(b[i + 1])}L{f(x[i])} {f(b[i])}Z"
        doc.add(f'<path d="{pd}" fill="{doc.lit(shade(paper, tones[i]), 2)}"/>')
    if not small:
        doc.add(f'<path d="{allp}" fill="{doc.rim(0.35)}"/>')
    # trail: from the upper left (entry) in a turning curve to the you-are-here (landing)
    gold = C["earth-deep"]
    # S-curve through knots: down from the entry, a turn (the spirit screen), then to the mark
    knots = [(X(4.4), X(6.4)), (X(6.6), X(8.6)), (X(6.4), X(11.0)), (X(9.0), X(12.6)), (X(11.8), X(12.9))]
    pts = []
    for i in range(len(knots) - 1):
        p0 = knots[max(0, i - 1)]; p1, p2 = knots[i], knots[i + 1]; p3 = knots[min(len(knots) - 1, i + 2)]
        for j in range(12):
            t = j / 12
            t2, t3 = t * t, t * t * t
            pts.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    # equal spacing along the arc
    import itertools
    acc = [0.0] + list(itertools.accumulate(math.dist(a_, b_) for a_, b_ in zip(pts, pts[1:])))
    n = 5 if small else 9
    dots = []
    for k in range(n):
        target = acc[-1] * k / (n - 1) * 0.92
        i = next(i for i, v in enumerate(acc) if v >= target)
        dots.append(pts[i])
    for k, (px_, py_) in enumerate(dots):
        rr = (0.45 if small else 0.26 + 0.02 * k) * FEN
        if k == 0:
            continue
        doc.add(f'<path d="{circle(px_, py_, rr)}" fill="{gold}" opacity="{f(0.5 + 0.05 * k)}"/>')
    sx, sy = dots[0]
    doc.add(f'<path d="{circle(sx, sy, 0.9 * FEN)}{circle(sx, sy, 0.5 * FEN)}" fill-rule="evenodd" fill="{gold}"/>')
    # you-are-here: gold point with a soft halo (the light it gives is its own, not a second sun)
    hx, hy = X(13.9), X(12.6)
    i = doc.id("h")
    doc.defs.append(f'<radialGradient id="{i}"><stop offset="0" stop-color="{C["earth"]}" stop-opacity="0.85"/>'
                    f'<stop offset="1" stop-color="{C["earth"]}" stop-opacity="0"/></radialGradient>')
    doc.add(f'<path d="{circle(hx, hy, 2.6 * FEN)}" fill="url(#{i})"/>')
    obj(doc, circle(hx, hy, 1.2 * FEN), C["earth"], small, spread=2, lift=0.4, gloss=0.6)
    doc.add(f'<path d="{circle(hx, hy, 0.45 * FEN)}" fill="#FFFFFF"/>')
    return doc.svg()


ICONS = {"settings": settings, "store": store, "files": files, "console": console,
         "doctor": doctor, "atlas-folio": atlas}


def main(argv):
    out = argv[0] if argv else os.path.join(HERE, "..", "..", "brand", "icons")
    os.makedirs(os.path.join(out, "small"), exist_ok=True)
    for name, fn in ICONS.items():
        for small in (False, True):
            p = os.path.join(out, "small" if small else "", f"wolos-{name}.svg")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(fn(small))
    print(f"wrote {2 * len(ICONS)} icons to {os.path.normpath(out)}")


if __name__ == "__main__":
    main(sys.argv[1:])
