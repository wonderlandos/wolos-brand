# SPDX-License-Identifier: GPL-2.0-or-later
"""Pen: the stroke grammar of the WolOS UI symbolic set (docs/adr/brand-ui.md section 1).

Icons are authored once on the 24-fen master (centre 12, art box 21 fen = 1.5..22.5, the zucai) and
drawn at N = 24 or 16 px by a Pen.  The pen turns every stroke into a filled outline (GTK 4.20 draws
`stroke` symbolics as blobs), reusing the contour machinery of tools/icons.py (imported, not edited).

Grammar (derived from the A2 geometry, tools/brand/types.py a2_*):
  G1 stroke   2 fen at 24 px (A2 detail 1.4 fen x 21/15, the symbolic glyph is 1.4x the A2 glyph),
              1.5 px at 16 px; round caps and joins (A2: every end is th/2).
  G2 module   outer sizes on named fen (21, 15, 10, 6, 4, 3, 2), gaps one stroke wide (G1) or 3 fen.
  G3 corners  containers r = 3 fen (outer) from 12 fen wide, 2 fen below; height <= 6 fen: a pill.
  G4 juzhe    a slope that has a ridge and an eave (roof, folder tab, drop, shield) is a juzhe curve.
  G5 light    one light, upper left: openings and gaps face the lower right, the one solid mass (the
              landing) sits lower right of the figure.
  G6 leaf     a second leaf (inactive level, back panel) is the same glyph at opacity 0.35.
Hinting: 24 px lines snap to whole px (stroke 2 -> crisp both edges); 16 px lines snap to n+0.25 or
n+0.75 (stroke 1.5 -> one crisp edge); outer edges of boxes snap to whole px.
"""
import importlib.util
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BRAND = os.path.normpath(os.path.join(HERE, "..", "brand"))
sys.path.insert(0, BRAND)
_spec = importlib.util.spec_from_file_location("wol_old_icons", os.path.join(HERE, "..", "icons.py"))
OLD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(OLD)
import geom  # noqa: E402  (brand geometry: juzhe)


class Pen:
    def __init__(self, N, fit=1.0, shift=(0.0, 0.0)):
        assert N in (16, 24)
        self.N = N
        self.fit, self.sx, self.sy = fit, shift[0], shift[1]
        self.sw = 2.0 if N == 24 else 1.5
        self.s = 22 / 21 if N == 24 else 2 / 3            # fen -> px along a position
        self.k = 1.0 if N == 24 else 2 / 3                # fen -> px for a length
        self.c = N / 2

    # ---- hinting
    def pos(self, v, axis=0):
        return self.c + (v - 12) * self.s * self.fit + (self.sy if axis else self.sx)

    def q(self, v, axis=0):
        """a stroke centre-line coordinate, hinted (curve samples, off the half-fen grid, are not)"""
        x = self.pos(v, axis)
        if abs(v * 2 - round(v * 2)) > 1e-6:
            return x
        if self.N == 24:
            return float(round(x))
        n = math.floor(x)
        return n + 0.25 if x - n < 0.5 else n + 0.75

    def qo(self, v, axis=0):
        """an outer edge coordinate, hinted to whole px"""
        return float(round(self.pos(v, axis)))

    def qd(self, v, axis=0):
        """a dot centre: whole + half px at 24, nearest quarter at 16"""
        x = self.pos(v, axis)
        return math.floor(x) + 0.5 if self.N == 24 else round(x * 4) / 4

    def ln(self, v):
        return v * self.k

    # ---- primitives (master fen in, filled outlines out)
    def L(self, x1, y1, x2, y2):
        return OLD.L(self.q(x1), self.q(y1, 1), self.q(x2), self.q(y2, 1), w=self.sw)

    def P(self, pts, r=0.0, closed=False):
        """polyline stroke. Vertices may carry their own radius (x, y, r); others take r (fen).  Fillets are
        sampled into short segments so the outline is smooth, not faceted."""
        pts = [tuple(pt) if len(pt) == 3 else (pt[0], pt[1], r) for pt in pts]
        if closed and len(pts) > 1 and math.dist(pts[0][:2], pts[-1][:2]) < 1e-9:
            pts = pts[:-1]
        hp = []
        n = len(pts)
        for i, (x, y, rv) in enumerate(pts):
            ends = not closed and (i == 0 or i == n - 1)
            if rv <= 0 or ends:
                hp.append((self.q(x), self.q(y, 1)))
                continue
            a, b = pts[i - 1], pts[(i + 1) % n]
            ux, uy, vx, vy = a[0] - x, a[1] - y, b[0] - x, b[1] - y
            lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
            if lu < 1e-9 or lv < 1e-9:
                continue
            ux, uy, vx, vy = ux / lu, uy / lu, vx / lv, vy / lv
            cosang = max(-1.0, min(1.0, ux * vx + uy * vy))
            th = math.acos(cosang)
            if th > math.pi - 0.05:                 # nearly straight: no fillet
                hp.append((self.q(x), self.q(y, 1)))
                continue
            t = min(rv / math.tan(th / 2), lu / 2, lv / 2)
            p1 = (x + ux * t, y + uy * t)
            p2 = (x + vx * t, y + vy * t)
            k = 6
            for m in range(k + 1):
                u = m / k
                qx = (1 - u) ** 2 * p1[0] + 2 * (1 - u) * u * x + u * u * p2[0]
                qy = (1 - u) ** 2 * p1[1] + 2 * (1 - u) * u * y + u * u * p2[1]
                hp.append((self.q(qx), self.q(qy, 1)) if m in (0, k) else (self.pos(qx), self.pos(qy, 1)))
        out = []
        for pt in hp:
            if not out or math.dist(out[-1], pt) > 1e-6:
                out.append(pt)
        if closed and len(out) > 1 and math.dist(out[0], out[-1]) < 1e-6:
            out.pop()
        return OLD.P(out, closed=closed, r=0.0, w=self.sw)

    def box(self, x, y, w, h, r=3.0):
        """outline box, OUTER edges in fen"""
        x0, y0, x1, y1 = self.qo(x), self.qo(y, 1), self.qo(x + w), self.qo(y + h, 1)
        hh = self.sw / 2
        rr = min(self.ln(r), (x1 - x0) / 2, (y1 - y0) / 2) - hh
        return OLD.R(x0 + hh, y0 + hh, x1 - x0 - self.sw, y1 - y0 - self.sw, max(rr, 0.0), lw=self.sw)

    def slab(self, x, y, w, h, r=2.0):
        """solid box, outer edges in fen"""
        x0, y0, x1, y1 = self.qo(x), self.qo(y, 1), self.qo(x + w), self.qo(y + h, 1)
        return OLD.F(x0, y0, x1 - x0, y1 - y0, min(self.ln(r), (x1 - x0) / 2, (y1 - y0) / 2))

    def ring(self, cx, cy, ro):
        """ring, OUTER radius in fen, centre on a stroke coordinate"""
        r = self.ln(ro) * self.fit - self.sw / 2
        return OLD.C(self.pos(cx) if self.N == 16 else self.q(cx), self.pos(cy, 1) if self.N == 16 else self.q(cy, 1), r, w=self.sw)

    def arc(self, cx, cy, r, a0, a1):
        """arc of centre-line radius r (fen), degrees, 0 = east, clockwise on screen"""
        return OLD.A(self.pos(cx), self.pos(cy, 1), self.ln(r) * self.fit, a0, a1, w=self.sw)

    def dot(self, cx, cy, r=1.5):
        return OLD.D(self.qd(cx), self.qd(cy, 1), self.ln(r) if self.N == 24 else self.ln(r) * 1.1)

    def poly(self, pts, round_=True):
        """solid polygon (centre line), corners rounded by a stroke-wide outline"""
        hp = []
        for x, y in pts:
            pt = (self.q(x), self.q(y, 1))
            if not hp or math.dist(hp[-1], pt) > 1e-6:
                hp.append(pt)
        c = OLD.Contour(hp[0])
        for pt in hp[1:]:
            c.line(*pt)
        c.line(*hp[0])
        out = [c.oriented()]
        if round_:
            out += OLD.P(hp, closed=True, w=self.sw)
        return out

    def hole(self, contours):
        return OLD.HOLE(contours)

    def pill(self, x, y, w, h):
        """outline pill, OUTER edges"""
        return self.box(x, y, w, h, min(w, h) / 2)

    def pslab(self, x, y, w, h):
        return self.slab(x, y, w, h, min(w, h) / 2)

    def pie(self, cx, cy, r, a0, a1):
        return OLD.PIE(self.pos(cx), self.pos(cy, 1), self.ln(r) * self.fit, a0, a1)

    def disc(self, cx, cy, r):
        return OLD.D(self.pos(cx), self.pos(cy, 1), self.ln(r) * self.fit)

    def moon_solid(self, cx, cy, r, ox, oy, rr=None):
        return OLD.moon_solid(self.pos(cx), self.pos(cy, 1), self.ln(r) * self.fit, self.ln(ox) * self.fit, self.ln(oy) * self.fit, self.ln(rr) * self.fit if rr else None)

    def moon_arcs(self, cx, cy, r, ox, oy, rr=None):
        (c1, r1, o), (c2, r2, i) = OLD.moon_arcs(cx, cy, r, ox, oy, rr)
        return self.arc(c1[0], c1[1], r1, *o) + self.arc(c2[0], c2[1], r2, *i)

    def curve(self, pts, closed=False, n=8):
        """smooth stroke through master points (Catmull-Rom sampled, round joins)"""
        d = geom.smooth(pts, closed)
        return self.P(_sample(pts, closed, n))

    def juzhe(self, x0, y0, x1, y1, purlins=4, first=0.1, n=8):
        """G4: ridge (x0,y0) to eave (x1,y1) as a stroked folded slope"""
        pts = geom.juzhe(x0, y0, x1, y1, purlins=purlins, first=first)
        return self.P(_sample(pts, False, n))

    def juzhe_pts(self, x0, y0, x1, y1, purlins=4, first=0.1, n=8):
        return _sample(geom.juzhe(x0, y0, x1, y1, purlins=purlins, first=first), False, n)

    def raw(self, c):
        return c


def _sample(pts, closed, n):
    """Catmull-Rom through pts, n samples per span"""
    out = []
    m = len(pts)
    spans = m if closed else m - 1
    for i in range(spans):
        p0 = pts[i - 1] if (i > 0 or closed) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % m]
        p3 = pts[(i + 2) % m] if (i + 2 < m or closed) else p2
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                                    + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    if not closed:
        out.append(pts[-1])
    return out


def svg(layers, N):
    """layers: list of contour lists or (opacity, contours[, class]); fill-only SVG"""
    parts = []
    for l in layers:
        op, cs, cls = (l[0], l[1], l[2] if len(l) > 2 else None) if isinstance(l, tuple) else (1.0, l, None)
        d = "".join(c.d() for c in cs)
        a = ""
        if op < 1:
            a += f' opacity="{op:g}"'
        if cls:
            a += f' class="{cls}"'
        parts.append(f'<path d="{d}"{a}/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {N} {N}" width="{N}" height="{N}" style="color:#2e3436">'
            f'<g fill="currentColor">{"".join(parts)}</g></svg>\n')
