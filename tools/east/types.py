# SPDX-License-Identifier: GPL-2.0-or-later
"""Icon types, second batch (lead 06:49-06:54Z: the grammar of Chinese app icons; the shipped card).

  python3 -I design/tools/east/types.py [outdir]     (default design/east/types)

  A bold    flat saturated card in the app's phase colour, one big white glyph (about 2/3 of the
            card), thick rounded strokes, one accent of colour; light only as a 1-fen lift.
  B motif   the glyph grows from a traditional motif: ruyi-cloud gear, the bag sealed with a cash
            coin (round outside, square hole), a hand scroll, a seal stamp, the longevity peach,
            the folio with a luopan dial as the you-are-here.
  C jianzhi paper-cut: a light paper card, the glyph cut from one sheet of coloured paper, with
            crescent and window cuts, lifted 1 fen off the card (shadow 1:2).
Card: the shipped silhouette (100..924 of 1024), 21 fen wide; glyphs sit on the 15-fen square.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calculus as K  # noqa: E402
from geom import Doc, rrect, circle, juzhe, smooth, shade, f  # noqa: E402
from colour import from_oklch, oklch  # noqa: E402
import icons_east as IE  # noqa: E402  (shipped card path)
from directions import gear_path, keyhole, heart, ribbon, COL  # noqa: E402

S = 1024
FEN = 824 / 21
L0, C0, H0 = oklch(K.BASE)
HUE = {e: K.hue_of(e) for e in ("fire", "earth", "wood", "water")}
WHITE = "#FFFFFF"
CARD = {
    "settings": from_oklch(K.ladder(L0, -1), C0, H0),                       # water: the base violet
    "store": from_oklch(K.ladder(L0, 7), C0 * 16 / 21, HUE["earth"]),       # earth
    "files": from_oklch(K.ladder(L0, -1), C0 * 13 / 21, HUE["water"]),      # water: azurite
    "console": from_oklch(K.ladder(L0, -13), C0 * 4 / 21, H0),              # water: ink
    "doctor": from_oklch(K.ladder(L0, -1), C0 * 13 / 21, HUE["wood"]),      # wood feeds fire
    "atlas": from_oklch(K.ladder(L0, -3), C0 * 15 / 21, 258),               # water: lake blue
}
GOLD = from_oklch(K.ladder(L0, 13), C0 * 15 / 21, HUE["earth"])
RED = from_oklch(K.ladder(L0, 0), C0 * 16 / 21, HUE["fire"])
JADE = from_oklch(0.80, 0.14, HUE["wood"])


def X(x):
    return 100 + x * FEN


def card(doc, colour, flat=True):
    d = IE.card_path()
    doc.shadow(d, shade(colour, -14), FEN, opacity=0.28, lift=1.2)
    doc.add(f'<path d="{d}" fill="{doc.lit(colour, 1.5 if flat else 3)}"/>')


def glyph(doc, d, colour=WHITE, under=None, lift=0.35, rule="nonzero"):
    """Flat glyph with a 1:2 contact shadow in the card's own deeper tone."""
    if under:
        dx, dy = 0.35 * lift * FEN, 0.7 * lift * FEN
        doc.add(f'<path d="{d}" fill-rule="{rule}" transform="translate({f(dx)} {f(dy)})" fill="{shade(under, -6)}" opacity="0.55"/>')
    doc.add(f'<path d="{d}" fill-rule="{rule}" fill="{colour}"/>')


def bag(x0, x1, top, bot, r=1.2):
    """Bag body: a slight taper (wider at the foot), rounded foot."""
    rr = r * FEN
    return (f"M{f(X(x0 + 0.4))} {f(X(top))}H{f(X(x1 - 0.4))}L{f(X(x1))} {f(X(bot) - rr)}Q{f(X(x1))} {f(X(bot))} {f(X(x1) - rr)} {f(X(bot))}"
            f"H{f(X(x0) + rr)}Q{f(X(x0))} {f(X(bot))} {f(X(x0))} {f(X(bot) - rr)}Z")


def handle(cx, base, w, h, th):
    pts = [(X(cx) - w / 2 * FEN, X(base))] + [(X(cx) - w / 2 * FEN * math.cos(t / 12 * math.pi), X(base - 1.0) - h * FEN * math.sin(t / 12 * math.pi)) for t in range(0, 13)] + [(X(cx) + w / 2 * FEN, X(base))]
    return ribbon(pts, th * FEN)


def folder(x0, y0, w, h, tab_w=6.0, tab_h=1.6, r=1.2):
    rr = r * FEN
    tab = juzhe(X(x0 + tab_w), X(y0), X(x0 + tab_w + 1.8), X(y0 + tab_h), purlins=3, first=0.15)
    return (f"M{f(X(x0))} {f(X(y0) + rr)}Q{f(X(x0))} {f(X(y0))} {f(X(x0) + rr)} {f(X(y0))}H{f(X(x0 + tab_w))}" + smooth(tab) +
            f"H{f(X(x0 + w) - rr)}Q{f(X(x0 + w))} {f(X(y0 + tab_h))} {f(X(x0 + w))} {f(X(y0 + tab_h) + rr)}V{f(X(y0 + h) - rr)}"
            f"Q{f(X(x0 + w))} {f(X(y0 + h))} {f(X(x0 + w) - rr)} {f(X(y0 + h))}H{f(X(x0) + rr)}Q{f(X(x0))} {f(X(y0 + h))} {f(X(x0))} {f(X(y0 + h) - rr)}Z")


def chevron(cx, cy, a, th):
    return ribbon([(X(cx), X(cy - a)), (X(cx + a * 1.05), X(cy)), (X(cx), X(cy + a))], th * FEN)


def map3(x0, y0, w, h, skew):
    pw = w / 3
    xs = [x0 + i * pw for i in range(4)]
    tops = [y0 + skew, y0, y0 + skew, y0]
    out = []
    for i in range(3):
        out.append(f"M{f(X(xs[i]))} {f(X(tops[i]))}L{f(X(xs[i + 1]))} {f(X(tops[i + 1]))}L{f(X(xs[i + 1]))} {f(X(tops[i + 1] + h))}L{f(X(xs[i]))} {f(X(tops[i] + h))}Z")
    return out


def pulse(y, x0, x1, th):
    pts = [(x0, y), (x0 + (x1 - x0) * 0.3, y), (x0 + (x1 - x0) * 0.42, y - 2.4), (x0 + (x1 - x0) * 0.57, y + 2.6), (x0 + (x1 - x0) * 0.68, y - 1.0), (x0 + (x1 - x0) * 0.76, y), (x1, y)]
    return ribbon([(X(a), X(b)) for a, b in pts], th * FEN)


# ===================================================== A bold
def a_settings():
    doc = Doc(S, S, "settings, bold"); c = CARD["settings"]; card(doc, c)
    d = gear_path(X(10.5), X(10.5), 7.6 * FEN, 5.9 * FEN) + circle(X(10.5), X(10.5), 2.7 * FEN)
    glyph(doc, d, under=c, rule="evenodd")
    glyph(doc, keyhole(X(10.5), X(10.5) - 1.5 * FEN, 1.4 * FEN), GOLD)
    return doc.svg()


def a_store():
    doc = Doc(S, S, "store, bold"); c = CARD["store"]; card(doc, c)
    glyph(doc, handle(10.5, 7.6, 6.4, 3.4, 1.3), under=c)
    glyph(doc, bag(3.5, 17.5, 7.0, 18.0), under=c)
    glyph(doc, keyhole(X(10.5), X(10.6), 2.4 * FEN), CARD["settings"])
    return doc.svg()


def a_files():
    doc = Doc(S, S, "files, bold"); c = CARD["files"]; card(doc, c)
    glyph(doc, folder(3.0, 5.0, 15.0, 11.5), under=c)
    glyph(doc, rrect(X(4.8), X(9.0), 4.2 * FEN, 1.8 * FEN, 0.7 * FEN), GOLD)
    return doc.svg()


def a_console():
    doc = Doc(S, S, "console, bold"); c = CARD["console"]; card(doc, c)
    glyph(doc, chevron(4.6, 10.0, 3.6, 2.0), under=c)
    glyph(doc, rrect(X(10.6), X(13.0), 6.4 * FEN, 2.2 * FEN, 1.0 * FEN), JADE)
    return doc.svg()


def a_doctor():
    doc = Doc(S, S, "doctor, bold"); c = CARD["doctor"]; card(doc, c)
    glyph(doc, heart(X(10.5), X(4.0), 15 * FEN, 13.6 * FEN), under=c)
    glyph(doc, pulse(10.0, 5.2, 15.8, 1.2), RED)
    return doc.svg()


def a_atlas():
    doc = Doc(S, S, "atlas folio, bold"); c = CARD["atlas"]; card(doc, c)
    ps = map3(3.0, 4.0, 15.0, 12.0, 1.5)
    for i, p in enumerate(ps):
        glyph(doc, p, WHITE if i != 1 else shade(WHITE, -3), under=c if i == 0 else None)
    glyph(doc, circle(X(13.2), X(10.8), 2.0 * FEN), GOLD)
    glyph(doc, circle(X(13.2), X(10.8), 0.75 * FEN), WHITE)
    return doc.svg()


# ===================================================== B motif
def ruyi_gear(cx, cy, r_body, r_lobe, n=8):
    """A gear whose teeth are ruyi cloud heads: each tooth is three lobes (one big, two small)."""
    d = circle(X(cx), X(cy), r_body * FEN)
    for i in range(n):
        a = i / n * 2 * math.pi - math.pi / 2
        for da, rr, dist in ((0, r_lobe, r_body + r_lobe * 0.35), (-0.24, r_lobe * 0.62, r_body + r_lobe * 0.05), (0.24, r_lobe * 0.62, r_body + r_lobe * 0.05)):
            d += circle(X(cx) + dist * FEN * math.cos(a + da), X(cy) + dist * FEN * math.sin(a + da), rr * FEN)
    return d


def b_settings():
    doc = Doc(S, S, "settings, motif: ruyi-cloud gear"); c = CARD["settings"]; card(doc, c)
    glyph(doc, ruyi_gear(10.5, 10.5, 5.6, 1.45), under=c)
    glyph(doc, circle(X(10.5), X(10.5), 3.0 * FEN), shade(c, -2))
    glyph(doc, keyhole(X(10.5), X(10.5) - 1.6 * FEN, 1.5 * FEN), GOLD)
    return doc.svg()


def coin(cx, cy, r, hole):
    h = hole * FEN
    return circle(X(cx), X(cy), r * FEN) + f"M{f(X(cx) - h / 2)} {f(X(cy) - h / 2)}h{f(h)}v{f(h)}h{f(-h)}Z"


def b_store():
    doc = Doc(S, S, "store, motif: the bag sealed with a cash coin"); c = CARD["store"]; card(doc, c)
    glyph(doc, handle(10.5, 7.6, 6.4, 3.4, 1.3), RED, under=c)
    glyph(doc, bag(3.5, 17.5, 7.0, 18.0), under=c)
    glyph(doc, coin(10.5, 12.6, 3.4, 2.0), GOLD, rule="evenodd")
    glyph(doc, circle(X(10.5), X(12.6), 2.6 * FEN) + circle(X(10.5), X(12.6), 2.25 * FEN), shade(GOLD, -5), rule="evenodd")
    return doc.svg()


def b_files():
    doc = Doc(S, S, "files, motif: the hand scroll"); c = CARD["files"]; card(doc, c)
    glyph(doc, rrect(X(4.2), X(5.5), 12.6 * FEN, 10.0 * FEN, 0.4 * FEN), under=c)
    for x in (3.0, 16.0):   # rollers with knobs
        glyph(doc, rrect(X(x), X(4.6), 2.0 * FEN, 11.8 * FEN, 1.0 * FEN), GOLD, under=c)
        glyph(doc, rrect(X(x + 0.5), X(3.8), 1.0 * FEN, 13.4 * FEN, 0.5 * FEN), shade(GOLD, -6))
    for j, w in enumerate((8, 5, 8)):
        glyph(doc, rrect(X(6.2), X(7.8 + j * 2.0), w * FEN, 0.9 * FEN, 0.45 * FEN), shade(c, 2))
    glyph(doc, rrect(X(12.4), X(11.6), 2.2 * FEN, 2.2 * FEN, 0.3 * FEN), RED)       # the owner's seal
    return doc.svg()


def b_console():
    doc = Doc(S, S, "console, motif: the seal stamp"); c = CARD["console"]; card(doc, c)
    seal = rrect(X(3.5), X(3.5), 14 * FEN, 14 * FEN, 1.6 * FEN)
    glyph(doc, seal, RED, under=c)
    inner = rrect(X(4.6), X(4.6), 11.8 * FEN, 11.8 * FEN, 1.0 * FEN) + rrect(X(5.2), X(5.2), 10.6 * FEN, 10.6 * FEN, 0.7 * FEN)
    glyph(doc, inner, WHITE, rule="evenodd")
    glyph(doc, chevron(6.8, 9.4, 2.4, 1.5), WHITE)
    glyph(doc, rrect(X(10.4), X(12.0), 4.4 * FEN, 1.6 * FEN, 0.6 * FEN), WHITE)
    return doc.svg()


def peach(cx, top, w, h):
    """Longevity peach: two shoulders and a pointed tip leaning right, a cleft line down the left."""
    l = w / 2
    return (f"M{f(X(cx))} {f(X(top + 1.4))}"
            f"C{f(X(cx - 0.8))} {f(X(top - 0.2))} {f(X(cx - l))} {f(X(top + 0.6))} {f(X(cx - l))} {f(X(top + h * 0.5))}"
            f"C{f(X(cx - l))} {f(X(top + h * 0.85))} {f(X(cx - l * 0.3))} {f(X(top + h))} {f(X(cx + 0.4))} {f(X(top + h))}"
            f"C{f(X(cx + l * 0.9))} {f(X(top + h))} {f(X(cx + l))} {f(X(top + h * 0.6))} {f(X(cx + l * 0.8))} {f(X(top + h * 0.32))}"
            f"C{f(X(cx + l * 0.6))} {f(X(top + 0.4))} {f(X(cx + 0.9))} {f(X(top - 0.6))} {f(X(cx))} {f(X(top + 1.4))}Z")


def b_doctor():
    doc = Doc(S, S, "doctor, motif: the longevity peach"); c = CARD["doctor"]; card(doc, c)
    leaf = (f"M{f(X(10.2))} {f(X(5.4))}C{f(X(8.0))} {f(X(2.4))} {f(X(4.6))} {f(X(3.0))} {f(X(3.6))} {f(X(4.4))}"
            f"C{f(X(5.2))} {f(X(6.4))} {f(X(8.4))} {f(X(6.6))} {f(X(10.2))} {f(X(5.4))}Z")
    glyph(doc, leaf, JADE, under=c)
    pd = peach(10.8, 4.4, 13.6, 13.4)
    glyph(doc, pd, under=c)
    i = doc.id("pk")
    doc.defs.append(f'<linearGradient id="{i}" x1="0.75" y1="0" x2="0.25" y2="1"><stop offset="0" stop-color="{RED}"/>'
                    f'<stop offset="0.55" stop-color="{shade(RED, 9)}" stop-opacity="0.35"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>')
    doc.add(f'<path d="{pd}" fill="url(#{i})"/>')
    glyph(doc, pulse(11.4, 5.4, 16.0, 0.9), RED)
    return doc.svg()


def luopan(cx, cy, r):
    return (circle(X(cx), X(cy), r * FEN), circle(X(cx), X(cy), r * 0.68 * FEN), circle(X(cx), X(cy), r * 0.3 * FEN))


def b_atlas():
    doc = Doc(S, S, "atlas folio, motif: folio with a luopan dial"); c = CARD["atlas"]; card(doc, c)
    for i, p in enumerate(map3(3.0, 4.0, 15.0, 12.0, 1.5)):
        glyph(doc, p, WHITE if i != 1 else shade(WHITE, -3), under=c if i == 0 else None)
    o, m, n = luopan(13.0, 11.0, 3.2)
    glyph(doc, o, GOLD, under=WHITE)
    glyph(doc, m, shade(GOLD, -6))
    ticks = "".join(f"M{f(X(13.0) + 2.2 * FEN * math.cos(a))} {f(X(11.0) + 2.2 * FEN * math.sin(a))}L{f(X(13.0) + 3.0 * FEN * math.cos(a))} {f(X(11.0) + 3.0 * FEN * math.sin(a))}" for a in [k * math.pi / 4 for k in range(8)])
    doc.add(f'<path d="{ticks}" stroke="{shade(GOLD, -9)}" stroke-width="{f(0.3 * FEN)}" stroke-linecap="round"/>')
    needle = f"M{f(X(13.0))} {f(X(11.0 - 1.9))}L{f(X(13.0 + 0.5))} {f(X(11.0))}L{f(X(13.0))} {f(X(11.0 + 1.9))}L{f(X(13.0 - 0.5))} {f(X(11.0))}Z"
    glyph(doc, needle, RED)
    glyph(doc, n, WHITE)
    return doc.svg()


# ===================================================== C jianzhi (paper-cut)
PAPER = from_oklch(0.975, C0 * 1.2 / 21, HUE["earth"])


def crescent(cx, cy, r, ang, thick=0.42):
    """A crescent cut (yueya wen): a disc minus an offset disc."""
    ox, oy = math.cos(ang) * r * thick, math.sin(ang) * r * thick
    return circle(X(cx), X(cy), r * FEN), circle(X(cx) + ox * FEN, X(cy) + oy * FEN, r * 0.86 * FEN)


def cut(doc, base_d, colour, cuts, lift=0.8):
    """Paper glyph lifted off the card: shadow 1:2, then the paper with its cuts showing the card."""
    mid = doc.id("m")
    holes = "".join(f'<path d="{d}" fill-rule="evenodd" fill="#000"/>' for d in cuts)
    doc.defs.append(f'<mask id="{mid}"><rect width="{S}" height="{S}" fill="#fff"/>{holes}</mask>')
    doc.add(f'<g mask="url(#{mid})"><path d="{base_d}" transform="translate({f(0.3 * lift * FEN)} {f(0.6 * lift * FEN)})" fill="{shade(PAPER, -10)}" opacity="0.8"/>'
            f'<path d="{base_d}" fill="{colour}"/></g>')


def crescents_ring(cx, cy, r, n, size, out=True):
    res = []
    for k in range(n):
        a = k / n * 2 * math.pi - math.pi / 2
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        disc, off = crescent(x, y, size, a + (0 if out else math.pi))
        res.append(disc)
        res.append(None)
        res[-1] = ("keep", off)
    return res


def jz_cuts(spec):
    """Flatten crescent specs into hole paths: a crescent hole = disc minus offset disc (evenodd)."""
    out = []
    for cx, cy, r, ang in spec:
        d1, d2 = crescent(cx, cy, r, ang)
        out.append(d1 + d2)
    return out


def c_card(doc):
    d = IE.card_path()
    doc.shadow(d, shade(PAPER, -18), FEN, opacity=0.24, lift=1.2)
    doc.add(f'<path d="{d}" fill="{doc.lit(PAPER, 1.5)}"/>')


def c_settings():
    doc = Doc(S, S, "settings, jianzhi"); c_card(doc)
    d = gear_path(X(10.5), X(10.5), 7.6 * FEN, 5.9 * FEN)
    holes = [circle(X(10.5), X(10.5), 2.4 * FEN)]
    holes += jz_cuts([(10.5 + 4.2 * math.cos(k * math.pi / 4 + math.pi / 8), 10.5 + 4.2 * math.sin(k * math.pi / 4 + math.pi / 8), 0.85, k * math.pi / 4 + math.pi / 8) for k in range(8)])
    cut(doc, d, CARD["settings"], holes)
    glyph(doc, keyhole(X(10.5), X(10.5) - 1.3 * FEN, 1.2 * FEN), CARD["settings"])
    return doc.svg()


def c_store():
    doc = Doc(S, S, "store, jianzhi"); c_card(doc)
    body = bag(3.5, 17.5, 7.0, 18.0) + handle(10.5, 7.6, 6.4, 3.4, 1.3)
    holes = [coin(10.5, 12.8, 2.8, 1.6).split("Z", 1)[1] if False else f"M{f(X(9.7))} {f(X(12.0))}h{f(1.6 * FEN)}v{f(1.6 * FEN)}h{f(-1.6 * FEN)}Z"]
    holes += [circle(X(10.5), X(12.8), 3.2 * FEN) + circle(X(10.5), X(12.8), 2.5 * FEN)]   # the coin ring
    holes += jz_cuts([(5.6, 9.4, 0.8, -math.pi * 0.75), (15.4, 9.4, 0.8, -math.pi * 0.25)])
    cut(doc, body, from_oklch(K.ladder(L0, 0), C0 * 16 / 21, HUE["earth"] - 8), holes)
    return doc.svg()


def c_files():
    doc = Doc(S, S, "files, jianzhi"); c_card(doc)
    d = folder(3.0, 5.0, 15.0, 11.5)
    holes = [rrect(X(5.0), X(9.0 + j * 2.2), (9 if j % 2 == 0 else 6) * FEN, 0.9 * FEN, 0.45 * FEN) for j in range(3)]
    holes += jz_cuts([(15.0, 13.6, 1.0, math.pi * 0.25)])
    cut(doc, d, CARD["files"], holes)
    return doc.svg()


def c_console():
    doc = Doc(S, S, "console, jianzhi"); c_card(doc)
    d = rrect(X(3.0), X(4.5), 15 * FEN, 12 * FEN, 1.6 * FEN)
    holes = [chevron(5.6, 10.5, 2.6, 1.5), rrect(X(10.4), X(12.4), 5.2 * FEN, 1.6 * FEN, 0.6 * FEN)]
    holes += jz_cuts([(4.6 + k * 1.3, 6.0, 0.4, -math.pi / 2) for k in range(3)])
    cut(doc, d, CARD["console"], holes)
    return doc.svg()


def c_doctor():
    doc = Doc(S, S, "doctor, jianzhi"); c_card(doc)
    d = heart(X(10.5), X(4.0), 15 * FEN, 13.6 * FEN)
    holes = [pulse(10.0, 5.2, 15.8, 1.1)]
    holes += jz_cuts([(6.4, 7.0, 1.0, -math.pi * 0.7), (14.6, 7.0, 1.0, -math.pi * 0.3), (10.5, 14.2, 0.9, math.pi / 2)])
    cut(doc, d, RED, holes)
    return doc.svg()


def c_atlas():
    doc = Doc(S, S, "atlas folio, jianzhi"); c_card(doc)
    ps = map3(3.0, 4.0, 15.0, 12.0, 1.5)
    holes = [circle(X(13.2), X(10.8), 1.6 * FEN)]
    holes += jz_cuts([(5.5, 8.0, 0.7, 0.6), (7.0, 10.6, 0.7, 1.2), (9.6, 12.2, 0.7, 0.2)])
    holes += [rrect(X(7.85), X(4.6), 0.3 * FEN, 11.0 * FEN, 0.15 * FEN), rrect(X(12.85), X(4.6), 0.3 * FEN, 11.0 * FEN, 0.15 * FEN)]   # the folds
    cut(doc, "".join(ps), CARD["atlas"], holes)
    glyph(doc, circle(X(13.2), X(10.8), 1.0 * FEN), GOLD)
    return doc.svg()


TYPES = {
    "A-bold": [("Settings", a_settings), ("Store", a_store), ("Files", a_files), ("Console", a_console), ("Doctor", a_doctor), ("Atlas Folio", a_atlas)],
    "B-motif": [("Settings", b_settings), ("Store", b_store), ("Files", b_files), ("Console", b_console), ("Doctor", b_doctor), ("Atlas Folio", b_atlas)],
    "C-jianzhi": [("Settings", c_settings), ("Store", c_store), ("Files", c_files), ("Console", c_console), ("Doctor", c_doctor), ("Atlas Folio", c_atlas)],
}


def main(argv):
    out = argv[0] if argv else os.path.join(HERE, "..", "..", "east", "types")
    for t, icons in TYPES.items():
        os.makedirs(os.path.join(out, t), exist_ok=True)
        for name, fn in icons:
            open(os.path.join(out, t, f"wolos-{name.lower().replace(' ', '-')}.svg"), "w").write(fn())
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main(sys.argv[1:])
