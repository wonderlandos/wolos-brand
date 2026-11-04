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

import calculus as K
from geom import f, smooth
from walls_lib import lin, rad, blurf

EL = {"base", "earth", "fire", "wood", "water"}

# role: (k on the value ruler, chroma in 21sts of the base, element of the hue)
DAY = dict(
    sky_top=(9, 7, "water"), sky_mid=(14, 5, "base"), sky_hor=(18, 4, "earth"), glow=(20, 6, "earth"), sun=(20, 9, "earth"),
    cloud_lit=(19, 3, "earth"), cloud=(16, 3, "base"), cloud_shd=(12, 5, "base"), fog=(17, 3, "earth"),
    r0=(15, 4, "base"), r1=(13, 5, "water"), r2=(11, 5, "base"), r3=(8, 6, "water"), rlit=(17, 5, "earth"),
    valley=(11, 5, "wood"), valley2=(8, 6, "wood"), field=(13, 5, "earth"), roofdot=(9, 8, "fire"), walldot=(17, 3, "earth"),
    river=(16, 4, "water"), river_d=(11, 5, "water"), ripple=(19, 2, "base"),
    tree_lit=(9, 6, "wood"), tree=(3, 6, "wood"), tree_shd=(-3, 5, "water"), tree_dk=(-8, 4, "base"),
    pl_lit=(18, 6, "earth"), pl=(14, 6, "earth"), pl_shd=(6, 5, "base"), pl_dk=(1, 5, "base"),
    trim=(17, 4, "earth"), brick=(6, 9, "fire"), brick_lit=(11, 9, "fire"),
    hole=(-7, 4, "base"), glass=(-4, 4, "base"), glass_hi=(6, 4, "water"), frame=(9, 3, "earth"),
    canopy=(6, 4, "base"), canopy_hi=(12, 4, "base"), iron=(-9, 4, "base"),
    plat=(14, 3, "base"), plat_edge=(9, 3, "base"), shadow=(5, 5, "base"),
    ballast=(9, 3, "base"), ballast_d=(4, 3, "base"), sleeper=(0, 4, "fire"), rail=(-6, 3, "base"), rail_hi=(19, 4, "earth"),
    grass=(9, 7, "wood"), grass_d=(4, 7, "wood"),
    tile=(5, 10, "fire"), tile_lit=(10, 10, "fire"), tile_shd=(-1, 8, "fire"), hw=(16, 4, "earth"), hw_shd=(8, 4, "base"),
    gold=(14, 15, "earth"), lamp=(14, 15, "earth"), star=(20, 2, "base"))
NIGHT = dict(
    sky_top=(-18, 7, "base"), sky_mid=(-15, 6, "base"), sky_hor=(-10, 6, "water"), glow=(-5, 5, "water"), sun=(19, 3, "water"),
    cloud_lit=(-6, 4, "base"), cloud=(-11, 4, "base"), cloud_shd=(-14, 4, "base"), fog=(-11, 4, "base"),
    r0=(-11, 5, "base"), r1=(-12, 5, "water"), r2=(-14, 5, "base"), r3=(-15, 5, "water"), rlit=(-8, 5, "water"),
    valley=(-15, 5, "wood"), valley2=(-16, 5, "wood"), field=(-13, 4, "base"), roofdot=(10, 13, "earth"), walldot=(-11, 3, "base"),
    river=(-9, 5, "water"), river_d=(-14, 5, "water"), ripple=(-3, 4, "water"),
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
        self.cy = (0.60 if W / H > 1.7 else 0.62) * H    # the horizon
        self.hc = 5.0                            # eye 5 m up, on the far bank of the Paraiba
        self.hw = -1.6                           # the river's level under the yard
        self.mirror = False
        vx = 0.115                               # the wing's vanishing point, under the light
        rx = (vx - 0.5) * W / self.fl
        n = math.hypot(rx, 1)
        self.dR = (-rx / n, -1 / n)              # along the facade, to the right (toward us)
        zb = 74.0 if W / H > 1.7 else 70.0
        self.O = ((0.585 - 0.5) * W / self.fl * zb, zb)  # the block's left corner
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
        g = d.id("mw")
        d.defs.append(f'<filter id="{g}" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="{f(0.03 * H)}"/></filter>')
        band = P2([(0.98 * W, -0.02 * H), (1.05 * W, 0.10 * H), (0.62 * W, 0.42 * H), (0.30 * W, 0.50 * H), (0.26 * W, 0.40 * H), (0.58 * W, 0.26 * H)])
        self.add(f'<path d="{band}" fill="{self.C("cloud_lit")}" opacity="0.32" filter="url(#{g})"/>')
        lane = PL([(1.0 * W, 0.04 * H), (0.80 * W, 0.20 * H), (0.58 * W, 0.33 * H), (0.40 * W, 0.42 * H)])
        g2 = d.id("mw")
        d.defs.append(f'<filter id="{g2}" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="{f(0.008 * H)}"/></filter>')
        self.add(f'<path d="{lane}" fill="none" stroke="{self.C("sky_top")}" stroke-width="{f(0.018 * H)}" opacity="0.5" filter="url(#{g2})"/>')
        rnd = random.Random(21)
        st = []
        for i in range(900):
            if i < 520:   # in the band
                t = rnd.random()
                cx, cy = 1.0 * W + (0.30 * W - 1.0 * W) * t, 0.0 * H + 0.46 * H * t ** 0.9
                cx += rnd.gauss(0, 0.05 * W)
                cy += rnd.gauss(0, 0.05 * H)
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
                      f'<feTurbulence type="fractalNoise" baseFrequency="{f(0.02 * 2160 / H)}" numOctaves="3" seed="7" result="n"/>'
                      f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{f(0.010 * H)}" xChannelSelector="R" yChannelSelector="G"/></filter>')
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
            for j, (fq, a) in enumerate(((1.3, 1.0), (3.1, 0.5), (7.3, 0.22), (15.0, 0.1), (31, 0.05), (63, 0.025))):
                y += a * math.sin(fq * t * 6.28 + ph[j]) * (rough if j > 2 else 1)
            env = 1.0 if peaks is None else peaks(t)
            pts.append((x, base - amp * env * (0.55 + 0.45 * y)))
        return pts

    def ridges(self):
        W, H, d, cy = self.W, self.H, self.doc, self.cy
        # (role, seed, base y over the horizon, amplitude, fog) far to near; higher on the right (anchor)
        layers = [("r0", 3, 0.000, 0.30, 0.50), ("r1", 8, 0.004, 0.23, 0.36), ("r2", 15, 0.008, 0.16, 0.22), ("r3", 23, 0.012, 0.09, 0.10)]
        for li, (role, seed, b, amp, fg) in enumerate(layers):
            env = (lambda t, li=li: (0.35 + 0.65 * min(1, max(0, (t - 0.08) / 0.8)) ** 1.3) * (1 - 0.25 * math.exp(-((t - 0.25) / 0.12) ** 2)))
            pts = self.profile(seed, -0.02 * W, 1.02 * W, cy - b * H, amp * H, 0.8 + 0.2 * li, peaks=env)
            area = PL(pts) + f" L{f(1.02 * W)} {f(cy + 0.02 * H)} L{f(-0.02 * W)} {f(cy + 0.02 * H)}Z"
            cid = d.id("rc")
            d.defs.append(f'<clipPath id="{cid}"><path d="{area}"/></clipPath>')
            top = min(y for _, y in pts)
            lit = self.C("rlit", fg)
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
            self.add(f'<path d="{"".join(st)}" fill="none" stroke="{self.C(role, max(0, fg - 0.15), -1.5)}" stroke-width="{f(0.0011 * H)}" opacity="0.45"/>')
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
        u, w = 46.0, 12.6
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
                      f'<feTurbulence type="turbulence" baseFrequency="{f(0.09 * 2160 / self.H / scale)}" numOctaves="2" seed="11" result="n"/>'
                      f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{f(0.005 * self.H * scale)}" xChannelSelector="R" yChannelSelector="G"/></filter>')
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
        self.add(f'<path d="{self.ground_strip(near, 6.0, 19.4)}" fill="{lin(d, [(0, self.C("grass_d"), 1), (1, self.C("grass", 0.4), 1)], (0, self.H), (0, self.cy))}"/>')

    def wing(self, u0, u1, right=False):
        d = self.doc
        WALL, CORN, PAR, PIN = 6.2, 6.8, 7.6, 8.9
        Zm = self.Zu((u0 + u1) / 2)
        fog = self.fogZ(Zm)
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        # the end wall facing the light (left end), then the long wall
        if not right:
            pass
        wall = self.quad(u0, u1, 0.0, PAR)
        self.add(f'<path d="{wall}" fill="{lin(d, [(0, C("pl_lit"), 1), (0.5, C("pl"), 1), (1, C("pl", -1.5), 1)], self.F(u0, 4), self.F(u1, 4))}"/>')
        cid, fid = self.wall_grain(wall, Zm)
        self.add(f'<g clip-path="url(#{cid})"><rect x="0" y="0" width="{self.W}" height="{self.H}" fill="{C("pl_shd")}" opacity="0.16" filter="url(#{fid})"/></g>')
        self.add(f'<path d="{self.quad(u0, u1, 0.0, 0.8)}" fill="{C("pl_shd")}" opacity="0.55"/>')
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
        if not right:
            self.canopy(u0 + 0.3, u1 - 0.3, fog)

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
        self.add(f'<path d="{fas}" fill="{C("canopy", -2)}"/><path d="{"".join(sc)}" fill="{C("canopy", -4)}"/>'
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
        end = P2([self.F(u0, 0, 0.0), self.F(u0, 0, -9.0), self.F(u0, H1, -9.0), self.F(u0, H1, 0.0)])
        self.add(f'<path d="{end}" fill="{C("pl_lit", 1)}"/>')
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
        """A round-arched window: reveal (lit jamb, shaded jamb), glass with sky reflection, a
        mullion and transom, the fanlight with radial glazing bars, archivolt and keystone."""
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        k = self.k(uc, w)
        out = []
        outer = self.arch_pts(uc, half + 0.22, h0, hs, w)
        out.append(f'<path d="{P2(outer)}" fill="{C("trim")}"/>')
        rev = self.arch_pts(uc, half, h0, hs, w)
        out.append(f'<path d="{P2(rev)}" fill="{C("pl_shd")}"/>')
        glass = self.arch_pts(uc + 0.12, half - 0.12, h0 + 0.05, hs, w - 0.3)
        if lit:
            out.append(f'<path d="{P2(glass)}" fill="{self.C("lamp")}" opacity="0.9"/>')
        else:
            gx0, gy0 = self.F(uc, hs + half, w)
            gx1, gy1 = self.F(uc, h0, w)
            out.append(f'<path d="{P2(glass)}" fill="{lin(self.doc, [(0, C("glass_hi"), 1), (0.45, C("glass"), 1), (1, C("hole"), 1)], (gx0, gy0), (gx1, gy1))}"/>')
        bars = [PL([self.F(uc + 0.06, h0, w - 0.3), self.F(uc + 0.06, hs, w - 0.3)]),
                PL([self.F(uc - half + 0.12, hs, w - 0.3), self.F(uc + half, hs, w - 0.3)]),
                PL([self.F(uc - half + 0.12, (h0 + hs) / 2, w - 0.3), self.F(uc + half, (h0 + hs) / 2, w - 0.3)])]
        for j in (1, 2, 3):
            a = math.pi * j / 4
            bars.append(PL([self.F(uc + 0.06, hs, w - 0.3), self.F(uc + 0.06 - (half - 0.12) * math.cos(a), hs + (half - 0.12) * math.sin(a), w - 0.3)]))
        out.append(f'<path d="{"".join(bars)}" fill="none" stroke="{C("frame") if not lit else self.C("pl_shd", 0.0)}" stroke-width="{f(max(0.6, 0.06 * k))}"/>')
        out.append(f'<path d="{PL([self.F(uc + half, h0, w), self.F(uc + half, hs, w)])}" stroke="{C("pl_lit", 3)}" stroke-width="{f(max(0.7, 0.1 * k))}"/>')
        # sill and keystone
        out.append(f'<path d="{self.quad(uc - half - 0.3, uc + half + 0.3, h0 - 0.18, h0, w + 0.12)}{self.quad(uc - 0.14, uc + 0.14, hs + half + 0.05, hs + half + 0.4, w + 0.05)}" fill="{C("pl_lit")}"/>')
        return "".join(out)

    def block(self):
        d = self.doc
        Zm = self.Zu(12.0)
        fog = self.fogZ(Zm)
        C = lambda r, dk=0.0: self.C(r, fog, dk)
        k = self.k(12.0)
        sections = [(0.0, 10.5, 14.4, 0.0, [1.9, 5.25, 8.6], 0.62), (10.5, 19.5, 15.0, 0.6, [12.0, 14.0, 16.0, 18.0], 0.5), (19.5, 23.5, 14.2, 0.0, [21.5], 0.62)]
        DEPTH = 13.0
        # left return wall of the block, above the wing, facing the light
        side = P2([self.F(0.0, 7.6, 0.0), self.F(0.0, 7.6, -DEPTH), self.F(0.0, 14.4, -DEPTH), self.F(0.0, 14.4, 0.0)])
        self.add(f'<path d="{side}" fill="{C("pl_lit", 1.5)}"/>')
        sidewin = []
        for wv in (-3.0, -7.0, -11.0):
            for h0, hs in ((9.9, 12.3),):
                pts = [(0.0, h0, wv - 0.55), (0.0, hs, wv - 0.55)] + [(0.0, hs + 0.55 * math.sin(math.pi * j / 10), wv - 0.55 * math.cos(math.pi * j / 10)) for j in range(1, 10)] + [(0.0, hs, wv + 0.55), (0.0, h0, wv + 0.55)]
                sidewin.append(P2([self.F(a, b, c) for a, b, c in pts]))
        self.add(f'<path d="{"".join(sidewin)}" fill="{C("hole")}" opacity="0.85"/>')
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
                shd = P2([self.F(u1, 0, 0.0), self.F(u1 + 1.1, 0, 0.0), self.F(u1 + 1.1, hc - 0.6, 0.0), self.F(u1, hc, 0.0)])
                self.add(f'<path d="{shd}" fill="{C("shadow")}" opacity="0.5"/>')
            cid, fid = self.wall_grain(wall, Zm)
            self.add(f'<g clip-path="url(#{cid})"><rect width="{self.W}" height="{self.H}" fill="{C("pl_shd")}" opacity="0.18" filter="url(#{fid})"/></g>')
            # rusticated plinth, string courses
            self.add(f'<path d="{self.quad(u0, u1, 0.0, 1.0, fw + 0.06)}" fill="{C("pl_shd")}" opacity="0.6"/>')
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
        # the canopy's shadow on the platform
        sh = P2([self.F(-70, PH, 0.0), self.F(0.0, PH, 0.0), self.F(0.0, PH, 2.6), self.F(-70, PH, 2.6)])
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
        self.add(f'<path d="{"".join(gl)}" fill="none" stroke="{self.C("glow")}" stroke-width="{f(0.004 * H)}" opacity="0.5" filter="{blurf(d, 0.002 * H)}"/>')

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
        return 21.0 + 0.010 * max(0.0, u - 2.0) ** 2

    def river_front(self):
        d, W, H = self.doc, self.W, self.H
        us = [-900 + i * 6.0 for i in range(150)] + [-6 + i * 0.5 for i in range(140)]
        pts = []
        for u in us:
            w = self.bank_w(u)
            if w > self.wc - 3.0:
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
        fid = d.id("rf")
        d.defs.append(f'<filter id="{fid}" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
                      f'<feTurbulence type="fractalNoise" baseFrequency="{f(0.0009 * 2160 / self.H)} {f(0.03 * 2160 / self.H)}" numOctaves="2" seed="5" result="n"/>'
                      f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{f(0.012 * self.H)}" xChannelSelector="R" yChannelSelector="G"/></filter>')
        mid = d.id("rm")
        d.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{self.W}" height="{self.H}"><rect width="{self.W}" height="{self.H}" fill="{lin(d, [(0, "#FFFFFF", 0.0), (0.04, "#FFFFFF", 0.78), (0.6, "#FFFFFF", 0.5), (1, "#FFFFFF", 0.2)], (0, self.cy), (0, self.H))}"/></mask>')
        self.add(f'<g clip-path="url(#{self.water_clip})"><g mask="url(#{mid})"><g filter="url(#{fid})">{inner}</g></g></g>')

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
            if w > self.wc - 3.0:
                break
            top.append(self.F(u, 0.0, w))
            bot.append(self.F(u, self.hw, w))
        if self.mirror:
            pass
        face = P2(top + bot[::-1])
        self.add(f'<path d="{face}" fill="{lin(d, [(0, self.C("plat_edge", 0.6), 1), (1, self.C("pl_dk"), 1)], (0, self.cy), (0, self.H))}"/>')
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
            if w > self.wc - 3.0:
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
        self.add(f'<g filter="{self.leaf_filter(1.0)}">{"".join(out)}</g>')

    # ================================================================ composition
    def back(self):
        """Everything behind the yard that the river mirrors: trees behind the station, the station."""
        self.grove_uw(-170, -80, -40, 10, 40, 41, (10, 18))
        self.grove_uw(-80, 30, -60, -16, 46, 42, (12, 20))
        self.wing(-70.0, 0.0)
        self.end_pavilion(-78.0, -70.0)
        self.block()
        self.wing(23.5, 36.5, right=True)

    def paint(self):
        import os
        prof = os.environ.get("CACH_PROF")
        steps = [self.sky, self.ridges, self.valley, self.back, self.river_front, lambda: self.reflect(self.back), self.water_surface,
                 self.embankment, self.ground_front, self.yard, self.platform, self.tracks, self.poles, self.bamboo, self.reeds]
        if prof:
            for st in steps:
                n0 = sum(len(b) for b in self.doc.body) + sum(len(b) for b in self.doc.defs)
                st()
                n1 = sum(len(b) for b in self.doc.body) + sum(len(b) for b in self.doc.defs)
                print(getattr(st, "__name__", "reflect"), n1 - n0)
            return
        self.sky()
        self.ridges()
        self.valley()
        self.back()
        self.river_front()
        self.reflect(self.back)
        self.water_surface()
        self.embankment()
        self.ground_front()
        self.yard()
        self.platform()
        self.tracks()
        self.poles()
        self.bamboo()
        self.reeds()
        lx, ly = self.light
        self.add(f'<rect width="{self.W}" height="{self.H}" fill="{rad(self.doc, [(0, self.C("glow"), 0.28), (0.4, self.C("glow"), 0.08), (1, self.C("glow"), 0)], (lx, ly), 0.9 * self.W)}"/>')


def form_cachoeira(doc, fr, P):
    Painter(doc, fr, P["_name"]).paint()
