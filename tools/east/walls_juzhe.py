# SPDX-License-Identifier: GPL-2.0-or-later
"""juzhe (mature register): a lakeside hall under the mountains. Three planes: far ranges lost in mist,
a headland with two halls and a bridge, and the host hall at the lower right on a stone pier, its lit
door the landing, mirrored in the water. Flat vector planes, geometric texture (tile courses, stone
courses, contour strata, dot clusters), muted chroma, atmospheric perspective by palette(fog=t)."""
import math
import random

import calculus as K
from geom import f, smooth, juzhe, rrect
from walls_lib import (palette, lin, rad, along_light, blurf, cast, poly, sky, disc, bez, resample, pl,
                       mist, birds, pagoda, lattice, dougong, bricks, ridge_end, stair)


OPT = {}                       # per-form knobs, empty in the shipped forms


class grp:
    """Capture what is drawn into one <g id=...> kept in defs (so it can be used twice: the scene and
    its reflection)."""

    def __init__(self, doc, gid):
        self.doc, self.gid = doc, gid

    def __enter__(self):
        self.saved, self.doc.body = self.doc.body, []
        return self

    def __exit__(self, *a):
        inner = "".join(self.doc.body)
        self.doc.body = self.saved
        self.doc.defs.append(f'<g id="{self.gid}">{inner}</g>')


def strata(doc, fr, colour, y0, y1, step, opacity):
    n = int((y1 - y0) / step)
    d = "".join(f"M0 {f(y0 + i * step)}H{fr.w}" for i in range(n))
    doc.add(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{f(max(1.5, fr.s * 2))}" opacity="{f(opacity)}"/>')


# ------------------------------------------------------------------ mountains
def ridge(doc, fr, col, colf, shade, hi, tops, base, x0, x1, seed, contours=7, gap=26):
    """A range: peaks joined by juzhe slopes; vertical ramp from its colour to the fog at the foot;
    contour strata echoing the skyline; the shade face right of each spine (light is upper left)."""
    W, H = fr.w, fr.h
    rnd = random.Random(seed)
    pts = [(x0 * W, base * H)]
    prev = pts[0]
    faces = []
    for i, (tx, ty) in enumerate(tops):
        peak = (tx * W, ty * H)
        pts += juzhe(peak[0], peak[1], prev[0], prev[1], purlins=4, first=0.14)[::-1][1:]
        if i < len(tops) - 1:
            nx, ny = tops[i + 1]
            sx = peak[0] + (nx * W - peak[0]) * rnd.uniform(0.45, 0.6)
            sy = base * H - (base * H - max(peak[1], ny * H)) * rnd.uniform(0.2, 0.38)
        else:
            sx, sy = x1 * W, base * H
        down = juzhe(peak[0], peak[1], sx, sy, purlins=4, first=0.14)
        pts += down[1:]
        faces.append((peak, down, sx))
        prev = (sx, sy)
    top = min(p[1] for p in pts)
    line = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts)
    d = line + f"L{f(pts[-1][0])} {f((base + 0.3) * H)}L{f(pts[0][0])} {f((base + 0.3) * H)}Z"
    span = base * H + 0.05 * H - top
    g = lin(doc, [(0, col, 1), ((base * H - top) * 0.82 / span, colf, 1), ((base * H - top) / span, colf, 0.0), (1, colf, 0)], (0, top), (0, base * H + 0.05 * H))
    doc.add(f'<path d="{d}" fill="{g}"/>')
    c = doc.id("rc")
    doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
    g_sh = lin(doc, [(0, shade, 0.55), (1, shade, 0)], (0, top), (0, base * H))
    out = []
    for peak, down, sx in faces:
        foot = (peak[0] + 0.3 * (sx - peak[0]), base * H + 0.05 * H)
        out.append("M" + " L".join(f"{f(x)} {f(y)}" for x, y in [peak] + down[1:] + [(sx, base * H + 0.05 * H), foot]) + "Z")
    doc.add(f'<g clip-path="url(#{c})"><path d="{"".join(out)}" fill="{g_sh}"/>')
    for i in range(1, contours + 1):
        doc.add(f'<path d="{line}" transform="translate(0 {f(i * fr.l(gap))})" fill="none" stroke="{hi}" stroke-width="{f(max(1.5, fr.s * 2))}" opacity="{f(OPT.get('ridgeop', 0.34) * (1 - i / (contours + 1)))}"/>')
    doc.add("</g>")
    return top


# ------------------------------------------------------------------ trees
def dian_tree(doc, fr, Q, x, y, h, seed):
    """A broad tree as dian: a trunk with a turn, a dark mass of discs, mid dots, lit dots upper left."""
    rnd = random.Random(seed)
    tw = h * 0.05
    bend = rnd.uniform(-0.06, 0.06) * h
    doc.add(f'<path d="M{f(x - tw)} {f(y)}Q{f(x + bend - tw * 0.6)} {f(y - h * 0.35)} {f(x + bend)} {f(y - h * 0.6)}L{f(x + bend + tw * 0.5)} {f(y - h * 0.6)}Q{f(x + bend + tw)} {f(y - h * 0.3)} {f(x + tw)} {f(y)}Z" fill="{Q["bark"]}"/>')
    cx, cy = x + bend, y - h * 0.62
    rx, ry = h * 0.4, h * 0.24
    base, mid, lit = [], [], []
    for k in range(11):
        a, r = rnd.uniform(0, 6.283), rnd.random() ** 0.5
        base.append(f'<circle cx="{f(cx + rx * 0.75 * r * math.cos(a))}" cy="{f(cy + ry * 0.8 * r * math.sin(a))}" r="{f(h * rnd.uniform(0.08, 0.13))}"/>')
    for _ in range(150):
        a, r = rnd.uniform(0, 6.283), rnd.random() ** 0.5
        px_, py_ = rx * r * math.cos(a), ry * r * math.sin(a)
        c = f'<circle cx="{f(cx + px_)}" cy="{f(cy + py_)}" r="{f(h * rnd.uniform(0.018, 0.038))}"/>'
        (lit if (px_ / rx) * 0.45 + (py_ / ry) * 0.9 < -0.3 else mid).append(c)
    doc.add(f'<g fill="{Q["leaf2"]}">{"".join(base)}</g><g fill="{Q["leaf"]}">{"".join(mid)}</g><g fill="{Q["leaflit"]}" opacity="0.8">{"".join(lit)}</g>')


def spire(doc, fr, Q, x, y, h, seed):
    """A cypress: a narrow sawtooth spire, lit half and shade half split down the axis."""
    rnd = random.Random(seed)
    n = 11
    w = h * 0.11
    L, R = [], []
    for i in range(n + 1):
        t = i / n
        yy = y - h * t
        ww = w * math.sin(math.pi * min(1, 0.18 + 0.82 * (1 - t) ** 0.7 * 0.0 + 0.8 * (1 - t))) if False else w * (1 - t) ** 0.8 * (1.0 if i % 2 else 0.78)
        L.append((x - ww * rnd.uniform(0.9, 1.1), yy))
        R.append((x + ww * rnd.uniform(0.9, 1.1), yy))
    lit = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in L) + f"L{f(x)} {f(y - h)}L{f(x)} {f(y)}Z"
    shd = "M" + " L".join(f"{f(a)} {f(b)}" for a, b in R) + f"L{f(x)} {f(y - h)}L{f(x)} {f(y)}Z"
    doc.add(f'<path d="{lit}" fill="{Q["leaf"]}"/><path d="{shd}" fill="{Q["leaf2"]}"/>'
            f'<path d="M{f(x - w * 0.15)} {f(y - h * 0.9)}L{f(x - w * 0.15)} {f(y - h * 0.1)}" stroke="{Q["leaflit"]}" stroke-width="{f(max(2, h * 0.012))}" opacity="0.7"/>')


# ------------------------------------------------------------------ roofs and halls
def roof_m(doc, fr, Q, cx, ridge_y, ridge_w, eave_y, eave_w, pitch, lift=1.2, flick=0.05):
    """A hall roof in elevation: juzhe slopes, upturned eave corners, a lit-to-deep ramp along the
    light, tile ribs in lit/shade pairs, laps, hip edges, a fascia under the eave with tile ends,
    a ridge cap with a chiwen at each end. Returns the eave line."""
    W = fr.w
    rh = eave_y - ridge_y
    xl, xr = cx - ridge_w / 2, cx + ridge_w / 2
    el, er = cx - eave_w / 2, cx + eave_w / 2
    L = juzhe(xl, ridge_y, el, eave_y, purlins=6, first=0.3)
    R = juzhe(xr, ridge_y, er, eave_y, purlins=6, first=0.3)
    up = rh * flick * 4
    Lt = L[:-1] + [(el - eave_w * 0.01, eave_y - up)]
    Rt = R[:-1] + [(er + eave_w * 0.01, eave_y - up)]
    sag = rh * 0.06
    eave = [(er + eave_w * 0.01, eave_y - up), (er - eave_w * 0.06, eave_y + sag * 0.2), (cx, eave_y + sag),
            (el + eave_w * 0.06, eave_y + sag * 0.2), (el - eave_w * 0.01, eave_y - up)]
    TL = bez(Lt[::-1], 10) + [(xr, ridge_y)] + bez(Rt, 10)[1:]
    EL = bez(eave, 14)
    d = pl(TL) + " " + pl(EL[1:-1]).replace("M", "L", 1) + "Z"
    cast(doc, d, Q["shade"], fr, lift=lift, opacity=0.35)
    g0, g1 = along_light(fr, el, ridge_y, er, eave_y)
    doc.add(f'<path d="{d}" fill="{lin(doc, [(0, Q["roofa"], 1), (0.5, Q["roofb"], 1), (1, Q["roofc"], 1)], g0, g1)}"/>')
    c = doc.id("rc")
    doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
    n = max(12, int(eave_w / pitch))
    TA, EA = resample(TL, n), resample(EL[::-1], n)
    ribs = "".join(f"M{f(a[0])} {f(a[1])}L{f(b[0])} {f(b[1])}" for a, b in zip(TA, EA))
    sw = max(2, pitch * 0.16)
    laps = []
    for t in (0.18, 0.36, 0.54, 0.72, 0.88):
        laps.append(pl([(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(resample(TL, 60), resample(EL[::-1], 60))]))
    hips = pl(TL[: len(TL) // 2]) + pl(TL[len(TL) // 2:])
    doc.add(f'<g clip-path="url(#{c})" fill="none">'
            f'<path d="{ribs}" stroke="{Q["roofc"]}" stroke-opacity="0.5" stroke-width="{f(sw * 1.4)}" transform="translate({f(sw * 1.2)} 0)"/>'
            f'<path d="{ribs}" stroke="{Q["lit"]}" stroke-opacity="0.30" stroke-width="{f(sw)}"/>'
            f'<path d="{"".join(laps)}" stroke="{Q["roofc"]}" stroke-opacity="0.35" stroke-width="{f(sw * 1.3)}"/>'
            f'<path d="{hips}" stroke="{Q["lit"]}" stroke-opacity="0.55" stroke-width="{f(sw * 2.2)}"/></g>')
    # fascia under the eave and the round tile ends on it
    fa = max(4, rh * 0.075)
    fas = pl(EL) + " " + pl([(x, y + fa) for x, y in EL[::-1]]).replace("M", "L", 1) + "Z"
    doc.add(f'<path d="{fas}" fill="{Q["roofc"]}"/>')
    ends = resample(EL, max(8, int(eave_w / (pitch * 1.6))))
    r = max(3, pitch * 0.42)
    doc.add(f'<g fill="{Q["roofb"]}">{"".join(f"<circle cx={chr(34)}{f(x)}{chr(34)} cy={chr(34)}{f(y + fa * 0.45)}{chr(34)} r={chr(34)}{f(r)}{chr(34)}/>" for x, y in ends[1:-1])}</g>'
            f'<g fill="{Q["lit"]}" opacity="0.5">{"".join(f"<circle cx={chr(34)}{f(x - r * 0.3)}{chr(34)} cy={chr(34)}{f(y + fa * 0.45 - r * 0.3)}{chr(34)} r={chr(34)}{f(r * 0.4)}{chr(34)}/>" for x, y in ends[1:-1])}</g>')
    # soft shade under the eave on what lies below
    sh = pl(EL) + " " + pl([(x, y + fa + rh * 0.22) for x, y in EL[::-1]]).replace("M", "L", 1) + "Z"
    doc.add(f'<path d="{sh}" fill="{lin(doc, [(0, Q["shade"], 0.6), (1, Q["shade"], 0)], (0, eave_y), (0, eave_y + fa + rh * 0.22))}"/>')
    # ridge cap and ends
    rb = max(K.U * 2, rh * 0.075)
    doc.add(f'<path d="{rrect(xl - rb * 0.5, ridge_y - rb, ridge_w + rb, rb * 1.25, rb * 0.35)}" fill="{Q["roofb"]}"/>'
            f'<path d="M{f(xl)} {f(ridge_y - rb * 0.85)}H{f(xr)}" stroke="{Q["lit"]}" stroke-opacity="0.55" stroke-width="{f(max(2, rb * 0.14))}"/>'
            f'<path d="M{f(xl)} {f(ridge_y - rb * 0.35)}H{f(xr)}" stroke="{Q["roofc"]}" stroke-width="{f(max(2, rb * 0.22))}" stroke-dasharray="{f(rb * 0.4)} {f(rb * 0.4)}"/>')
    ridge_end(doc, fr, Q, xl, ridge_y - rb * 0.6, rb * 1.7, "roofb", mirror=True)
    ridge_end(doc, fr, Q, xr, ridge_y - rb * 0.6, rb * 1.7, "roofb")
    return EL


def caihua(doc, fr, Q, x, y, w, h):
    """The painted architrave: a band of diamonds and dots in jade, gold and cinnabar (tiny, muted)."""
    i = doc.id("ch")
    s = h
    doc.defs.append(f'<pattern id="{i}" patternUnits="userSpaceOnUse" x="{f(x)}" y="{f(y)}" width="{f(s * 1.6)}" height="{f(s)}">'
                    f'<path d="M{f(s * 0.4)} {f(s * 0.5)}L{f(s * 0.8)} {f(s * 0.12)}L{f(s * 1.2)} {f(s * 0.5)}L{f(s * 0.8)} {f(s * 0.88)}Z" fill="{Q["jade"]}" opacity="0.55"/>'
                    f'<circle cx="{f(s * 0.8)}" cy="{f(s * 0.5)}" r="{f(s * 0.1)}" fill="{Q["gold"]}" opacity="0.8"/>'
                    f'<path d="M0 {f(s * 0.5)}H{f(s * 0.3)}M{f(s * 1.3)} {f(s * 0.5)}H{f(s * 1.6)}" stroke="{Q["cinnabar"]}" stroke-width="{f(max(2, s * 0.08))}" opacity="0.6"/></pattern>')
    doc.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{Q["wall"]}"/>'
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="url(#{i})"/>')


def hall_m(doc, fr, Q, cx, base_y, w, double=False, lit_pattern=(1, 0, 1, 0, 1, 0, 1), lamp=1.0, bays=7, detail=1.0):
    """A hall in elevation on a stone pier: plinth and courses, a stair in the door bay, a balustrade,
    sill walls with lattice windows, columns, the painted architrave, a bracket band, the roof (two
    storeys when double). The door bay carries the one lit opening (the landing)."""
    s = w / 1000
    pf_h = 100 * s
    x0, x1 = cx - 0.36 * w, cx + 0.36 * w
    step = (x1 - x0) / bays
    top = base_y - pf_h
    # plinth (wider, low) and platform
    plinth = rrect(x0 - 90 * s, base_y - 34 * s, (x1 - x0) + 180 * s, 34 * s, 4 * s)
    pf = rrect(x0 - 50 * s, top, (x1 - x0) + 100 * s, pf_h - 30 * s, 4 * s)
    cast(doc, plinth, Q["shade"], fr, lift=1.4, opacity=0.4)
    doc.add(f'<path d="{plinth}" fill="{Q["block"]}"/><path d="{pf}" fill="{Q["ground"]}"/>')
    bricks(doc, fr, Q, pf, x0 - 50 * s, top, x1 + 50 * s, base_y, 56 * s * detail, 15 * s * detail)
    bricks(doc, fr, Q, plinth, x0 - 90 * s, base_y - 34 * s, x1 + 90 * s, base_y, 80 * s * detail, 17 * s * detail)
    doc.add(f'<rect x="{f(x0 - 50 * s)}" y="{f(top)}" width="{f((x1 - x0) + 100 * s)}" height="{f(max(2, 5 * s))}" fill="{Q["jointlit"]}" opacity="0.8"/>')
    # wall
    wall_h = 230 * s
    wy = top - wall_h
    doc.add(f'<rect x="{f(x0)}" y="{f(wy)}" width="{f(x1 - x0)}" height="{f(wall_h)}" fill="{Q["wall"]}"/>')
    cw = 18 * s
    mid = bays // 2
    dw = step - 2 * cw
    for i in range(bays):
        lx = x0 + i * step + cw
        if i == mid:
            continue
        # sill wall, then the window above it
        doc.add(f'<rect x="{f(lx)}" y="{f(wy + wall_h * 0.62)}" width="{f(dw)}" height="{f(wall_h * 0.38)}" fill="{Q["plaster"]}" opacity="0.9"/>'
                f'<rect x="{f(lx)}" y="{f(wy + wall_h * 0.62)}" width="{f(dw)}" height="{f(max(2, 4 * s))}" fill="{Q["lit"]}" opacity="0.4"/>')
        lat_back = Q["pane"] if lit_pattern[i % len(lit_pattern)] else Q["glass"]
        lattice(doc, fr, lx + 6 * s, wy + 34 * s, dw - 12 * s, wall_h * 0.62 - 54 * s, lat_back, Q["latbar"], max(8, 17 * s))
    # the door bay: a stair up to it and the lit opening
    dx = x0 + mid * step + cw
    dh = wall_h - 40 * s
    door = rrect(dx, wy + 40 * s, dw, dh, 4 * s)
    doc.add(f'<path d="{door}" fill="{rad(doc, [(0, Q["lightc"], 1), (0.55, Q["gold"], 1), (1, Q["gold"], 1)], (dx + dw * 0.4, wy + wall_h * 0.5), wall_h * 0.7)}"/>')
    mull = "".join(f"M{f(dx + dw * t)} {f(wy + 40 * s)}v{f(dh)}" for t in (0.25, 0.5, 0.75)) + "".join(f"M{f(dx)} {f(wy + 40 * s + dh * t)}h{f(dw)}" for t in (0.28, 0.72))
    doc.add(f'<path d="{mull}" fill="none" stroke="{Q["latbar"]}" stroke-width="{f(max(2, 5 * s))}" opacity="0.8"/>')
    # columns with a lit strip
    cols = []
    for i in range(bays + 1):
        x = x0 + i * step
        cols.append(f'<rect x="{f(x - cw / 2)}" y="{f(wy)}" width="{f(cw)}" height="{f(wall_h)}" fill="{Q["column"]}"/>'
                    f'<rect x="{f(x - cw / 2)}" y="{f(wy)}" width="{f(cw * 0.3)}" height="{f(wall_h)}" fill="{Q["blocklit"]}" opacity="0.4"/>')
    doc.add("".join(cols))
    # stair
    sx0, sx1 = dx - 14 * s, dx + dw + 14 * s
    stp = pf_h + 10 * s
    stair_d = f"M{f(sx0 - 30 * s)} {f(base_y)}L{f(sx0)} {f(top)}H{f(sx1)}L{f(sx1 + 30 * s)} {f(base_y)}Z"
    doc.add(f'<path d="{stair_d}" fill="{Q["jointlit"]}"/>')
    tr = "".join(f"M{f(sx0 - 30 * s * (1 - k / 7))} {f(top + stp * k / 7 - 10 * s * 0)}H{f(sx1 + 30 * s * (1 - k / 7))}" for k in range(1, 7))
    doc.add(f'<path d="{tr}" fill="none" stroke="{Q["joint"]}" stroke-width="{f(max(2, 5 * s))}" opacity="0.8"/>')
    # balustrade either side of the stair
    ry = top - 4 * s
    pw = 30 * s
    for (a, b) in ((x0 - 50 * s, sx0 - 10 * s), (sx1 + 10 * s, x1 + 50 * s)):
        n = max(2, int((b - a) / (pw * 1.6)))
        gap = (b - a) / n
        panels = "".join(f'<rect x="{f(a + k * gap + 6 * s)}" y="{f(ry - 24 * s)}" width="{f(gap - 12 * s)}" height="{f(18 * s)}" rx="{f(2 * s)}"/>' for k in range(n))
        posts = "".join(f'<rect x="{f(a + k * gap - 4 * s)}" y="{f(ry - 42 * s)}" width="{f(8 * s)}" height="{f(44 * s)}" rx="{f(2 * s)}"/>' for k in range(n + 1))
        doc.add(f'<g fill="{Q["rail"]}">{panels}{posts}</g><rect x="{f(a)}" y="{f(ry - 46 * s)}" width="{f(b - a)}" height="{f(7 * s)}" rx="{f(2 * s)}" fill="{Q["blocklit"]}" opacity="0.8"/>')
    # architrave and brackets
    ah = 34 * s
    caihua(doc, fr, Q, x0 - 8 * s, wy - ah, x1 - x0 + 16 * s, ah)
    bb = 60 * s
    doc.add(f'<rect x="{f(x0 - 14 * s)}" y="{f(wy - ah - bb)}" width="{f(x1 - x0 + 28 * s)}" height="{f(bb)}" fill="{Q["block"]}"/>')
    for i in range(bays * 2 + 1):
        dougong(doc, fr, Q, x0 + i * step / 2, wy - ah, min(bb * 0.95, step / 2 * 0.9 * 15 / 64))
    by = wy - ah - bb
    # lanterns at the lower eave corners
    pitch = max(8, 17 * s)
    if double:
        EL = roof_m(doc, fr, Q, cx, by - 30 * s, w * 0.78, by + 70 * s, w * 1.06, pitch, lift=1.6)
        wy2 = by - 40 * s
        doc.add(f'<rect x="{f(cx - w * 0.27)}" y="{f(wy2 - 150 * s)}" width="{f(w * 0.54)}" height="{f(150 * s)}" fill="{Q["wall"]}"/>')
        n2 = 5
        st2 = w * 0.54 / n2
        for i in range(n2):
            lattice(doc, fr, cx - w * 0.27 + i * st2 + 14 * s, wy2 - 120 * s, st2 - 28 * s, 90 * s,
                    Q["pane"] if lit_pattern[(i + 1) % len(lit_pattern)] else Q["glass"], Q["latbar"], max(8, 17 * s))
        for i in range(n2 + 1):
            x = cx - w * 0.27 + i * st2
            doc.add(f'<rect x="{f(x - 8 * s)}" y="{f(wy2 - 150 * s)}" width="{f(16 * s)}" height="{f(150 * s)}" fill="{Q["column"]}"/>')
        doc.add(f'<rect x="{f(cx - w * 0.29)}" y="{f(wy2 - 190 * s)}" width="{f(w * 0.58)}" height="{f(44 * s)}" fill="{Q["block"]}"/>')
        for i in range(2 * n2 + 1):
            dougong(doc, fr, Q, cx - w * 0.27 + i * st2 / 2, wy2 - 150 * s, min(40 * s, st2 / 2 * 0.9 * 15 / 64))
        roof_m(doc, fr, Q, cx, wy2 - 360 * s, w * 0.4, wy2 - 150 * s, w * 0.86, pitch, lift=1.8)
        top_y = wy2 - 360 * s
    else:
        roof_m(doc, fr, Q, cx, by - 210 * s, w * 0.5, by + 50 * s, w * 1.06, pitch, lift=1.4)
        top_y = by - 210 * s
    # the warm glow the door throws on the stair
    doc.add(f'<ellipse cx="{f(dx + dw / 2)}" cy="{f(top + 8 * s)}" rx="{f(dw * 1.5)}" ry="{f(24 * s)}" fill="{Q["gold"]}" opacity="{f(0.35 * lamp)}" filter="{blurf(doc, 14 * s)}"/>')
    return x0 - 90 * s, x1 + 90 * s, top_y


# ------------------------------------------------------------------ water and bridge
def bridge(doc, fr, Q, xa, xb, y_w, deck_h, arches=3):
    """A low stone arch bridge: parapet with balusters, a hump deck, three arches whose reflections
    close the circles; courses on the spandrels."""
    W = xb - xa
    deck_y = y_w - deck_h
    hump = deck_h * 0.18
    body = (f"M{f(xa)} {f(y_w)}L{f(xa)} {f(deck_y)}Q{f((xa + xb) / 2)} {f(deck_y - 2 * hump)} {f(xb)} {f(deck_y)}L{f(xb)} {f(y_w)}Z")
    cast(doc, body, Q["shade"], fr, lift=1.0, opacity=0.35)
    g0, g1 = along_light(fr, xa, deck_y, xb, y_w)
    doc.add(f'<path d="{body}" fill="{lin(doc, [(0, Q["jointlit"], 1), (1, Q["ground2"], 1)], g0, g1)}"/>')
    aw = W / arches
    for k in range(arches):
        ax = xa + aw * (k + 0.5)
        r = aw * 0.36
        ry = deck_h * (0.62 if k == arches // 2 else 0.5)
        doc.add(f'<path d="M{f(ax - r)} {f(y_w)}A{f(r)} {f(ry)} 0 0 1 {f(ax + r)} {f(y_w)}Z" fill="{lin(doc, [(0, Q["roofc"], 0.85), (0.6, Q["water"], 1), (1, Q["water"], 1)], (0, y_w - ry), (0, y_w))}"/>'
                f'<path d="M{f(ax - r)} {f(y_w)}A{f(r)} {f(ry)} 0 0 1 {f(ax + r)} {f(y_w)}" fill="none" stroke="{Q["lit"]}" stroke-opacity="0.5" stroke-width="{f(max(2, fr.s * 4))}"/>')
    cs = "".join(f"M{f(xa)} {f(y_w - deck_h * t)}H{f(xb)}" for t in (0.22, 0.45, 0.68, 0.9))
    doc.add(f'<path d="{cs}" fill="none" stroke="{Q["joint"]}" stroke-width="{f(max(1.5, fr.s * 2))}" opacity="0.45"/>')
    # parapet
    n = int(W / (fr.l(26)))
    posts = []
    for i in range(n + 1):
        t = i / n
        x = xa + W * t
        yy = deck_y - 4 * hump * t * (1 - t)
        posts.append(f'<rect x="{f(x - fr.l(3))}" y="{f(yy - fr.l(26))}" width="{f(fr.l(6))}" height="{f(fr.l(26))}"/>')
    doc.add(f'<g fill="{Q["rail"]}">{"".join(posts)}</g>'
            f'<path d="M{f(xa)} {f(deck_y - fr.l(26))}Q{f((xa + xb) / 2)} {f(deck_y - fr.l(26) - 2 * hump)} {f(xb)} {f(deck_y - fr.l(26))}" stroke="{Q["blocklit"]}" stroke-width="{f(fr.l(6))}" fill="none"/>')


def water(doc, fr, P, y0, y_w):
    W, H = fr.w, fr.h
    g0, g1 = along_light(fr, -0.2 * W, y0, 1.2 * W, H)
    g = lin(doc, [(0, P["fog"], 1), (0.35, P["water"], 1), (1, P["water2"], 1)], g0, g1)
    doc.add(f'<rect x="0" y="{f(y0)}" width="{W}" height="{f(H - y0)}" fill="{g}"/>')


def water_lines(doc, fr, P, y0, seed):
    """Ripple strata: long thin lines, wider apart and thicker toward the viewer."""
    rnd = random.Random(seed)
    out = []
    n = 90
    for i in range(n):
        t = (i / n) ** 1.7
        y = y0 + (fr.h - y0) * t
        l = fr.w * rnd.uniform(0.05, 0.22) * (0.5 + t)
        x = rnd.uniform(-0.05, 1.0) * fr.w
        out.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(l)}" height="{f(max(1.5, fr.s * (1.5 + 5 * t)))}" rx="1"/>')
    doc.add(f'<g fill="{P["ripple"]}" opacity="0.5">{"".join(out)}</g>')


def glade(doc, fr, P, x, y0, seed):
    """The light's path on the water: short broken bars under the light, wider and farther apart
    toward the viewer."""
    rnd = random.Random(seed)
    out = []
    n = 16
    for i in range(n):
        t = (i + 0.5) / n
        y = y0 + (fr.h - y0) * t ** 1.25
        w = fr.l(60 + 380 * t) * rnd.uniform(0.6, 1.1)
        cx = x + rnd.uniform(-1, 1) * fr.l(40 + 70 * t)
        out.append(f'<rect x="{f(cx - w / 2)}" y="{f(y)}" width="{f(w)}" height="{f(max(2, fr.s * (3 + 6 * t)))}" rx="2" opacity="{f(0.7 - 0.35 * t)}"/>')
    doc.add(f'<g fill="{P["lightc"]}">{"".join(out)}</g>')


def reflect(doc, fr, P, gid, y_w, depth, seed):
    """The mirror image of group gid below y_w: clipped, faded with depth, broken by horizontal gaps."""
    W, H = fr.w, fr.h
    rnd = random.Random(seed)
    m = doc.id("rm")
    strips = []
    y = y_w
    while y < H:
        t = (y - y_w) / (H - y_w)
        gap = fr.s * (3 + 14 * t) * rnd.uniform(0.6, 1.3)
        x = -rnd.uniform(0, 0.1) * W
        while x < W:
            ln = rnd.uniform(0.05, 0.2) * W
            strips.append(f'<rect x="{f(x)}" y="{f(y)}" width="{f(ln)}" height="{f(gap)}" fill="#000"/>')
            x += ln + rnd.uniform(0.012, 0.05) * W
        y += gap + fr.s * (10 + 22 * (1 - t)) * rnd.uniform(0.6, 1.4)
    doc.defs.append(f'<linearGradient id="{m}g" gradientUnits="userSpaceOnUse" x1="0" y1="{f(y_w)}" x2="0" y2="{f(y_w + depth)}">'
                    f'<stop offset="0" stop-color="#fff" stop-opacity="0.85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                    f'<mask id="{m}" maskUnits="userSpaceOnUse" x="0" y="{f(y_w)}" width="{W}" height="{f(H - y_w)}">'
                    f'<rect x="0" y="{f(y_w)}" width="{W}" height="{f(H - y_w)}" fill="url(#{m}g)"/>{"".join(strips)}</mask>')
    c = doc.id("rcl")
    doc.defs.append(f'<clipPath id="{c}"><rect x="0" y="{f(y_w)}" width="{W}" height="{f(H - y_w)}"/></clipPath>')
    doc.add(f'<g clip-path="url(#{c})"><g mask="url(#{m})"><use xlink:href="#{gid}" transform="translate(0 {f(2 * y_w)}) scale(1 -1)" opacity="0.7"/></g></g>')


def bank(doc, fr, P, seed):
    """The near plane at the lower left: a dark bank with strata, three stones lit upper left, reeds
    leaning toward the host (they point the eye along the vein)."""
    W, H = fr.w, fr.h
    rnd = random.Random(seed)
    pts = [(-0.03 * W, 0.925 * H), (0.04 * W, 0.915 * H), (0.09 * W, 0.94 * H), (0.135 * W, 0.98 * H), (0.16 * W, 1.03 * H)]
    d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts) + f"L{f(-0.03 * W)} {f(1.03 * H)}Z"
    g0, g1 = along_light(fr, 0, 0.87 * H, 0.24 * W, H)
    cast(doc, d, P["shade"], fr, lift=1.6, opacity=0.4)
    doc.add(f'<path d="{d}" fill="{lin(doc, [(0, P["roofb"], 1), (1, P["roofc"], 1)], g0, g1)}"/>')
    c = doc.id("bk")
    doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
    line = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts)
    ls = "".join(f'<path d="{line}" transform="translate({f(-i * fr.l(6))} {f(i * fr.l(18))})"/>' for i in range(1, 8))
    doc.add(f'<g clip-path="url(#{c})"><g fill="none" stroke="{P["lit"]}" stroke-width="{f(max(1.5, fr.s * 2))}" opacity="0.3">{ls}</g></g>')
    for x, y, r in ((0.035, 0.945, 50), (0.085, 0.975, 34), (0.01, 0.99, 38)):
        rx, ry = fr.l(r) * 1.5, fr.l(r)
        cx, cy = x * W, y * H
        stone = f"M{f(cx - rx)} {f(cy + ry * 0.4)}C{f(cx - rx)} {f(cy - ry)} {f(cx + rx * 0.4)} {f(cy - ry * 1.1)} {f(cx + rx)} {f(cy + ry * 0.3)}Z"
        doc.add(f'<path d="{stone}" fill="{lin(doc, [(0, P["roofa"], 1), (1, P["roofc"], 1)], *along_light(fr, cx - rx, cy - ry, cx + rx, cy + ry))}"/>'
                f'<path d="M{f(cx - rx * 0.8)} {f(cy - ry * 0.1)}Q{f(cx - rx * 0.3)} {f(cy - ry * 0.9)} {f(cx + rx * 0.2)} {f(cy - ry * 0.85)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(max(2, fr.s * 4))}" opacity="0.5"/>')
    out, heads = [], []
    for i in range(34):
        x = rnd.uniform(0.0, 0.12) * W
        y = (0.93 + 0.06 * (x / (0.12 * W))) * H + fr.l(30)
        h = fr.l(rnd.uniform(110, 300)) * (1 - 0.5 * x / (0.12 * W) + 0.2)
        lean = fr.l(rnd.uniform(30, 150))
        out.append(f"M{f(x)} {f(y)}Q{f(x + lean * 0.25)} {f(y - h * 0.6)} {f(x + lean)} {f(y - h)}")
        if i % 5 == 0:
            heads.append(f'<ellipse cx="{f(x + lean)}" cy="{f(y - h)}" rx="{f(fr.l(7))}" ry="{f(fr.l(26))}" transform="rotate(20 {f(x + lean)} {f(y - h)})"/>')
    doc.add(f'<path d="{"".join(out)}" fill="none" stroke="{P["roofc"]}" stroke-width="{f(max(2, fr.s * 5))}" stroke-linecap="round"/><g fill="{P["roofb"]}">{"".join(heads)}</g>')


def stars(doc, fr, P, seed, n=140):
    """Stars: tiny lit dots, most of them high and away from the moon, a few brighter with a cross."""
    rnd = random.Random(seed)
    out, big = [], []
    for _ in range(n):
        x, y = rnd.uniform(0, 1) * fr.w, rnd.uniform(0, 0.5) ** 1.3 * fr.h * 1.6
        if y > 0.46 * fr.h or math.hypot(x - 0.2 * fr.w, y - 0.2 * fr.h) < 0.12 * fr.h:
            continue
        r = fr.s * rnd.uniform(1.6, 3.6)
        out.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" opacity="{f(rnd.uniform(0.45, 0.95))}"/>')
        if rnd.random() < 0.1:
            a = r * 5
            big.append(f"M{f(x - a)} {f(y)}H{f(x + a)}M{f(x)} {f(y - a)}V{f(y + a)}")
    doc.add(f'<g fill="{P["lightc"]}">{"".join(out)}</g><path d="{"".join(big)}" stroke="{P["lightc"]}" stroke-width="{f(fr.s * 1.6)}" opacity="0.6" fill="none"/>')


def streak(doc, fr, colour, hair, x, y, w, h, opacity=0.8, up=0.0):
    """A stratus streak: a long lens that tapers at both ends, tail rising a little (juzhe turn-up),
    with hairlines along its length; flat, lit from above."""
    d = (f"M{f(x)} {f(y)}C{f(x + w * 0.25)} {f(y - h)} {f(x + w * 0.7)} {f(y - h * 0.8)} {f(x + w)} {f(y - up)}"
         f"C{f(x + w * 0.7)} {f(y + h * 0.5)} {f(x + w * 0.25)} {f(y + h * 0.6)} {f(x)} {f(y)}Z")
    hl = "".join(f"M{f(x + w * (0.08 + 0.05 * k))} {f(y - h * (0.28 - 0.2 * k))}H{f(x + w * (0.85 - 0.12 * k))}" for k in range(3))
    doc.add(f'<path d="{d}" fill="{colour}" opacity="{f(opacity)}"/>'
            f'<path d="{hl}" fill="none" stroke="{hair}" stroke-width="{f(max(2, fr.s * 3))}" opacity="0.45" stroke-linecap="round"/>')


def clouds(doc, fr, P):
    W, H = fr.w, fr.h
    streak(doc, fr, P["cloud"], P["cloudline"], 0.04 * W, 0.075 * H, fr.l(620), fr.l(34), 0.9, up=fr.l(10))
    streak(doc, fr, P["cloud"], P["cloudline"], 0.30 * W, 0.115 * H, fr.l(880), fr.l(44), 0.85, up=fr.l(16))
    streak(doc, fr, P["cloud2"], P["cloudline"], 0.62 * W, 0.075 * H, fr.l(760), fr.l(40), 0.8, up=fr.l(14))
    streak(doc, fr, P["cloud2"], P["cloudline"], 0.44 * W, 0.215 * H, fr.l(520), fr.l(28), 0.7, up=fr.l(8))
    streak(doc, fr, P["cloud"], P["cloudline"], 0.80 * W, 0.17 * H, fr.l(420), fr.l(26), 0.7, up=fr.l(8))


def plum(doc, fr, P, anchor, length, ang, seed):
    """A flowering plum limb from the upper-left edge (perseverance, first spring): a bark limb that
    turns, thinning twigs at mature angles, five-petal blossoms at the twig tips, a few cinnabar buds."""
    rnd = random.Random(seed)
    segs, blooms = [], []

    def limb(x, y, a, L, w, depth):
        pts = [(x, y)]
        for i in range(5):
            a += math.radians(rnd.uniform(-16, 22) if depth == 0 else rnd.uniform(-30, 30))
            x += math.cos(a) * L / 5
            y += math.sin(a) * L / 5
            pts.append((x, y))
        line = bez(pts, 6)
        l, r = [], []
        for i, (px_, py_) in enumerate(line):
            q, p0 = line[min(i + 1, len(line) - 1)], line[max(i - 1, 0)]
            dx, dy = q[0] - p0[0], q[1] - p0[1]
            n = math.hypot(dx, dy) or 1
            ww = w * (1 - 0.8 * i / len(line))
            l.append((px_ - dy / n * ww / 2, py_ + dx / n * ww / 2))
            r.append((px_ + dy / n * ww / 2, py_ - dx / n * ww / 2))
        segs.append("M" + " L".join(f"{f(a_)} {f(b_)}" for a_, b_ in l + r[::-1]) + "Z")
        if depth < 3:
            for k in range(3 if depth == 0 else 2):
                t = 0.35 + 0.6 * rnd.random()
                bx, by = line[int(t * (len(line) - 1))]
                side = rnd.choice((-1, 1))
                limb(bx, by, a + side * math.radians(rnd.uniform(28, 62)), L * rnd.uniform(0.35, 0.55), w * 0.5, depth + 1)
        else:
            blooms.append((x, y))
        if depth >= 2:
            blooms.append((x, y))
    limb(anchor[0], anchor[1], math.radians(ang), length, fr.l(44), 0)
    doc.add(f'<path d="{"".join(segs)}" fill="{P["bark"]}"/>')
    pet, cen, buds = [], [], []
    r0 = fr.l(15)
    for bx, by in blooms:
        for i in range(5):
            a = 2 * math.pi * i / 5 + rnd.uniform(0, 1)
            pet.append(f'<circle cx="{f(bx + math.cos(a) * r0 * 0.8)}" cy="{f(by + math.sin(a) * r0 * 0.8)}" r="{f(r0 * 0.62)}"/>')
        cen.append(f'<circle cx="{f(bx)}" cy="{f(by)}" r="{f(r0 * 0.28)}"/>')
        if rnd.random() < 0.5:
            buds.append(f'<circle cx="{f(bx + rnd.uniform(-1, 1) * r0 * 2.4)}" cy="{f(by + rnd.uniform(-1, 1) * r0 * 2.4)}" r="{f(r0 * 0.34)}"/>')
    doc.add(f'<g fill="{P["blossom"]}">{"".join(pet)}</g><g fill="{P["gold"]}">{"".join(cen)}</g><g fill="{P["cinnabar"]}">{"".join(buds)}</g>')


# ------------------------------------------------------------------ the form
def form_juzhe(doc, fr, P):
    W, H = fr.w, fr.h
    name = P["_name"]
    Pn, _ = palette(name, 0.12)            # middle plane
    Pf, _ = palette(name, 0.4)             # far plane
    Pm, _ = palette(name, 0.0)             # near plane
    y_w = fr.y(0.745)
    light = (fr.x(0.2), fr.y(0.2), fr.l(OPT.get('moon', 84)))
    sky(doc, fr, P, light)
    if name == 'night':
        stars(doc, fr, P, OPT.get('sseed', 5), OPT.get('stars', 140))
    strata(doc, fr, P["glow"], 0, fr.y(0.42), fr.l(30), 0.04 if name == 'night' else 0.10)
    gl = rad(doc, [(0, P["lightc"], 0.4), (0.3, P["lightc"], 0.12), (1, P["lightc"], 0)], (light[0], light[1]), light[2] * 6)
    doc.add(f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2] * 6)}" fill="{gl}"/>'
            f'<circle cx="{f(light[0])}" cy="{f(light[1])}" r="{f(light[2])}" fill="{P["lightc"]}"/>')
    # water: the sky's colour at the far shore, deeper toward the viewer
    water(doc, fr, P, fr.y(0.50), y_w)
    water_lines(doc, fr, P, y_w, 5)
    # far ranges, lighter and cooler with distance, a guest peak leaning to the host on the right
    ridge(doc, fr, P["ridge1"], P["fog"], P["ridge2"], P["lit"], [(0.30, 0.37), (0.45, 0.31), (0.60, 0.24), (0.78, 0.15), (0.93, 0.29)], 0.57, -0.05, 1.06, 5, contours=9)
    pagoda(doc, fr, Pf, fr.x(0.60), fr.y(0.245), fr.l(190), role="ridge4")
    mist(doc, fr, P, 0.40, 0.09, x0=0.2, opacity=0.55, seed=2)
    ridge(doc, fr, P["ridge2"], P["fog"], P["ridge3"], P["lit"], [(0.12, 0.44), (0.33, 0.40), (0.52, 0.36), (0.72, 0.31), (0.97, 0.42)], 0.61, -0.05, 1.06, 8, contours=8)
    mist(doc, fr, P, 0.50, 0.09, x0=0.2, opacity=0.6, seed=4)
    ridge(doc, fr, P["ridge3"], P["fog"], P["ridge4"], P["lit"], [(0.50, 0.50), (0.68, 0.46), (0.9, 0.48)], 0.665, -0.05, 1.06, 3, contours=6)
    with grp(doc, "land"):
        # the headland: terraces as contour lines, trees as dian, two halls and a stair
        top = [(-0.05 * W, 0.40 * H), (0.06 * W, 0.405 * H), (0.17 * W, 0.44 * H), (0.28 * W, 0.50 * H), (0.36 * W, 0.60 * H), (0.405 * W, 0.70 * H), (0.43 * W, y_w - 0.004 * H)]
        shore = [(0.43 * W, y_w - 0.004 * H), (0.34 * W, y_w + 0.008 * H), (0.26 * W, y_w - 0.006 * H), (0.17 * W, y_w + 0.012 * H), (0.08 * W, y_w - 0.004 * H), (-0.05 * W, y_w + 0.006 * H)]
        d = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + smooth(shore) + "Z"
        g0, g1 = along_light(fr, 0, 0.4 * H, 0.43 * W, y_w)
        doc.add(f'<path d="{d}" fill="{lin(doc, [(0, Pn["hill"], 1), (1, Pn["hill2"], 1)], g0, g1)}"/>')
        c = doc.id("hc")
        doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
        line = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top)
        lines = "".join(f'<path d="{line}" transform="translate({f(-i * fr.l(10))} {f(i * fr.l(38))})"/>' for i in range(1, 12))
        doc.add(f'<g clip-path="url(#{c})"><g fill="none" stroke="{Pn["lit"]}" stroke-width="{f(max(2, fr.s * 3))}" opacity="{0.24 if name == 'night' else 0.42}">{lines}</g>'
                f'<g fill="none" stroke="{Pn["shade"]}" stroke-width="{f(max(2, fr.s * 3))}" opacity="0.35" transform="translate(0 {f(fr.l(8))})">{lines}</g></g>')
        # the far hall (high on the headland), in mist
        hall_m(doc, fr, Pf, fr.x(0.115), fr.y(0.455), fr.l(430), lit_pattern=(0,), lamp=0.3, detail=1.6)
        mist(doc, fr, P, 0.46, 0.06, x0=0.0, x1=0.4, opacity=0.5, seed=7)
        for x, y, h, sd in ((0.035, 0.455, 210, 1), (0.215, 0.49, 170, 2), (0.19, 0.50, 120, 3)):
            dian_tree(doc, fr, Pf, fr.x(x), fr.y(y), fr.l(h), sd)
        stair(doc, fr, Pn, [(0.42 * W, 0.745 * H), (0.355 * W, 0.70 * H), (0.335 * W, 0.65 * H), (0.30 * W, 0.615 * H)], fr.l(130), fr.l(60))
        hall_m(doc, fr, Pn, fr.x(0.255), fr.y(0.585), fr.l(780), lit_pattern=(0, 1, 0), lamp=0.6, detail=1.3)
        for x, y, h, sd in ((0.075, 0.60, 300, 4), (0.125, 0.625, 230, 5), (0.375, 0.63, 250, 6), (0.40, 0.70, 190, 8)):
            dian_tree(doc, fr, Pn, fr.x(x), fr.y(y), fr.l(h), sd)
        spire(doc, fr, Pn, fr.x(0.045), fr.y(0.62), fr.l(330), 9)
        spire(doc, fr, Pn, fr.x(0.095), fr.y(0.64), fr.l(250), 10)
        bridge(doc, fr, Pn, fr.x(0.41), fr.x(0.585), y_w, fr.l(150))
        hall_m(doc, fr, Pm, fr.x(OPT.get('hx', 0.735)), y_w, fr.l(1320), double=True, lit_pattern=(1, 0, 1, 1, 0, 1, 0), lamp=1.0, detail=1.0)
    reflect(doc, fr, P, "land", y_w, fr.h - y_w, 3)
    if OPT.get('glade', 1):
        glade(doc, fr, P, light[0], y_w + 0.01 * H, 4)
    doc.add('<use xlink:href="#land"/>')
    # a low mist along the water, between the planes
    mist(doc, fr, P, 0.70, 0.05, x0=0.3, x1=0.7, opacity=0.35, seed=9)
    if OPT.get('bank', 0):
        bank(doc, fr, Pm, 3)
    if OPT.get('clouds', 1):
        clouds(doc, fr, P)
    if OPT.get('plum', 1):
        plum(doc, fr, Pm, (-0.02 * W, 0.045 * H), OPT.get('plumlen', 0.3) * W, 8, 21)
    birds(doc, fr, P, [(0.34 * W, 0.17 * H), (0.46 * W, 0.12 * H), (0.56 * W, 0.17 * H), (0.60 * W, 0.28 * H)], 9, 4, role="line2")
