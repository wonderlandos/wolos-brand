# SPDX-License-Identifier: GPL-2.0-or-later
"""cachoeira (place): the Estacao Ferroviaria de Cachoeira Paulista (Central do Brasil, 1877-1890s
eclectic station), seen from the mirante above the town at the golden hour, drawn from photographs
(references and measurements in .claude/v012/brand-east/walls/ref-cachoeira/, never embedded).

What the photographs show, and what is drawn (metres, measured against the 1.6 m broad gauge and
the 4.5 m bay of the platform wing):
  * the three-storey block (23.5 m): a left part of 3 window axes, the projecting central pavilion
    of 4 tall round-arched windows per floor under a gable with a pendant-arch frieze and a
    quatrefoil, a narrow right part of one axis; string courses at 5.0 and 9.4 m, a corbel-arch
    frieze under the cornice, a merlon band and square pinnacles at every corner;
  * the long one-storey wing (4.5 m bays, arched doors and windows between pilasters, a merlon
    parapet with brick-capped pinnacles twice per bay), its platform canopy on iron scroll brackets,
    and a two-storey end pavilion;
  * the platform, three broad-gauge tracks that turn once and run off into the valley over an iron
    bridge on the Paraiba; telegraph poles; the tile roofs of the town below the mirante;
  * the Paraiba do Sul winding through the valley, Cancao Nova on the far rise, the Mantiqueira
    ranges in four planes.
One light at the upper left (sun at day, moon at night): the entry. The rails are the water line:
from the far bridge they turn once and land at the block in the lower-right third. The middle of the
frame is sky and haze, calm for windows. Every colour is calculus.derive() on the base violet."""
import math
import random
import re

import calculus as K
from geom import f, smooth
from walls_lib import lin, rad, blurf

EL = {"base", "earth", "fire", "wood", "water"}

# role: (k on the value ruler, chroma in 21sts of the base, element of the hue)
DAY = dict(
    sky_top=(9, 7, "water"), sky_mid=(14, 5, "base"), sky_hor=(18, 4, "earth"), glow=(20, 6, "earth"), sun=(20, 9, "earth"),
    cloud_lit=(19, 3, "earth"), cloud=(16, 3, "base"), cloud_shd=(12, 5, "base"), fog=(17, 3, "earth"),
    r0=(14, 4, "water"), r1=(12, 5, "water"), r2=(10, 5, "wood"), r3=(7, 6, "wood"), rlit=(14, 4, "earth"),
    valley=(11, 5, "wood"), valley2=(8, 6, "wood"), field=(13, 5, "earth"), roofdot=(9, 8, "fire"), walldot=(17, 3, "earth"),
    river=(16, 4, "water"), river_d=(11, 5, "water"), ripple=(19, 2, "base"),
    tree_lit=(9, 6, "wood"), tree=(3, 6, "wood"), tree_shd=(-3, 5, "water"), tree_dk=(-8, 4, "base"),
    pl_lit=(17, 6, "earth"), pl=(13, 6, "earth"), pl_shd=(5, 5, "fire"), pl_dk=(-1, 5, "base"),
    trim=(17, 4, "earth"), brick=(6, 9, "fire"), brick_lit=(11, 9, "fire"),
    hole=(-7, 4, "base"), glass=(-4, 4, "base"), glass_hi=(6, 4, "water"), frame=(9, 3, "earth"),
    canopy=(6, 4, "base"), canopy_hi=(12, 4, "base"), iron=(-9, 4, "base"),
    plat=(14, 3, "base"), plat_edge=(9, 3, "base"), shadow=(5, 5, "base"),
    ballast=(9, 3, "base"), ballast_d=(4, 3, "base"), sleeper=(0, 4, "fire"), rail=(-6, 3, "base"), rail_hi=(19, 4, "earth"),
    grass=(9, 7, "wood"), grass_d=(4, 7, "wood"),
    tile=(5, 7, "fire"), tile_lit=(10, 7, "fire"), tile_shd=(-1, 6, "fire"), hw=(16, 4, "earth"), hw_shd=(8, 4, "base"),
    gold=(14, 15, "earth"), lamp=(14, 15, "earth"), star=(20, 2, "base"))
NIGHT = dict(
    sky_top=(-18, 7, "base"), sky_mid=(-15, 6, "base"), sky_hor=(-10, 6, "water"), glow=(-6, 5, "base"), sun=(19, 3, "water"),
    cloud_lit=(-6, 4, "base"), cloud=(-11, 4, "base"), cloud_shd=(-14, 4, "base"), fog=(-11, 4, "base"),
    r0=(-11, 5, "base"), r1=(-12, 5, "water"), r2=(-14, 5, "base"), r3=(-15, 5, "water"), rlit=(-8, 5, "water"),
    valley=(-15, 5, "wood"), valley2=(-16, 5, "wood"), field=(-13, 4, "base"), roofdot=(10, 13, "earth"), walldot=(-11, 3, "base"),
    river=(-12, 5, "water"), river_d=(-16, 5, "water"), ripple=(-3, 4, "water"),
    tree_lit=(-11, 6, "wood"), tree=(-14, 6, "wood"), tree_shd=(-17, 5, "water"), tree_dk=(-19, 4, "base"),
    pl_lit=(-3, 5, "earth"), pl=(-8, 5, "earth"), pl_shd=(-13, 5, "base"), pl_dk=(-16, 5, "base"),
    trim=(-5, 4, "earth"), brick=(-12, 7, "fire"), brick_lit=(-8, 7, "fire"),
    hole=(-18, 3, "base"), glass=(-15, 4, "water"), glass_hi=(-9, 4, "water"), frame=(-11, 3, "earth"),
    canopy=(-15, 4, "base"), canopy_hi=(-11, 4, "base"), iron=(-19, 3, "base"),
    plat=(-10, 3, "base"), plat_edge=(-13, 3, "base"), shadow=(-16, 5, "base"),
    ballast=(-13, 3, "base"), ballast_d=(-16, 3, "base"), sleeper=(-16, 4, "fire"), rail=(-18, 3, "base"), rail_hi=(-2, 4, "water"),
    grass=(-15, 6, "wood"), grass_d=(-17, 5, "wood"),
    tile=(-12, 7, "fire"), tile_lit=(-9, 7, "fire"), tile_shd=(-16, 6, "fire"), hw=(-7, 4, "earth"), hw_shd=(-13, 4, "base"),
    gold=(12, 14, "earth"), lamp=(13, 15, "earth"), star=(19, 2, "base"))
ROLES = {"day": DAY, "night": NIGHT, "dusk": dict(DAY, sky_top=(5, 8, "base"), sky_mid=(12, 6, "fire"), sky_hor=(17, 6, "earth")),
         "jade": dict(DAY, sky_top=(10, 7, "wood"), sky_mid=(15, 5, "water"))}


def g1(v):
    """A coordinate to 0.1 px (4K: invisible, and it halves the file)."""
    t = f"{v:.1f}"
    return t[:-2] if t.endswith(".0") else t


def P2(pts):
    return "M" + "L".join(f"{g1(x)} {g1(y)}" for x, y in pts) + "Z"


def PL(pts):
    return "M" + "L".join(f"{g1(x)} {g1(y)}" for x, y in pts)


class Painter:
    def __init__(self, doc, fr, name):
        self.doc, self.W, self.H = doc, fr.w, fr.h
        self.night = name == "night"
        self.R = ROLES.get(name, DAY)
        W, H = self.W, self.H
        self.fl = 0.80 * W                       # focal length: 64 degrees across
        self.cy = (0.40 if W / H > 1.7 else 0.42) * H    # the horizon
        self.hc = 22.0                           # the mirante above the town: eye 22 m over the square
        self.hw = -3.0                           # the Paraiba's level in the valley behind
        self.mirror = False
        vx = -0.30                               # the facade's vanishing point, off the frame to the left
        rx = (vx - 0.5) * W / self.fl
        n = math.hypot(rx, 1)
        self.dR = (-rx / n, -1 / n)              # along the facade, to the right (toward us)
        zb = 82.0 if W / H > 1.7 else 80.0
        self.O = ((0.505 - 0.5) * W / self.fl * zb, zb)  # the block's left corner
        a, b = self.dR
        self.nT = (b, -a) if (b * -self.O[0] + -a * -self.O[1]) > 0 else (-b, a)   # off the facade toward us
        self.wc = abs(self.O[0] * self.nT[0] + self.O[1] * self.nT[1])          # our distance from the facade line
        self.light = (0.15 * W, 0.16 * H)

    # ---------------------------------------------------------------- colour
    def C(self, role, fog=0.0, dk=0.0):
        k, c, el = self.R[role]
        fk, fc, fel = self.R["fog"]
        k = k + dk
        if fog:
            k, c = k + (fk - k) * fog, c + (fc - c) * fog
        return K.derive(round(k, 2), round(c, 2), K.hue_of(el))

    def fogZ(self, Z):
        return max(0.0, min(0.92, 1 - math.exp(-max(0.0, Z - 40) / 900)))

    # ---------------------------------------------------------------- projection
    def proj(self, X, Y, Z):
        Z = max(Z, 1.0)
        if self.mirror:
            Y = 2 * self.hw - Y
        return (self.W / 2 + self.fl * X / Z, self.cy - self.fl * (Y - self.hc) / Z)

    def world(self, u, w):
        return (self.O[0] + u * self.dR[0] + w * self.nT[0], self.O[1] + u * self.dR[1] + w * self.nT[1])

    def F(self, u, h, w=0.0):
        X, Z = self.world(u, w)
        return self.proj(X, h, Z)

    def k(self, u, w=0.0):
        return self.fl / self.world(u, w)[1]      # px per metre at that depth

    def Zu(self, u, w=0.0):
        return self.world(u, w)[1]

    def add(self, s):
        self.doc.add(s)

    def quad(self, u0, u1, h0, h1, w=0.0):
        return P2([self.F(u0, h0, w), self.F(u1, h0, w), self.F(u1, h1, w), self.F(u0, h1, w)])

    def arch_pts(self, uc, half, h0, hs, w=0.0, n=14, out=0.0):
        r = half + out
        pts = [(uc - r, h0), (uc - r, hs)]
        pts += [(uc - r * math.cos(math.pi * j / n), hs + r * math.sin(math.pi * j / n)) for j in range(1, n)]
        pts += [(uc + r, hs), (uc + r, h0)]
        return [self.F(a, b, w) for a, b in pts]

    def arc_line(self, uc, r, hs, w=0.0, n=14):
        return [self.F(uc - r * math.cos(math.pi * j / n), hs + r * math.sin(math.pi * j / n), w) for j in range(n + 1)]

    # ---------------------------------------------------------------- perspective pattern tiles
    def tile(self, kind):
        """Base tiles, in metres of the surface (x along, y down): drawn once, reused by every
        instance through xlink:href with the local perspective as patternTransform."""
        if not hasattr(self, "_tiles"):
            self._tiles = {}
        key = (kind, self.mirror)
        if key in self._tiles:
            return self._tiles[key]
        d = self.doc
        i = d.id("t")
        C = self.C
        if kind == "brick":       # running bond, 25 x 7.5 cm, mortar 1 cm
            w, h = 0.5, 0.15
            body = (f'<rect width="{w}" height="{h}" fill="{C("brick")}"/>'
                    f'<rect x="0.26" y="0.01" width="0.23" height="0.055" fill="{C("brick_lit")}" opacity="0.6"/>'
                    f'<rect x="0.02" y="0.085" width="0.2" height="0.055" fill="{C("brick", -2)}" opacity="0.5"/>'
                    f'<path d="M0 0.0H0.5M0 0.075H0.5M0.25 0V0.075M0 0.075V0.15M0.5 0.075V0.15" stroke="{C("trim", -2)}" stroke-width="0.012" fill="none"/>')
        elif kind == "ashlar":    # dressed stone, 60 x 30 cm
            w, h = 1.2, 0.6
            body = (f'<rect width="{w}" height="{h}" fill="{C("pl_shd")}"/>'
                    f'<rect x="0.03" y="0.03" width="0.54" height="0.24" fill="{C("pl_shd", 2)}"/><rect x="0.63" y="0.03" width="0.54" height="0.24" fill="{C("pl_shd", 1)}"/>'
                    f'<rect x="0.33" y="0.33" width="0.54" height="0.24" fill="{C("pl_shd", 2.5)}"/><rect x="-0.27" y="0.33" width="0.54" height="0.24" fill="{C("pl_shd", 1.5)}"/><rect x="0.93" y="0.33" width="0.54" height="0.24" fill="{C("pl_shd", 1.5)}"/>')
        elif kind == "stone":     # coursed stone of the river wall, 27 cm courses
            w, h = 1.6, 0.54
            rnd = random.Random(4)
            rr = []
            for row in range(2):
                x = -rnd.uniform(0, 0.3)
                while x < w:
                    L = rnd.uniform(0.3, 0.6)
                    rr.append(f'<rect x="{f(x + 0.02)}" y="{f(row * 0.27 + 0.02)}" width="{f(L - 0.04)}" height="0.23" rx="0.04" fill="{C("plat_edge", rnd.uniform(-1.5, 0.8))}"/>')
                    x += L
            body = f'<rect width="{w}" height="{h}" fill="{C("plat_edge", -3)}"/>' + "".join(rr)
        elif kind == "tiles":     # capa e canal: channels 20 cm, courses 35 cm, lit on the left
            w, h = 0.4, 0.35
            body = (f'<rect width="{w}" height="{h}" fill="{C("tile_shd")}"/>'
                    f'<rect x="0.02" y="0" width="0.16" height="0.33" rx="0.07" fill="{C("tile")}"/><rect x="0.22" y="0" width="0.16" height="0.33" rx="0.07" fill="{C("tile", -1)}"/>'
                    f'<rect x="0.04" y="0.02" width="0.04" height="0.28" rx="0.02" fill="{C("tile_lit")}"/><rect x="0.24" y="0.02" width="0.04" height="0.28" rx="0.02" fill="{C("tile_lit", -1)}"/>')
        elif kind == "paving":    # platform slabs 1.0 x 0.6 m
            w, h = 1.0, 1.2
            body = (f'<rect width="{w}" height="{h}" fill="{C("plat")}"/><rect x="0.03" y="0.63" width="0.45" height="0.54" fill="{C("plat", 0.8)}"/>'
                    f'<path d="M0 0H1M0 0.6H1M0 0V0.6M0.5 0.6V1.2" stroke="{C("plat_edge")}" stroke-width="0.025" fill="none"/>')
        elif kind == "cobble":    # granite setts of the street, 20 x 12 cm, joints in sand
            w, h = 0.4, 0.24
            body = (f'<rect width="{w}" height="{h}" fill="{C("ballast_d")}"/>'
                    f'<rect x="0.01" y="0.01" width="0.18" height="0.1" rx="0.02" fill="{C("ballast")}"/><rect x="0.21" y="0.01" width="0.18" height="0.1" rx="0.02" fill="{C("ballast", -1)}"/>'
                    f'<rect x="-0.09" y="0.13" width="0.18" height="0.1" rx="0.02" fill="{C("ballast", 0.5)}"/><rect x="0.11" y="0.13" width="0.18" height="0.1" rx="0.02" fill="{C("ballast", -0.5)}"/><rect x="0.31" y="0.13" width="0.18" height="0.1" rx="0.02" fill="{C("ballast")}"/>')
        elif kind == "wave":      # pedra portuguesa: dark waves on light stone, 4 m wavelength
            w, h = 2.4, 1.2
            pts_a = " ".join(f"{f(2.4 * i / 16)} {f(0.3 + 0.22 * math.sin(2 * math.pi * i / 16))}" for i in range(17))
            pts_b = " ".join(f"{f(2.4 * i / 16)} {f(0.55 + 0.22 * math.sin(2 * math.pi * i / 16))}" for i in range(16, -1, -1))
            body = (f'<rect width="{w}" height="{h}" fill="{C("plat", 2)}"/>'
                    f'<path d="M{pts_a} L{pts_b}Z" fill="{C("plat", -5)}"/>'
                    f'<path d="M0 0.9H2.4" stroke="{C("plat", 0.5)}" stroke-width="0.015"/>')
        elif kind == "sheet":     # corrugated sheet of the canopy, 7.6 cm pitch
            w, h = 0.152, 1.0
            body = f'<rect width="{w}" height="{h}" fill="{C("canopy")}"/><rect x="0.0" width="0.05" height="{h}" fill="{C("canopy_hi")}"/><rect x="0.09" width="0.03" height="{h}" fill="{C("canopy", -2)}"/>'
        else:
            raise KeyError(kind)
        d.defs.append(f'<pattern id="{i}" patternUnits="userSpaceOnUse" width="{w}" height="{h}">{body}</pattern>')
        self._tiles[key] = i
        return i

    def pat(self, kind, u, h, w=0.0, plane="facade", rot=None):
        """A pattern fill laid on a surface with the local perspective at (u, h, w): the tile's x runs
        along the surface, its y down it (facade: along u and down h; ground: along u and toward us;
        end: along -w and down h)."""
        if self.mirror:   # the river does not show mortar joints: a flat tone of the tile
            return self.C({"brick": "brick", "ashlar": "pl_shd", "stone": "plat_edge", "tiles": "tile", "paving": "plat", "sheet": "canopy", "cobble": "ballast", "wave": "plat"}[kind])
        base = self.tile(kind)
        p0 = self.F(u, h, w)
        if plane == "facade":
            a, b = self.F(u + 1, h, w), self.F(u, h - 1, w)
        elif plane == "ground":
            a, b = self.F(u + 1, h, w), self.F(u, h, w + 1)
        elif plane == "end":
            a, b = self.F(u, h, w - 1), self.F(u, h - 1, w)
        else:
            a, b = plane
        A = (a[0] - p0[0], a[1] - p0[1])
        B = (b[0] - p0[0], b[1] - p0[1])
        d = self.doc
        i = d.id("p")
        d.defs.append(f'<pattern id="{i}" xlink:href="#{base}" patternTransform="matrix({f(A[0])} {f(A[1])} {f(B[0])} {f(B[1])} {f(p0[0])} {f(p0[1])})"/>')
        return f"url(#{i})"

    def pat2(self, kind, p0, pa, pb):
        """Pattern laid by three screen points: origin, +1 m along, +1 m down the surface."""
        return self.pat(kind, 0, 0, plane=None) if False else self._pat_pts(kind, p0, pa, pb)

    def _pat_pts(self, kind, p0, pa, pb):
        if self.mirror:   # the river does not show mortar joints: a flat tone of the tile
            return self.C({"brick": "brick", "ashlar": "pl_shd", "stone": "plat_edge", "tiles": "tile", "paving": "plat", "sheet": "canopy"}[kind])
        base = self.tile(kind)
        A = (pa[0] - p0[0], pa[1] - p0[1])
        B = (pb[0] - p0[0], pb[1] - p0[1])
        d = self.doc
        i = d.id("p")
        d.defs.append(f'<pattern id="{i}" xlink:href="#{base}" patternTransform="matrix({f(A[0])} {f(A[1])} {f(B[0])} {f(B[1])} {f(p0[0])} {f(p0[1])})"/>')
        return f"url(#{i})"

    # ================================================================ sky
    def sky(self):
        W, H, d = self.W, self.H, self.doc
        g = lin(d, [(0, self.C("sky_top"), 1), (0.55, self.C("sky_mid"), 1), (1, self.C("sky_hor"), 1)], (0.7 * W, 0), (0.55 * W, self.cy))
        self.add(f'<rect width="{W}" height="{H}" fill="{g}"/>')
        lx, ly = self.light
        self.add(f'<rect width="{W}" height="{f(self.cy + 0.05 * H)}" fill="{rad(d, [(0, self.C("glow"), 0.95), (0.25, self.C("glow"), 0.55), (0.6, self.C("glow"), 0.15), (1, self.C("glow"), 0)], (lx, ly), 0.95 * W)}"/>')
        # horizon band of warm haze
        self.add(f'<rect y="{f(self.cy - 0.20 * H)}" width="{W}" height="{f(0.26 * H)}" fill="{lin(d, [(0, self.C("fog"), 0), (0.75, self.C("fog"), 0.75), (1, self.C("fog"), 0.4)], (0, self.cy - 0.20 * H), (0, self.cy + 0.06 * H))}"/>')
        if self.night:
            self.milky()
        r = 0.022 * H
        self.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{f(r * 9)}" fill="{rad(d, [(0, self.C("sun"), 0.55), (0.18, self.C("sun"), 0.22), (1, self.C("sun"), 0)], (lx, ly), r * 9)}"/>')
        if not self.night:
            self.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{f(r * 2.6)}" fill="{rad(d, [(0, self.C("gold"), 0.0), (0.38, self.C("gold"), 0.35), (1, self.C("gold"), 0)], (lx, ly), r * 2.6)}"/>')
        self.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{f(r)}" fill="{self.C("sun")}"/>')
        if self.night:   # the moon's maria, faint
            self.add(f'<g fill="{self.C("sky_hor")}" opacity="0.18"><circle cx="{f(lx - 0.3 * r)}" cy="{f(ly - 0.2 * r)}" r="{f(0.35 * r)}"/><circle cx="{f(lx + 0.3 * r)}" cy="{f(ly + 0.25 * r)}" r="{f(0.25 * r)}"/><circle cx="{f(lx + 0.1 * r)}" cy="{f(ly - 0.45 * r)}" r="{f(0.16 * r)}"/></g>')
        # sun rays, very faint, fanning to the lower right (the direction of the light)
        rays = []
        rnd = random.Random(4)
        for i in range(9):
            a0 = math.radians(8 + i * 9 + rnd.uniform(-2, 2))
            a1 = a0 + math.radians(rnd.uniform(1.5, 3.5))
            L = 1.25 * W
            rays.append(P2([(lx, ly), (lx + L * math.cos(a0), ly + L * math.sin(a0)), (lx + L * math.cos(a1), ly + L * math.sin(a1))]))
        if not self.night:
            self.add(f'<path d="{"".join(rays)}" fill="{rad(d, [(0, self.C("glow"), 0.22), (0.6, self.C("glow"), 0.05), (1, self.C("glow"), 0)], (lx, ly), 1.1 * W)}"/>')
        self.clouds()

    def milky(self):
        W, H, d = self.W, self.H, self.doc
        # the band runs from the upper right down toward the moon's side, wide and soft
        # the band: a wide soft strip across the sky (gradient across it, no filter), a brighter core
        def strip(p0, p1, half, op, col):
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            n = math.hypot(dx, dy)
            nx, ny = -dy / n * half, dx / n * half
            g = lin(d, [(0, col, 0), (0.5, col, op), (1, col, 0)], (p0[0] + nx, p0[1] + ny), (p0[0] - nx, p0[1] - ny))
            pts = [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]
            return f'<path d="{P2(pts)}" fill="{g}"/>'
        a, b = (0.34 * W, -0.06 * H), (1.06 * W, 0.34 * H)
        fade = d.id("mf")
        d.defs.append(f'<mask id="{fade}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="{lin(d, [(0, "#FFFFFF", 0.2), (0.5, "#FFFFFF", 1), (1, "#FFFFFF", 0.5)], (0.34 * W, 0), (W, 0.34 * H))}"/></mask>')
        self.add(f'<g mask="url(#{fade})">' + strip(a, b, 0.10 * H, 0.30, self.C("cloud_lit")) + strip(a, b, 0.035 * H, 0.22, self.C("cloud_lit", 0, 3))
 + '</g>')
        rnd = random.Random(21)
        st = []
        for i in range(900):
            if i < 520:   # in the band
                t = rnd.random()
                cx, cy = 0.34 * W + 0.72 * W * t, -0.06 * H + 0.40 * H * t
                g_ = rnd.gauss(0, 0.045 * H)
                cx += g_ * 0.48
                cy -= g_ * 0.88
            else:
                cx, cy = rnd.uniform(0, W), rnd.uniform(0.04 * H, 0.50 * H)
            if cy > self.cy - 0.12 * H or cy < 0.04 * H or math.dist((cx, cy), self.light) < 0.10 * H:
                continue
            r = (0.5 + rnd.random() ** 6 * 2.2) * H / 2160
            st.append(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" opacity="{f(0.35 + 0.6 * rnd.random())}"/>')
        self.add(f'<g fill="{self.C("star")}">{"".join(st)}</g>')

    def clouds(self):
        """Cumulus with flat bases in the upper band, lit from the upper left: a body of many lobes,
        a soft self-shadow to the lower right, lit crowns, the edges frayed by a displacement."""
        W, H, d = self.W, self.H, self.doc
        fid = d.id("cl")
        d.defs.append(f'<filter id="{fid}" x="-5%" y="-30%" width="110%" height="160%" color-interpolation-filters="sRGB">'
                      f'<feGaussianBlur stdDeviation="{f(0.0012 * H)}"/></filter>')
        soft = blurf(d, 0.006 * H)
        rnd = random.Random(9)
        groups = [(0.40, 0.14, 0.26, 0.050, 30), (0.66, 0.09, 0.20, 0.036, 22), (0.86, 0.22, 0.24, 0.052, 30), (0.55, 0.27, 0.12, 0.022, 12), (0.97, 0.08, 0.10, 0.025, 10)]
        out = []
        for cx, cy, wd, ht, n in groups:
            x0 = (cx - wd / 2) * W
            base_y = cy * H
            lobes = []
            for i in range(n):
                t = rnd.random()
                env = math.sin(math.pi * t) ** 0.8
                r = ht * H * (0.25 + 0.75 * env) * rnd.uniform(0.55, 1.0)
                x = x0 + t * wd * W
                y = base_y - r * rnd.uniform(0.35, 0.9) - ht * H * 0.25 * env
                lobes.append((x, y, r))
            lobes.sort(key=lambda a: a[1])
            ell = lambda dx, dy, sc: "".join(f'<ellipse cx="{f(x + dx * r)}" cy="{f(y + dy * r)}" rx="{f(r * 1.25 * sc)}" ry="{f(r * 0.9 * sc)}"/>' for x, y, r in lobes)
            cid = d.id("cc")
            d.defs.append(f'<clipPath id="{cid}"><rect x="0" y="0" width="{W}" height="{f(base_y)}"/></clipPath>')
            bid = d.id("cb")
            d.defs.append(f'<clipPath id="{bid}">{ell(0, 0, 1)}</clipPath>')
            g = lin(d, [(0, self.C("cloud_lit"), 1), (0.6, self.C("cloud"), 1), (1, self.C("cloud_shd"), 1)], (x0, base_y - ht * H * 2.2), (x0 + 0.2 * wd * W, base_y))
            out.append(f'<g clip-path="url(#{cid})"><g fill="{g}">{ell(0, 0, 1)}</g>'
                       f'<g clip-path="url(#{bid})"><g fill="{self.C("cloud_shd")}" opacity="0.55" filter="{soft}">{ell(0.35, 0.45, 0.8)}</g>'
                       f'<g fill="{self.C("cloud_lit")}" opacity="0.8" filter="{soft}">{ell(-0.3, -0.35, 0.55)}</g></g></g>')
        self.add(f'<g filter="url(#{fid})" opacity="{0.9 if not self.night else 0.55}">{"".join(out)}</g>')
        # high cirrus near the light, long thin and soft
        ci = []
        for i in range(7):
            y = (0.05 + 0.035 * i + rnd.uniform(-0.01, 0.01)) * H
            x = rnd.uniform(0.02, 0.30) * W
            L = rnd.uniform(0.15, 0.32) * W
            ci.append(f"M{f(x)} {f(y)}q{f(L / 2)} {f(-0.012 * H)} {f(L)} {f(0.004 * H)}")
        self.add(f'<path d="{"".join(ci)}" fill="none" stroke="{self.C("cloud_lit")}" stroke-width="{f(0.004 * H)}" stroke-linecap="round" opacity="0.45" filter="{blurf(d, 0.002 * H)}"/>')

    # ================================================================ far: the Mantiqueira
    def profile(self, seed, x0, x1, base, amp, rough, n=140, peaks=None):
        rnd = random.Random(seed)
        ph = [rnd.uniform(0, 6.3) for _ in range(6)]
        pts = []
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = 0.0
            for j, (fq, a) in enumerate(((1.1, 1.0), (2.3, 0.45), (5.1, 0.2), (11.0, 0.08), (23, 0.035), (47, 0.015))):
                y += a * math.sin(fq * t * 6.28 + ph[j]) * (rough if j > 2 else 1)
            env = 1.0 if peaks is None else peaks(t)
            pts.append((x, base - amp * env * (0.55 + 0.45 * y)))
        return pts

    def ridges(self):
        W, H, d, cy = self.W, self.H, self.doc, self.cy
        # (role, seed, base y over the horizon, amplitude, fog) far to near; higher on the right (anchor)
        layers = [("r0", 3, 0.000, 0.125, 0.46), ("r1", 8, 0.002, 0.10, 0.36), ("r2", 15, 0.004, 0.075, 0.26), ("r3", 23, 0.006, 0.05, 0.16), ("r3", 31, 0.008, 0.028, 0.08)]
        for li, (role, seed, b, amp, fg) in enumerate(layers):
            env = (lambda t, li=li: (0.35 + 0.65 * min(1, max(0, (t - 0.08) / 0.8)) ** 1.3) * (1 - 0.25 * math.exp(-((t - 0.25) / 0.12) ** 2)))
            pts = self.profile(seed, -0.02 * W, 1.02 * W, cy - b * H, amp * H, 0.8 + 0.2 * li, peaks=env)
            area = PL(pts) + f" L{f(1.02 * W)} {f(cy + 0.02 * H)} L{f(-0.02 * W)} {f(cy + 0.02 * H)}Z"
            cid = d.id("rc")
            d.defs.append(f'<clipPath id="{cid}"><path d="{area}"/></clipPath>')
            top = min(y for _, y in pts)
            lit = self.C(role, max(0, fg - 0.1), 2.5)
            body = self.C(role, fg)
            self.add(f'<path d="{area}" fill="{lit}"/>')
            # shade = the same ridge moved right: what stays uncovered is the lit flank facing the light
            dx = (0.010 - 0.002 * li) * W
            shifted = PL([(x + dx, y + 0.002 * H) for x, y in pts]) + f" L{f(1.1 * W)} {f(cy + 0.05 * H)} L{f(-0.1 * W)} {f(cy + 0.05 * H)} L{f(-0.1 * W)} {f(pts[0][1])}Z"
            g = lin(d, [(0, body, 1), (1, self.C(role, min(0.9, fg + 0.35)), 1)], (0, top), (0, cy))
            self.add(f'<g clip-path="url(#{cid})"><path d="{shifted}" fill="{g}"/>')
            # strata: the ridge line repeated downward, the geometric cun of the hills
            st = []
            for j in range(1, 7):
                off = j * 0.0065 * H * (1 + 0.15 * j)
                st.append(PL([(x + j * 0.002 * W, y + off) for x, y in pts[::2]]))
            self.add(f'<path d="{"".join(st)}" fill="none" stroke="{self.C(role, fg, -1.0)}" stroke-width="{f(0.0009 * H)}" opacity="0.3"/>')
            self.add(f'<rect y="{f(cy - 0.06 * H)}" width="{W}" height="{f(0.08 * H)}" fill="{lin(d, [(0, self.C("fog"), 0), (1, self.C("fog"), 0.8)], (0, cy - 0.06 * H), (0, cy + 0.01 * H))}"/></g>')

    # ================================================================ middle: the valley
    def valley(self):
        W, H, d, cy = self.W, self.H, self.doc, self.cy
        g = lin(d, [(0, self.C("valley", 0.75), 1), (0.25, self.C("valley", 0.45), 1), (1, self.C("valley2", 0.0), 1)], (0, cy - 0.005 * H), (0, H))
        self.add(f'<rect y="{f(cy - 0.006 * H)}" width="{W}" height="{f(H - cy + 0.006 * H)}" fill="{g}"/>')
        rnd = random.Random(31)
        # fields: ground-plane strips in perspective (lit and shaded furrow bands)
        fl = []
        for i in range(70):
            Z = 220 * (1.045 ** i)
            if Z > 6000:
                break
            X0 = rnd.uniform(-1.6, 0.9) * Z
            wd = rnd.uniform(0.08, 0.3) * Z
            dz = Z * 0.035
            fog = self.fogZ(Z)
            pts = [self.proj(X0, 0, Z), self.proj(X0 + wd, 0, Z), self.proj(X0 + wd * 1.05, 0, Z + dz), self.proj(X0 + wd * 0.05, 0, Z + dz)]
            fl.append(f'<path d="{P2(pts)}" fill="{self.C("field" if i % 3 else "valley2", fog)}" opacity="0.55"/>')
        self.add("".join(fl))
        # hedgerows and tree lines across the valley: dotted crowns along ground-plane lines
        hedge = []
        for i in range(26):
            Z = 260 * (1.11 ** i)
            if Z > 7000:
                break
            fog = self.fogZ(Z)
            X0 = rnd.uniform(-1.9, 0.4) * Z
            L = rnd.uniform(0.2, 0.8) * Z
            n = int(18 + 30 * rnd.random())
            r = max(0.9, 7.0 * self.fl / Z)
            dots = []
            for j in range(n):
                X = X0 + L * j / n + rnd.uniform(-0.01, 0.01) * Z
                x, y = self.proj(X, 0, Z + rnd.uniform(-0.01, 0.01) * Z)
                rr = r * rnd.uniform(0.7, 1.3)
                dots.append(f'<circle cx="{f(x)}" cy="{f(y - rr * 0.6)}" r="{f(rr)}"/>')
            hedge.append(f'<g fill="{self.C("tree", min(0.92, fog + 0.05))}">{"".join(dots)}</g>')
        self.add("".join(hedge))
        self.town()

    def town(self):
        """Cachoeira and Cancao Nova at the foot of the far rise: tiny walls and tile roofs."""
        rnd = random.Random(5)
        out, lights = [], []
        for i in range(520):
            Z = rnd.uniform(500, 1500)
            X = rnd.uniform(-1.35, -0.62) * Z if i % 4 else rnd.uniform(-0.6, -0.30) * Z
            fog = self.fogZ(Z)
            k = self.fl / Z
            w, h = rnd.uniform(6, 14) * k, rnd.uniform(4, 7) * k
            x, y = self.proj(X, 0, Z)
            if y < self.cy + 2:
                continue
            out.append(f'<rect x="{f(x)}" y="{f(y - h)}" width="{f(w)}" height="{f(h)}" fill="{self.C("walldot", fog)}"/>'
                       f'<path d="M{f(x - 0.1 * w)} {f(y - h)}L{f(x + 0.5 * w)} {f(y - h - 0.45 * h)}L{f(x + 1.1 * w)} {f(y - h)}Z" fill="{self.C("roofdot", fog)}"/>')
            if self.night and rnd.random() < 0.35:
                lights.append(f'<circle cx="{f(x + w / 2)}" cy="{f(y - h / 2)}" r="{f(max(1.0, 0.4 * h))}"/>')
        self.add("".join(out))
        # Cancao Nova: the white hall with its curved roof and the tower with the cross, on the rise
        Z = 1350.0
        k = self.fl / Z
        fog = self.fogZ(Z) * 0.8
        x, y = self.proj(-0.55 * Z, 0, Z)
        wd, ht = 120 * k, 22 * k
        hall = (f'<path d="M{f(x)} {f(y)}L{f(x)} {f(y - ht)}Q{f(x + wd / 2)} {f(y - ht * 1.9)} {f(x + wd)} {f(y - ht)}L{f(x + wd)} {f(y)}Z" fill="{self.C("walldot", fog * 0.6)}"/>'
                f'<path d="M{f(x + wd * 0.5)} {f(y - ht * 1.45)}Q{f(x + wd * 0.75)} {f(y - ht * 1.35)} {f(x + wd)} {f(y - ht)}L{f(x + wd)} {f(y)}L{f(x + wd * 0.5)} {f(y)}Z" fill="{self.C("pl_shd", fog)}" opacity="0.35"/>')
        tx = x - 18 * k
        tower = (f'<rect x="{f(tx)}" y="{f(y - 60 * k)}" width="{f(7 * k)}" height="{f(60 * k)}" fill="{self.C("walldot", fog * 0.6)}"/>'
                 f'<path d="M{f(tx + 3.5 * k)} {f(y - 72 * k)}v{f(12 * k)}M{f(tx - 0.5 * k)} {f(y - 68 * k)}h{f(8 * k)}" stroke="{self.C("walldot", fog * 0.6)}" stroke-width="{f(max(1, 1.6 * k))}"/>')
        self.add(hall + tower)
        if lights:
            self.add(f'<g fill="{self.C("lamp")}" opacity="0.8">{"".join(lights)}</g>')

    # ================================================================ the river and the line
    def track_plan(self):
        """Centre of the middle track in the ground plane: straight along the platform, then one
        turn of 300 m radius away from the viewer, then straight into the valley to the bridge."""
        pts = []
        u, w = 46.0, -25.0
        X, Z = self.world(u, w)
        th = math.atan2(-self.dR[0], -self.dR[1])   # heading toward the left (away along the facade)
        s, ds = 0.0, 2.0
        R, turn, s_turn = 420.0, math.radians(30), 46.0 + 96.0
        while s < 2600:
            pts.append((X, Z, th))
            if s_turn < s < s_turn + R * turn:
                th += ds / R
            X += math.sin(th) * ds
            Z += math.cos(th) * ds
            s += ds
            ds = 2.0 if s < 400 else 8.0
        return pts

    def off(self, plan, w):
        """Plan points offset sideways by w (positive toward the viewer's side)."""
        out = []
        for X, Z, th in plan:
            nx, nz = -math.cos(th), math.sin(th)     # left of the heading = toward the camera here
            out.append((X + nx * w, Z + nz * w))
        return out

    def ground_strip(self, plan, w0, w1, h=0.0):
        a = [self.proj(X, h, Z) for X, Z in self.off(plan, w0)]
        b = [self.proj(X, h, Z) for X, Z in self.off(plan, w1)]
        return P2(a + b[::-1])

    def river(self):
        W, H, d = self.W, self.H, self.doc
        plan = self.track_plan()
        # the bridge: where the line meets the river, 900 m out
        bi = min(range(len(plan)), key=lambda i: abs(plan[i][1] - 900))
        bX, bZ = plan[bi][0], plan[bi][1]
        cl = [(bX + 900, 3800), (bX + 380, 2400), (bX - 60, 1500), (bX, bZ), (bX - 160, 620), (bX - 70, 430), (bX - 230, 300), (bX - 420, 240), (bX - 700, 230)]
        smooth_pts = []
        for i in range(len(cl) - 1):
            for j in range(12):
                t = j / 12
                p0 = cl[max(0, i - 1)]
                p1, p2 = cl[i], cl[i + 1]
                p3 = cl[min(len(cl) - 1, i + 2)]
                tt = t
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * tt + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * tt ** 2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * tt ** 3)
                z = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * tt + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * tt ** 2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * tt ** 3)
                smooth_pts.append((x, z))
        smooth_pts.append(cl[-1])
        L, Rr = [], []
        for i, (x, z) in enumerate(smooth_pts):
            a = smooth_pts[max(0, i - 1)]
            b = smooth_pts[min(len(smooth_pts) - 1, i + 1)]
            dx, dz = b[0] - a[0], b[1] - a[1]
            n = math.hypot(dx, dz) or 1
            wd = 42 + 18 * (i / len(smooth_pts))
            L.append(self.proj(x - dz / n * wd, 0, z + dx / n * wd))
            Rr.append(self.proj(x + dz / n * wd, 0, z - dx / n * wd))
        water = P2(L + Rr[::-1])
        cid = d.id("rv")
        d.defs.append(f'<clipPath id="{cid}"><path d="{water}"/></clipPath>')
        g = lin(d, [(0, self.C("river", 0.5), 1), (1, self.C("river_d"), 1)], (0, self.cy), (0, 0.72 * H))
        self.add(f'<path d="{water}" fill="{g}"/>')
        # sky glint and ripples, longer and wider apart toward the viewer
        rnd = random.Random(12)
        rp = []
        for i in range(90):
            Z = 230 * (1.035 ** i)
            if Z > 3500:
                break
            x0, y = self.proj(-2000, 0, Z)
            x1, _ = self.proj(1500, 0, Z)
            k = self.fl / Z
            for _ in range(3):
                xs = rnd.uniform(x0, x1)
                rp.append(f"M{f(xs)} {f(y)}h{f(rnd.uniform(8, 30) * k)}")
        self.add(f'<g clip-path="url(#{cid})"><path d="{"".join(rp)}" fill="none" stroke="{self.C("ripple")}" stroke-width="{f(max(1.0, 0.0012 * H))}" opacity="0.55"/>'
                 f'<rect width="{W}" height="{H}" fill="{rad(d, [(0, self.C("glow"), 0.5), (1, self.C("glow"), 0)], (0.16 * W, self.cy + 0.03 * H), 0.25 * W)}"/></g>')
        # the banks: a thin lit lip on the far bank, a dark one on the near bank
        self.add(f'<path d="{PL(L)}" fill="none" stroke="{self.C("grass_d", 0.4)}" stroke-width="{f(0.0016 * H)}" opacity="0.7"/>'
                 f'<path d="{PL(Rr)}" fill="none" stroke="{self.C("ripple", 0.2)}" stroke-width="{f(0.0012 * H)}" opacity="0.6"/>')
        self.bridge(plan, bi)

    def bridge(self, plan, bi):
        """A Pratt truss of three spans over the river, lattice drawn in perspective."""
        seg = plan[bi - 22: bi + 22]
        if len(seg) < 4:
            return
        out = []
        Zm = plan[bi][1]
        fog = self.fogZ(Zm) * 0.85
        col = self.C("iron", fog)
        sw = max(1.0, 0.45 * self.fl / Zm)
        for side in (-3.4, 3.4):
            pts = self.off(seg, side)
            bot = [self.proj(X, 4.0, Z) for X, Z in pts]
            top = [self.proj(X, 10.0, Z) for X, Z in pts]
            out.append(PL(bot) + PL(top))
            for i in range(0, len(pts) - 1, 2):
                out.append(PL([bot[i], top[i]]))
                if i + 2 < len(pts):
                    out.append(PL([bot[i], top[i + 2]]))
        for i in (0, len(seg) // 3, 2 * len(seg) // 3, len(seg) - 1):   # piers
            X, Z = seg[i][0], seg[i][1]
            a, b = self.proj(X - 3, 0, Z), self.proj(X + 3, 4, Z)
            out.append(P2([a, (b[0], a[1]), b, (a[0], b[1])]))
        self.add(f'<path d="{"".join(out)}" fill="none" stroke="{col}" stroke-width="{f(sw)}" stroke-linejoin="round"/>')

    # ================================================================ trees
    def crown(self, x, y, r, seed, fog, lobes=7, dark=False):
        """A broad-leaf crown built from leaf clusters in three values: the shade mass, the body
        turned to the light, the lit tops at the upper left (edges scalloped by the grove filter)."""
        rnd = random.Random(seed)
        cl = []
        n = 7 + min(8, int(r / 16))
        for i in range(n):
            a = rnd.uniform(0, 2 * math.pi)
            q = rnd.random() ** 0.6
            cl.append((x + math.cos(a) * q * r * 0.8, y + math.sin(a) * q * r * 0.55, r * rnd.uniform(0.28, 0.44)))
        lx, ly = -0.6, -0.8
        c = lambda cx, cy, rr: f'<circle cx="{g1(cx)}" cy="{g1(cy)}" r="{g1(rr)}"/>'
        sh = "".join(c(cx, cy, rr) for cx, cy, rr in cl)
        body = "".join(c(cx - 0.12 * rr, cy - 0.16 * rr, rr * 0.8) for cx, cy, rr in cl if ((cx - x) * lx + (cy - y) * ly) / r > -0.3)
        lit = "".join(c(cx - 0.26 * rr, cy - 0.32 * rr, rr * 0.46) for cx, cy, rr in cl if ((cx - x) * lx + (cy - y) * ly) / r > 0.15)
        return (f'<g fill="{self.C("tree_dk" if dark else "tree_shd", fog)}">{sh}</g><g fill="{self.C("tree", fog)}">{body}</g>'
                f'<g fill="{self.C("tree_lit", fog)}">{lit}</g>')

    def leaf_filter(self, scale):
        """Leafy edges for a whole grove: the crowns' outlines broken by fine noise (one filter)."""
        d = self.doc
        fid = d.id("lf")
        d.defs.append(f'<filter id="{fid}" x="-2%" y="-5%" width="104%" height="110%" color-interpolation-filters="sRGB">'
                      f'<feTurbulence type="turbulence" baseFrequency="{f(0.12 * 2160 / self.H / scale)}" numOctaves="1" seed="11" result="n"/>'
                      f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{f(0.005 * self.H * scale)}" xChannelSelector="R" yChannelSelector="G" result="d"/>'
                      f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 -4 0 1.6" result="ma"/>'
                      f'<feComposite in="d" in2="ma" operator="in" result="leaf"/>'
                      f'<feComponentTransfer in="leaf" result="dark"><feFuncR type="linear" slope="0.82"/><feFuncG type="linear" slope="0.86"/><feFuncB type="linear" slope="0.9"/></feComponentTransfer>'
                      f'<feMerge><feMergeNode in="d"/><feMergeNode in="dark"/></feMerge></filter>')
        return f"url(#{fid})"

    def trunk(self, x, y0, y1, w, fog):
        return f'<path d="M{f(x - w)} {f(y0)}L{f(x - w * 0.5)} {f(y1)}L{f(x + w * 0.5)} {f(y1)}L{f(x + w)} {f(y0)}Z" fill="{self.C("tree_dk", fog)}"/>'

    def grove(self, X0, X1, Z0, Z1, n, seed, size=(7, 12)):
        rnd = random.Random(seed)
        items = []
        for i in range(n):
            Z = rnd.uniform(Z0, Z1)
            X = rnd.uniform(X0, X1)
            items.append((Z, X, rnd.uniform(*size), rnd.randrange(10 ** 6)))
        out = []
        for Z, X, s, sd in sorted(items, reverse=True):
            fog = self.fogZ(Z)
            x, y = self.proj(X, 0, Z)
            k = self.fl / Z
            r = s * k * 0.55
            out.append(self.trunk(x, y, y - s * k * 0.55, max(0.8, 0.25 * k), fog))
            out.append(self.crown(x, y - s * k * 0.75, r, sd, fog))
        self.add("".join(out))

    # ================================================================ the station
    def station(self):
        self.yard()
        self.wing(-70.0, 0.0)
        self.end_pavilion(-78.0, -70.0)
        self.block()
        self.wing(23.5, 48.0, right=True)
        self.platform()
        self.tracks()
        self.poles()

    def bbox(self, path_d):
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", path_d)]
        xs, ys = nums[0::2], nums[1::2]
        x0, y0 = max(0.0, min(xs)), max(0.0, min(ys))
        x1, y1 = min(self.W, max(xs)), min(self.H, max(ys))
        return x0, y0, max(1.0, x1 - x0), max(1.0, y1 - y0)

    def grain(self, path_d, Zm, colour, opacity):
        """The grain group for a wall: the noise only over the wall's own box (render cost)."""
        x, y, w, h = self.bbox(path_d)
        if w * h < 400 or self.mirror:
            return ""
        cid, fid = self.wall_grain(path_d, Zm)
        return f'<g clip-path="url(#{cid})"><rect x="{g1(x)}" y="{g1(y)}" width="{g1(w)}" height="{g1(h)}" fill="{colour}" opacity="{opacity}" filter="url(#{fid})"/></g>'

    def wall_grain(self, path_d, Zm):
        """Weathered plaster: a faint low-frequency stain clipped to the wall (fractal noise, alpha
        only, so the colour stays the wall's own)."""
        d = self.doc
        cid, fid = d.id("wg"), d.id("wf")
        sc = self.fl / Zm
        d.defs.append(f'<clipPath id="{cid}"><path d="{path_d}"/></clipPath>')
        d.defs.append(f'<filter id="{fid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                      f'<feTurbulence type="fractalNoise" baseFrequency="{f(1.6 / sc)} {f(0.6 / sc)}" numOctaves="3" seed="3"/>'
                      f'<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.6 0.95"/>'
                      f'<feComposite in2="SourceGraphic" operator="in"/></filter>')
        return cid, fid

    def yard(self):
        """Ground of the yard: grass verges, the platform's shadow line, ballast bed."""
        d = self.doc
        plan = self.track_plan()
        near = plan[:220]
        self.add(f'<path d="{self.ground_strip(near, -6.6, 6.8)}" fill="{lin(d, [(0, self.C("grass_d"), 1), (1, self.C("grass", 0.4), 1)], (0, self.H), (0, self.cy))}"/>')

    def wing(self, u0, u1, right=False):
        d = self.doc
        WALL, CORN, PAR, PIN = 6.2, 6.8, 7.6, 8.9
        Zm = self.Zu((u0 + u1) / 2)
        fog = self.fogZ(Zm)
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        # the roof behind the parapet (seen from the mirante), then the street wall
        self.roof(u0, u1, CORN + 0.3, -0.4, -12.0, 3.2, fog)
        if right:   # the end wall turned toward us, in shade
            self.add(f'<path d="{P2([self.F(u1, 0, 0), self.F(u1, 0, -12), self.F(u1, PAR, -12), self.F(u1, PAR, 0)])}" fill="{C("pl_shd", 1)}"/>')
        wall = self.quad(u0, u1, 0.0, PAR)
        self.add(f'<path d="{wall}" fill="{lin(d, [(0, C("pl_lit"), 1), (0.5, C("pl"), 1), (1, C("pl", -1.5), 1)], self.F(u0, 4), self.F(u1, 4))}"/>')
        self.add(self.grain(wall, Zm, C("pl_shd"), 0.2))
        self.add(f'<path d="{self.quad(u0, u1, 0.0, 0.8)}" fill="{self.pat("ashlar", u0, 0.8) if u1 - u0 < 30 or right else C("pl_shd")}" opacity="0.8"/>')
        if not right:
            for a_, b_ in ((u0, u0 + 26), (u0 + 26, u0 + 50), (u0 + 50, u1)):
                self.add(f'<path d="{self.quad(a_, b_, 0.0, 0.8)}" fill="{self.pat("ashlar", (a_ + b_) / 2, 0.8)}" opacity="0.8"/>')
        # bays: pilasters every 4.5 m, arched door / window alternating
        bays = []
        u = u0 + 0.0
        while u <= u1 + 0.01:
            bays.append(u)
            u += 4.5
        ops, rims, lits, pil, pil_sh, hole_in = [], [], [], [], [], []
        for i, ub in enumerate(bays[:-1]):
            uc = ub + 2.25
            door = (i % 3 == 1)
            h0, hs, half = (0.0, 3.4, 1.05) if door else (1.1, 3.4, 0.8)
            ops.append(P2(self.arch_pts(uc, half, h0, hs)))
            # the reveal: the jamb facing the light shows lit, the other in shade (depth 0.35 m)
            hole_in.append(P2(self.arch_pts(uc + 0.18, half - 0.18, h0, hs - 0.05)))
            rims.append(PL(self.arc_line(uc, half + 0.18, hs)))
            lits.append(PL([self.F(uc + half, h0), self.F(uc + half, hs)]))
        for ub in bays:
            pil.append(self.quad(ub - 0.32, ub + 0.32, 0.0, WALL, 0.18))
            pil_sh.append(self.quad(ub + 0.32, ub + 0.52, 0.0, WALL))
        k = self.k((u0 + u1) / 2)
        lit_open = self.night
        self.add(f'<path d="{"".join(pil_sh)}" fill="{C("pl_shd")}" opacity="0.4"/>')
        self.add(f'<path d="{"".join(ops)}" fill="{C("pl_shd")}"/>')
        self.add(f'<path d="{"".join(hole_in)}" fill="{C("hole")}"/>')
        if lit_open:
            sel = "".join(o for j, o in enumerate(hole_in) if j % 2 == 0)
            self.add(f'<path d="{sel}" fill="{self.C("lamp")}" opacity="0.78"/>')
        self.add(f'<path d="{"".join(rims)}" fill="none" stroke="{C("trim")}" stroke-width="{f(max(1.0, 0.22 * k))}"/>')
        self.add(f'<path d="{"".join(lits)}" fill="none" stroke="{C("pl_lit", 2)}" stroke-width="{f(max(0.8, 0.12 * k))}" opacity="0.8"/>')
        self.add(f'<path d="{"".join(pil)}" fill="{C("pl_lit")}"/>')
        # cornice, parapet with merlons, pinnacles twice per bay
        self.add(f'<path d="{self.quad(u0, u1, WALL, CORN, 0.25)}" fill="{C("trim")}"/>'
                 f'<path d="{self.quad(u0, u1, WALL - 0.22, WALL, 0.1)}" fill="{C("pl_shd")}" opacity="0.7"/>'
                 f'<path d="{self.quad(u0, u1, CORN, PAR, 0.05)}" fill="{C("pl", -1)}"/>')
        mer, pins, caps, capsl = [], [], [], []
        u = u0 + 0.15
        while u < u1:
            mer.append(self.quad(u, u + 0.32, PAR, PAR + 0.34, 0.05))
            u += 0.62
        for ub in bays:
            for du in (0.0, 2.25):
                uu = ub + du
                if uu > u1 + 0.01:
                    continue
                pins.append(self.quad(uu - 0.3, uu + 0.3, CORN, PIN, 0.2))
                caps.append(self.quad(uu - 0.38, uu + 0.38, PIN, PIN + 0.35, 0.2))
                capsl.append(self.quad(uu - 0.38, uu - 0.12, PIN, PIN + 0.35, 0.2))
        self.add(f'<path d="{"".join(mer)}" fill="{C("pl")}"/>'
                 f'<path d="{"".join(pins)}" fill="{C("brick")}"/>'
                 f'<path d="{"".join(caps)}" fill="{C("trim")}"/><path d="{"".join(capsl)}" fill="{C("pl_lit", 2)}"/>')
        # brick courses on the near pinnacles (where a course is wider than 2 px)
        for j in range(0, len(pins)):
            uu = u0 + 2.25 * j
            if self.k(uu) * 0.075 < 2.2 or uu > u1:
                continue
            self.add(f'<path d="{pins[j]}" fill="{self.pat("brick", uu, PIN)}" opacity="{f(1 - fog)}"/>'
                     f'<path d="{self.quad(uu + 0.12, uu + 0.3, CORN, PIN, 0.2)}" fill="{C("shadow")}" opacity="0.35"/>')
        pass

    def canopy(self, u0, u1, fog):
        """The platform canopy: iron scroll brackets on the pilasters, a sloping roof of corrugated
        sheet seen from above, a scalloped fascia; its coloured shadow on wall and platform."""
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        DEP, HW, HE = 3.4, 5.7, 5.05
        # cast shadow on the wall under the canopy and on the platform
        sh = P2([self.F(u0, HW), self.F(u1, HW), self.F(u1, 3.7), self.F(u0, 3.7)])
        self.add(f'<path d="{sh}" fill="{C("shadow")}" opacity="0.45"/>')
        br = []
        u = u0 + 0.0
        while u < u1:
            a = self.F(u, 3.5, 0.15)
            m = self.F(u, 4.75, 1.2)
            c = self.F(u, HE - 0.05, DEP - 0.3)
            s1 = self.F(u, 4.4, 0.6)
            br.append(f"M{f(a[0])} {f(a[1])}Q{f(m[0])} {f(m[1])} {f(c[0])} {f(c[1])}")
            br.append(PL([self.F(u, HW - 0.2, 0.15), self.F(u, HE, DEP - 0.2)]))
            r = 0.28 * self.k(u)
            br.append(f"M{f(s1[0])} {f(s1[1])}a{f(r)} {f(r)} 0 1 1 {f(r)} {f(-r)}")
            u += 4.5
        k = self.k((u0 + u1) / 2)
        self.add(f'<path d="{"".join(br)}" fill="none" stroke="{C("iron")}" stroke-width="{f(max(0.9, 0.09 * k))}" stroke-linecap="round"/>')
        roof = P2([self.F(u0, HW, 0.0), self.F(u1, HW, 0.0), self.F(u1, HE, DEP), self.F(u0, HE, DEP)])
        self.add(f'<path d="{roof}" fill="{lin(self.doc, [(0, C("canopy_hi"), 1), (1, C("canopy"), 1)], self.F(u0, HW), self.F(u1, HE, DEP))}"/>')
        for a_, b_ in ((u1 - 14, u1), (u1 - 28, u1 - 14)):
            q = P2([self.F(a_, HW, 0.0), self.F(b_, HW, 0.0), self.F(b_, HE, DEP), self.F(a_, HE, DEP)])
            m = (a_ + b_) / 2
            self.add(f'<path d="{q}" fill="{self._pat_pts("sheet", self.F(m, HW, 0), self.F(m + 1, HW, 0), self.F(m, HW - 0.19, 1.0))}" opacity="0.8"/>')
        rib = []
        u = u0
        while u < u1:
            rib.append(PL([self.F(u, HW, 0.0), self.F(u, HE, DEP)]))
            u += 0.75
        self.add(f'<path d="{"".join(rib)}" fill="none" stroke="{C("canopy", -3)}" stroke-width="{f(max(0.6, 0.04 * k))}" opacity="0.6"/>')
        fas = P2([self.F(u0, HE, DEP), self.F(u1, HE, DEP), self.F(u1, HE - 0.32, DEP), self.F(u0, HE - 0.32, DEP)])
        sc = []
        u = u0
        while u < u1:
            a, b, c = self.F(u, HE - 0.32, DEP), self.F(u + 0.25, HE - 0.48, DEP), self.F(u + 0.5, HE - 0.32, DEP)
            sc.append(f"M{f(a[0])} {f(a[1])}Q{f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])}Z")
            u += 0.5
        rv = []
        u = u0
        while u < u1:
            x, y = self.F(u, HE - 0.16, DEP)
            rv.append(f"M{g1(x)} {g1(y)}h0.1")
            u += 0.5
        self.add(f'<path d="{fas}" fill="{C("canopy", -2)}"/><path d="{"".join(sc)}" fill="{C("canopy", -4)}"/>'
                 f'<path d="{"".join(rv)}" stroke="{C("canopy_hi", 2)}" stroke-width="{f(max(0.8, 0.05 * k))}" stroke-linecap="round" fill="none"/>'
                 f'<path d="{PL([self.F(u0, HE, DEP), self.F(u1, HE, DEP)])}" stroke="{C("canopy_hi", 3)}" stroke-width="{f(max(0.8, 0.06 * k))}"/>')
        # lamps hung from the fascia every second bay
        lamps = []
        u = u0 + 2.25
        while u < u1:
            x, y = self.F(u, HE - 0.9, DEP - 0.4)
            kk = self.k(u, DEP)
            lamps.append((x, y, kk))
            u += 9.0
        out = []
        for x, y, kk in lamps:
            out.append(f'<path d="M{f(x)} {f(y - 0.55 * kk)}v{f(0.3 * kk)}" stroke="{C("iron")}" stroke-width="{f(max(0.7, 0.05 * kk))}"/>'
                       f'<path d="M{f(x - 0.16 * kk)} {f(y - 0.25 * kk)}h{f(0.32 * kk)}l{f(-0.05 * kk)} {f(0.3 * kk)}h{f(-0.22 * kk)}Z" fill="{self.C("lamp") if self.night else C("iron")}"/>')
            if self.night:
                out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(2.6 * kk)}" fill="{rad(self.doc, [(0, self.C("lamp"), 0.55), (0.3, self.C("lamp"), 0.18), (1, self.C("lamp"), 0)], (x, y), 2.6 * kk)}"/>')
        self.add("".join(out))

    def end_pavilion(self, u0, u1):
        """The two-storey pavilion closing the wing at the far end; its end wall faces the light."""
        Zm = self.Zu(u0)
        fog = self.fogZ(Zm)
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        H1 = 10.2
        self.roof(u0, u1, H1, 0.0, -9.0, 2.6, fog)
        self.add(f'<path d="{self.quad(u0, u1, 0.0, H1)}" fill="{C("pl")}"/>')
        ops = []
        for uc in (u0 + 2.0, u0 + 6.0):
            ops.append(P2(self.arch_pts(uc, 0.75, 1.0, 3.3)))
            ops.append(P2(self.arch_pts(uc, 0.6, 6.0, 8.2)))
        self.add(f'<path d="{"".join(ops)}" fill="{C("hole")}"/>')
        self.add(f'<path d="{self.quad(u0 - 0.15, u1 + 0.15, H1 - 0.6, H1, 0.2)}" fill="{C("trim")}"/>'
                 f'<path d="{self.quad(u0, u1, 5.0, 5.3, 0.1)}" fill="{C("trim")}"/>')
        mer = []
        u = u0
        while u < u1:
            mer.append(self.quad(u, u + 0.3, H1, H1 + 0.32, 0.1))
            u += 0.6
        self.add(f'<path d="{"".join(mer)}" fill="{C("pl")}"/>'
                 f'<path d="{self.quad(u0 - 0.3, u0 + 0.3, H1, H1 + 1.4, 0.2)}{self.quad(u1 - 0.3, u1 + 0.3, H1, H1 + 1.4, 0.2)}" fill="{C("brick")}"/>')

    def window(self, uc, half, h0, hs, w, fog, lit=False, twin=False):
        """A round-arched window: archivolt (lit on its upper-left), a deep reveal (the jamb facing
        the light lit, the soffit in shade), a sash of 2 x 3 panes and a fanlight with radial bars,
        the sash's shadow on the glass, a sky gleam on the upper panes, sill and keystone."""
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        k = self.k(uc, w)
        out = []
        outer = self.arch_pts(uc, half + 0.22, h0, hs, w)
        out.append(f'<path d="{P2(outer)}" fill="{C("trim")}"/>')
        out.append(f'<path d="{PL(self.arc_line(uc, half + 0.2, hs, w, 10)[:6])}" fill="none" stroke="{C("pl_lit", 3)}" stroke-width="{f(max(0.7, 0.07 * k))}"/>')
        rev = self.arch_pts(uc, half, h0, hs, w)
        out.append(f'<path d="{P2(rev)}" fill="{C("pl_shd")}"/>')
        D = 0.3
        g0 = self.arch_pts(uc + 0.1, half - 0.1, h0 + 0.04, hs - 0.06, w - D)
        if lit:
            out.append(f'<path d="{P2(g0)}" fill="{self.C("lamp")}"/>')
            out.append(f'<path d="{P2(self.arch_pts(uc + 0.1, half - 0.1, h0 + 0.04, h0 + 0.6, w - D, n=4))}" fill="{self.C("lamp", 0, -3)}" opacity="0.5"/>')
        else:
            gx0, gy0 = self.F(uc, hs + half, w)
            gx1, gy1 = self.F(uc, h0, w)
            out.append(f'<path d="{P2(g0)}" fill="{lin(self.doc, [(0, C("glass_hi"), 1), (0.3, C("glass"), 1), (1, C("hole"), 1)], (gx0, gy0), (gx1, gy1))}"/>')
            # the sash's shadow along the top and the lit-side jamb
            out.append(f'<path d="{PL(self.arc_line(uc + 0.1, half - 0.18, hs - 0.06, w - D, 10))}" fill="none" stroke="{C("hole")}" stroke-width="{f(max(0.8, 0.1 * k))}" opacity="0.7"/>')
            gl = P2([self.F(uc - half + 0.2, hs - 0.2, w - D), self.F(uc - half + 0.45, hs - 0.2, w - D), self.F(uc - half + 0.2, hs - 0.9, w - D)])
            out.append(f'<path d="{gl}" fill="{C("glass_hi", 3)}" opacity="0.5"/>')
        bw = max(0.6, 0.055 * k)
        ww = w - D
        bars = [PL([self.F(uc + 0.05, h0, ww), self.F(uc + 0.05, hs, ww)]), PL([self.F(uc - half + 0.1, hs, ww), self.F(uc + half, hs, ww)])]
        for t in (1 / 3, 2 / 3):
            hh = h0 + (hs - h0) * t
            bars.append(PL([self.F(uc - half + 0.1, hh, ww), self.F(uc + half, hh, ww)]))
        for j in (1, 2, 3):
            a = math.pi * j / 4
            bars.append(PL([self.F(uc + 0.05, hs, ww), self.F(uc + 0.05 - (half - 0.1) * math.cos(a), hs + (half - 0.1) * math.sin(a), ww)]))
        bars.append(PL(self.arc_line(uc + 0.05, (half - 0.1) * 0.45, hs, ww, 6)))
        out.append(f'<path d="{"".join(bars)}" fill="none" stroke="{C("frame") if not lit else self.C("pl_shd")}" stroke-width="{f(bw)}"/>')
        # the jamb facing the light, lit; the soffit's shadow
        out.append(f'<path d="{P2([self.F(uc + half, h0, w), self.F(uc + half, hs, w), self.F(uc + half - 0.05, hs, ww), self.F(uc + half - 0.05, h0, ww)])}" fill="{C("pl_lit", 2)}"/>')
        out.append(f'<path d="{self.quad(uc - half - 0.32, uc + half + 0.32, h0 - 0.2, h0, w + 0.14)}" fill="{C("pl_lit")}"/>'
                   f'<path d="{self.quad(uc - half - 0.32, uc + half + 0.32, h0 - 0.32, h0 - 0.2, w + 0.1)}" fill="{C("shadow")}" opacity="0.5"/>'
                   f'<path d="{self.quad(uc - 0.15, uc + 0.15, hs + half + 0.02, hs + half + 0.42, w + 0.06)}" fill="{C("pl_lit", 1)}"/>')
        return "".join(out)

    def brick_patch(self, uc, hc, rw, rh, w, seed, fog):
        """Plaster fallen away round a window: an irregular patch of brick, a lit lip of plaster on
        its lower right edge and a shadow on the upper left (the plaster stands proud)."""
        rnd = random.Random(seed)
        pts = []
        for j in range(14):
            a = 2 * math.pi * j / 14
            rr = rnd.uniform(0.65, 1.0)
            pts.append(self.F(uc + math.cos(a) * rw * rr, hc + math.sin(a) * rh * rr, w))
        dd = f"M{g1(pts[0][0])} {g1(pts[0][1])}" + smooth(pts, closed=True) + "Z"
        return (f'<path d="{dd}" fill="{self.pat("brick", uc, hc, w)}"/>'
                f'<path d="{dd}" fill="none" stroke="{self.C("pl_lit", fog, 1)}" stroke-width="{f(max(0.8, 0.06 * self.k(uc, w)))}" opacity="0.7"/>')

    def roof(self, u0, u1, h0, wf, wb, rise, fog, hip=True):
        """A hipped tile roof over [u0, u1] x [wb, wf] from eave height h0, rising `rise` to the
        ridge: the slope turned to us in tiles laid in its own plane (courses along the eave), the
        hip end turned to us darker, the ridge capped, the eave casting its shadow line."""
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        wm = (wf + wb) / 2
        dep = (wf - wb) / 2
        r0, r1 = (u0 + dep, h0 + rise, wm), (u1 - dep if hip else u1, h0 + rise, wm)
        e = [(u0, h0, wf), (u1, h0, wf), (u1, h0, wb), (u0, h0, wb)]
        P = lambda q: self.F(q[1 - 1 + 0], q[1], q[2]) if False else self.F(q[0], q[1], q[2])
        back = P2([P(e[3]), P(e[2]), P(r1), P(r0)])
        self.add(f'<path d="{back}" fill="{C("tile_shd")}"/>')
        right = P2([P(e[1]), P(e[2]), P(r1)])
        self.add(f'<path d="{right}" fill="{C("tile_shd", 1)}"/>')
        front = P2([P(e[0]), P(e[1]), P(r1), P(r0)])
        self.add(f'<path d="{front}" fill="{lin(self.doc, [(0, C("tile_lit"), 1), (1, C("tile"), 1)], P(e[0]), P(e[1]))}"/>')
        k = self.k((u0 + u1) / 2, wf)
        if k * 0.35 > 2.5:
            m = (u0 + u1) / 2
            o = self.F(m, h0 + rise, wm)
            sl = math.hypot(dep, rise)
            down = self.F(m, h0 + rise - rise / sl, wm + dep / sl)
            fill = self._pat_pts("tiles", o, self.F(m + 1, h0 + rise, wm), down)
            self.add(f'<path d="{front}" fill="{fill}" opacity="{f(0.9 * (1 - fog))}"/>')
        left = P2([P(e[0]), P(e[3]), P(r0)])
        self.add(f'<path d="{left}" fill="{C("tile_lit", 1)}"/>')
        self.add(f'<path d="{PL([P(e[0]), P(r0), P(r1), P(e[1])])}" fill="none" stroke="{C("tile_lit", 3)}" stroke-width="{f(max(0.8, 0.12 * k))}" stroke-linejoin="round"/>'
                 f'<path d="{PL([P(e[0]), P(e[1])])}" fill="none" stroke="{C("shadow")}" stroke-width="{f(max(0.8, 0.2 * k))}" opacity="0.6"/>')

    def block_volume(self):
        """The block's roofs and its right flank (two-point depth): hipped roofs over the side parts,
        the pavilion's gable roof running back, the right side wall turned to us in shade."""
        Zm = self.Zu(12.0)
        fog = self.fogZ(Zm)
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        DEPTH = 13.0
        self.roof(0.2, 10.5, 14.4, -0.2, -DEPTH, 3.0, fog)
        self.roof(19.5, 23.3, 14.2, -0.2, -DEPTH, 2.4, fog)
        # the pavilion's gable roof: ridge from the gable back to the rear gable
        um, hp, hc = 15.0, 19.4, 15.0
        a, b = (10.6, hc, 0.6), (19.4, hc, 0.6)
        ra, rb = (um, hp, 0.6), (um, hp, -DEPTH)
        aa, bb = (10.6, hc, -DEPTH), (19.4, hc, -DEPTH)
        L = P2([self.F(*a), self.F(*ra), self.F(*rb), self.F(*aa)])
        R = P2([self.F(*b), self.F(*ra), self.F(*rb), self.F(*bb)])
        self.add(f'<path d="{L}" fill="{C("tile_lit")}"/><path d="{R}" fill="{C("tile_shd")}"/>')
        k = self.k(um)
        if not self.mirror:
            o = self.F(um, hp, 0.6)
            sl = math.hypot(4.4, 4.4)
            self.add(f'<path d="{R}" fill="{self._pat_pts("tiles", o, self.F(um, hp, -0.4), self.F(um + 4.4 / sl, hp - 4.4 / sl, 0.6))}" opacity="0.85"/>')
        self.add(f'<path d="{PL([self.F(*ra), self.F(*rb)])}" stroke="{C("tile_lit", 3)}" stroke-width="{f(0.18 * k)}"/>')
        # right flank of the block above the right wing
        side = P2([self.F(23.5, 7.6, 0.0), self.F(23.5, 7.6, -DEPTH), self.F(23.5, 14.2, -DEPTH), self.F(23.5, 14.2, 0.0)])
        self.add(f'<path d="{side}" fill="{C("pl_shd", 1.5)}"/>')
        sw = []
        for wv in (-3.2, -6.5, -9.8):
            pts = [(23.5, 9.9, wv + 0.55), (23.5, 12.3, wv + 0.55)] + [(23.5, 12.3 + 0.55 * math.sin(math.pi * j / 10), wv + 0.55 * math.cos(math.pi * j / 10)) for j in range(1, 10)] + [(23.5, 12.3, wv - 0.55), (23.5, 9.9, wv - 0.55)]
            sw.append(P2([self.F(*q) for q in pts]))
        lit = self.night
        self.add(f'<path d="{"".join(sw)}" fill="{self.C("lamp") if lit else C("hole")}" opacity="0.85"/>')
        self.add(f'<path d="{PL([self.F(23.5, 14.2, 0.0), self.F(23.5, 14.2, -DEPTH)])}" stroke="{C("trim")}" stroke-width="{f(0.5 * k)}"/>')

    def block(self):
        d = self.doc
        Zm = self.Zu(12.0)
        fog = self.fogZ(Zm)
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        k = self.k(12.0)
        sections = [(0.0, 10.5, 14.4, 0.0, [1.9, 5.25, 8.6], 0.62), (10.5, 19.5, 15.0, 0.6, [12.0, 14.0, 16.0, 18.0], 0.5), (19.5, 23.5, 14.2, 0.0, [21.5], 0.62)]
        DEPTH = 13.0
        # left return wall of the block, above the wing, facing the light
        self.block_volume()
        allwall = []
        for (u0, u1, hc, wf, axes, half) in sections:
            fw = wf
            wall = self.quad(u0, u1, 0.0, hc, fw)
            allwall.append(wall)
            g = lin(d, [(0, C("pl_lit")), (0.35, C("pl")), (1, C("pl", -1.2))] and [(0, C("pl_lit"), 1), (0.35, C("pl"), 1), (1, C("pl", -1.2), 1)], self.F(u0, hc, fw), self.F(u1, 0, fw))
            self.add(f'<path d="{wall}" fill="{g}"/>')
            if wf:   # the pavilion projects: its left return is lit, a shadow falls to its right
                ret = P2([self.F(u0, 0, 0.0), self.F(u0, 0, wf), self.F(u0, hc, wf), self.F(u0, hc, 0.0)])
                self.add(f'<path d="{ret}" fill="{C("pl_lit", 2)}"/>')
                rr = P2([self.F(u1, 0, 0.0), self.F(u1, 0, wf), self.F(u1, hc, wf), self.F(u1, hc, 0.0)])
                self.add(f'<path d="{rr}" fill="{C("pl_shd")}"/>')
                shd = P2([self.F(u1, 0, 0.0), self.F(u1 + 1.1, 0, 0.0), self.F(u1 + 1.1, hc - 0.6, 0.0), self.F(u1, hc, 0.0)])
                self.add(f'<path d="{shd}" fill="{C("shadow")}" opacity="0.5"/>')
            self.add(self.grain(wall, Zm, C("pl_shd"), 0.2))
            # rusticated plinth of dressed stone, string courses
            self.add(f'<path d="{self.quad(u0, u1, 0.0, 1.0, fw + 0.06)}" fill="{self.pat("ashlar", u0, 1.0, fw + 0.06)}"/>')
            # rustication lines on the ground storey
            rl = "".join(PL([self.F(u0, hh, fw), self.F(u1, hh, fw)]) for hh in (1.6, 2.2, 2.8, 3.4, 4.0, 4.6))
            self.add(f'<path d="{rl}" fill="none" stroke="{C("pl_shd")}" stroke-width="{f(max(0.6, 0.03 * k))}" opacity="0.45"/>')
            if wf:
                pr = random.Random(77)
                patches = "".join(self.brick_patch(ac + pr.uniform(-0.2, 0.3), 7.0 + pr.uniform(-0.6, 0.6), 0.9 + pr.uniform(0, 0.4), 1.6 + pr.uniform(0, 0.8), fw + 0.01, int(ac * 13), fog)
                                  for ac in axes[1:3])
                patches += self.brick_patch(axes[3] + 0.4, 11.3, 0.8, 1.2, fw + 0.01, 5, fog) + self.brick_patch(axes[0] - 0.3, 2.6, 0.7, 1.0, fw + 0.01, 6, fog)
                self.add(patches)
            for hh in (5.0, 9.4):
                self.add(f'<path d="{self.quad(u0, u1, hh, hh + 0.32, fw + 0.12)}" fill="{C("trim")}"/>'
                         f'<path d="{self.quad(u0, u1, hh - 0.14, hh, fw + 0.06)}" fill="{C("pl_shd")}" opacity="0.6"/>')
            # windows: ground (doors), first, second floor
            rnd = random.Random(int(u0 * 10) + 1)
            for fl_, (h0, hs) in enumerate(((0.0, 3.5), (5.7, 8.1), (10.0, 12.2))):
                for ac in axes:
                    hf = half * (1.15 if fl_ == 0 else 1.0)
                    lit = self.night and rnd.random() < (0.55 if fl_ else 0.8)
                    if wf and fl_ > 0:
                        self.add(self.window(ac, hf, h0, hs + 0.4, fw, fog, lit))
                    else:
                        self.add(self.window(ac, hf, h0, hs, fw, fog, lit))
            # weathering: grime washed down from each sill and from the cornice (the photos' streaks)
            if not self.mirror:
                sr = random.Random(int(u0) + 31)
                st = []
                for ac in axes:
                    for h0 in (5.7, 10.0):
                        for _ in range(3):
                            uu = ac + sr.uniform(-0.6, 0.6)
                            L = sr.uniform(0.8, 2.6)
                            wd_ = sr.uniform(0.05, 0.16)
                            st.append(self.quad(uu, uu + wd_, h0 - 0.35 - L, h0 - 0.35, fw + 0.01))
                for _ in range(int((u1 - u0) * 1.6)):
                    uu = sr.uniform(u0 + 0.3, u1 - 0.3)
                    L = sr.uniform(0.5, 2.0)
                    st.append(self.quad(uu, uu + sr.uniform(0.04, 0.12), hc - 1.25 - L, hc - 1.25, fw + 0.01))
                g = lin(d, [(0, C("pl_dk"), 0.35), (1, C("pl_dk"), 0.0)], self.F(u0, hc, fw), self.F(u0, hc - 4.5, fw))
                self.add(f'<path d="{"".join(st)}" fill="{C("pl_dk")}" opacity="0.13"/>')
                # scored plaster joints of the ground storey (rustication blocks)
                vj = []
                for hh0, hh1, off in ((1.0, 1.6, 0), (1.6, 2.2, 0.6), (2.2, 2.8, 0), (2.8, 3.4, 0.6), (3.4, 4.0, 0), (4.0, 4.6, 0.6)):
                    uu = u0 + off + 0.3
                    while uu < u1 - 0.3:
                        vj.append(PL([self.F(uu, hh0, fw), self.F(uu, hh1, fw)]))
                        uu += 1.2
                self.add(f'<path d="{"".join(vj)}" fill="none" stroke="{C("pl_shd")}" stroke-width="{f(max(0.6, 0.03 * k))}" opacity="0.4"/>')
            # pilaster strips at the corners
            pl = self.quad(u0, u0 + 0.45, 0.0, hc, fw + 0.1) + self.quad(u1 - 0.45, u1, 0.0, hc, fw + 0.1)
            self.add(f'<path d="{pl}" fill="{C("pl_lit")}"/>'
                     f'<path d="{self.quad(u1 - 0.12, u1, 0.0, hc, fw + 0.1)}" fill="{C("pl_shd")}" opacity="0.6"/>')
            # corbel-arch frieze, cornice, merlons
            fr_ = []
            u = u0 + 0.5
            while u + 0.45 < u1 - 0.4:
                fr_.append(P2(self.arch_pts(u + 0.22, 0.2, hc - 1.15, hc - 0.95, fw)))
                u += 0.62
            self.add(f'<path d="{self.quad(u0, u1, hc - 1.25, hc - 0.55, fw + 0.08)}" fill="{C("trim")}"/>'
                     f'<path d="{"".join(fr_)}" fill="{C("pl_shd")}"/>'
                     f'<path d="{self.quad(u0 - 0.15, u1 + 0.15, hc - 0.55, hc, fw + 0.3)}" fill="{C("trim", 1)}"/>'
                     f'<path d="{self.quad(u0 - 0.15, u1 + 0.15, hc - 0.7, hc - 0.55, fw + 0.2)}" fill="{C("pl_shd")}" opacity="0.8"/>')
            mer = []
            u = u0 + 0.1
            while u < u1 - 0.2:
                mer.append(self.quad(u, u + 0.34, hc, hc + 0.42, fw + 0.2))
                u += 0.66
            self.add(f'<path d="{"".join(mer)}" fill="{C("pl", 0.5)}"/>')
        # the gable of the pavilion
        u0, u1, hc = 10.5, 19.5, 15.0
        um, hp = 15.0, 19.6
        tri = [self.F(u0 + 0.2, hc, 0.6), self.F(u1 - 0.2, hc, 0.6), self.F(um, hp, 0.6)]
        self.add(f'<path d="{P2(tri)}" fill="{lin(d, [(0, C("pl_lit"), 1), (1, C("pl"), 1)], self.F(u0, hp, 0.6), self.F(u1, hc, 0.6))}"/>')
        teeth = []
        for sgn, ue in ((1, u0 + 0.2), (-1, u1 - 0.2)):
            for j in range(1, 11):
                t = j / 11
                uu = ue + sgn * (um - ue) * sgn * t if sgn > 0 else ue - (ue - um) * t
                hh = hc + (hp - hc) * t
                teeth.append(P2(self.arch_pts(uu - sgn * 0.05, 0.17, hh - 1.3, hh - 0.75, 0.6, n=8)))
        self.add(f'<path d="{"".join(teeth)}" fill="{C("pl_shd")}"/>')
        coping = PL([self.F(u0 - 0.1, hc + 0.1, 0.9), self.F(um, hp + 0.25, 0.9), self.F(u1 + 0.1, hc + 0.1, 0.9)])
        self.add(f'<path d="{coping}" fill="none" stroke="{C("trim", 1)}" stroke-width="{f(0.45 * k)}" stroke-linejoin="round"/>')
        # quatrefoil roundel
        qx, qy = self.F(um, hc + 2.1, 0.62)
        r = 0.42 * k
        q = "".join(f'<circle cx="{f(qx + dx * r * 0.55)}" cy="{f(qy + dy * r * 0.55)}" r="{f(r * 0.5)}"/>' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        self.add(f'<circle cx="{f(qx)}" cy="{f(qy)}" r="{f(r * 1.25)}" fill="{C("trim")}"/><g fill="{C("pl_shd")}">{q}</g>')
        # pinnacles at the pavilion corners and the block corners, a finial at the apex
        pins = []
        for uu, hh, wv in ((0.0, 14.4, 0.0), (10.5, 15.0, 0.6), (19.5, 15.0, 0.6), (23.5, 14.2, 0.0)):
            top = hh + 2.0
            pins.append(f'<path d="{self.quad(uu - 0.38, uu + 0.38, hh, top, wv + 0.3)}" fill="{C("trim")}"/>'
                        f'<path d="{self.quad(uu + 0.12, uu + 0.38, hh, top, wv + 0.3)}" fill="{C("pl_shd")}" opacity="0.55"/>'
                        f'<path d="{self.quad(uu - 0.5, uu + 0.5, top, top + 0.3, wv + 0.3)}" fill="{C("pl_lit", 2)}"/>'
                        f'<path d="{P2([self.F(uu - 0.32, top + 0.3, wv + 0.3), self.F(uu + 0.32, top + 0.3, wv + 0.3), self.F(uu, top + 1.0, wv + 0.3)])}" fill="{C("brick")}"/>')
        ax, ay = self.F(um, hp + 0.2, 0.9)
        pins.append(f'<path d="{self.quad(um - 0.3, um + 0.3, hp, hp + 1.4, 0.9)}" fill="{C("trim")}"/>'
                    f'<path d="{PL([self.F(um, hp + 1.4, 0.9), self.F(um, hp + 2.4, 0.9)])}{PL([self.F(um - 0.35, hp + 2.0, 0.9), self.F(um + 0.35, hp + 2.0, 0.9)])}" stroke="{C("iron")}" stroke-width="{f(0.1 * k)}"/>')
        self.add("".join(pins))
        if self.night:   # warm light spilling on the block from the platform lamps
            x, y = self.F(12.0, 2.0, 2.0)
            self.add(f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(14 * k)}" ry="{f(6 * k)}" fill="{rad(d, [(0, self.C("lamp"), 0.3), (1, self.C("lamp"), 0)], (x, y), 14 * k)}"/>')

    def platform(self):
        d = self.doc
        u0, u1 = -78.0, 48.0
        Zm = self.Zu(-10)
        fog = self.fogZ(Zm) * 0.6
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        PH, PW = 0.9, 6.2
        top = P2([self.F(u0, PH, 0.0), self.F(u1, PH, 0.0), self.F(u1, PH, PW), self.F(u0, PH, PW)])
        self.add(f'<path d="{top}" fill="{lin(d, [(0, C("plat", 1), 1), (1, C("plat", -1), 1)], self.F(u0, PH, PW), self.F(u1, PH, PW))}"/>')
        for a_, b_ in ((-12, 4), (4, 20), (20, 48)):
            q = P2([self.F(a_, PH, 0.0), self.F(b_, PH, 0.0), self.F(b_, PH, PW - 0.75), self.F(a_, PH, PW - 0.75)])
            self.add(f'<path d="{q}" fill="{self.pat("paving", (a_ + b_) / 2, PH, PW / 2, plane="ground")}" opacity="0.85"/>')
        # the canopy's shadow on the platform
        sh = P2([self.F(-70, PH, 0.0), self.F(36.0, PH, 0.0), self.F(36.0, PH, 2.6), self.F(-70, PH, 2.6)])
        self.add(f'<path d="{sh}" fill="{C("shadow")}" opacity="0.4"/>')
        flag = []
        u = u0
        while u < u1:
            flag.append(PL([self.F(u, PH, 0.6), self.F(u, PH, PW - 0.5)]))
            u += 1.5
        k = self.k(10, PW)
        self.add(f'<path d="{"".join(flag)}" fill="none" stroke="{C("plat_edge")}" stroke-width="{f(max(0.5, 0.03 * k))}" opacity="0.5"/>')
        edge = P2([self.F(u0, PH, PW), self.F(u1, PH, PW), self.F(u1, 0.0, PW), self.F(u0, 0.0, PW)])
        self.add(f'<path d="{edge}" fill="{C("plat_edge", -2)}"/>'
                 f'<path d="{P2([self.F(u0, PH, PW - 0.3), self.F(u1, PH, PW - 0.3), self.F(u1, PH, PW), self.F(u0, PH, PW)])}" fill="{C("plat", 3)}"/>'
                 f'<path d="{P2([self.F(u0, PH, PW - 0.75), self.F(u1, PH, PW - 0.75), self.F(u1, PH, PW - 0.6), self.F(u0, PH, PW - 0.6)])}" fill="{self.C("gold")}" opacity="0.75"/>')
        cs = []
        u = u0
        while u < u1:   # coping stones
            cs.append(PL([self.F(u, PH, PW), self.F(u, 0.0, PW)]))
            u += 1.2
        self.add(f'<path d="{"".join(cs)}" fill="none" stroke="{C("plat_edge", -5)}" stroke-width="{f(max(0.5, 0.03 * k))}" opacity="0.6"/>')

    def tracks(self):
        d = self.doc
        plan = self.track_plan()
        near = [p for p in plan if p[1] < 2400]
        H = self.H
        # ballast beds, one per track, with a dark gravel stipple
        for wc in (-4.4, 0.0, 4.4):
            bed = self.ground_strip(near, wc - 2.2, wc + 2.2, 0.0)
            g = lin(d, [(0, self.C("ballast", 0.0), 1), (1, self.C("ballast", 0.7), 1)], (0, H), (0, self.cy))
            self.add(f'<path d="{bed}" fill="{g}"/>')
        pid = d.id("bp")
        s = max(4, round(0.006 * H))
        rnd = random.Random(2)
        dots = "".join(f'<circle cx="{f(rnd.uniform(0, s * 4))}" cy="{f(rnd.uniform(0, s * 2))}" r="{f(rnd.uniform(0.6, 1.5) * H / 2160)}"/>' for _ in range(24))
        d.defs.append(f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="{f(s * 4)}" height="{f(s * 2)}"><g fill="{self.C("ballast_d")}">{dots}</g></pattern>')
        allbed = "".join(self.ground_strip(near[:160], wc - 2.2, wc + 2.2, 0.0) for wc in (-4.4, 0.0, 4.4))
        self.add(f'<path d="{allbed}" fill="url(#{pid})" opacity="0.7"/>')
        # sleepers: drawn while they are wider than a pixel or two, then a tone
        for wc in (-4.4, 0.0, 4.4):
            sl = []
            pts = self.off(near, wc)
            s_acc = 0.0
            for i in range(1, len(near)):
                X, Z, th = near[i]
                step = math.dist(pts[i], pts[i - 1])
                s_acc += step
                if Z > 260:
                    break
                while s_acc > 0.65:
                    s_acc -= 0.65
                    nx, nz = -math.cos(th), math.sin(th)
                    tx, tz = math.sin(th), math.cos(th)
                    cx, cz = X + nx * wc, Z + nz * wc
                    q = [(cx + nx * 1.4, cz + nz * 1.4), (cx - nx * 1.4, cz - nz * 1.4), (cx - nx * 1.4 + tx * 0.24, cz - nz * 1.4 + tz * 0.24), (cx + nx * 1.4 + tx * 0.24, cz + nz * 1.4 + tz * 0.24)]
                    sl.append(P2([self.proj(a, 0.06, b) for a, b in q]))
            self.add(f'<path d="{"".join(sl)}" fill="{self.C("sleeper")}" opacity="0.85"/>')
        # rails: web in shade, head with the specular of the low sun, and the long glint
        for wc in (-4.4, 0.0, 4.4):
            for side in (-0.8, 0.8):
                pts = self.off(near, wc + side)
                web = P2([self.proj(X, 0.0, Z) for X, Z in pts] + [self.proj(X, 0.17, Z) for X, Z in pts][::-1])
                self.add(f'<path d="{web}" fill="{self.C("rail")}"/>')
                head = PL([self.proj(X, 0.17, Z) for X, Z in pts])
                self.add(f'<path d="{head}" fill="none" stroke="{self.C("rail_hi")}" stroke-width="{f(max(1.0, 0.0011 * H))}" opacity="0.9"/>')
        gl = []
        for wc in (-4.4, 0.0, 4.4):
            gl.append(PL([self.proj(X, 0.17, Z) for X, Z in self.off(near, wc - 0.8)][40:240]))
        x, y = self.proj(*self.off(near, 0)[150][:1], 0, self.off(near, 0)[150][1])


    def poles(self):
        """Telegraph poles between the tracks with two crossarms, the wires sagging between."""
        plan = self.track_plan()
        tops = [[], [], [], []]
        out = []
        s = 0
        for i, (X, Z, th) in enumerate(plan):
            if Z > 1800:
                break
            if i % 22 != 5 or i < 60:
                continue
            nx, nz = -math.cos(th), math.sin(th)
            px, pz = X + nx * 2.2, Z + nz * 2.2
            k = self.fl / pz
            fog = self.fogZ(pz)
            b, t = self.proj(px, 0, pz), self.proj(px, 8.5, pz)
            col = self.C("iron", min(0.9, fog + 0.35))
            arms = []
            for j, hh in enumerate((8.2, 7.4)):
                a1, a2 = self.proj(px - nx * 1.0, hh, pz - nz * 1.0), self.proj(px + nx * 1.0, hh, pz + nz * 1.0)
                arms.append(PL([a1, a2]))
                tops[2 * j].append(a1)
                tops[2 * j + 1].append(a2)
            out.append(f'<path d="{PL([b, t])}" stroke="{col}" stroke-width="{f(max(0.8, 0.22 * k))}"/>'
                       f'<path d="{"".join(arms)}" stroke="{col}" stroke-width="{f(max(0.6, 0.12 * k))}"/>')
        self.add("".join(out))
        wires = []
        for row in tops:
            if len(row) < 2:
                continue
            dd = f"M{f(row[0][0])} {f(row[0][1])}"
            for a, b in zip(row, row[1:]):
                sag = 0.18 * abs(a[0] - b[0]) * 0.08 + 1
                dd += f"Q{f((a[0] + b[0]) / 2)} {f((a[1] + b[1]) / 2 + sag)} {f(b[0])} {f(b[1])}"
            wires.append(dd)
        self.add(f'<path d="{"".join(wires)}" fill="none" stroke="{self.C("iron", 0.25)}" stroke-width="{f(max(0.7, 0.0006 * self.H))}" opacity="0.55"/>')

    # ================================================================ near: the town under the mirante
    # ================================================================ the Paraiba in front
    def bank_w(self, u):
        """The far bank of the river, w off the facade: parallel to the line, then curving toward us
        and out at the bottom of the frame (water turns back, never runs into the edge straight)."""
        return 21.0 + 0.012 * max(0.0, u - 36.0) ** 2

    def river_front(self):
        d, W, H = self.doc, self.W, self.H
        us = [-900 + i * 6.0 for i in range(150)] + [-6 + i * 0.5 for i in range(140)]
        pts = []
        for u in us:
            w = self.bank_w(u)
            if w > self.wc - 3.0 or self.world(u, w)[1] < 9.0:
                break
            pts.append(self.F(u, self.hw, w))
        pts = [p for p in pts if p[1] > self.cy - 2]
        water = P2(pts + [(pts[-1][0], H + 20), (-20, H + 20), (-20, pts[0][1])])
        cid = d.id("wv")
        d.defs.append(f'<clipPath id="{cid}"><path d="{water}"/></clipPath>')
        self.water_d, self.water_clip = water, cid
        # the water's own tone: the sky turned over, lighter at the far bank, deeper toward us
        g = lin(d, [(0, self.C("sky_hor"), 1), (0.35, self.C("river"), 1), (1, self.C("river_d"), 1)], (0, self.cy), (0, H))
        self.add(f'<path d="{water}" fill="{g}"/>')
        lx, ly = self.light
        self.add(f'<g clip-path="url(#{cid})"><ellipse cx="{f(lx)}" cy="{f(2 * self.cy - ly)}" rx="{f(0.16 * W)}" ry="{f(0.30 * H)}" fill="{rad(d, [(0, self.C("glow"), 0.55), (1, self.C("glow"), 0)], (lx, 2 * self.cy - ly), 0.3 * H)}"/></g>')

    def reflect(self, draw):
        """Draw the scene again turned over the water plane, clipped to the water, broken by a
        horizontal ripple displacement and faded toward the viewer."""
        d = self.doc
        n0 = len(d.body)
        self.mirror = True
        draw()
        self.mirror = False
        inner = "".join(d.body[n0:])
        del d.body[n0:]
        H, W = self.H, self.W
        pid = d.id("rs")
        rnd = random.Random(14)
        lines = []
        y = 0.0
        while y < H - self.cy:   # gaps get taller toward us (ripples seen closer)
            depth = y / (H - self.cy)
            hgt = 0.0012 * H + 0.006 * H * depth
            lines.append(f'<rect y="{g1(self.cy + y)}" width="{W}" height="{g1(hgt * rnd.uniform(0.3, 0.8))}" opacity="{f(rnd.uniform(0.4, 1))}"/>')
            y += hgt * rnd.uniform(1.6, 3.2)
        mid = d.id("rm")
        d.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="{lin(d, [(0, "#FFFFFF", 0.0), (0.04, "#FFFFFF", 0.8), (0.6, "#FFFFFF", 0.55), (1, "#FFFFFF", 0.25)], (0, self.cy), (0, H))}"/>'
                      f'<g fill="#000000">{"".join(lines)}</g></mask>')
        self.add(f'<g clip-path="url(#{self.water_clip})"><g mask="url(#{mid})">{inner}</g></g>')

    def water_surface(self):
        """Ripples on top of the reflection: lit lines and dark lines in perspective, longer and
        wider apart toward us; a sheen band where the light lies on the water."""
        d, W, H = self.doc, self.W, self.H
        rnd = random.Random(12)
        lt, dk = [], []
        y = self.cy + 2
        while y < H:
            depth = (y - self.cy) / (H - self.cy)
            for _ in range(int(3 + 9 * (1 - depth))):
                x = rnd.uniform(-0.05, 1.0) * W
                L = (0.004 + 0.05 * depth ** 1.4) * W * rnd.uniform(0.4, 1.3)
                (lt if rnd.random() < 0.55 else dk).append(f"M{f(x)} {f(y)}h{f(L)}")
            y += max(2.0, 0.0025 * H + depth ** 1.6 * 0.03 * H) * rnd.uniform(0.7, 1.3)
        sw = max(1.0, 0.0011 * H)
        self.add(f'<g clip-path="url(#{self.water_clip})"><path d="{"".join(lt)}" fill="none" stroke="{self.C("ripple")}" stroke-width="{f(sw)}" stroke-linecap="round" opacity="0.5"/>'
                 f'<path d="{"".join(dk)}" fill="none" stroke="{self.C("river_d", 0, -3)}" stroke-width="{f(sw * 1.4)}" stroke-linecap="round" opacity="0.35"/></g>')

    def embankment(self):
        """The far bank: a coursed stone wall from the yard down to the water, grass on its lip."""
        d = self.doc
        us = [-600 + i * 4.0 for i in range(148)] + [-8 + i * 0.5 for i in range(200)]
        top, bot = [], []
        for u in us:
            w = self.bank_w(u)
            if w > self.wc - 3.0 or self.world(u, w)[1] < 9.0:
                break
            top.append(self.F(u, 0.0, w))
            bot.append(self.F(u, self.hw, w))
        if self.mirror:
            pass
        face = P2(top + bot[::-1])
        self.add(f'<path d="{face}" fill="{lin(d, [(0, self.C("plat_edge", 0.6), 1), (1, self.C("pl_dk"), 1)], (0, self.cy), (0, self.H))}"/>')
        for uu in (-30.0, 0.0, 22.0):
            w_ = self.bank_w(uu)
            seg = [i for i, u in enumerate(us[:len(top)]) if abs(u - uu) < (16 if uu > -20 else 30)]
            if len(seg) > 2:
                q = P2([top[i] for i in seg] + [bot[i] for i in seg][::-1])
                self.add(f'<path d="{q}" fill="{self.pat("stone", uu, 0.0, w_)}" opacity="0.75"/>')
        courses = []
        for t in (0.33, 0.66):
            courses.append(PL([(a[0], a[1] + (b[1] - a[1]) * t) for a, b in zip(top, bot)]))
        joints = []
        for i in range(0, len(top), 3):
            a, b = top[i], bot[i]
            joints.append(PL([a, b]))
        self.add(f'<path d="{"".join(courses)}{"".join(joints)}" fill="none" stroke="{self.C("shadow")}" stroke-width="{f(max(0.6, 0.0007 * self.H))}" opacity="0.45"/>')
        self.add(f'<path d="{PL(top)}" fill="none" stroke="{self.C("grass")}" stroke-width="{f(0.003 * self.H)}" stroke-linejoin="round"/>')

    def ground_front(self):
        """Grass between the yard and the bank, where the bank curves away toward us."""
        us = [-600 + i * 4.0 for i in range(148)] + [-8 + i * 0.5 for i in range(200)]
        pts = []
        for u in us:
            w = self.bank_w(u)
            if w > self.wc - 3.0 or self.world(u, w)[1] < 9.0:
                break
            pts.append(self.F(u, 0.0, w))
        far = [self.F(u, 0.0, 19.4) for u in (-600, -300, -150, -60, -20, 0, 15, 30, 40, 48)]
        poly = P2(far + [(self.W + 50, self.H + 50), (pts[-1][0], self.H + 50)] + pts[::-1])
        self.add(f'<path d="{poly}" fill="{lin(self.doc, [(0, self.C("grass", 0.5), 1), (1, self.C("grass_d"), 1)], (0, self.cy), (0, self.H))}"/>')
        rnd = random.Random(8)
        tuft = []
        for _ in range(500):
            u = rnd.uniform(-60, 60)
            w = rnd.uniform(19.6, min(self.bank_w(u), self.wc - 4))
            if w >= self.bank_w(u):
                continue
            x, y = self.F(u, 0.0, w)
            k = self.k(u, w)
            hgt = rnd.uniform(0.25, 0.6) * k
            tuft.append(f"M{f(x)} {f(y)}l{f(-0.08 * k)} {f(-hgt)}M{f(x)} {f(y)}l{f(0.1 * k)} {f(-hgt * 0.8)}")
        self.add(f'<path d="{"".join(tuft)}" fill="none" stroke="{self.C("grass", 0, 3)}" stroke-width="{f(max(0.7, 0.0008 * self.H))}" opacity="0.7"/>')

    # ================================================================ near: bamboo on our bank
    def bamboo(self):
        """A clump of bamboo on our bank (touceira, the Paraiba's banks are lined with them): culms
        leaning toward the station, nodes, leaf sprays; backlit, with a rim of the light."""
        W, H = self.W, self.H
        rnd = random.Random(23)
        culms, nodes, leaves_d, leaves_l = [], [], [], []
        base = (0.035 * W, 1.03 * H)
        for i in range(11):
            x0 = base[0] + rnd.uniform(-0.03, 0.05) * W
            Lh = rnd.uniform(0.45, 0.78) * H
            lean = math.radians(rnd.uniform(8, 26))
            bend = rnd.uniform(0.25, 0.55)
            wd0 = rnd.uniform(0.0045, 0.0065) * H
            pts = []
            n = 24
            for j in range(n + 1):
                t = j / n
                a = lean + bend * t * t
                x = x0 + math.sin(a) * Lh * t
                y = base[1] - math.cos(a) * Lh * t
                pts.append((x, y, wd0 * (1 - 0.75 * t)))
            left = [(x - w_, y) for x, y, w_ in pts]
            right = [(x + w_, y) for x, y, w_ in pts]
            culms.append(P2(left + right[::-1]))
            for j in range(2, n, 2):
                x, y, w_ = pts[j]
                nodes.append(f"M{f(x - w_ * 1.3)} {f(y)}h{f(w_ * 2.6)}")
            for j in range(10, n + 1, 2):
                x, y, w_ = pts[j]
                for m in range(rnd.randint(2, 5)):
                    ang = math.radians(rnd.uniform(-10, 70) + (0 if m % 2 else 100))
                    L = rnd.uniform(0.028, 0.05) * H
                    wl = L * 0.13
                    tip = (x + math.cos(ang) * L, y + math.sin(ang) * L * 0.6 + L * 0.35)
                    mid = ((x + tip[0]) / 2, (y + tip[1]) / 2)
                    nx, ny = -(tip[1] - y) / L * wl, (tip[0] - x) / L * wl
                    leaf = f"M{f(x)} {f(y)}Q{f(mid[0] + nx)} {f(mid[1] + ny)} {f(tip[0])} {f(tip[1])}Q{f(mid[0] - nx)} {f(mid[1] - ny)} {f(x)} {f(y)}Z"
                    (leaves_l if rnd.random() < 0.3 else leaves_d).append(leaf)
        C = self.C
        self.add(f'<path d="{"".join(culms)}" fill="{lin(self.doc, [(0, C("tree"), 1), (1, C("tree_dk"), 1)], (0, 0.3 * H), (0, H))}"/>'
                 f'<path d="{"".join(nodes)}" fill="none" stroke="{C("tree_lit")}" stroke-width="{f(max(1, 0.0012 * H))}" opacity="0.8"/>'
                 f'<path d="{"".join(leaves_d)}" fill="{C("tree_shd")}"/>'
                 f'<path d="{"".join(leaves_l)}" fill="{C("tree")}"/>')

    def near_bank(self):
        """Our own bank closing the lower right: a low grassy lip over the water, never a wall."""
        W, H = self.W, self.H
        pts = [(0.56 * W, 1.02 * H), (0.62 * W, 0.975 * H), (0.72 * W, 0.955 * H), (0.84 * W, 0.93 * H), (0.95 * W, 0.90 * H), (1.02 * W, 0.885 * H), (1.02 * W, 1.02 * H)]
        d_ = f"M{g1(pts[0][0])} {g1(pts[0][1])}" + smooth(pts[:-1]) + f"L{g1(pts[-1][0])} {g1(pts[-1][1])}Z"
        self.add(f'<path d="{d_}" fill="{lin(self.doc, [(0, self.C("grass"), 1), (1, self.C("grass_d", 0, -3), 1)], (0, 0.88 * H), (0, H))}"/>'
                 f'<path d="M{g1(pts[0][0])} {g1(pts[0][1])}{smooth(pts[:-1])}" fill="none" stroke="{self.C("tree_lit")}" stroke-width="{f(0.002 * H)}" opacity="0.6"/>')
        rnd = random.Random(33)
        dk, lt = [], []
        for _ in range(220):
            x = rnd.uniform(0.6, 1.0) * W
            t = (x - 0.56 * W) / (0.46 * W)
            y = (0.975 - 0.09 * t) * H + rnd.uniform(0, 0.05) * H
            hgt = rnd.uniform(0.02, 0.07) * H
            b = rnd.uniform(-0.015, 0.03) * H
            (lt if rnd.random() < 0.4 else dk).append(f"M{g1(x)} {g1(y)}Q{g1(x + b * 0.3)} {g1(y - hgt * 0.6)} {g1(x + b)} {g1(y - hgt)}")
        sw = max(1.2, 0.0014 * H)
        self.add(f'<path d="{"".join(dk)}" fill="none" stroke="{self.C("tree_shd")}" stroke-width="{f(sw)}" stroke-linecap="round"/>'
                 f'<path d="{"".join(lt)}" fill="none" stroke="{self.C("grass", 0, 2)}" stroke-width="{f(sw * 0.8)}" stroke-linecap="round"/>')

    def reeds(self):
        """Reeds and grass on our bank at the bottom edge: the near plane, low and open."""
        W, H = self.W, self.H
        rnd = random.Random(29)
        dk, lt = [], []
        for _ in range(260):
            x = rnd.uniform(-0.02, 0.36) * W if rnd.random() < 0.7 else rnd.uniform(0.40, 0.62) * W
            y = H + 0.01 * H
            hgt = rnd.uniform(0.03, 0.12) * H * (1.3 if x < 0.2 * W else 0.7)
            bend = rnd.uniform(-0.02, 0.05) * H
            d_ = f"M{f(x)} {f(y)}Q{f(x + bend * 0.3)} {f(y - hgt * 0.6)} {f(x + bend)} {f(y - hgt)}"
            (lt if rnd.random() < 0.35 else dk).append(d_)
        sw = max(1.2, 0.0016 * H)
        self.add(f'<path d="{"".join(dk)}" fill="none" stroke="{self.C("tree_shd")}" stroke-width="{f(sw)}" stroke-linecap="round"/>'
                 f'<path d="{"".join(lt)}" fill="none" stroke="{self.C("grass")}" stroke-width="{f(sw * 0.8)}" stroke-linecap="round"/>')

    def grove_uw(self, u0, u1, w0, w1, n, seed, size=(8, 14)):
        rnd = random.Random(seed)
        items = []
        for _ in range(n):
            X, Z = self.world(rnd.uniform(u0, u1), rnd.uniform(w0, w1))
            if Z < 20:
                continue
            items.append((Z, X, rnd.uniform(*size), rnd.randrange(10 ** 6)))
        out = []
        for Z, X, s_, sd in sorted(items, reverse=True):
            fog = self.fogZ(Z)
            x, y = self.proj(X, 0, Z)
            k = self.fl / Z
            yt = self.proj(X, s_ * 0.62, Z)[1]
            out.append(self.trunk(x, y, yt, max(0.8, 0.22 * k), fog))
            out.append(self.crown(x, yt, s_ * 0.5 * k, sd, fog))
        self.add(f'<g filter="{self.leaf_filter(1.0)}">{"".join(out)}</g>' if not self.mirror else f'<g>{"".join(out)}</g>')

    # ================================================================ composition
    def hill_town(self):
        """The town climbing the hill behind the station (the photos from the mirante): a green
        rise, and houses on it, whitewashed walls and capa-e-canal tile roofs, hipped, lit from the left."""
        d = self.doc
        rnd = random.Random(61)
        # the rise: a ground surface stepping up behind the block
        pts = []
        hill = lambda u, ww: (-ww - 30) * 0.32 * (0.6 + 0.4 * math.sin(math.pi * min(1, max(0, (u + 110) / 150)))) + 1.5 * math.sin(u * 0.11)
        for i in range(41):
            u = -110 + i * 4.0
            pts.append(self.F(u, hill(u, -95), -95))
        base = [self.F(-110, 0, -95), self.F(50, 0, -95)]
        if not self.mirror:
            pass
        poly = P2([base[0]] + pts + [base[1]])
        fog = self.fogZ(self.Zu(0, -70))
        self.add(f'<path d="{poly}" fill="{lin(d, [(0, self.C("grass", fog), 1), (1, self.C("grass_d", fog), 1)], (0, min(p[1] for p in pts)), (0, self.cy))}"/>')
        houses = []
        for i in range(16):
            u = rnd.uniform(-75, -10)
            ww = rnd.uniform(-92, -55)
            houses.append((self.Zu(u, ww), u, ww, max(0.0, hill(u, ww))))
        for Z, u, ww, hh in sorted(houses, reverse=True):
            self.add(self.house(u, ww, hh, rnd.uniform(6, 10), rnd.uniform(5, 7), rnd.uniform(3.0, 4.0), rnd.randrange(999)))

    def house(self, u, ww, h0, wd, dp, ht, seed):
        """One town house aligned with the street (the facade axes): front wall, lit end wall,
        windows, and a hipped tile roof with courses and channels (pattern in the roof's own plane)."""
        fog = self.fogZ(self.Zu(u, ww))
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        rnd = random.Random(seed)
        P = lambda a, b, h: self.F(u + a, h0 + h, ww - b)   # a along, b back (away from us)
        out = [f'<path d="{P2([P(0, 0, 0), P(wd, 0, 0), P(wd, 0, ht), P(0, 0, ht)])}" fill="{C("hw")}"/>',
               f'<path d="{P2([P(0, 0, 0), P(0, dp, 0), P(0, dp, ht), P(0, 0, ht)])}" fill="{C("hw", 2)}"/>']
        win = []
        a = 0.9
        while a + 0.9 < wd:
            win.append(P2([P(a, 0, 0.9), P(a + 0.8, 0, 0.9), P(a + 0.8, 0, 2.3), P(a, 0, 2.3)]))
            a += 1.9
        lit = self.night and rnd.random() < 0.6
        out.append(f'<path d="{"".join(win)}" fill="{self.C("lamp") if lit else C("hole")}" opacity="0.85"/>')
        rh, ov = 2.0, 0.45
        e0, e1, e2, e3 = P(-ov, -ov, ht), P(wd + ov, -ov, ht), P(wd + ov, dp + ov, ht), P(-ov, dp + ov, ht)
        r0, r1 = P(dp / 2, dp / 2, ht + rh), P(wd - dp / 2, dp / 2, ht + rh)
        front = P2([e0, e1, r1, r0])
        out.append(f'<path d="{front}" fill="{C("tile")}"/>')
        k = self.k(u, ww)
        if k * 0.2 > 1.6 and not self.mirror:
            # the roof plane: x along the eave, y down the slope toward the eave
            mid = ((e0[0] + r0[0]) / 2, (e0[1] + r0[1]) / 2)
            ea = math.dist(e0, e1) / (wd + 2 * ov)
            ux, uy = (e1[0] - e0[0]) / math.dist(e0, e1) * ea, (e1[1] - e0[1]) / math.dist(e0, e1) * ea
            sl = math.dist(r0, P(dp / 2, -ov, ht))
            slope_len = math.hypot(dp / 2 + ov, rh)
            vx, vy = (e0[0] - r0[0]), (e0[1] - r0[1])
            vn = math.hypot(vx, vy)
            sc = sl / slope_len
            vx, vy = vx / vn * sc, vy / vn * sc
            fill = self._pat_pts("tiles", r0, (r0[0] + ux, r0[1] + uy), (r0[0] + vx, r0[1] + vy))
            out.append(f'<path d="{front}" fill="{fill}"/>')
        out.append(f'<path d="{P2([e0, r0, e3])}" fill="{C("tile_lit")}"/>')
        out.append(f'<path d="{PL([e0, e1])}" stroke="{C("hw_shd")}" stroke-width="{f(max(0.6, 0.12 * k))}" opacity="0.8"/>'
                   f'<path d="{PL([e0, r0, r1, e1])}" fill="none" stroke="{C("tile_lit", 2)}" stroke-width="{f(max(0.6, 0.1 * k))}" stroke-linejoin="round"/>')
        return "".join(out)

    # ================================================================ behind the station: the line
    def back_line(self):
        """The yard behind the station (seen around and over it): platforms, three tracks curving
        away into the valley at the left and out of the frame at the right, telegraph poles, the
        water tower, a semaphore mast and the island shelter on columns past the building's end."""
        d = self.doc
        plan = self.track_plan()
        far = [p for p in plan if p[1] < 3000]
        # the yard's ground and the platform behind
        self.add(f'<path d="{self.ground_strip(far, -9.0, 9.0)}" fill="{lin(d, [(0, self.C("grass", 0.3), 1), (1, self.C("grass", 0.8), 1)], (0, 0.75 * self.H), (0, self.cy))}"/>')
        for wc in (-4.4, 0.0, 4.4):
            self.add(f'<path d="{self.ground_strip(far, wc - 2.0, wc + 2.0)}" fill="{lin(d, [(0, self.C("ballast", 0.2), 1), (1, self.C("ballast", 0.8), 1)], (0, 0.75 * self.H), (0, self.cy))}"/>')
            for side in (-0.8, 0.8):
                pts = [self.proj(X, 0.17, Z) for X, Z in self.off(far, wc + side)]
                self.add(f'<path d="{PL(pts)}" fill="none" stroke="{self.C("rail_hi", 0.3)}" stroke-width="{f(max(1.0, 0.0009 * self.H))}" opacity="0.85"/>')
        sl = []
        for wc in (-4.4, 0.0, 4.4):
            pts = self.off(far, wc)
            for i in range(0, len(far) - 1):
                X, Z, th = far[i]
                if Z > 400:
                    break
                nx, nz = -math.cos(th), math.sin(th)
                cx, cz = pts[i]
                sl.append(PL([self.proj(cx + nx * 1.4, 0.05, cz + nz * 1.4), self.proj(cx - nx * 1.4, 0.05, cz - nz * 1.4)]))
        self.add(f'<path d="{"".join(sl)}" fill="none" stroke="{self.C("sleeper", 0.3)}" stroke-width="{f(max(0.8, 0.0012 * self.H))}" opacity="0.6"/>')
        self.poles()
        self.water_tower(40.0, -30.0)
        self.semaphore(-96.0, -18.0)
        self.shelter(34.0, 62.0)

    def water_tower(self, u, w):
        """A railway water tank on a riveted steel trestle (the steam era's caixa d'agua)."""
        fog = self.fogZ(self.Zu(u, w))
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        k = self.k(u, w)
        out = []
        legs = [(-2.2, -2.2), (2.2, -2.2), (2.2, 2.2), (-2.2, 2.2)]
        for a, b in legs:
            out.append(PL([self.F(u + a, 0, w + b), self.F(u + a * 0.8, 9.0, w + b * 0.8)]))
        for hh in (3.0, 6.0):
            for (a, b), (c, e) in zip(legs, legs[1:] + legs[:1]):
                out.append(PL([self.F(u + a * (1 - hh / 45), hh, w + b * (1 - hh / 45)), self.F(u + c * (1 - hh / 45), hh, w + e * (1 - hh / 45))]))
            out.append(PL([self.F(u - 2.2, hh - 3, w + 2.2), self.F(u + 2.0, hh, w + 2.0)]))
        self.add(f'<path d="{"".join(out)}" fill="none" stroke="{C("iron")}" stroke-width="{f(max(0.8, 0.12 * k))}"/>')
        # the tank: a cylinder, lit on the left, riveted bands, a conical lid
        n = 18
        top = [self.F(u + 2.6 * math.cos(2 * math.pi * i / n), 13.0, w + 2.6 * math.sin(2 * math.pi * i / n)) for i in range(n)]
        bot = [self.F(u + 2.6 * math.cos(2 * math.pi * i / n), 9.0, w + 2.6 * math.sin(2 * math.pi * i / n)) for i in range(n)]
        xs = [p[0] for p in top]
        i0, i1 = xs.index(min(xs)), xs.index(max(xs))
        body = P2([top[i0], top[i1], bot[i1], bot[i0]])
        self.add(f'<path d="{body}" fill="{lin(self.doc, [(0, C("canopy_hi", 2), 1), (0.4, C("canopy"), 1), (1, C("iron", 3), 1)], top[i0], top[i1])}"/>')
        bands = "".join(PL([self.F(u - 2.6, hh, w), self.F(u, hh, w + 2.6), self.F(u + 2.6, hh, w)]) for hh in (10.0, 11.0, 12.0))
        self.add(f'<path d="{bands}" fill="none" stroke="{C("iron")}" stroke-width="{f(max(0.6, 0.06 * k))}" opacity="0.6"/>')
        apex = self.F(u, 14.6, w)
        self.add(f'<path d="{P2([top[i0], apex, top[i1]])}" fill="{C("canopy", -1)}"/><path d="{P2([top[i0], apex, (apex[0], top[i0][1])])}" fill="{C("canopy_hi", 2)}"/>')

    def semaphore(self, u, w):
        """A semaphore signal: a lattice mast, the arm at danger-off, a lamp."""
        fog = self.fogZ(self.Zu(u, w))
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        k = self.k(u, w)
        b, t = self.F(u, 0, w), self.F(u, 9.0, w)
        a0, a1 = self.F(u, 8.0, w), self.F(u + 1.6, 8.6, w)
        self.add(f'<path d="{PL([b, t])}" stroke="{C("iron")}" stroke-width="{f(max(1, 0.18 * k))}"/>'
                 f'<path d="{PL([a0, a1])}" stroke="{self.C("cinnabar") if "cinnabar" in self.R else C("brick")}" stroke-width="{f(max(1, 0.25 * k))}"/>')
        lx, ly = self.F(u, 7.6, w)
        self.add(f'<circle cx="{g1(lx)}" cy="{g1(ly)}" r="{g1(max(1.2, 0.18 * k))}" fill="{self.C("lamp") if self.night else C("iron")}"/>')

    def shelter(self, u0, u1):
        """The island shelter past the building's end: cast-iron columns in two rows with spandrel
        brackets, a ridged roof of corrugated sheet; the depth between columns reads in perspective."""
        plan = self.track_plan()
        ws = (-9.5, -13.5)
        cols = []
        u = u0
        while u <= u1:
            cols.append(u)
            u += 4.5
        for wv in ws:
            fog = self.fogZ(self.Zu(u0, wv))
            C = lambda r, dk=0.0: self.C(r, fog, dk)
            out = []
            for uu in cols:
                k = self.k(uu, wv)
                out.append(f'<path d="{PL([self.F(uu, 0.9, wv), self.F(uu, 4.2, wv)])}" stroke="{C("iron")}" stroke-width="{f(max(0.8, 0.16 * k))}"/>')
                out.append(f'<path d="M{g1(self.F(uu - 0.9, 4.2, wv)[0])} {g1(self.F(uu - 0.9, 4.2, wv)[1])}Q{g1(self.F(uu, 3.6, wv)[0])} {g1(self.F(uu, 3.6, wv)[1])} {g1(self.F(uu + 0.9, 4.2, wv)[0])} {g1(self.F(uu + 0.9, 4.2, wv)[1])}" fill="none" stroke="{C("iron")}" stroke-width="{f(max(0.6, 0.08 * k))}"/>')
            self.add("".join(out))
        fog = self.fogZ(self.Zu(u0, -11.5))
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        A = P2([self.F(u0 - 1, 4.3, -8.0), self.F(u1 + 1, 4.3, -8.0), self.F(u1 + 1, 5.3, -11.5), self.F(u0 - 1, 5.3, -11.5)])
        B = P2([self.F(u0 - 1, 5.3, -11.5), self.F(u1 + 1, 5.3, -11.5), self.F(u1 + 1, 4.3, -15.0), self.F(u0 - 1, 4.3, -15.0)])
        self.add(f'<path d="{B}" fill="{C("canopy", -2)}"/><path d="{A}" fill="{C("canopy_hi")}"/>')
        o = self.F(u0, 4.3, -8.0)
        self.add(f'<path d="{A}" fill="{self._pat_pts("sheet", o, self.F(u0 + 1, 4.3, -8.0), self.F(u0, 4.45, -8.5))}" opacity="0.7"/>')

    # ================================================================ in front: the street and the square
    def street(self):
        """Sidewalk slabs along the facade, the street in granite setts, the square in pedra
        portuguesa waves, kerbs; the station's cast shadow lies on the sidewalk."""
        d = self.doc
        U0, U1 = -120.0, 70.0
        def band(w0, w1, kind, um=0.0):
            q = P2([self.F(U0, 0, w0), self.F(U1, 0, w0), self.F(U1, 0, w1), self.F(U0, 0, w1)])
            self.add(f'<path d="{q}" fill="{self.C(dict(paving="plat", cobble="ballast", wave="plat")[kind])}"/>')
            for a, b in ((-120, -60), (-60, -20), (-20, 10), (10, 40), (40, 70)):
                q2 = P2([self.F(a, 0, w0), self.F(b, 0, w0), self.F(b, 0, w1), self.F(a, 0, w1)])
                m = (a + b) / 2
                self.add(f'<path d="{q2}" fill="{self._pat_pts(kind, self.F(m, 0, w0), self.F(m + 1, 0, w0), self.F(m, 0, w0 + 1))}" opacity="0.9"/>')
            return q
        band(0.0, 3.2, "paving")
        band(3.2, 11.0, "cobble")
        band(11.0, 27.0, "wave")
        # beyond the square, toward us: the town's street and yards
        q = P2([self.F(-140, 0, 27.0), self.F(70, 0, 27.0), self.F(70, 0, 80.0), self.F(-140, 0, 80.0)])
        self.add(f'<path d="{q}" fill="{self.C("grass_d")}"/>')
        self.add(f'<path d="{PL([self.F(-140, 0.15, 27.0), self.F(70, 0.15, 27.0)])}" stroke="{self.C("plat", 3)}" stroke-width="{f(max(1, 0.0016 * self.H))}"/>')
        for w_ in (3.2, 11.0):
            self.add(f'<path d="{PL([self.F(U0, 0.15, w_), self.F(U1, 0.15, w_)])}" stroke="{self.C("plat", 3)}" stroke-width="{f(max(1, 0.0016 * self.H))}"/>')
        # cast shadow of the wing and the block on the sidewalk (light from the upper left)
        sh = P2([self.F(-78, 0, 0), self.F(23.5, 0, 0), self.F(30, 0, 2.6), self.F(-70, 0, 2.6)])
        self.add(f'<path d="{sh}" fill="{self.C("shadow")}" opacity="0.35"/>')
        # the haze of the valley seen past the square's far side
        self.add(f'<rect width="{self.W}" height="{self.H}" fill="{lin(d, [(0, self.C("fog"), 0), (1, self.C("fog"), 0)], (0, 0), (0, 1))}"/>')

    def lamp_post(self, u, w, h=4.6):
        """A cast-iron street lamp: plinth, fluted shaft, collar, scroll arm, lantern with a roof;
        at night its glow and the pool of light on the paving with the post's coloured shadow."""
        k = self.k(u, w)
        fog = self.fogZ(self.Zu(u, w))
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        b = self.F(u, 0, w)
        t = self.F(u, h, w)
        sw = max(1.2, 0.16 * k)
        out = []
        if self.night:
            pool = [self.F(u + 2.6 * math.cos(a), 0, w + 2.6 * math.sin(a)) for a in (2 * math.pi * i / 16 for i in range(16))]
            cx, cy = b
            r = max(math.dist(b, p) for p in pool)
            out.append(f'<path d="{P2(pool)}" fill="{rad(self.doc, [(0, self.C("lamp"), 0.45), (1, self.C("lamp"), 0)], (cx, cy), r)}"/>')
            out.append(f'<path d="{PL([b, self.F(u + 2.2, 0, w + 1.2)])}" stroke="{self.C("shadow")}" stroke-width="{f(sw * 1.5)}" opacity="0.5" stroke-linecap="round"/>')
        out.append(f'<path d="{self.quad(u - 0.25, u + 0.25, 0, 0.6, w)}" fill="{C("iron")}"/>')
        out.append(f'<path d="{PL([b, t])}" stroke="{C("iron")}" stroke-width="{f(sw)}"/>'
                   f'<path d="{PL([self.F(u - 0.04, 0.6, w), self.F(u - 0.04, h, w)])}" stroke="{C("canopy_hi")}" stroke-width="{f(sw * 0.3)}" opacity="0.6"/>')
        c1 = self.F(u, h - 0.5, w)
        out.append(f'<path d="M{g1(c1[0])} {g1(c1[1])}q{g1(0.5 * k)} {g1(-0.5 * k)} {g1(0.2 * k)} {g1(-0.8 * k)}" fill="none" stroke="{C("iron")}" stroke-width="{f(sw * 0.5)}"/>')
        lx, ly = self.F(u, h + 0.35, w)
        lw, lh = 0.32 * k, 0.55 * k
        lantern = f'M{g1(lx - lw)} {g1(ly - lh * 0.4)}L{g1(lx + lw)} {g1(ly - lh * 0.4)}L{g1(lx + lw * 0.7)} {g1(ly + lh * 0.5)}L{g1(lx - lw * 0.7)} {g1(ly + lh * 0.5)}Z'
        out.append(f'<path d="{lantern}" fill="{self.C("lamp") if self.night else C("glass")}"/>'
                   f'<path d="M{g1(lx - lw * 1.2)} {g1(ly - lh * 0.4)}L{g1(lx)} {g1(ly - lh * 0.95)}L{g1(lx + lw * 1.2)} {g1(ly - lh * 0.4)}Z" fill="{C("iron")}"/>'
                   f'<path d="M{g1(lx)} {g1(ly - lh * 0.4)}V{g1(ly + lh * 0.5)}" stroke="{C("iron")}" stroke-width="{f(sw * 0.3)}"/>')
        if self.night:
            out.append(f'<circle cx="{g1(lx)}" cy="{g1(ly)}" r="{g1(3.0 * k)}" fill="{rad(self.doc, [(0, self.C("lamp"), 0.5), (0.25, self.C("lamp"), 0.18), (1, self.C("lamp"), 0)], (lx, ly), 3.0 * k)}"/>')
        return "".join(out)

    def square_items(self):
        """Trees, lamps and benches on the square, sorted far to near."""
        rnd = random.Random(71)
        items = []
        for u in (-62, -44, -26, -8, 10, 28):
            items.append((self.Zu(u, 3.0), "lamp", u, 2.6))
        for u, w in ((-74, 18), (-52, 22), (-34, 16), (-12, 23), (30, 20), (-92, 24)):
            items.append((self.Zu(u, w), "tree", u, w))
        for u in (-44, -22, 0, 18):
            items.append((self.Zu(u, 13.0), "lamp", u, 13.0))
        out = []
        for Z, kind, u, w in sorted(items, key=lambda t: -t[0]):
            if kind == "lamp":
                out.append(self.lamp_post(u, w))
            else:
                k = self.k(u, w)
                X, Zw = self.world(u, w)
                fog = self.fogZ(Zw)
                x, y = self.F(u, 0, w)
                yt = self.F(u, 5.0, w)[1]
                # coloured shadow of the crown on the stone, toward the lower right
                sx, sy = self.F(u + 3.0, 0, w + 2.0)
                out.append(f'<ellipse cx="{g1(sx)}" cy="{g1(sy)}" rx="{g1(3.6 * k)}" ry="{g1(1.2 * k)}" fill="{self.C("shadow")}" opacity="0.35"/>')
                out.append(self.trunk(x, y, yt, max(1, 0.25 * k), fog))
                out.append(f'<g filter="{self.leaf_filter(1.0)}">{self.crown(x, yt - 1.2 * k, 3.6 * k, int(u * 7 + w), fog)}</g>')
        self.add("".join(out))

    def town_front(self):
        """The town under the mirante, closest to us: blocks of houses with tile roofs, in rows along
        the streets (parallel to the station), back yards with a tree here and there."""
        rnd = random.Random(19)
        items = []
        for row, w in enumerate((21.0, 30.0, 39.0, 48.0)):
            u = -150 + rnd.uniform(0, 6)
            while u < 40:
                wd = rnd.uniform(7, 11)
                Z = self.Zu(u + wd / 2, w)
                x = self.F(u, 0, w)[0]
                if Z > 34 and -400 < x < self.W + 200:
                    items.append((Z, "h", u, w, wd))
                if rnd.random() < 0.25:
                    items.append((self.Zu(u + wd + 1.5, w + 6), "t", u + wd + 1.5, w + 6, 0))
                u += wd + rnd.uniform(0.3, 2.5)
        out = []
        for Z, kind, u, w, wd in sorted(items, key=lambda t: -t[0]):
            if kind == "h":
                out.append(self.house(u, w + 7.0, 0.0, wd, rnd.uniform(7, 9), rnd.uniform(3.4, 4.8), rnd.randrange(999)))
            else:
                k = self.k(u, w)
                x, y = self.F(u, 0, w)
                yt = self.F(u, 4.5, w)[1]
                out.append(self.trunk(x, y, yt, max(1, 0.25 * k), 0.0) + self.crown(x, yt - k, 3.2 * k, int(u * 3 + w), 0.0))
        self.add("".join(out))

    # ================================================================ composition
    def back(self):
        self.grove_uw(-260, -100, -120, -40, 30, 41, (8, 14))
        self.back_line()
        self.grove_uw(-80, 40, -70, -30, 22, 42, (9, 15))
        self.end_pavilion(-78.0, -70.0)
        self.wing(-70.0, 0.0)
        self.block()
        self.wing(23.5, 33.0, right=True)

    def paint(self):
        steps = [self.sky, self.ridges, self.valley, self.river, self.back, self.street, self.square_items, self.town_front]
        for st in steps:
            st()
        lx, ly = self.light
        self.add(f'<rect width="{self.W}" height="{self.H}" fill="{rad(self.doc, [(0, self.C("glow"), 0.18), (0.4, self.C("glow"), 0.05), (1, self.C("glow"), 0)], (lx, ly), 0.9 * self.W)}"/>')


def form_cachoeira(doc, fr, P):
    Painter(doc, fr, P["_name"]).paint()
