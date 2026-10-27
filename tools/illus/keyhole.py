# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 Julia Klee
"""The Keyhole: the small door into Wonderland, with the light coming through."""
import math
import random
from kit import f, path, sample, volume, band, sparkle, KEY
from parts import BRASS, BRASS_SPIN, glow, motes, ground, scallop, conic

# right half of the escutcheon outline, top to bottom (mirrored for the left)
PLATE_R = [(256, 58), (266, 61), (273, 72), (270, 86), (280, 96), (302, 102), (324, 98), (338, 110), (334, 128),
           (316, 136), (304, 146), (316, 186), (322, 232), (316, 278), (302, 318), (314, 340), (330, 360),
           (328, 380), (312, 386), (296, 392), (286, 412), (274, 434), (256, 454)]


def mirrored(half):
    right = half
    left = [(512 - x, y) for x, y in half[1:-1]][::-1]
    return right + left


def mark_paths(cx, cy, k):
    """The WolOS keyhole-with-ears as one outline (ears, head, foot), in our coords."""
    def T(x, y):
        return f"{f(cx + (x - 32) * k)} {f(cy + (y - 33) * k)}"
    ears = (f"M{T(22, 22)}C{T(17, 14)} {T(16, 4)} {T(21, 3)}C{T(26, 2)} {T(28, 12)} {T(28, 21)}Z"
            f"M{T(42, 22)}C{T(47, 14)} {T(48, 4)} {T(43, 3)}C{T(38, 2)} {T(36, 12)} {T(36, 21)}Z")
    r = 15 * k
    head = f"M{f(cx - r)} {f(cy)}a{f(r)} {f(r)} 0 1 0 {f(2 * r)} 0a{f(r)} {f(r)} 0 1 0 {f(-2 * r)} 0Z"
    foot = f"M{T(27, 40)}L{T(24, 60)}H{T(40, 60).split()[0]}L{T(37, 40)}Z"
    return ears, head, foot


def engraving(cv, d, w=2.2):
    """Engraved line: dark cut, bright lip below-right."""
    return (f'<path d="{d}" fill="none" stroke="#5E3A08" stroke-width="{w}" stroke-linecap="round" opacity=".75"/>'
            f'<path d="{d}" fill="none" stroke="#FFF1C0" stroke-width="{w * .6}" stroke-linecap="round" opacity=".7" '
            f'transform="translate(.8 1)"/>')


def screw(cv, x, y, r, rot):
    return (f'<circle cx="{f(x + 1.5)}" cy="{f(y + 2)}" r="{f(r)}" fill="#3A2205" opacity=".5" filter="{cv.blur(1.5)}"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{cv.rad(x - r * .4, y - r * .4, r * 1.4, BRASS, x - r * .5, y - r * .5)}"/>'
            f'<path d="M{f(x - r * .75)} {f(y)}H{f(x + r * .75)}" stroke="#5E3A08" stroke-width="{f(r * .28)}" '
            f'transform="rotate({rot} {f(x)} {f(y)})" stroke-linecap="round"/>'
            f'<path d="M{f(x - r * .7)} {f(y + r * .16)}H{f(x + r * .7)}" stroke="#FFF1C0" stroke-width="{f(r * .1)}" '
            f'transform="rotate({rot} {f(x)} {f(y)})" opacity=".8"/>'
            f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="none" stroke="#5E3A08" stroke-width=".8" opacity=".6"/>')


def wonderland_view(cv, box):
    """What you see through the keyhole: a dusk garden, glowing."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    sky = cv.rad(cx, y0 + (y1 - y0) * .45, (y1 - y0) * .75,
                 [(0, "#FFFFFF"), (0.3, "#FFF8E4"), (0.6, "#FFD9B8"), (0.85, "#E3B8FF"), (1, "#B08CFF")])
    g = f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(x1 - x0)}" height="{f(y1 - y0)}" fill="{sky}"/>'
    h = y1 - y0
    w = x1 - x0
    g += glow(cv, cx, y0 + h * .44, w * .45, "#FFFFFF", .95)
    rnd = random.Random(5)
    for _ in range(9):
        g += sparkle(rnd.uniform(x0, x1), rnd.uniform(y0, y0 + h * .6), rnd.uniform(1.5, 3.5), "#fff", rnd.uniform(.6, 1))
    return g


def rays(cv, cx, cy, n, length, spread, seed, color="#FFF4D6", op=.5, a0=0, a1=360, width=(4, 14)):
    rnd = random.Random(seed)
    out = ""
    for i in range(n):
        a = math.radians(rnd.uniform(a0, a1))
        L = length * rnd.uniform(.55, 1)
        wdt = math.radians(rnd.uniform(*width) / 10)
        x1, y1 = cx + math.cos(a - wdt) * L, cy + math.sin(a - wdt) * L
        x2, y2 = cx + math.cos(a + wdt) * L, cy + math.sin(a + wdt) * L
        gr = cv.rad(cx, cy, L, [(0, color, op * rnd.uniform(.5, 1)), (0.6, color, op * .25), (1, color, 0)])
        out += f'<path d="M{f(cx)} {f(cy)}L{f(x1)} {f(y1)}L{f(x2)} {f(y2)}Z" fill="{gr}"/>'
    return f'<g filter="{cv.blur(spread)}">{out}</g>'


def keyhole(cv, backdrop=True, shadow=True):
    g = ""
    cx, cy, k = 256, 248, 2.55
    if shadow:
        g += ground(cv, 256, 488, 170, 14, .3)
    if backdrop:
        # a round panel of violet lacquered wood: the door
        R = 222
        g += (f'<circle cx="262" cy="270" r="{R}" fill="#1A0D4A" opacity=".45" filter="{cv.blur(14)}"/>')
        panel = cv.rad(220, 190, R * 1.25, [(0, "#6E50F0"), (0.4, "#3E24B0"), (0.8, "#22106A"), (1, "#150845")])
        dp = f"M{256 - R} 256a{R} {R} 0 1 0 {2 * R} 0a{R} {R} 0 1 0 {-2 * R} 0Z"
        grain = ""
        rnd = random.Random(8)
        for i in range(34):
            x = 40 + i * 13 + rnd.uniform(-3, 3)
            grain += f"M{f(x)} 30C{f(x + rnd.uniform(-14, 14))} 160 {f(x + rnd.uniform(-14, 14))} 330 {f(x + rnd.uniform(-8, 8))} 490"
        c = cv.clip(dp)
        inner = (f'<path d="{grain}" stroke="#1E0E5C" stroke-width="1.2" fill="none" opacity=".25"/>'
                 f'<path d="{grain}" stroke="#B9A6FF" stroke-width=".7" fill="none" opacity=".18" transform="translate(2 0)"/>'
                 + band(cv, dp, [(34, 34), (478, 478)], (-KEY[0], -KEY[1]), 30, 22, "#0E0630", .55)
                 + band(cv, dp, [(34, 34), (478, 478)], KEY, 10, 8, "#D8C8FF", .55)
                 # the light from the keyhole warms the wood around it
                 + glow(cv, cx, cy + 20, 210, "#FFD9A8", .55))
        g += f'<path d="{dp}" fill="{panel}"/><g clip-path="{c}">{inner}</g>'
        # moulding ring: a bevelled brass bead
        for r, w, col, op in ((R - 6, 7, "#1E0E5C", .7), (R - 7, 4, cv.lin(60, 60, 452, 452, BRASS), 1),
                              (R - 7.6, 1.2, "#FFF4C9", .9)):
            g += f'<circle cx="256" cy="256" r="{r}" fill="none" stroke="{col}" stroke-width="{w}" opacity="{op}"/>'
        g += (f'<circle cx="256" cy="256" r="{R - 26}" fill="none" stroke="#1E0E5C" stroke-width="3" opacity=".5" '
              f'filter="{cv.blur(2)}"/><circle cx="256" cy="256" r="{R - 26}" fill="none" stroke="#B9A6FF" '
              f'stroke-width="1" opacity=".5" transform="translate(-1 -1)"/>')

    # ---- escutcheon: a scalloped rosette of polished brass
    R0 = 168
    rose = scallop(256, 256, R0, 9, 16)
    rp = [(256 + R0 * math.cos(a / 40 * math.pi), 256 + R0 * math.sin(a / 40 * math.pi)) for a in range(80)]
    g += f'<path d="{rose}" fill="#0A0420" opacity=".6" transform="translate(10 14)" filter="{cv.blur(12)}"/>'
    g += f'<path d="{rose}" fill="#0A0420" opacity=".5" transform="translate(2 3)" filter="{cv.blur(2.5)}"/>'
    sheen = conic(256, 256, R0 + 12, BRASS_SPIN)
    g += volume(cv, rose, rp, "#C98F2C", shade=("#3A2205", .5, 12, 8), hi=("#FFF6D6", .7, 5, 3),
                rim=("#C9B8FF", .9, 2.5, 1.5), extra=sheen)
    # scallop ribs: each lobe catches its own highlight
    ribs = ""
    for i in range(16):
        a = 2 * math.pi * (i + .5) / 16
        x0, y0 = 256 + math.cos(a) * (R0 - 26), 256 + math.sin(a) * (R0 - 26)
        x1, y1 = 256 + math.cos(a) * (R0 - 6), 256 + math.sin(a) * (R0 - 6)
        ribs += f"M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}"
    g += engraving(cv, ribs, 1.6)
    # bevelled groove, then the engine-turned inner field
    for r, w, col, op, dx in ((R0 - 30, 6, "#3A2205", .6, 0), (R0 - 30, 2, "#FFF1C0", .8, -1.2)):
        g += (f'<circle cx="{256 + dx}" cy="{256 + dx}" r="{r}" fill="none" stroke="{col}" stroke-width="{w}" '
              f'opacity="{op}"/>')
    Ri = R0 - 36
    fd = f"M{256 - Ri} 256a{Ri} {Ri} 0 1 0 {2 * Ri} 0a{Ri} {Ri} 0 1 0 {-2 * Ri} 0Z"
    fpts = [(256 + Ri * math.cos(a / 40 * math.pi), 256 + Ri * math.sin(a / 40 * math.pi)) for a in range(80)]
    guil = ""
    for i in range(96):
        a = 2 * math.pi * i / 96
        guil += (f"M{f(256 + math.cos(a) * 66)} {f(256 + math.sin(a) * 66)}"
                 f"L{f(256 + math.cos(a) * (Ri - 4))} {f(256 + math.sin(a) * (Ri - 4))}")
    field = (conic(256, 256, Ri + 4, BRASS_SPIN, phase=20)
             + f'<path d="{guil}" stroke="#5E3A08" stroke-width=".9" opacity=".35"/>'
             + f'<path d="{guil}" stroke="#FFF1C0" stroke-width=".5" opacity=".45" transform="rotate(1.2 256 256)"/>'
             + "".join(f'<circle cx="256" cy="256" r="{r}" fill="none" stroke="#5E3A08" stroke-width=".9" opacity=".4"/>'
                       for r in (Ri - 10, Ri - 14)))
    g += volume(cv, fd, fpts, "#D79E36", shade=("#FFF1C0", .45, 8, 5), hi=("#4A2A05", .45, 8, 5), extra=field)
    for a in (-90, 90, 0, 180):
        x, y = 256 + math.cos(math.radians(a)) * (R0 - 17), 256 + math.sin(math.radians(a)) * (R0 - 17)
        g += screw(cv, x, y, 6.5, a + 37)

    # ---- the keyhole itself (the WolOS mark, cut through)
    ears, head, foot = mark_paths(cx, cy, k)
    hole = ears + head + foot
    # a raised brass lip around the hole
    g += (f'<path d="{hole}" fill="none" stroke="#3A2205" stroke-width="12" stroke-linejoin="round" opacity=".55" '
          f'filter="{cv.blur(3)}" transform="translate(2 3)"/>')
    g += (f'<path d="{hole}" fill="none" stroke="{cv.lin(cx - 60, cy - 90, cx + 60, cy + 90, [(0, "#FFF4C9"), (0.5, "#D79E36"), (1, "#6B4410")])}" '
          f'stroke-width="9" stroke-linejoin="round"/>')
    hc = cv.clip(hole)
    x0, y0, x1, y1 = cx - 17 * k, cy - 31 * k, cx + 17 * k, cy + 28 * k
    view = wonderland_view(cv, (x0, y0, x1, y1))
    # inner wall of the hole: the brass is thick, the light comes from deep inside
    wall = (f'<g filter="{cv.blur(2.5)}"><path d="M{f(x0 - 40)} {f(y0 - 40)}H{f(x1 + 40)}V{f(y1 + 40)}H{f(x0 - 40)}Z{hole}" '
            f'fill-rule="evenodd" fill="#6B4410" transform="translate(6 8)" opacity=".9"/></g>'
            f'<g filter="{cv.blur(1.2)}"><path d="M{f(x0 - 40)} {f(y0 - 40)}H{f(x1 + 40)}V{f(y1 + 40)}H{f(x0 - 40)}Z{hole}" '
            f'fill-rule="evenodd" fill="#F6C76A" transform="translate(3 4)" opacity=".9"/></g>')
    g += f'<g clip-path="{hc}">{view}{wall}</g>'

    # ---- light pouring out, towards us: soft on the brass, plain in the air beyond
    m = cv.id("m")
    fade = cv.rad(cx, cy, 300, [(0, "#fff", .35), (0.45, "#fff", .4), (0.62, "#fff", 1), (1, "#fff", 1)])
    cv.defs.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="-100" y="-100" width="712" height="712">'
                   f'<rect x="-100" y="-100" width="712" height="712" fill="{fade}"/></mask>')
    beams = (rays(cv, cx, cy + 4, 30, 330, 5, 3, "#FFE3A6", 1, 0, 360, (5, 15))
             + rays(cv, cx, cy + 4, 14, 300, 2, 6, "#FFFFFF", .9, 0, 360, (1.5, 4)))
    pc = cv.clip("M36 256a220 220 0 1 0 440 0a220 220 0 1 0 -440 0Z")
    g += f'<g clip-path="{pc}"><g mask="url(#{m})">{beams}</g></g>'
    g += glow(cv, cx, cy, 120, "#FFE2A8", .45)
    g += glow(cv, cx, cy - 6, 70, "#FFFFFF", .75)
    g += motes(cv, (80, 70, 440, 440), 40, 21, "#FFF6DA", 6)
    return g
