# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""Shared parts: eyes, brass, sparkles."""
import math
import random
from kit import f, path, sample, volume, band, sparkle, KEY

BRASS = [(0, "#FFF4C9"), (0.28, "#F2C766"), (0.6, "#C98F2C"), (1, "#7A4E12")]


def crescent(cx, cy, rx, ry, a0, a1, w, rot=0, n=24, out=1.0, taper=True):
    """Tapered stroke along an elliptical arc (angles in degrees, 0 = right, 90 = down)."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def pt(a, k):
        x, y = rx * k * math.cos(math.radians(a)), ry * k * math.sin(math.radians(a))
        return (cx + x * c - y * s, cy + x * s + y * c)
    o, i = [], []
    for j in range(n + 1):
        u = j / n
        a = a0 + (a1 - a0) * u
        t = math.sin(math.pi * u) ** 0.6 if taper else 1
        o.append(pt(a, out + w * t / max(rx, ry) * 0.5))
        i.append(pt(a, out - w * t / max(rx, ry) * 0.5))
    pts = o + i[::-1]
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in pts) + "Z"


def eye(cv, cx, cy, rx, ry, look=(0, 0), rot=0, iris_k=0.66, pupil_k=0.46, lid=0.0,
        palette=("#12082A", "#3E1F9C", "#7C5CFF", "#D8C8FF"), lash="#24123F", lashes=2, socket=True, lidfill="#fff"):
    """A big, wet, Pixar-ish eye. look in -1..1 of the free space; lid 0..1 closes the top."""
    rr = math.radians(rot)
    t = f"rotate({f(rot)} {f(cx)} {f(cy)})"
    sd = f"M{f(cx - rx)} {f(cy)}a{f(rx)} {f(ry)} 0 1 0 {f(2 * rx)} 0a{f(rx)} {f(ry)} 0 1 0 {f(-2 * rx)} 0Z"
    clip = cv.clip(sd, t)
    g = ""
    if socket:   # soft socket: the eye sits in the face
        g += (f'<ellipse cx="{f(cx + 1)}" cy="{f(cy + 2)}" rx="{f(rx * 1.22)}" ry="{f(ry * 1.18)}" fill="#8E7BC8" '
              f'opacity=".28" transform="{t}" filter="{cv.blur(rx * .14)}"/>')
    sclera = cv.ell_rad(cx, cy, rx, ry, rot, [(0, "#FFFFFF"), (0.7, "#F6F2FF"), (1, "#C9BEEA")], -0.25, -0.1)
    g += f'<path d="{sd}" fill="{sclera}" transform="{t}"/>'
    ir = min(rx, ry) * iris_k * 1.08
    ix = cx + look[0] * (rx - ir) * 0.85
    iy = cy + look[1] * (ry - ir) * 0.85
    d0, d1, d2, d3 = palette
    iris = cv.rad(ix, iy + ir * 0.15, ir, [(0, d2), (0.55, d1), (0.86, d0), (1, d0)], ix, iy + ir * 0.55)
    inner = f'<circle cx="{f(ix)}" cy="{f(iy)}" r="{f(ir)}" fill="{iris}"/>'
    # iris fibres
    rnd = random.Random(int(cx * 7 + cy))
    fib = ""
    for k in range(40):
        a = 2 * math.pi * k / 40 + rnd.uniform(-.05, .05)
        r0, r1 = ir * 0.42, ir * rnd.uniform(0.75, 0.95)
        fib += f"M{f(ix + math.cos(a) * r0)} {f(iy + math.sin(a) * r0)}L{f(ix + math.cos(a) * r1)} {f(iy + math.sin(a) * r1)}"
    inner += f'<path d="{fib}" stroke="{d3}" stroke-width="{f(max(ir * .035, .5))}" opacity=".35" fill="none"/>'
    # lower glow in the iris (light passing through the lens)
    inner += (f'<ellipse cx="{f(ix + ir * .1)}" cy="{f(iy + ir * .5)}" rx="{f(ir * .62)}" ry="{f(ir * .34)}" fill="{d3}" '
              f'opacity=".55" filter="{cv.blur(ir * .12)}"/>')
    inner += f'<circle cx="{f(ix)}" cy="{f(iy)}" r="{f(ir * pupil_k)}" fill="#0A0418"/>'
    inner += (f'<circle cx="{f(ix)}" cy="{f(iy)}" r="{f(ir)}" fill="none" stroke="{d0}" stroke-width="{f(ir * .09)}" '
              f'opacity=".85"/>')
    # upper-lid shadow on the eyeball
    inner += band(cv, sd, [(cx - rx, cy - ry), (cx + rx, cy + ry)], (0, -1), ry * 0.22, ry * 0.12, "#5A4796", .42)
    if lid > 0:
        ly = cy - ry + 2 * ry * lid
        inner += (f'<path d="M{f(cx - rx * 1.3)} {f(cy - ry * 1.4)}H{f(cx + rx * 1.3)}V{f(ly)}'
                  f'Q{f(cx)} {f(ly + ry * .25)} {f(cx - rx * 1.3)} {f(ly)}Z" fill="{lidfill}"/>')
    # catchlights: key light top-left, bounce bottom-right
    inner += (f'<ellipse cx="{f(ix - ir * .36)}" cy="{f(iy - ir * .4)}" rx="{f(ir * .3)}" ry="{f(ir * .26)}" '
              f'fill="#fff" transform="rotate(-25 {f(ix - ir * .36)} {f(iy - ir * .4)})"/>')
    inner += f'<circle cx="{f(ix + ir * .05)}" cy="{f(iy - ir * .62)}" r="{f(ir * .085)}" fill="#fff" opacity=".9"/>'
    inner += f'<circle cx="{f(ix + ir * .42)}" cy="{f(iy + ir * .38)}" r="{f(ir * .12)}" fill="#fff" opacity=".75"/>'
    # wet sheen across the sclera
    inner += (f'<ellipse cx="{f(cx - rx * .35)}" cy="{f(cy - ry * .45)}" rx="{f(rx * .38)}" ry="{f(ry * .16)}" fill="#fff" '
              f'opacity=".35" transform="rotate(-30 {f(cx - rx * .35)} {f(cy - ry * .45)})" filter="{cv.blur(1.2)}"/>')
    g += f'<g clip-path="{clip}">{inner}</g>'
    # lash line + lower lid hint
    g += f'<path d="{crescent(cx, cy, rx, ry, 188, 352, max(rx * .16, 1.4), rot)}" fill="{lash}"/>'
    g += f'<path d="{crescent(cx, cy, rx, ry, 30, 150, max(rx * .05, .6), rot, out=1.02)}" fill="{lash}" opacity=".35"/>'
    # lashes at the outer corner
    side = 1 if look[0] >= 0 else 1
    for k in range(lashes):
        a = math.radians(-20 - k * 22) if side > 0 else math.radians(200 + k * 22)
        a2 = math.radians(-20 - k * 22)
        bx, by = cx + rx * math.cos(a2), cy + ry * math.sin(a2)
        c, s = math.cos(rr), math.sin(rr)
        x0, y0 = cx + (bx - cx) * c - (by - cy) * s, cy + (bx - cx) * s + (by - cy) * c
        L = rx * (0.42 - k * 0.08)
        ang = a2 + rr - 0.35
        x1, y1 = x0 + math.cos(ang) * L, y0 + math.sin(ang) * L
        xm, ym = x0 + math.cos(ang + .5) * L * .55, y0 + math.sin(ang + .5) * L * .55
        g += (f'<path d="M{f(x0 - 1.4)} {f(y0 + .6)}Q{f(xm)} {f(ym)} {f(x1)} {f(y1)}Q{f(xm + 1)} {f(ym + 2)} '
              f'{f(x0 + 1.6)} {f(y0 + 2.2)}Z" fill="{lash}"/>')
    return g


def glow(cv, x, y, r, color, op=1.0):
    g = cv.rad(x, y, r, [(0, color, op), (0.35, color, op * .45), (1, color, 0)])
    return f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{g}"/>'


def motes(cv, box, n, seed, color="#fff", rmax=6, op=(0.4, 1)):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    out = ""
    for _ in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        r = rnd.uniform(1.5, rmax)
        o = rnd.uniform(*op)
        if r > rmax * .6:
            out += glow(cv, x, y, r * 2.2, color, o * .5) + sparkle(x, y, r, color, o, rnd.choice([0, 0, 45]))
        else:
            out += f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r * .45)}" fill="{color}" opacity="{o:.2f}"/>'
    return out


def ground(cv, cx, cy, rx, ry, op=.28, color="#2A1A55"):
    g = cv.ell_rad(cx, cy, rx, ry, 0, [(0, color, op), (0.5, color, op * .55), (1, color, 0)])
    g2 = cv.ell_rad(cx, cy, rx * .45, ry * .5, 0, [(0, color, op * 1.2), (1, color, 0)])
    return (f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{g}"/>'
            f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx * .45)}" ry="{f(ry * .5)}" fill="{g2}"/>')


BRASS_SPIN = ["#FFF4CC", "#E2A94A", "#8A5A16", "#D9A040", "#FFE7A3", "#B57C22", "#6B4410", "#E8B04B"]


def scallop(cx, cy, R, a, n, steps=320):
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        r = R - a + a * abs(math.cos(n * t / 2)) ** .55
        pts.append(f"{f(cx + r * math.cos(t))} {f(cy + r * math.sin(t))}")
    return "M" + "L".join(pts) + "Z"


def conic(cx, cy, R, cols, n=120, phase=0):
    """Anisotropic polished-metal sheen: a conic gradient made of thin wedges."""
    def mix(c1, c2, u):
        a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
        b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
        return "#" + "".join(f"{round(x + (y - x) * u):02X}" for x, y in zip(a, b))
    out = ""
    m = len(cols)
    for i in range(n):
        u = i / n * m
        c = mix(cols[int(u) % m], cols[(int(u) + 1) % m], u - int(u))
        a0 = math.radians(i / n * 360 - .4 + phase)
        a1 = math.radians((i + 1) / n * 360 + .4 + phase)
        out += (f'<path d="M{f(cx)} {f(cy)}L{f(cx + R * math.cos(a0))} {f(cy + R * math.sin(a0))}'
                f'L{f(cx + R * math.cos(a1))} {f(cy + R * math.sin(a1))}Z" fill="{c}"/>')
    return out


def cubic_pts(segs, step=1.0):
    """Points every `step` units along a list of cubic segments [(p0, c1, c2, p3), ...]."""
    out = []
    for p0, c1, c2, p3 in segs:
        n = 400
        prev = None
        acc = step
        for i in range(n + 1):
            u = i / n
            a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
            x = a * p0[0] + b * c1[0] + c * c2[0] + d * p3[0]
            y = a * p0[1] + b * c1[1] + c * c2[1] + d * p3[1]
            if prev:
                acc += math.hypot(x - prev[0], y - prev[1])
            if acc >= step:
                out.append((x, y))
                acc = 0
            prev = (x, y)
    return out


def chain_links(cv, segs, link=9.0, w=3.2):
    """A real curb chain: links alternate face-on (rings) and edge-on (bars), each turned to the curve."""
    pts = cubic_pts(segs, link * .78)
    sh, body, hi = "", "", ""
    for i in range(1, len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i - 1], pts[i + 1]
        x, y = pts[i]
        a = math.degrees(math.atan2(y1 - y0, x1 - x0))
        if i % 2:
            ring = (f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="{f(link * .55)}" ry="{f(link * .34)}" '
                    f'transform="rotate({f(a)} {f(x)} {f(y)})"/>')
            sh += ring
            body += ring
            hi += (f'<path d="M{f(x - link * .4)} {f(y - link * .12)}Q{f(x)} {f(y - link * .38)} {f(x + link * .3)} '
                   f'{f(y - link * .2)}" transform="rotate({f(a)} {f(x)} {f(y)})"/>')
        else:
            bar = (f'<path d="M{f(x - link * .5)} {f(y)}H{f(x + link * .5)}" transform="rotate({f(a)} {f(x)} {f(y)})"/>')
            sh += bar
            body += bar.replace("<path", '<path class="b"')
    return (f'<g fill="none" stroke="#2A1A05" stroke-width="{f(w + 1)}" opacity=".35" transform="translate(2 4)" '
            f'filter="{cv.blur(1.8)}" stroke-linecap="round">{sh}</g>'
            f'<g fill="none" stroke="{cv.lin(0, 0, 512, 512, [(0, "#FFE7A3"), (0.35, "#C98F2C"), (0.7, "#F2C766"), (1, "#8A5A16")])}" '
            f'stroke-width="{f(w)}" stroke-linecap="round">{body}</g>'
            f'<g fill="none" stroke="#7A4E12" stroke-width="{f(w * .35)}" opacity=".5" transform="translate(.6 .9)">{body}</g>'
            f'<g fill="none" stroke="#FFF8DC" stroke-width="{f(w * .35)}" stroke-linecap="round" opacity=".9">{hi}</g>')
