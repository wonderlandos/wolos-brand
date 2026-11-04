# SPDX-License-Identifier: GPL-2.0-or-later
"""Shared kit for the east wallpapers (walls.py): palettes, frame, gradients, detail drawing
(roofs, halls, trees, ridges, mist). Forms live in walls_<form>.py."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calculus as K  # noqa: E402
from geom import Doc, f, smooth, juzhe, circle, rrect  # noqa: E402
from colour import oklch  # noqa: E402

SIZES = {"4k": (3840, 2160), "16x10": (2560, 1600)}

# ---------------------------------------------------------------- palettes
# role: (k on the value ruler, chroma in 21sts of the base, element of the hue)
PALETTES = {
    "day": dict(
        cloud=(20, 2, "base"), cloud2=(15, 6, "base"), cloudline=(10, 9, "base"), hill=(8, 8, "base"), hill2=(2, 9, "water"),
        sky0=(20, 1, "earth"), sky1=(17, 4, "base"), sky2=(14, 5, "water"), glow=(20, 3, "earth"), lightc=(18, 9, "earth"),
        far=(13, 7, "base"), far2=(10, 7, "water"), mid=(8, 10, "base"), mid2=(4, 11, "base"),
        near=(1, 15, "base"), near2=(-3, 17, "base"), ground=(3, 9, "base"), ground2=(-3, 12, "water"),
        water=(13, 5, "water"), water2=(8, 7, "water"), shade=(6, 8, "base"), line=(18, 3, "base"), line2=(-6, 8, "base"),
        mistc=(20, 2, "base"), bark=(-12, 6, "base"), needle=(-4, 10, "base"), needle2=(-10, 9, "base"), needlelit=(8, 10, "wood"),
        leaf=(4, 10, "wood"), leaf2=(-3, 11, "wood"), leaflit=(13, 8, "wood"), ripple=(19, 2, "base"),
        joint=(-5, 9, "water"), jointlit=(12, 6, "base"), block=(-6, 12, "base"), block2=(-2, 14, "base"), blocklit=(10, 10, "base"),
        column=(0, 15, "fire"), latback=(17, 11, "earth"), latbar=(-8, 10, "base"),
        gold=(13, 15, "earth"), cinnabar=(2, 15, "fire"), jade=(10, 9, "wood")),
    "night": dict(
        cloud=(1, 5, "base"), cloud2=(-3, 5, "base"), cloudline=(6, 5, "base"), hill=(-12, 8, "base"), hill2=(-15, 7, "base"),
        sky0=(-10, 5, "base"), sky1=(-11, 5, "base"), sky2=(-12, 5, "base"), glow=(-9, 5, "base"), lightc=(20, 1, "earth"),
        far=(-10, 7, "base"), far2=(-12, 7, "water"), mid=(-12, 9, "base"), mid2=(-14, 9, "base"),
        near=(-13, 11, "base"), near2=(-16, 9, "base"), ground=(-16, 8, "water"), ground2=(-18, 6, "base"),
        water=(-11, 6, "water"), water2=(-15, 7, "water"), shade=(-17, 6, "base"), line=(-3, 8, "base"), line2=(-1, 6, "base"),
        mistc=(-3, 4, "base"), bark=(-17, 4, "base"), needle=(-14, 7, "base"), needle2=(-17, 5, "base"), needlelit=(-6, 8, "wood"),
        leaf=(-12, 8, "wood"), leaf2=(-15, 6, "wood"), leaflit=(-6, 8, "wood"), ripple=(6, 4, "base"),
        joint=(-18, 5, "base"), jointlit=(-9, 6, "base"), block=(-15, 8, "base"), block2=(-13, 9, "base"), blocklit=(-7, 8, "base"),
        column=(-8, 12, "fire"), latback=(12, 14, "earth"), latbar=(-16, 6, "base"),
        gold=(12, 14, "earth"), cinnabar=(0, 14, "fire"), jade=(-6, 9, "wood")),
    "dusk": dict(
        cloud=(14, 5, "earth"), cloud2=(6, 8, "base"), cloudline=(-2, 10, "base"), hill=(-1, 11, "base"), hill2=(-6, 11, "base"),
        sky0=(15, 2, "earth"), sky1=(6, 8, "base"), sky2=(-2, 11, "base"), glow=(14, 6, "earth"), lightc=(20, 2, "earth"),
        far=(4, 9, "base"), far2=(1, 10, "water"), mid=(-3, 13, "base"), mid2=(-6, 13, "base"),
        near=(-8, 15, "base"), near2=(-11, 13, "base"), ground=(-11, 12, "water"), ground2=(-15, 10, "base"),
        water=(4, 6, "water"), water2=(-2, 8, "water"), shade=(-10, 10, "base"), line=(10, 6, "base"), line2=(-12, 8, "base"),
        mistc=(12, 5, "base"), bark=(-16, 6, "base"), needle=(-10, 11, "base"), needle2=(-14, 9, "base"), needlelit=(0, 10, "wood"),
        leaf=(-6, 10, "wood"), leaf2=(-11, 9, "wood"), leaflit=(2, 9, "wood"), ripple=(14, 4, "base"),
        joint=(-15, 8, "base"), jointlit=(-4, 8, "base"), block=(-12, 11, "base"), block2=(-9, 12, "base"), blocklit=(-2, 10, "base"),
        column=(-4, 15, "fire"), latback=(15, 14, "earth"), latbar=(-14, 9, "base"),
        gold=(14, 16, "earth"), cinnabar=(2, 16, "fire"), jade=(2, 10, "wood")),
    "jade": dict(
        cloud=(20, 2, "water"), cloud2=(15, 5, "water"), cloudline=(8, 8, "water"), hill=(9, 7, "wood"), hill2=(5, 8, "water"),
        sky0=(19, 2, "earth"), sky1=(15, 5, "water"), sky2=(11, 6, "water"), glow=(20, 3, "earth"), lightc=(18, 9, "earth"),
        far=(11, 6, "wood"), far2=(8, 7, "wood"), mid=(5, 9, "wood"), mid2=(1, 10, "wood"),
        near=(-2, 12, "wood"), near2=(-6, 12, "wood"), ground=(-4, 10, "water"), ground2=(-9, 11, "water"),
        water=(8, 9, "water"), water2=(2, 12, "water"), shade=(2, 8, "wood"), line=(17, 4, "water"), line2=(-8, 8, "water"),
        mistc=(19, 3, "water"), bark=(-13, 6, "water"), needle=(-5, 11, "wood"), needle2=(-11, 9, "wood"), needlelit=(8, 12, "wood"),
        leaf=(2, 11, "wood"), leaf2=(-5, 11, "wood"), leaflit=(12, 9, "wood"), ripple=(18, 3, "water"),
        joint=(-12, 8, "water"), jointlit=(4, 6, "water"), block=(-8, 11, "water"), block2=(-4, 12, "water"), blocklit=(8, 9, "water"),
        column=(0, 15, "fire"), latback=(17, 11, "earth"), latbar=(-10, 9, "water"),
        gold=(13, 15, "earth"), cinnabar=(2, 15, "fire"), jade=(-1, 21, "base")),
}


# Roles added for the mature register (muted planes, fog, glass, ridge layers): name -> spec per palette
EXTRA = {
    "day": dict(fog=(18, 2, "base"), ridge1=(12, 4, "water"), ridge2=(9, 5, "base"), ridge3=(6, 6, "water"), ridge4=(3, 7, "base"),
                glass=(-9, 5, "base"), pane=(4, 6, "earth"), rail=(2, 4, "base"), roofa=(-1, 7, "base"), roofb=(-7, 8, "base"),
                roofc=(-12, 8, "base"), lit=(8, 5, "base"), wall=(-8, 6, "base"), plaster=(12, 3, "base"), plaster2=(8, 4, "base"), moon=(20, 2, "earth"), blossom=(12, 7, "fire")),
    "night": dict(fog=(-12, 4, "base"), ridge1=(-11, 5, "base"), ridge2=(-12, 5, "water"), ridge3=(-14, 6, "base"), ridge4=(-15, 6, "water"),
                  glass=(-18, 4, "base"), pane=(8, 12, "earth"), rail=(-11, 4, "base"), roofa=(-12, 7, "base"), roofb=(-16, 7, "base"),
                  roofc=(-19, 6, "base"), lit=(-4, 5, "base"), wall=(-16, 5, "base"), plaster=(-11, 4, "base"), plaster2=(-15, 4, "base"), moon=(18, 3, "water"), blossom=(15, 5, "fire")),
    "dusk": dict(fog=(10, 5, "earth"), ridge1=(6, 6, "base"), ridge2=(2, 8, "base"), ridge3=(-2, 9, "base"), ridge4=(-6, 10, "base"),
                 glass=(-14, 6, "base"), pane=(6, 11, "earth"), rail=(-4, 6, "base"), roofa=(-8, 9, "base"), roofb=(-13, 9, "base"),
                 roofc=(-17, 8, "base"), lit=(5, 6, "earth"), wall=(-12, 7, "base"), plaster=(3, 5, "earth"), plaster2=(-2, 6, "base"), moon=(19, 4, "earth"), blossom=(19, 5, "fire")),
    "jade": dict(fog=(18, 2, "water"), ridge1=(14, 3, "water"), ridge2=(11, 4, "wood"), ridge3=(8, 5, "water"), ridge4=(5, 6, "wood"),
                 glass=(-10, 5, "water"), pane=(4, 6, "earth"), rail=(0, 4, "water"), roofa=(-2, 7, "wood"), roofb=(-9, 8, "wood"),
                 roofc=(-13, 8, "water"), lit=(8, 5, "water"), wall=(-7, 6, "water"), plaster=(12, 3, "water"), plaster2=(8, 4, "water"), moon=(20, 2, "earth"), blossom=(20, 3, "fire")),
}
MUTE = 0.6                      # chroma scale of every non-accent role (mature register)
ACCENT = {"blossom", "gold", "cinnabar", "lightc", "glow", "pane", "latback", "column", "jade", "moon", "sky0"}


def spec_of(name):
    d = dict(PALETTES[name])
    d.update(EXTRA[name])
    return d


def palette(name, fog=0.0, fog_of=None):
    """Derived colours of a palette. fog in 0..1 walks every role toward the palette's fog role along
    the value ruler and the chroma (atmospheric perspective); hue stays the role's own."""
    spec = spec_of(name)
    fk, fc, _ = spec["fog"]
    out, why = {}, {}
    for role, (k, c, el) in spec.items():
        if role not in ACCENT:
            c = c * MUTE
        if fog and role not in ("fog", "sky0", "sky1", "sky2", "glow", "lightc", "moon"):
            k, c = k + (fk - k) * fog, c + (fc * MUTE - c) * fog
        out[role] = K.derive(round(k, 2), round(c, 2), K.hue_of(el, K.BASE), K.BASE)
        why[role] = f"derive({round(k, 2)},{round(c, 2)}/21,{el})"
    return out, why


# ---------------------------------------------------------------- frame helpers
class Frame:
    """Fractions of the frame to px, snapped to the fen; s = px per 1/2160 of the height."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.s = h / 2160

    def x(self, fx):
        return round(fx * self.w / K.U) * K.U

    def y(self, fy):
        return round(fy * self.h / K.U) * K.U

    def l(self, v):                     # a length given at 2160 high, snapped
        return max(K.U, round(v * self.s / K.U) * K.U)


def lin(doc, stops, p0, p1):
    """Linear gradient in user space from p0 to p1; stops = [(offset, colour, opacity)]."""
    i = doc.id("l")
    st = "".join(f'<stop offset="{f(o)}" stop-color="{c}"' + (f' stop-opacity="{f(a)}"' if a < 1 else "") + "/>"
                 for o, c, a in stops)
    doc.defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{f(p0[0])}" y1="{f(p0[1])}" '
                    f'x2="{f(p1[0])}" y2="{f(p1[1])}">{st}</linearGradient>')
    return f"url(#{i})"


def rad(doc, stops, c, r):
    i = doc.id("r")
    st = "".join(f'<stop offset="{f(o)}" stop-color="{cc}" stop-opacity="{f(a)}"/>' for o, cc, a in stops)
    doc.defs.append(f'<radialGradient id="{i}" gradientUnits="userSpaceOnUse" cx="{f(c[0])}" cy="{f(c[1])}" '
                    f'r="{f(r)}">{st}</radialGradient>')
    return f"url(#{i})"


def along_light(fr, x0, y0, x1, y1):
    """Gradient end points across a box, along the light (dx:dy = 1:2), lit end first."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    half = (abs(x1 - x0) * 1 + abs(y1 - y0) * 2) / (2 * math.sqrt(5))
    ux, uy = 1 / math.sqrt(5), 2 / math.sqrt(5)
    return (cx - ux * half, cy - uy * half), (cx + ux * half, cy + uy * half)


def blurf(doc, std):
    i = doc.id("b")
    doc.defs.append(f'<filter id="{i}" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">'
                    f'<feGaussianBlur stdDeviation="{f(std)}"/></filter>')
    return f"url(#{i})"


def cast(doc, d, colour, fr, lift=1.0, opacity=0.4):
    """Coloured soft shadow of path d: offset (1, 2) away from the light, blurred (rule S1/S2)."""
    o = fr.l(10) * lift
    doc.add(f'<path d="{d}" transform="translate({f(o * 0.5)} {f(o)})" fill="{colour}" opacity="{f(opacity)}" '
            f'filter="{blurf(doc, fr.l(14) * lift)}"/>')


def poly(pts, close=True):
    d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts)
    return d + ("Z" if close else "")


def sky(doc, fr, P, light):
    """The ground: lit at the light, falling off along 1:2; and the light itself (the entry)."""
    W, H = fr.w, fr.h
    g = lin(doc, [(0, P["sky0"], 1), (0.55, P["sky1"], 1), (1, P["sky2"], 1)], (0, 0), (W * 0.42, H * 1.05))
    doc.add(f'<rect width="{W}" height="{H}" fill="{g}"/>')
    lx, ly, lr = light
    doc.add(f'<rect width="{W}" height="{H}" fill="{rad(doc, [(0, P["glow"], 0.85), (0.35, P["glow"], 0.3), (1, P["glow"], 0)], (lx, ly), H * 0.9)}"/>')


def disc(doc, fr, P, light, halo=True):
    lx, ly, lr = light
    if halo:
        doc.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{f(lr * 1.9)}" fill="{P["lightc"]}" opacity="0.18"/>')
        doc.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{f(lr * 1.4)}" fill="{P["lightc"]}" opacity="0.22"/>')
    doc.add(f'<circle cx="{f(lx)}" cy="{f(ly)}" r="{f(lr)}" fill="{P["lightc"]}"/>')



# ---------------------------------------------------------------- detail kit
def bez(pts, n=10):
    """Sample the Catmull-Rom curve that geom.smooth draws (same tangents), n points per segment."""
    out = [pts[0]]
    m = len(pts)
    for i in range(m - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < m else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        for k in range(1, n + 1):
            t = k / n
            a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
            out.append((a * p1[0] + b * c1[0] + c * c2[0] + d * p2[0], a * p1[1] + b * c1[1] + c * c2[1] + d * p2[1]))
    return out


def resample(line, n):
    """n points at equal arc length along a polyline."""
    acc = [0.0]
    for a, b in zip(line, line[1:]):
        acc.append(acc[-1] + math.dist(a, b))
    out, j = [], 0
    for i in range(n):
        s = acc[-1] * i / max(1, n - 1)
        while j < len(acc) - 2 and acc[j + 1] < s:
            j += 1
        t = (s - acc[j]) / max(1e-9, acc[j + 1] - acc[j])
        a, b = line[j], line[j + 1]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def pl(line):
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in line)


def pine(doc, fr, P, anchor, length, ang, seed, role="near", flip=False, pads=9):
    """A pine bough in ink: a bent limb (it turns: juzhe-like sag), needle pads lit from the upper
    left (light top, shade under), each pad a fan of needle strokes."""
    rnd = random.Random(seed)
    x, y = anchor
    L = length
    pts = [(x, y)]
    a = math.radians(ang)
    for i in range(1, 6):
        a += math.radians(rnd.uniform(-14, 18)) * (-1 if flip else 1)
        x += math.cos(a) * L / 5
        y += math.sin(a) * L / 5
        pts.append((x, y))
    limb = bez(pts, 8)
    w0 = fr.l(26)
    left, right = [], []
    for i, (px_, py_) in enumerate(limb):
        q = limb[min(i + 1, len(limb) - 1)]
        p0 = limb[max(i - 1, 0)]
        dx, dy = q[0] - p0[0], q[1] - p0[1]
        n = math.hypot(dx, dy) or 1
        w = w0 * (1 - 0.75 * i / len(limb))
        left.append((px_ - dy / n * w / 2, py_ + dx / n * w / 2))
        right.append((px_ + dy / n * w / 2, py_ - dx / n * w / 2))
    d = pl(left) + " L" + " L".join(f"{f(a_)} {f(b_)}" for a_, b_ in right[::-1]) + "Z"
    cast(doc, d, P["shade"], fr, lift=2.5, opacity=0.3)
    doc.add(f'<path d="{d}" fill="{P["bark"]}"/>')
    # twigs and pads
    out = []
    for k in range(pads):
        t = 0.2 + 0.8 * k / max(1, pads - 1)
        bx, by = limb[min(len(limb) - 1, int(t * (len(limb) - 1)))]
        side = 1 if k % 2 else -1
        tx, ty = bx + side * fr.l(rnd.uniform(40, 120)), by + fr.l(rnd.uniform(30, 110)) * (0.6 if side > 0 else -0.3)
        out.append(f'<path d="M{f(bx)} {f(by)}Q{f((bx + tx) / 2)} {f(by - fr.l(30))} {f(tx)} {f(ty)}" stroke="{P["bark"]}" stroke-width="{fr.l(9)}" fill="none" stroke-linecap="round"/>')
        r = fr.l(rnd.uniform(90, 140))
        pad = f"M{f(tx - r)} {f(ty)}C{f(tx - r)} {f(ty - r * 0.55)} {f(tx + r)} {f(ty - r * 0.55)} {f(tx + r)} {f(ty)}C{f(tx + r * 0.6)} {f(ty + r * 0.28)} {f(tx - r * 0.6)} {f(ty + r * 0.28)} {f(tx - r)} {f(ty)}Z"
        g0, g1 = along_light(fr, tx - r, ty - r * 0.5, tx + r, ty + r * 0.3)
        out.append(f'<path d="{pad}" fill="{lin(doc, [(0, P["needle"], 1), (1, P["needle2"], 1)], g0, g1)}"/>')
        strokes = []
        for j in range(26):
            u = -1 + 2 * j / 25
            sx = tx + u * r * 0.9
            sy = ty - r * 0.12 * (1 - u * u)
            ex = tx + u * r * 1.15
            ey = ty - r * (0.55 + 0.25 * (1 - abs(u))) * (1 - 0.3 * abs(u))
            strokes.append(f"M{f(sx)} {f(sy)}L{f(ex)} {f(ey)}")
        out.append(f'<path d="{"".join(strokes)}" stroke="{P["needle2"]}" stroke-width="{fr.l(5)}" stroke-linecap="round"/>')
        lit = "".join(f"M{f(tx + u * r * 0.7)} {f(ty - r * 0.3)}L{f(tx + u * r * 0.95)} {f(ty - r * 0.62)}" for u in (-0.8, -0.55, -0.3, -0.05))
        out.append(f'<path d="{lit}" stroke="{P["needlelit"]}" stroke-width="{fr.l(4)}" stroke-linecap="round" opacity="0.8"/>')
    doc.add("".join(out))


def mist(doc, fr, P, y, h, x0=-0.1, x1=1.1, opacity=0.55, seed=1, role="mistc"):
    """A stratum of mist: a long soft band with a wavy top, lighter than what it veils."""
    rnd = random.Random(seed)
    W, H = fr.w, fr.h
    pts = [(x0 * W, (y + h * 0.5) * H)]
    n = 9
    for i in range(1, n):
        pts.append(((x0 + (x1 - x0) * i / n) * W, (y + rnd.uniform(-0.3, 0.3) * h) * H))
    pts.append((x1 * W, (y + h * 0.4) * H))
    d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts) + f"L{f(x1 * W)} {f((y + h) * H)}L{f(x0 * W)} {f((y + h) * H)}Z"
    g = lin(doc, [(0, P[role], opacity), (0.6, P[role], opacity * 0.6), (1, P[role], 0)], (0, (y - h * 0.3) * H), (0, (y + h) * H))
    doc.add(f'<path d="{d}" fill="{g}" filter="{blurf(doc, fr.l(22))}"/>')


def birds(doc, fr, P, path_pts, n, seed, role="line2"):
    """A flock along a curve (the qi path made visible): small two-arc strokes, smaller far."""
    rnd = random.Random(seed)
    line = resample(bez(path_pts, 12), n)
    out = []
    for i, (x, y) in enumerate(line):
        s = fr.l(14 + 16 * i / max(1, n - 1)) * rnd.uniform(0.8, 1.2)
        x += rnd.uniform(-1, 1) * s * 2
        y += rnd.uniform(-1, 1) * s * 2
        out.append(f"M{f(x - s * 1.6)} {f(y - s * 0.2)}Q{f(x - s * 0.7)} {f(y - s * 0.9)} {f(x)} {f(y)}Q{f(x + s * 0.7)} {f(y - s * 0.9)} {f(x + s * 1.6)} {f(y - s * 0.2)}")
    doc.add(f'<path d="{"".join(out)}" fill="none" stroke="{P[role]}" stroke-width="{fr.l(5)}" stroke-linecap="round" stroke-linejoin="round"/>')


def cun(doc, fr, P, ridge_pts, depth, seed, role, n=60, opacity=0.5):
    """Texture strokes (cun) down a slope from its ridge: short curved strokes, denser near the
    ridge, lighter on the lit (left) faces."""
    rnd = random.Random(seed)
    line = bez(ridge_pts, 8)
    out = []
    for _ in range(n):
        x, y = line[rnd.randrange(len(line))]
        dy = depth * rnd.random() ** 1.6
        y2 = y + dy
        l = fr.l(rnd.uniform(40, 120))
        out.append(f"M{f(x)} {f(y2)}q{f(l * 0.3)} {f(l * 0.4)} {f(l * 0.15)} {f(l)}")
    doc.add(f'<path d="{"".join(out)}" fill="none" stroke="{P[role]}" stroke-width="{fr.l(4)}" stroke-linecap="round" opacity="{f(opacity)}"/>')


def pagoda(doc, fr, P, x, y, h, role="far2"):
    """A small far pagoda: five tiers, each roof a pair of juzhe slopes with lifted eaves."""
    out = []
    tiers = 5
    th = h / (tiers + 1.2)
    for i in range(tiers):
        w = h * (0.5 - 0.06 * i)
        yb = y - i * th
        body = f'<rect x="{f(x - w * 0.28)}" y="{f(yb - th * 0.7)}" width="{f(w * 0.56)}" height="{f(th * 0.7)}" fill="{P[role]}"/>'
        L = juzhe(x, yb - th * 1.15, x - w / 2, yb - th * 0.62, purlins=3, first=0.2)
        R = juzhe(x, yb - th * 1.15, x + w / 2, yb - th * 0.62, purlins=3, first=0.2)
        roof = pl(L[::-1] + R) + f"L{f(x + w / 2 + th * 0.12)} {f(yb - th * 0.75)}L{f(x - w / 2 - th * 0.12)} {f(yb - th * 0.75)}Z"
        out.append(body + f'<path d="{roof}" fill="{P[role]}"/>')
    out.append(f'<path d="M{f(x)} {f(y - tiers * th - th * 0.2)}V{f(y - tiers * th - th * 1.1)}" stroke="{P[role]}" stroke-width="{f(th * 0.14)}" stroke-linecap="round"/>')
    doc.add("".join(out))


def lotus(doc, fr, P, cx, cy, r, seed):
    """A lotus pad lying on the water: a flattened disc with a notch and radial veins, lit edge."""
    rnd = random.Random(seed)
    ry = r * 0.36
    a0 = rnd.uniform(0, 6.28)
    pad = (f"M{f(cx)} {f(cy)}L{f(cx + r * math.cos(a0 - 0.12))} {f(cy + ry * math.sin(a0 - 0.12))}"
           f"A{f(r)} {f(ry)} 0 1 1 {f(cx + r * math.cos(a0 + 0.12))} {f(cy + ry * math.sin(a0 + 0.12))}Z")
    g0, g1 = along_light(fr, cx - r, cy - ry, cx + r, cy + ry)
    veins = "".join(f"M{f(cx)} {f(cy)}L{f(cx + r * 0.9 * math.cos(a0 + 0.4 + k * 0.62))} {f(cy + ry * 0.9 * math.sin(a0 + 0.4 + k * 0.62))}" for k in range(9))
    doc.add(f'<ellipse cx="{f(cx + r * 0.08)}" cy="{f(cy + ry * 0.25)}" rx="{f(r)}" ry="{f(ry)}" fill="{P["shade"]}" opacity="0.35"/>'
            f'<path d="{pad}" fill="{lin(doc, [(0, P["leaf"], 1), (1, P["leaf2"], 1)], g0, g1)}"/>'
            f'<path d="{veins}" stroke="{P["leaflit"]}" stroke-width="{fr.l(3)}" opacity="0.6"/>')


def ripples(doc, fr, P, x0, y0, x1, y1, n, seed, role="ripple"):
    """Short lit arcs on water, longer and wider apart toward the viewer (perspective)."""
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        t = rnd.random()
        y = y0 + (y1 - y0) * t ** 0.8
        x = rnd.uniform(x0, x1)
        l = fr.l(30 + 160 * t)
        out.append(f"M{f(x - l)} {f(y)}q{f(l)} {f(-l * 0.06)} {f(2 * l)} 0")
    doc.add(f'<path d="{"".join(out)}" fill="none" stroke="{P[role]}" stroke-width="{fr.l(4)}" stroke-linecap="round" opacity="0.55"/>')


def bricks(doc, fr, P, clip_d, x0, y0, x1, y1, bw, bh, role="ground"):
    """Running-bond stone courses as a pattern, each block lit on its upper-left edge."""
    i = doc.id("pt")
    doc.defs.append(f'<pattern id="{i}" patternUnits="userSpaceOnUse" width="{f(bw)}" height="{f(bh * 2)}">'
                    f'<path d="M0 0H{f(bw)}M0 {f(bh)}H{f(bw)}M0 0V{f(bh)}M{f(bw / 2)} {f(bh)}V{f(bh * 2)}" stroke="{P["joint"]}" stroke-width="{f(fr.l(4))}" fill="none"/>'
                    f'<path d="M{f(fr.l(4))} {f(fr.l(4))}H{f(bw - fr.l(4))}M{f(bw / 2 + fr.l(4))} {f(bh + fr.l(4))}H{f(bw)}M0 {f(bh + fr.l(4))}H{f(bw / 2 - fr.l(4))}" stroke="{P["jointlit"]}" stroke-width="{f(fr.l(3))}" fill="none" opacity="0.7"/>'
                    f'</pattern>')
    c = doc.id("bc")
    doc.defs.append(f'<clipPath id="{c}"><path d="{clip_d}"/></clipPath>')
    doc.add(f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="url(#{i})" clip-path="url(#{c})" opacity="0.7"/>')


def lattice(doc, fr, x, y, w, h, back, bar, cell):
    """A window lattice (square grid turned into a fret: every other cell holds a short bar)."""
    i = doc.id("lt")
    s = cell
    doc.defs.append(f'<pattern id="{i}" patternUnits="userSpaceOnUse" x="{f(x)}" y="{f(y)}" width="{f(s)}" height="{f(s)}">'
                    f'<path d="M0 0H{f(s)}V{f(s)}M0 0V{f(s)}M{f(s * 0.25)} {f(s * 0.5)}H{f(s * 0.75)}" stroke="{bar}" stroke-width="{f(s * 0.12)}" fill="none"/></pattern>')
    doc.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{f(s * 0.2)}" fill="{back}"/>'
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="url(#{i})"/>')


def dougong(doc, fr, P, x, y, s):
    """One bracket set in cai-fen: bearing block (dou), arms (gong) of a cai 15 x 10 section,
    a second tier, small blocks of the zhi 6 x 4; lit faces up-left."""
    u = s / 15
    parts = []
    def blk(cx, top, w, h, c):
        parts.append(f'<rect x="{f(cx - w / 2)}" y="{f(top)}" width="{f(w)}" height="{f(h)}" rx="{f(u * 1.2)}" fill="{c}"/>'
                     f'<rect x="{f(cx - w / 2)}" y="{f(top)}" width="{f(w)}" height="{f(u * 1.5)}" rx="{f(u * 0.7)}" fill="{P["blocklit"]}" opacity="0.7"/>')
    blk(x, y - 10 * u, 16 * u, 10 * u, P["block"])                  # dou
    blk(x, y - 19 * u, 44 * u, 9 * u, P["block2"])                 # first arm
    for dx in (-18, 0, 18):
        blk(x + dx * u, y - 25 * u, 8 * u, 6 * u, P["block"])     # small blocks (zhi 6 x 4 scale)
    blk(x, y - 33 * u, 64 * u, 8 * u, P["block2"])                 # second arm
    doc.add("".join(parts))


# ---------------------------------------------------------------- forms
def wing(doc, fr, P, x0, y0, x1, y1, th, role, lift, courses=5, fade=0.85, ends=True, rib=None):
    """One roof wing: top edge the juzhe slope ridge -> eave, the eave turning back up (qiao),
    the underside sweeping back. Tiles: courses parallel to the slope (a lit lap over a shadow),
    ribs down the slope, round tile ends along the eave, two rows of rafter ends under it."""
    W, H = fr.w, fr.h
    rise = y1 - y0
    top = juzhe(x0, y0, x1 - 0.07 * W, y1 + 0.05 * rise, purlins=6, first=0.2)
    tip = [(x1 - 0.03 * W, y1 + 0.03 * rise), (x1, y1 - 0.02 * rise)]
    under = [(x1 - 0.015 * W, y1 + th * 0.08), (x1 - 0.05 * W, y1 + th * 0.32),
             (x1 - 0.2 * W, y1 + th * 0.78), (x0 + (x1 - x0) * 0.35, y0 + rise * 0.55 + th),
             (x0, y0 + th * 1.05)]
    outline = top + tip + under
    d = poly(outline)
    dense = bez(outline, 12)
    ntop = (len(top) + len(tip) - 1) * 12
    T, U = dense[:ntop + 1], dense[ntop:]
    rafters = []
    if ends:                                            # rafter ends under the eave, drawn first
        R = resample(U[:len(U) // 2], 40)
        for k, (x, y) in enumerate(R[2:]):
            r = fr.l(16) * (0.5 + 0.5 * (1 - k / 40))
            rafters.append(f'<circle cx="{f(x)}" cy="{f(y + r * 1.4)}" r="{f(r)}" fill="{P["block"]}"/>'
                           f'<circle cx="{f(x - r * 0.25)}" cy="{f(y + r * 1.15)}" r="{f(r * 0.45)}" fill="{P["blocklit"]}" opacity="0.8"/>')
        doc.add("".join(rafters))
    cast(doc, d, P["shade"], fr, lift=lift, opacity=0.3)
    a, b = along_light(fr, x0, y0, x1, y1 + th)
    m = doc.id("m")
    doc.defs.append(f'<linearGradient id="{m}" gradientUnits="userSpaceOnUse" x1="{f(x0)}" y1="0" x2="{f(x1)}" y2="0">'
                    f'<stop offset="0" stop-color="#fff" stop-opacity="{f(fade)}"/><stop offset="0.7" stop-color="#fff"/></linearGradient>'
                    f'<mask id="{m}k"><path d="{d}" fill="url(#{m})"/></mask>')
    g = lin(doc, [(0, P[role], 1), (1, P[role + "2"] if role + "2" in P else P[role], 1)], a, b)
    parts = [f'<path d="{d}" fill="{g}"/>']
    clip = doc.id("c")
    doc.defs.append(f'<clipPath id="{clip}"><path d="{d}"/></clipPath>')
    # ribs: from the top edge down to the underside, evenly spaced along both
    nr = rib or max(24, int((x1 - x0) / fr.l(52)))
    TA, UA = resample(T, nr), resample(U[::-1], nr)
    ribs = "".join(f"M{f(a_[0])} {f(a_[1])}L{f(b_[0])} {f(b_[1])}" for a_, b_ in zip(TA, UA))
    parts.append(f'<path d="{ribs}" stroke="{P["shade"]}" stroke-opacity="0.5" stroke-width="{fr.l(7)}"/>')
    parts.append(f'<path d="{ribs}" transform="translate({-fr.l(5)} 0)" stroke="{P["line"]}" stroke-opacity="0.35" stroke-width="{fr.l(3)}"/>')
    for t in range(1, courses + 1):
        cs = [(a_[0] + (b_[0] - a_[0]) * t / (courses + 1), a_[1] + (b_[1] - a_[1]) * t / (courses + 1)) for a_, b_ in zip(resample(T, 60), resample(U[::-1], 60))]
        dd = pl(cs)
        parts.append(f'<path d="{dd}" fill="none" stroke="{P["shade"]}" stroke-opacity="0.5" stroke-width="{fr.l(10)}" '
                     f'filter="{blurf(doc, fr.l(5))}" transform="translate(0 {fr.l(7)})"/>')
        parts.append(f'<path d="{dd}" fill="none" stroke="{P["line"]}" stroke-opacity="0.6" stroke-width="{fr.l(4)}"/>')
    parts.append(f'<path d="{pl(T)}" fill="none" stroke="{P["line"]}" stroke-opacity="0.7" stroke-width="{fr.l(6)}"/>')
    doc.add(f'<g mask="url(#{m}k)"><g clip-path="url(#{clip})">{"".join(parts)}</g></g>')
    if ends:                                            # round tile ends along the eave front
        E = resample(U[:int(len(U) * 0.55)], 34)
        te = []
        for k, (x, y) in enumerate(E[1:]):
            r = fr.l(15) * (1 - 0.4 * k / 34)
            te.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{P[role + "2"] if role + "2" in P else P[role]}" stroke="{P["line"]}" stroke-width="{fr.l(3)}" stroke-opacity="0.7"/>')
        doc.add("".join(te))
    return T, U


def far_range(doc, fr, P, x0, x1, base, amp, seed, role="far", peaks=4):
    """A far range from x0 to x1 (fractions): peaks joined by juzhe-concave slopes, rising out of
    the mist on the light side (masked), standing on a soft base."""
    rnd = random.Random(seed)
    W, H = fr.w, fr.h
    span = (x1 - x0) * W
    tops = []
    for i in range(peaks):
        x = x0 * W + span * (i + 0.5 + rnd.uniform(-0.15, 0.15)) / peaks
        tops.append((x, (base - amp * (0.55 + 0.45 * rnd.random()) * (0.6 + 0.4 * i / max(1, peaks - 1))) * H))
    pts = [(x0 * W - span * 0.1, base * H)]
    prev = pts[0]
    for x, y in tops:                    # up the concave slope to the peak, then down to a saddle
        up = juzhe(x, y, prev[0], prev[1], purlins=4, first=0.16)[::-1]
        pts += up[1:]
        sx = x + span / peaks * 0.5
        sy = y + (base * H - y) * rnd.uniform(0.35, 0.6)
        down = juzhe(x, y, sx, sy, purlins=4, first=0.16)
        pts += down[1:]
        prev = (sx, sy)
    pts.append((x1 * W + span * 0.1, base * H))
    d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts) + f"L{f(pts[-1][0])} {f((base + 0.25) * H)}L{f(pts[0][0])} {f((base + 0.25) * H)}Z"
    g0, g1 = along_light(fr, x0 * W, (base - amp) * H, x1 * W, base * H)
    m = doc.id("fm")
    doc.defs.append(f'<linearGradient id="{m}g" gradientUnits="userSpaceOnUse" x1="{f(x0 * W)}" y1="0" x2="{f(x0 * W + span * 0.35)}" y2="0">'
                    f'<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
                    f'<mask id="{m}"><rect width="{W}" height="{H}" fill="url(#{m}g)"/></mask>')
    doc.add(f'<path d="{d}" mask="url(#{m})" fill="{lin(doc, [(0, P[role], 1), (1, P[role + "2"] if role + "2" in P else P[role], 1)], g0, g1)}"/>')


def terrace(doc, fr, P, y_left, y_right, role="ground"):
    """The ground plane at the frame bottom: a long curve, lower on the light side."""
    W, H = fr.w, fr.h
    pts = [(-0.05 * W, y_left * H), (0.3 * W, (y_left + 0.01) * H), (0.65 * W, (y_right + 0.02) * H), (1.05 * W, y_right * H)]
    d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts) + f"L{f(1.05 * W)} {f(H * 1.05)}L{f(-0.05 * W)} {f(H * 1.05)}Z"
    g0, g1 = along_light(fr, 0, y_right * H, W, H)
    cast(doc, d, P["shade"], fr, lift=1.2, opacity=0.35)
    doc.add(f'<path d="{d}" fill="{lin(doc, [(0, P[role], 1), (1, P[role + "2"], 1)], g0, g1)}"/>')


def ridge_end(doc, fr, P, x, y, s, role, mirror=False):
    """The ridge-end ornament (chiwen): a curled horn rising from the ridge end, curling inward."""
    k = -1 if mirror else 1
    X = lambda v: f(x + k * v)
    d = (f"M{X(-s * 0.35)} {f(y)}C{X(-s * 0.5)} {f(y - s * 0.7)} {X(-s * 0.1)} {f(y - s * 1.15)} {X(s * 0.35)} {f(y - s * 1.0)}"
         f"C{X(s * 0.1)} {f(y - s * 0.85)} {X(-s * 0.02)} {f(y - s * 0.55)} {X(s * 0.25)} {f(y - s * 0.35)}"
         f"C{X(s * 0.35)} {f(y - s * 0.2)} {X(s * 0.3)} {f(y)} {X(s * 0.3)} {f(y)}Z")
    doc.add(f'<path d="{d}" fill="{P[role]}"/>')


def roof(doc, fr, P, cx, ridge_y, ridge_w, eave_y, eave_w, role, rows=40, flick=0.05, lift=1.5):
    """A hall roof in front elevation: a ridge (ridge tiles, a chiwen at each end), two juzhe
    slopes from the ridge ends down to the eaves, the eave corners turning up (qiao jiao), tile rows
    down the face, tile laps, round tile ends along the eave. Returns the eave line."""
    W, H = fr.w, fr.h
    rh = (eave_y - ridge_y)
    xl, xr = cx - ridge_w / 2, cx + ridge_w / 2
    el, er = cx - eave_w / 2, cx + eave_w / 2
    L = juzhe(xl, ridge_y, el, eave_y, purlins=6, first=0.3)          # ridge -> left eave
    R = juzhe(xr, ridge_y, er, eave_y, purlins=6, first=0.3)
    up = rh * flick * 4
    Lt = L[:-1] + [(el - eave_w * 0.01, eave_y - up)]
    Rt = R[:-1] + [(er + eave_w * 0.01, eave_y - up)]
    sag = rh * 0.06
    eave = [(er + eave_w * 0.01, eave_y - up), (er - eave_w * 0.06, eave_y + sag * 0.2), (cx, eave_y + sag),
            (el + eave_w * 0.06, eave_y + sag * 0.2), (el - eave_w * 0.01, eave_y - up)]
    topline = Lt[::-1] + Rt
    TL = bez(Lt[::-1], 10) + [(xr, ridge_y)] + bez(Rt, 10)[1:]
    EL = bez(eave, 14)
    d = pl(TL) + " " + pl(EL[1:-1]).replace("M", "L", 1) + "Z"
    cast(doc, d, P["shade"], fr, lift=lift, opacity=0.38)
    g0, g1 = along_light(fr, el, ridge_y, er, eave_y)
    doc.add(f'<path d="{d}" fill="{lin(doc, [(0, P[role], 1), (1, P[role + "2"], 1)], g0, g1)}"/>')
    c = doc.id("rc")
    doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
    TA = resample(TL, rows)
    EA = resample(EL[::-1], rows)
    rowsd = "".join(f"M{f(a_[0])} {f(a_[1])}L{f(b_[0])} {f(b_[1])}" for a_, b_ in zip(TA, EA))
    sw = max(K.U, eave_w / rows * 0.32)
    laps = []
    for t in (0.2, 0.4, 0.6, 0.8):
        laps.append(pl([(a_[0] + (b_[0] - a_[0]) * t, a_[1] + (b_[1] - a_[1]) * t) for a_, b_ in zip(TA, EA)]))
    doc.add(f'<g clip-path="url(#{c})">'
            f'<path d="{rowsd}" stroke="{P["shade"]}" stroke-opacity="0.55" stroke-width="{f(sw)}" transform="translate({f(sw * 0.45)} {f(sw * 0.3)})"/>'
            f'<path d="{rowsd}" stroke="{P["line"]}" stroke-opacity="0.75" stroke-width="{f(sw * 0.55)}"/>'
            f'<path d="{"".join(laps)}" fill="none" stroke="{P["shade"]}" stroke-opacity="0.25" stroke-width="{f(sw * 0.5)}"/></g>')
    # tile ends along the eave
    te = "".join(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(sw * 0.75)}"/>' for x, y in EA[1:-1])
    doc.add(f'<g fill="{P[role + "2"]}" stroke="{P["line"]}" stroke-width="{f(sw * 0.25)}">{te}</g>')
    # ridge: a band of ridge tiles, chiwen at both ends
    rb = max(K.U * 2, rh * 0.09)
    doc.add(f'<path d="{rrect(xl - rb * 0.5, ridge_y - rb, ridge_w + rb, rb * 1.3, rb * 0.4)}" fill="{P[role + "2"]}"/>'
            f'<path d="M{f(xl)} {f(ridge_y - rb * 0.55)}H{f(xr)}" stroke="{P["line"]}" stroke-width="{f(rb * 0.18)}" stroke-dasharray="{f(rb * 0.5)} {f(rb * 0.25)}" stroke-opacity="0.8"/>')
    ridge_end(doc, fr, P, xl, ridge_y - rb * 0.6, rb * 2.2, role + "2", mirror=True)
    ridge_end(doc, fr, P, xr, ridge_y - rb * 0.6, rb * 2.2, role + "2")
    return EL


def temple(doc, fr, P, cx, base_y, w, role, double=False, door=True, stair=None, lift=1.5):
    """A hall in front elevation: stone platform (bricks), columns (cinnabar, small), lattice
    windows between them, a bracket band under the eave, the roof; a double eave for the host."""
    W, H = fr.w, fr.h
    s = w / 1000                                    # the hall's own unit
    pf_h = 70 * s
    wall_h = 230 * s
    x0, x1 = cx - w * 0.36, cx + w * 0.36
    # platform
    pf = rrect(x0 - 40 * s, base_y - pf_h, (x1 - x0) + 80 * s, pf_h, 8 * s)
    cast(doc, pf, P["shade"], fr, lift=lift, opacity=0.35)
    doc.add(f'<path d="{pf}" fill="{P["ground"]}"/>')
    bricks(doc, fr, P, pf, x0 - 40 * s, base_y - pf_h, x1 + 40 * s, base_y, 64 * s, 18 * s)
    top = base_y - pf_h
    # wall and columns
    wy = top - wall_h
    doc.add(f'<rect x="{f(x0)}" y="{f(wy)}" width="{f(x1 - x0)}" height="{f(wall_h)}" fill="{P[role + "2"]}"/>')
    n = 7
    step = (x1 - x0) / n
    cw = 18 * s
    for i in range(n):
        lx = x0 + i * step + cw
        if door and i == n // 2:
            dw = step - 2 * cw
            dd = rrect(lx, wy + 40 * s, dw, wall_h - 40 * s, dw / 2, dw / 2, 0, 0)
            doc.add(f'<path d="{dd}" fill="{rad(doc, [(0, P["lightc"], 1), (0.55, P["gold"], 1), (1, P["gold"], 1)], (lx + dw * 0.4, wy + wall_h * 0.4), wall_h)}"/>')
            continue
        lattice(doc, fr, lx + 4 * s, wy + 50 * s, step - 2 * cw - 8 * s, wall_h - 80 * s, P["latback"], P["latbar"], max(K.U * 2, 22 * s))
    for i in range(n + 1):
        x = x0 + i * step
        doc.add(f'<rect x="{f(x - cw / 2)}" y="{f(wy)}" width="{f(cw)}" height="{f(wall_h)}" fill="{P["column"]}"/>'
                f'<rect x="{f(x - cw / 2)}" y="{f(wy)}" width="{f(cw * 0.32)}" height="{f(wall_h)}" fill="{P["blocklit"]}" opacity="0.5"/>')
    # bracket band
    bb = 60 * s
    doc.add(f'<rect x="{f(x0 - 10 * s)}" y="{f(wy - bb)}" width="{f(x1 - x0 + 20 * s)}" height="{f(bb)}" fill="{P["block"]}"/>')
    for i in range(n * 2 + 1):
        dougong(doc, fr, P, x0 + i * step / 2, wy, min(bb * 0.9, step / 2 * 0.85 * 15 / 64))
    if double:
        EL = roof(doc, fr, P, cx, wy - bb - 30 * s, w * 0.78, wy - bb + 70 * s, w * 1.06, role, rows=60, lift=lift)
        # upper storey and roof
        wy2 = wy - bb - 40 * s
        doc.add(f'<rect x="{f(cx - w * 0.27)}" y="{f(wy2 - 150 * s)}" width="{f(w * 0.54)}" height="{f(150 * s)}" fill="{P[role + "2"]}"/>')
        lattice(doc, fr, cx - w * 0.22, wy2 - 120 * s, w * 0.44, 90 * s, P["latback"], P["latbar"], max(K.U * 2, 22 * s))
        doc.add(f'<rect x="{f(cx - w * 0.29)}" y="{f(wy2 - 190 * s)}" width="{f(w * 0.58)}" height="{f(44 * s)}" fill="{P["block"]}"/>')
        for i in range(13):
            dougong(doc, fr, P, cx - w * 0.27 + i * w * 0.54 / 12, wy2 - 150 * s, min(40 * s, w * 0.54 / 12 * 0.85 * 15 / 64))
        roof(doc, fr, P, cx, wy2 - 360 * s, w * 0.4, wy2 - 150 * s, w * 0.86, role, rows=48, lift=lift)
    else:
        roof(doc, fr, P, cx, wy - bb - 210 * s, w * 0.5, wy - bb + 50 * s, w * 1.06, role, rows=44, lift=lift)
    return x0 - 40 * s, x1 + 40 * s, base_y


def hill(doc, fr, P, pts, role, seed, cun_n=70, texture=True):
    """A hill or slope: closed by the frame bottom, lit along 1:2, texture strokes down its face."""
    W, H = fr.w, fr.h
    d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts) + f"L{f(pts[-1][0])} {f(H * 1.05)}L{f(pts[0][0])} {f(H * 1.05)}Z"
    ys = [y for _, y in pts]
    g0, g1 = along_light(fr, pts[0][0], min(ys), pts[-1][0], H)
    cast(doc, d, P["shade"], fr, lift=1.2, opacity=0.3)
    doc.add(f'<path d="{d}" fill="{lin(doc, [(0, P[role], 1), (1, P[role + "2"], 1)], g0, g1)}"/>')
    if texture:
        c = doc.id("hc")
        doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
        doc.add(f'<g clip-path="url(#{c})">')
        cun(doc, fr, P, pts, fr.l(320), seed, "shade", n=cun_n, opacity=0.45)
        cun(doc, fr, P, [(x - fr.l(8), y + fr.l(4)) for x, y in pts], fr.l(260), seed + 1, "line", n=cun_n // 2, opacity=0.35)
        doc.add("</g>")
    return d


def stair(doc, fr, P, pts, w0, w1):
    """A stone stair climbing between terraces: a ribbon narrowing uphill, treads as short lit lines."""
    line = resample(bez(pts, 12), 70)
    left, right, treads = [], [], []
    for i, (x, y) in enumerate(line):
        q = line[min(i + 1, len(line) - 1)]; p0 = line[max(i - 1, 0)]
        dx, dy = q[0] - p0[0], q[1] - p0[1]; n = math.hypot(dx, dy) or 1
        w = w0 + (w1 - w0) * i / (len(line) - 1)
        left.append((x - dy / n * w / 2, y + dx / n * w / 2)); right.append((x + dy / n * w / 2, y - dx / n * w / 2))
        if i % 2 == 0:
            treads.append(f"M{f(left[-1][0])} {f(left[-1][1])}L{f(right[-1][0])} {f(right[-1][1])}")
    d = pl(left) + " L" + " L".join(f"{f(a)} {f(b)}" for a, b in right[::-1]) + "Z"
    doc.add(f'<path d="{d}" fill="{P["jointlit"]}"/><path d="{"".join(treads)}" stroke="{P["joint"]}" stroke-width="{fr.l(4)}" opacity="0.7"/>')



def tree(doc, fr, P, x, y, h, seed, kind="broad", role="leaf"):
    """One tree in flat planes: trunk with a turn, canopy of overlapping lit discs (broad) or
    stacked needle pads (pine); dot texture (dian) on the shade side."""
    rnd = random.Random(seed)
    tw = h * 0.07
    bend = rnd.uniform(-0.1, 0.1) * h
    trunk = f"M{f(x - tw / 2)} {f(y)}Q{f(x + bend - tw / 2)} {f(y - h * 0.4)} {f(x + bend * 0.6 - tw * 0.3)} {f(y - h * 0.7)}L{f(x + bend * 0.6 + tw * 0.3)} {f(y - h * 0.7)}Q{f(x + bend + tw / 2)} {f(y - h * 0.4)} {f(x + tw / 2)} {f(y)}Z"
    doc.add(f'<path d="{trunk}" fill="{P["bark"]}"/>')
    cx, cy = x + bend * 0.6, y - h * 0.68
    out = []
    if kind == "pine":
        for i in range(4):
            yy = cy - h * 0.06 + i * h * 0.12 - h * 0.18
            r = h * (0.16 + 0.07 * i) * rnd.uniform(0.85, 1.1)
            xx = cx + rnd.uniform(-0.05, 0.05) * h
            pad = f"M{f(xx - r)} {f(yy)}C{f(xx - r)} {f(yy - r * 0.45)} {f(xx + r)} {f(yy - r * 0.45)} {f(xx + r)} {f(yy)}C{f(xx + r * 0.6)} {f(yy + r * 0.22)} {f(xx - r * 0.6)} {f(yy + r * 0.22)} {f(xx - r)} {f(yy)}Z"
            g0, g1 = along_light(fr, xx - r, yy - r * 0.45, xx + r, yy + r * 0.2)
            out.append(f'<path d="{pad}" fill="{lin(doc, [(0, P["needle"], 1), (1, P["needle2"], 1)], g0, g1)}"/>')
    else:
        blobs = [(rnd.uniform(-0.24, 0.24) * h, rnd.uniform(-0.22, 0.08) * h, h * rnd.uniform(0.2, 0.3)) for _ in range(6)]
        blobs.sort(key=lambda b: b[1])
        for bx, by, r in blobs:
            g0, g1 = along_light(fr, cx + bx - r, cy + by - r, cx + bx + r, cy + by + r)
            out.append(f'<circle cx="{f(cx + bx)}" cy="{f(cy + by)}" r="{f(r)}" fill="{lin(doc, [(0, P[role + "lit"], 1), (0.45, P[role], 1), (1, P[role + "2"], 1)], g0, g1)}"/>')
        dots = []
        for _ in range(26):
            bx, by, r = blobs[rnd.randrange(len(blobs))]
            a = rnd.uniform(0.2, 1.6)
            rr = r * rnd.uniform(0.3, 0.85)
            dots.append(f'<circle cx="{f(cx + bx + rr * math.cos(a))}" cy="{f(cy + by + rr * math.sin(a))}" r="{f(r * 0.09)}"/>')
        out.append(f'<g fill="{P[role + "2"]}" opacity="0.7">{"".join(dots)}</g>')
    cast(doc, f"M{f(cx - h * 0.3)} {f(y)}a{f(h * 0.3)} {f(h * 0.05)} 0 1 0 {f(h * 0.6)} 0a{f(h * 0.3)} {f(h * 0.05)} 0 1 0 {f(-h * 0.6)} 0Z", P["shade"], fr, lift=0.5, opacity=0.35)
    doc.add("".join(out))


def grove(doc, fr, P, x, y, h, seed, kinds=("broad", "pine", "broad", "broad"), role="leaf"):
    """Mustard Seed grammar: a host tree and guests, never in a row, never equal, trunks not parallel."""
    rnd = random.Random(seed)
    spec = [(0, 0, 1.0), (-0.42, 0.04, 0.72), (0.38, 0.06, 0.6), (0.7, 0.02, 0.48)]
    for (dx, dy, sc), k in sorted(zip(spec, kinds), key=lambda t: t[0][1]):
        tree(doc, fr, P, x + dx * h + rnd.uniform(-0.05, 0.05) * h, y + dy * h, h * sc, rnd.randrange(999), k, role)


def bamboo(doc, fr, P, x, y, h, seed, n=6):
    """A bamboo clump: culms with nodes leaning from one root, leaves in fans of three."""
    rnd = random.Random(seed)
    out, leaves = [], []
    for i in range(n):
        lean = math.radians(rnd.uniform(-10, 14) + (i - n / 2) * 3)
        hh = h * rnd.uniform(0.7, 1.0)
        x0 = x + (i - n / 2) * h * 0.025
        x1, y1 = x0 + math.sin(lean) * hh, y - math.cos(lean) * hh
        w = h * 0.018
        out.append(f'<path d="M{f(x0)} {f(y)}L{f(x1)} {f(y1)}" stroke="{P["leaf2"]}" stroke-width="{f(w)}" stroke-linecap="round"/>')
        for k in range(1, 7):
            t = k / 7
            nx, ny = x0 + (x1 - x0) * t, y + (y1 - y) * t
            out.append(f'<path d="M{f(nx - w * 0.7)} {f(ny)}h{f(w * 1.4)}" stroke="{P["leaflit"]}" stroke-width="{f(w * 0.35)}"/>')
            if k >= 3 and rnd.random() < 0.8:
                side = rnd.choice((-1, 1))
                for j in range(3):
                    a = math.radians(-20 + side * (25 + j * 22))
                    ll = h * 0.11
                    lx, ly = nx + side * math.cos(a) * ll, ny + math.sin(a) * ll * 0.6 + ll * 0.25
                    leaves.append(f"M{f(nx)} {f(ny)}Q{f((nx + lx) / 2 + w)} {f((ny + ly) / 2 - w * 2)} {f(lx)} {f(ly)}Q{f((nx + lx) / 2)} {f((ny + ly) / 2 + w)} {f(nx)} {f(ny)}Z")
    doc.add("".join(out) + f'<path d="{"".join(leaves)}" fill="{P["leaf"]}"/>')



def spiral(cx, cy, r, turns=1.6, ccw=False, n=40):
    pts = []
    for i in range(n):
        t = i / (n - 1)
        a = (1 if ccw else -1) * t * turns * 2 * math.pi
        rr = r * (1 - 0.82 * t)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def cloud(doc, fr, P, x, y, w, seed, role="cloud", lobes=5, tail=True, lift=1.0, opacity=1.0):
    """A ruyi cloud (xiangyun): lobes curled into spirals along a flat-bottomed band, the biggest
    lobe toward the light-facing end, a tail drawn out behind; lit top-left, a coloured shade line
    under the band."""
    rnd = random.Random(seed)
    r0 = w / (lobes * 1.55)
    xs = [x + r0 + i * (w - 2 * r0) / max(1, lobes - 1) for i in range(lobes)]
    rs = [r0 * (1.25 - 0.5 * abs(i - lobes * 0.35) / lobes) * rnd.uniform(0.85, 1.1) for i in range(lobes)]
    base = y + r0 * 0.35
    parts = []
    body = []
    for cx, r in zip(xs, rs):
        body.append(f"M{f(cx - r)} {f(base - r * 0.6)}a{f(r)} {f(r)} 0 1 1 {f(2 * r)} 0a{f(r)} {f(r)} 0 1 1 {f(-2 * r)} 0Z")
    band = rrect(x, base - r0 * 0.9, w, r0 * 0.9, r0 * 0.45)
    body.append(band)
    if tail:
        tx = x - w * 0.35
        body.append(f"M{f(x + r0)} {f(base - r0 * 0.85)}C{f(x - w * 0.1)} {f(base - r0 * 0.9)} {f(tx + w * 0.1)} {f(base - r0 * 0.1)} {f(tx)} {f(base - r0 * 0.25)}C{f(tx + w * 0.12)} {f(base + r0 * 0.05)} {f(x)} {f(base)} {f(x + r0)} {f(base)}Z")
    d = "".join(body)
    cast(doc, d, P["shade"], fr, lift=lift, opacity=0.25 * opacity)
    g0, g1 = along_light(fr, x, y - r0 * 1.6, x + w, base)
    parts.append(f'<path d="{d}" fill="{lin(doc, [(0, P[role], 1), (1, P[role + "2"], 1)], g0, g1)}"/>')
    sp = "".join(pl(spiral(cx + r * 0.08, base - r * 0.62, r * 0.78, ccw=i % 2 == 0)) for i, (cx, r) in enumerate(zip(xs, rs)))
    parts.append(f'<path d="{sp}" fill="none" stroke="{P["cloudline"]}" stroke-width="{f(max(K.U, r0 * 0.07))}" stroke-linecap="round"/>')
    parts.append(f'<path d="M{f(x + r0 * 0.3)} {f(base - r0 * 0.2)}H{f(x + w - r0 * 0.3)}" stroke="{P["cloudline"]}" stroke-width="{f(max(K.U, r0 * 0.06))}" stroke-linecap="round"/>')
    doc.add(f'<g opacity="{f(opacity)}">{"".join(parts)}</g>')


