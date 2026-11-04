# SPDX-License-Identifier: GPL-2.0-or-later
"""rioniteroi (place): the Rio-Niteroi bridge abstracted as one long arc across Guanabara Bay. The
deck is a box girder on piers at equal spacing (the rhythm), rising into the steel span over the
channel where the girder deepens and a lattice of diagonals appears; it curves away to the light at
the upper left, where the Sugarloaf stands in haze with its cable-car line. The water takes the sky;
the piers mirror in it; sails and a ship scale the bay."""
import math
import random

import calculus as K
from geom import f, smooth
from walls_lib import palette, lin, rad, along_light, blurf, sky, mist, birds, resample
from walls_juzhe import OPT, grp, stars, streak, water_lines, ridge, glade
from walls_track import Track


def hf(z, zh=62.0, zw=24.7, base=7.0, rise=6.5):
    """Deck height above the water at depth z: a long rise to the steel span, a gentle fall after."""
    return base + rise * math.exp(-((z - zh) / zw) ** 2)


def form_rioniteroi(doc, fr, P):
    W, H = fr.w, fr.h
    name = P["_name"]
    night = name == "night"
    Pf, _ = palette(name, 0.6)
    Pn, _ = palette(name, 0.3)
    Pm, _ = palette(name, 0.0)
    ctrl = [(1.30 * W, 0.98 * H), (0.95 * W, 0.84 * H), (0.60 * W, 0.74 * H), (0.46 * W, 0.56 * H), (0.235 * W, 0.46 * H)]
    Z0 = 4.7
    T = Track(ctrl, unit=0.03 * W, z0=Z0, lat=(0.30, -0.10))
    V = ctrl[-1]
    light = (fr.x(0.15), fr.y(0.14), fr.l(72))
    sky(doc, fr, P, light)
    if night:
        stars(doc, fr, P, 5, 110)
    gl = rad(doc, [(0, P["lightc"], 0.5), (0.3, P["lightc"], 0.14), (1, P["lightc"], 0)], (light[0], light[1]), light[2] * 7)
    doc.add(f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2] * 7)}" fill="{gl}"/>'
            f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2])}" fill="{P["lightc"] if night else P["gold"]}"/>')
    streak(doc, fr, P["cloud"], P["cloudline"], 0.34 * W, 0.09 * H, fr.l(900), fr.l(44), 0.8, up=fr.l(14))
    streak(doc, fr, P["cloud2"], P["cloudline"], 0.68 * W, 0.16 * H, fr.l(700), fr.l(34), 0.7, up=fr.l(10))
    # the bay takes the sky; the far shore: hills of Rio and the Sugarloaf at the vanishing point
    y_h = V[1] + 0.012 * H
    doc.add(f'<rect x="0" y="{f(y_h)}" width="{W}" height="{f(H - y_h)}" fill="{lin(doc, [(0, P["fog"], 1), (0.25, P["water"], 1), (1, P["water2"], 1)], *along_light(fr, -0.2 * W, y_h, 1.2 * W, H))}"/>')
    ridge(doc, fr, P["ridge1"], P["fog"], P["ridge2"], P["lit"], [(0.05, 0.40), (0.14, 0.37), (0.3, 0.42), (0.62, 0.44), (0.9, 0.41)], y_h / H + 0.002, -0.05, 1.06, 3, contours=6, gap=14)
    sx, sy = 0.205 * W, y_h
    sl = f"M{f(sx - 0.05 * W)} {f(sy)}C{f(sx - 0.045 * W)} {f(sy - 0.07 * H)} {f(sx - 0.02 * W)} {f(sy - 0.16 * H)} {f(sx + 0.005 * W)} {f(sy - 0.162 * H)}C{f(sx + 0.03 * W)} {f(sy - 0.16 * H)} {f(sx + 0.045 * W)} {f(sy - 0.08 * H)} {f(sx + 0.05 * W)} {f(sy)}Z"
    doc.add(f'<path d="{sl}" fill="{lin(doc, [(0, Pf["ridge4"], 1), (1, Pf["fog"], 1)], (0, sy - 0.16 * H), (0, sy))}"/>')
    hx, hy = 0.15 * W, y_h - 0.115 * H
    doc.add(f'<path d="M{f(hx)} {f(hy)}L{f(sx - 0.002 * W)} {f(sy - 0.158 * H)}" stroke="{Pf["lit"]}" stroke-width="{f(fr.l(3))}" opacity="0.8"/>')
    mist(doc, fr, P, 0.43, 0.06, opacity=0.8, seed=2)
    water_lines(doc, fr, P, y_h + 0.02 * H, 4)
    # the bridge: piers every 9 units, girder as a ribbon whose height follows hf(z)
    zs = [Z0 * (1.012 ** i) for i in range(0, 520)]
    zs = [z for z in zs if z < 380]
    deckL = [T.pt(z, -5.0, hf(z)) for z in zs]
    deckR = [T.pt(z, 5.0, hf(z)) for z in zs]
    gird = 1.3
    underL = [T.pt(z, -5.0, hf(z) - gird * (1 + 1.6 * math.exp(-((z - 62) / 26) ** 2))) for z in zs]
    underR = [T.pt(z, 5.0, hf(z) - gird * (1 + 1.6 * math.exp(-((z - 62) / 26) ** 2))) for z in zs]
    def poly_pts(a, b):
        return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in a + b[::-1]) + "Z"
    # piers: far to near
    pz = [Z0 + 9.0 * i for i in range(0, 42)]
    for z in pz[::-1]:
        t = T.t_of(z)
        Pb = palette(name, min(0.85, t * 1.1))[0]
        k = T.U * T.s(t)
        h = hf(z) - gird
        for v in (-2.6, 2.6):
            x0, y0 = T.pt(z, v, 0.0)
            x1, y1 = T.pt(z, v, h)
            w = max(2, 0.9 * k)
            doc.add(f'<path d="M{f(x0 - w * 0.7)} {f(y0)}L{f(x1 - w * 0.5)} {f(y1)}L{f(x1 + w * 0.5)} {f(y1)}L{f(x0 + w * 0.7)} {f(y0)}Z" fill="{Pb["plaster2"]}"/>'
                    f'<path d="M{f(x0 - w * 0.7)} {f(y0)}L{f(x1 - w * 0.5)} {f(y1)}L{f(x1 - w * 0.1)} {f(y1)}L{f(x0 - w * 0.1)} {f(y0)}Z" fill="{Pb["plaster"]}"/>')
        xa, ya = T.pt(z, -3.6, h)
        xb, yb = T.pt(z, 3.6, h)
        doc.add(f'<path d="M{f(xa)} {f(ya)}L{f(xb)} {f(yb)}" stroke="{Pb["plaster2"]}" stroke-width="{f(max(2, 1.2 * k))}" stroke-linecap="round"/>')
    # girder underside (shade) and the side face (lit upper left), then the deck surface and rails
    side = lin(doc, [(0, Pm["plaster"], 1), (1, P["fog"], 1)], (0.8 * W, H), (0.25 * W, 0.45 * H))
    doc.add(f'<path d="{poly_pts(deckL, underL)}" fill="{side}"/>')
    doc.add(f'<path d="{poly_pts(deckR, underR)}" fill="{Pm["plaster2"]}" opacity="0.9"/>')
    deck = lin(doc, [(0, Pm["roofb"], 1), (0.7, Pn["roofa"], 1), (1, P["fog"], 1)], (0.8 * W, H), (0.25 * W, 0.45 * H))
    doc.add(f'<path d="{poly_pts(deckL, deckR)}" fill="{deck}"/>')
    # lane lines and edge lines
    for v, col, op, w in ((-4.7, "lit", 0.6, 0.12), (4.7, "lit", 0.6, 0.12), (0.0, "gold", 0.8, 0.14), (-2.4, "lit", 0.35, 0.08), (3.0, "lit", 0.35, 0.08)):
        pts = [T.pt(z, v, hf(z)) for z in zs]
        dash = "stroke-dasharray=\"6 14\"" if v in (-2.4, 3.0) else ""
        doc.add(f'<path d="M{" L".join(f"{f(x)} {f(y)}" for x, y in pts)}" fill="none" stroke="{P[col]}" stroke-opacity="{op}" stroke-width="{f(fr.l(5 if v == 0 else 4))}" {dash}/>')
    # the steel span: a lattice of diagonals on the girder side face
    diag = []
    zsp = [34 + 3.0 * i for i in range(0, 20)]
    for i, z in enumerate(zsp[:-1]):
        a = T.pt(z, -5.0, hf(z))
        b = T.pt(zsp[i + 1], -5.0, hf(zsp[i + 1]) - gird * 2.4)
        c = T.pt(z, -5.0, hf(z) - gird * 2.4)
        d = T.pt(zsp[i + 1], -5.0, hf(zsp[i + 1]))
        diag.append(f"M{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}M{f(c[0])} {f(c[1])}L{f(d[0])} {f(d[1])}")
    doc.add(f'<path d="{"".join(diag)}" fill="none" stroke="{Pm["lit"]}" stroke-opacity="0.55" stroke-width="{f(fr.l(4))}"/>')
    # lamp posts along the rail, lit at night
    for z in [Z0 + 4.7 * i for i in range(0, 60)][::-1]:
        t = T.t_of(z)
        k = T.U * T.s(t)
        x0, y0 = T.pt(z, -5.0, hf(z))
        x1, y1 = T.pt(z, -5.0, hf(z) + 4.2)
        doc.add(f'<path d="M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}" stroke="{P["plaster2"]}" stroke-width="{f(max(1.5, 0.16 * k))}"/>')
        if night:
            doc.add(f'<circle cx="{f(x1)}" cy="{f(y1)}" r="{f(max(3, 0.9 * k))}" fill="{rad(doc, [(0, P["gold"], 0.9), (1, P["gold"], 0)], (x1, y1), max(3, 0.9 * k))}"/>')
    # reflections of the piers in the bay, short and broken
    refl = []
    for z in pz:
        t = T.t_of(z)
        k = T.U * T.s(t)
        for v in (-2.6, 2.6):
            x0, y0 = T.pt(z, v, 0.0)
            refl.append(f'<rect x="{f(x0 - 0.5 * k)}" y="{f(y0)}" width="{f(k)}" height="{f(3.5 * k)}" opacity="0.18"/>')
    doc.add(f'<g fill="{P["plaster2"]}">{"".join(refl)}</g>')
    # sails and a ship to give the bay scale
    for (sx_, sy_, s_) in ((0.50, 0.74, 1.0), (0.58, 0.69, 0.7), (0.34, 0.66, 0.45)):
        x, y, u = sx_ * W, sy_ * H, fr.l(95) * s_
        doc.add(f'<path d="M{f(x)} {f(y - u * 1.6)}L{f(x)} {f(y)}L{f(x + u * 0.7)} {f(y)}Z" fill="{P["plaster"]}"/>'
                f'<path d="M{f(x - u * 0.12)} {f(y - u * 1.2)}L{f(x - u * 0.12)} {f(y)}L{f(x - u * 0.6)} {f(y)}Z" fill="{P["lit"]}" opacity="0.9"/>'
                f'<path d="M{f(x - u * 0.7)} {f(y)}H{f(x + u * 0.8)}L{f(x + u * 0.6)} {f(y + u * 0.18)}H{f(x - u * 0.5)}Z" fill="{P["roofb"]}"/>')
    birds(doc, fr, P, [(0.34 * W, 0.17 * H), (0.46 * W, 0.12 * H), (0.56 * W, 0.17 * H)], 8, 4, role="line2")
    if night:
        glade(doc, fr, P, light[0], y_h + 0.03 * H, 4)
