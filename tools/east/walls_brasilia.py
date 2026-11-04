# SPDX-License-Identifier: GPL-2.0-or-later
"""brasilia (place): Niemeyer's Brasilia abstracted from its own geometry. The Cathedral is drawn as
what it is, a hyperboloid of one sheet: sixteen hyperbolic concrete columns (x = R r(u) sin t,
r(u) = sqrt(w^2 + k^2 (u - u0)^2)) leaning to a waist and opening into the crown, glazed between,
standing on the mirror pool; behind it the Esplanada in haze: the twin slabs of the Congress joined by
their bridges, the Senate bowl turned up and the Chamber bowl turned down on the long low base.
Flowing cloud ribbons run down the sky to the cathedral (the vein); the plaza falls to the viewer on
lines that meet at the horizon."""
import math
import random

import calculus as K
from geom import f, smooth
from walls_lib import palette, lin, rad, along_light, blurf, sky, mist, birds
from walls_juzhe import OPT, grp, ridge, stars, streak, water_lines, glade, reflect


def wave(doc, fr, colour, hair, x0, x1, y0, amp, thick, phase, opacity, tilt=0.0):
    """A sky ribbon: a wave band thick in the middle and tapering to both ends, with hairlines."""
    n = 28
    top, bot = [], []
    for i in range(n + 1):
        u = i / n
        x = x0 + (x1 - x0) * u
        y = y0 + tilt * (u - 0.5) + amp * math.sin(2 * math.pi * (u * 1.15 + phase))
        w = thick * math.sin(math.pi * u) ** 0.8
        top.append((x, y - w / 2))
        bot.append((x, y + w / 2))
    d = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + f"L{f(bot[-1][0])} {f(bot[-1][1])}" + smooth(bot[::-1]) + "Z"
    hl = "".join(f"M{f(top[0][0])} {f(top[0][1] + (bot[0][1] - top[0][1]) * k / 4)}" + smooth([(t[0], t[1] + (b[1] - t[1]) * k / 4) for t, b in zip(top, bot)]) for k in (1, 2, 3))
    doc.add(f'<path d="{d}" fill="{colour}" opacity="{f(opacity)}"/><path d="{hl}" fill="none" stroke="{hair}" stroke-width="{f(max(1.5, fr.s * 2.5))}" opacity="{f(opacity * 0.5)}"/>')


def cathedral(doc, fr, Q, cx, base_y, hc, rb, night):
    """Sixteen hyperbolic columns, glass between, the crown ring open to the sky, the base ring."""
    u0, w = 0.55, 0.42
    k = math.sqrt(1 - w * w) / u0

    def r(u):
        return math.sqrt(w * w + k * k * (u - u0) ** 2)

    def col(theta, n=46):
        return [(cx + rb * r(1.15 * i / n) * math.sin(theta), base_y - hc * 1.15 * i / n) for i in range(n + 1)]

    def col_glass(theta, n=40):
        return [(cx + rb * r(i / n) * math.sin(theta), base_y - hc * i / n) for i in range(n + 1)]

    cols = [2 * math.pi * i / 16 + math.pi / 16 for i in range(16)]
    back = sorted([t for t in cols if math.cos(t) < 0], key=lambda t: math.cos(t))
    front = sorted([t for t in cols if math.cos(t) >= 0], key=lambda t: -math.cos(t))
    rt = r(1.0) * rb
    rtip = r(1.15) * rb
    # the hull silhouette (extreme columns at +-90 deg): glass
    left = [(cx - rb * r(i / 40), base_y - hc * i / 40) for i in range(41)]
    right = [(cx + rb * r(i / 40), base_y - hc * i / 40) for i in range(41)]
    hull = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in left + right[::-1]) + "Z"
    # base ring and pedestal
    ped = fr.l(34)
    doc.add(f'<ellipse cx="{f(cx)}" cy="{f(base_y)}" rx="{f(rb * 1.18)}" ry="{f(rb * 0.2)}" fill="{lin(doc, [(0, Q["plaster"], 1), (1, Q["plaster2"], 1)], (cx - rb, base_y), (cx + rb, base_y))}"/>'
            f'<ellipse cx="{f(cx)}" cy="{f(base_y - ped * 0.3)}" rx="{f(rb * 1.05)}" ry="{f(rb * 0.16)}" fill="{Q["plaster2"]}" opacity="0.8"/>')
    # inside the crown: the back of the ring, the sky seen through it
    doc.add(f'<ellipse cx="{f(cx)}" cy="{f(base_y - hc)}" rx="{f(rt)}" ry="{f(rt * 0.16)}" fill="{Q["glass"]}"/>')
    sh = lin(doc, [(0, Q["plaster"], 1), (0.55, Q["plaster2"], 1), (1, Q["wall"], 1)], (cx - rb, 0), (cx + rb, 0))
    bw = max(3, fr.l(11))
    for t in back:
        d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in col(t))
        doc.add(f'<path d="{d}" fill="none" stroke="{Q["plaster2"]}" stroke-opacity="0.55" stroke-width="{f(bw)}" stroke-linecap="round"/>')
    # glass between: a lit interior at night, a pale reflective pane by day
    if night:
        g = rad(doc, [(0, Q["lightc"], 0.95), (0.35, Q["gold"], 0.9), (1, Q["gold"], 0.35)], (cx, base_y - hc * 0.18), hc * 0.8)
        doc.add(f'<path d="{hull}" fill="{g}"/>')
    else:
        doc.add(f'<path d="{hull}" fill="{lin(doc, [(0, Q["sky1"], 0.55), (1, Q["fog"], 0.75)], (0, base_y - hc), (0, base_y))}"/>')
    for t in front:
        c = math.cos(t)
        d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in col(t))
        doc.add(f'<path d="{d}" fill="none" stroke="{sh}" stroke-width="{f(bw * (1.1 + 0.6 * c))}" stroke-linecap="round"/>')
        d2 = "M" + " L".join(f"{f(x - bw * 0.25)} {f(y)}" for x, y in col(t))
        doc.add(f'<path d="{d2}" fill="none" stroke="{Q["lit"]}" stroke-opacity="0.45" stroke-width="{f(max(1.5, bw * 0.25))}"/>')
    # the crown: the front half of the ring, a coloured shade under it
    top_y = base_y - hc
    doc.add(f'<path d="M{f(cx - rt)} {f(top_y)}A{f(rt)} {f(rt * 0.16)} 0 0 0 {f(cx + rt)} {f(top_y)}" fill="none" stroke="{Q["plaster"]}" stroke-width="{f(bw * 1.4)}"/>'
            f'<path d="M{f(cx - rt)} {f(top_y)}A{f(rt)} {f(rt * 0.16)} 0 0 1 {f(cx + rt)} {f(top_y)}" fill="none" stroke="{Q["plaster2"]}" stroke-width="{f(bw * 0.9)}" opacity="0.8"/>')
    # the waist ring, where the columns lean closest
    wy = base_y - hc * u0
    doc.add(f'<path d="M{f(cx - rb * w)} {f(wy)}A{f(rb * w)} {f(rb * w * 0.12)} 0 0 0 {f(cx + rb * w)} {f(wy)}" fill="none" stroke="{Q["lit"]}" stroke-opacity="0.5" stroke-width="{f(bw * 0.6)}"/>')


def congress(doc, fr, Q, x, y, s):
    """The Congress in haze: two slabs with their bridges, the Senate bowl up and the Chamber bowl down."""
    tw, th = 0.34 * s, 1.5 * s
    for dx in (-0.5, 0.5):
        xx = x + dx * tw * 1.8
        doc.add(f'<rect x="{f(xx - tw / 2)}" y="{f(y - th)}" width="{f(tw)}" height="{f(th)}" fill="{lin(doc, [(0, Q["plaster"], 1), (1, Q["plaster2"], 1)], (xx - tw / 2, 0), (xx + tw / 2, 0))}"/>')
        fl = "".join(f"M{f(xx - tw / 2)} {f(y - th + th * k / 26)}h{f(tw)}" for k in range(1, 26))
        doc.add(f'<path d="{fl}" stroke="{Q["shade"]}" stroke-opacity="0.35" stroke-width="{f(max(1, s * 0.012))}" fill="none"/>')
    for hh in (0.55, 0.8):
        doc.add(f'<rect x="{f(x - tw * 0.9)}" y="{f(y - th * hh)}" width="{f(tw * 1.8)}" height="{f(s * 0.07)}" fill="{Q["plaster2"]}"/>')
    base_w = 5.5 * s
    doc.add(f'<rect x="{f(x - base_w / 2)}" y="{f(y - 0.14 * s)}" width="{f(base_w)}" height="{f(0.14 * s)}" fill="{Q["plaster2"]}"/>')
    r = 1.05 * s
    doc.add(f'<path d="M{f(x - base_w * 0.46)} {f(y - 0.14 * s)}A{f(r)} {f(r * 0.5)} 0 0 1 {f(x - base_w * 0.46 + 2 * r)} {f(y - 0.14 * s)}Z" fill="{lin(doc, [(0, Q["plaster"], 1), (1, Q["plaster2"], 1)], (x - base_w * 0.46, 0), (x - base_w * 0.46 + 2 * r, 0))}"/>')
    bx = x + base_w * 0.46 - 2 * r
    doc.add(f'<path d="M{f(bx)} {f(y - 0.14 * s)}H{f(bx + 2 * r)}A{f(r)} {f(r * 0.5)} 0 0 1 {f(bx)} {f(y - 0.14 * s)}Z" fill="{Q["plaster2"]}"/>'
            f'<path d="M{f(bx)} {f(y - 0.14 * s)}H{f(bx + 2 * r)}" stroke="{Q["lit"]}" stroke-width="{f(max(1.5, s * 0.02))}"/>')


def form_brasilia(doc, fr, P):
    W, H = fr.w, fr.h
    name = P["_name"]
    night = name == "night"
    Pf, _ = palette(name, 0.55)
    Pm, _ = palette(name, 0.0)
    y_h = 0.60 * H
    y_w = 0.775 * H
    light = (fr.x(0.17), fr.y(0.16), fr.l(76))
    sky(doc, fr, P, light)
    if night:
        stars(doc, fr, P, 5, 130)
    gl = rad(doc, [(0, P["lightc"], 0.5), (0.3, P["lightc"], 0.14), (1, P["lightc"], 0)], (light[0], light[1]), light[2] * 7)
    doc.add(f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2] * 7)}" fill="{gl}"/>'
            f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2])}" fill="{P["lightc"] if night else P["gold"]}"/>')
    # flowing ribbons: the sky runs down to the cathedral
    wave(doc, fr, P["cloud"], P["cloudline"], -0.05 * W, 1.05 * W, 0.20 * H, 0.04 * H, 0.10 * H, 0.0, 0.6, tilt=0.12 * H)
    wave(doc, fr, P["cloud2"], P["cloudline"], 0.08 * W, 1.0 * W, 0.31 * H, 0.03 * H, 0.07 * H, 0.3, 0.5, tilt=0.16 * H)
    wave(doc, fr, P["cloud"], P["cloudline"], -0.05 * W, 0.8 * W, 0.08 * H, 0.025 * H, 0.05 * H, 0.6, 0.75, tilt=0.06 * H)
    wave(doc, fr, P["cloud2"], P["cloudline"], 0.35 * W, 1.05 * W, 0.44 * H, 0.02 * H, 0.05 * H, 0.1, 0.45, tilt=0.07 * H)
    # the cerrado: low far hills with haze at the horizon
    ridge(doc, fr, P["ridge1"], P["fog"], P["ridge2"], P["lit"], [(0.1, 0.55), (0.33, 0.52), (0.6, 0.545), (0.85, 0.51), (1.0, 0.54)], 0.62, -0.05, 1.06, 5, contours=5, gap=14)
    congress(doc, fr, palette(name, 0.25)[0], 0.40 * W, 0.612 * H, fr.l(230))
    mist(doc, fr, P, 0.60, 0.05, opacity=0.8, seed=2)
    # the plaza: paving falling to the viewer, lines meeting at the horizon
    edge = [(-0.05 * W, y_h + 0.004 * H), (0.2 * W, y_h - 0.003 * H), (0.45 * W, y_h + 0.005 * H), (0.7 * W, y_h - 0.004 * H), (1.05 * W, y_h + 0.003 * H)]
    plaza = f"M{f(edge[0][0])} {f(edge[0][1])}" + smooth(edge) + f"L{W * 1.05} {H * 1.05}L{-0.05 * W} {H * 1.05}Z"
    doc.add(f'<path d="{plaza}" fill="{lin(doc, [(0, P["fog"], 1), (0.25, P["plaster"], 1), (1, P["plaster2"], 1)], (0, y_h), (0, H))}"/>')
    vp = (0.5 * W, y_h)
    for xa, xb, xc in ((-0.7, -0.05, 0.12), (1.05, 1.7, 0.88)):
        d = f"M{f(vp[0])} {f(vp[1])}L{f(xa * W)} {f(H * 1.05)}L{f(xb * W)} {f(H * 1.05)}Z"
        doc.add(f'<path d="{d}" fill="{lin(doc, [(0, P["fog"], 0.0), (0.35, P["leaf"], 0.3), (1, P["leaf2"], 0.4)], (0, y_h), (0, H))}"/>')
    rays = "".join(f"M{f(vp[0] + (x - 0.5) * 0.06 * W)} {f(vp[1])}L{f(x * W)} {f(H * 1.05)}" for x in [-1.6 + 0.26 * i for i in range(20)])
    doc.add(f'<path d="{rays}" stroke="{P["shade"]}" stroke-opacity="0.10" stroke-width="{f(max(1.5, fr.s * 2))}" fill="none"/>')
    cross = "".join(f"M0 {f(y_h + (H - y_h) * (k / 9) ** 2.2)}H{W}" for k in range(1, 9))
    doc.add(f'<path d="{cross}" stroke="{P["shade"]}" stroke-opacity="0.07" stroke-width="{f(max(1.5, fr.s * 2))}" fill="none"/>')
    # the mirror pool, a long oval opening to the right
    pool = f"M{0.50 * W} {y_w + 0.012 * H}" + smooth([(0.50 * W, y_w + 0.012 * H), (0.60 * W, y_w - 0.004 * H), (0.80 * W, y_w - 0.01 * H), (1.06 * W, y_w - 0.004 * H)]) + f"L{1.06 * W} {1.06 * H}L{0.40 * W} {1.06 * H}Q{0.38 * W} {0.9 * H} {0.50 * W} {y_w + 0.012 * H}Z"
    pc = doc.id("pcl")
    doc.defs.append(f'<clipPath id="{pc}"><path d="{pool}"/></clipPath>')
    doc.add(f'<path d="{pool}" fill="{lin(doc, [(0, P["fog"], 1), (0.3, P["water"], 1), (1, P["water2"], 1)], *along_light(fr, 0.2 * W, y_w, 1.1 * W, H))}"/>')
    doc.add(f'<g clip-path="url(#{pc})">')
    water_lines(doc, fr, P, y_w, 4)
    doc.add("</g>")
    cx_c, hc, rb = fr.x(0.655), fr.l(1010), fr.l(300)
    with grp(doc, "land"):
        # baptistery dome and bell tower beside the cathedral
        dx = cx_c - rb * 2.35
        doc.add(f'<path d="M{f(dx - rb * 0.62)} {f(y_w)}A{f(rb * 0.62)} {f(rb * 0.36)} 0 0 1 {f(dx + rb * 0.62)} {f(y_w)}Z" fill="{lin(doc, [(0, Pm["plaster"], 1), (1, Pm["plaster2"], 1)], (dx - rb * 0.6, 0), (dx + rb * 0.6, 0))}"/>')
        bx = cx_c - rb * 1.55
        doc.add(f'<path d="M{f(bx - fr.l(26))} {f(y_w)}L{f(bx - fr.l(12))} {f(y_w - hc * 0.55)}L{f(bx + fr.l(12))} {f(y_w - hc * 0.55)}L{f(bx + fr.l(26))} {f(y_w)}Z" fill="{lin(doc, [(0, Pm["plaster"], 1), (1, Pm["plaster2"], 1)], (bx - fr.l(26), 0), (bx + fr.l(26), 0))}"/>'
                f'<path d="M{f(bx)} {f(y_w - hc * 0.55)}v{f(-fr.l(70))}" stroke="{Pm["plaster2"]}" stroke-width="{f(fr.l(8))}"/>')
        cathedral(doc, fr, Pm, cx_c, y_w, hc, rb, night)
    reflect(doc, fr, P, "land", y_w, H - y_w, 3)
    doc.add('<use xlink:href="#land"/>')
    mist(doc, fr, P, 0.74, 0.04, x0=0.3, x1=1.0, opacity=0.35, seed=9)
    birds(doc, fr, P, [(0.10 * W, 0.34 * H), (0.20 * W, 0.28 * H), (0.30 * W, 0.30 * H), (0.38 * W, 0.37 * H)], 9, 4, role="line2")
    # the near plane: a Niemeyer curve sweeping in from the lower left, one white arc, lit on its upper edge
    arc = [(-0.03 * W, 0.965 * H), (0.07 * W, 0.955 * H), (0.15 * W, 0.98 * H), (0.2 * W, 1.03 * H)]
    d = f"M{f(arc[0][0])} {f(arc[0][1])}" + smooth(arc) + f"L{f(-0.03 * W)} {f(1.03 * H)}Z"
    doc.add(f'<path d="{d}" fill="{lin(doc, [(0, P["plaster2"], 1), (1, P["plaster2"], 1)], *along_light(fr, 0, 0.9 * H, 0.3 * W, H))}"/>'
            f'<path d="M{f(arc[0][0])} {f(arc[0][1])}{smooth(arc)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.l(6))}" opacity="0.25"/>')
