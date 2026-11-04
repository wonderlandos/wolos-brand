# SPDX-License-Identifier: GPL-2.0-or-later
"""estaiada (place): the Octavio Frias de Oliveira cable-stayed bridge (Sao Paulo) abstracted from its
geometry: a single concrete mast shaped as an X, two curved decks that cross at it, and two fans of
stay cables running from the mast arms to the decks on both sides. Cables are straight lines at equal
steps, so the fans moire into sails; the river mirrors mast and cables; the skyline of the Marginal
stands in haze behind, lit windows at night, and a long exposure of the traffic runs along the deck."""
import math
import random

import calculus as K
from geom import f, smooth
from walls_lib import palette, lin, rad, along_light, blurf, sky, mist, birds
from walls_juzhe import OPT, grp, stars, streak, water, water_lines, glade, reflect, ridge


def skyline(doc, fr, Q, y_base, seed, x0=0.0, x1=1.0, night=False):
    """Towers of the Marginal in haze: slabs of varied height, lit-window grids at night."""
    rnd = random.Random(seed)
    W, H = fr.w, fr.h
    x = x0 * W
    out, win = [], []
    while x < x1 * W:
        w = rnd.uniform(0.012, 0.03) * W
        h = rnd.choice([0.05, 0.08, 0.12, 0.16, 0.22]) * H * rnd.uniform(0.8, 1.2)
        out.append(f'<rect x="{f(x)}" y="{f(y_base - h)}" width="{f(w)}" height="{f(h + 4)}"/>')
        if night:
            for r_ in range(int(h / fr.l(30))):
                for c_ in range(int(w / fr.l(22))):
                    if rnd.random() < 0.28:
                        win.append(f'<rect x="{f(x + fr.l(8) + c_ * fr.l(22))}" y="{f(y_base - h + fr.l(10) + r_ * fr.l(30))}" width="{f(fr.l(10))}" height="{f(fr.l(14))}"/>')
        x += w + rnd.uniform(0.002, 0.012) * W
    doc.add(f'<g fill="{lin(doc, [(0, Q["ridge3"], 1), (1, Q["fog"], 1)], (0, y_base - 0.22 * H), (0, y_base))}">{"".join(out)}</g>')
    if win:
        doc.add(f'<g fill="{Q["pane"]}" opacity="0.7">{"".join(win)}</g>')


def leg(doc, fr, Q, p0, p1, w0, w1, bend, lit_first):
    """One leg of the mast: a tapering curved column, two faces (lit left, shade right), form-work joints."""
    n = 30
    pts = []
    for i in range(n + 1):
        u = i / n
        x = p0[0] + (p1[0] - p0[0]) * u + bend * math.sin(math.pi * u)
        y = p0[1] + (p1[1] - p0[1]) * u
        pts.append((x, y, w0 + (w1 - w0) * u))
    L = [(x - w / 2, y) for x, y, w in pts]
    R = [(x + w / 2, y) for x, y, w in pts]
    M = [(x, y) for x, y, w in pts]
    lit = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in L + M[::-1]) + "Z"
    shd = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in M + R[::-1]) + "Z"
    doc.add(f'<path d="{lit}" fill="{Q["plaster"] if lit_first else Q["lit"]}"/><path d="{shd}" fill="{Q["plaster2"]}"/>')
    joints = "".join(f"M{f(L[i][0])} {f(L[i][1])}L{f(R[i][0])} {f(R[i][1])}" for i in range(2, n, 2))
    doc.add(f'<path d="{joints}" stroke="{Q["shade"]}" stroke-opacity="0.22" stroke-width="{f(max(1.5, fr.s * 2))}" fill="none"/>')
    return pts


def form_estaiada(doc, fr, P):
    W, H = fr.w, fr.h
    name = P["_name"]
    night = name == "night"
    Pf, _ = palette(name, 0.6)
    Pn, _ = palette(name, 0.3)
    Pm, _ = palette(name, 0.0)
    y_w = 0.78 * H
    light = (fr.x(0.17), fr.y(0.15), fr.l(72))
    sky(doc, fr, P, light)
    if night:
        stars(doc, fr, P, 5, 90)
    gl = rad(doc, [(0, P["lightc"], 0.5), (0.3, P["lightc"], 0.14), (1, P["lightc"], 0)], (light[0], light[1]), light[2] * 7)
    doc.add(f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2] * 7)}" fill="{gl}"/>'
            f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2])}" fill="{P["lightc"] if night else P["gold"]}"/>')
    streak(doc, fr, P["cloud"], P["cloudline"], 0.30 * W, 0.10 * H, fr.l(900), fr.l(44), 0.8, up=fr.l(14))
    streak(doc, fr, P["cloud2"], P["cloudline"], 0.62 * W, 0.045 * H, fr.l(700), fr.l(34), 0.75, up=fr.l(10))
    water(doc, fr, P, 0.56 * H, y_w)
    skyline(doc, fr, Pf, 0.62 * H, 4, 0.0, 1.0, night)
    ridge(doc, fr, P["ridge2"], P["fog"], P["ridge3"], P["lit"], [(0.12, 0.56), (0.40, 0.545), (0.74, 0.56)], 0.65, -0.05, 1.06, 2, contours=4, gap=14)
    skyline(doc, fr, Pn, 0.66 * H, 9, 0.02, 0.45, night)
    mist(doc, fr, P, 0.60, 0.07, opacity=0.8, seed=2)
    water_lines(doc, fr, P, y_w, 4)
    xm, ytop, ydk = 0.64 * W, 0.13 * H, 0.665 * H          # mast axis, mast top, deck level at the mast
    dx = 0.05 * W
    with grp(doc, "land"):
        # the back deck: the other roadway, farther, crossing
        back = [(-0.05 * W, 0.70 * H), (0.25 * W, 0.725 * H), (xm - 0.1 * W, 0.70 * H), (xm + 0.12 * W, 0.675 * H), (1.05 * W, 0.70 * H)]
        d_top = f"M{f(back[0][0])} {f(back[0][1])}" + smooth(back)
        d_poly = d_top + "L" + " L".join(f"{f(x)} {f(y + 0.016 * H)}" for x, y in back[::-1]) + "Z"
        doc.add(f'<path d="{d_poly}" fill="{Pn["plaster2"]}"/><path d="{d_top}" fill="none" stroke="{Pn["lit"]}" stroke-width="{f(fr.l(5))}" opacity="0.6"/>')
        # mast: two legs crossing; the right leg behind, the left leg in front
        base_y = ydk + 0.05 * H
        dxt = 0.036 * W
        Lm = dict(Pm)
        if not night:
            Lm["plaster"], Lm["plaster2"], Lm["lit"] = Pm["plaster2"], Pm["roofa"], Pm["plaster"]
        leg(doc, fr, Lm, (xm + dx, base_y), (xm - dxt, ytop), fr.l(78), fr.l(46), 0.0, False)
        leg(doc, fr, Lm, (xm - dx, base_y), (xm + dxt, ytop), fr.l(78), fr.l(46), 0.0, True)
        # cable fans: anchors along the two arms above the crossing, deck points at equal steps
        cross_y = base_y - (base_y - ytop) * dx / (dx + dxt)
        lines_r, lines_l, lines_b = [], [], []
        n = 22
        for i in range(n):
            u = i / (n - 1)
            ay = ytop + (cross_y - ytop - 0.03 * H) * (0.03 + 0.94 * u)
            # right fan from the upper-right arm, left fan from the upper-left arm
            axr = xm - dx + (base_y - ay) / (base_y - ytop) * (dx + dxt)
            axl = xm + dx - (base_y - ay) / (base_y - ytop) * (dx + dxt)
            xr_end = xm + 0.075 * W + (0.36 * W) * (u ** 1.1)
            xl_end = xm - 0.075 * W - (0.54 * W) * (u ** 1.1)
            yd_r = 0.665 * H + (xr_end - xm) / W * 0.09 * H
            yd_l = 0.665 * H + (xm - xl_end) / W * 0.055 * H
            lines_r.append(f"M{f(axr)} {f(ay)}L{f(xr_end)} {f(yd_r)}")
            lines_l.append(f"M{f(axl)} {f(ay)}L{f(xl_end)} {f(yd_l)}")
            lines_b.append(f"M{f(axr + 0.004 * W)} {f(ay + fr.l(10))}L{f(xr_end + 0.006 * W)} {f(yd_r - 0.02 * H)}")
        doc.add(f'<path d="{"".join(lines_b)}" stroke="{Pn["lit"]}" stroke-opacity="0.35" stroke-width="{f(max(1.5, fr.s * 2))}" fill="none"/>')
        doc.add(f'<path d="{"".join(lines_r)}" stroke="{Pm["lit"]}" stroke-opacity="0.9" stroke-width="{f(max(2, fr.s * 3))}" fill="none"/>'
                f'<path d="{"".join(lines_l)}" stroke="{Pm["lit"]}" stroke-opacity="0.9" stroke-width="{f(max(2, fr.s * 3))}" fill="none"/>')
        # the front deck: curved, with a lit upper edge and a dark under-face; the traffic on it
        front = [(-0.05 * W, 0.735 * H), (0.22 * W, 0.70 * H), (xm - 0.08 * W, 0.672 * H), (xm + 0.1 * W, 0.668 * H), (0.9 * W, 0.70 * H), (1.05 * W, 0.745 * H)]
        top = f"M{f(front[0][0])} {f(front[0][1])}" + smooth(front)
        body = top + "L" + " L".join(f"{f(x)} {f(y + 0.02 * H)}" for x, y in front[::-1]) + "Z"
        cast = doc.id("fd")
        doc.defs.append(f'<clipPath id="{cast}"><path d="{body}"/></clipPath>')
        doc.add(f'<path d="{body}" fill="{lin(doc, [(0, Pm["plaster2"], 1), (1, Pm["roofb"], 1)], *along_light(fr, 0, 0.66 * H, W, 0.76 * H))}"/>'
                f'<path d="{top}" fill="none" stroke="{Pm["lit"]}" stroke-width="{f(fr.l(6))}" opacity="0.8"/>')
        under = "L" + " L".join(f"{f(x)} {f(y + 0.02 * H)}" for x, y in front[::-1])
        doc.add(f'<path d="{top}{under}Z" fill="none"/>')
        # piers under the deck into the river
        for px_ in (0.14 * W, 0.38 * W, 0.86 * W):
            yd = 0.70 * H + 0.02 * H
            doc.add(f'<rect x="{f(px_ - fr.l(18))}" y="{f(yd)}" width="{f(fr.l(36))}" height="{f(y_w - yd)}" fill="{Pn["plaster2"]}"/>')
        # the traffic: a long exposure along the deck
        tr_ = f"M{f(front[0][0])} {f(front[0][1] - fr.l(14))}" + smooth([(x, y - fr.l(14)) for x, y in front])
        doc.add(f'<path d="{tr_}" fill="none" stroke="{P["gold"]}" stroke-width="{f(fr.l(7))}" stroke-opacity="{0.9 if night else 0.35}" stroke-linecap="round"/>'
                f'<path d="{tr_}" fill="none" stroke="{P["cinnabar"]}" stroke-width="{f(fr.l(4))}" stroke-opacity="{0.8 if night else 0.25}" transform="translate(0 {fr.l(-14)})"/>')
    reflect(doc, fr, P, "land", y_w, H - y_w, 3)
    if night:
        glade(doc, fr, P, light[0], y_w + 0.012 * H, 4)
    doc.add('<use xlink:href="#land"/>')
    mist(doc, fr, P, 0.76, 0.04, opacity=0.35, seed=9)
    birds(doc, fr, P, [(0.10 * W, 0.34 * H), (0.20 * W, 0.28 * H), (0.30 * W, 0.30 * H), (0.38 * W, 0.37 * H)], 8, 4, role="line2")
    # near plane: the river bank at the lower left with reeds, low and dark
    arc = [(-0.03 * W, 0.95 * H), (0.06 * W, 0.935 * H), (0.14 * W, 0.965 * H), (0.19 * W, 1.03 * H)]
    doc.add(f'<path d="M{f(arc[0][0])} {f(arc[0][1])}{smooth(arc)}L{f(-0.03 * W)} {f(1.03 * H)}Z" fill="{lin(doc, [(0, Pm["roofb"], 1), (1, Pm["roofc"], 1)], *along_light(fr, 0, 0.93 * H, 0.2 * W, H))}"/>')
