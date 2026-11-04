# SPDX-License-Identifier: GPL-2.0-or-later
"""Swept ribbons: real shaded 3D surfaces projected to the frame. A ribbon is a 3D centre curve with a
parallel-transport frame, a width, and a twist angle along it. It is cut into quads; each quad gets a
normal (tangent x width direction), is lit by one key light (upper left, toward the viewer) plus an
ambient fill, is darker on its far side and carries a subtle rim light where it turns edge-on; the back
face takes a second quiet tone. Quads of all ribbons are sorted by depth so one ribbon passes behind
another (self-occlusion); each quad has a thin thickness strip under its lower edge, and the whole
bundle throws a soft contact shadow. Matte throughout: no specular, no gloss."""
import math

import calculus as K
from geom import f
from walls_lib import lin, rad, blurf

LIGHT = (-0.45, -0.75, 0.55)
_n = math.sqrt(sum(v * v for v in LIGHT))
LIGHT = tuple(v / _n for v in LIGHT)


def catmull(pts, per=24, closed=False):
    out = []
    n = len(pts)
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        for k in range(per):
            t = k / per
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3) for a, b, c, d in zip(p0, p1, p2, p3)))
    if not closed:
        out.append(pts[-1])
    return out


def resample3(pts, n, closed=False):
    acc = [0.0]
    seq = pts + ([pts[0]] if closed else [])
    for a, b in zip(seq, seq[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    out, j = [], 0
    m = n if closed else n + 1
    for i in range(m):
        s = acc[-1] * i / (n if not closed else n)
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        t = (s - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        a, b = seq[j], seq[j + 1]
        out.append(tuple(x + (y - x) * t for x, y in zip(a, b)))
    return out


def unit(v):
    n = math.sqrt(sum(c * c for c in v)) or 1
    return tuple(c / n for c in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def ribbon(ctrl, width, theta, N=360, closed=False, ref=None, M=1, cup=0.0):
    """Return the strips of a ribbon: list of (corner points a0, a1, b1, b0 in 3D). Units: heights.
    width(s), theta(s) in radians; ref: reference vector for the width direction (default: in the screen,
    perpendicular to the tangent)."""
    cl = catmull(ctrl, 24, closed)
    P = resample3(cl, N, closed)
    m = len(P)
    strips = []
    frames = []
    for i in range(m):
        a, b = P[(i - 1) % m] if (closed or i > 0) else P[i], P[(i + 1) % m] if (closed or i < m - 1) else P[i]
        T = unit(tuple(y - x for x, y in zip(a, b)))
        R0 = ref(P[i]) if ref else (-T[1], T[0], 0.0)
        e1 = unit(tuple(r - dot(R0, T) * t for r, t in zip(R0, T)))
        e2 = cross(T, e1)
        s = i / (m - 1 if not closed else m)
        th, w = theta(s), width(s)
        wd = tuple(math.cos(th) * x + math.sin(th) * y for x, y in zip(e1, e2))
        nrm_ = unit(cross(T, wd))
        frames.append((P[i], wd, w, nrm_))
    last = m if closed else m - 1

    def corner(fr_, u):
        p, wd, w, nn = fr_
        sag = cup * w * (1 - 4 * u * u)
        return tuple(p[k] + wd[k] * w * u + nn[k] * sag for k in range(3))

    for i in range(last):
        fa, fb = frames[i], frames[(i + 1) % m]
        for j in range(M):
            u0, u1 = -0.5 + j / M, -0.5 + (j + 1) / M
            strips.append((corner(fa, u0), corner(fb, u0), corner(fb, u1), corner(fa, u1)))
    return strips


class Scene:
    def __init__(self, doc, fr, P, night):
        self.doc, self.fr, self.P, self.night = doc, fr, P, night
        self.quads = []
        self.shadow = []
        self._col = {}
        base = K.BASE
        self.hb = K.hue_of("base", base)
        self.hw = K.hue_of("water", base)
        self.base = base
        if night:
            self.k_hi, self.k_lo, self.fade_to = -2.0, -15.0, (-8.0, 3.5)
        else:
            self.k_hi, self.k_lo, self.fade_to = 18.0, 1.5, (17.0, 3.0)

    def colour(self, k, c, back):
        key = (round(k * 6) / 6, round(c * 2) / 2, back)
        if key not in self._col:
            self._col[key] = K.derive(key[0], key[1], self.hw if back else self.hb, self.base)
        return self._col[key]

    def add(self, strips, tone=(0.0, 1.0), fade=0.0, chroma=5.5, shadow=True, emit=None, thick=6, fibres=True):
        """tone: (low, high) share of the value range this ribbon uses; fade: 0..1 toward the background."""
        W, H = self.fr.w, self.fr.h
        n0, zmin, mine = len(self.quads), 9.0, []
        for si, (a0, a1, b1, b0) in enumerate(strips):
            ctr = tuple((a0[k] + a1[k] + b1[k] + b0[k]) / 4 for k in range(3))
            t = tuple(((a1[k] + b1[k]) - (a0[k] + b0[k])) / 2 for k in range(3))
            w = tuple(((b0[k] + b1[k]) - (a0[k] + a1[k])) / 2 for k in range(3))
            n = unit(cross(t, w))
            back = n[2] < 0
            if back:
                n = (-n[0], -n[1], -n[2])
            diff = max(0.0, dot(n, LIGHT))
            shade = 0.06 + 0.94 * diff + 0.10 * max(0.0, -n[1])
            rim = (1 - abs(n[2])) ** 3
            lo, hi = tone
            v = lo + (hi - lo) * shade
            v = min(1.0, v + 0.12 * rim)
            if emit:
                v = min(1.0, v * 0.75 + emit(si / max(1, len(strips) - 1)) * (0.45 + 0.55 * abs(n[2])))
            if back:
                v *= 0.80
            k = self.k_lo + (self.k_hi + (9.0 if emit else 0.0) - self.k_lo) * v
            c = chroma * (0.55 if back else 1.0)
            if fade:
                k += (self.fade_to[0] - k) * fade
                c += (self.fade_to[1] - c) * fade
            col = self.colour(k, c, back)
            dk = self.colour(k - 3.2, c, back)
            pts = [(p[0] * H, p[1] * H) for p in (a0, a1, b1, b0)]
            d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"
            th = self.fr.s * (thick(si / max(1, len(strips) - 1)) if callable(thick) else thick)
            ea, eb = (pts[0], pts[1]) if (pts[0][1] + pts[1][1]) > (pts[2][1] + pts[3][1]) else (pts[3], pts[2])
            dth = f"M{f(ea[0])} {f(ea[1])}L{f(eb[0])} {f(eb[1])}L{f(eb[0])} {f(eb[1] + th)}L{f(ea[0])} {f(ea[1] + th)}Z"
            lerp = lambda p, q, u: (p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u)
            fib = ""
            for u in (0.2, 0.4, 0.6, 0.8):
                p0_, p1_ = lerp(pts[0], pts[3], u), lerp(pts[1], pts[2], u)
                fib += f"M{f(p0_[0])} {f(p0_[1])}L{f(p1_[0])} {f(p1_[1])}"
            fc = self.colour(k + 1.6, c, back)
            svg = (f'<path d="{dth}" fill="{dk}" stroke="{dk}" stroke-width="1"/>'
                   f'<path d="{d}" fill="{col}" stroke="{col}" stroke-width="1.2" stroke-linejoin="round"/>')
            if fibres:
                svg += f'<path d="{fib}" fill="none" stroke="{fc}" stroke-width="{f(self.fr.s * 1.6)}" opacity="0.5"/>'
            self.quads.append((ctr[2], svg))
            if shadow:
                self.shadow.append(d)
                mine.append(d)
            zmin = min(zmin, ctr[2])
        if shadow:
            self.occlude(mine, zmin, 0.20 if not self.night else 0.30)

    def occlude(self, mine, zmin, op):
        if mine:
            sh = self.P["shade"]
            self.quads.append((zmin - 0.002, f'<path d="{"".join(mine)}" transform="translate({f(self.fr.l(26))} {f(self.fr.l(54))})" fill="{sh}" opacity="{f(op)}" filter="{blurf(self.doc, self.fr.l(34))}"/>'))

    def render(self, shadow_op=0.20, glow=False):
        W, H = self.fr.w, self.fr.h
        if glow and self.shadow:
            self.doc.add(f'<path d="{"".join(self.shadow)}" fill="{self.P["lightc"]}" opacity="0.30" filter="{blurf(self.doc, self.fr.l(70))}"/>')
            shadow_op = shadow_op * 0.6
        if self.shadow:
            sh = self.P["shade"]
            self.doc.add(f'<path d="{"".join(self.shadow)}" transform="translate({f(self.fr.l(70))} {f(self.fr.l(150))})" fill="{sh}" opacity="{f(shadow_op)}" filter="{blurf(self.doc, self.fr.l(60))}"/>')
        self.quads.sort(key=lambda q: q[0])
        self.doc.add("".join(s for _, s in self.quads))
