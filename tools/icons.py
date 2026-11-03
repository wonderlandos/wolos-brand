# SPDX-License-Identifier: GPL-2.0-or-later
"""WolOS icon set v2: one geometry for every icon. Python 3 stdlib only.

  python3 design/tools/icons.py [--sheet OUT.png] [--overlay DIR]

Writes
  design/icons/symbolic/<name>-symbolic.svg   16 grid, 1.5 px line, 2 px corner radius, currentColor
  design/icons/apps/wolos-<name>.svg          24-cell pixel tile (the WolOS wordmark's cells)
  design/icons/index.theme                    theme WolOS (same file as the overlay's)
  <overlay>/usr/share/icons/WolOS/{48x48,128x128,512x512}/apps/wolos-<name>.png and index.theme
  (overlay default: desktop/overlay of the repo that has design/ as a submodule)

Symbolic icons are drawn as lines and rings of width 1.5 and written as filled outlines (GTK 4.20
draws stroked symbolics as blobs, crates/shell/tests/symbolic_icons.rs): every line is a capsule,
every ring an outer contour plus a reversed inner one, so the default nonzero fill unions them.
App icons are a grid of cells: a squarish tile with stepped corners, a dithered two-tone gradient
(Bayer 8x8, as on wolos.org), a one-cell bevel and an edge that reads on light and dark grounds.
The PNGs and the contact sheet are rasterised here from the same shapes (no external renderer).
"""
import math, os, struct, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.normpath(os.path.join(HERE, ".."))
SYM_DIR = os.path.join(DESIGN, "icons", "symbolic")
APP_DIR = os.path.join(DESIGN, "icons", "apps")
# Brand drawings kept as they are (the logo is not redrawn here).
KEEP_SYMBOLIC = {"wolos-glyph-symbolic", "wolos-logo-symbolic"}
KEEP_APPS = {"wolos-mark"}
PNG_SIZES = (48, 128, 512)

# ======================================================================================
# Symbolic geometry
# ======================================================================================
SW = 1.5            # line width
H = SW / 2
RADIUS = 2.0        # corner radius of boxes (centre line)


class Contour:
    """Closed path: start point and segments ('L', x, y) or ('A', r, sweep, x, y, cx, cy)."""

    def __init__(self, start):
        self.start = start
        self.segs = []

    def line(self, x, y):
        self.segs.append(("L", x, y))
        return self

    def arc(self, r, sweep, x, y, cx, cy):
        self.segs.append(("A", r, sweep, x, y, cx, cy))
        return self

    def points(self):
        pts = [self.start]
        cur = self.start
        for s in self.segs:
            if s[0] == "L":
                pts.append((s[1], s[2]))
            else:
                _, r, sweep, x, y, cx, cy = s
                a0 = math.atan2(cur[1] - cy, cur[0] - cx)
                a1 = math.atan2(y - cy, x - cx)
                if sweep:
                    while a1 <= a0 + 1e-9:
                        a1 += 2 * math.pi
                else:
                    while a1 >= a0 - 1e-9:
                        a1 -= 2 * math.pi
                n = max(4, int(abs(a1 - a0) / (math.pi / 24)) + 1)
                for i in range(1, n + 1):
                    a = a0 + (a1 - a0) * i / n
                    pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
                pts[-1] = (x, y)
            cur = pts[-1]
        return pts

    def area(self):
        p = self.points()
        return sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p))) / -2

    def reversed(self):
        verts = [self.start] + [(s[1], s[2]) if s[0] == "L" else (s[3], s[4]) for s in self.segs]
        c = Contour(verts[-1])
        for i in range(len(self.segs) - 1, -1, -1):
            s = self.segs[i]
            x, y = verts[i]
            if s[0] == "L":
                c.line(x, y)
            else:
                c.arc(s[1], 1 - s[2], x, y, s[5], s[6])
        return c

    def oriented(self, solid=True):
        a = self.area()
        return self if (a > 0) == solid else self.reversed()

    def d(self):
        f = lambda v: f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) > 5e-4 else "0"
        out = [f"M{f(self.start[0])} {f(self.start[1])}"]
        cur = self.start
        for s in self.segs:
            if s[0] == "L":
                if abs(s[1] - cur[0]) > 1e-6 or abs(s[2] - cur[1]) > 1e-6:
                    out.append(f"L{f(s[1])} {f(s[2])}")
                cur = (s[1], s[2])
            else:
                _, r, sweep, x, y, cx, cy = s
                a0 = math.atan2(cur[1] - cy, cur[0] - cx)
                a1 = math.atan2(y - cy, x - cx)
                span = (a1 - a0) % (2 * math.pi) if sweep else (a0 - a1) % (2 * math.pi)
                if span < 1e-6:
                    span = 2 * math.pi
                if span > math.pi * 1.999:      # a full turn: two halves
                    mx, my = 2 * cx - cur[0], 2 * cy - cur[1]
                    out.append(f"A{f(r)} {f(r)} 0 0 {sweep} {f(mx)} {f(my)}")
                    out.append(f"A{f(r)} {f(r)} 0 0 {sweep} {f(x)} {f(y)}")
                else:
                    out.append(f"A{f(r)} {f(r)} 0 {1 if span > math.pi else 0} {sweep} {f(x)} {f(y)}")
                cur = (x, y)
        return "".join(out) + "Z"


def circle_contour(cx, cy, r):
    c = Contour((cx + r, cy))
    c.arc(r, 1, cx - r, cy, cx, cy).arc(r, 1, cx + r, cy, cx, cy)
    return c


def rrect_contour(x, y, w, h, r):
    r = max(0.0, min(r, w / 2, h / 2))
    if r < 1e-6:
        return Contour((x, y)).line(x + w, y).line(x + w, y + h).line(x, y + h).line(x, y)
    c = Contour((x + r, y))
    c.line(x + w - r, y).arc(r, 1, x + w, y + r, x + w - r, y + r)
    c.line(x + w, y + h - r).arc(r, 1, x + w - r, y + h, x + w - r, y + h - r)
    c.line(x + r, y + h).arc(r, 1, x, y + h - r, x + r, y + h - r)
    c.line(x, y + r).arc(r, 1, x + r, y, x + r, y + r)
    return c


# Primitives return lists of oriented contours (solid > 0, holes < 0).
def L(x1, y1, x2, y2, w=SW):
    """Line with round caps."""
    h = w / 2
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    if n < 1e-9:
        return [circle_contour(x1, y1, h)]
    nx, ny = -dy / n * h, dx / n * h
    c = Contour((x1 + nx, y1 + ny))
    c.line(x2 + nx, y2 + ny).arc(h, 0, x2 - nx, y2 - ny, x2, y2)
    c.line(x1 - nx, y1 - ny).arc(h, 0, x1 + nx, y1 + ny, x1, y1)
    return [c.oriented()]


def P(pts, closed=False, r=0.0, w=SW):
    """Polyline; r rounds the inner corners (fillets) on the centre line."""
    pts = list(pts)
    if closed:
        pts = pts + [pts[0]]
    if r <= 0:
        out = []
        for a, b in zip(pts, pts[1:]):
            out += L(*a, *b, w=w)
        return out
    out = []
    n = len(pts)
    # Fillet each interior vertex (all vertices when closed).
    corners = range(1, n - 1) if not closed else range(0, n - 1)
    cut = {}
    for i in corners:
        p = pts[i]
        a = pts[i - 1] if i > 0 else pts[n - 2]
        b = pts[i + 1]
        ux, uy = a[0] - p[0], a[1] - p[1]
        vx, vy = b[0] - p[0], b[1] - p[1]
        lu, lv = math.hypot(ux, uy), math.hypot(vx, vy)
        ux, uy, vx, vy = ux / lu, uy / lu, vx / lv, vy / lv
        cosang = max(-1.0, min(1.0, ux * vx + uy * vy))
        th = math.acos(cosang)
        if th < 1e-3 or abs(th - math.pi) < 1e-3:
            continue
        t = min(r / math.tan(th / 2), lu / 2, lv / 2)
        rr = t * math.tan(th / 2)
        p1 = (p[0] + ux * t, p[1] + uy * t)
        p2 = (p[0] + vx * t, p[1] + vy * t)
        bx, by = ux + vx, uy + vy
        bl = math.hypot(bx, by)
        dist = rr / math.sin(th / 2)
        cx, cy = p[0] + bx / bl * dist, p[1] + by / bl * dist
        cut[i] = (p1, p2, (cx, cy), rr)
    segs = []
    for i in range(n - 1):
        a = cut[i][1] if i in cut else pts[i]
        if closed and i == 0 and 0 in cut:
            a = cut[0][1]
        j = i + 1
        jj = 0 if (closed and j == n - 1) else j
        b = cut[jj][0] if jj in cut else pts[j]
        segs += L(*a, *b, w=w)
    for i, (p1, p2, (cx, cy), rr) in cut.items():
        a0 = math.degrees(math.atan2(p1[1] - cy, p1[0] - cx))
        a1 = math.degrees(math.atan2(p2[1] - cy, p2[0] - cx))
        if (a1 - a0) % 360 > 180:
            a0, a1 = a1, a0
        if a1 < a0:
            a1 += 360
        segs += A(cx, cy, rr, a0, a1, w=w)
    return out + segs


def R(x, y, w, h, r=RADIUS, lw=SW):
    """Box outline: centre line x, y, w, h."""
    hh = lw / 2
    out = [rrect_contour(x - hh, y - hh, w + lw, h + lw, r + hh).oriented()]
    if w > lw and h > lw:
        out.append(rrect_contour(x + hh, y + hh, w - lw, h - lw, max(r - hh, 0)).oriented(False))
    return out


def C(cx, cy, r, w=SW):
    """Ring."""
    out = [circle_contour(cx, cy, r + w / 2).oriented()]
    if r - w / 2 > 0:
        out.append(circle_contour(cx, cy, r - w / 2).oriented(False))
    return out


def A(cx, cy, r, a0, a1, w=SW):
    """Arc from a0 to a1 degrees (0 = east, clockwise on screen), round caps."""
    h = w / 2
    t0, t1 = math.radians(a0), math.radians(a1)
    pt = lambda rad, t: (cx + rad * math.cos(t), cy + rad * math.sin(t))
    o0, o1 = pt(r + h, t0), pt(r + h, t1)
    i0, i1 = pt(r - h, t0), pt(r - h, t1)
    c = Contour(o0)
    # split into <= 90 degree pieces so the SVG large-arc flag never matters
    k = max(1, int(math.ceil(abs(a1 - a0) / 90)))
    for j in range(1, k + 1):
        c.arc(r + h, 1, *pt(r + h, t0 + (t1 - t0) * j / k), cx, cy)
    c.line(*i1)
    for j in range(k - 1, -1, -1):
        c.arc(r - h, 0, *pt(r - h, t0 + (t1 - t0) * j / k), cx, cy)
    c.line(*o0)
    return [c.oriented(), circle_contour(*pt(r, t0), h).oriented(), circle_contour(*pt(r, t1), h).oriented()]


def D(cx, cy, r):
    """Filled disc."""
    return [circle_contour(cx, cy, r).oriented()]


def F(x, y, w, h, r=0.0):
    """Filled box (outer edges)."""
    return [rrect_contour(x, y, w, h, r).oriented()]


def FP(pts, round_=True):
    """Filled polygon; round_ adds a 1.5 line around it (rounded corners, same weight as lines)."""
    c = Contour(pts[0])
    for p in pts[1:]:
        c.line(*p)
    c.line(*pts[0])
    out = [c.oriented()]
    if round_:
        out += P(pts, closed=True)
    return out


def PIE(cx, cy, r, a0, a1):
    """Filled sector."""
    t0, t1 = math.radians(a0), math.radians(a1)
    c = Contour((cx, cy)).line(cx + r * math.cos(t0), cy + r * math.sin(t0))
    k = max(1, int(math.ceil(abs(a1 - a0) / 90)))
    for j in range(1, k + 1):
        t = t0 + (t1 - t0) * j / k
        c.arc(r, 1, cx + r * math.cos(t), cy + r * math.sin(t), cx, cy)
    c.line(cx, cy)
    return [c.oriented()]


def HOLE(contours):
    return [c.oriented(False) for c in contours]


def arc_through(ax, ay, bx, by, sag, w=SW):
    """Circular arc from a to b bulging `sag` to the left of a->b (negative: right)."""
    mx, my = (ax + bx) / 2, (ay + by) / 2
    dx, dy = bx - ax, by - ay
    c = math.hypot(dx, dy) / 2
    r = (c * c + sag * sag) / (2 * abs(sag))
    nx, ny = dy / (2 * c), -dx / (2 * c)       # left normal (screen)
    s = 1 if sag > 0 else -1
    cx, cy = mx - nx * s * (r - abs(sag)), my - ny * s * (r - abs(sag))
    a0 = math.degrees(math.atan2(ay - cy, ax - cx))
    a1 = math.degrees(math.atan2(by - cy, bx - cx))
    if (a1 - a0) % 360 > 180:
        a0, a1 = a1, a0
    if a1 < a0:
        a1 += 360
    return A(cx, cy, r, a0, a1, w=w)


def head(x, y, ang, size=3.0):
    """Arrow head with its tip at x, y pointing along ang degrees."""
    out = []
    for da in (150, -150):
        t = math.radians(ang + da)
        out += L(x, y, x + size * math.cos(t), y + size * math.sin(t))
    return out


def arrow(x1, y1, x2, y2, size=3.5):
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    return L(x1, y1, x2, y2) + head(x2, y2, ang, size)


def cloud(circles, base):
    """Cloud outline from circles tangent to the base line, left to right."""
    out = []
    ints = []
    for (x1, y1, r1), (x2, y2, r2) in zip(circles, circles[1:]):
        d = math.hypot(x2 - x1, y2 - y1)
        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
        hh = math.sqrt(max(r1 * r1 - a * a, 0))
        px, py = x1 + a * (x2 - x1) / d, y1 + a * (y2 - y1) / d
        cands = [(px + hh * (y2 - y1) / d, py - hh * (x2 - x1) / d),
                 (px - hh * (y2 - y1) / d, py + hh * (x2 - x1) / d)]
        ints.append(min(cands, key=lambda p: p[1]))
    for i, (x, y, r) in enumerate(circles):
        ang = lambda p: math.degrees(math.atan2(p[1] - y, p[0] - x))
        a0 = 90 if i == 0 else ang(ints[i - 1])
        a1 = 450 if i == len(circles) - 1 else ang(ints[i])
        if i > 0:
            a0 %= 360
        while a1 <= a0:
            a1 += 360
        out += A(x, y, r, a0, a1)
    out += L(circles[0][0], base, circles[-1][0], base)
    return out


def moon_arcs(cx, cy, r, ox, oy, rr=None):
    """Crescent: circle (cx, cy, r) minus the circle offset by (ox, oy). Returns
    ((c1, r, a0, a1) outer arc, (c2, rr, b0, b1) inner arc), angles increasing."""
    rr = rr or r
    x2, y2 = cx + ox, cy + oy
    d = math.hypot(ox, oy)
    a = (r * r - rr * rr + d * d) / (2 * d)
    hh = math.sqrt(r * r - a * a)
    px, py = cx + a * ox / d, cy + a * oy / d
    p1 = (px + hh * oy / d, py - hh * ox / d)
    p2 = (px - hh * oy / d, py + hh * ox / d)
    ang = lambda p, c: math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))
    # outer: the long way round circle 1 (away from circle 2)
    b0, b1 = ang(p1, (cx, cy)), ang(p2, (cx, cy))
    away = math.degrees(math.atan2(-oy, -ox))
    def span(s, e, through):
        while e <= s:
            e += 360
        t = through
        while t < s:
            t += 360
        return (s, e) if t <= e else (e, s + 360)
    o = span(b0, b1, away)
    c0, c1 = ang(p1, (x2, y2)), ang(p2, (x2, y2))
    towards = math.degrees(math.atan2(-oy, -ox))
    i = span(c0, c1, towards)
    return ((cx, cy), r, o), ((x2, y2), rr, i)


def moon(cx, cy, r, ox, oy, rr=None):
    (c1, r1, o), (c2, r2, i) = moon_arcs(cx, cy, r, ox, oy, rr)
    return A(*c1, r1, *o) + A(*c2, r2, *i)


def moon_solid(cx, cy, r, ox, oy, rr=None):
    """Filled crescent (one contour: outer arc out, inner arc back)."""
    (c1, r1, o), (c2, r2, i) = moon_arcs(cx, cy, r, ox, oy, rr)
    pt = lambda c, rad, a: (c[0] + rad * math.cos(math.radians(a)), c[1] + rad * math.sin(math.radians(a)))
    con = Contour(pt(c1, r1, o[0]))
    k = 4
    for j in range(1, k + 1):
        con.arc(r1, 1, *pt(c1, r1, o[0] + (o[1] - o[0]) * j / k), *c1)
    end = pt(c1, r1, o[1])
    fwd = math.dist(end, pt(c2, r2, i[0])) < math.dist(end, pt(c2, r2, i[1]))
    seq = [i[0] + (i[1] - i[0]) * j / k for j in range(k + 1)]
    if not fwd:
        seq = seq[::-1]
    for a in seq[1:]:
        con.arc(r2, 1 if fwd else 0, *pt(c2, r2, a), *c2)
    con.line(*con.start)
    return [con.oriented()]


def gear(cx, cy, ro, ri, teeth, hole):
    pts = []
    for k in range(teeth):
        base = 360 * k / teeth
        for da, rad in ((-0.30, ri), (-0.17, ro), (0.17, ro), (0.30, ri)):
            t = math.radians(base + da * 360 / teeth)
            pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))
    return P(pts, closed=True, r=0.5) + C(cx, cy, hole)


def star(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for k in range(2 * n):
        t = math.radians(rot + 180 * k / n)
        rad = ro if k % 2 == 0 else ri
        pts.append((cx + rad * math.cos(t), cy + rad * math.sin(t)))
    return pts


def sparkle(cx, cy, r, waist=0.28):
    return star(cx, cy, r, r * waist, n=4, rot=-90)


def dashed_rect(x, y, w, h, dash=2.0, gap=1.75):
    """Rounded box drawn in dashes along its centre line."""
    out = []
    for (x1, y1, x2, y2) in ((x, y, x + w, y), (x + w, y, x + w, y + h), (x + w, y + h, x, y + h), (x, y + h, x, y)):
        n = math.hypot(x2 - x1, y2 - y1)
        k = max(1, int(round((n + gap) / (dash + gap))))
        step = n / k
        for j in range(k):
            s = j * step + gap / 2
            e = min(n, s + step - gap)
            if j == 0:
                s = 0
            if j == k - 1:
                e = n
            out += L(x1 + (x2 - x1) * s / n, y1 + (y2 - y1) * s / n, x1 + (x2 - x1) * e / n, y1 + (y2 - y1) * e / n)
    return out


def corners(x, y, w, h, arm=3.0, r=1.5):
    out = []
    for (px, py, sx, sy) in ((x, y, 1, 1), (x + w, y, -1, 1), (x + w, y + h, -1, -1), (x, y + h, 1, -1)):
        out += P([(px, py + sy * arm), (px, py), (px + sx * arm, py)], r=r)
    return out


def slash():
    return L(2.25, 2.25, 13.75, 13.75)


# ---- shared parts --------------------------------------------------------------------
def magnifier(cx=6.75, cy=6.75, r=4.5):
    k = r / math.sqrt(2) + 0.75
    return C(cx, cy, r) + L(cx + k, cy + k, 13.75, 13.75)


def person(cx=8, top=2.0, s=1.0):
    return C(cx, top + 2.75 * s, 2.5 * s) + A(cx, top + 12.5 * s, 5.25 * s, 200, 340)


def lock(x=3.0, y=7.0, w=10.0, h=6.75, sh=3.0):
    cx = x + w / 2
    return R(x, y, w, h) + P([(cx - sh, y), (cx - sh, y - 1.75)]) + A(cx, y - 1.75, sh, 180, 360) + \
        P([(cx + sh, y - 1.75), (cx + sh, y)]) + D(cx, y + h / 2, 1.0)


def monitor():
    return R(1.75, 2.25, 12.5, 8.75) + L(8, 11.75, 8, 13.5) + L(5, 13.75, 11, 13.75)


def speaker():
    return FP([(1.75, 6.25), (3.75, 6.25), (6.75, 3.25), (6.75, 12.75), (3.75, 9.75), (1.75, 9.75)])


def waves(level, n=3):
    out = []
    for i, r in enumerate((2.5, 4.75, 7.0)[:n]):
        ang = (52, 50, 44)[i]
        out.append((1.0 if i < level else 0.35, A(6.75, 8, r, -ang, ang)))
    return out


def wifi(level, enc=False):
    out = [(1.0 if level > 0 else 0.35, D(8, 12.75, 1.4))]
    for i, r in enumerate((3.5, 6.5, 9.5)):
        a = 45 if i < 2 else 40
        out.append((1.0 if i < level else 0.35, A(8, 13.25, r, 270 - a, 270 + a)))
    return out


def battery(frac, charging=False, caution=False, missing=False):
    out = [(1.0, R(1.75, 4.25, 10.75, 7.5) + F(13.25, 6.25, 1.5, 3.5, 0.75))]
    if frac > 0:
        wfill = max(1.5, 7.25 * frac)
        out.append((0.35 if charging else 1.0, F(3.5, 6.0, wfill, 4.0, 0.75), "error" if caution and not charging else None))
    if charging:
        out.append((1.0, FP([(8.25, 3.0), (5.0, 8.5), (7.25, 8.5), (6.5, 13.0), (10.0, 7.5), (7.75, 7.5)])))
    if missing:
        out.append((1.0, slash()))
    return out


def bell():
    return P([(4.0, 6.75), (4.0, 9.75), (2.5, 11.5), (13.5, 11.5), (12.0, 9.75), (12.0, 6.75)], r=1.25) + \
        A(8, 6.75, 4, 180, 360) + A(8, 12.5, 1.75, 20, 160)


def page(x=3.0, y=1.75, w=10.0, h=12.5, fold=3.0):
    return P([(x + w - fold, y), (x, y), (x, y + h), (x + w, y + h), (x + w, y + fold)], closed=True, r=1.5) + \
        P([(x + w - fold, y), (x + w - fold, y + fold), (x + w, y + fold)], r=1.0)


def folder():
    return P([(1.75, 3.0), (6.0, 3.0), (7.5, 4.75), (14.25, 4.75), (14.25, 13.0), (1.75, 13.0)], closed=True, r=1.75)


def frame_pic():
    return R(1.75, 2.75, 12.5, 10.5) + P([(4.25, 10.75), (7.0, 7.5), (9.0, 9.5), (10.5, 8.25), (12.0, 9.75)], r=0.75) + D(10.5, 5.75, 1.25)


def sun(cx=8, cy=8, r=2.75, r0=5.0, r1=6.5, rays=8):
    out = C(cx, cy, r)
    for k in range(rays):
        t = math.radians(360 * k / rays)
        out += L(cx + r0 * math.cos(t), cy + r0 * math.sin(t), cx + r1 * math.cos(t), cy + r1 * math.sin(t))
    return out


def cloud_big():
    return cloud([(4.25, 10.0, 2.75), (8.5, 8.25, 4.5), (12.0, 10.5, 2.25)], 12.75)


def cloud_high():
    return cloud([(4.25, 7.0, 2.5), (8.25, 5.75, 3.75), (11.75, 7.5, 2.0)], 9.5)


def gauge(angle):
    t = math.radians(angle)
    return A(8, 10, 6, 180, 360) + L(8, 10, 8 + 4 * math.cos(t), 10 + 4 * math.sin(t)) + D(8, 10, 1.5)


def drive(y=4.25, h=7.5):
    return R(1.75, y, 12.5, h) + D(11.25, y + h / 2, 0.9) + L(4.5, y + h / 2, 7.5, y + h / 2)


def window_frame():
    return R(1.75, 2.75, 12.5, 10.5) + L(1.75, 5.75, 14.25, 5.75)


def chevron(dirn, size=4.5, cx=8, cy=8, r=0.5):
    s = size / 2
    pts = {
        "right": [(cx - s / 2, cy - s), (cx + s / 2, cy), (cx - s / 2, cy + s)],
        "left": [(cx + s / 2, cy - s), (cx - s / 2, cy), (cx + s / 2, cy + s)],
        "down": [(cx - s, cy - s / 2), (cx, cy + s / 2), (cx + s, cy - s / 2)],
        "up": [(cx - s, cy + s / 2), (cx, cy - s / 2), (cx + s, cy + s / 2)],
    }[dirn]
    return P(pts, r=r)


def eye():
    return arc_through(1.75, 8, 14.25, 8, 4.75) + arc_through(1.75, 8, 14.25, 8, -4.75) + C(8, 8, 2.0)


def leaf():
    return arc_through(3.0, 13.0, 13.0, 3.0, 3.25) + arc_through(3.0, 13.0, 13.0, 3.0, -3.25) + L(3.0, 13.0, 9.0, 7.0)


def bolt(dx=0.0, dy=0.0, s=1.0):
    pts = [(9.0, 1.75), (4.0, 9.0), (7.75, 9.0), (7.0, 14.25), (12.0, 7.0), (8.25, 7.0)]
    return FP([(dx + 8 + (x - 8) * s, dy + 8 + (y - 8) * s) for x, y in pts])


def shield():
    return P([(8, 1.75), (13.25, 3.5), (13.25, 8.0), (8, 14.25), (2.75, 8.0), (2.75, 3.5)], closed=True, r=2.0)


def bluetooth():
    return P([(4.5, 5.0), (11.0, 10.75), (8.0, 13.75), (8.0, 2.25), (11.0, 5.25), (4.5, 11.0)], r=0.5)


def mic():
    return R(5.75, 1.75, 4.5, 7.75, 2.25) + A(8, 7.25, 4.25, 20, 160) + L(8, 11.5, 8, 14.25)


def headphones():
    return A(8, 9.25, 5.75, 180, 360) + F(1.5, 9.0, 3.5, 5.25, 1.25) + F(11.0, 9.0, 3.5, 5.25, 1.25)


def globe():
    return C(8, 8, 6.25) + L(1.75, 8, 14.25, 8) + arc_through(8, 1.75, 8, 14.25, 2.75) + arc_through(8, 1.75, 8, 14.25, -2.75)


def refresh(cx=8, cy=8, r=5.5):
    a1 = 300
    t = math.radians(a1)
    tip = (cx + r * math.cos(t), cy + r * math.sin(t))
    return A(cx, cy, r, 0, a1) + head(tip[0], tip[1], a1 + 98, 3.0)


def keyboard():
    out = R(1.25, 3.75, 13.5, 8.5)
    for row, y in enumerate((6.25, 8.5)):
        for k in range(5):
            out += D(4.0 + k * 2.0, y, 0.7)
    return out + L(5.5, 10.25, 10.5, 10.25)


def gamepad():
    out = P([(4.75, 4.0), (11.25, 4.0), (13.25, 4.75), (14.5, 11.0), (12.75, 12.75), (10.5, 10.5), (5.5, 10.5), (3.25, 12.75), (1.5, 11.0), (2.75, 4.75)], closed=True, r=1.25)
    return out + L(4.25, 7.25, 7.0, 7.25) + L(5.625, 5.875, 5.625, 8.625) + D(10.25, 6.5, 0.9) + D(11.75, 8.25, 0.9)


def capture_dot():
    return D(8, 8, 2.25)


def tile_grid():
    out = []
    for i in range(3):
        for j in range(3):
            out += F(1.5 + i * 4.75, 1.5 + j * 4.75, 3.5, 3.5, 1.0)
    return out


def calendar():
    return R(1.75, 2.75, 12.5, 11.5) + L(1.75, 6.25, 14.25, 6.25) + L(5.0, 1.5, 5.0, 4.0) + L(11.0, 1.5, 11.0, 4.0)


def chip():
    out = R(4.0, 4.0, 8.0, 8.0, 1.5) + F(6.5, 6.5, 3.0, 3.0, 0.75)
    for k in (6.0, 8.0, 10.0):
        out += L(k, 1.5, k, 2.75) + L(k, 13.25, k, 14.5) + L(1.5, k, 2.75, k) + L(13.25, k, 14.5, k)
    return out


def note_pair():
    return D(4.5, 12.0, 2.0) + D(11.25, 10.5, 2.0) + L(5.75, 12.0, 5.75, 3.75) + L(12.5, 10.5, 12.5, 2.25) + \
        FP([(5.75, 3.0), (12.5, 1.5), (12.5, 3.25), (5.75, 4.75)])


def house():
    return P([(2.0, 7.5), (8.0, 2.25), (14.0, 7.5)], r=0.75) + P([(3.75, 6.25), (3.75, 13.25), (12.25, 13.25), (12.25, 6.25)], r=1.5) + \
        P([(6.75, 13.25), (6.75, 9.75), (9.25, 9.75), (9.25, 13.25)], r=0.75)


def trash():
    return L(2.25, 4.0, 13.75, 4.0) + P([(6.0, 4.0), (6.25, 2.0), (9.75, 2.0), (10.0, 4.0)], r=0.5) + \
        P([(3.75, 4.5), (4.5, 13.5), (11.5, 13.5), (12.25, 4.5)], r=1.5) + L(6.5, 7.0, 6.75, 10.75) + L(9.5, 7.0, 9.25, 10.75)


def clipboard():
    return P([(5.0, 3.0), (3.0, 3.0), (3.0, 14.25), (13.0, 14.25), (13.0, 3.0), (11.0, 3.0)], r=2.0) + R(5.75, 1.75, 4.5, 2.5, 1.0)


def puzzle():
    return P([(5.0, 4.75), (2.25, 4.75), (2.25, 13.75), (11.25, 13.75), (11.25, 11.0)], r=2.0) + A(6.75, 4.75, 1.75, 180, 360) +         P([(8.5, 4.75), (11.25, 4.75), (11.25, 7.5)], r=2.0) + A(11.25, 9.25, 1.75, 270, 450)


def sliders():
    return R(1.75, 2.75, 12.5, 4.0, 2.0) + D(12.25, 4.75, 1.5) + R(1.75, 9.25, 12.5, 4.0, 2.0) + C(3.75, 11.25, 1.0, w=1.5)


SYMBOLIC = {}


def sym(name, *layers):
    """layers: contour lists (opacity 1) or (opacity, contours[, class])."""
    out = []
    for l in layers:
        if isinstance(l, tuple):
            out.append((l[0], l[1], l[2] if len(l) > 2 else None))
        else:
            out.append((1.0, l, None))
    SYMBOLIC[name + "-symbolic"] = out


def build_symbolic():
    # navigation and window
    sym("go-next", chevron("right", 9.0))
    sym("go-previous", chevron("left", 9.0))
    sym("go-up", chevron("up", 9.0))
    sym("go-down", chevron("down", 9.0))
    sym("pan-end", chevron("right", 6.0))
    sym("pan-start", chevron("left", 6.0))
    sym("pan-up", chevron("up", 6.0))
    sym("pan-down", chevron("down", 6.0))
    sym("window-close", L(4.0, 4.0, 12.0, 12.0) + L(12.0, 4.0, 4.0, 12.0))
    sym("window-minimize", L(4.0, 11.5, 12.0, 11.5))
    sym("window-maximize", R(3.5, 3.5, 9.0, 9.0))
    sym("window-restore", R(2.75, 5.25, 8.0, 8.0) + P([(5.25, 2.75), (13.25, 2.75), (13.25, 10.75)], r=2.0))
    sym("view-more", D(3.25, 8, 1.4) + D(8, 8, 1.4) + D(12.75, 8, 1.4))
    sym("open-menu", L(2.75, 4.0, 13.25, 4.0) + L(2.75, 8.0, 13.25, 8.0) + L(2.75, 12.0, 13.25, 12.0))
    sym("view-list", L(5.5, 4.0, 13.75, 4.0) + L(5.5, 8.0, 13.75, 8.0) + L(5.5, 12.0, 13.75, 12.0) + D(2.5, 4, 1) + D(2.5, 8, 1) + D(2.5, 12, 1))
    sym("view-grid", R(2.25, 2.25, 4.5, 4.5, 1.5) + R(9.25, 2.25, 4.5, 4.5, 1.5) + R(2.25, 9.25, 4.5, 4.5, 1.5) + R(9.25, 9.25, 4.5, 4.5, 1.5))
    sym("view-app-grid", tile_grid())
    sym("view-refresh", refresh())
    sym("view-reveal", eye())
    sym("view-conceal", eye(), slash())
    sym("list-add", L(8, 2.75, 8, 13.25) + L(2.75, 8, 13.25, 8))
    sym("list-remove", L(2.75, 8, 13.25, 8))
    sym("value-increase", L(8, 2.75, 8, 13.25) + L(2.75, 8, 13.25, 8))
    sym("value-decrease", L(2.75, 8, 13.25, 8))
    sym("object-select", P([(2.75, 8.5), (6.25, 12.0), (13.25, 4.25)], r=0.75))
    sym("emblem-default", C(8, 8, 6.25) + P([(5.0, 8.25), (7.0, 10.25), (11.0, 5.75)], r=0.5))
    sym("edit-delete", trash())
    sym("user-trash", trash())
    sym("edit-paste", clipboard())
    sym("edit-copy", R(5.25, 5.25, 8.75, 8.75) + P([(2.0, 10.0), (2.0, 2.0), (10.0, 2.0)], r=2.0))
    sym("edit-cut", C(4.25, 11.5, 2.25) + C(11.75, 11.5, 2.25) + L(5.75, 9.75, 11.5, 2.0) + L(10.25, 9.75, 4.5, 2.0))
    sym("edit-find", magnifier())
    sym("system-search", magnifier())
    sym("zoom-in", magnifier() + L(6.75, 4.75, 6.75, 8.75) + L(4.75, 6.75, 8.75, 6.75))
    sym("zoom-out", magnifier() + L(4.75, 6.75, 8.75, 6.75))
    sym("edit-clear", C(8, 8, 6.25) + L(5.75, 5.75, 10.25, 10.25) + L(10.25, 5.75, 5.75, 10.25))
    sym("edit-undo", A(8.5, 9.0, 4.75, 200, 450) + head(8.5 + 4.75 * math.cos(math.radians(200)), 9.0 + 4.75 * math.sin(math.radians(200)), 110, 3.0))
    sym("edit-redo", A(7.5, 9.0, 4.75, 90, 340) + head(7.5 + 4.75 * math.cos(math.radians(340)), 9.0 + 4.75 * math.sin(math.radians(340)), 70, 3.0))
    sym("edit-select-all", dashed_rect(2.0, 2.0, 12.0, 12.0) + F(5.0, 5.0, 6.0, 6.0, 1.0))
    sym("document-edit", P([(3.0, 13.0), (3.5, 10.25), (10.75, 3.0), (13.0, 5.25), (5.75, 12.5)], closed=True, r=0.75) + L(9.25, 4.5, 11.5, 6.75))
    sym("document-open", folder())
    sym("document-save", arrow(8, 1.75, 8, 9.75, 3.75) + P([(2.0, 10.0), (2.0, 13.75), (14.0, 13.75), (14.0, 10.0)], r=1.5))
    sym("document-new", page() + L(8, 7.0, 8, 11.5) + L(5.75, 9.25, 10.25, 9.25))
    sym("folder-new", folder() + L(8, 7.0, 8, 11.0) + L(6.0, 9.0, 10.0, 9.0))
    sym("text-x-generic", page() + L(5.5, 7.5, 10.5, 7.5) + L(5.5, 10.0, 10.5, 10.0) + L(5.5, 12.0, 8.5, 12.0))
    sym("x-office-document", page() + L(5.5, 7.5, 10.5, 7.5) + L(5.5, 10.0, 10.5, 10.0) + L(5.5, 12.0, 8.5, 12.0))
    sym("applications-office", page() + L(5.5, 7.5, 10.5, 7.5) + L(5.5, 10.0, 10.5, 10.0) + L(5.5, 12.0, 8.5, 12.0))
    sym("help-about", C(8, 8, 6.25) + D(8, 4.9, 1.0) + L(8, 7.5, 8, 11.25))
    sym("dialog-information", C(8, 8, 6.25) + D(8, 4.9, 1.0) + L(8, 7.5, 8, 11.25))
    sym("dialog-question", C(8, 8, 6.25) + A(8, 6.25, 2.0, 180, 400) + L(8 + 2.0 * math.cos(math.radians(40)), 6.25 + 2.0 * math.sin(math.radians(40)), 8, 9.0) + D(8, 11.5, 1.0))
    sym("dialog-warning", P([(8, 1.75), (14.5, 13.5), (1.5, 13.5)], closed=True, r=1.5) + L(8, 6.25, 8, 9.25) + D(8, 11.25, 0.95))
    sym("dialog-error", C(8, 8, 6.25) + L(8, 4.5, 8, 8.75) + D(8, 11.25, 0.95))
    sym("dialog-password", R(1.75, 4.25, 12.5, 7.5) + D(5.0, 8, 1.1) + D(8, 8, 1.1) + D(11.0, 8, 1.1))
    sym("caps-lock", P([(8, 2.0), (13.5, 7.75), (10.5, 7.75), (10.5, 10.5), (5.5, 10.5), (5.5, 7.75), (2.5, 7.75)], closed=True, r=0.75) + L(5.5, 13.5, 10.5, 13.5))
    sym("process-working", (1.0, A(8, 8, 6.0, -90, 30)), (0.35, C(8, 8, 6.0)))
    sym("starred", FP(star(8, 8.4, 6.6, 2.9)))
    sym("non-starred", P(star(8, 8.4, 6.25, 2.75), closed=True, r=0.5))
    sym("mark-location", A(8, 6.25, 4.75, 142.2, 397.8) + L(8 + 4.75 * math.cos(math.radians(37.8)), 6.25 + 4.75 * math.sin(math.radians(37.8)), 8, 14.25) +
        L(8 + 4.75 * math.cos(math.radians(142.2)), 6.25 + 4.75 * math.sin(math.radians(142.2)), 8, 14.25) + C(8, 6.25, 1.75))
    sym("mail-unread", R(1.75, 3.25, 12.5, 9.5) + P([(2.25, 4.0), (8, 8.75), (13.75, 4.0)], r=1.0))
    sym("media-eject", FP([(8, 3.0), (13.0, 9.0), (3.0, 9.0)]) + L(3.0, 12.75, 13.0, 12.75))

    # system
    sym("system-shutdown", A(8, 8.75, 5.5, -55, 235) + L(8, 1.75, 8, 7.5))
    sym("system-reboot", refresh())
    sym("system-log-out", P([(8.75, 2.75), (2.75, 2.75), (2.75, 13.25), (8.75, 13.25)], r=2.0) + arrow(6.5, 8, 13.75, 8, 3.25))
    sym("system-lock-screen", lock())
    sym("channel-secure", lock())
    sym("security-high", shield() + P([(5.5, 8.0), (7.25, 9.75), (10.5, 6.25)], r=0.5))
    sym("system-users", person(6.0, 2.0, 0.85) + C(11.5, 4.25, 1.75) + A(11.5, 12.0, 4.0, 255, 330))
    sym("avatar-default", C(8, 8, 6.25) + C(8, 6.5, 2.25) + A(8, 15.25, 5.25, 235, 305))
    sym("user-available", person())
    sym("emblem-system", gear(8, 8, 6.25, 4.5, 8, 1.75))
    sym("preferences-system", gear(8, 8, 6.25, 4.5, 8, 1.75))
    sym("software-update-available", C(8, 8, 6.25) + arrow(8, 4.5, 8, 11.25, 3.0))
    sym("software-update-urgent", A(8, 8.5, 5.75, -20, 290) + arrow(8, 5.0, 8, 11.5, 3.0) + D(12.75, 3.25, 2.25))
    sym("view-pin", P([(6.0, 1.75), (6.0, 6.25), (3.5, 8.75), (12.5, 8.75), (10.0, 6.25), (10.0, 1.75)], r=1.0) +
        L(4.75, 1.75, 11.25, 1.75) + L(8, 8.75, 8, 14.25))
    sym("package-x-generic", R(2.25, 6.0, 11.5, 8.0) + R(1.5, 2.25, 13.0, 3.75, 1.25) + L(6.5, 8.75, 9.5, 8.75))
    sym("application-x-addon", puzzle())
    sym("printer", R(1.75, 5.75, 12.5, 5.5) + P([(4.5, 5.75), (4.5, 2.0), (11.5, 2.0), (11.5, 5.75)], r=1.0) + R(4.5, 9.0, 7.0, 5.0, 1.0) + D(11.75, 7.75, 0.8))
    sym("computer", R(2.75, 2.75, 10.5, 7.5) + L(1.25, 12.75, 14.75, 12.75))
    sym("video-display", monitor())
    sym("preferences-desktop-screensaver", monitor() + moon(8, 6.5, 2.5, 1.5, -1.0, 2.0))
    sym("user-desktop", monitor() + D(5.0, 5.0, 0.8) + D(5.0, 7.75, 0.8))
    sym("drive-harddisk", drive())
    sym("drive-multidisk", drive(1.75, 5.25) + drive(9.0, 5.25))
    sym("drive-removable-media", R(1.75, 5.75, 12.5, 6.5) + L(4.5, 9.0, 6.5, 9.0) + D(11.0, 9.0, 0.9) + L(5.0, 3.0, 11.0, 3.0))
    sym("network-server", R(1.75, 1.75, 12.5, 5.0, 1.75) + R(1.75, 9.25, 12.5, 5.0, 1.75) + D(4.5, 4.25, 0.9) + D(4.5, 11.75, 0.9) + L(7.5, 4.25, 11.5, 4.25) + L(7.5, 11.75, 11.5, 11.75))
    sym("network-wired", R(5.75, 1.75, 4.5, 3.5, 1.0) + R(1.75, 10.75, 4.5, 3.5, 1.0) + R(9.75, 10.75, 4.5, 3.5, 1.0) +
        L(8, 5.25, 8, 8.0) + P([(4.0, 10.75), (4.0, 8.0), (12.0, 8.0), (12.0, 10.75)], r=1.0))
    sym("network-offline", R(5.75, 1.75, 4.5, 3.5, 1.0) + R(1.75, 10.75, 4.5, 3.5, 1.0) + R(9.75, 10.75, 4.5, 3.5, 1.0) +
        L(8, 5.25, 8, 8.0) + P([(4.0, 10.75), (4.0, 8.0), (12.0, 8.0), (12.0, 10.75)], r=1.0), slash())
    sym("network-wireless", *wifi(3))
    sym("network-wireless-signal-excellent", *wifi(3))
    sym("network-wireless-signal-good", *wifi(2))
    sym("network-wireless-signal-ok", *wifi(1))
    sym("network-wireless-signal-weak", *wifi(1)[:1], *[(0.35, l[1]) for l in wifi(0)[1:]])
    sym("network-wireless-signal-none", *wifi(0))
    sym("network-wireless-offline", *wifi(0), slash())
    sym("network-wireless-encrypted", *wifi(2)[:3], R(10.0, 11.0, 4.25, 3.25, 1.0) + A(12.125, 11.0, 1.25, 180, 360))
    sym("network-workgroup", R(5.75, 1.75, 4.5, 3.5, 1.0) + R(1.75, 10.75, 4.5, 3.5, 1.0) + R(9.75, 10.75, 4.5, 3.5, 1.0) +
        L(8, 5.25, 8, 8.0) + P([(4.0, 10.75), (4.0, 8.0), (12.0, 8.0), (12.0, 10.75)], r=1.0))
    sym("bluetooth-active", bluetooth())
    sym("bluetooth", bluetooth())
    sym("bluetooth-disabled", (0.35, bluetooth()), slash())
    sym("phone", R(4.25, 1.75, 7.5, 12.5) + L(7.0, 11.75, 9.0, 11.75))
    sym("input-keyboard", keyboard())
    sym("input-mouse", R(4.25, 1.75, 7.5, 12.5, 3.75) + L(8, 4.25, 8, 6.25))
    sym("input-touchpad", R(1.75, 2.75, 12.5, 10.5) + L(8, 10.0, 8, 13.25) + L(1.75, 10.0, 14.25, 10.0))
    sym("input-tablet", R(2.75, 1.75, 10.5, 12.5) + L(6.5, 11.75, 9.5, 11.75))
    sym("input-gaming", gamepad())
    sym("applications-games", gamepad())
    sym("applications-engineering", L(3.0, 13.0, 8.6, 7.4) + A(10.5, 5.5, 2.75, 0, 270))
    sym("applications-graphics", P([(3.0, 13.0), (3.5, 10.25), (10.75, 3.0), (13.0, 5.25), (5.75, 12.5)], closed=True, r=0.75) + L(9.25, 4.5, 11.5, 6.75))
    sym("applications-multimedia", R(1.75, 2.75, 12.5, 10.5) + FP([(6.5, 5.75), (10.5, 8.0), (6.5, 10.25)]))
    sym("camera-photo", P([(1.75, 5.0), (5.0, 5.0), (6.25, 3.0), (9.75, 3.0), (11.0, 5.0), (14.25, 5.0), (14.25, 13.0), (1.75, 13.0)], closed=True, r=1.75) + C(8, 8.75, 2.5))
    sym("image-x-generic", frame_pic())
    sym("preferences-desktop-wallpaper", frame_pic())
    sym("audio-x-generic", note_pair())
    sym("audio-speakers", R(3.25, 1.75, 9.5, 12.5) + C(8, 10.0, 2.25) + D(8, 4.75, 0.9))
    sym("audio-headphones", headphones())
    sym("audio-headset", headphones() + P([(12.75, 12.5), (12.75, 14.25), (8.5, 14.25)], r=1.25))
    sym("audio-input-microphone", mic())
    sym("microphone-sensitivity-high", mic())
    sym("microphone-sensitivity-medium", mic())
    sym("microphone-sensitivity-low", mic())
    sym("microphone-sensitivity-muted", (0.35, mic()), slash())
    sym("audio-volume-high", speaker(), *waves(3))
    sym("audio-volume-medium", speaker(), *waves(2))
    sym("audio-volume-low", speaker(), *waves(1))
    sym("audio-volume-muted", speaker() + L(10.0, 5.75, 14.0, 10.25) + L(14.0, 5.75, 10.0, 10.25))
    sym("media-playback-start", FP([(5.0, 3.0), (12.75, 8.0), (5.0, 13.0)]))
    sym("media-playback-pause", F(3.5, 2.75, 3.25, 10.5, 1.0) + F(9.25, 2.75, 3.25, 10.5, 1.0))
    sym("media-playback-stop", F(3.0, 3.0, 10.0, 10.0, 2.0))
    sym("media-record", D(8, 8, 5.0))
    sym("media-skip-forward", FP([(3.0, 3.75), (9.75, 8.0), (3.0, 12.25)]) + L(12.75, 3.0, 12.75, 13.0))
    sym("media-skip-backward", FP([(13.0, 3.75), (6.25, 8.0), (13.0, 12.25)]) + L(3.25, 3.0, 3.25, 13.0))
    sym("display-brightness", D(8, 8, 3.0) + sun(r=2.5, r0=5.0, r1=6.5)[2:])
    sym("keyboard-brightness", R(2.0, 9.0, 12.0, 5.0, 1.5) + L(5.5, 11.5, 10.5, 11.5) + L(8, 1.75, 8, 3.75) + L(3.5, 3.5, 4.75, 5.0) + L(12.5, 3.5, 11.25, 5.0))
    sym("night-light", moon(7.5, 8.5, 5.5, 3.0, -2.25, 4.5) + FP(sparkle(12.25, 3.75, 2.25), round_=False))
    sym("power-profile-balanced", gauge(270))
    sym("power-profile-performance", gauge(315))
    sym("power-profile-power-saver", leaf())
    for lvl, frac in (("empty", 0.0), ("caution", 0.12), ("low", 0.3), ("good", 0.65), ("full", 1.0)):
        sym(f"battery-{lvl}", *battery(frac, caution=lvl == "caution"))
        sym(f"battery-{lvl}-charging", *battery(frac, charging=True))
    sym("battery-full-charged", *battery(1.0, charging=True))
    sym("battery", *battery(0.5))
    sym("battery-missing", *battery(0.0, missing=True))
    sym("preferences-system-notifications", bell())
    sym("notifications-disabled", bell(), slash())
    sym("preferences-system-time", C(8, 8, 6.25) + P([(8, 4.5), (8, 8), (10.75, 9.75)], r=0.5))
    sym("preferences-desktop-locale", globe())
    sym("preferences-desktop-appearance", C(8, 8, 6.25) + D(5.0, 6.5, 1.1) + D(8, 4.5, 1.1) + D(11.0, 6.5, 1.1) + C(10.0, 10.5, 1.25))
    sym("preferences-desktop-accessibility", D(8, 3.0, 1.5) + L(3.0, 6.0, 13.0, 6.0) + L(8, 6.0, 8, 9.25) + P([(5.25, 14.0), (8, 9.25), (10.75, 14.0)], r=0.5))
    sym("x-office-calendar", calendar() + D(5.0, 9.25, 0.85) + D(8, 9.25, 0.85) + D(11.0, 9.25, 0.85) + D(5.0, 11.75, 0.85) + D(8, 11.75, 0.85))
    sym("folder", folder())
    sym("folder-publicshare", folder() + C(8, 7.75, 1.25, w=1.25) + A(8, 12.75, 2.5, 200, 340, w=1.25))
    sym("folder-documents", folder() + L(5.0, 8.25, 11.0, 8.25) + L(5.0, 10.75, 9.0, 10.75))
    sym("folder-download", folder() + arrow(8, 6.75, 8, 11.0, 2.5))
    sym("folder-music", folder() + D(7.0, 10.75, 1.25) + P([(8.0, 10.75), (8.0, 6.75), (10.25, 7.5)], r=0.5))
    sym("folder-pictures", folder() + P([(4.25, 11.25), (6.75, 8.5), (8.75, 10.25), (10.0, 9.0), (11.75, 11.0)], r=0.75))
    sym("folder-videos", folder() + FP([(6.75, 7.25), (10.25, 9.0), (6.75, 10.75)]))
    sym("user-home", house())

    # weather
    sym("weather-clear", sun())
    sym("weather-clear-night", moon(7.5, 8.5, 5.75, 3.25, -2.5, 4.75))
    sym("weather-few-clouds", A(6.0, 6.0, 2.75, 120, 330) + L(6.0, 0.75 + 0.75, 6.0, 1.75) + L(1.5, 6.0, 2.5, 6.0) + L(2.75, 2.75, 3.5, 3.5) + L(9.25, 2.75, 8.5, 3.5) +
        cloud([(5.25, 11.25, 2.25), (9.25, 9.75, 3.75), (12.5, 11.75, 1.75)], 13.5))
    sym("weather-few-clouds-night", moon(5.5, 5.75, 3.75, 2.25, -1.5, 3.0) +
        cloud([(5.25, 11.25, 2.25), (9.25, 9.75, 3.75), (12.5, 11.75, 1.75)], 13.5))
    sym("weather-overcast", cloud_big())
    sym("weather-fog", cloud_high() + L(2.0, 12.0, 12.0, 12.0) + L(4.0, 14.25, 14.0, 14.25))
    sym("weather-showers", cloud_high() + L(5.0, 11.75, 4.25, 14.25) + L(8.25, 11.75, 7.5, 14.25) + L(11.5, 11.75, 10.75, 14.25))
    sym("weather-showers-scattered", cloud_high() + L(5.5, 11.75, 4.75, 14.25) + L(10.5, 11.75, 9.75, 14.25))
    sym("weather-snow", cloud_high() + D(5.0, 12.5, 0.9) + D(8.25, 14.0, 0.9) + D(11.5, 12.5, 0.9))
    sym("weather-storm", cloud_high() + FP([(8.75, 10.5), (6.5, 13.0), (8.25, 13.0), (7.25, 15.0)], round_=False) + P([(8.75, 10.5), (6.5, 13.0), (8.25, 13.0), (7.25, 15.0)], r=0.25, w=1.25))

    # WolOS
    sym("wolos-assistant", FP(sparkle(7.0, 9.0, 5.75)) + FP(sparkle(12.5, 3.5, 2.25), round_=False))
    sym("wolos-effects", L(2.5, 13.5, 9.0, 7.0) + FP(sparkle(11.25, 4.75, 3.25), round_=False) + D(4.5, 4.0, 0.9) + D(13.0, 11.0, 0.9))
    sym("wolos-capture-screen", corners(1.75, 2.75, 12.5, 10.5, 3.25) + F(5.25, 6.0, 5.5, 4.0, 1.0))
    sym("wolos-capture-selection", dashed_rect(2.0, 2.75, 12.0, 10.5))
    sym("wolos-capture-window", corners(1.75, 2.75, 12.5, 10.5, 3.0) + R(4.75, 5.75, 6.5, 4.5, 1.0))
    sym("wolos-record-screen", R(1.75, 2.75, 12.5, 10.5) + capture_dot())
    sym("wolos-record-selection", dashed_rect(2.0, 2.75, 12.0, 10.5) + capture_dot())
    sym("wolos-chip", chip())
    sym("wolos-control-center", sliders())
    sym("wolos-contrast", C(8, 8, 6.25) + PIE(8, 8, 6.0, 270, 450))
    sym("wolos-dark-mode", moon(8.0, 8.0, 6.0, 3.25, -2.75, 5.0) + moon_solid(8.0, 8.0, 6.0, 3.25, -2.75, 5.0))
    sym("wolos-dock", R(1.75, 2.75, 12.5, 10.5) + F(4.5, 9.5, 7.0, 2.0, 1.0))
    sym("wolos-reduce-motion", C(10.25, 8, 3.5) + L(1.75, 5.5, 4.25, 5.5) + L(1.75, 8.0, 5.0, 8.0) + L(1.75, 10.5, 4.25, 10.5))
    sym("wolos-restore", A(8, 8, 5.75, 160, 450) + head(8 + 5.75 * math.cos(math.radians(160)), 8 + 5.75 * math.sin(math.radians(160)), 75, 3.0) + P([(8, 5.0), (8, 8.25), (10.25, 9.5)], r=0.5))
    sym("wolos-widgets", R(1.75, 1.75, 5.25, 5.25, 1.75) + R(9.0, 1.75, 5.25, 5.25, 1.75) + R(1.75, 9.0, 12.5, 5.25, 1.75))
    sym("wolos-kit", R(1.75, 5.0, 12.5, 9.0) + P([(5.5, 5.0), (5.5, 2.5), (10.5, 2.5), (10.5, 5.0)], r=1.0) + L(1.75, 8.75, 14.25, 8.75))
    # the console module (registry icon, docs/modules/modules.md): a window with a prompt
    sym("utilities-terminal", R(1.75, 2.75, 12.5, 10.5) + P([(4.75, 6.0), (6.75, 8.0), (4.75, 10.0)], r=0.5) + L(8.5, 10.0, 11.25, 10.0))


# ======================================================================================
# Rasteriser (symbolic): nonzero scanline with exact horizontal coverage, 4 sub-rows.
# ======================================================================================
def raster(contours, size, scale_from=16.0, ss=5):
    k = size / scale_from
    edges = []
    for c in contours:
        p = [(x * k, y * k) for x, y in c.points()]
        for i in range(len(p)):
            x0, y0 = p[i - 1]
            x1, y1 = p[i]
            if abs(y1 - y0) > 1e-12:
                edges.append((x0, y0, x1, y1))
    cov = [[0.0] * size for _ in range(size)]
    for row in range(size):
        line = cov[row]
        for s in range(ss):
            y = row + (s + 0.5) / ss
            xs = []
            for x0, y0, x1, y1 in edges:
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append((x0 + (y - y0) * (x1 - x0) / (y1 - y0), 1 if y1 > y0 else -1))
            if not xs:
                continue
            xs.sort()
            wnd = 0
            for i in range(len(xs) - 1):
                wnd += xs[i][1]
                if wnd == 0:
                    continue
                a, b = max(xs[i][0], 0.0), min(xs[i + 1][0], float(size))
                if b <= a:
                    continue
                ia, ib = int(a), int(b)
                if ia == ib:
                    line[ia] += (b - a) / ss
                    continue
                line[ia] += (ia + 1 - a) / ss
                for j in range(ia + 1, min(ib, size)):
                    line[j] += 1.0 / ss
                if ib < size:
                    line[ib] += (b - ib) / ss
    return [[min(v, 1.0) for v in r] for r in cov]


def render_symbolic(name, size):
    """Alpha grid of a symbolic icon (layers composited by opacity)."""
    out = [[0.0] * size for _ in range(size)]
    for op, contours, _cls in SYMBOLIC[name]:
        a = raster(contours, size)
        for y in range(size):
            o, r = out[y], a[y]
            for x in range(size):
                v = r[x] * op
                if v:
                    o[x] = v + o[x] * (1 - v)
    return out


def symbolic_svg(name):
    parts = []
    for op, contours, cls in SYMBOLIC[name]:
        d = "".join(c.d() for c in contours)
        attrs = ""
        if op < 1:
            attrs += f' opacity="{op:g}"'
        if cls:
            attrs += f' class="{cls}"'
        parts.append(f'<path d="{d}"{attrs}/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16" style="color:#2e3436">'
            f'<g fill="currentColor">{"".join(parts)}</g></svg>\n')


# ======================================================================================
# App icons: 24 x 24 cells
# ======================================================================================
N = 24
BAYER = [0, 32, 8, 40, 2, 34, 10, 42, 48, 16, 56, 24, 50, 18, 58, 26, 12, 44, 4, 36, 14, 46, 6, 38, 60, 28, 52, 20, 62, 30, 54, 22,
         3, 35, 11, 43, 1, 33, 9, 41, 51, 19, 59, 27, 49, 17, 57, 25, 15, 47, 7, 39, 13, 45, 5, 37, 63, 31, 55, 23, 61, 29, 53, 21]
bayer = lambda c, r: (BAYER[(r & 7) * 8 + (c & 7)] + 0.5) / 64

LIGHT_BG, DARK_BG = "#F5F5F7", "#1C1C1E"


def hx(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def tohex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, int(round(v)))) for v in rgb)


def mix(a, b, t):
    a, b = hx(a), hx(b)
    return tohex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = hx(c)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


EDGE_MIN = 1.3   # tile edge against both the light and the dark ground (tests/icons_v2.rs checks it)


def edge_color(c):
    """The tile colour nudged until it separates from both grounds."""
    for t in [i / 20 for i in range(21)]:
        e = mix(c, "#000000", t) if lum(c) > 0.3 else mix(c, "#FFFFFF", t)
        if contrast(e, LIGHT_BG) >= EDGE_MIN and contrast(e, DARK_BG) >= EDGE_MIN:
            return e
    return "#8E8E93"


class Cells:
    def __init__(self):
        self.c = {}

    def px(self, x, y, col):
        if 0 <= x < N and 0 <= y < N:
            self.c[(x, y)] = col

    def rect(self, x, y, w, h, col):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.px(i, j, col)

    def disc(self, cx, cy, r, col, r0=-1.0):
        for j in range(N):
            for i in range(N):
                d = math.hypot(i + 0.5 - cx, j + 0.5 - cy)
                if r0 < d <= r:
                    self.px(i, j, col)

    def line(self, x0, y0, x1, y1, col, w=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            for a in range(w):
                for b in range(w):
                    self.px(x0 + a, y0 + b, col)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def art(self, x, y, rows, pal):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in pal:
                    self.px(x + i, y + j, pal[ch])

    def clear(self, x, y, w=1, h=1):
        for j in range(y, y + h):
            for i in range(x, x + w):
                self.c.pop((i, j), None)


TILE = (1, 1, 22, 21)   # x, y, w, h in cells; the row under it is the shadow
TILE_R = 3.6


def in_tile(i, j):
    x, y, w, h = TILE
    cx, cy = i + 0.5, j + 0.5
    if not (x <= cx <= x + w and y <= cy <= y + h):
        return False
    qx = min(max(cx, x + TILE_R), x + w - TILE_R)
    qy = min(max(cy, y + TILE_R), y + h - TILE_R)
    return math.hypot(cx - qx, cy - qy) <= TILE_R


APPS = {}


def tile_shape():
    return {(i, j) for j in range(N) for i in range(N) if in_tile(i, j)}, None


def app(name, top, bottom, draw, kit=False, glyph_shadow=True, shape=tile_shape, ctx="apps"):
    """ctx apps: design/icons/apps/wolos-<name>.svg (+ PNGs); other contexts: icons/<ctx>/<name>.svg."""
    APPS[name] = (top, bottom, draw, kit, glyph_shadow, shape, ctx)


def compose(name):
    """name -> {(x, y): (hex, alpha, role)}."""
    top, bottom, draw, kit, gshadow, shape, _ctx = APPS[name]
    levels = [mix(top, bottom, k / 4) for k in range(5)]
    grid = {}
    tile_cells, post = shape()
    y0 = min(j for _, j in tile_cells)
    h = max(j for _, j in tile_cells) - y0 + 1
    for (i, j) in tile_cells:
        t = (j - y0) / (h - 1) * 4
        lo = min(int(t), 3)
        f = t - lo
        col = levels[lo + 1] if bayer(i, j) < f else levels[lo]
        grid[(i, j)] = (col, 1.0, "tile")
    if post:
        post(grid)
    if kit:
        # Kits: a lid band two cells deep, lighter (a box of things).
        for (i, j) in tile_cells:
            if j in (y0 + 3, y0 + 4):
                grid[(i, j)] = (mix(grid[(i, j)][0], "#FFFFFF", 0.22), 1.0, "tile")
            if j == y0 + 5:
                grid[(i, j)] = (mix(grid[(i, j)][0], "#000000", 0.18), 1.0, "tile")
    # bevel: first row lighter, last row darker
    for (i, j) in tile_cells:
        if (i, j - 1) not in tile_cells:
            grid[(i, j)] = (mix(grid[(i, j)][0], "#FFFFFF", 0.28), 1.0, "tile")
        elif (i, j + 1) not in tile_cells:
            grid[(i, j)] = (mix(grid[(i, j)][0], "#000000", 0.22), 1.0, "tile")
    # edge: every tile cell touching the outside (4-neighbourhood)
    for (i, j) in tile_cells:
        if any((i + a, j + b) not in tile_cells for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            grid[(i, j)] = (edge_color(grid[(i, j)][0]), 1.0, "edge")
    # shadow under the tile
    for (i, j) in tile_cells:
        if (i, j + 1) not in tile_cells and (i, j + 1) not in grid:
            grid[(i, j + 1)] = ("#000000", 0.20, "shadow")
    g = Cells()
    draw(g)
    if gshadow:
        for (i, j), col in g.c.items():
            k = (i, j + 1)
            if k not in g.c and k in tile_cells and grid[k][2] == "tile":
                grid[k] = (mix(grid[k][0], "#000000", 0.28), 1.0, "tile")
    for k, col in g.c.items():
        if k in tile_cells:
            grid[k] = (col, 1.0, "glyph")
    return grid


def app_svg(name):
    grid = compose(name)
    rows = []
    for (role, alpha) in (("shadow", None), ("tile", None), ("edge", None), ("glyph", None)):
        for j in range(N):
            i = 0
            while i < N:
                v = grid.get((i, j))
                if not v or v[2] != role:
                    i += 1
                    continue
                k = i
                while k + 1 < N and grid.get((k + 1, j)) == v:
                    k += 1
                cls = f' class="{role}"' if role in ("edge", "shadow") else ""
                op = f' fill-opacity="{v[1]:g}"' if v[1] < 1 else ""
                rows.append(f'<rect x="{i}" y="{j}" width="{k - i + 1}" height="1" fill="{v[0]}"{op}{cls}/>')
                i = k + 1
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="512" height="512" shape-rendering="crispEdges">'
            f'<title>{name}</title>{"".join(rows)}</svg>\n')


def render_app(name, size):
    """RGBA rows (floats 0..1, straight alpha) of an app icon at size px, box-filtered cells."""
    grid = compose(name)
    s = size / N
    # per output pixel: cells it covers with weights
    def weights(p):
        a, b = p / s, (p + 1) / s
        out = []
        c = int(a)
        while c < N and c < b:
            lo, hi = max(a, c), min(b, c + 1)
            if hi > lo:
                out.append((c, (hi - lo) / (b - a)))
            c += 1
        return out
    W = [weights(p) for p in range(size)]
    prem = {}
    for k, (col, al, _r) in grid.items():
        r, g, b = hx(col)
        prem[k] = (r / 255 * al, g / 255 * al, b / 255 * al, al)
    # horizontal pass per cell row
    hrows = []
    for j in range(N):
        row = []
        for p in range(size):
            acc = [0.0, 0.0, 0.0, 0.0]
            for c, wgt in W[p]:
                v = prem.get((c, j))
                if v:
                    for q in range(4):
                        acc[q] += v[q] * wgt
            row.append(acc)
        hrows.append(row)
    out = []
    for p in range(size):
        ws = W[p]
        if len(ws) == 1:
            out.append(hrows[ws[0][0]])
            continue
        row = []
        for x in range(size):
            acc = [0.0, 0.0, 0.0, 0.0]
            for c, wgt in ws:
                v = hrows[c][x]
                for q in range(4):
                    acc[q] += v[q] * wgt
            row.append(acc)
        out.append(row)
    return out


# ---- app glyphs ----------------------------------------------------------------------
WHITE = "#FFFFFF"
INK = "#1C1C1E"
VIOLET = "#7C5CFF"


def g_files(g):
    g.rect(4, 6, 7, 2, "#D4E8FF")
    g.rect(4, 8, 16, 11, "#D4E8FF")
    g.rect(4, 10, 16, 9, WHITE)
    g.rect(9, 13, 6, 1, "#9CC8FF")


def g_mail(g):
    g.rect(4, 7, 16, 11, WHITE)
    for k in range(7):
        g.px(4 + k, 7 + k, "#2F7BF0")
        g.px(19 - k, 7 + k, "#2F7BF0")
    g.px(11, 14, "#2F7BF0")
    g.px(12, 14, "#2F7BF0")


def g_calendar(g):
    g.rect(4, 4, 16, 4, "#FF3B30")
    g.px(7, 3, "#8E8E93"), g.px(16, 3, "#8E8E93")
    for r in range(4):
        for c in range(5):
            x, y = 5 + c * 3, 10 + r * 2.5
            col = VIOLET if (r, c) == (1, 2) else "#C7C7CC"
            g.rect(x, int(y), 2, 2 if (r, c) == (1, 2) else 1, col)


def g_notes(g):
    g.rect(5, 4, 14, 3, "#E8A400")
    g.rect(5, 7, 14, 13, "#FFF8DC")
    for y in (10, 13, 16):
        g.rect(7, y, 10 if y != 16 else 6, 1, "#B8962E")


def g_photos(g):
    cols = ["#FF9500", "#FFCC00", "#9BE15D", "#34C759", "#32ADE6", "#5856D6", "#AF52DE", "#FF3B30"]
    for k, c in enumerate(cols):
        t = math.radians(-90 + 45 * k)
        g.disc(12 + 4.6 * math.cos(t), 12 + 4.6 * math.sin(t), 2.7, c)
    g.disc(12, 12, 1.6, WHITE)


def g_settings(g):
    dark, light = "#2F333B", "#D5D8DE"
    for k in range(8):
        t = math.radians(22.5 + 45 * k)
        cx, cy = 12 + 6.6 * math.cos(t), 12 + 6.6 * math.sin(t)
        g.rect(int(cx - 1), int(cy - 1), 2, 2, dark)
    g.disc(12, 12, 6.2, dark)
    g.disc(12, 12, 3.6, light)
    g.disc(12, 12, 1.8, dark)


def g_store(g):
    g.disc(12, 9, 4.0, WHITE, 2.6)
    g.clear(0, 9, 24, 15)
    g.rect(5, 9, 14, 11, WHITE)
    g.rect(8, 11, 1, 2, "#7C5CFF"), g.rect(15, 11, 1, 2, "#7C5CFF")
    g.rect(9, 15, 6, 1, "#B8A6FF")


def g_terminal(g):
    green = "#3CE37A"
    for k in range(3):
        g.rect(6 + k, 8 + k, 2, 1, green)
        g.rect(6 + k, 14 - k, 2, 1, green)
    g.rect(11, 14, 6, 2, WHITE)
    g.px(5, 5, "#FF5F57"), g.px(7, 5, "#FEBC2E"), g.px(9, 5, "#28C840")


def g_browser(g):
    g.disc(12, 12, 7.6, WHITE)
    g.disc(12, 12, 6.6, "#E6F2FF", 6.0)
    red, grey = "#FF3B30", "#9AA4B8"
    for k in range(5):
        g.rect(12 + k, 11 - k, 1, 1, red), g.rect(11 + k, 11 - k, 1, 1, red)
        g.rect(11 - k, 12 + k, 1, 1, grey), g.rect(12 - k, 12 + k, 1, 1, grey)
    g.rect(11, 11, 2, 2, INK)


def g_installer(g):
    # arrow into a tray, the WolOS ears on the arrow
    g.rect(9, 3, 2, 3, WHITE), g.rect(13, 3, 2, 3, WHITE)
    g.rect(10, 6, 4, 6, WHITE)
    for k in range(4):
        g.rect(7 + k, 11 + k, 10 - 2 * k, 1, WHITE)
    g.rect(5, 16, 2, 4, "#D9D0FF"), g.rect(17, 16, 2, 4, "#D9D0FF"), g.rect(5, 19, 14, 2, "#D9D0FF")


def g_control_center(g):
    g.rect(5, 6, 14, 5, VIOLET)
    g.rect(6, 5, 12, 7, VIOLET)
    g.disc(15.5, 8.5, 2.2, WHITE)
    g.rect(5, 14, 14, 5, "#6B6F7B")
    g.rect(6, 13, 12, 7, "#6B6F7B")
    g.disc(8.5, 16.5, 2.2, WHITE)


def g_plugin_maker(g):
    g.art(5, 5, [
        "...wwww.....",
        "...wwww.....",
        "....ww......",
        "wwwwwwwwww..",
        "wwwwwwwwww..",
        "wwwwwwwwww..",
        ".wwwwwwwwwww",
        ".wwwwwwwwwww",
        "wwwwwwwwww..",
        "wwwwwwwwww..",
        "wwwwwwwwww..",
        "wwwwwwwwww..",
    ], {"w": WHITE})
    g.art(15, 3, ["..y..", "..y..", "yyyyy", "..y..", "..y.."], {"y": "#FFD60A"})


def g_launcher(g):
    cols = ["#FF6A88", "#FFB340", "#3CD070", "#40A8FF", VIOLET, "#FF5E3A", "#30D0C0", "#B07CFF", "#FFD60A"]
    for k, c in enumerate(cols):
        g.rect(5 + (k % 3) * 5, 5 + (k // 3) * 5, 4, 4, c)


def g_music(g):
    g.rect(9, 5, 2, 11, WHITE)
    g.rect(16, 4, 2, 11, WHITE)
    g.rect(9, 4, 9, 2, WHITE)
    g.disc(7.5, 16.5, 2.6, WHITE)
    g.disc(14.5, 15.5, 2.6, WHITE)


def g_calculator(g):
    for r in range(3):
        for c in range(3):
            col = "#FF9F0A" if c == 2 else ("#A5A5AA" if r == 0 else "#5A5A60")
            g.rect(5 + c * 5, 5 + r * 5, 4, 4, col)


def g_games(g):
    g.rect(5, 8, 14, 7, "#E9EEF7")
    g.rect(4, 10, 16, 7, "#E9EEF7")
    g.clear(9, 15, 6, 2)
    g.rect(6, 11, 3, 1, "#2B3B5C"), g.rect(7, 10, 1, 3, "#2B3B5C")
    g.px(15, 10, "#FF375F"), g.px(17, 12, "#30D158"), g.px(13, 12, "#0A84FF")


def g_text_editor(g):
    g.rect(5, 4, 12, 16, WHITE)
    for y, w in ((7, 8), (10, 7), (13, 8), (16, 5)):
        g.rect(7, y, w, 1, "#8A90A0")
    for k in range(6):
        g.rect(13 + k, 18 - k, 2, 2, VIOLET)


def g_system_monitor(g):
    pts = [(4, 15), (7, 15), (9, 10), (11, 18), (13, 7), (15, 15), (19, 15)]
    for (a, b), (c, d) in zip(pts, pts[1:]):
        g.line(a, b, c, d, "#3CE37A")


def g_trash(g):
    g.rect(5, 6, 14, 2, "#E5E5EA")
    g.rect(10, 4, 4, 2, "#E5E5EA")
    g.rect(6, 9, 12, 11, "#E5E5EA")
    for x in (9, 12, 15):
        g.rect(x - 1 if x != 12 else 11, 11, 1 if x != 12 else 2, 7, "#9A9AA2")


def g_kit_craft(g):
    # pencil on a diagonal
    for k in range(9):
        g.rect(6 + k, 17 - k, 3, 2, "#FFD60A")
    g.rect(15, 7, 3, 2, "#FF8FB1"), g.rect(16, 6, 2, 1, "#FF8FB1")
    g.rect(5, 18, 2, 2, "#FFE7B3"), g.px(4, 20, INK)


def g_kit_codecs(g):
    g.rect(4, 8, 16, 11, "#22222A")
    for x in range(5, 20, 3):
        g.px(x, 9, WHITE), g.px(x, 17, WHITE)
    for k in range(3):
        g.rect(10, 11 + k, 2 + 2 * k, 1, WHITE)
        g.rect(10, 15 - k, 2 + 2 * k, 1, WHITE)
    g.rect(10, 13, 6, 1, WHITE)


def g_kit_dev(g):
    c = WHITE
    for k in range(4):
        g.rect(8 - k, 10 + k, 2, 1, c), g.rect(8 - k, 16 - k, 2, 1, c)
        g.rect(14 + k, 10 + k, 2, 1, c), g.rect(14 + k, 16 - k, 2, 1, c)
    g.rect(5, 13, 1, 1, c), g.rect(18, 13, 1, 1, c)
    g.line(13, 9, 10, 18, "#B8A6FF")


def g_kit_ai(g):
    c = WHITE
    g.art(5, 7, [
        "......w......",
        "......w......",
        ".....www.....",
        ".....www.....",
        "....wwwww....",
        "wwwwwwwwwwwww",
        "....wwwww....",
        ".....www.....",
        ".....www.....",
        "......w......",
        "......w......",
    ], {"w": c})
    g.art(16, 6, [".y.", "yyy", ".y."], {"y": "#FFD60A"})


def g_kit_creative(g):
    g.disc(11.5, 13.5, 6.3, "#FFF3E0")
    g.disc(15.5, 16.5, 1.6, "#9C3BD6")
    for (x, y, c) in ((8, 11, "#FF3B30"), (11, 9, "#FFCC00"), (15, 11, "#34C759"), (8, 15, "#0A84FF")):
        g.rect(x - 1, y - 1, 2, 2, c)


def g_kit_gaming(g):
    g.rect(5, 10, 14, 7, WHITE)
    g.rect(4, 12, 16, 7, WHITE)
    g.clear(9, 17, 6, 2)
    g.rect(6, 13, 3, 1, "#0F8A47"), g.rect(7, 12, 1, 3, "#0F8A47")
    g.px(16, 12, "#FF375F"), g.px(17, 14, "#0A84FF")


def build_apps():
    app("files", "#5DB2FF", "#1B5FD9", g_files)
    app("mail", "#6AC8FF", "#1A6CEB", g_mail)
    app("calendar", "#FFFFFF", "#E4E4EA", g_calendar, glyph_shadow=False)
    app("notes", "#FFE07A", "#F5B400", g_notes)
    app("photos", "#FFFFFF", "#E6E6EE", g_photos, glyph_shadow=False)
    app("settings", "#B9BEC7", "#5E6470", g_settings)
    app("software", "#A48DFF", "#5434E0", g_store)
    app("terminal", "#3A3A44", "#121216", g_terminal)
    app("browser", "#62D0FF", "#2463EB", g_browser)
    app("installer", "#8E70FF", "#3B22B0", g_installer)
    app("control-center", "#5A5E6A", "#24262E", g_control_center)
    app("plugin-maker", "#3DD6A8", "#0E8466", g_plugin_maker)
    app("launcher", "#4A4E5A", "#1E2027", g_launcher)
    app("music", "#FF7A93", "#E31F4C", g_music)
    app("calculator", "#4A4A50", "#1C1C20", g_calculator)
    app("games", "#3A4F78", "#101A30", g_games)
    app("text-editor", "#F2F2F6", "#D6D8E0", g_text_editor)
    app("system-monitor", "#33333C", "#101014", g_system_monitor)
    app("trash", "#9A9AA4", "#5A5A64", g_trash)
    app("kit-craft-suite", "#FFA94D", "#E2560B", g_kit_craft, kit=True)
    app("kit-codecs", "#FF6F91", "#C21858", g_kit_codecs, kit=True)
    app("kit-dev", "#33466E", "#0E1628", g_kit_dev, kit=True)
    app("kit-ai", "#9B85FF", "#3E6BF0", g_kit_ai, kit=True)
    app("kit-creative", "#E58CFF", "#8A2BD9", g_kit_creative, kit=True)
    app("kit-gaming", "#45D477", "#0E8243", g_kit_gaming, kit=True)
    build_places()


# ---- places, devices, mimetypes: the same cells, other silhouettes ----------------------
def rect_cells(x, y, w, h):
    return {(i, j) for j in range(y, y + h) for i in range(x, x + w)}


def folder_shape():
    back = rect_cells(2, 4, 8, 2) | rect_cells(2, 5, 20, 3)
    front = rect_cells(2, 8, 20, 12)
    cells = back | front
    for c in ((2, 4), (9, 4), (2, 19), (21, 19), (21, 5)):
        cells.discard(c)

    def post(grid):
        for (i, j), (col, a, r) in list(grid.items()):
            if j < 8:
                grid[(i, j)] = (mix(col, "#000000", 0.16), a, r)
            elif j == 8:
                grid[(i, j)] = (mix(col, "#FFFFFF", 0.35), a, r)
    return cells, post


def page_shape():
    cells = {(i, j) for (i, j) in rect_cells(5, 2, 14, 20) if i - j <= 12}
    cells -= {(5, 2), (5, 21), (18, 21)}

    def post(grid):
        for (i, j) in list(grid):
            if 14 <= i <= 18 and 2 <= j <= 6 and (i - 14) <= (j - 2):
                grid[(i, j)] = ("#D2D6E0", 1.0, "tile")
    return cells, post


def drive_shape():
    cells = rect_cells(2, 7, 20, 11) - {(2, 7), (21, 7), (2, 17), (21, 17)}
    return cells, None


def stick_shape():
    body = rect_cells(7, 7, 10, 14) - {(7, 7), (16, 7), (7, 20), (16, 20)}
    plug = rect_cells(9, 2, 6, 5)

    def post(grid):
        for (i, j) in list(grid):
            if j < 7:
                dark = (i, j) in ((10, 3), (13, 3), (10, 4), (13, 4))
                grid[(i, j)] = ("#6E737D" if dark else "#C7CBD3", 1.0, "tile")
    return body | plug, post


def globe_shape():
    return {(i, j) for j in range(N) for i in range(N) if math.hypot(i + 0.5 - 12, j + 0.5 - 12) <= 9.6}, None


PAPER = ({(7, 0), (8, 0), (13, 0), (14, 0), (15, 0)} | rect_cells(6, 1, 5, 1) | rect_cells(12, 1, 6, 1)
         | rect_cells(5, 2, 14, 3))


def bin_full_shape():
    cells, post = bin_shape()
    cells = (cells - rect_cells(10, 2, 4, 2)) | PAPER

    def post2(grid):
        post(grid)
        for (i, j) in PAPER:
            if (i, j) in grid:
                col = "#FFD60A" if i <= 9 else ("#5DB2FF" if i >= 15 else "#FFFFFF")
                if bayer(i, j) > 0.72:
                    col = mix(col, "#000000", 0.25)
                grid[(i, j)] = (col, 1.0, "tile")
    return cells, post2


def bin_shape():
    lid = rect_cells(4, 4, 16, 2)
    knob = rect_cells(10, 2, 4, 2)
    body = {(i, j) for j in range(6, 21) for i in range(5 + (j - 6) // 7, 19 - (j - 6) // 7)}

    def post(grid):
        for (i, j), (col, a, r) in list(grid.items()):
            if j < 6:
                grid[(i, j)] = (mix(col, "#FFFFFF", 0.2), a, r)
    return lid | knob | body, post


FOLDER = ("#74BDFF", "#2F7FEF")
EMBOSS = "#1A4FB8"


EMBOSS_LIGHT = "#B8DCFF"


def emboss(art, x=7, y=11):
    """Glyph pressed into the folder front: dark cells with a light lip under them."""
    def d(g):
        g.art(x, y, art, {"#": EMBOSS})
        dark = set(g.c)
        for (i, j) in dark:
            if (i, j + 1) not in dark:
                g.px(i, j + 1, EMBOSS_LIGHT)
    return d


GLYPH_ART = {
    "folder": [],
    "folder-documents": ["..######..", "..#....#..", "..#.##.#..", "..#....#..", "..#.##.#..", "..######.."],
    "folder-download": ["....##....", "....##....", "..######..", "...####...", "....##....", ".########."],
    "folder-music": ["....####..", "....#..#..", "....#..#..", "..###.##..", "..###.##..", ".........."],
    "folder-pictures": ["......##..", "......##..", "...#......", "..###..#..", ".#####.##.", "##########"],
    "folder-publicshare": ["....##....", "...####...", "....##....", "..######..", ".########.", ".........."],
    "folder-templates": ["..##.##...", "..#...#...", "..........", "..#...#...", "..##.##...", ".........."],
    "folder-videos": ["...#......", "...###....", "...#####..", "...###....", "...#......", ".........."],
    "user-home": ["....##....", "...####...", "..######..", ".########.", "..##..##..", "..##..##.."],
    "user-desktop": [".########.", ".#......#.", ".#......#.", ".########.", "....##....", "..######.."],
}


def page_glyph(kind):
    def d(g):
        grey = "#B9BEC9"
        if kind == "pdf":
            g.rect(6, 12, 12, 7, "#E5372C")
            g.art(7, 13, ["##.##..###", "#.##.#.#..", "##.#.#.##.", "#..#.#.#..", "#..##..#.."], {"#": WHITE})
        elif kind == "exec":
            g.disc(12, 14, 4.2, "#6E737D")
            g.disc(12, 14, 1.6, WHITE)
            for a in range(0, 360, 45):
                t = math.radians(a)
                g.px(int(12 + 4.6 * math.cos(t)), int(14 + 4.6 * math.sin(t)), "#6E737D")
        elif kind == "audio":
            g.rect(11, 9, 2, 8, "#FF2D55")
            g.rect(13, 9, 3, 2, "#FF2D55")
            g.disc(10.5, 17, 2.1, "#FF2D55")
        elif kind == "image":
            g.rect(7, 10, 10, 9, "#DCEBFF")
            g.disc(14.5, 12.5, 1.4, "#FFB800")
            for k in range(5):
                g.rect(8 + k, 17 - k, 1, k + 1, "#34C759")
                g.rect(12 + k, 14 + k // 2, 1, 4 - k // 2, "#2AA34A")
        elif kind == "package":
            g.rect(7, 10, 10, 8, "#C8935A")
            g.rect(7, 10, 10, 2, "#E0AE76")
            g.rect(11, 10, 2, 4, "#8A5A2B")
        elif kind == "video":
            g.rect(7, 10, 10, 8, "#2C2C34")
            g.art(10, 11, ["#...", "##..", "###.", "##..", "#..."], {"#": WHITE})
        elif kind == "document":
            g.rect(7, 9, 4, 4, "#2F7BF0")
            for y in (14, 16, 18):
                g.rect(7, y, 10, 1, "#7FA8E8")
            g.rect(12, 10, 5, 1, "#7FA8E8")
            g.rect(12, 12, 5, 1, "#7FA8E8")
        elif kind == "presentation":
            g.rect(7, 10, 10, 7, "#FF9500")
            g.rect(9, 13, 2, 3, WHITE)
            g.rect(12, 12, 2, 4, WHITE)
            g.rect(15, 11, 1, 5, WHITE)
        elif kind == "spreadsheet":
            for r in range(5):
                for c in range(3):
                    g.rect(7 + c * 4, 9 + r * 2, 3, 1, "#34C759" if r == 0 else "#9ADBA9")
        else:  # generic text
            for y, w in ((9, 8), (11, 10), (13, 9), (15, 10), (17, 6)):
                g.rect(7, y, w, 1, grey)
    return d


def g_globe(g):
    for j in range(N):
        for i in range(N):
            dx, dy = i + 0.5 - 12, j + 0.5 - 12
            if math.hypot(dx, dy) > 9.6:
                continue
            meridian = 4.6 * math.sqrt(max(0.0, 1 - (dy / 9.6) ** 2))
            if j in (7, 12, 16) or abs(dx) < 0.6 or abs(abs(dx) - meridian) < 0.5:
                g.px(i, j, "#D6ECFF")


def g_bin(full):
    def d(g):
        for x in (8, 11, 14):
            g.rect(x, 9, 2 if x == 11 else 1, 9, "#6E737D")
        if full:
            pass
    return d


def g_disk(g):
    g.rect(4, 13, 9, 1, "#6E737D")
    g.rect(17, 12, 2, 2, "#34C759")


def g_stick(g):
    g.rect(10, 11, 4, 2, "#8B6CFF")
    g.rect(10, 15, 4, 1, "#6E737D")


def build_places():
    for n, art in GLYPH_ART.items():
        app(n, *FOLDER, emboss(art), shape=folder_shape, ctx="places", glyph_shadow=False)
    app("network-workgroup", "#62D0FF", "#2463EB", g_globe, shape=globe_shape, ctx="places")
    app("user-trash", "#C9CCD3", "#7D818B", g_bin(False), shape=bin_shape, ctx="places")
    app("user-trash-full", "#C9CCD3", "#7D818B", g_bin(True), shape=bin_full_shape, ctx="places")
    app("drive-harddisk", "#D9DCE2", "#8D929C", g_disk, shape=drive_shape, ctx="devices")
    app("drive-removable-media", "#5A5E6A", "#24262E", g_stick, shape=stick_shape, ctx="devices")
    for n, kind in (("application-pdf", "pdf"), ("application-x-executable", "exec"), ("application-x-generic", "generic"),
                    ("audio-x-generic", "audio"), ("image-x-generic", "image"), ("package-x-generic", "package"),
                    ("text-x-generic", "generic"), ("video-x-generic", "video"), ("x-office-document", "document"),
                    ("x-office-presentation", "presentation"), ("x-office-spreadsheet", "spreadsheet")):
        app(n, "#FFFFFF", "#ECEEF3", page_glyph(kind), shape=page_shape, ctx="mimetypes", glyph_shadow=False)


# Names other apps and desktop files ask for, installed as symlinks (install.sh, aliases.tsv).
ALIASES = {
    "files": "org.gnome.Nautilus system-file-manager thunar org.xfce.thunar pcmanfm nemo",
    "terminal": "utilities-terminal org.gnome.Terminal foot kitty Alacritty org.wezfurlong.wezterm xfce4-terminal com.mitchellh.ghostty",
    "browser": "helium firefox web-browser org.mozilla.firefox chromium librewolf epiphany",
    "settings": "preferences-system org.gnome.Settings gnome-control-center nwg-look org.wolos.settings",
    "software": "system-software-install org.gnome.Software octopkg org.wolos.store wolos-store",
    "music": "multimedia-audio-player org.gnome.Music audacious rhythmbox elisa io.bassi.Amberol",
    "photos": "multimedia-photo-viewer org.gnome.eog org.gnome.Loupe org.gnome.Shotwell ristretto",
    "notes": "accessories-notes org.gnome.gitlab.cheywood.Iotas xpad org.gnome.Gnote",
    "calendar": "office-calendar org.gnome.Calendar",
    "mail": "internet-mail mail-client thunderbird org.mozilla.Thunderbird evolution org.gnome.Geary",
    "calculator": "accessories-calculator org.gnome.Calculator galculator qalculate-gtk",
    "games": "steam applications-games lutris",
    "text-editor": "accessories-text-editor org.gnome.TextEditor org.gnome.gedit mousepad code codium",
    "system-monitor": "utilities-system-monitor org.gnome.SystemMonitor htop btop",
    "trash": "user-trash user-trash-full",
    "launcher": "system-search fuzzel",
    "installer": "org.wolos.installer",
    "control-center": "org.wolos.control-center",
    "plugin-maker": "org.wolos.plugin-maker",
}


# ======================================================================================
# PNG
# ======================================================================================
def APP_NAMES():
    return [n for n in APPS if APPS[n][6] == "apps"]


def icon_path(n):
    ctx = APPS[n][6]
    if ctx == "apps":
        return os.path.join(APP_DIR, f"wolos-{n}.svg")
    return os.path.join(DESIGN, "icons", ctx, f"{n}.svg")


def png_bytes(w, h, rows):
    """rows: list of list of (r, g, b, a) 0..255 ints."""
    raw = bytearray()
    for r in rows:
        raw.append(0)
        for px in r:
            raw.extend(px)
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def straight(acc):
    a = acc[3]
    if a <= 1e-6:
        return (0, 0, 0, 0)
    return tuple(int(round(min(1.0, acc[q] / a) * 255)) for q in range(3)) + (int(round(min(a, 1.0) * 255)),)


# design/icons laid out as a theme (kit/style.rs links design/icons/* under a temp WolOS dir in
# dev and golden runs, so the repo's icons win over Adwaita's of the same name).
DEV_THEME = """[Icon Theme]
Name=WolOS
Comment=WolOS icons from the repo (dev and golden renders), design/tools/icons.py
Inherits=Adwaita,hicolor
Directories=apps,places,devices,mimetypes,symbolic

[apps]
Size=128
MinSize=16
MaxSize=1024
Context=Applications
Type=Scalable

[places]
Size=128
MinSize=16
MaxSize=1024
Context=Places
Type=Scalable

[devices]
Size=128
MinSize=16
MaxSize=1024
Context=Devices
Type=Scalable

[mimetypes]
Size=128
MinSize=16
MaxSize=1024
Context=MimeTypes
Type=Scalable

[symbolic]
Size=16
MinSize=16
MaxSize=512
Context=Status
Type=Scalable
"""

INDEX_THEME = """[Icon Theme]
Name=WolOS
Comment=WolOS (Wonderland OS) icons: one geometry, design/tools/icons.py
Inherits=Adwaita,hicolor
Directories=48x48/apps,128x128/apps,512x512/apps,scalable/apps,scalable/places,scalable/devices,scalable/mimetypes,symbolic/status,symbolic/actions

[48x48/apps]
Size=48
Context=Applications
Type=Fixed

[128x128/apps]
Size=128
Context=Applications
Type=Fixed

[512x512/apps]
Size=512
Context=Applications
Type=Fixed

[scalable/apps]
Size=128
MinSize=16
MaxSize=1024
Context=Applications
Type=Scalable

[scalable/places]
Size=128
MinSize=16
MaxSize=1024
Context=Places
Type=Scalable

[scalable/devices]
Size=128
MinSize=16
MaxSize=1024
Context=Devices
Type=Scalable

[scalable/mimetypes]
Size=128
MinSize=16
MaxSize=1024
Context=MimeTypes
Type=Scalable

[symbolic/status]
Size=16
MinSize=16
MaxSize=512
Context=Status
Type=Scalable

[symbolic/actions]
Size=16
MinSize=16
MaxSize=512
Context=Actions
Type=Scalable
"""


def write(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode, **({} if mode == "wb" else {"newline": "\n", "encoding": "utf-8"})) as f:
        f.write(data)


def sheet(path):
    """Contact sheet: app icons at 128 on light and 48 on dark, symbolics at 32 and 16 both ways."""
    names = sorted(APPS)
    syms = sorted(SYMBOLIC)
    W = 1100
    cols128 = W // 136
    rows128 = -(-len(names) // cols128)
    cols32 = W // 44
    rows32 = -(-len(syms) // cols32)
    cols16 = W // 24
    rows16 = -(-len(syms) // cols16)
    Hh = 16 + rows128 * 140 + 16 + 64 + 16 + rows32 * 44 * 2 + 16 + rows16 * 24 * 2 + 16
    light, dark = hx(LIGHT_BG), hx(DARK_BG)
    img = [[list(light) for _ in range(W)] for _ in range(Hh)]

    def band(y0, y1, col):
        for y in range(y0, min(y1, Hh)):
            for x in range(W):
                img[y][x] = list(col)

    def blit_rgba(px, py, rows):
        for j, r in enumerate(rows):
            if not (0 <= py + j < Hh):
                continue
            for i, acc in enumerate(r):
                a = acc[3]
                if a <= 0 or not (0 <= px + i < W):
                    continue
                d = img[py + j][px + i]
                for q in range(3):
                    d[q] = acc[q] * 255 + d[q] * (1 - a)

    def blit_alpha(px, py, al, col):
        for j, r in enumerate(al):
            for i, a in enumerate(r):
                if a <= 0:
                    continue
                d = img[py + j][px + i]
                for q in range(3):
                    d[q] = col[q] * a + d[q] * (1 - a)

    y = 16
    order = []
    for k, n in enumerate(names):
        blit_rgba(8 + (k % cols128) * 136, y + (k // cols128) * 140, render_app(n, 128))
        order.append(f"app128 r{k // cols128} c{k % cols128} {n}")
    y += rows128 * 140 + 16
    band(y - 8, y + 72, dark)
    for k, n in enumerate(names):
        blit_rgba(8 + k * 52, y + 8, render_app(n, 48))
    y += 64 + 24
    for k, n in enumerate(syms):
        al = render_symbolic(n, 32)
        blit_alpha(8 + (k % cols32) * 44, y + (k // cols32) * 44, al, hx(INK))
        order.append(f"sym r{k // cols32} c{k % cols32} {n}")
    y += rows32 * 44
    band(y, y + rows32 * 44, dark)
    for k, n in enumerate(syms):
        blit_alpha(8 + (k % cols32) * 44, y + 6 + (k // cols32) * 44, render_symbolic(n, 32), hx("#F5F5F7"))
    y += rows32 * 44 + 16
    for k, n in enumerate(syms):
        blit_alpha(8 + (k % cols16) * 24, y + (k // cols16) * 24, render_symbolic(n, 16), hx(INK))
    y += rows16 * 24
    band(y, y + rows16 * 24 + 8, dark)
    for k, n in enumerate(syms):
        blit_alpha(8 + (k % cols16) * 24, y + 4 + (k // cols16) * 24, render_symbolic(n, 16), hx("#F5F5F7"))
    rows = [[tuple(int(max(0, min(255, round(v)))) for v in p) + (255,) for p in r] for r in img]
    write(path, png_bytes(W, Hh, rows))
    write(os.path.splitext(path)[0] + ".txt", "\n".join(order) + "\n")


def main(argv):
    build_symbolic()
    build_apps()
    overlay = os.path.normpath(os.path.join(DESIGN, "..", "desktop", "overlay"))
    sheet_out = None
    only = None
    a = list(argv)
    while a:
        k = a.pop(0)
        if k == "--sheet":
            sheet_out = a.pop(0)
        elif k == "--overlay":
            overlay = a.pop(0)
        elif k == "--only-sheet":
            only = "sheet"
        else:
            sys.exit(f"icons.py: unknown argument {k}")
    if only != "sheet":
        os.makedirs(SYM_DIR, exist_ok=True)
        for f in os.listdir(SYM_DIR):
            stem = f[:-4] if f.endswith(".svg") else None
            if (stem and stem not in SYMBOLIC and stem not in KEEP_SYMBOLIC) or f == "ADWAITA.tsv":
                os.remove(os.path.join(SYM_DIR, f))
        for n in SYMBOLIC:
            write(os.path.join(SYM_DIR, n + ".svg"), symbolic_svg(n))
        for n in APPS:
            write(icon_path(n), app_svg(n))
        write(os.path.join(DESIGN, "icons", "index.theme"), INDEX_THEME)
        write(os.path.join(DESIGN, "icons", "dev.theme"), DEV_THEME)
        write(os.path.join(DESIGN, "icons", "aliases.tsv"),
              "# wolos-<icon>\tfreedesktop/app icon names (tab-separated). install.sh symlinks these. Generated by tools/icons.py.\n" +
              "".join(f"{k}\t{v}\n" for k, v in ALIASES.items()))
        theme = os.path.join(overlay, "usr", "share", "icons", "WolOS")
        if os.path.isdir(os.path.dirname(os.path.dirname(theme))):
            write(os.path.join(theme, "index.theme"), INDEX_THEME)
            for size in PNG_SIZES:
                for n in APP_NAMES():
                    rows = [[straight(p) for p in r] for r in render_app(n, size)]
                    write(os.path.join(theme, f"{size}x{size}", "apps", f"wolos-{n}.png"), png_bytes(size, size, rows))
        print(f"icons.py: {len(SYMBOLIC)} symbolic, {len(APP_NAMES())} app icons x {len(PNG_SIZES)} PNG sizes, "
              f"{len(APPS) - len(APP_NAMES())} places/devices/mimetypes")
    if sheet_out:
        sheet(sheet_out)
        print(f"icons.py: sheet {sheet_out}")


if __name__ == "__main__":
    main(sys.argv[1:])
