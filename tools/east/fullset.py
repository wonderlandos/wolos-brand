# SPDX-License-Identifier: GPL-2.0-or-later
"""Type A2 for the full shipped set (docs/adr/brand-east.md section 8.2), in batches of six.

  python3 -I design/tools/east/fullset.py BATCH [--sheet OUT.png]      BATCH = 1, 2, ...

Writes east/fullset/wolos-<app>.svg and small/; with --sheet, the current vs A2 board with the
eight-rule scores and the craft checks (scored in parallel, par.fanout)."""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location("east_types", os.path.join(HERE, "types.py"))
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)
from geom import Doc, rrect, circle, juzhe, smooth, shade, f  # noqa: E402

D = os.path.normpath(os.path.join(HERE, "..", ".."))
S = 1024
VIOLET, INK, JADE_CARD, AZURITE, LAKE, OCHRE = (T.CARD["settings"], T.CARD["console"], T.CARD["doctor"],
                                                T.CARD["files"], T.CARD["atlas"], T.STORE_A2)
WHITE, GOLD, RED, JADE = T.WHITE, T.GOLD, T.RED, T.JADE


def start(title, card):
    T.a2_setup()
    doc = Doc(S, S, title)
    T.a2_card(doc, card)
    return doc, T.X, T.FEN


def g(doc, d, colour=WHITE, small=False, elev="glyph", rule="nonzero"):
    T.g2(doc, d, colour, small=small, elev=elev, rule=rule)


def flat(doc, d, colour, rule="nonzero"):
    doc.add(f'<path d="{d}" fill-rule="{rule}" fill="{colour}"/>')


# ---------------------------------------------------------------- batch 1
def calculator(small=False):
    doc, X, F = start("calculator, A2", INK)
    keys = [(3.0, 3.0), (11.0, 3.0), (3.0, 11.0), (11.0, 11.0)]          # 7 x 7 keys, 1 fen gap
    for i, (x, y) in enumerate(keys):
        g(doc, rrect(X(x), X(y), 7 * F, 7 * F, 1.6 * F), GOLD if i == 3 else WHITE, small, "accent" if i == 3 else "glyph")
    th = (1.2 if small else 0.9) * F
    sym = INK
    cx, cy = 6.5, 6.5                                                      # plus
    flat(doc, rrect(X(cx - 2), X(cy) - th / 2, 4 * F, th, th / 2) + rrect(X(cx) - th / 2, X(cy - 2), th, 4 * F, th / 2), sym)
    flat(doc, rrect(X(14.5 - 2), X(6.5) - th / 2, 4 * F, th, th / 2), sym)  # minus
    cx, cy = 6.5, 14.5                                                     # times: the plus turned 45
    flat(doc, f'{rrect(X(cx - 2), X(cy) - th / 2, 4 * F, th, th / 2)}{rrect(X(cx) - th / 2, X(cy - 2), th, 4 * F, th / 2)}', sym)
    doc.body[-1] = doc.body[-1].replace("<path ", f'<path transform="rotate(45 {f(X(cx))} {f(X(cy))})" ')
    for dy in (-0.9, 0.9):                                                 # equals, on the gold key
        flat(doc, rrect(X(12.5), X(14.5 + dy) - th / 2, 4 * F, th, th / 2), INK)
    return doc.svg()


def calendar(small=False):
    doc, X, F = start("calendar, A2", JADE_CARD)
    page = rrect(X(3.0), X(4.0), 15 * F, 14.5 * F, 1.6 * F)
    g(doc, page, small=small)
    band = rrect(X(3.0), X(4.0), 15 * F, 4.0 * F, 1.6 * F, 1.6 * F, 0, 0)
    flat(doc, band, T.leaf(JADE_CARD))
    for x in (7.0, 14.0):                                                  # the rings
        g(doc, rrect(X(x - 0.6), X(2.4), 1.2 * F, 3.4 * F, 0.6 * F), shade(JADE_CARD, -8), small, "accent")
    if small:
        g(doc, circle(X(10.5), X(13.2), 2.6 * F), RED, small, "accent")
    else:
        for r in range(2):
            for c in range(4):
                x, y = 5.0 + c * 3.0, 10.2 + r * 3.4
                if (r, c) == (1, 2):
                    g(doc, circle(X(x + 0.5), X(y + 0.5), 1.25 * F), RED, small, "accent")
                else:
                    flat(doc, rrect(X(x - 0.4), X(y - 0.4), 1.8 * F, 1.8 * F, 0.5 * F), T.leaf(JADE_CARD))
    return doc.svg()


def control_center(small=False):
    doc, X, F = start("control center, A2", VIOLET)
    for i, (y, on) in enumerate(((4.0, True), (11.5, False))):
        pill = rrect(X(3.0), X(y), 15 * F, 5.5 * F, 2.75 * F)
        g(doc, pill, WHITE if on else T.leaf(VIOLET), small)
        kx = 15.25 if on else 5.75
        g(doc, circle(X(kx), X(y + 2.75), 2.0 * F), GOLD if on else WHITE, small, "accent")
    return doc.svg()


def games(small=False):
    doc, X, F = start("games, A2", VIOLET)
    # controller: a body 15 x 8 with two grips falling to y 17 (water forms: no corner)
    body = (f"M{f(X(6.0))} {f(X(6.5))}H{f(X(15.0))}C{f(X(18.2))} {f(X(6.5))} {f(X(19.0))} {f(X(10.5))} {f(X(18.6))} {f(X(14.5))}"
            f"C{f(X(18.3))} {f(X(17.4))} {f(X(15.6))} {f(X(17.6))} {f(X(14.4))} {f(X(15.0))}L{f(X(13.4))} {f(X(13.4))}H{f(X(7.6))}"
            f"L{f(X(6.6))} {f(X(15.0))}C{f(X(5.4))} {f(X(17.6))} {f(X(2.7))} {f(X(17.4))} {f(X(2.4))} {f(X(14.5))}"
            f"C{f(X(2.0))} {f(X(10.5))} {f(X(2.8))} {f(X(6.5))} {f(X(6.0))} {f(X(6.5))}Z")
    g(doc, body, small=small)
    th = (1.4 if small else 1.1) * F
    cx, cy = 6.5, 10.0                                                     # d-pad
    flat(doc, rrect(X(cx - 1.9), X(cy) - th / 2, 3.8 * F, th, th / 3) + rrect(X(cx) - th / 2, X(cy - 1.9), th, 3.8 * F, th / 3), VIOLET)
    for (x, y) in ((14.0, 9.0), (15.9, 11.0)):                            # two buttons (fire as accent)
        g(doc, circle(X(x), X(y), (1.1 if not small else 1.3) * F), RED, small, "accent")
    return doc.svg()


def installer(small=False):
    doc, X, F = start("installer, A2", VIOLET)
    # the door (the mark's arch), 11 wide x 15 tall, with the down arrow inside it
    w, top, bot = 11.0, 3.0, 18.0
    r = w / 2 * F
    door = f"M{f(X(10.5 - w / 2))} {f(X(bot))}V{f(X(top) + r)}A{f(r)} {f(r)} 0 0 1 {f(X(10.5 + w / 2))} {f(X(top) + r)}V{f(X(bot))}Z"
    g(doc, door, small=small)
    th = (1.8 if small else 1.4) * F
    stem = rrect(X(10.5) - th / 2, X(7.0), th, 6.0 * F, th / 2)
    head = T.ribbon([(X(7.6), X(10.6)), (X(10.5), X(13.6)), (X(13.4), X(10.6))], th)
    g(doc, stem + head, GOLD, small, "accent")
    return doc.svg()


def launcher(small=False):
    """Search: the lens (a ring 12 fen across) and its handle along the light's 1:2 diagonal; the
    keyhole in the lens is the landing (what you look for opens)."""
    doc, X, F = start("launcher (search), A2", VIOLET)
    cx, cy, ro, ri = 9.0, 9.0, 6.0, 4.4 if not small else 4.0
    ring = circle(X(cx), X(cy), ro * F) + circle(X(cx), X(cy), ri * F)
    ang = math.atan2(2, 1)                                   # down-right, 1:2
    x0, y0 = cx + ro * 0.92 * math.cos(ang), cy + ro * 0.92 * math.sin(ang)
    x1, y1 = cx + (ro + 4.4) * math.cos(ang), cy + (ro + 4.4) * math.sin(ang)   # ends 2 fen inside the card: no line into the frame
    hnd = T.ribbon([(X(x0), X(y0)), (X(x1), X(y1))], (2.6 if small else 2.2) * F)
    g(doc, ring + hnd, small=small, rule="evenodd")
    g(doc, T.keyhole_at(X(cx), X(cy), (2.6 if small else 2.0) * F), GOLD, small, "accent")
    return doc.svg()


BATCHES = {1: [("calculator", calculator), ("calendar", calendar), ("control-center", control_center),
               ("games", games), ("installer", installer), ("launcher", launcher)]}


# ---------------------------------------------------------------- batch 2
def sparkle(X, F, cx, cy, r, k=0.18):
    """Four points with concave flanks (each flank bows in toward the centre)."""
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    d = f"M{f(X(pts[0][0]))} {f(X(pts[0][1]))}"
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        d += f"Q{f(X(cx + (a[0] + b[0] - 2 * cx) * k))} {f(X(cy + (a[1] + b[1] - 2 * cy) * k))} {f(X(b[0]))} {f(X(b[1]))}"
    return d + "Z"


def kit_ai(small=False):
    doc, X, F = start("kit ai, A2", VIOLET)
    g(doc, sparkle(X, F, 9.5, 11.0, 7.0), small=small)
    g(doc, sparkle(X, F, 16.0, 5.0, 2.6), WHITE, small)
    g(doc, circle(X(9.5), X(11.0), 1.6 * F), GOLD, small, "accent")
    return doc.svg()


def kit_codecs(small=False):
    doc, X, F = start("kit codecs, A2", INK)
    tri = T.ribbon([(X(6.5), X(4.5)), (X(17.0), X(10.5)), (X(6.5), X(16.5)), (X(6.5), X(4.5))], 0.1 * F)
    r = 1.6 * F
    body = (f"M{f(X(6.0))} {f(X(5.6))}Q{f(X(6.0))} {f(X(3.6))} {f(X(7.8))} {f(X(4.6))}L{f(X(16.6))} {f(X(9.4))}"
            f"Q{f(X(18.2))} {f(X(10.5))} {f(X(16.6))} {f(X(11.6))}L{f(X(7.8))} {f(X(16.4))}Q{f(X(6.0))} {f(X(17.4))} {f(X(6.0))} {f(X(15.4))}Z")
    g(doc, body, small=small)
    g(doc, circle(X(10.0), X(10.5), 1.8 * F), JADE, small, "accent")
    return doc.svg()


def kit_craft_suite(small=False):
    doc, X, F = start("kit craft suite, A2", OCHRE)
    g(doc, T.ribbon([(X(16.6), X(3.6)), (X(10.2), X(11.0))], (2.8 if small else 1.6) * F), small=small)
    g(doc, T.ribbon([(X(10.6), X(10.6)), (X(9.2), X(12.2))], 2.6 * F), T.leaf(OCHRE), small)
    tip = (f"M{f(X(8.2))} {f(X(11.2))}C{f(X(10.6))} {f(X(12.4))} {f(X(10.4))} {f(X(14.8))} {f(X(8.4))} {f(X(16.6))}"
           f"C{f(X(7.0))} {f(X(17.8))} {f(X(4.4))} {f(X(18.2))} {f(X(3.4))} {f(X(17.8))}C{f(X(4.6))} {f(X(16.8))} {f(X(5.2))} {f(X(15.2))} {f(X(5.6))} {f(X(13.6))}"
           f"C{f(X(6.0))} {f(X(12.2))} {f(X(7.0))} {f(X(11.0))} {f(X(8.2))} {f(X(11.2))}Z")
    g(doc, tip, VIOLET, small, "accent")
    return doc.svg()


def kit_creative(small=False):
    doc, X, F = start("kit creative, A2", JADE_CARD)
    pal = circle(X(10.5), X(10.5), 7.5 * F) + circle(X(13.6), X(14.0), 1.6 * F)
    g(doc, pal, small=small, rule="evenodd")
    for (x, y), c in zip(((7.0, 8.0), (10.5, 6.0), (14.2, 8.0), (7.4, 12.6)), (RED, GOLD, VIOLET, LAKE)):
        g(doc, circle(X(x), X(y), (1.5 if not small else 1.8) * F), c, small, "accent")
    return doc.svg()


def brace(X, F, x, flip, th):
    s = -1 if flip else 1
    pts = [(x + 2.0 * s, 3.5), (x + 0.6 * s, 4.2), (x + 0.6 * s, 9.0), (x - 1.0 * s, 10.5), (x + 0.6 * s, 12.0), (x + 0.6 * s, 16.8), (x + 2.0 * s, 17.5)]
    return T.ribbon([(X(a), X(b)) for a, b in pts], th)


def kit_dev(small=False):
    doc, X, F = start("kit dev, A2", INK)
    th = (1.8 if small else 1.5) * F
    g(doc, brace(X, F, 5.5, False, th) + brace(X, F, 15.5, True, th), small=small)
    g(doc, circle(X(10.5), X(10.5), (1.8 if not small else 2.2) * F), JADE, small, "accent")
    return doc.svg()


def kit_gaming(small=False):
    doc, X, F = start("kit gaming, A2", VIOLET)
    th = 5.0 * F
    cross = rrect(X(3.0), X(10.5) - th / 2, 15 * F, th, 1.4 * F) + rrect(X(10.5) - th / 2, X(3.0), th, 15 * F, 1.4 * F)
    g(doc, cross, small=small)
    for (x, y, a) in ((10.5, 5.2, 0), (15.8, 10.5, 90), (10.5, 15.8, 180), (5.2, 10.5, 270)):
        tri = f"M{f(X(x))} {f(X(y) - 0.9 * F)}L{f(X(x) + 0.9 * F)} {f(X(y) + 0.6 * F)}L{f(X(x) - 0.9 * F)} {f(X(y) + 0.6 * F)}Z"
        doc.add(f'<path d="{tri}" transform="rotate({a} {f(X(x))} {f(X(y))})" fill="{T.leaf(VIOLET)}"/>')
    g(doc, circle(X(10.5), X(10.5), 1.8 * F), GOLD, small, "accent")
    return doc.svg()


def mail(small=False):
    doc, X, F = start("mail, A2", AZURITE)
    env = rrect(X(3.0), X(5.5), 15 * F, 10.5 * F, 1.4 * F)
    g(doc, env, small=small)
    flap = T.ribbon([(X(4.0), X(6.6)), (X(10.5), X(11.4)), (X(17.0), X(6.6))], (1.2 if small else 0.9) * F)
    flat(doc, flap, T.leaf(AZURITE))
    g(doc, circle(X(10.5), X(11.4), (2.0 if not small else 2.4) * F), GOLD, small, "accent")
    return doc.svg()


# ---------------------------------------------------------------- batch 3
def music(small=False):
    doc, X, F = start("music, A2", VIOLET)
    th = (1.4 if small else 1.1) * F
    beam = f"M{f(X(8.0))} {f(X(4.4))}L{f(X(16.6))} {f(X(3.0))}V{f(X(5.6))}L{f(X(8.0))} {f(X(7.0))}Z"
    stems = rrect(X(8.0), X(5.0), th, 10.2 * F, th / 2) + rrect(X(16.6) - th, X(3.6), th, 10.2 * F, th / 2)
    g(doc, beam + stems, small=small)
    for (x, y) in ((6.0, 15.4), (14.6, 14.0)):
        head = f'<ellipse cx="{f(X(x))}" cy="{f(X(y))}" rx="{f(2.6 * F)}" ry="{f(2.0 * F)}"/>'
        d = f"M{f(X(x) - 2.6 * F)} {f(X(y))}A{f(2.6 * F)} {f(2.0 * F)} 0 1 0 {f(X(x) + 2.6 * F)} {f(X(y))}A{f(2.6 * F)} {f(2.0 * F)} 0 1 0 {f(X(x) - 2.6 * F)} {f(X(y))}Z"
        doc.body.append(f'<g transform="rotate(-20 {f(X(x))} {f(X(y))})">')
        g(doc, d, GOLD if x > 10 else WHITE, small, "accent" if x > 10 else "glyph")
        doc.body.append("</g>")
    return doc.svg()


def page(X, F, x0, y0, w, h, fold=3.0):
    return (f"M{f(X(x0) + F)} {f(X(y0))}H{f(X(x0 + w - fold))}L{f(X(x0 + w))} {f(X(y0 + fold))}V{f(X(y0 + h) - F)}"
            f"Q{f(X(x0 + w))} {f(X(y0 + h))} {f(X(x0 + w) - F)} {f(X(y0 + h))}H{f(X(x0) + F)}Q{f(X(x0))} {f(X(y0 + h))} {f(X(x0))} {f(X(y0 + h) - F)}"
            f"V{f(X(y0) + F)}Q{f(X(x0))} {f(X(y0))} {f(X(x0) + F)} {f(X(y0))}Z")


def lines(doc, X, F, x0, y0, widths, colour, pitch=2.2):
    for j, w in enumerate(widths):
        doc.add(f'<path d="{rrect(X(x0), X(y0 + j * pitch), w * F, 0.9 * F, 0.45 * F)}" fill="{colour}"/>')


def notes(small=False):
    doc, X, F = start("notes, A2", OCHRE)
    g(doc, page(X, F, 4.5, 3.0, 12.0, 15.0, fold=0.01), small=small)
    if not small:
        lines(doc, X, F, 6.5, 7.0, (8, 5, 8, 5), T.leaf(OCHRE))
    g(doc, circle(X(10.5), X(3.6), (1.6 if not small else 2.0) * F), VIOLET, small, "accent")
    return doc.svg()


def photos(small=False):
    doc, X, F = start("photos, A2", LAKE)
    frame = rrect(X(3.0), X(4.5), 15 * F, 12 * F, 1.6 * F)
    cid = doc.id("pc")
    doc.defs.append(f'<clipPath id="{cid}"><path d="{frame}"/></clipPath>')
    g(doc, frame, small=small)
    far = juzhe(X(12.0), X(8.6), X(18.4), X(13.4), purlins=4, first=0.12)
    far_l = juzhe(X(12.0), X(8.6), X(6.0), X(16.6), purlins=4, first=0.12)[::-1]
    near = juzhe(X(7.6), X(10.4), X(14.0), X(16.6), purlins=4, first=0.12)
    near_l = juzhe(X(7.6), X(10.4), X(2.6), X(16.6), purlins=4, first=0.12)[::-1]
    for pts, c in ((far_l + far[1:], T.leaf(LAKE)), (near_l + near[1:], shade(LAKE, -2))):
        d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts) + f"L{f(X(18.4))} {f(X(17))}L{f(X(2.6))} {f(X(17))}Z"
        doc.add(f'<path d="{d}" fill="{c}" clip-path="url(#{cid})"/>')
    g(doc, circle(X(14.6), X(7.4), (1.8 if not small else 2.2) * F), GOLD, small, "accent")
    return doc.svg()


def plugin_maker(small=False):
    doc, X, F = start("plugin maker, A2", INK)
    # the knob is drawn first and the body over it (one union, no winding cut)
    g(doc, circle(X(9.0), X(6.5), 2.2 * F), small=small)
    g(doc, rrect(X(3.5), X(6.5), 11 * F, 11 * F, 1.4 * F), small=small)
    g(doc, circle(X(14.5), X(12.0), 2.4 * F), JADE, small, "accent")
    return doc.svg()


def system_monitor(small=False):
    doc, X, F = start("system monitor, A2", JADE_CARD)
    cx, cy, r = 10.5, 12.0, 6.6
    pts = [(X(cx + r * math.cos(a)), X(cy + r * math.sin(a))) for a in [math.pi * (0.85 + 1.3 * t / 24) for t in range(25)]]
    g(doc, T.ribbon(pts, (2.4 if small else 2.0) * F), small=small)
    ang = math.radians(-50)
    nd = T.ribbon([(X(cx), X(cy)), (X(cx + 5.0 * math.cos(ang)), X(cy + 5.0 * math.sin(ang)))], (1.4 if small else 1.1) * F)
    g(doc, nd + circle(X(cx), X(cy), 1.6 * F), RED, small, "accent")
    return doc.svg()


def text_editor(small=False):
    doc, X, F = start("text editor, A2", AZURITE)
    g(doc, page(X, F, 4.0, 3.0, 13.0, 15.0), small=small)
    if not small:
        lines(doc, X, F, 6.0, 7.4, (8, 6, 8), T.leaf(AZURITE), pitch=2.4)
    g(doc, rrect(X(6.0), X(13.6), 7.0 * F, 1.0 * F, 0.5 * F) if not small else rrect(X(6.0), X(9.0), 7 * F, 1.4 * F, 0.7 * F), T.leaf(AZURITE), small)
    g(doc, rrect(X(13.4), X(12.4), (1.1 if not small else 1.5) * F, 3.6 * F, 0.5 * F), GOLD, small, "accent")
    return doc.svg()


METAL = T.from_oklch(0.92, 0.012, T.H0)


def trash(small=False):
    doc, X, F = start("trash, A2", METAL)
    lid = rrect(X(4.0), X(4.0), 13 * F, 1.8 * F, 0.9 * F) + rrect(X(8.5), X(2.6), 4 * F, 2.0 * F, 0.8 * F)
    body = f"M{f(X(5.2))} {f(X(6.6))}H{f(X(15.8))}L{f(X(14.8))} {f(X(17.6))}Q{f(X(14.7))} {f(X(18.5))} {f(X(13.8))} {f(X(18.5))}H{f(X(7.2))}Q{f(X(6.3))} {f(X(18.5))} {f(X(6.2))} {f(X(17.6))}Z"
    g(doc, lid + body, INK, small)
    if not small:
        for x in (8.2, 10.5, 12.8):
            doc.add(f'<path d="{rrect(X(x) - 0.4 * F, X(8.6), 0.8 * F, 8.0 * F, 0.4 * F)}" fill="{METAL}" opacity="0.5"/>')
    return doc.svg()


BATCHES[2] = [("kit-ai", kit_ai), ("kit-codecs", kit_codecs), ("kit-craft-suite", kit_craft_suite), ("kit-creative", kit_creative),
              ("kit-dev", kit_dev), ("kit-gaming", kit_gaming), ("mail", mail)]
BATCHES[3] = [("music", music), ("notes", notes), ("photos", photos), ("plugin-maker", plugin_maker),
              ("system-monitor", system_monitor), ("text-editor", text_editor), ("trash", trash)]


# ---------------------------------------------------------------- places, devices, mimetypes (cardless)
GROUND = T.from_oklch(0.95, 0.009, T.H0)        # the window ground the shadow falls on (base neutral)
RIVER = T.from_oklch(0.62, 0.15, T.HUE["water"])


def bare(title):
    T.a2_setup()
    doc = Doc(S, S, title)
    doc.card_colour = GROUND
    return doc, T.X, T.FEN


def sym(doc, X, F, kind, cx, cy, col, small=False):
    """Place and type symbols, about 6 fen, centred on (cx, cy)."""
    th = (1.3 if small else 1.0) * F
    if kind == "lines":
        rows = ((6, 4, 6), 2.2) if not small else ((6, 4), 3.2)          # small: two lines, a clear gap
        for j, w in enumerate(rows[0]):
            flat(doc, rrect(X(cx - 3), X(cy - 2.2 + j * rows[1]) - th / 2, w * F, th, th / 2), col)
    elif kind == "arrow":
        flat(doc, rrect(X(cx) - th / 2, X(cy - 3), th, 4.6 * F, th / 2) + T.ribbon([(X(cx - 2.4), X(cy - 0.2)), (X(cx), X(cy + 2.4)), (X(cx + 2.4), X(cy - 0.2))], th), col)
    elif kind == "note":
        flat(doc, rrect(X(cx + 0.4), X(cy - 3), th, 5.2 * F, th / 2) + circle(X(cx - 0.8), X(cy + 2.0), 1.5 * F) +
             T.ribbon([(X(cx + 0.9), X(cy - 2.6)), (X(cx + 2.8), X(cy - 1.6))], th), col)
    elif kind == "mountain":
        flat(doc, f"M{f(X(cx - 3.4))} {f(X(cy + 2.4))}L{f(X(cx - 0.8))} {f(X(cy - 1.4))}L{f(X(cx + 0.8))} {f(X(cy + 0.6))}L{f(X(cx + 1.8))} {f(X(cy - 0.6))}L{f(X(cx + 3.4))} {f(X(cy + 2.4))}Z"
             + circle(X(cx + 2.0), X(cy - 2.4), 0.9 * F), col)
    elif kind == "people":
        flat(doc, circle(X(cx - 1.5), X(cy - 1.4), 1.2 * F) + circle(X(cx + 1.6), X(cy - 1.4), 1.2 * F) +
             rrect(X(cx - 3.4), X(cy + 0.4), 3.8 * F, 2.4 * F, 1.2 * F) + rrect(X(cx - 0.3), X(cy + 0.4), 3.8 * F, 2.4 * F, 1.2 * F), col)
    elif kind == "dashed":
        for (x, y, w, h) in ((-3, -3, 2.0, th / F), (1.0, -3, 2.0, th / F), (-3, 3 - th / F, 2.0, th / F), (1.0, 3 - th / F, 2.0, th / F),
                             (-3, -0.8, th / F, 1.6), (3 - th / F, -0.8, th / F, 1.6)):
            flat(doc, rrect(X(cx + x), X(cy + y), w * F, h * F, th / 2), col)
    elif kind == "play":
        flat(doc, f"M{f(X(cx - 1.8))} {f(X(cy - 2.6))}L{f(X(cx + 2.6))} {f(X(cy))}L{f(X(cx - 1.8))} {f(X(cy + 2.6))}Z", col)
    elif kind == "house":
        roof = juzhe(X(cx), X(cy - 3.2), X(cx + 3.6), X(cy - 0.4), purlins=3, first=0.12)
        rl = [(2 * X(cx) - x, y) for x, y in reversed(roof)]
        d = (f"M{f(rl[0][0])} {f(rl[0][1])}" + smooth(rl) + smooth(roof) + f"L{f(X(cx + 2.6))} {f(X(cy - 0.4))}V{f(X(cy + 2.8))}H{f(X(cx - 2.6))}V{f(X(cy - 0.4))}Z")
        flat(doc, d, col)
        flat(doc, T.keyhole_at(X(cx), X(cy + 1.0), 1.2 * F), GOLD)
    elif kind == "code":
        flat(doc, T.ribbon([(X(cx - 1.2), X(cy - 2.4)), (X(cx - 3.2), X(cy)), (X(cx - 1.2), X(cy + 2.4))], th) +
             T.ribbon([(X(cx + 1.2), X(cy - 2.4)), (X(cx + 3.2), X(cy)), (X(cx + 1.2), X(cy + 2.4))], th), col)
    elif kind == "box":
        flat(doc, rrect(X(cx - 3), X(cy - 2.4), 6 * F, 5.2 * F, 0.6 * F), col)
        flat(doc, rrect(X(cx - 0.6), X(cy - 2.4), 1.2 * F, 2.4 * F, 0.3 * F), GROUND)
    elif kind == "slides":
        flat(doc, rrect(X(cx - 3.2), X(cy - 2.6), 6.4 * F, 4.2 * F, 0.6 * F) + rrect(X(cx) - th / 2, X(cy + 1.6), th, 1.6 * F, th / 2), col)
    elif kind == "grid":
        n, cell, gap = (3, 1.4, 1.0) if not small else (2, 2.4, 1.2)       # gaps that stay open at 16 px
        span = n * cell + (n - 1) * gap
        for r in range(n):
            for c in range(n):
                flat(doc, rrect(X(cx - span / 2 + c * (cell + gap)), X(cy - span / 2 + r * (cell + gap)), cell * F, cell * F, 0.3 * F), col)
    elif kind == "gear":
        flat(doc, T.gear_path(X(cx), X(cy), 3.2 * F, 2.5 * F) + circle(X(cx), X(cy), 1.1 * F), col, "evenodd")
    elif kind == "nodes":
        pts = [(cx - 2.6, cy + 1.8), (cx, cy - 2.2), (cx + 2.6, cy + 1.8)]
        flat(doc, T.ribbon([(X(a), X(b)) for a, b in pts + [pts[0]]], th * 0.8), col)
        for (a, b) in pts:
            flat(doc, circle(X(a), X(b), 1.25 * F), col)
    elif kind == "dot":
        flat(doc, circle(X(cx), X(cy), 2.2 * F), col)


def folder_icon(symbol, colour=None):
    colour = colour or AZURITE

    def fn(small=False):
        doc, X, F = bare(f"folder {symbol}, A2")
        back = T.folder(0.0, 2.0, 21.0, 16.5, tab_w=8.0, tab_h=2.0, r=1.6)
        g(doc, back, shade(colour, -4), small)
        flat(doc, rrect(X(1.6), X(4.6), 17.8 * F, 6 * F, 0.6 * F), WHITE)      # paper: also at 16 px (3:1)
        front = rrect(X(0.0), X(6.0), 21 * F, 12.5 * F, 1.6 * F)
        g(doc, front, colour, small)
        if symbol:
            sym(doc, X, F, symbol, 10.5, 12.4, WHITE, small)
        return doc.svg()
    return fn


def crumple(X, F, cx, cy, r, seed):
    """A crumpled sheet: a rounded polygon with uneven radii (paper, not a ball)."""
    import random
    rnd = random.Random(seed)
    pts = []
    for k in range(9):
        ang = k / 9 * 2 * math.pi
        rr = r * rnd.uniform(0.78, 1.0)
        pts.append((X(cx) + rr * F * math.cos(ang), X(cy) + rr * F * math.sin(ang)))
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"


def bin_icon(full):
    def fn(small=False):
        doc, X, F = bare(f"user trash{' full' if full else ''}, A2")
        # body: tapered (21 fen at the rim, 15 at the foot), rounded foot; a rim band in the leaf
        # tint; three soft grooves; lid: a shallow juzhe dome with a handle
        top, foot = 7.0, 21.0
        body = (f"M{f(X(1.8))} {f(X(top))}H{f(X(19.2))}L{f(X(17.4))} {f(X(foot) - 1.6 * F)}"
                f"Q{f(X(17.1))} {f(X(foot))} {f(X(15.6))} {f(X(foot))}H{f(X(5.4))}Q{f(X(3.9))} {f(X(foot))} {f(X(3.6))} {f(X(foot) - 1.6 * F)}Z")
        if full:      # the paper is INSIDE: drawn before the body, so the front wall covers it and
            # only the crumpled tops show above the rim (lead 07:50Z: it sat on top of the bin)
            sheets = ((7.0, 5.2, 3.3, 3, WHITE), (14.0, 5.4, 3.1, 7, WHITE), (10.6, 4.0, 3.0, 11, GOLD)) if not small else ((8.0, 5.0, 3.4, 3, WHITE), (13.2, 4.8, 3.2, 11, GOLD))
            for (cx, cy, r, sd, c) in sheets:
                g(doc, crumple(X, F, cx, cy, r, sd), c, small, "accent" if c == GOLD else "glyph")
        BIN = shade(VIOLET, -3)    # one step deeper: holds 3:1 under the white paper at 16 px
        g(doc, body, BIN, small)
        flat(doc, rrect(X(1.8), X(top), 17.4 * F, 1.8 * F, 0.6 * F) if False else f"M{f(X(1.8))} {f(X(top))}H{f(X(19.2))}L{f(X(18.95))} {f(X(top + 1.6))}H{f(X(2.05))}Z", shade(BIN, 6))
        if True:
            for x0, x1 in (((7.2, 7.8), (10.2, 10.5), (13.8, 13.2)) if not small else ((7.6, 8.0), (13.4, 13.0))):
                w = 0.9 if not small else 2.2
                groove = T.ribbon([(X(x0), X(top + 3.6)), (X(x1), X(foot - 2.4))], w * F)
                flat(doc, groove, shade(BIN, 6) if not small else WHITE)
        if full:
            return doc.svg()
        dome = juzhe(X(10.5), X(3.4), X(0.4), X(5.6), purlins=3, first=0.14)[::-1] + juzhe(X(10.5), X(3.4), X(20.6), X(5.6), purlins=3, first=0.14)[1:]
        lid = f"M{f(dome[0][0])} {f(dome[0][1])}" + smooth(dome) + f"L{f(X(20.6))} {f(X(6.6))}Q{f(X(20.6))} {f(X(7.0))} {f(X(20.2))} {f(X(7.0))}H{f(X(0.8))}Q{f(X(0.4))} {f(X(7.0))} {f(X(0.4))} {f(X(6.6))}Z"
        handle = rrect(X(8.0), X(1.6), 5 * F, 2.4 * F, 1.2 * F) + rrect(X(9.2), X(2.4), 2.6 * F, 1.2 * F, 0.6 * F)
        g(doc, lid, VIOLET, small)
        g(doc, handle, VIOLET, small, rule="evenodd")
        return doc.svg()
    return fn


def object_icon(kind):
    def fn(small=False):
        if kind == "desktop":
            doc, X, F = bare("user desktop, A2")
            g(doc, rrect(X(0), X(2.5), 21 * F, 13.5 * F, 1.6 * F), VIOLET, small)
            flat(doc, rrect(X(1.4), X(3.9), 18.2 * F, 10.7 * F, 0.8 * F), T.leaf(VIOLET))
            g(doc, rrect(X(8.0), X(14.8), 5 * F, 3.6 * F, 0.4 * F) + rrect(X(5.0), X(18.0), 11 * F, 1.8 * F, 0.9 * F), INK, small)   # stand joins screen and foot
            g(doc, circle(X(10.5), X(9.2), 2.0 * F), GOLD, small, "accent")
        elif kind == "network":
            doc, X, F = bare("network workgroup, A2")
            # three computers (upper left = the entry, upper right, bottom centre) joined through a
            # gold hub, the landing; screens are 8 x 6 fen, links are soft ribbons
            hub = (10.5, 10.8)
            scr = [(0.0, 1.0), (13.0, 1.0), (6.5, 14.0)]
            for (x, y) in scr:
                g(doc, T.ribbon([(X(hub[0]), X(hub[1])), (X(x + 4), X(y + 3))], 1.2 * F), shade(LAKE, 4), small)
            for (x, y) in scr:
                g(doc, rrect(X(x), X(y), 8 * F, 6 * F, 1.2 * F), LAKE, small)
                flat(doc, rrect(X(x + 1.0), X(y + 1.0), 6 * F, 3.6 * F, 0.6 * F), WHITE if small else T.leaf(LAKE))
            g(doc, circle(X(hub[0]), X(hub[1]), 3.0 * F), GOLD, small, "accent")
        elif kind == "harddisk":
            doc, X, F = bare("drive harddisk, A2")
            g(doc, rrect(X(0), X(5.5), 21 * F, 10 * F, 2.0 * F), VIOLET, small)
            g(doc, rrect(X(2.4), X(9.6), 9 * F, 2.4 * F, 1.2 * F), WHITE, small)
            g(doc, circle(X(17.4), X(10.8), 1.2 * F), JADE, small, "accent")
        elif kind == "removable":
            doc, X, F = bare("drive removable media, A2")
            g(doc, rrect(X(7.0), X(1.0), 7 * F, 5 * F, 0.8 * F), T.leaf(VIOLET), small)
            g(doc, rrect(X(3.0), X(5.0), 15 * F, 15 * F, 2.4 * F), VIOLET, small)
            g(doc, rrect(X(6.0), X(9.0), 9 * F, 2.4 * F, 1.2 * F), WHITE, small)
            g(doc, circle(X(10.5), X(15.4), 1.3 * F), JADE, small, "accent")
        return doc.svg()
    return fn


def mime_icon(colour, symbol):
    """A page with its folded corner; the type's colour is a chip at the upper left (the entry),
    the symbol sits large in the page's lower middle (the landing). No full-width band: a straight
    edge across the page is a sha cut."""
    def fn(small=False):
        doc, X, F = bare(f"mimetype {symbol}, A2")
        pg = page(X, F, 3.0, 0.0, 15.0, 21.0, fold=4.0)
        g(doc, pg, WHITE, small)
        fold = f"M{f(X(14.0))} {f(X(0))}V{f(X(3.2))}Q{f(X(14.0))} {f(X(4.0))} {f(X(14.8))} {f(X(4.0))}H{f(X(18.0))}Z"
        flat(doc, fold, T.leaf(colour))
        g(doc, rrect(X(5.0), X(2.4), (6.0 if not small else 7.0) * F, (2.4 if not small else 3.0) * F, 1.2 * F), colour, small, "accent")
        doc.body.append(f'<g transform="translate({f(X(10.5))} {f(X(12.8))}) scale(1.35) translate({f(-X(10.5))} {f(-X(12.8))})">')
        sym(doc, X, F, symbol, 10.5, 12.8, colour, small)
        doc.body.append("</g>")
        return doc.svg()
    return fn


BATCHES[4] = [("folder", folder_icon(None)), ("folder-documents", folder_icon("lines")), ("folder-download", folder_icon("arrow")),
              ("folder-music", folder_icon("note")), ("folder-pictures", folder_icon("mountain")), ("folder-publicshare", folder_icon("people")),
              ("folder-templates", folder_icon("dashed")), ("folder-videos", folder_icon("play")), ("user-home", folder_icon("house")),
              ("user-desktop", object_icon("desktop")), ("network-workgroup", folder_icon("nodes", LAKE)),
              ("user-trash", bin_icon(False)), ("user-trash-full", bin_icon(True))]
BATCHES[5] = [("drive-harddisk", object_icon("harddisk")), ("drive-removable-media", object_icon("removable")),
              ("application-pdf", mime_icon(RED, "lines")), ("application-x-executable", mime_icon(INK, "gear")),
              ("application-x-generic", mime_icon(VIOLET, "dot")), ("audio-x-generic", mime_icon(VIOLET, "note")),
              ("image-x-generic", mime_icon(LAKE, "mountain")), ("package-x-generic", mime_icon(OCHRE, "box")),
              ("text-x-generic", mime_icon(INK, "lines")), ("video-x-generic", mime_icon(INK, "play")),
              ("x-office-document", mime_icon(AZURITE, "lines")), ("x-office-presentation", mime_icon(OCHRE, "slides")),
              ("x-office-spreadsheet", mime_icon(JADE_CARD, "grid"))]


def current_path(n):
    for ctx in ("apps", "places", "devices", "mimetypes"):
        for nm in (f"wolos-{n}.svg", f"{n}.svg"):
            p = os.path.join(D, "icons", ctx, nm)
            if os.path.exists(p):
                return p
    return None


def fname(n):
    return f"wolos-{n}.svg" if os.path.exists(os.path.join(D, "icons", "apps", f"wolos-{n}.svg")) else f"{n}.svg"


def _job(args):
    b, i, small = args
    name, fn = BATCHES[b][i]
    out = os.path.join(D, "east", "fullset", "small" if small else "")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, fname(name)), "w").write(fn(small))
    return name


def _score(p):
    import board as B
    import craft
    s = B.scored(p, "icon")
    c = craft.check(p)
    return s, [k for k, (ok, _) in c.items() if not ok]


def sheet(b, out):
    import board as B
    from par import fanout
    from PIL import Image, ImageDraw
    names = [n for n, _ in BATCHES[b]]
    cur = [current_path(n) for n in names]
    new = [os.path.join(D, "east", "fullset", fname(n)) for n in names]
    small = [os.path.join(D, "east", "fullset", "small", fname(n)) for n in names]
    res = fanout(_score, cur + new + small)
    k = len(names)
    if k > 7:
        a = sheet_rows(b, names, cur, new, small, res, out)
        return a
    cw, pad = 230, 24
    W, H = pad + k * (cw + pad), 720
    im = Image.new("RGB", (W, H), B.BG)
    dr = ImageDraw.Draw(im)
    dr.text((pad, 10), f"Type A2, full set, batch {b}: current (top) vs A2 (bottom), score 0-100, craft checks", font=B.font(20, True), fill=B.INK)
    for i, n in enumerate(names):
        x = pad + i * (cw + pad)
        (sa, fa), (sb, fb), (_, fs) = res[i], res[k + i], res[2 * k + i]
        for row, (p, s) in enumerate(((cur[i], sa), (new[i], sb))):
            y = 50 + row * 300
            ic = B.raster(p, 200, 200)
            im.paste(ic, (x + 10, y), ic)
            col = B.INK if row == 0 else (B.GOOD if sb["total"] > sa["total"] else B.BAD)
            dr.text((x + 10, y + 208), f"{n}  {s['total']:.1f}", font=B.font(17, True), fill=col)
        for j, sz in enumerate((16, 32, 64)):
            t = B.raster(small[i] if sz <= 32 else new[i], sz, sz)
            im.paste(t, (x + 10 + j * 60, 600 + (64 - sz) // 2), t)
        bad = sorted(set(fb) | set(fs))
        dr.text((x + 10, 680), "craft: pass" if not bad else "craft FAIL: " + ", ".join(bad), font=B.font(13, True), fill=B.GOOD if not bad else B.BAD)
    im.save(out)
    return {n: (res[i][0]["total"], res[k + i][0]["total"], sorted(set(res[k + i][1]) | set(res[2 * k + i][1]))) for i, n in enumerate(names)}


def sheet_rows(b, names, cur, new, small, res, out):
    import board as B
    from PIL import Image, ImageDraw
    k = len(names)
    per = 7
    rows = (k + per - 1) // per
    cw, pad, rh = 200, 20, 470
    W, H = pad + per * (cw + pad), 50 + rows * rh
    im = Image.new("RGB", (W, H), B.BG)
    dr = ImageDraw.Draw(im)
    dr.text((pad, 10), f"Type A2, batch {b}: current (top) vs A2 (bottom), score, craft", font=B.font(20, True), fill=B.INK)
    out_t = {}
    for i, n in enumerate(names):
        x = pad + (i % per) * (cw + pad)
        y0 = 50 + (i // per) * rh
        (sa, _), (sb, fb), (_, fs) = res[i], res[k + i], res[2 * k + i]
        for row, (p, sc) in enumerate(((cur[i], sa), (new[i], sb))):
            y = y0 + row * 190
            ic = B.raster(p, 150, 150)
            im.paste(ic, (x + 10, y), ic)
            col = B.INK if row == 0 else (B.GOOD if sb["total"] > sa["total"] else B.BAD)
            dr.text((x + 10, y + 156), f"{n[:20]}  {sc['total']:.1f}", font=B.font(13, True), fill=col)
        for j, sz in enumerate((16, 32)):
            t = B.raster(small[i], sz, sz)
            im.paste(t, (x + 10 + j * 50, y0 + 390 + (32 - sz) // 2), t)
        bad = sorted(set(fb) | set(fs))
        dr.text((x + 110, y0 + 398), "craft ok" if not bad else "FAIL " + ",".join(bad), font=B.font(12, True), fill=B.GOOD if not bad else B.BAD)
        out_t[n] = (sa["total"], sb["total"], bad)
    im.save(out)
    return out_t


def main(argv):
    from par import fanout
    b = int(argv[0])
    fanout(_job, [(b, i, sm) for i in range(len(BATCHES[b])) for sm in (False, True)])
    if "--sheet" in argv:
        r = sheet(b, argv[argv.index("--sheet") + 1])
        for n, (a, e, bad) in r.items():
            print(f"{n:16s} {a:5.1f} -> {e:5.1f}  craft {'pass' if not bad else bad}")


if __name__ == "__main__":
    main(sys.argv[1:])
