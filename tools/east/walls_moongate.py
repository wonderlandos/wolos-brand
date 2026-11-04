# SPDX-License-Identifier: GPL-2.0-or-later
"""moongate (mature register): a lime-washed garden wall with a dragon-back coping, a round door and
two leak windows; through the door a lake, ridges in three distances and a far pagoda (the landing);
in front, stone paving; a bamboo clump and a plum limb at the entry whose shadows fall on the wall
(coloured, offset 1:2). Flat planes, geometric texture (voussoirs, tile courses, fret, slabs)."""
import math
import random

import calculus as K
from geom import f, smooth, circle, rrect
from walls_lib import (palette, lin, rad, along_light, blurf, cast, sky, bez, resample, pl, mist, birds, pagoda,
                       lattice, bamboo)
from walls_juzhe import (OPT, grp, ridge, stars, streak, plum, dian_tree, water, water_lines, glade, hall_m)


def fret_window(doc, fr, Q, x, y, w, h, lit):
    """A leak window (loutang): stone frame, a meander (huiwen) lattice, lit from behind at night."""
    s = max(12, round(h / 9 / K.U) * K.U)
    i = doc.id("mf")
    doc.defs.append(f'<pattern id="{i}" patternUnits="userSpaceOnUse" x="{f(x)}" y="{f(y)}" width="{f(s * 2)}" height="{f(s * 2)}">'
                    f'<path d="M0 {f(s * 1.8)}V{f(s * 0.2)}H{f(s * 1.4)}V{f(s * 1.4)}H{f(s * 0.6)}V{f(s * 0.8)}H{f(s * 1.0)}" fill="none" stroke="{Q["latbar"]}" stroke-width="{f(s * 0.2)}" stroke-linecap="square"/></pattern>')
    fw = max(8, round(h * 0.07 / K.U) * K.U)
    frame = rrect(x - fw, y - fw, w + 2 * fw, h + 2 * fw, fw * 0.5)
    cast(doc, frame, Q["shade"], fr, lift=0.8, opacity=0.35)
    doc.add(f'<path d="{frame}" fill="{lin(doc, [(0, Q["jointlit"], 1), (1, Q["ground2"], 1)], *along_light(fr, x, y, x + w, y + h))}"/>')
    doc.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{Q["pane"] if lit else Q["glass"]}"/>'
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="url(#{i})"/>'
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h * 0.12)}" fill="{Q["shade"]}" opacity="0.35"/>')


def octagon_window(doc, fr, Q, cx, cy, r, lit):
    """An octagonal leak window with a square-grid lattice (every other crossing dotted)."""
    pts = [(cx + r * math.cos(math.pi / 8 + k * math.pi / 4), cy + r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]
    d = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in pts) + "Z"
    fw = r * 0.16
    big = "M" + " L".join(f"{f(cx + (r + fw) * math.cos(math.pi / 8 + k * math.pi / 4))} {f(cy + (r + fw) * math.sin(math.pi / 8 + k * math.pi / 4))}" for k in range(8)) + "Z"
    cast(doc, big, Q["shade"], fr, lift=0.8, opacity=0.35)
    doc.add(f'<path d="{big}" fill="{lin(doc, [(0, Q["jointlit"], 1), (1, Q["ground2"], 1)], *along_light(fr, cx - r, cy - r, cx + r, cy + r))}"/>'
            f'<path d="{d}" fill="{Q["pane"] if lit else Q["glass"]}"/>')
    c = doc.id("oc")
    doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
    n = 6
    g = "".join(f"M{f(cx - r + (2 * r) * k / n)} {f(cy - r)}v{f(2 * r)}M{f(cx - r)} {f(cy - r + (2 * r) * k / n)}h{f(2 * r)}" for k in range(1, n))
    dots = "".join(f'<circle cx="{f(cx - r + 2 * r * a / n)}" cy="{f(cy - r + 2 * r * b / n)}" r="{f(r * 0.045)}"/>' for a in range(1, n) for b in range(1, n) if (a + b) % 2 == 0)
    doc.add(f'<g clip-path="url(#{c})"><path d="{g}" fill="none" stroke="{Q["latbar"]}" stroke-width="{f(r * 0.05)}"/><g fill="{Q["latbar"]}">{dots}</g></g>')


def view(doc, fr, P, Pf, cx, cy, R):
    """What the door shows: pale sky, three ridges, a far pagoda and hall, the lake, a tree at the rim."""
    W, H = fr.w, fr.h
    c = doc.id("vc")
    doc.defs.append(f'<clipPath id="{c}"><path d="{circle(cx, cy, R)}"/></clipPath>')
    doc.add(f'<g clip-path="url(#{c})">')
    doc.add(f'<rect x="{f(cx - R)}" y="{f(cy - R)}" width="{f(2 * R)}" height="{f(2 * R)}" fill="{lin(doc, [(0, P["sky1"], 1), (1, P["fog"], 1)], (0, cy - R), (0, cy + 0.1 * R))}"/>')
    hz = (cy + 0.1 * R) / H
    water(doc, fr, P, hz * H - 4, hz * H)
    gx = cx / W
    ridge(doc, fr, P["ridge1"], P["fog"], P["ridge2"], P["lit"], [(gx - 0.05, hz - 0.16), (gx + 0.03, hz - 0.20), (gx + 0.12, hz - 0.12)], hz, gx - 0.2, gx + 0.2, 4, contours=6, gap=20)
    pagoda(doc, fr, Pf, cx + 0.12 * R, (hz - 0.16) * H, 0.2 * R, role="ridge4")
    mist(doc, fr, P, hz - 0.07, 0.06, x0=gx - 0.2, x1=gx + 0.2, opacity=0.6, seed=3)
    ridge(doc, fr, P["ridge3"], P["fog"], P["ridge4"], P["lit"], [(gx - 0.1, hz - 0.07), (gx + 0.01, hz - 0.1)], hz + 0.006, gx - 0.2, gx + 0.2, 6, contours=5, gap=16)
    hall_m(doc, fr, Pf, cx - 0.35 * R, (hz - 0.002) * H, 0.45 * R, lit_pattern=(1, 0, 1), lamp=0.6, bays=5, detail=2.0)
    water_lines(doc, fr, P, hz * H, 8)
    glade(doc, fr, P, cx + 0.25 * R, hz * H + 0.01 * H, 5)
    dian_tree(doc, fr, palette(P["_name"], 0.0)[0], cx + 0.62 * R, cy + 0.78 * R, 0.62 * R, 11)
    if P["_name"] == "night":
        doc.add(f'<circle cx="{f(cx + 0.34 * R)}" cy="{f(cy - 0.5 * R)}" r="{f(0.075 * R)}" fill="{P["lightc"]}"/>')
        doc.add(f'<circle cx="{f(cx + 0.34 * R)}" cy="{f(cy - 0.5 * R)}" r="{f(0.4 * R)}" fill="{rad(doc, [(0, P["lightc"], 0.35), (1, P["lightc"], 0)], (cx + 0.34 * R, cy - 0.5 * R), 0.4 * R)}"/>')
    doc.add("</g>")


def form_moongate(doc, fr, P):
    W, H = fr.w, fr.h
    name = P["_name"]
    Pf, _ = palette(name, 0.45)
    Pm, _ = palette(name, 0.0)
    light = (fr.x(0.16), fr.y(0.1), fr.l(70))
    sky(doc, fr, P, light)
    if name == "night":
        stars(doc, fr, P, 7, 90)
    gl = rad(doc, [(0, P["lightc"], 0.4), (0.3, P["lightc"], 0.12), (1, P["lightc"], 0)], (light[0], light[1]), light[2] * 6)
    doc.add(f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2] * 6)}" fill="{gl}"/><circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2])}" fill="{P["lightc"]}"/>')
    streak(doc, fr, P["cloud"], P["cloudline"], 0.36 * W, 0.075 * H, fr.l(820), fr.l(40), 0.85, up=fr.l(14))
    streak(doc, fr, P["cloud2"], P["cloudline"], 0.70 * W, 0.045 * H, fr.l(640), fr.l(32), 0.8, up=fr.l(10))
    birds(doc, fr, P, [(0.5 * W, 0.12 * H), (0.58 * W, 0.09 * H), (0.67 * W, 0.12 * H), (0.74 * W, 0.17 * H)], 7, 4, role="line2")
    # the wall with its dragon-back top
    top = []
    nx = 14
    for i in range(nx + 1):
        x = -0.04 * W + 1.08 * W * i / nx
        y = 0.215 * H - 0.012 * H * (1 - i / nx) + 0.022 * H * math.sin(i / nx * 2 * math.pi * 2.2 + 0.6)
        top.append((x, y))
    wy_bot = 0.80 * H
    wall = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + f"L{f(top[-1][0])} {f(wy_bot)}L{f(top[0][0])} {f(wy_bot)}Z"
    cast(doc, wall, P["shade"], fr, lift=1.0, opacity=0.25)
    g0, g1 = along_light(fr, 0, 0.2 * H, W, wy_bot)
    doc.add(f'<path d="{wall}" fill="{lin(doc, [(0, P["plaster"], 1), (1, P["plaster2"], 1)], g0, g1)}"/>')
    c = doc.id("wc")
    doc.defs.append(f'<clipPath id="{c}"><path d="{wall}"/></clipPath>')
    # lime-wash strata and tile coping
    st = "".join(f"M0 {f(0.26 * H + i * fr.l(34))}H{W}" for i in range(int((wy_bot - 0.26 * H) / fr.l(34))))
    doc.add(f'<g clip-path="url(#{c})"><path d="{st}" fill="none" stroke="{P["shade"]}" stroke-width="{f(max(1.5, fr.s * 2))}" opacity="0.07"/></g>')
    cop = fr.l(92)
    tdn = [(x, y + cop) for x, y in top]
    coping = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + f"L{f(tdn[-1][0])} {f(tdn[-1][1])}" + smooth(tdn[::-1]) + "Z"
    cast(doc, coping, P["shade"], fr, lift=1.4, opacity=0.4)
    doc.add(f'<path d="{coping}" fill="{lin(doc, [(0, P["roofa"], 1), (1, P["roofc"], 1)], g0, g1)}"/>')
    ta, tb = resample(bez(top, 12), 150), resample(bez(tdn, 12), 150)
    rib = "".join(f"M{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}" for a, b in zip(ta, tb))
    c2 = doc.id("cc")
    doc.defs.append(f'<clipPath id="{c2}"><path d="{coping}"/></clipPath>')
    doc.add(f'<g clip-path="url(#{c2})" fill="none"><path d="{rib}" stroke="{P["lit"]}" stroke-opacity="0.3" stroke-width="{f(max(2, fr.s * 3))}"/>'
            f'<path d="{pl(ta)}" stroke="{P["lit"]}" stroke-opacity="0.55" stroke-width="{f(fr.l(8))}"/></g>')
    ends = resample(bez(tdn, 12), 120)
    r = fr.l(9)
    doc.add(f'<g fill="{P["roofb"]}">{"".join(f"<circle cx={chr(34)}{f(x)}{chr(34)} cy={chr(34)}{f(y)}{chr(34)} r={chr(34)}{f(r)}{chr(34)}/>" for x, y in ends[1:-1])}</g>')
    sh = pl(tdn) + " " + pl([(x, y + fr.l(70)) for x, y in tdn[::-1]]).replace("M", "L", 1) + "Z"
    doc.add(f'<g clip-path="url(#{c})"><path d="{sh}" fill="{lin(doc, [(0, P["shade"], 0.45), (1, P["shade"], 0)], (0, 0.3 * H), (0, 0.4 * H))}"/></g>')
    # stone footing of the wall
    foot = rrect(-0.02 * W, 0.755 * H, 1.04 * W, 0.045 * H, 0)
    doc.add(f'<path d="{foot}" fill="{lin(doc, [(0, P["jointlit"], 1), (1, P["ground2"], 1)], g0, g1)}"/>')
    # the door
    cx, cy, R = fr.x(0.62), fr.y(0.515), fr.l(520)
    view(doc, fr, P, Pf, cx, cy, R)
    ring = circle(cx, cy, R + fr.l(46)) + circle(cx, cy, R)
    cast(doc, circle(cx, cy, R + fr.l(46)), P["shade"], fr, lift=1.3, opacity=0.35)
    doc.add(f'<path d="{ring}" fill-rule="evenodd" fill="{lin(doc, [(0, P["jointlit"], 1), (1, P["ground2"], 1)], *along_light(fr, cx - R, cy - R, cx + R, cy + R))}"/>')
    vj = "".join(f"M{f(cx + R * math.cos(math.radians(a)))} {f(cy + R * math.sin(math.radians(a)))}L{f(cx + (R + fr.l(46)) * math.cos(math.radians(a)))} {f(cy + (R + fr.l(46)) * math.sin(math.radians(a)))}" for a in range(0, 360, 6))
    doc.add(f'<path d="{vj}" stroke="{P["joint"]}" stroke-width="{f(max(2, fr.s * 3))}" opacity="0.55" fill="none"/>'
            f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(R + fr.l(52))}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.l(6))}" opacity="0.5"/>')
    # the reveal: the wall's thickness shades the upper left inside the opening
    c3 = doc.id("rv")
    doc.defs.append(f'<clipPath id="{c3}"><path d="{circle(cx, cy, R)}"/></clipPath>')
    s = fr.l(46)
    doc.add(f'<g clip-path="url(#{c3})"><path d="{circle(cx, cy, R + 2) + circle(cx + s * 0.5, cy + s, R)}" fill-rule="evenodd" fill="{P["shade"]}" opacity="0.5"/></g>')
    # leak windows left of the door
    fret_window(doc, fr, Pm, fr.x(0.095), fr.y(0.40), fr.l(300), fr.l(300), name == "night")
    octagon_window(doc, fr, Pm, fr.x(0.315), fr.y(0.47), fr.l(160), name != "night")
    # the courtyard: paving courses, wider toward the viewer, joints staggered
    fy = 0.80 * H
    floor = rrect(-0.02 * W, fy, 1.04 * W, H - fy + 0.02 * H, 0)
    doc.add(f'<path d="{floor}" fill="{lin(doc, [(0, P["ground"], 1), (1, P["ground2"], 1)], *along_light(fr, 0, fy, W, H))}"/>')
    rows = [0.0, 0.045, 0.1, 0.17, 0.26, 0.2 + 0.25]
    ys = [fy + (H - fy) * t / 0.45 for t in (0, 0.07, 0.17, 0.33, 0.58, 1.0)]
    hj = "".join(f"M0 {f(y)}H{W}" for y in ys[1:-1])
    rnd = random.Random(9)
    vj2 = []
    for k in range(len(ys) - 1):
        sw = fr.l(140 + 120 * k)
        off = (k % 2) * sw / 2
        x = -off
        while x < W:
            vj2.append(f"M{f(x)} {f(ys[k])}V{f(ys[k + 1])}")
            x += sw
    doc.add(f'<path d="{hj}" stroke="{P["joint"]}" stroke-width="{f(fr.l(5))}" opacity="0.6" fill="none"/>'
            f'<path d="{"".join(vj2)}" stroke="{P["joint"]}" stroke-width="{f(fr.l(4))}" opacity="0.45" fill="none"/>'
            f'<path d="M0 {f(fy + fr.l(6))}H{W}" stroke="{P["lit"]}" stroke-width="{f(fr.l(5))}" opacity="0.5"/>')
    # the light of the door falls on the paving (night: gold; day: the sky)
    doc.add(f'<ellipse cx="{f(cx + R * 0.1)}" cy="{f(fy + fr.l(130))}" rx="{f(R * 0.9)}" ry="{f(fr.l(90))}" fill="{P["pane"] if name == "night" else P["lit"]}" opacity="0.28" filter="{blurf(doc, fr.l(40))}"/>')
    # bamboo at the entry and its shadow on the wall (coloured, offset 1:2)
    Ps = dict(Pm)
    for k in ("leaf", "leaf2", "leaflit"):
        Ps[k] = P["shade"]
    doc.add(f'<g opacity="0.28" filter="{blurf(doc, fr.l(7))}" clip-path="url(#{c})">')
    bamboo(doc, fr, Ps, 0.03 * W + fr.l(150), 0.84 * H, fr.l(1500), 6, n=7)
    doc.add("</g>")
    bamboo(doc, fr, Pm, 0.03 * W, 0.97 * H, fr.l(1500), 6, n=7)
    plum(doc, fr, Pm, (-0.02 * W, 0.045 * H), 0.26 * W, 8, 21)
