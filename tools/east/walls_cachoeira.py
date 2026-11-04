# SPDX-License-Identifier: GPL-2.0-or-later
"""cachoeira (place): the station of Cachoeira Paulista abstracted as a light-filled railway
perspective. A curved track runs from the lower right to the light at the upper left (the entry);
beside it the platform with its canopy colonnade and arcaded facade recedes in rhythm (the landing is
the lit near bay, lower right); on the other side catenary masts carry their wire along the same
curve. Rails, sleepers, columns, arches and masts all converge on one vanishing point, so the plan
reads as a station before it reads as art. Flat planes, translucent light ribbons, geometric texture."""
import math
import random

import calculus as K
from geom import f, smooth, juzhe
from walls_lib import palette, lin, rad, along_light, blurf, sky, mist, birds, resample, pl
from walls_juzhe import OPT, ridge, streak, stars
from walls_track import Track


def band(P, name, t):
    """Atmospheric bucket: the palette walked toward the fog by depth."""
    return palette(name, min(0.85, t * 1.1))[0]


def form_cachoeira(doc, fr, P):
    W, H = fr.w, fr.h
    name = P["_name"]
    night = name == "night"
    ctrl = [(0.66 * W, 1.18 * H), (0.80 * W, 0.84 * H), (0.22 * W, 0.80 * H), (0.58 * W, 0.50 * H), (0.255 * W, 0.405 * H)]
    Z0 = 6.0
    ZN = Z0
    T = Track(ctrl, unit=0.034 * W, z0=Z0)
    V = ctrl[-1]
    # lightsource and sky
    light = (fr.x(0.17), fr.y(0.15), fr.l(70))
    sky(doc, fr, P, light)
    if night:
        stars(doc, fr, P, 5, 110)
    gl = rad(doc, [(0, P["lightc"], 0.5), (0.3, P["lightc"], 0.15), (1, P["lightc"], 0)], (light[0], light[1]), light[2] * 7)
    doc.add(f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2] * 7)}" fill="{gl}"/>'
            f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2])}" fill="{P["lightc"]}"/>')
    streak(doc, fr, P["cloud"], P["cloudline"], 0.36 * W, 0.09 * H, fr.l(900), fr.l(44), 0.8, up=fr.l(14))
    streak(doc, fr, P["cloud2"], P["cloudline"], 0.66 * W, 0.15 * H, fr.l(700), fr.l(34), 0.7, up=fr.l(10))
    # the ground: a meadow falling to the viewer, furrows following the track
    Pg = band(P, name, 0.0)
    gnd = f"M{-0.05 * W} {0.425 * H}L{W * 1.05} {0.425 * H}L{W * 1.05} {H * 1.05}L{-0.05 * W} {H * 1.05}Z"
    doc.add(f'<path d="{gnd}" fill="{lin(doc, [(0, P["fog"], 1), (0.18, P["hill"], 1), (1, P["hill2"], 1)], (0, 0.425 * H), (0, H))}"/>')
    # the hills of the valley, three distances, lost in haze at the vanishing point
    ridge(doc, fr, P["ridge1"], P["fog"], P["ridge2"], P["lit"], [(0.12, 0.30), (0.34, 0.27), (0.58, 0.31), (0.82, 0.25), (0.98, 0.30)], 0.43, -0.05, 1.06, 5, contours=7)
    mist(doc, fr, P, 0.36, 0.07, opacity=0.55, seed=2)
    mist(doc, fr, P, 0.415, 0.05, opacity=0.9, seed=6)
    ridge(doc, fr, P["ridge3"], P["fog"], P["ridge4"], P["lit"], [(0.05, 0.36), (0.30, 0.355), (0.52, 0.37), (0.78, 0.34), (1.0, 0.37)], 0.47, -0.05, 1.06, 9, contours=6)
    strips = [(-46, -30, "hill2", 0.0), (-30, -21, "hill", 0.0), (-21, -15, "leaf", 0.55), (-15, -10.5, "hill2", 0.0), (-10.5, -7.2, "leaflit", 0.5), (-7.2, -5.0, "hill", 0.0)]
    for v0, v1, role, op in strips:
        col = P[role]
        g = lin(doc, [(0, col, 1 if op == 0 else op), (1, P["fog"], 0.0 if op else 1)], (0, H), (0, 0.42 * H))
        doc.add(f'<path d="{T.poly(ZN, 500, v0, v1)}" fill="{g}"/>')
        doc.add(f'<path d="{T.line(ZN, 500, v1, 0.0, 40)}" fill="none" stroke="{P["lit"]}" stroke-opacity="0.35" stroke-width="{f(fr.l(4))}"/>')
        fur = "".join(T.line(ZN, 500, v0 + (v1 - v0) * k / 7, 0.0, 40) for k in range(1, 7))
        doc.add(f'<path d="{fur}" fill="none" stroke="{P["shade"] if op == 0 else P["leaf2"]}" stroke-opacity="0.14" stroke-width="{f(fr.l(3))}"/>')
    # ballast and the light that runs along the rails
    doc.add(f'<path d="{T.poly(ZN, 400, -2.9, 2.9)}" fill="{lin(doc, [(0, P["block2"], 1), (0.6, P["joint"], 1), (1, P["fog"], 1)], (0, H), (0, 0.42 * H))}"/>')
    rnd = random.Random(3)
    dots = []
    for _ in range(520):
        z = Z0 * (60 ** rnd.random() ** 0.6)
        v = rnd.uniform(-2.7, 2.7)
        x, y = T.pt(z, v)
        dots.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(max(1.2, T.U * T.s(T.t_of(z)) * 0.07))}"/>')
    doc.add(f'<g fill="{P["joint"]}" opacity="0.5">{"".join(dots)}</g>')
    # sleepers: far to near
    sl = []
    z = ZN
    zs = []
    while z < 260:
        zs.append(z)
        z += 0.62
    for z in zs[::-1]:
        t = T.t_of(z)
        a, b = T.pt(z, -1.35), T.pt(z, 1.35)
        c, d = T.pt(z + 0.26, 1.35), T.pt(z + 0.26, -1.35)
        sl.append((t, "M" + " L".join(f"{f(x)} {f(y)}" for x, y in (a, b, c, d)) + "Z"))
    for lo, hi, col in ((0.0, 0.5, "bark"), (0.5, 0.8, "bark"), (0.8, 1.0, "bark")):
        Pb = band(P, name, (lo + hi) / 2)
        doc.add(f'<path d="{"".join(d for t, d in sl if lo <= t < hi)}" fill="{Pb[col]}"/>')
    # rails: web, head highlight, and the glow trail that follows them
    for v in (-0.72, 0.72):
        doc.add(f'<path d="{T.poly(ZN, 400, v - 0.1, v + 0.1, 0.0, 0.0)}" fill="{P["block"]}"/>'
                f'<path d="{T.poly(ZN, 400, v - 0.085, v + 0.085, 0.16, 0.16)}" fill="{P["lit"]}" opacity="0.85"/>')
    for v, op, w in ((-0.72, 0.5, 0.22), (0.72, 0.5, 0.22)):
        g = lin(doc, [(0, P["gold"] if night else P["lightc"], op), (1, P["lightc"], 0)], (0, H), (0, 0.41 * H))
        doc.add(f'<path d="{T.poly(ZN, 400, v - w, v + w, 0.0, 0.0)}" fill="{g}" filter="{blurf(doc, fr.l(10))}"/>')
    # catenary masts on the left with the wire hung along the curve
    zm = [6 * (1.55 ** i) for i in range(10)]
    masts = []
    wires_a, wires_b = [], []
    for i, z in enumerate(zm):
        Pb = band(P, name, T.t_of(z))
        k = T.U * T.s(T.t_of(z))
        x0, y0 = T.pt(z, -4.4, 0.0)
        x1, y1 = T.pt(z, -4.4, 7.4)
        w = max(2, 0.22 * k)
        doc.add(f'<path d="M{f(x0 - w / 2)} {f(y0)}L{f(x1 - w * 0.3)} {f(y1)}L{f(x1 + w * 0.3)} {f(y1)}L{f(x0 + w / 2)} {f(y0)}Z" fill="{Pb["block"]}"/>')
        ax, ay = T.pt(z, -2.2, 7.0)
        doc.add(f'<path d="M{f(x1)} {f(y1 + 0.5 * k)}L{f(ax)} {f(ay)}" stroke="{Pb["block"]}" stroke-width="{f(max(1.5, 0.12 * k))}"/>')
        wires_a.append((ax, ay))
        wires_b.append((x1, y1))
    for pts in (wires_a, wires_b):
        d = "M" + " ".join(f"{f(x)} {f(y)}" if i == 0 else f"Q{f((pts[i - 1][0] + x) / 2)} {f((pts[i - 1][1] + y) / 2 + 14)} {f(x)} {f(y)}" for i, (x, y) in enumerate(pts[::-1]))
        doc.add(f'<path d="{d}" fill="none" stroke="{P["lit"]}" stroke-opacity="0.55" stroke-width="{f(fr.l(4))}"/>')
    # platform, then the station building along it: an arcade of round arches between pilasters
    ph = 0.9
    VB = 7.2                                    # the building's front, lateral
    doc.add(f'<path d="{T.poly(ZN, 400, 2.9, 2.9, 0.0, ph)}" fill="none"/>')
    edge = T.ribbon(ZN, 400, 2.9, 2.9, 0.0, ph)
    doc.add(f'<path d="M{" L".join(f"{f(x)} {f(y)}" for x, y in edge[0] + edge[1][::-1])}Z" fill="{lin(doc, [(0, P["ground2"], 1), (1, P["fog"], 1)], (0, H), (0, 0.42 * H))}"/>')
    surf = lin(doc, [(0, P["plaster"], 1), (1, P["fog"], 1)], (0.5 * W, H), (0.3 * W, 0.45 * H))
    doc.add(f'<path d="{T.poly(ZN, 400, 2.9, VB, ph, ph)}" fill="{surf}"/>')
    doc.add(f'<path d="{T.poly(ZN, 400, 3.25, 3.55, ph, ph)}" fill="{P["gold"]}" opacity="0.9"/>')
    joints = []
    for i in range(1, 70):
        z = Z0 + 3.0 * i
        a_, b_ = T.pt(z, 3.7, ph), T.pt(z, VB, ph)
        joints.append(f"M{f(a_[0])} {f(a_[1])}L{f(b_[0])} {f(b_[1])}")
    doc.add(f'<path d="{"".join(joints)}" fill="none" stroke="{P["shade"]}" stroke-opacity="0.22" stroke-width="{f(fr.l(3))}"/>')
    bh = 4.6                                    # wall height under the cornice
    wall = T.poly(ZN, 400, VB, VB, ph, ph + bh)
    doc.add(f'<path d="{wall}" fill="{lin(doc, [(0, P["plaster2"], 1), (1, P["fog"], 1)], (0.6 * W, H), (0.3 * W, 0.4 * H))}"/>')
    pil = []
    for i in range(80, -1, -1):
        zc = Z0 + 3.0 * i + 1.5
        t = T.t_of(zc)
        Pb = band(P, name, t)
        wz, wh = 1.5, 3.0
        arc = [(zc + wz * 0.5 * math.cos(math.pi * (1 - j / 14)), ph + 1.0 + wh - wz * 0.5 + wz * 0.5 * math.sin(math.pi * (1 - j / 14))) for j in range(15)]
        outline = [(zc - wz / 2, ph + 1.0)] + arc + [(zc + wz / 2, ph + 1.0)]
        d = "M" + " L".join(f"{f(T.pt(zz, VB, hh)[0])} {f(T.pt(zz, VB, hh)[1])}" for zz, hh in outline) + "Z"
        lit = night and i % 3 != 1
        doc.add(f'<path d="{d}" fill="{Pb["pane"] if lit else Pb["glass"]}"/>')
        # the arch moulding: a lit rim on the upper left, as a stroke along the curve
        rim = "M" + " L".join(f"{f(T.pt(zz, VB, hh)[0])} {f(T.pt(zz, VB, hh)[1])}" for zz, hh in arc)
        doc.add(f'<path d="{rim}" fill="none" stroke="{Pb["lit"]}" stroke-opacity="0.7" stroke-width="{f(max(1.5, 0.1 * T.U * T.s(t)))}"/>')
        # pilaster between this bay and the next
        zp = zc + 1.5
        a_, b_ = T.pt(zp, VB, ph), T.pt(zp, VB, ph + bh)
        k = T.U * T.s(T.t_of(zp))
        w = max(2, 0.34 * k)
        doc.add(f'<path d="M{f(a_[0] - w / 2)} {f(a_[1])}L{f(b_[0] - w / 2)} {f(b_[1])}L{f(b_[0] + w / 2)} {f(b_[1])}L{f(a_[0] + w / 2)} {f(a_[1])}Z" fill="{Pb["block2"]}" opacity="0.8"/>')
        if night and lit:
            lx, ly = T.pt(zc, VB - 0.6, ph + 0.2)
            doc.add(f'<ellipse cx="{f(lx)}" cy="{f(ly)}" rx="{f(1.2 * k)}" ry="{f(0.35 * k)}" fill="{P["gold"]}" opacity="0.28" filter="{blurf(doc, max(2, 0.2 * k))}"/>')
    # cornice, roof and the clock tower
    doc.add(f'<path d="{T.poly(ZN, 400, VB - 0.2, VB + 0.2, ph + bh, ph + bh + 0.3)}" fill="{P["ridge2"]}"/>')
    doc.add(f'<path d="{T.poly(ZN, 400, VB, VB + 2.2, ph + bh + 0.3, ph + bh + 1.3)}" fill="{lin(doc, [(0, P["ridge4"], 1), (0.55, P["ridge3"], 1), (1, P["fog"], 1)], (0.7 * W, 0.45 * H), (0.3 * W, 0.4 * H))}"/>')
    rb = "".join(f"M{f(T.pt(z, VB, ph + bh + 0.35)[0])} {f(T.pt(z, VB, ph + bh + 0.35)[1])}L{f(T.pt(z, VB + 2.2, ph + bh + 1.3)[0])} {f(T.pt(z, VB + 2.2, ph + bh + 1.3)[1])}" for z in [Z0 + 0.8 * i for i in range(220)])
    doc.add(f'<path d="{rb}" fill="none" stroke="{P["roofc"]}" stroke-opacity="0.35" stroke-width="{f(fr.l(3))}"/>')
    # the tower: a shaft above the roofline with a clock and a pyramid roof
    z0t, z1t, th = Z0 + 3.0 * 17, Z0 + 3.0 * 17 + 5.0, 13.0
    Pt = band(P, name, T.t_of(z0t))
    tw = T.poly(z0t, z1t, VB - 0.2, VB - 0.2, ph, ph + th, 4)
    doc.add(f'<path d="{tw}" fill="{lin(doc, [(0, Pt["plaster"], 1), (1, Pt["plaster2"], 1)], (T.pt(z0t, VB, ph)[0], 0), (T.pt(z1t, VB, ph)[0], 0))}"/>')
    side = f"M{f(T.pt(z0t, VB - 0.2, ph)[0])} {f(T.pt(z0t, VB - 0.2, ph)[1])}L{f(T.pt(z0t, VB + 2.4, ph)[0])} {f(T.pt(z0t, VB + 2.4, ph)[1])}L{f(T.pt(z0t, VB + 2.4, ph + th)[0])} {f(T.pt(z0t, VB + 2.4, ph + th)[1])}L{f(T.pt(z0t, VB - 0.2, ph + th)[0])} {f(T.pt(z0t, VB - 0.2, ph + th)[1])}Z"
    doc.add(f'<path d="{side}" fill="{Pt["plaster2"]}"/>')
    ap = T.pt((z0t + z1t) / 2, VB + 1.1, ph + th + 3.6)
    ca, cb = T.pt(z0t, VB - 0.2, ph + th), T.pt(z1t, VB - 0.2, ph + th)
    cc, cd = T.pt(z0t, VB + 2.4, ph + th), T.pt(z1t, VB + 2.4, ph + th)
    doc.add(f'<path d="M{f(ca[0])} {f(ca[1])}L{f(cb[0])} {f(cb[1])}L{f(ap[0])} {f(ap[1])}Z" fill="{Pt["roofa"]}"/>'
            f'<path d="M{f(ca[0])} {f(ca[1])}L{f(cc[0])} {f(cc[1])}L{f(ap[0])} {f(ap[1])}Z" fill="{Pt["roofb"]}"/>')
    kc = T.U * T.s(T.t_of(z0t))
    cx_, cy_ = T.pt((z0t + z1t) / 2, VB - 0.2, ph + th - 2.6)
    doc.add(f'<ellipse cx="{f(cx_)}" cy="{f(cy_)}" rx="{f(1.1 * kc * 0.55)}" ry="{f(1.1 * kc)}" fill="{Pt["lit"]}"/>'
            f'<ellipse cx="{f(cx_)}" cy="{f(cy_)}" rx="{f(0.9 * kc * 0.55)}" ry="{f(0.9 * kc)}" fill="{Pt["pane"] if night else Pt["plaster"]}"/>'
            f'<path d="M{f(cx_)} {f(cy_)}v{f(-0.7 * kc)}M{f(cx_)} {f(cy_)}l{f(0.3 * kc)} {f(0.18 * kc)}" stroke="{Pt["block"]}" stroke-width="{f(max(2, 0.07 * kc))}" stroke-linecap="round"/>')
    # the vanishing light: the entry
    doc.add(f'<circle cx="{f(V[0])}" cy="{f(V[1])}" r="{f(0.16 * W)}" fill="{rad(doc, [(0, P["lightc"], 0.5), (0.4, P["lightc"], 0.14), (1, P["lightc"], 0)], V, 0.16 * W)}"/>')
    doc.add(f'<path d="M{f(V[0] - 3)} {f(V[1])}h6" stroke="{P["lightc"]}"/>')
