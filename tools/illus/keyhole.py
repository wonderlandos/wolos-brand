# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""The Keyhole: the small door into Wonderland, with the light coming through.
It is the WolOS mark made as an object: four nested arched doors on one floor line. The outer
door is a polished brass frame, the next two are violet lacquer set deeper and deeper into it,
and the smallest door is open: Wonderland light pours out of it, over the lacquer and the sill."""
import math
import os
import random
import sys
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "brand"))
from kit import f, volume, band, sparkle, KEY
from parts import BRASS, glow, motes, ground
from marks import door_boxes, door_geo, ACC, DEEP, NIGHT, LIGHT  # noqa: E402  (the one door geometry)

# mark space: the brand mark is drawn on a 1024 grid; 1024 units = 81.92 of ours at k = 1, and
# the point (512, 542.5) of that grid lands on (cx, cy).  So k means the same here as it did for
# the earlier 64-unit mark: k = 1 is the 64 px mark.
MARK_S = 0.08
MARK_O = (512, 542.5)
FLOOR = 880


def _at(cx, cy, k):
    s = MARK_S * k
    return lambda x, y: (cx + (x - MARK_O[0]) * s, cy + (y - MARK_O[1]) * s)


def door_list(cx, cy, k, n=4):
    """The mark's n nested doors in our coords, outer first: [(x0, x1, floor_y, arch_y, r)]."""
    P = _at(cx, cy, k)
    out = []
    for g in door_boxes(n):
        x0, x1, yb, ya, r = door_geo(*g)
        (X0, YB), (X1, YA) = P(x0, yb), P(x1, ya)
        out.append((X0, X1, YB, YA, r * MARK_S * k))
    return out


def arch(d):
    """One door as a closed path, drawn clockwise (so nested doors union under nonzero)."""
    x0, x1, yb, ya, r = d
    return f"M{f(x0)} {f(yb)}V{f(ya)}A{f(r)} {f(r)} 0 0 1 {f(x1)} {f(ya)}V{f(yb)}Z"


def arch_pts(d, n=24):
    """The door outline as points (for the light bands), clockwise from the bottom left."""
    x0, x1, yb, ya, r = d
    cx = (x0 + x1) / 2
    pts = [(x0, yb), (x0, (yb + ya) / 2)]
    pts += [(cx - r * math.cos(math.pi * i / n), ya - r * math.sin(math.pi * i / n)) for i in range(n + 1)]
    return pts + [(x1, (yb + ya) / 2), (x1, yb), (cx, yb)]


def in_door(d, x, y):
    x0, x1, yb, ya, r = d
    if not (x0 <= x <= x1 and y <= yb):
        return False
    return y >= ya or (x - (x0 + x1) / 2) ** 2 + (y - ya) ** 2 <= r * r


# right half of the brass frame outline, top to bottom (mirrored for the left): the mark's outer
# door at the size the character draws it
PLATE_R = [(round(x), round(y)) for x, y in arch_pts(door_list(256, 260, 7.2)[0], 8)[6:]]


def mirrored(half):
    right = half
    left = [(512 - x, y) for x, y in half[1:-1]][::-1]
    return right + left


def mark_paths(cx, cy, k):
    """The WolOS mark, nested doors on one floor line, as three parts (outer door, the two
    middle doors, the lit door). All clockwise, so together under nonzero they fill the outer
    door's silhouette, and stroked they draw every door. In our coords."""
    ds = door_list(cx, cy, k)
    return arch(ds[0]), arch(ds[1]) + arch(ds[2]), arch(ds[3])


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
    """What you see through the little door: a dusk garden, washed out by its own light."""
    x0, y0, x1, y1 = box
    cx = (x0 + x1) / 2
    h = y1 - y0
    w = x1 - x0
    sky = cv.rad(cx, y0 + h * .55, h * .8,
                 [(0, "#FFFFFF"), (0.35, "#FFF7EC"), (0.7, LIGHT), (1, "#C4B2FF")])
    g = f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(w)}" height="{f(h)}" fill="{sky}"/>'
    # a lawn and a path running away from the door
    g += (f'<path d="M{f(x0)} {f(y0 + h * .74)}C{f(cx - w * .2)} {f(y0 + h * .68)} {f(cx + w * .2)} {f(y0 + h * .76)} '
          f'{f(x1)} {f(y0 + h * .7)}V{f(y1)}H{f(x0)}Z" fill="#D6C8FF" opacity=".7"/>'
          f'<path d="M{f(cx - w * .26)} {f(y1)}L{f(cx - w * .03)} {f(y0 + h * .72)}H{f(cx + w * .03)}L{f(cx + w * .26)} {f(y1)}Z" '
          f'fill="#FFF8EC"/>')
    g += glow(cv, cx, y0 + h * .6, w * .7, "#FFFFFF", .95)
    rnd = random.Random(5)
    for _ in range(6):
        g += sparkle(rnd.uniform(x0, x1), rnd.uniform(y0, y0 + h * .55), rnd.uniform(1.5, 3), "#fff", rnd.uniform(.6, 1))
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


def lip(d):
    """The arch of a door without its floor edge: where one door meets the one around it."""
    x0, x1, yb, ya, r = d
    return f"M{f(x0)} {f(yb)}V{f(ya)}A{f(r)} {f(r)} 0 0 1 {f(x1)} {f(ya)}V{f(yb)}"


def recess(cv, d, top, bottom, depth, u=1.0):
    """A lacquered door set into the one around it: the lip above casts a shadow down into it
    (the key light is top-left), its lower right edge catches the light, and the open door
    further in warms its floor. `u` scales every distance (1 at k = 6.4)."""
    x0, x1, yb, ya, r = d
    p = arch(d)
    pts = arch_pts(d)
    fill = cv.lin(x0, ya - r, x1, yb, [(0, top), (1, bottom)])
    inner = (band(cv, p, pts, (-.35, -1), (12 + depth * 3) * u, 6 * u, "#0A0628", .7)
             + band(cv, p, pts, (-KEY[0], -KEY[1]), 2.5 * u, 1.5 * u, "#E9E3FF", .45)
             + glow(cv, (x0 + x1) / 2, yb - (yb - ya + r) * .22, (x1 - x0) * .62, "#FFC98A", .30))
    bead = cv.lin(x0, ya - r, x1, yb, [(0, "#7A4E12"), (0.45, "#C98F2C"), (1, "#FFF1C0")])
    return (volume(cv, p, pts, fill, hi=("#0A0628", .55, (5 + depth * 2) * u, (4 + depth) * u), extra=inner)
            + f'<path d="{lip(d)}" fill="none" stroke="{bead}" stroke-width="{f(max((3.2 - depth * .6) * u, .8))}"/>')


def light_heart(ds):
    """Where the light is brightest: low inside the little open door."""
    lx0, lx1, lyb, lya, lr = ds[3]
    return (lx0 + lx1) / 2, lyb - (lyb - lya + lr) * .45


def door_set(cv, cx, cy, k, bead=True):
    """The mark as an object: the outer door in violet lacquer, two lacquered doors set deeper,
    the little one open on Wonderland with its light pouring out over the lacquer.
    Same placement as mark_paths(cx, cy, k)."""
    u = k / 6.4
    ds = door_list(cx, cy, k)
    outer, mid, deep, lit = ds
    x0, x1, yb, ya, r = outer
    lx0, lx1, lyb, lya, lr = lit
    lcx, lcy = light_heart(ds)
    po, pts = arch(outer), arch_pts(outer)
    lacquer = cv.lin(x0, ya - r, x1, yb, [(0, "#A48CFF"), (0.35, ACC), (1, "#5A3BE0")])
    e = 18 * u
    gloss = (f'<path d="M{f(x0 + e)} {f(ya + 40 * u)}V{f(ya)}A{f(r - e)} {f(r - e)} 0 0 1 {f((x0 + x1) / 2 - 10 * u)} '
             f'{f(ya - r + e)}" fill="none" stroke="#FFFFFF" stroke-width="{f(10 * u)}" stroke-linecap="round" '
             f'opacity=".28" filter="{cv.blur(4 * u)}"/>')
    g = volume(cv, po, pts, lacquer, shade=("#1E0E5C", .55, 16 * u, 10 * u), hi=("#FFFFFF", .45, 6 * u, 4 * u),
               rim=("#FFD9A8", .8, 3 * u, 1.6 * u), extra=gloss)
    if bead:
        bd = cv.lin(x0, ya - r, x1, yb, [(0, "#FFF4C9"), (0.3, "#E9B654"), (0.6, "#9A6618"), (0.8, "#F2C766"), (1, "#7A4E12")])
        g += (f'<path d="{lip(outer)}" fill="none" stroke="#3A2205" stroke-width="{f(7 * u)}" opacity=".35" '
              f'transform="translate({f(u)} {f(2 * u)})" filter="{cv.blur(1.5 * u)}"/>'
              f'<path d="{lip(outer)}" fill="none" stroke="{bd}" stroke-width="{f(5 * u)}"/>'
              f'<path d="{lip(outer)}" fill="none" stroke="#FFF6D6" stroke-width="{f(1.2 * u)}" opacity=".8" '
              f'transform="translate({f(-.8 * u)} {f(-.8 * u)})"/>')
    g += recess(cv, mid, "#6446F0", DEEP, 1, u)
    g += recess(cv, deep, "#3F27B0", NIGHT, 2, u)
    # the little door is open: Wonderland beyond, a lavender jamb catching its light
    pl, lpts = arch(lit), arch_pts(lit)
    view = wonderland_view(cv, (lx0, lya - lr, lx1, lyb))
    jamb = (band(cv, pl, lpts, KEY, 5 * u, 3 * u, "#7A5CCF", .55)
            + band(cv, pl, lpts, KEY, 1.5 * u, u, "#FFFFFF", .8))
    g += f'<g clip-path="{cv.clip(pl)}">{view}{jamb}</g>'
    # its light across the lacquer (only inside the doors) and down onto the floor
    m = cv.id("m")
    bx0, by0, bw, bh = x0 - 40 * u, ya - r - 40 * u, x1 - x0 + 80 * u, yb - ya + r + 80 * u
    fade = cv.rad(lcx, lcy, 260 * u, [(0, "#fff", .2), (0.3, "#fff", .55), (0.7, "#fff", 1), (1, "#fff", 0)])
    cv.defs.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="{f(bx0)}" y="{f(by0)}" width="{f(bw)}" height="{f(bh)}">'
                   f'<rect x="{f(bx0)}" y="{f(by0)}" width="{f(bw)}" height="{f(bh)}" fill="{fade}"/></mask>')
    beams = (rays(cv, lcx, lcy, 18, 220 * u, 5 * u, 3, "#FFE3A6", .9, 190, 350, (5, 14))
             + rays(cv, lcx, lcy, 8, 200 * u, 2 * u, 6, "#FFFFFF", .8, 200, 340, (1.5, 4)))
    mc = cv.clip(arch(mid))
    g += f'<g clip-path="{mc}"><g mask="url(#{m})">{beams}</g>{glow(cv, lcx, lyb, 150 * u, "#FFD9A0", .55)}</g>'
    g += glow(cv, lcx, lcy, 90 * u, "#FFE8BC", .45) + glow(cv, lcx, lcy + 6 * u, 46 * u, "#FFFFFF", .7)
    return g


def keyhole(cv, backdrop=True, shadow=True):
    """The character at 512x512. `backdrop` adds the warm halo the door stands in."""
    g = ""
    cx, cy, k = 256, 260, 7.2
    ds = door_list(cx, cy, k)
    outer, lit = ds[0], ds[3]
    x0, x1, yb, ya, r = outer
    lcx, lcy = light_heart(ds)
    if shadow:
        g += ground(cv, cx, yb + 14, 214, 18, .34)
    if backdrop:
        g += glow(cv, cx, cy + 10, 250, "#FFE2B0", .22) + glow(cv, cx, cy - 20, 200, "#B9A6FF", .18)
    po = arch(outer)
    g += f'<path d="{po}" fill="#140A3A" opacity=".45" transform="translate(10 14)" filter="{cv.blur(12)}"/>'
    g += f'<path d="{po}" fill="#140A3A" opacity=".45" transform="translate(2 3)" filter="{cv.blur(2.5)}"/>'
    g += door_set(cv, cx, cy, k)

    # ---- the sill: the mark's floor line, a brass bar the doors stand on, lit from inside
    sx0, sx1, sy, sh = x0 - 16, x1 + 16, yb - 2, 16
    sill = f"M{f(sx0 + 6)} {f(sy)}H{f(sx1 - 6)}Q{f(sx1)} {f(sy)} {f(sx1)} {f(sy + 6)}V{f(sy + sh - 5)}Q{f(sx1)} {f(sy + sh)} " \
           f"{f(sx1 - 6)} {f(sy + sh)}H{f(sx0 + 6)}Q{f(sx0)} {f(sy + sh)} {f(sx0)} {f(sy + sh - 5)}V{f(sy + 6)}Q{f(sx0)} {f(sy)} {f(sx0 + 6)} {f(sy)}Z"
    spts = [(sx0, sy), (sx1, sy), (sx1, sy + sh), (sx0, sy + sh)]
    sfill = cv.lin(0, sy, 0, sy + sh, [(0, "#FFF0B8"), (0.35, "#D9A040"), (1, "#6B4410")])
    spill = cv.rad(lcx, sy, 150, [(0, "#FFFFFF", .95), (0.4, "#FFE6B8", .55), (1, "#FFE6B8", 0)],
                   tf=f"translate({f(lcx)} {f(sy)}) scale(1 .25) translate({f(-lcx)} {f(-sy)})")
    g += f'<path d="{sill}" fill="#140A3A" opacity=".4" transform="translate(4 6)" filter="{cv.blur(5)}"/>'
    g += volume(cv, sill, spts, sfill, hi=("#FFF6D6", .6, 2, 1),
                extra=f'<rect x="{f(sx0)}" y="{f(sy - 40)}" width="{f(sx1 - sx0)}" height="80" fill="{spill}"/>')
    g += motes(cv, (lcx - 120, lit[3] - lit[4] - 120, lcx + 120, lit[2] - 10), 22, 21, "#FFF6DA", 5)
    return g
