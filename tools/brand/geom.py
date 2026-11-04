# SPDX-License-Identifier: GPL-2.0-or-later
"""Brand geometry kit: the juzhe roof curve, the card, light-directed gradients and soft shadows,
written as SVG strings. Stdlib only."""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calculus as K  # noqa: E402
from colour import oklch, from_oklch  # noqa: E402


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def juzhe(x0, y0, x1, y1, purlins=4, first=0.1):
    """Yingzao fashi juzhe (raise and fold): a roof slope from the ridge (x0, y0) down to the eave
    (x1, y1). The rise H = |y1 - y0|. Purlins sit at equal horizontal steps; the first one below the
    ridge drops H*first (1/10) under the straight ridge-eave line, each next one drops half as much
    (1/20, 1/40, ...) under the line from the previous folded purlin to the eave. Returns the
    folded points ridge -> eave (a concave curve, steep at the ridge, flat at the eave)."""
    H = abs(y1 - y0)
    sgn = 1 if y1 > y0 else -1
    pts = [(x0, y0)]
    px, py = x0, y0
    drop = H * first
    for i in range(1, purlins):
        x = x0 + (x1 - x0) * i / purlins
        t = (x - px) / (x1 - px)
        y_line = py + (y1 - py) * t
        y = y_line + sgn * drop
        pts.append((x, y))
        px, py = x, y
        drop /= 2
    pts.append((x1, y1))
    return pts


def smooth(pts, closed=False):
    """Catmull-Rom through the points as cubic Beziers (path data after the first M)."""
    d = []
    n = len(pts)
    for i in range(n - 1 if not closed else n):
        p0 = pts[i - 1] if i > 0 or closed else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (i + 2 < n or closed) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}")
    return " ".join(d)


def rrect(x, y, w, h, r_tl, r_tr=None, r_br=None, r_bl=None, k=0.56):
    """Rounded rectangle with four radii, smooth corners (k = handle length / radius)."""
    r_tr = r_tl if r_tr is None else r_tr
    r_br = r_tl if r_br is None else r_br
    r_bl = r_tr if r_bl is None else r_bl
    c = 1 - k
    return (f"M{f(x + r_tl)} {f(y)}H{f(x + w - r_tr)}"
            f"C{f(x + w - r_tr * c)} {f(y)} {f(x + w)} {f(y + r_tr * c)} {f(x + w)} {f(y + r_tr)}"
            f"V{f(y + h - r_br)}"
            f"C{f(x + w)} {f(y + h - r_br * c)} {f(x + w - r_br * c)} {f(y + h)} {f(x + w - r_br)} {f(y + h)}"
            f"H{f(x + r_bl)}"
            f"C{f(x + r_bl * c)} {f(y + h)} {f(x)} {f(y + h - r_bl * c)} {f(x)} {f(y + h - r_bl)}"
            f"V{f(y + r_tl)}"
            f"C{f(x)} {f(y + r_tl * c)} {f(x + r_tl * c)} {f(y)} {f(x + r_tl)} {f(y)}Z")


def circle(cx, cy, r):
    return (f"M{f(cx - r)} {f(cy)}A{f(r)} {f(r)} 0 1 0 {f(cx + r)} {f(cy)}"
            f"A{f(r)} {f(r)} 0 1 0 {f(cx - r)} {f(cy)}Z")


def shade(hexc, fen):
    """Move a colour `fen` steps on its own value ruler (21 fen to white / to black)."""
    L, C, h = oklch(hexc)
    return from_oklch(K.ladder(L, fen), C * (1 - abs(fen) / 42), h)


class Doc:
    """An SVG under construction with unique ids."""

    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.defs, self.body, self.n = [], [], 0

    def id(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def lit(self, colour, spread=3, box=None):
        """Linear gradient along the light: lighter at the upper left, darker at the lower right
        (dx:dy = 1:2, the SHADOW vector). `spread` = fen up and down the value ruler."""
        i = self.id("g")
        a, b = shade(colour, spread), shade(colour, -spread)
        self.defs.append(f'<linearGradient id="{i}" x1="0.25" y1="0" x2="0.75" y2="1">'
                         f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>')
        return f"url(#{i})"

    def rim(self, opacity=0.55):
        """Gloss: white at the lit corner fading out by the middle."""
        i = self.id("r")
        self.defs.append(f'<linearGradient id="{i}" x1="0.25" y1="0" x2="0.75" y2="1">'
                         f'<stop offset="0" stop-color="#FFFFFF" stop-opacity="{opacity}"/>'
                         f'<stop offset="0.45" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>')
        return f"url(#{i})"

    def blur(self, std):
        i = self.id("b")
        self.defs.append(f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%">'
                         f'<feGaussianBlur stdDeviation="{f(std)}"/></filter>')
        return f"url(#{i})"

    def shadow(self, d, colour, unit, opacity=0.3, lift=1.0):
        """Soft shadow of path d, offset away from the light by `lift` x (0.25, 0.5) units."""
        dx, dy = K.SHADOW
        n = math.hypot(dx, dy)
        ox, oy = dx / n * unit * 0.55 * lift, dy / n * unit * 0.55 * lift
        self.body.append(f'<path d="{d}" transform="translate({f(ox)} {f(oy)})" fill="{colour}" '
                         f'opacity="{opacity}" filter="{self.blur(unit * 0.45 * lift)}"/>')

    def add(self, s):
        self.body.append(s)

    def svg(self, lic=True):
        L = ('<!-- SPDX-License-Identifier: LicenseRef-Wonderland-Brand-1.0. (c) 2026 Julia Klee. '
             'WolOS brand study (design/tools/brand). -->') if lic else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {f(self.w)} {f(self.h)}" '
                f'width="{f(self.w)}" height="{f(self.h)}"><title>{self.title}</title>{L}'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>\n')
