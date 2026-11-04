# SPDX-License-Identifier: GPL-2.0-or-later
"""Perspective kit for the places: a curved centreline C(t) from the viewer (t = 0) to a vanishing
point (t = 1), the depth z mapped to t = 1 - z0/z (true perspective scale s = 1 - t), a lateral
axis v and a height h. Everything on a railway or a road is drawn as ribbons between two (v, h)
curves, so rails, sleepers, platforms, columns and arches converge and recede together."""
import math

from geom import f


class Track:
    def __init__(self, ctrl, unit, z0=3.0, lateral_mix=0.45, lat=None):
        self.c = ctrl                 # control points in px, near -> far
        self.U = unit                 # px per world unit at s = 1
        self.z0 = z0
        self.mix = lateral_mix
        self.lat = lat                # fixed screen vector for +v (a side view), else the curve's normal

    def C(self, t):
        pts = list(self.c)
        while len(pts) > 1:
            pts = [((1 - t) * a[0] + t * b[0], (1 - t) * a[1] + t * b[1]) for a, b in zip(pts, pts[1:])]
        return pts[0]

    def tan(self, t):
        e = 1e-3
        a, b = self.C(max(0, t - e)), self.C(min(1, t + e))
        d = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
        return ((b[0] - a[0]) / d, (b[1] - a[1]) / d)

    def t_of(self, z):
        return max(-0.8, min(0.9999, 1 - self.z0 / max(z, self.z0 * 0.2)))

    def s(self, t):
        return 1 - t

    def pt(self, z, v, h=0.0):
        """Screen point at depth z (world), lateral v (right +), height h (up +)."""
        t = self.t_of(z)
        x, y = self.C(t)
        tx, ty = self.tan(t)
        nx, ny = -ty, tx                       # perpendicular, to the right of travel
        if nx < 0:
            nx, ny = -nx, -ny
        lx, ly = (1 - self.mix) * nx + self.mix, (1 - self.mix) * ny
        if self.lat:
            lx, ly = self.lat
        n = math.hypot(lx, ly) or 1
        k = self.U * self.s(t)
        return (x + lx / n * v * k, y + ly / n * v * k - h * k)

    def ribbon(self, z_a, z_b, v0, v1, h0=0.0, h1=None, n=24):
        """Polygon of the strip between lateral v0 and v1 (heights h0, h1) from depth z_a to z_b."""
        h1 = h0 if h1 is None else h1
        zs = [z_a * (z_b / z_a) ** (i / n) for i in range(n + 1)]
        a = [self.pt(z, v0, h0) for z in zs]
        b = [self.pt(z, v1, h1) for z in zs]
        return a, b

    def poly(self, z_a, z_b, v0, v1, h0=0.0, h1=None, n=24):
        a, b = self.ribbon(z_a, z_b, v0, v1, h0, h1, n)
        return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in a + b[::-1]) + "Z"

    def line(self, z_a, z_b, v, h=0.0, n=24):
        zs = [z_a * (z_b / z_a) ** (i / n) for i in range(n + 1)]
        return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in (self.pt(z, v, h) for z in zs))
