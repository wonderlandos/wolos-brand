# SPDX-License-Identifier: GPL-2.0-or-later
"""Three icon directions derived from the brand calculus (docs/adr/brand-calculus.md section 8).

  python3 -I design/tools/brand/directions.py [outdir]     (default design/brand/directions)

Canvas 1024 = 24 fen; the art box is the zucai, 21 fen, 1.5 fen in from every edge. Every shape
is placed in fen; every icon returns its art and its construction (grid, named lines, light,
qi path, the shape's own construction), so the sheet can show how it was made.

  1 wuxing  Five shapes: the silhouette is the app's element shape (metal round, wood upright,
            water curved, fire pointed, earth square); colour = that element, derived from the base.
  2 strata  Layered ramie patches (Korean jogakbo): translucent rectangles of named fen sizes,
            stacked along the qi path from the upper-left entry to the landing patch.
  3 gate    The wall and the opening: a battered wall on a plinth (Yingzao shoufen), the meaning
            cut through it as an opening of light, the light falling through it onto the plinth.
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
F = S / 24.0
O = 1.5 * F
PAL = {k: v[0] for k, v in K.brand_palette().items()}
L0, C0, H0 = oklch(K.BASE)
HUE = {e: K.hue_of(e) for e in ("fire", "earth", "wood", "water")}
COL = {
    "metal": from_oklch(0.90, C0 * 1.0 / 21, H0),
    "earth": from_oklch(K.ladder(L0, 9), C0 * 15 / 21, HUE["earth"]),
    "wood": from_oklch(K.ladder(L0, 0), C0 * 13 / 21, HUE["wood"]),
    "water": from_oklch(K.ladder(L0, -3), C0 * 14 / 21, HUE["water"]),
    "ink": from_oklch(K.ladder(L0, -12), C0 * 4 / 21, H0),
    "fire": from_oklch(K.ladder(L0, 0), C0 * 15 / 21, HUE["fire"]),
    "violet": PAL["accent"],
    "gold": from_oklch(K.ladder(L0, 13), C0 * 15 / 21, HUE["earth"]),
    "jade": from_oklch(0.82, 0.13, HUE["wood"]),
    "paper": from_oklch(0.975, C0 * 0.8 / 21, H0),
    "light": from_oklch(0.97, C0 * 2 / 21, HUE["earth"]),
}


def g(x):
    """fen (0..21 inside the art box) -> px."""
    return O + x * F


def P(*pts):
    return [(g(x), g(y)) for x, y in pts]


def poly(pts, close=True):
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + ("Z" if close else "")


class Icon:
    def __init__(self, title):
        self.doc = Doc(S, S, title)
        self.cons = []          # construction snippets (px)
        self.qi = []            # qi path points (fen)

    def con_circle(self, cx, cy, r, label=None):
        self.cons.append(f'<circle cx="{f(g(cx))}" cy="{f(g(cy))}" r="{f(r * F)}" fill="none" stroke="#E0457B" stroke-width="2" stroke-dasharray="8 6"/>')
        if label:
            self.cons.append(f'<text x="{f(g(cx) + r * F * 0.72)}" y="{f(g(cy) - r * F * 0.72)}" font-family="Inter" font-size="26" fill="#E0457B">{label}</text>')

    def con_line(self, pts, label=None, dots=False):
        self.cons.append(f'<path d="{poly(P(*pts), False)}" fill="none" stroke="#E0457B" stroke-width="2.5"/>')
        if dots:
            for x, y in pts:
                self.cons.append(f'<circle cx="{f(g(x))}" cy="{f(g(y))}" r="6" fill="#E0457B"/>')
        if label:
            x, y = pts[-1]
            self.cons.append(f'<text x="{f(g(x) + 8)}" y="{f(g(y) - 8)}" font-family="Inter" font-size="26" fill="#E0457B">{label}</text>')

    def con_box(self, x, y, w, h, label=None):
        self.cons.append(f'<rect x="{f(g(x))}" y="{f(g(y))}" width="{f(w * F)}" height="{f(h * F)}" fill="none" stroke="#2F7DE1" stroke-width="2.5"/>')
        if label:
            self.cons.append(f'<text x="{f(g(x) + 6)}" y="{f(g(y) - 8)}" font-family="Inter" font-size="26" fill="#2F7DE1">{label}</text>')

    def svg(self):
        return self.doc.svg()

    def construction(self):
        """The art at 35 % under the grid, the named lines, the light vector, the qi path."""
        art = self.doc.svg(lic=False)
        inner = art[art.index("<defs>"):art.rindex("</svg>")]
        grid = []
        for i in range(25):
            x = i * F
            named = (i - 1.5) in (0, 3, 6, 10.5, 15, 18, 21) if False else None
            grid.append(f'<path d="M{f(x)} 0V{S}M0 {f(x)}H{S}" stroke="#9AA0B5" stroke-width="1" opacity="0.35"/>')
        for n in (0, 3, 6, 10.5, 15, 18, 21):
            grid.append(f'<path d="M{f(g(n))} {f(O)}V{f(g(21))}M{f(O)} {f(g(n))}H{f(g(21))}" stroke="#2F7DE1" stroke-width="1.6" opacity="0.6"/>')
        grid.append(f'<rect x="{f(O)}" y="{f(O)}" width="{f(21 * F)}" height="{f(21 * F)}" fill="none" stroke="#2F7DE1" stroke-width="3"/>')
        lx, ly = K.LIGHT
        grid.append(f'<path d="M{f(O - 10)} {f(O - 10)}l{f(-lx * 120)} {f(-ly * 120)}" stroke="#E0A21F" stroke-width="5" opacity="0"/>')
        grid.append(f'<path d="M{f(O + 10)} {f(O + 10)}L{f(O + 10 - lx * 0 + 70)} {f(O + 10 + 140)}" stroke="#E0A21F" stroke-width="6" marker-end="url(#ar)"/>')
        grid.append(f'<text x="{f(O + 40)}" y="{f(O + 60)}" font-family="Inter" font-size="26" fill="#C58A00">light 1:2</text>')
        qi = ""
        if self.qi:
            pts = P(*self.qi)
            qi = (f'<path d="M{f(pts[0][0])} {f(pts[0][1])}{smooth(pts)}" fill="none" stroke="#1F984B" stroke-width="7" '
                  f'stroke-dasharray="18 10" marker-end="url(#aq)"/>'
                  f'<circle cx="{f(pts[0][0])}" cy="{f(pts[0][1])}" r="14" fill="#1F984B"/>')
        markers = ('<defs><marker id="ar" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5" orient="auto">'
                   '<path d="M0 0L10 5L0 10Z" fill="#E0A21F"/></marker>'
                   '<marker id="aq" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
                   '<path d="M0 0L10 5L0 10Z" fill="#1F984B"/></marker></defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}" width="{S}" height="{S}">{markers}'
                f'<rect width="{S}" height="{S}" fill="#FFFFFF"/><g opacity="0.38">{inner}</g>'
                f'{"".join(grid)}{"".join(self.cons)}{qi}</svg>\n')


def solid(ic, d, colour, spread=3, lift=1.0, gloss=0.45, shadow=True):
    doc = ic.doc
    if shadow:
        doc.shadow(d, shade(colour, -16), F, opacity=0.30, lift=lift)
    doc.add(f'<path d="{d}" fill="{doc.lit(colour, spread)}"/>')
    if gloss:
        doc.add(f'<path d="{d}" fill="{doc.rim(gloss)}"/>')


def gear_path(cx, cy, ro, rr, teeth=8, tip=0.42, root=0.78):
    pts = []
    for i in range(teeth):
        a0 = i / teeth * 2 * math.pi - math.pi / 2
        ht, hr = math.pi / teeth * tip, math.pi / teeth * root
        for a, r in ((a0 - hr, rr), (a0 - ht, ro), (a0 + ht, ro), (a0 + hr, rr)):
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d = f"M{f(pts[0][0])} {f(pts[0][1])}"
    for i in range(1, len(pts) + 1):
        x, y = pts[i % len(pts)]
        kind = i % 4
        if kind == 2:   # along the tip
            d += f"A{f(ro)} {f(ro)} 0 0 1 {f(x)} {f(y)}"
        elif kind == 0:  # along the root
            d += f"A{f(rr)} {f(rr)} 0 0 1 {f(x)} {f(y)}"
        else:
            d += f"L{f(x)} {f(y)}"
    return d + "Z"


def keyhole(cx, top, w):
    r = w / 2
    cy = top + r
    return (circle(cx, cy, r) + f"M{f(cx - r * 0.42)} {f(cy + r * 0.25)}L{f(cx + r * 0.42)} {f(cy + r * 0.25)}"
            f"L{f(cx + r * 0.7)} {f(cy + r * 2.5)}L{f(cx - r * 0.7)} {f(cy + r * 2.5)}Z")


def heart(cx, top, w, h):
    lr = w / 4
    ly = top + lr
    return (f"M{f(cx)} {f(ly - lr * 0.15)}"
            f"C{f(cx)} {f(top - lr * 0.15)} {f(cx - 2 * lr)} {f(top - lr * 0.15)} {f(cx - 2 * lr)} {f(ly + lr * 0.25)}"
            f"C{f(cx - 2 * lr)} {f(ly + 2.1 * lr)} {f(cx - 0.6 * lr)} {f(top + h - 0.9 * lr)} {f(cx)} {f(top + h)}"
            f"C{f(cx + 0.6 * lr)} {f(top + h - 0.9 * lr)} {f(cx + 2 * lr)} {f(ly + 2.1 * lr)} {f(cx + 2 * lr)} {f(ly + lr * 0.25)}"
            f"C{f(cx + 2 * lr)} {f(top - lr * 0.15)} {f(cx)} {f(top - lr * 0.15)} {f(cx)} {f(ly - lr * 0.15)}Z")


def ribbon(pts, th):
    """A filled polyline of width th (px) with square-ish joins and round ends."""
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy) or 1
        nx, ny = -dy / n * th / 2, dx / n * th / 2
        left.append((x + nx, y + ny)); right.append((x - nx, y - ny))
    d = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in left)
    d += f"A{f(th / 2)} {f(th / 2)} 0 0 0 {f(right[-1][0])} {f(right[-1][1])}"
    d += "L" + "L".join(f"{f(x)} {f(y)}" for x, y in reversed(right))
    d += f"A{f(th / 2)} {f(th / 2)} 0 0 0 {f(left[0][0])} {f(left[0][1])}Z"
    return d


def wave_top(x0, x1, y_base, amp, crest_at=0.35):
    """A water edge: rises from the left on a juzhe curve to a crest, falls on a juzhe curve."""
    xc = x0 + (x1 - x0) * crest_at
    up = juzhe(xc, y_base - amp, x0, y_base, purlins=4, first=0.12)[::-1]
    down = juzhe(xc, y_base - amp, x1, y_base, purlins=4, first=0.12)
    return up + down[1:]


# =============================================================== 1 wuxing
def w_settings():
    ic = Icon("settings, wuxing: metal is round")
    cx = cy = 10.5
    disc = circle(g(cx), g(cy), 10.5 * F)
    solid(ic, disc, COL["metal"], spread=5, lift=1.3, gloss=0.6)
    # the gear is relief on the coin (raised, lit like the coin): 8 teeth for the eight directions
    gp = gear_path(g(cx), g(cy), 7.5 * F, 6.0 * F)
    solid(ic, gp, shade(COL["metal"], 2), spread=4, lift=0.45, gloss=0.5)
    # the keyhole face: base violet (water; metal feeds water)
    solid(ic, circle(g(cx), g(cy), 3.6 * F), COL["violet"], spread=3, lift=0.4, gloss=0.4)
    ic.doc.add(f'<path d="{keyhole(g(cx), g(cy) - 2.1 * F, 1.8 * F)}" fill="{COL["paper"]}"/>')
    ic.con_circle(cx, cy, 10.5, "21")
    ic.con_circle(cx, cy, 7.5, "15")
    ic.con_circle(cx, cy, 6.0, "12")
    ic.con_circle(cx, cy, 3.6)
    for i in range(8):
        a = i / 8 * 2 * math.pi - math.pi / 2
        ic.con_line([(cx, cy), (cx + 10.5 * math.cos(a), cy + 10.5 * math.sin(a))])
    ic.qi = [(3.2, 3.6), (6.0, 2.6), (8.8, 6.0), (10.5, 9.4)]
    return ic


def w_store():
    ic = Icon("store, wuxing: earth is square")
    # earth square 21 x 18 (from y 3), radius 2 fen; the handle is die-cut through it
    body = rrect(g(0), g(3), 21 * F, 18 * F, 2.4 * F)
    hole = rrect(g(6.0), g(5.2), 9.0 * F, 2.4 * F, 1.2 * F)     # the die-cut handle slot, 9 x 2.4
    d = body + hole
    ic.doc.shadow(body, shade(COL["earth"], -16), F, opacity=0.3, lift=1.3)
    ic.doc.add(f'<path d="{d}" fill-rule="evenodd" fill="{ic.doc.lit(COL["earth"], 4)}"/>')
    ic.doc.add(f'<path d="{d}" fill-rule="evenodd" fill="{ic.doc.rim(0.5)}"/>')
    # the seam where the bag folds (wood? no: a deeper earth line, the gusset on the shadow side)
    ic.doc.add(f'<path d="{rrect(g(17.4), g(3), 3.6 * F, 18 * F, 0, 2.4 * F, 2.4 * F, 0)}" fill="{shade(COL["earth"], -3)}" opacity="0.6"/>')
    # keyhole seal (water violet on earth: ke, kept under 1/7)
    solid(ic, circle(g(10.5), g(14.6), 3.0 * F), COL["violet"], spread=3, lift=0.4, gloss=0.4)
    ic.doc.add(f'<path d="{keyhole(g(10.5), g(14.6) - 1.8 * F, 1.5 * F)}" fill="{COL["paper"]}"/>')
    ic.con_box(0, 3, 21, 18, "21 x 18")
    ic.con_box(6.0, 5.2, 9.0, 2.4, "slot 9")
    ic.con_circle(10.5, 14.6, 3.0)
    ic.con_line([(17.4, 3), (17.4, 21)], "gusset")
    ic.qi = [(1.6, 4.4), (6.0, 6.4), (15.0, 6.4), (10.5, 13.4)]
    return ic


def w_files():
    ic = Icon("files, wuxing: wood is upright (a folder standing)")
    # back leaf 15 x 21 with the tab at the upper left (the entry); paper rises out of it; front leaf
    x0, w = 3.0, 15.0
    tab = juzhe(g(x0 + 6.0), g(0.0), g(x0 + 8.0), g(1.6), purlins=3, first=0.15)
    back = (f"M{f(g(x0))} {f(g(1.0))}Q{f(g(x0))} {f(g(0))} {f(g(x0 + 1.0))} {f(g(0))}H{f(g(x0 + 6.0))}" + smooth(tab) +
            f"H{f(g(x0 + w - 1.0))}Q{f(g(x0 + w))} {f(g(1.6))} {f(g(x0 + w))} {f(g(2.6))}V{f(g(21))}H{f(g(x0))}Z")
    solid(ic, back, shade(COL["wood"], -3), spread=2, lift=0.9, gloss=0.25)
    solid(ic, rrect(g(x0 + 1.2), g(2.6), (w - 2.4) * F, 10 * F, 0.6 * F), COL["paper"], spread=1, lift=0.4, gloss=0.0)
    for j, (wl, yl) in enumerate(((10, 4.4), (6, 6.4))):     # rhythm 10 : 6
        ic.doc.add(f'<path d="{rrect(g(x0 + 2.4), g(yl), wl * F, 0.8 * F, 0.4 * F)}" fill="{COL["wood"]}" opacity="0.5"/>')
    edge = juzhe(g(x0 - 0.3), g(8.6), g(x0 + w + 0.3), g(7.6), purlins=4, first=0.2)
    front = (f"M{f(edge[0][0])} {f(edge[0][1])}" + smooth(edge) +
             f"L{f(g(x0 + w))} {f(g(19.8))}Q{f(g(x0 + w))} {f(g(21))} {f(g(x0 + w - 1.2))} {f(g(21))}H{f(g(x0 + 1.2))}Q{f(g(x0))} {f(g(21))} {f(g(x0))} {f(g(19.8))}Z")
    solid(ic, front, COL["wood"], spread=4, lift=1.2, gloss=0.5)
    solid(ic, rrect(g(x0 + 2.2), g(10.6), 4.0 * F, 2.0 * F, 0.6 * F), COL["gold"], spread=2, lift=0.3, gloss=0.3)
    ic.con_box(x0, 0, w, 21, "15 x 21 (5:7)")
    ic.con_line([(x0 - 0.3, 8.6), (x0 + w + 0.3, 7.6)], "juzhe lip")
    ic.qi = [(4.5, 0.8), (7.0, 4.4), (12.0, 6.4), (5.2, 11.6)]
    return ic


def w_console():
    ic = Icon("console, wuxing: water is curved")
    top = wave_top(g(0), g(21), g(5.0), 2.0 * F, crest_at=0.3)
    r = 2.4 * F
    d = (f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) +
         f"V{f(g(19.5) - r)}Q{f(g(21))} {f(g(19.5))} {f(g(21) - r)} {f(g(19.5))}H{f(g(0) + r)}Q{f(g(0))} {f(g(19.5))} {f(g(0))} {f(g(19.5) - r)}Z")
    solid(ic, d, COL["ink"], spread=3, lift=1.3, gloss=0.25)
    # the prompt chevron: arms are juzhe slopes; water feeds wood (jade)
    cx, cy, a, th = 3.6, 11.6, 3.0, 1.3
    up = juzhe(g(cx), g(cy - a), g(cx + a * 1.1), g(cy), purlins=3, first=0.12)
    dn = juzhe(g(cx + a * 1.1), g(cy), g(cx), g(cy + a), purlins=3, first=0.12)
    inner = [(x - th * F * 0.9, y) for x, y in reversed(up + dn[1:])]
    ch = f"M{f(up[0][0])} {f(up[0][1])}" + smooth(up) + smooth(dn) + "L" + "L".join(f"{f(x)} {f(y)}" for x, y in inner) + "Z"
    solid(ic, ch, COL["jade"], spread=3, lift=0.4, gloss=0.35)
    solid(ic, rrect(g(10.5), g(13.2), 6.0 * F, 1.8 * F, 0.6 * F), COL["jade"], spread=3, lift=0.4, gloss=0.35)
    ic.con_line([(0, 5), (6.3, 3.0), (21, 5)], "crest", dots=True)
    ic.con_box(0, 3, 21, 16.5, "21 x 16.5")
    ic.con_line([(cx, cy - a), (cx + a * 1.1, cy), (cx, cy + a)], "chevron 6")
    ic.qi = [(1.5, 6.0), (4.0, 9.0), (7.0, 11.6), (13.5, 14.1)]
    return ic


def w_doctor():
    ic = Icon("doctor, wuxing: fire is pointed (the heart belongs to fire)")
    d = heart(g(10.5), g(0.6), 21 * F, 20.0 * F)
    solid(ic, d, COL["fire"], spread=4, lift=1.3, gloss=0.5)
    y = 9.8
    pts = P((3.4, y), (7.0, y), (8.6, y - 3.2), (10.6, y + 3.6), (12.4, y - 1.4), (13.8, y), (16.0, y))
    ic.doc.add(f'<path d="{ribbon(pts, 1.25 * F)}" fill="{COL["gold"]}"/>')
    solid(ic, circle(g(17.2), g(y), 1.15 * F), COL["gold"], spread=2, lift=0.3, gloss=0.4)
    ic.con_box(0, 0.6, 21, 20, "21 x 20")
    ic.con_circle(5.25, 5.85, 5.25)
    ic.con_circle(15.75, 5.85, 5.25)
    ic.qi = [(3.0, 3.6), (5.0, 8.0), (8.6, 7.0), (10.6, 13.0), (17.2, 9.8)]
    return ic


def w_atlas():
    ic = Icon("atlas, wuxing: water is curved (the folds are a wave)")
    xs = [0, 5.25, 10.5, 15.75, 21]
    tops = [4.5, 2.5, 4.5, 2.5, 4.5]
    bots = [19.0, 17.0, 19.0, 17.0, 19.0]
    # each panel's value follows its facing: a face turned to the upper-left light is lighter
    for i in range(4):
        pts = P((xs[i], tops[i]), (xs[i + 1], tops[i + 1]), (xs[i + 1], bots[i + 1]), (xs[i], bots[i]))
        rising = tops[i + 1] < tops[i]
        c = shade(COL["water"], 6 if rising else -2)
        if i == 0:
            outline = P((0, 4.5), (5.25, 2.5), (10.5, 4.5), (15.75, 2.5), (21, 4.5), (21, 19), (15.75, 17), (10.5, 19), (5.25, 17), (0, 19))
            ic.doc.shadow(poly(outline), shade(COL["water"], -16), F, opacity=0.3, lift=1.2)
        ic.doc.add(f'<path d="{poly(pts)}" fill="{ic.doc.lit(c, 2)}"/>')
    # trail: gold, a turning path from the entry to the you-are-here
    trail = [(2.2, 6.6), (4.6, 8.2), (5.6, 10.8), (8.6, 12.4), (12.0, 12.0), (14.4, 10.4)]
    for k, (x, y) in enumerate(trail):
        ic.doc.add(f'<path d="{circle(g(x), g(y), (0.55 + 0.05 * k) * F)}" fill="{COL["gold"]}" opacity="{0.6 + 0.06 * k:.2f}"/>')
    solid(ic, circle(g(16.6), g(9.4), 1.9 * F), COL["gold"], spread=3, lift=0.4, gloss=0.6)
    ic.doc.add(f'<path d="{circle(g(16.6), g(9.4), 0.7 * F)}" fill="#FFFFFF"/>')
    ic.con_line([(0, 4.5), (5.25, 2.5), (10.5, 4.5), (15.75, 2.5), (21, 4.5)], "wave of folds", dots=True)
    ic.con_box(0, 2.5, 21, 16.5)
    ic.qi = trail + [(16.6, 9.4)]
    return ic


# =============================================================== 2 strata
def patch(ic, x, y, w, h, colour, op=0.82, r=1.0, seam=True, lift=0.6):
    d = rrect(g(x), g(y), w * F, h * F, r * F)
    ic.doc.shadow(d, shade(colour, -18), F, opacity=0.22, lift=lift)
    ic.doc.add(f'<path d="{d}" fill="{ic.doc.lit(colour, 3)}" opacity="{op}"/>')
    if seam:
        ic.doc.add(f'<path d="{d}" fill="none" stroke="{ic.doc.rim(0.9)}" stroke-width="{f(0.22 * F)}"/>')
    ic.con_box(x, y, w, h, f"{w:g}x{h:g}" if w * h > 40 else None)
    return d


def s_settings():
    ic = Icon("settings, strata: three sliders")
    rows = [(3.0, 21.0, 4.8), (9.0, 21.0, 10.5), (15.0, 21.0, 16.2)]
    for i, (y, w, knob) in enumerate(rows):
        patch(ic, 0, y, w, 3.0, COL["metal"], op=0.95, r=1.5, lift=0.4)
        patch(ic, 0, y, knob, 3.0, COL["violet"] if i == 2 else shade(COL["violet"], 8), op=0.55 + 0.15 * i, r=1.5, seam=False, lift=0.0)
        solid(ic, circle(g(knob), g(y + 1.5), (2.1 + 0.4 * i) * F), COL["violet"] if i == 2 else COL["paper"], spread=3, lift=0.6, gloss=0.5)
    ic.qi = [(4.8, 4.5), (10.5, 10.5), (16.2, 16.5)]
    return ic


def s_store():
    ic = Icon("store, strata: the bag of three patches")
    patch(ic, 5.0, 1.5, 3.0, 9.0, COL["fire"], op=0.85, r=1.5)
    patch(ic, 13.0, 1.5, 3.0, 9.0, COL["fire"], op=0.85, r=1.5)
    patch(ic, 5.0, 1.5, 11.0, 3.0, COL["fire"], op=0.85, r=1.5, seam=False)
    patch(ic, 0.0, 6.0, 21.0, 15.0, COL["earth"], op=0.88, r=1.5)
    patch(ic, 15.0, 6.0, 6.0, 15.0, shade(COL["earth"], -4), op=0.5, r=1.5, seam=False, lift=0)
    solid(ic, circle(g(9.0), g(14.0), 3.0 * F), COL["violet"], spread=3, lift=0.4, gloss=0.4)
    ic.doc.add(f'<path d="{keyhole(g(9.0), g(14.0) - 1.8 * F, 1.5 * F)}" fill="{COL["paper"]}"/>')
    ic.qi = [(6.5, 2.5), (10.5, 3.0), (14.5, 6.5), (9.0, 14.0)]
    return ic


def s_files():
    ic = Icon("files, strata: sheets stepping toward the light")
    patch(ic, 0.0, 0.0, 15.0, 16.0, COL["wood"], op=0.55, r=1.2)
    patch(ic, 3.0, 2.5, 15.0, 16.0, COL["wood"], op=0.7, r=1.2)
    patch(ic, 6.0, 5.0, 15.0, 16.0, COL["paper"], op=0.96, r=1.2, lift=1.0)
    for j, (wl, yl) in enumerate(((10, 10.0), (6, 12.6), (10, 15.2), (6, 17.8))):
        ic.doc.add(f'<path d="{rrect(g(8.5), g(yl), wl * F, 0.9 * F, 0.45 * F)}" fill="{COL["wood"]}" opacity="0.55"/>')
    solid(ic, rrect(g(8.5), g(6.8), 4.0 * F, 2.0 * F, 0.6 * F), COL["gold"], spread=2, lift=0.3, gloss=0.3)
    ic.qi = [(1.5, 1.5), (4.5, 4.0), (7.5, 6.5), (10.5, 7.8), (14.0, 13.0)]
    return ic


def s_console():
    ic = Icon("console, strata: the screen over its shadow plane")
    patch(ic, 3.0, 4.5, 18.0, 15.0, COL["violet"], op=0.45, r=1.5)
    patch(ic, 0.0, 1.5, 18.0, 15.0, COL["ink"], op=0.94, r=1.5, lift=1.0)
    ch = ribbon(P((3.0, 5.8), (6.4, 9.0), (3.0, 12.2)), 1.3 * F)
    solid(ic, ch, COL["jade"], spread=3, lift=0.3, gloss=0.3)
    patch(ic, 8.0, 10.6, 6.0, 2.0, COL["jade"], op=1.0, r=0.6, seam=False, lift=0.3)
    ic.qi = [(1.5, 3.0), (3.0, 5.8), (6.4, 9.0), (11.0, 11.6)]
    return ic


def s_doctor():
    ic = Icon("doctor, strata: two patches crossing, the heart at the crossing")
    patch(ic, 0.0, 7.0, 21.0, 7.0, COL["wood"], op=0.75, r=1.5)
    patch(ic, 7.0, 0.0, 7.0, 21.0, COL["wood"], op=0.75, r=1.5)
    solid(ic, heart(g(10.5), g(8.2), 5.0 * F, 4.8 * F), COL["fire"], spread=3, lift=0.4, gloss=0.5)
    ic.qi = [(8.5, 1.5), (10.5, 6.0), (10.5, 10.5)]
    return ic


def s_atlas():
    ic = Icon("atlas, strata: four panels offset like a fold")
    for i in range(4):
        y = 1.5 if i % 2 else 3.0
        patch(ic, i * 5.25, y, 5.25, 16.5, COL["water"], op=0.62 + 0.1 * (i % 2), r=0.8, lift=0.5)
    trail = [(2.4, 6.0), (4.6, 8.0), (6.0, 10.6), (8.8, 12.2), (12.2, 11.8)]
    for k, (x, y) in enumerate(trail):
        ic.doc.add(f'<path d="{circle(g(x), g(y), (0.55 + 0.05 * k) * F)}" fill="{COL["gold"]}" opacity="{0.65 + 0.06 * k:.2f}"/>')
    solid(ic, circle(g(15.0), g(10.0), 2.0 * F), COL["gold"], spread=3, lift=0.4, gloss=0.6)
    ic.doc.add(f'<path d="{circle(g(15.0), g(10.0), 0.7 * F)}" fill="#FFFFFF"/>')
    ic.qi = trail + [(15.0, 10.0)]
    return ic


# =============================================================== 3 gate
def wall(ic, colour):
    """The battered wall on its plinth: base 21, top 18 (shoufen, 1.5 fen in on each side over
    the height), a juzhe roof cap with flared eaves, plinth 21 x 2.5 of light stone."""
    ridge, eave = 0.0, 2.2
    left = juzhe(g(10.5), g(ridge), g(0.6), g(eave), purlins=4, first=0.1)[::-1]
    right = juzhe(g(10.5), g(ridge), g(20.4), g(eave), purlins=4, first=0.1)
    roof = left + right[1:]
    body = (f"M{f(g(0))} {f(g(eave + 0.3))}" + "".join(f"L{f(x)} {f(y)}" for x, y in [roof[0]]) + smooth(roof) +
            f"L{f(g(21))} {f(g(eave + 0.3))}L{f(g(19.5))} {f(g(eave + 1.2))}L{f(g(21))} {f(g(18.5))}H{f(g(0))}L{f(g(1.5))} {f(g(eave + 1.2))}Z")
    ic.doc.shadow(body, shade(colour, -16), F, opacity=0.3, lift=1.2)
    ic.doc.add(f'<path d="{body}" fill="{ic.doc.lit(colour, 3)}"/>')
    ic.doc.add(f'<path d="{body}" fill="{ic.doc.rim(0.35)}"/>')
    plinth = rrect(g(0), g(18.5), 21 * F, 2.5 * F, 0.5 * F)
    ic.doc.add(f'<path d="{plinth}" fill="{ic.doc.lit(COL["metal"], 2)}"/>')
    ic.con_line([(0.6, eave), (10.5, ridge), (20.4, eave)], "juzhe cap", dots=True)
    ic.con_line([(1.5, 3.4), (0, 18.5)], "shoufen")
    ic.con_line([(19.5, 3.4), (21, 18.5)])
    ic.con_box(0, 18.5, 21, 2.5, "plinth")
    return body


def opening(ic, d, shift=(1.0, 2.0)):
    """Light through the opening: the opening glows, and its light falls on the plinth down-right."""
    i = ic.doc.id("o")
    ic.doc.defs.append(f'<linearGradient id="{i}" x1="0.25" y1="0" x2="0.75" y2="1"><stop offset="0" stop-color="#FFFFFF"/>'
                       f'<stop offset="1" stop-color="{COL["light"]}"/></linearGradient>')
    # inner shadow on the lit side (the reveal of a hole is dark at the upper left)
    ic.doc.add(f'<path d="{d}" fill="{shade(COL["light"], -6)}"/>')
    ic.doc.add(f'<path d="{d}" transform="translate({f(0.35 * F)} {f(0.7 * F)})" fill="url(#{i})"/>')
    cid = ic.doc.id("c")
    ic.doc.defs.append(f'<clipPath id="{cid}"><rect x="{f(g(0))}" y="{f(g(18.5))}" width="{f(21 * F)}" height="{f(2.5 * F)}"/></clipPath>')



def gate_settings():
    ic = Icon("settings, gate: a gear of light")
    wall(ic, from_oklch(K.ladder(L0, -6), C0 * 9 / 21, H0))
    d = gear_path(g(10.5), g(10.2), 6.4 * F, 5.1 * F) + circle(g(10.5), g(10.2), 2.4 * F)
    opening(ic, d)
    ic.doc.add(f'<path d="{keyhole(g(10.5), g(10.2) - 1.3 * F, 1.2 * F)}" fill="{COL["light"]}"/>')
    ic.con_circle(10.5, 10.2, 6.4)
    ic.con_circle(10.5, 10.2, 2.4)
    ic.qi = [(2.0, 3.0), (6.0, 5.4), (10.5, 10.2)]
    return ic


def gate_store():
    ic = Icon("store, gate: a bag of light")
    wall(ic, from_oklch(K.ladder(L0, 4), C0 * 14 / 21, HUE["earth"]))
    body = poly(P((5.6, 8.6), (15.4, 8.6), (16.4, 16.4), (4.6, 16.4)))
    handle = ribbon([(g(8.0), g(8.8))] + [(g(10.5) - 2.5 * F * math.cos(t / 10 * math.pi), g(8.0) - 3.0 * F * math.sin(t / 10 * math.pi)) for t in range(1, 10)] + [(g(13.0), g(8.8))], 0.7 * F)
    d = body + handle
    opening(ic, d)
    ic.doc.add(f'<path d="{keyhole(g(10.5), g(10.6), 1.6 * F)}" fill="{COL["violet"]}"/>')
    ic.con_box(4.6, 8.6, 11.8, 7.8, "trapezoid")
    ic.qi = [(2.0, 3.0), (7.3, 6.0), (10.5, 4.6), (10.5, 11.8)]
    return ic


def gate_files():
    ic = Icon("files, gate: a folder of light")
    wall(ic, from_oklch(K.ladder(L0, -3), C0 * 12 / 21, HUE["wood"]))
    tab = juzhe(g(9.5), g(6.5), g(11.3), g(7.8), purlins=3, first=0.15)
    d = (f"M{f(g(4.0))} {f(g(7.3))}Q{f(g(4.0))} {f(g(6.5))} {f(g(4.8))} {f(g(6.5))}H{f(g(9.5))}" + smooth(tab) +
         f"H{f(g(16.2))}Q{f(g(17.0))} {f(g(7.8))} {f(g(17.0))} {f(g(8.6))}V{f(g(15.2))}Q{f(g(17.0))} {f(g(16.0))} {f(g(16.2))} {f(g(16.0))}"
         f"H{f(g(4.8))}Q{f(g(4.0))} {f(g(16.0))} {f(g(4.0))} {f(g(15.2))}Z")
    opening(ic, d)
    ic.doc.add(f'<path d="{rrect(g(5.4), g(10.0), 10.2 * F, 0.5 * F, 0.25 * F)}" fill="{shade(COL["light"], -10)}" opacity="0.6"/>')
    ic.con_box(4, 6.5, 13, 9.5, "13 x 9.5")
    ic.qi = [(2.0, 3.0), (5.0, 6.5), (10.5, 8.0), (10.5, 12.0)]
    return ic


def gate_console():
    ic = Icon("console, gate: the prompt of light")
    wall(ic, COL["ink"])
    d = ribbon(P((4.4, 6.8), (8.6, 10.4), (4.4, 14.0)), 1.6 * F) + rrect(g(10.4), g(13.0), 6.4 * F, 1.8 * F, 0.5 * F)
    opening(ic, d)
    ic.qi = [(2.0, 3.0), (4.4, 6.8), (8.6, 10.4), (13.6, 13.9)]
    return ic


def gate_doctor():
    ic = Icon("doctor, gate: a heart of light")
    wall(ic, COL["fire"])
    d = heart(g(10.5), g(5.0), 12 * F, 11.4 * F)
    opening(ic, d)
    y = 9.8
    pts = P((5.6, y), (8.0, y), (9.0, y - 2.0), (10.6, y + 2.4), (11.8, y - 0.8), (12.6, y), (15.4, y))
    ic.doc.add(f'<path d="{ribbon(pts, 0.9 * F)}" fill="{COL["fire"]}"/>')
    ic.qi = [(2.0, 3.0), (6.0, 6.0), (10.5, 12.0)]
    return ic


def gate_atlas():
    ic = Icon("atlas, gate: three windows folded like a map")
    wall(ic, COL["water"])
    xs, tops, bots = [4.0, 8.3, 12.7, 17.0], [7.6, 6.2, 7.6, 6.2], [16.4, 15.0, 16.4, 15.0]
    d = "".join(poly(P((xs[i] + 0.25, tops[i] + 0.2), (xs[i + 1] - 0.25, tops[i + 1] + 0.2), (xs[i + 1] - 0.25, bots[i + 1] - 0.2), (xs[i] + 0.25, bots[i] - 0.2))) for i in range(3))
    opening(ic, d)
    solid(ic, circle(g(13.6), g(11.0), 1.5 * F), COL["gold"], spread=3, lift=0.3, gloss=0.6)
    ic.qi = [(2.0, 3.0), (6.0, 8.6), (10.5, 12.0), (13.6, 11.0)]
    return ic


DIRECTIONS = {
    "1-wuxing": [("Settings", w_settings), ("Store", w_store), ("Files", w_files), ("Console", w_console), ("Doctor", w_doctor), ("Atlas Folio", w_atlas)],
    "2-strata": [("Settings", s_settings), ("Store", s_store), ("Files", s_files), ("Console", s_console), ("Doctor", s_doctor), ("Atlas Folio", s_atlas)],
    "3-gate": [("Settings", gate_settings), ("Store", gate_store), ("Files", gate_files), ("Console", gate_console), ("Doctor", gate_doctor), ("Atlas Folio", gate_atlas)],
}


def main(argv):
    out = argv[0] if argv else os.path.join(HERE, "..", "..", "brand", "directions")
    for dname, icons in DIRECTIONS.items():
        os.makedirs(os.path.join(out, dname, "construction"), exist_ok=True)
        for name, fn in icons:
            ic = fn()
            slug = name.lower().replace(" ", "-")
            open(os.path.join(out, dname, f"wolos-{slug}.svg"), "w").write(ic.svg())
            open(os.path.join(out, dname, "construction", f"wolos-{slug}.svg"), "w").write(ic.construction())
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main(sys.argv[1:])
