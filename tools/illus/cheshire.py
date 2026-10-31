# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""The Cheshire Cat: curled into a ring, tail vanishing first. Loading and thinking."""
import math
import random
from kit import f, path, sample, fluffy, volume, band, fur, KEY, ellipse_pts
from parts import crescent, glow, ground

LIGHT = "#E4DAFF"
MID = "#B7A2FF"
DARK = "#6A4AE8"
DEEPER = "#3E24B0"

C = (236, 282)
RAD = 140
TH0, SPAN = -38.0, 292.0     # head at the top right, tail curling round to the top left


def width(u):
    # neck -> chest -> belly -> haunch -> tail
    if u < .5:
        return 84 + 30 * math.sin(u / .5 * math.pi * .9)
    if u < .62:
        return 84 - (u - .5) / .12 * 52
    return 32 - (u - .62) / .38 * 18


def at(u, off=0.0):
    th = math.radians(TH0 + SPAN * u)
    r = RAD + off
    return C[0] + r * math.cos(th), C[1] + r * math.sin(th)


def body_pts(n=36):
    outer = [at(i / n, width(i / n) / 2) for i in range(n + 1)]
    inner = [at(i / n, -width(i / n) / 2) for i in range(n + 1)]
    # rounded tail tip
    tx, ty = at(1.0, 0)
    th = math.radians(TH0 + SPAN)
    tip = (tx - math.sin(th) * 12, ty + math.cos(th) * 12)
    return outer[1:] + [tip] + inner[::-1][:-1]


def stripes(cv, n=22):
    out = ""
    rnd = random.Random(4)
    for i in range(n):
        u = .03 + i / n * .97
        w = .018 + .006 * rnd.random()
        pts = []
        for k in range(7):
            off = -70 + k * 140 / 6
            wob = math.sin(k * 1.3 + i) * .01
            pts.append(at(u + wob, off))
        for k in range(7):
            off = 70 - k * 140 / 6
            wob = math.sin(k * 1.1 + i * 2) * .008
            pts.append(at(u + w + wob + (.006 if 2 < k < 5 else 0), off))
        out += f'<path d="{path(pts, t=.8)}"/>'
    return out


def cat_eye(cv, cx, cy, rx, ry, rot, lid, look=0.0):
    t = f"rotate({f(rot)} {f(cx)} {f(cy)})"
    # almond
    d = (f"M{f(cx - rx)} {f(cy)}Q{f(cx - rx * .2)} {f(cy - ry * 1.5)} {f(cx + rx)} {f(cy - ry * .15)}"
         f"Q{f(cx + rx * .1)} {f(cy + ry * 1.3)} {f(cx - rx)} {f(cy)}Z")
    c = cv.clip(d, t)
    ix = cx + look * rx * .3
    iris = cv.rad(ix, cy + ry * .2, rx * .85, [(0, "#FFF6B8"), (0.45, "#FFD24A"), (0.8, "#E59A1A"), (1, "#8A4E0A")],
                  ix, cy + ry * .5)
    g = (f'<path d="{d}" fill="{DEEPER}" opacity=".5" transform="{t} translate(1 2)" filter="{cv.blur(3)}"/>'
         f'<path d="{d}" fill="{iris}" transform="{t}"/>')
    inner = (f'<ellipse cx="{f(ix)}" cy="{f(cy)}" rx="{f(rx * .16)}" ry="{f(ry * 1.1)}" fill="#1A0A06"/>'
             # the lid: heavy, smug
             f'<path d="M{f(cx - rx * 1.4)} {f(cy - ry * 2)}H{f(cx + rx * 1.4)}V{f(cy - ry + 2 * ry * lid)}'
             f'Q{f(cx)} {f(cy - ry + 2 * ry * lid + ry * .5)} {f(cx - rx * 1.4)} {f(cy - ry + 2 * ry * lid + ry * .1)}Z" '
             f'fill="{cv.lin(cx, cy - ry, cx, cy + ry * .2, [(0, MID), (1, DARK)])}"/>'
             f'<path d="M{f(cx - rx * 1.4)} {f(cy - ry + 2 * ry * lid + ry * .1)}Q{f(cx)} {f(cy - ry + 2 * ry * lid + ry * .5)} '
             f'{f(cx + rx * 1.4)} {f(cy - ry + 2 * ry * lid)}" stroke="#3A1A12" stroke-width="5" fill="none" opacity=".5" '
             f'filter="{cv.blur(2)}"/>'
             # cheeks push the lower lid up: a grin reaches the eyes
             f'<path d="M{f(cx - rx * 1.4)} {f(cy + ry * 2)}V{f(cy + ry * .75)}Q{f(cx)} {f(cy + ry * .3)} '
             f'{f(cx + rx * 1.4)} {f(cy + ry * .62)}V{f(cy + ry * 2)}Z" fill="{cv.lin(cx, cy, cx, cy + ry, [(0, "#C9B8FF"), (1, LIGHT)])}"/>'
             f'<path d="M{f(cx - rx * 1.4)} {f(cy + ry * .75)}Q{f(cx)} {f(cy + ry * .3)} {f(cx + rx * 1.4)} {f(cy + ry * .62)}" '
             f'stroke="#5A2A10" stroke-width="3" fill="none" opacity=".35" filter="{cv.blur(1.5)}"/>'
             f'<ellipse cx="{f(ix - rx * .3)}" cy="{f(cy + ry * .1)}" rx="{f(rx * .14)}" ry="{f(ry * .14)}" fill="#fff"/>'
             f'<ellipse cx="{f(ix + rx * .3)}" cy="{f(cy + ry * .5)}" rx="{f(rx * .3)}" ry="{f(ry * .12)}" fill="#FFF6B8" '
             f'opacity=".6" filter="{cv.blur(1.5)}"/>')
    g += f'<g clip-path="{c}"><g transform="{t}">{inner}</g></g>'
    g += f'<path d="{d}" fill="none" stroke="#24104F" stroke-width="2.6" transform="{t}"/>'
    return g


def cheshire(cv, shadow=True):
    g = ""
    if shadow:
        g += ground(cv, 256, 470, 150, 13, .25)
    pts = body_pts()
    bd = path(pts, t=.9)
    bp = sample(pts, per=6, t=.9)
    fill = cv.lin(120, 120, 400, 440, [(0, LIGHT), (0.5, MID), (1, "#8E72FF")])
    stripe_g = f'<g fill="{DARK}" opacity=".85">{stripes(cv)}</g>'
    hairs = fur(cv, bp, 160, lambda x, y: math.atan2(y - C[1], x - C[0]) + 1.4, (5, 10), .8,
                ("#ffffff", "#F0EBFF", "#4A2FC0"), (.15, .45), 9)
    # the tail vanishes first: a mask of wedges fading along the curl
    m = cv.id("m")
    wedges = ""
    n = 48
    u0 = .5
    for i in range(n):
        ua, ub = u0 + (1 - u0) * i / n, u0 + (1 - u0) * (i + 1.2) / n
        a, b = at(ua, 90), at(ub, 90)
        op = max(0.0, 1 - (i / n) ** 1.3 * 1.0)
        wedges += f'<path d="M{f(C[0])} {f(C[1])}L{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}Z" fill="#fff" fill-opacity="{op:.3f}"/>'
    ua = at(u0, 90)
    ue = at(1.0, 90)
    # everything outside the fading sector stays fully visible
    keep = ""
    for i in range(40):
        a0 = TH0 + SPAN * u0 - (i + 1) * 9
        p1 = (C[0] + 400 * math.cos(math.radians(a0)), C[1] + 400 * math.sin(math.radians(a0)))
        p2 = (C[0] + 400 * math.cos(math.radians(a0 + 9.5)), C[1] + 400 * math.sin(math.radians(a0 + 9.5)))
        if i * 9 > 360 - SPAN * (1 - u0) - 12:
            break
        keep += f'<path d="M{f(C[0])} {f(C[1])}L{f(p1[0])} {f(p1[1])}L{f(p2[0])} {f(p2[1])}Z" fill="#fff"/>'
    cv.defs.append(f'<mask id="{m}" maskUnits="userSpaceOnUse" x="-100" y="-100" width="712" height="712">'
                   f'<g filter="{cv.blur(5)}">{keep}{wedges}</g></mask>')
    body = volume(cv, bd, bp, fill, shade=(DEEPER, .55, 22, 14), hi=("#FFFFFF", .7, 8, 6),
                  rim=("#E8DEFF", .9, 3, 1.6), under=stripe_g, extra=hairs
                  + band(cv, bd, bp, (0, 1), 12, 8, "#24104F", .35))
    # a hind paw tucked into the curl
    paws = ""
    px, py = at(.39, -44)
    tang = TH0 + SPAN * .39 + 90
    for (px, py, rot) in ((px, py, tang),):
        pp = ellipse_pts(px, py, 22, 15, 10, rot)
        paws += f'<ellipse cx="{f(px + 3)}" cy="{f(py + 6)}" rx="22" ry="12" fill="{DEEPER}" opacity=".4" filter="{cv.blur(4)}"/>'
        paws += volume(cv, path(pp), sample(pp), cv.lin(px - 20, py - 15, px + 20, py + 15, [(0, LIGHT), (1, MID)]),
                       shade=(DEEPER, .45, 8, 5), hi=("#fff", .6, 4, 3), rim=("#E8DEFF", .9, 2, 1))
        paws += (f'<path d="M{f(px + 8)} {f(py - 10)}q4 8 2 18M{f(px)} {f(py - 12)}q3 9 1 20" stroke="{DEEPER}" '
                 f'stroke-width="1.3" fill="none" opacity=".5" transform="rotate({f(rot - 90)} {f(px)} {f(py)})"/>')
    g += f'<g mask="url(#{m})">{body}</g>{paws}'

    # ---- head
    hx, hy = 318, 156
    g += f'<g transform="rotate(7 {hx} {hy + 40})">{head(cv, hx, hy)}</g>'
    return g


def head(cv, hx, hy):
    g = ""
    # ears
    for sgn, rot in ((-1, -14), (1, 18)):
        ex = hx + sgn * 58
        ear = [(ex - 30, hy - 30), (ex - 6 + sgn * 6, hy - 100, 0), (ex + 30, hy - 36)]
        if sgn < 0:
            ear = [(ex - 30, hy - 36), (ex - 10, hy - 104, 0), (ex + 30, hy - 30)]
        ed = path(ear + [(ex, hy - 10)], t=.6)
        g += volume(cv, ed, sample(ear + [(ex, hy - 10)], t=.6),
                    cv.lin(ex - 30, hy - 100, ex + 30, hy - 20, [(0, LIGHT), (1, DARK)]),
                    shade=(DEEPER, .5, 10, 6), hi=("#fff", .6, 5, 3), rim=("#E8DEFF", .9, 2.4, 1.2))
        inner = [(ex - 16, hy - 40), (ex - 6 + (2 if sgn > 0 else -4), hy - 86, 0), (ex + 16, hy - 42)]
        g += volume(cv, path(inner + [(ex, hy - 30)], t=.6), sample(inner + [(ex, hy - 30)], t=.6),
                    cv.lin(ex, hy - 86, ex, hy - 36, [(0, "#FFC2DA"), (1, "#C25FA0")]),
                    shade=("#7A2A6A", .5, 6, 4))
        g += (f'<path d="M{f(ex - 4)} {f(hy - 44)}l{f(-3 * sgn)} -22M{f(ex + 4)} {f(hy - 44)}l{f(2 * sgn)} -18" '
              f'stroke="#fff" stroke-width="1.2" opacity=".7"/>')
    # head: wide, with cheek ruffs
    hpts = [(hx, hy - 66), (hx + 48, hy - 60), (hx + 84, hy - 30), (hx + 100, hy + 8), (hx + 92, hy + 44),
            (hx + 60, hy + 70), (hx, hy + 80), (hx - 60, hy + 70), (hx - 92, hy + 44), (hx - 100, hy + 8),
            (hx - 84, hy - 30), (hx - 48, hy - 60)]
    hd, hp = fluffy(hpts, [(0.2, 0.46, 1.0), (0.54, 0.8, 1.0)], amp=7, step=13, sweep=.55, seed=77)
    hfill = cv.lin(hx - 90, hy - 70, hx + 80, hy + 90, [(0, "#F1EBFF"), (0.5, MID), (1, "#8E72FF")])
    hstr = ""
    # tabby stripes: forehead and cheeks
    for (x0, y0, x1, y1, x2, y2, w) in ((-14, -64, -10, -50, -6, -36, 7), (14, -64, 10, -50, 6, -36, 7),
                                        (0, -66, 0, -54, 0, -42, 6),
                                        (-100, 4, -84, 8, -66, 14, 8), (-100, 22, -86, 26, -70, 28, 7),
                                        (100, 4, 84, 8, 66, 14, 8), (100, 22, 86, 26, 70, 28, 7),
                                        (-44, -60, -40, -48, -34, -36, 6), (44, -60, 40, -48, 34, -36, 6)):
        hstr += (f'<path d="M{f(hx + x0)} {f(hy + y0)}Q{f(hx + x1)} {f(hy + y1)} {f(hx + x2)} {f(hy + y2)}" '
                 f'stroke="{DARK}" stroke-width="{w}" stroke-linecap="round" fill="none"/>')
    hhair = fur(cv, hp, 110, lambda x, y: math.atan2(y - hy + 40, x - hx), (4, 9), .8, ("#ffffff", "#4A2FC0"),
                (.15, .4), 78)
    g += volume(cv, hd, hp, hfill, shade=(DEEPER, .55, 18, 12), hi=("#FFFFFF", .75, 8, 6),
                rim=("#E8DEFF", .95, 3, 1.6), under=f'<g opacity=".8">{hstr}</g>', extra=hhair)
    # muzzle glow so the grin sits on a lighter field
    g += f'<ellipse cx="{hx}" cy="{hy + 30}" rx="74" ry="34" fill="#F4EFFF" opacity=".55" filter="{cv.blur(10)}"/>'
    # eyes: half-closed, pleased with themselves
    g += cat_eye(cv, hx - 40, hy - 18, 25, 30, -10, .2, .2)
    g += cat_eye(cv, hx + 40, hy - 20, 25, 30, 10, .2, .2)
    # the grin: enormous, closed, every tooth on show
    gl, gr_, gy = hx - 84, hx + 86, hy + 16

    def lip(u, top):
        x = gl + (gr_ - gl) * u
        sag = 4 * u * (1 - u)
        y = gy - 6 * u + (22 if top else 46) * sag ** (1.0 if top else .8)
        return x, y
    N = 24
    up = [lip(i / N, True) for i in range(N + 1)]
    lo = [lip(i / N, False) for i in range(N + 1)][::-1]
    grin = "M" + "L".join(f"{f(x)} {f(y)}" for x, y in up + lo) + "Z"
    gc = cv.clip(grin)
    mouth = cv.lin(hx, gy, hx, gy + 50, [(0, "#4A0E3A"), (1, "#22051C")])
    tooth = cv.lin(hx, gy - 4, hx, gy + 48, [(0, "#FFFFFF"), (0.7, "#F3EEFB"), (1, "#CFC3E6")])
    teeth = ""
    nt = 16
    for i in range(nt):
        u0, u1 = i / nt, (i + 1) / nt
        a0, a1 = lip(u0, True), lip(u1, True)
        b0, b1 = lip(u0, False), lip(u1, False)
        mid = lambda p, q, k: (p[0] + (q[0] - p[0]) * k, p[1] + (q[1] - p[1]) * k)
        m0, m1 = mid(a0, b0, .5), mid(a1, b1, .5)
        # upper tooth: from the top lip down to just past the bite line, rounded tip
        teeth += (f'<path d="M{f(a0[0])} {f(a0[1] - 4)}L{f(a1[0])} {f(a1[1] - 4)}L{f(m1[0] - .6)} {f(m1[1])}'
                  f'Q{f((m0[0] + m1[0]) / 2)} {f((m0[1] + m1[1]) / 2 + 4)} {f(m0[0] + .6)} {f(m0[1])}Z"/>')
        teeth += (f'<path d="M{f(b0[0])} {f(b0[1] + 4)}L{f(b1[0])} {f(b1[1] + 4)}L{f(m1[0] - .6)} {f(m1[1] + 2.5)}'
                  f'Q{f((m0[0] + m1[0]) / 2)} {f((m0[1] + m1[1]) / 2 - 1)} {f(m0[0] + .6)} {f(m0[1] + 2.5)}Z"/>')
    mouth_inner = (f'<rect x="{gl - 10}" y="{gy - 30}" width="{gr_ - gl + 20}" height="100" fill="{mouth}"/>'
                   f'<g fill="{tooth}" stroke="#A898C8" stroke-width=".9">{teeth}</g>'
                   + band(cv, grin, [(gl, gy - 20), (gr_, gy + 70)], (0, -1), 7, 4, "#3A1060", .5)
                   + band(cv, grin, [(gl, gy - 20), (gr_, gy + 70)], (0, 1), 6, 4, "#3A1060", .35)
                   + f'<path d="M{f(gl + 30)} {f(gy + 6)}Q{f(hx)} {f(gy + 18)} {f(gr_ - 40)} {f(gy + 2)}" stroke="#fff" '
                   f'stroke-width="3" fill="none" opacity=".6" filter="{cv.blur(1.5)}"/>')
    g += f'<path d="{grin}" fill="#24104F" opacity=".45" transform="translate(1 3)" filter="{cv.blur(3)}"/>'
    g += f'<path d="{grin}" fill="{mouth}"/><g clip-path="{gc}">{mouth_inner}</g>'
    g += f'<path d="{grin}" fill="none" stroke="#24104F" stroke-width="2.4" stroke-linejoin="round"/>'
    # smile creases curling up at the corners
    g += (f'<path d="M{f(gl - 2)} {f(gy - 6)}q-10 -6 -8 -18M{f(gr_ + 2)} {f(gy - 10)}q10 -6 8 -18" stroke="#24104F" '
          f'stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    # nose
    g += (f'<path d="M{f(hx - 9)} {f(hy + 4)}Q{f(hx)} {f(hy)} {f(hx + 9)} {f(hy + 4)}Q{f(hx + 6)} {f(hy + 12)} {f(hx)} '
          f'{f(hy + 14)}Q{f(hx - 6)} {f(hy + 12)} {f(hx - 9)} {f(hy + 4)}Z" fill="{cv.rad(hx - 2, hy + 4, 10, [(0, "#FFB8D4"), (1, "#C2457A")])}"/>'
          f'<ellipse cx="{hx - 3}" cy="{hy + 4}" rx="3" ry="1.5" fill="#fff" opacity=".85"/>')
    # whiskers
    wk = ""
    for sgn in (-1, 1):
        for k in range(3):
            x0, y0 = hx + sgn * 24, hy + 14 + k * 5
            wk += f"M{f(x0)} {f(y0)}Q{f(x0 + sgn * 50)} {f(y0 - 16 + k * 4)} {f(x0 + sgn * 100)} {f(y0 - 22 + k * 14)}"
    g += (f'<path d="{wk}" stroke="#24104F" stroke-width="1.2" fill="none" opacity=".5"/>'
          f'<path d="{wk}" stroke="#fff" stroke-width=".7" fill="none" opacity=".85" transform="translate(-.5 -.8)"/>')
    return g
