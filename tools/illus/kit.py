# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 Julia Klee
"""Tiny vector-painting kit for the WolOS illustrations.

Shapes are Catmull-Rom splines through hand-placed points. Volume is painted the way a
2D lighting artist would: base gradient, a blurred form shadow on the side away from the
key light, a warm highlight on the lit side, a thin violet rim from behind, and texture
strokes, all clipped to the shape. One light rig for every character:
key light top-left (warm), rim light back-right (violet)."""
import math
import random

KEY = (-0.62, -0.78)   # direction *towards* the key light (top-left)
RIM = (0.85, -0.25)    # direction towards the rim light (back-right)


def f(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


# ---------------------------------------------------------------- curves
def _cr(p0, p1, p2, p3, t=1.0):
    k = t / 6.0
    c1 = (p1[0] + (p2[0] - p0[0]) * k, p1[1] + (p2[1] - p0[1]) * k)
    c2 = (p2[0] - (p3[0] - p1[0]) * k, p2[1] - (p3[1] - p1[1]) * k)
    return c1, c2


def beziers(pts, closed=True, t=1.0):
    """Catmull-Rom through pts -> list of cubic segments (p1, c1, c2, p2).
    A point given as (x, y, 0) is a corner (no smoothing through it)."""
    n = len(pts)
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 and p[2] == 0 for p in pts]
    segs = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        i0, i2, i3 = (i - 1) % n, (i + 1) % n, (i + 2) % n
        if not closed:
            i0 = max(i - 1, 0)
            i3 = min(i + 2, n - 1)
        p0, p1, p2, p3 = P[i0], P[i], P[i2], P[i3]
        if sharp[i]:
            p0 = p1
        if sharp[i2]:
            p3 = p2
        c1, c2 = _cr(p0, p1, p2, p3, t)
        segs.append((p1, c1, c2, p2))
    return segs


def path(pts, closed=True, t=1.0):
    segs = beziers(pts, closed, t)
    d = f"M{f(segs[0][0][0])} {f(segs[0][0][1])}"
    for _, c1, c2, p2 in segs:
        d += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}"
    return d + ("Z" if closed else "")


def sample(pts, closed=True, per=12, t=1.0):
    out = []
    for p1, c1, c2, p2 in beziers(pts, closed, t):
        for k in range(per):
            u = k / per
            a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
            out.append((a * p1[0] + b * c1[0] + c * c2[0] + d * p2[0],
                        a * p1[1] + b * c1[1] + c * c2[1] + d * p2[1]))
    if not closed:
        out.append(pts[-1][:2])
    return out


def area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def inside(poly, x, y):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            c = not c
        j = i
    return c


def bbox(poly, pad=0):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs) - pad, min(ys) - pad, max(xs) + pad, max(ys) + pad


def fluffy(pts, ranges, amp=6.0, step=9.0, sweep=0.7, seed=1, per=16):
    """Spline outline with fur tufts along parameter ranges (0..1 of the outline).
    Returns (d, poly)."""
    rnd = random.Random(seed)
    poly = sample(pts, True, per)
    n = len(poly)
    sgn = 1 if area(poly) > 0 else -1   # screen coords: area>0 means clockwise
    # resample to equal arc length
    L = [0.0]
    for i in range(1, n + 1):
        a, b = poly[i - 1], poly[i % n]
        L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tot = L[-1]

    def at(s):
        s %= tot
        lo, hi = 0, n
        while hi - lo > 1:
            m = (lo + hi) // 2
            if L[m] <= s:
                lo = m
            else:
                hi = m
        a, b = poly[lo], poly[(lo + 1) % n]
        u = (s - L[lo]) / max(L[lo + 1] - L[lo], 1e-9)
        x, y = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        tx, ty = b[0] - a[0], b[1] - a[1]
        m = math.hypot(tx, ty) or 1
        tx, ty = tx / m, ty / m
        nx, ny = ty * sgn, -tx * sgn   # outward normal
        return x, y, tx, ty, nx, ny

    def tufted(s):
        u = (s % tot) / tot
        for r in ranges:
            a, b = r[0], r[1]
            if (a <= u <= b) if a <= b else (u >= a or u <= b):
                return r[2] if len(r) > 2 else 1.0
        return 0.0

    d = ""
    s = 0.0
    x, y, *_ = at(0)
    d = f"M{f(x)} {f(y)}"
    while s < tot - 1e-6:
        k = tufted(s)
        if k > 0:
            st = step * rnd.uniform(0.75, 1.3)
            s2 = min(s + st, tot)
            x1, y1, tx, ty, nx, ny = at(s + st * 0.55)
            a = amp * k * rnd.uniform(0.6, 1.25)
            tipx = x1 + nx * a + tx * a * sweep
            tipy = y1 + ny * a + ty * a * sweep
            x2, y2, *_ = at(s2)
            xa, ya, *_ = at(s + st * 0.35)
            d += f"Q{f(xa + nx * a * .3)} {f(ya + ny * a * .3)} {f(tipx)} {f(tipy)}"
            d += f"Q{f(x1 + nx * a * .15)} {f(y1 + ny * a * .15)} {f(x2)} {f(y2)}"
            s = s2
        else:
            s2 = min(s + 4.0, tot)
            x2, y2, *_ = at(s2)
            d += f"L{f(x2)} {f(y2)}"
            s = s2
    return d + "Z", poly


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, prefix, region=(-256, -256, 1024, 1024)):
        self.p = prefix
        self.defs = []
        self.n = 0
        self.region = region
        self._blur = {}

    def id(self, k="i"):
        self.n += 1
        return f"{self.p}{k}{self.n}"

    @staticmethod
    def _stops(stops):
        out = ""
        for s in stops:
            o, c = s[0], s[1]
            op = s[2] if len(s) > 2 else 1
            out += f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{op}"' if op != 1 else "") + "/>"
        return out

    def lin(self, x1, y1, x2, y2, stops):
        i = self.id("l")
        self.defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{f(x1)}" y1="{f(y1)}" '
                         f'x2="{f(x2)}" y2="{f(y2)}">{self._stops(stops)}</linearGradient>')
        return f"url(#{i})"

    def rad(self, cx, cy, r, stops, fx=None, fy=None, tf=None):
        i = self.id("r")
        fxy = "" if fx is None else f' fx="{f(fx)}" fy="{f(fy)}"'
        t = f' gradientTransform="{tf}"' if tf else ""
        self.defs.append(f'<radialGradient id="{i}" gradientUnits="userSpaceOnUse" cx="{f(cx)}" cy="{f(cy)}" '
                         f'r="{f(r)}"{fxy}{t}>{self._stops(stops)}</radialGradient>')
        return f"url(#{i})"

    def ell_rad(self, cx, cy, rx, ry, rot, stops, fx=0.0, fy=0.0):
        """Elliptical radial gradient: unit circle mapped onto an ellipse; fx/fy in -1..1."""
        tf = f"translate({f(cx)} {f(cy)}) rotate({f(rot)}) scale({f(rx)} {f(ry)})"
        return self.rad(0, 0, 1, stops, fx, fy, tf)

    def clip(self, d, tf=None):
        i = self.id("c")
        t = f' transform="{tf}"' if tf else ""
        self.defs.append(f'<clipPath id="{i}"><path d="{d}"{t}/></clipPath>')
        return f"url(#{i})"

    def blur(self, sd):
        sd = round(sd, 1)
        if sd not in self._blur:
            i = self.id("b")
            x, y, w, h = self.region
            self.defs.append(f'<filter id="{i}" filterUnits="userSpaceOnUse" x="{x}" y="{y}" width="{w}" height="{h}" '
                             f'color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{sd}"/></filter>')
            self._blur[sd] = f"url(#{i})"
        return self._blur[sd]

    def pattern(self, w, h, body, tf=None):
        i = self.id("p")
        t = f' patternTransform="{tf}"' if tf else ""
        self.defs.append(f'<pattern id="{i}" patternUnits="userSpaceOnUse" width="{w}" height="{h}"{t}>{body}</pattern>')
        return f"url(#{i})"

    def defs_xml(self):
        return "<defs>" + "".join(self.defs) + "</defs>"


def band(cv, d, poly, toward, dist, blur, color, op, pad=60, tf=None):
    """Light or shadow band hugging the edge of shape d on the side *toward* (dx,dy).
    Drawn as (bbox minus the shape shifted away), blurred; caller clips to the shape."""
    x0, y0, x1, y1 = bbox(poly, pad + dist + blur * 3)
    dx, dy = -toward[0] * dist, -toward[1] * dist
    return (f'<path d="M{f(x0)} {f(y0)}H{f(x1)}V{f(y1)}H{f(x0)}Z{d}" fill-rule="evenodd" fill="{color}" '
            f'opacity="{op}" transform="translate({f(dx)} {f(dy)})" filter="{cv.blur(blur)}"/>')


def volume(cv, d, poly, fill, shade=None, hi=None, rim=None, extra="", outline=None, under=""):
    """Paint a shape with form shadow, highlight and rim.
    shade=(color, opacity, dist, blur)  on the side away from the key light
    hi=(color, opacity, dist, blur)     on the lit side
    rim=(color, opacity, dist, blur)    thin, back-right
    extra: svg drawn inside the clip (texture, local shadows)."""
    c = cv.clip(d)
    g = f'<path d="{d}" fill="{fill}"/>'
    inner = under
    if shade:
        col, op, dist, bl = shade
        inner += band(cv, d, poly, (-KEY[0], -KEY[1]), dist, bl, col, op)
    if hi:
        col, op, dist, bl = hi
        inner += band(cv, d, poly, KEY, dist, bl, col, op)
    inner += extra
    if rim:
        col, op, dist, bl = rim
        inner += band(cv, d, poly, RIM, dist, bl, col, op)
    g += f'<g clip-path="{c}">{inner}</g>'
    if outline:
        g += f'<path d="{d}" fill="none" stroke="{outline[0]}" stroke-width="{outline[1]}" opacity="{outline[2]}"/>'
    return g


def fur(cv, poly, n, flow, length=(6, 12), width=1.0, colors=("#ffffff",), op=(0.25, 0.6), seed=3, margin=2):
    """Short hair strokes inside poly. flow(x, y) -> angle in radians."""
    rnd = random.Random(seed)
    x0, y0, x1, y1 = bbox(poly)
    out = []
    tries = 0
    while len(out) < n and tries < n * 30:
        tries += 1
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if not inside(poly, x, y):
            continue
        a = flow(x, y) + rnd.uniform(-0.25, 0.25)
        L = rnd.uniform(*length)
        bend = rnd.uniform(-0.3, 0.3)
        ex, ey = x + math.cos(a) * L, y + math.sin(a) * L
        mx = (x + ex) / 2 - math.sin(a) * L * bend
        my = (y + ey) / 2 + math.cos(a) * L * bend
        col = rnd.choice(colors)
        out.append(f'<path d="M{f(x)} {f(y)}Q{f(mx)} {f(my)} {f(ex)} {f(ey)}" stroke="{col}" '
                   f'stroke-opacity="{rnd.uniform(*op):.2f}"/>')
    return (f'<g fill="none" stroke-width="{width}" stroke-linecap="round">' + "".join(out) + "</g>")


def sparkle(x, y, r, color="#fff", op=1.0, rot=0):
    """Four-point star."""
    k = r * 0.16
    d = (f"M{f(x)} {f(y - r)}Q{f(x + k)} {f(y - k)} {f(x + r)} {f(y)}Q{f(x + k)} {f(y + k)} {f(x)} {f(y + r)}"
         f"Q{f(x - k)} {f(y + k)} {f(x - r)} {f(y)}Q{f(x - k)} {f(y - k)} {f(x)} {f(y - r)}Z")
    return f'<path d="{d}" fill="{color}" opacity="{op}" transform="rotate({rot} {f(x)} {f(y)})"/>'


def ellipse_pts(cx, cy, rx, ry, n=8, rot=0.0, jitter=None):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2
        x, y = rx * math.cos(a), ry * math.sin(a)
        if jitter:
            k = jitter[i % len(jitter)]
            x, y = x * k, y * k
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def svg(w, h, cv_list, body, title=""):
    defs = "".join(c.defs_xml() for c in cv_list)
    t = f"<title>{title}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f"{t}<!-- SPDX-License-Identifier: LicenseRef-Wonderland-Brand-1.0. (c) 2026 Julia Klee. WolOS illustrations. -->{defs}{body}</svg>\n")
