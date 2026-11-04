# SPDX-License-Identifier: GPL-2.0-or-later
"""Pure abstracts (the register of the big OS default wallpapers, from our calculus):
  veil   translucent bands sweeping from the light (upper left) to one landing (lower right)
  bloom  petals of light layered around the landing, turned by the 7:5 step
  dunes  wave hills in six layers, light on the crests, haze between
  twist  one ribbon folding over itself along an S-curve, lit face and shade face
Colours are the palette roles (all derive()); the accent (gold) stays under 1/7 of the frame; the
bands and petals use cai-fen widths (21, 42, 84, 144 fen); nine zones are balanced by construction
(the paths cross every third of the frame) and the centre carries thin parts only."""
import math
import random

import calculus as K
from geom import f, smooth
from walls_lib import palette, lin, rad, blurf, sky, bez, resample, pl, mist
from walls_juzhe import stars

FEN = K.U


def band(doc, fr, P, fill, y0, y1, amp, phase, thick, opacity, blur=0, hair=True, x0=-0.08, x1=1.08, p=0.9, f2=1.7, a2=0.35):
    """One veil: centreline from (x0, y0) to (x1, y1) with two sine terms, thickness tapering at both ends."""
    W, H = fr.w, fr.h
    n = 36
    top, bot, mid = [], [], []
    for i in range(n + 1):
        u = i / n
        x = (x0 + (x1 - x0) * u) * W
        y = (y0 + (y1 - y0) * u) * H + amp * H * (math.sin(2 * math.pi * (1.1 * u + phase)) + a2 * math.sin(2 * math.pi * (f2 * u + phase * 2.3)))
        w = thick * H * (math.sin(math.pi * u) ** p)
        mid.append((x, y))
        top.append((x, y - w / 2))
        bot.append((x, y + w / 2))
    d = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + f"L{f(bot[-1][0])} {f(bot[-1][1])}" + smooth(bot[::-1]) + "Z"
    flt = f' filter="{blurf(doc, blur)}"' if blur else ""
    doc.add(f'<path d="{d}" fill="{fill}" opacity="{f(opacity)}"{flt}/>')
    if hair and not blur:
        t_ = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top)
        b_ = f"M{f(bot[0][0])} {f(bot[0][1])}" + smooth(bot)
        doc.add(f'<path d="{t_}" fill="none" stroke="{P["lit"]}" stroke-width="{f(max(1.5, fr.s * 2.5))}" opacity="{f(opacity * 0.55)}"/>'
                f'<path d="{b_}" fill="none" stroke="{P["shade"]}" stroke-width="{f(max(1.5, fr.s * 2))}" opacity="{f(opacity * 0.25)}"/>')
    return mid


def backdrop(doc, fr, P, night, seed=5):
    W, H = fr.w, fr.h
    sky(doc, fr, P, (fr.x(0.12), fr.y(0.12), fr.l(60)))
    if night:
        stars(doc, fr, P, seed, 70)
    g = rad(doc, [(0, P["lightc"], 0.55), (0.3, P["lightc"], 0.16), (1, P["lightc"], 0)], (0.12 * W, 0.12 * H), 0.7 * H)
    doc.add(f'<circle cx="{f(0.12 * W)}" cy="{f(0.12 * H)}" r="{f(0.7 * H)}" fill="{g}"/>')


def landing_glow(doc, fr, P, cx, cy, r):
    g = rad(doc, [(0, P["gold"], 0.85), (0.25, P["gold"], 0.35), (1, P["gold"], 0)], (cx, cy), r)
    doc.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{g}"/>')


FAMILIES = {
    # swirls: (point, sign, strength, radius); meander: lateral wave amplitude; seeds: number of veils
    "fold": dict(swirls=[((0.40, 0.66), 1, 1.0, 0.30)], meander=0.0, n=11, th=1.0),
    "vortex": dict(swirls=[((0.72, 0.70), 1, 1.5, 0.55)], meander=0.0, n=11, th=1.0),
    "pair": dict(swirls=[((0.28, 0.30), 1, 0.9, 0.24), ((0.44, 0.84), -1, 0.7, 0.20)], meander=0.0, n=11, th=0.9),
    "braid": dict(swirls=[((0.34, 0.40), 1, 0.8, 0.20), ((0.50, 0.78), -1, 0.7, 0.18)], meander=0.0, n=13, th=0.7),
    "meander": dict(swirls=[], meander=0.9, n=11, th=0.9),
    "lattice": dict(swirls=[((0.45, 0.60), 1, 0.5, 0.40)], meander=0.0, n=26, th=0.32),
}


def flow_dir(x, y, land=(0.72, 0.70), fam="fold"):
    """Unit direction of the flow at (x, y) in frame fractions: toward the landing, bent by the family's
    swirls (the spirit screen: the path turns before it lands, never a straight shot)."""
    F = FAMILIES[fam]
    dx, dy = land[0] - x, land[1] - y
    d = math.hypot(dx, dy) or 1
    ux, uy = dx / d, dy / d
    vx, vy = ux, uy
    for (px, py), sg, k, rad_ in F["swirls"]:
        fx, fy = x - px, y - py
        r = math.hypot(fx, fy) or 1e-3
        w = k * math.exp(-(r / rad_) ** 2)
        vx += sg * w * 1.6 * (-fy / r)
        vy += sg * w * 1.6 * (fx / r)
    if F["meander"]:
        s_ = (x * 0.8 + y * 0.5)
        a_ = F["meander"] * math.sin(2 * math.pi * 1.7 * s_) * min(1.0, d * 2.5)
        vx += a_ * -uy
        vy += a_ * ux
    n = math.hypot(vx, vy) or 1
    return vx / n, vy / n


def streamline(x0, y0, land=(0.72, 0.70), step=0.012, n=160, aspect=16 / 9, fam="fold"):
    pts = [(x0, y0)]
    x, y = x0, y0
    for _ in range(n):
        vx, vy = flow_dir(x, y, land, fam)
        x += vx * step
        y += vy * step * aspect
        pts.append((x, y))
        if math.hypot((x - land[0]), (y - land[1]) / aspect) < 0.03:
            break
    return pts


def veil_from(doc, fr, P, pts, fill, thick, opacity, blur=0, hair=True, taper=(0.15, 0.55)):
    """A translucent band laid along a streamline: thin at the entry, fullest before the fold, closing
    on the landing (kai he: opening and closing)."""
    W, H = fr.w, fr.h
    m = resample([(x * W, y * H) for x, y in pts], 40)
    top, bot = [], []
    for i, (x, y) in enumerate(m):
        u = i / (len(m) - 1)
        q = m[min(i + 1, len(m) - 1)]
        p0 = m[max(i - 1, 0)]
        dx, dy = q[0] - p0[0], q[1] - p0[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        env = math.sin(math.pi * min(1.0, u ** taper[0])) ** 1.2 * (1 - 0.6 * u ** 3)
        w = thick * H * env
        top.append((x + nx * w / 2, y + ny * w / 2))
        bot.append((x - nx * w / 2, y - ny * w / 2))
    d = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + f"L{f(bot[-1][0])} {f(bot[-1][1])}" + smooth(bot[::-1]) + "Z"
    flt = f' filter="{blurf(doc, blur)}"' if blur else ""
    doc.add(f'<path d="{d}" fill="{fill}" opacity="{f(opacity)}"{flt}/>')
    if hair and not blur:
        doc.add(f'<path d="M{f(top[0][0])} {f(top[0][1])}{smooth(top)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(max(1.5, fr.s * 2.5))}" opacity="{f(opacity * 0.6)}"/>'
                f'<path d="M{f(bot[0][0])} {f(bot[0][1])}{smooth(bot)}" fill="none" stroke="{P["shade"]}" stroke-width="{f(fr.s * 2)}" opacity="{f(opacity * 0.3)}"/>')


def form_veil(doc, fr, P):
    """Reading: enters by the light at the upper left, bends around the fold in the middle, lands at
    the lower right where the veils close over the gold."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    backdrop(doc, fr, P, night)
    land = (0.72, 0.70)
    seeds = [(-0.05, 0.06, "ridge1", "fog", 0.30, 0.5, 30), (-0.05, 0.16, "cloud", "ridge1", 0.22, 0.55, 0), (-0.05, 0.28, "ridge2", "ridge1", 0.20, 0.6, 0),
             (0.02, -0.04, "plaster", "ridge2", 0.07, 0.55, 0), (-0.05, 0.40, "water", "ridge3", 0.17, 0.62, 0), (-0.05, 0.50, "leaf", "water", 0.15, 0.55, 0),
             (0.10, -0.05, "ridge3", "ridge4", 0.15, 0.68, 0), (-0.05, 0.62, "ridge4", "roofb", 0.13, 0.78, 0), (-0.05, 0.74, "plaster", "ridge2", 0.05, 0.6, 0),
             (0.20, -0.05, "cloud", "water", 0.10, 0.5, 0), (-0.05, 0.86, "ridge2", "ridge1", 0.12, 0.5, 0)]
    for x0, y0, a, b, th, op, bl in seeds:
        pts = streamline(x0, y0, land)
        g = lin(doc, [(0, P[a], 1), (1, P[b], 1)], (pts[0][0] * W, pts[0][1] * H), (pts[-1][0] * W, pts[-1][1] * H))
        veil_from(doc, fr, P, pts, g, th, op, bl)
    # the fold itself: a few thin hairline streamlines that carry the eye around the turn
    for y0 in (0.22, 0.34, 0.46, 0.58):
        pts = streamline(-0.05, y0, land)
        doc.add(f'<path d="M{" L".join(f"{f(x * W)} {f(y * H)}" for x, y in pts)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 2)}" opacity="0.35"/>')
    landing_glow(doc, fr, P, land[0] * W, land[1] * H, 0.2 * H)
    for r_ in (21, 42, 84):
        doc.add(f'<circle cx="{f(land[0] * W)}" cy="{f(land[1] * H)}" r="{f(r_ * FEN * fr.s * 3)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 2)}" opacity="0.35"/>')


def form_bloom(doc, fr, P):
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    backdrop(doc, fr, P, night)
    cx, cy = 0.66 * W, 0.60 * H
    roles = ["ridge1", "water", "cloud", "ridge2", "leaf", "ridge3", "plaster", "ridge4"]
    ang = math.radians(360 / 7 * 5 / 3)               # the 7:5 step turned into a quarter-turn fraction
    layers = 5
    for L in range(layers):
        n = 9 + L
        L_len = H * (0.95 - 0.12 * L)
        base_rot = L * ang + 0.35
        for i in range(n):
            a = base_rot + 2 * math.pi * i / n
            wid = 0.22 + 0.04 * (i % 3)
            x1, y1 = cx + math.cos(a) * L_len, cy + math.sin(a) * L_len
            nx, ny = -math.sin(a), math.cos(a)
            w = L_len * wid
            curl = 0.22 * L_len
            c1 = (cx + math.cos(a) * L_len * 0.45 + nx * (w + curl), cy + math.sin(a) * L_len * 0.45 + ny * (w + curl))
            c2 = (cx + math.cos(a) * L_len * 0.45 - nx * (w - curl), cy + math.sin(a) * L_len * 0.45 - ny * (w - curl))
            x1, y1 = x1 + nx * curl * 0.6, y1 + ny * curl * 0.6
            d = f"M{f(cx)} {f(cy)}Q{f(c1[0])} {f(c1[1])} {f(x1)} {f(y1)}Q{f(c2[0])} {f(c2[1])} {f(cx)} {f(cy)}Z"
            role = roles[(i * 3 + L * 2) % len(roles)]
            g = rad(doc, [(0, P[role], 0.0), (0.18, P[role], 0.55), (1, P[role], 0.05)], (cx, cy), L_len)
            flt = f' filter="{blurf(doc, fr.l(18))}"' if L == 0 else ""
            doc.add(f'<path d="{d}" fill="{g}"{flt}/>')
            if L >= 2:
                doc.add(f'<path d="M{f(cx)} {f(cy)}Q{f(c1[0])} {f(c1[1])} {f(x1)} {f(y1)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 2)}" opacity="0.25"/>')
    landing_glow(doc, fr, P, cx, cy, 0.22 * H)
    doc.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(fr.l(26))}" fill="{P["lightc"]}" opacity="0.9"/>')


def form_dunes(doc, fr, P):
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    backdrop(doc, fr, P, night)
    names = [("ridge1", "fog"), ("ridge2", "ridge1"), ("ridge3", "ridge2"), ("ridge4", "ridge3"), ("plaster2", "ridge4"), ("roofb", "ridge4")]
    base = [0.36, 0.47, 0.58, 0.69, 0.81, 0.93]
    rnd = random.Random(4)
    for i, ((a, b), y0) in enumerate(zip(names, base)):
        ph = rnd.random()
        pts = []
        n = 40
        for k in range(n + 1):
            u = k / n
            y = y0 * H + H * (0.07 * math.sin(2 * math.pi * (0.75 * u + ph)) + 0.025 * math.sin(2 * math.pi * (1.9 * u + 2 * ph))) - H * 0.07 * (1 - u) * (1 if i % 2 == 0 else -0.6)
            pts.append((u * W * 1.1 - 0.05 * W, y))
        line = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts)
        d = line + f"L{f(pts[-1][0])} {f(H * 1.05)}L{f(pts[0][0])} {f(H * 1.05)}Z"
        top = min(p[1] for p in pts)
        g = lin(doc, [(0, P[a], 1), (0.55, P[b], 1), (1, P[b], 1)], (0, top), (0, y0 * H + 0.25 * H))
        cast = doc.id("dc")
        doc.defs.append(f'<clipPath id="{cast}"><path d="{d}"/></clipPath>')
        doc.add(f'<path d="{d}" fill="{g}"/>')
        rip = "".join(f'<path d="{line}" transform="translate(0 {f(k * fr.l(26))})"/>' for k in range(1, 9))
        doc.add(f'<g clip-path="url(#{cast})"><g fill="none" stroke="{P["lit"]}" stroke-width="{f(max(1.5, fr.s * 2))}" opacity="0.16">{rip}</g></g>'
                f'<path d="{line}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 3)}" opacity="0.5"/>')
        mist(doc, fr, P, y0 - 0.05, 0.05, opacity=0.5, seed=i + 3)
    # the dragon vein: a stream of light through the folds, bending once before it lands
    land = (0.72, 0.72)
    pts = streamline(-0.05, 0.30, land)
    g = lin(doc, [(0, P["lightc"], 1), (1, P["gold"], 1)], (pts[0][0] * W, pts[0][1] * H), (pts[-1][0] * W, pts[-1][1] * H))
    veil_from(doc, fr, P, pts, g, 0.05, 0.55, blur=fr.l(14), hair=False)
    veil_from(doc, fr, P, pts, g, 0.022, 0.85)
    landing_glow(doc, fr, P, 0.72 * W, 0.72 * H, 0.16 * H)


def form_twist(doc, fr, P):
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    backdrop(doc, fr, P, night)
    ctrl = [(-0.08 * W, 0.18 * H), (0.30 * W, 0.02 * H), (0.34 * W, 0.80 * H), (0.62 * W, 0.58 * H), (0.80 * W, 0.46 * H), (1.08 * W, 0.84 * H)]
    pts = bez(ctrl, 30)
    line = resample(pts, 220)

    def tones(role_a, role_b, n=9):
        out = []
        for i in range(n):
            u = i / (n - 1)
            out.append(lin(doc, [(0, P[role_a], 1), (1, P[role_b], 1)], (0, 0), (1, 1)) if False else None)
        return out
    ca = [P[r] for r in ("plaster", "cloud", "ridge1", "water")]
    cb = [P[r] for r in ("ridge3", "ridge4", "roofa", "roofb")]
    for (width, turns, off, opac, lit_cols, shd_cols, blur) in ((0.16, 1.6, 0.0, 0.95, ca, cb, 0), (0.10, 2.2, 0.6, 0.55, [P["leaf"], P["ridge2"]], [P["ridge4"], P["roofc"]], 0), (0.2, 1.1, 0.3, 0.3, [P["water"]], [P["ridge2"]], fr.l(26))):
        strips_l, strips_s = [], []
        n = len(line) - 1
        for i in range(n):
            u = i / n
            th = 2 * math.pi * (turns * u + off)
            c = math.cos(th)
            x, y = line[i]
            x2, y2 = line[i + 1]
            dx, dy = x2 - x, y2 - y
            ln = math.hypot(dx, dy) or 1
            nx, ny = -dy / ln, dx / ln
            wd = width * H * (math.sin(math.pi * min(1, u * 1.05)) ** 0.5) * (0.12 + 0.88 * abs(c))
            wd2 = width * H * (math.sin(math.pi * min(1, (u + 1 / n) * 1.05)) ** 0.5) * (0.12 + 0.88 * abs(math.cos(2 * math.pi * (turns * (u + 1 / n) + off))))
            q = f"M{f(x - nx * wd / 2)} {f(y - ny * wd / 2)}L{f(x2 - nx * wd2 / 2)} {f(y2 - ny * wd2 / 2)}L{f(x2 + nx * wd2 / 2)} {f(y2 + ny * wd2 / 2)}L{f(x + nx * wd / 2)} {f(y + ny * wd / 2)}Z"
            (strips_l if c >= 0 else strips_s).append((q, abs(c)))
        flt = f' filter="{blurf(doc, blur)}"' if blur else ""
        doc.add(f'<g opacity="{f(opac)}"{flt}>')
        for strips, cols in ((strips_s, shd_cols), (strips_l, lit_cols)):
            buckets = {}
            for q, a in strips:
                k = min(len(cols) - 1, int((1 - a) * len(cols)))
                buckets.setdefault(k, []).append(q)
            for k, qs in buckets.items():
                doc.add(f'<path d="{"".join(qs)}" fill="{cols[k]}" stroke="{cols[k]}" stroke-width="1"/>')
        doc.add("</g>")
    landing_glow(doc, fr, P, 0.80 * W, 0.52 * H, 0.17 * H)


def form_family(doc, fr, P, fam):
    """Veils laid along the streamlines of one flow family; reading line in the caption."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    backdrop(doc, fr, P, night)
    F = FAMILIES[fam]
    land = (0.72, 0.70)
    pairs = [("ridge1", "fog"), ("cloud", "ridge1"), ("ridge2", "ridge1"), ("plaster", "ridge2"), ("water", "ridge3"), ("leaf", "water"),
             ("ridge3", "ridge4"), ("ridge4", "roofb"), ("cloud", "water"), ("ridge2", "ridge1"), ("plaster", "ridge2"), ("leaf", "ridge3"), ("ridge4", "ridge3")]
    n = F["n"]
    rnd = random.Random(len(fam) * 7 + 1)
    for i in range(n):
        u = i / max(1, n - 1)
        if i % 3 == 2:
            x0, y0 = 0.05 + 0.5 * u, -0.05
        else:
            x0, y0 = -0.05, 0.02 + 0.9 * u
        pts = streamline(x0, y0, land, fam=fam)
        a, b = pairs[i % len(pairs)]
        g = lin(doc, [(0, P[a], 1), (1, P[b], 1)], (pts[0][0] * W, pts[0][1] * H), (pts[-1][0] * W, pts[-1][1] * H))
        th = (0.12 + 0.2 * rnd.random()) * F["th"]
        veil_from(doc, fr, P, pts, g, th, 0.45 + 0.35 * u, blur=fr.l(24) if i == 0 else 0)
    for y0 in (0.2, 0.35, 0.5, 0.65):
        pts = streamline(-0.05, y0, land, fam=fam)
        doc.add(f'<path d="M{" L".join(f"{f(x * W)} {f(y * H)}" for x, y in pts)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 2)}" opacity="0.3"/>')
    landing_glow(doc, fr, P, land[0] * W, land[1] * H, 0.2 * H)
    for r_ in (21, 42, 84):
        doc.add(f'<circle cx="{f(land[0] * W)}" cy="{f(land[1] * H)}" r="{f(r_ * FEN * fr.s * 3)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 2)}" opacity="0.3"/>')


READING = {
    "fold": "entra pela luz NO, contorna a dobra no meio, pousa no SE",
    "vortex": "entra pela luz NO e gira em espiral, fechando no SE",
    "pair": "entra pela luz NO, desce por uma curva em S entre dois redemoinhos, pousa no SE",
    "braid": "entra pela luz NO em fios que se cruzam, trançam e pousam juntos no SE",
    "meander": "entra pela luz NO, serpenteia pelo vazio e pousa no SE",
    "lattice": "entra pela luz NO em fios paralelos, curva uma vez no centro calmo e pousa no SE",
    "dunes": "entra pela luz NO como veio de luz, atravessa as dobras das dunas e pousa no SE",
    "bloom": "entra pela luz NO e as pétalas giram em torno do pouso no SE",
}
FAMILY_ORDER = ["fold", "vortex", "pair", "meander", "braid", "lattice", "dunes", "bloom"]


# ---------------------------------------------------------------- signature candidates
def juzhe_curve(x0, y0, x1, y1, flick):
    """The raise-and-fold of the Yingzao fashi from the ridge (x0, y0) to the eave (x1, y1), then the
    eave's own turn-up (qiao): steep, folding, flat, and a last lift. Points in frame fractions."""
    from geom import juzhe
    pts = juzhe(x0, y0, x1, y1, purlins=7, first=0.32)
    pts = bez(pts, 6)
    x, y = pts[-1]
    pts += [(x + 0.03, y - flick * 0.15), (x + 0.06, y - flick * 0.55), (x + 0.085, y - flick)]
    return pts


def form_sig_juzhe(doc, fr, P):
    """Signature A, the lifted eave. Reading: falls from the light NO in a fold (juzhe), flattens across the
    middle and lands in the lifted eave at the SE."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    backdrop(doc, fr, P, night)
    pairs = [("ridge1", "fog"), ("cloud", "ridge1"), ("ridge2", "ridge1"), ("water", "ridge3"), ("plaster", "ridge2"), ("leaf", "water"),
             ("ridge3", "ridge4"), ("ridge4", "roofb"), ("cloud", "water"), ("ridge2", "ridge3"), ("plaster", "ridge2"), ("ridge4", "ridge3")]
    n = 12
    for i in range(n):
        u = i / (n - 1)
        pts = juzhe_curve(-0.05 + 0.14 * u, -0.04 + 0.05 * u, 0.62 + 0.10 * u, 0.62 + 0.22 * u, 0.10 + 0.05 * u)
        a, b = pairs[i % len(pairs)]
        g = lin(doc, [(0, P[a], 1), (1, P[b], 1)], (pts[0][0] * W, pts[0][1] * H), (pts[-1][0] * W, pts[-1][1] * H))
        veil_from(doc, fr, P, pts, g, 0.10 + 0.07 * (1 - abs(u - 0.5) * 2), 0.42 + 0.4 * u, blur=fr.l(26) if i == 0 else 0)
        if i % 3 == 1:   # tile ribs: short ticks across the band every 21 fen
            m = resample([(x * W, y * H) for x, y in pts], 70)
            ticks = []
            for k in range(2, len(m) - 2):
                q, p0 = m[k + 1], m[k - 1]
                dx, dy = q[0] - p0[0], q[1] - p0[1]
                ln = math.hypot(dx, dy) or 1
                nx, ny = -dy / ln, dx / ln
                wd = 0.05 * H * (math.sin(math.pi * k / len(m)) ** 1.2)
                ticks.append(f"M{f(m[k][0] - nx * wd)} {f(m[k][1] - ny * wd)}L{f(m[k][0] + nx * wd)} {f(m[k][1] + ny * wd)}")
            doc.add(f'<path d="{"".join(ticks)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 1.6)}" opacity="0.3"/>')
    landing_glow(doc, fr, P, 0.80 * W, 0.70 * H, 0.2 * H)
    for r_ in (21, 42, 84):
        doc.add(f'<circle cx="{f(0.80 * W)}" cy="{f(0.70 * H)}" r="{f(r_ * FEN * fr.s * 3)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(fr.s * 2)}" opacity="0.3"/>')


def form_sig_gate(doc, fr, P):
    """Signature C, the gate in the flow. Reading: enters by the light NO, parts around the round void
    (xu) and closes behind it, landing in the gold at the SE; the circle is the moon gate."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    backdrop(doc, fr, P, night)
    asp = W / H
    c = (0.58, 0.54)
    R = 0.20                                       # in heights
    land = (0.80, 0.72)

    def field(x, y):
        ex, ey = 0.86, 0.50
        ln = math.hypot(ex, ey)
        ex, ey = ex / ln, ey / ln
        rx, ry = (x - c[0]) * asp, (y - c[1])      # in height units
        r2 = rx * rx + ry * ry
        r = math.sqrt(r2) or 1e-3
        dot = ex * rx / r + ey * ry / r
        k = R * R / r2
        vx = ex - k * (2 * dot * rx / r - ex)
        vy = ey - k * (2 * dot * ry / r - ey)
        dx, dy = (land[0] - x) * asp, land[1] - y
        d = math.hypot(dx, dy) or 1
        vx += 0.45 * dx / d
        vy += 0.45 * dy / d
        n = math.hypot(vx, vy) or 1
        return vx / n, vy / n

    pairs = [("ridge1", "fog"), ("cloud", "ridge1"), ("ridge2", "ridge1"), ("water", "ridge3"), ("plaster", "ridge2"), ("leaf", "water"),
             ("ridge3", "ridge4"), ("ridge4", "roofb"), ("cloud", "water"), ("ridge2", "ridge3"), ("plaster", "ridge2"), ("leaf", "ridge3"), ("ridge4", "ridge3")]
    n = 14
    for i in range(n):
        u = i / (n - 1)
        x, y = (-0.05, 0.02 + 0.95 * u) if i % 3 else (0.04 + 0.5 * u, -0.05)
        pts = [(x, y)]
        for _ in range(240):
            vx, vy = field(x, y)
            x += vx * 0.010 / asp
            y += vy * 0.010
            if math.hypot((x - c[0]) * asp, y - c[1]) < R * 1.03:
                x += (x - c[0]) * 0.03
                y += (y - c[1]) * 0.03
            pts.append((x, y))
            if math.hypot((x - land[0]) * asp, y - land[1]) < 0.04 or x > 1.08 or y > 1.1:
                break
        a, b = pairs[i % len(pairs)]
        g = lin(doc, [(0, P[a], 1), (1, P[b], 1)], (pts[0][0] * W, pts[0][1] * H), (pts[-1][0] * W, pts[-1][1] * H))
        veil_from(doc, fr, P, pts, g, (0.08 + 0.1 * (1 - abs(u - 0.5) * 2)), 0.42 + 0.35 * u, blur=fr.l(26) if i == 0 else 0)
    # the gate: a void lit from within, a ring of voussoirs, the gold at the lower right inside
    cx, cy, Rp = c[0] * W, c[1] * H, R * H
    gl = rad(doc, [(0, P["lightc"], 0.9), (0.5, P["fog"], 0.75), (1, P["sky1"], 0.9)], (cx - 0.25 * Rp, cy - 0.3 * Rp), Rp * 1.2)
    doc.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(Rp)}" fill="{gl}"/>')
    ring = "".join(f"M{f(cx + Rp * math.cos(math.radians(a)))} {f(cy + Rp * math.sin(math.radians(a)))}L{f(cx + Rp * 1.07 * math.cos(math.radians(a)))} {f(cy + Rp * 1.07 * math.sin(math.radians(a)))}" for a in range(0, 360, 6))
    doc.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(Rp * 1.035)}" fill="none" stroke="{P["lit"]}" stroke-width="{f(Rp * 0.07)}" opacity="0.55"/>'
            f'<path d="{ring}" stroke="{P["shade"]}" stroke-width="{f(fr.s * 2)}" opacity="0.4"/>')
    landing_glow(doc, fr, P, land[0] * W, land[1] * H, 0.2 * H)
    doc.add(f'<circle cx="{f(cx + 0.35 * Rp)}" cy="{f(cy + 0.40 * Rp)}" r="{f(Rp * 0.5)}" fill="{rad(doc, [(0, P["gold"], 0.7), (1, P["gold"], 0)], (cx + 0.35 * Rp, cy + 0.4 * Rp), Rp * 0.5)}"/>')


# ---------------------------------------------------------------- contemporary register (matte)
def grain(doc, fr, P, opacity=0.12, seed=3):
    """Paper grain: one small tile of tiny light and dark specks, repeated over the frame."""
    rnd = random.Random(seed)
    s = 192
    dots = "".join(f'<circle cx="{f(rnd.uniform(0, s))}" cy="{f(rnd.uniform(0, s))}" r="{f(rnd.uniform(0.5, 1.3))}" fill="{P["lit"] if rnd.random() < 0.5 else P["shade"]}" opacity="{f(rnd.uniform(0.3, 1.0))}"/>' for _ in range(260))
    i = doc.id("gr")
    doc.defs.append(f'<pattern id="{i}" patternUnits="userSpaceOnUse" width="{s}" height="{s}">{dots}</pattern>')
    doc.add(f'<rect width="{fr.w}" height="{fr.h}" fill="url(#{i})" opacity="{f(opacity)}"/>')


def matte_backdrop(doc, fr, P):
    """A long, low-contrast diagonal gradient and one very wide soft light at the upper left. No disc."""
    W, H = fr.w, fr.h
    night = P["_name"] == "night"
    ks = [(-6, 3), (-8, 3.5), (-10, 4)] if night else [(20, 2), (18, 3), (16, 4)]
    cols = [K.derive(k, c, K.hue_of("base", K.BASE), K.BASE) for k, c in ks]
    doc.add(f'<rect width="{W}" height="{H}" fill="{lin(doc, [(0, cols[0], 1), (0.6, cols[1], 1), (1, cols[2], 1)], (0, 0), (W * 0.55, H * 1.1))}"/>')
    g = rad(doc, [(0, P["glow"], 0.55), (0.5, P["glow"], 0.16), (1, P["glow"], 0)], (0.10 * W, 0.08 * H), 0.85 * H)
    doc.add(f'<rect width="{W}" height="{H}" fill="{g}"/>')


def sheet(doc, fr, P, pts, thick, ca, cb, shadow=0.16, opacity=1.0, blur=0, fibres=84, seed=1):
    """A matte sheet laid along a path, full width where it enters, fading on the landing. A soft coloured
    shadow beneath lifts it like cut paper; inside, fibres run along the flow (fine lines of varying
    weight, light on the lit side and shade on the other) so the field has a micro-texture. No outline,
    no highlight, no gloss."""
    W, H = fr.w, fr.h
    rnd = random.Random(seed)
    m = resample([(x * W, y * H) for x, y in pts], 56)
    nrm = []
    for i in range(len(m)):
        q, p0 = m[min(i + 1, len(m) - 1)], m[max(i - 1, 0)]
        dx, dy = q[0] - p0[0], q[1] - p0[1]
        ln = math.hypot(dx, dy) or 1
        nrm.append((-dy / ln, dx / ln))

    def edge(off):
        out = []
        for i, ((x, y), (nx, ny)) in enumerate(zip(m, nrm)):
            u = i / (len(m) - 1)
            w = thick * H * (1 - 0.35 * u ** 2)
            out.append((x + nx * w * off, y + ny * w * off))
        return out

    top, bot = edge(0.5), edge(-0.5)
    d = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + f"L{f(bot[-1][0])} {f(bot[-1][1])}" + smooth(bot[::-1]) + "Z"
    if shadow:
        doc.add(f'<path d="{d}" transform="translate({f(fr.l(14))} {f(fr.l(28))})" fill="{P["shade"]}" opacity="{f(shadow)}" filter="{blurf(doc, fr.l(26))}"/>')
    g = lin(doc, [(0, ca, 1), (0.7, cb, 1), (1, cb, 0.0)], (m[0][0], m[0][1]), (m[-1][0], m[-1][1]))
    flt = f' filter="{blurf(doc, blur)}"' if blur else ""
    doc.add(f'<path d="{d}" fill="{g}" opacity="{f(opacity)}"{flt}/>')
    if fibres and not blur:
        c = doc.id("sf")
        doc.defs.append(f'<clipPath id="{c}"><path d="{d}"/></clipPath>')
        up = edge(0.5)
        mid = edge(0.12)
        band_up = f"M{f(up[0][0])} {f(up[0][1])}" + smooth(up) + f"L{f(mid[-1][0])} {f(mid[-1][1])}" + smooth(mid[::-1]) + "Z"
        lo, lo2 = edge(-0.5), edge(-0.14)
        band_lo = f"M{f(lo[0][0])} {f(lo[0][1])}" + smooth(lo) + f"L{f(lo2[-1][0])} {f(lo2[-1][1])}" + smooth(lo2[::-1]) + "Z"
        doc.add(f'<g clip-path="url(#{c})"><path d="{band_up}" fill="{P["lit"]}" opacity="0.20" filter="{blurf(doc, fr.l(30))}"/>'
                f'<path d="{band_lo}" fill="{P["shade"]}" opacity="0.18" filter="{blurf(doc, fr.l(30))}"/></g>')
        lit, shd = [], []
        for k in range(fibres):
            off = rnd.uniform(-0.48, 0.48)
            wob = rnd.uniform(0.0, 0.03)
            pts_ = edge(off)
            pts_ = [(x + nx * thick * H * wob * math.sin(i * 0.4 + k), y + ny * thick * H * wob * math.sin(i * 0.4 + k)) for i, ((x, y), (nx, ny)) in enumerate(zip(pts_, nrm))]
            a_, b_ = int(rnd.uniform(0, 14)), int(rnd.uniform(34, 56))
            seg = pts_[a_:b_ + 1]
            ds = "M" + " ".join(f"{f(x)} {f(y)}" if i == 0 else f"L{f(x)} {f(y)}" for i, (x, y) in enumerate(seg))
            sw = fr.s * rnd.choice((1.6, 2.2, 3.0, 4.2))
            (lit if off < 0.05 else shd).append((ds, sw, rnd.uniform(0.16, 0.46)))
        out = [f'<g clip-path="url(#{c})" fill="none" stroke-linecap="round">']
        for col, group in ((P["lit"], lit), (P["shade"], shd)):
            out += [f'<path d="{ds}" stroke="{col}" stroke-width="{f(sw)}" opacity="{f(op)}"/>' for ds, sw, op in group]
        out.append("</g>")
        doc.add("".join(out))


def quiet_accent(doc, fr, P, cx, cy, r):
    g = rad(doc, [(0, P["gold"], 0.5), (0.6, P["gold"], 0.12), (1, P["gold"], 0)], (cx, cy), r)
    doc.add(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(r * 1.5)}" ry="{f(r)}" fill="{g}"/>')


TONES = ["fog", "cloud", "ridge1", "ridge2", "ridge3", "ridge4", "roofb"]


def form_m_juzhe(doc, fr, P):
    """Signature A (matte): the lifted eave. Reading: falls from the light NO in the juzhe fold, flattens
    across the middle and lands in the lifted eave at the SE."""
    W, H = fr.w, fr.h
    matte_backdrop(doc, fr, P)
    L = ladder(P)
    for i in range(5):
        u = i / 4
        pts = juzhe_curve(-0.12 + 0.20 * u, -0.10 + 0.06 * u, 0.60 + 0.12 * u, 0.58 + 0.17 * u, 0.09 + 0.04 * u)
        sheet(doc, fr, P, pts, 0.52 - 0.07 * i, L[i], L[min(4, i + 1)], shadow=0.14, blur=fr.l(8) if i == 0 else 0, seed=i)
        if i == 1:
            haze(doc, fr, P, pts, 0.30)
    threads(doc, fr, P, lambda y0: juzhe_curve(-0.12 + 0.2 * (y0 + 0.12), y0 - 0.05, 0.60 + 0.12 * (y0 + 0.12), 0.40 + 0.5 * y0, 0.08))
    quiet_accent(doc, fr, P, 0.80 * W, 0.70 * H, 0.2 * H)
    grain(doc, fr, P)


def form_m_fold(doc, fr, P):
    """Signature B (matte): the screen fold. Reading: enters by the light NO, turns once around the
    fold in the middle and lands at the SE."""
    W, H = fr.w, fr.h
    matte_backdrop(doc, fr, P)
    L = ladder(P)
    for i, y0 in enumerate((-0.10, 0.05, 0.22, 0.42, 0.62)):
        pts = streamline(-0.12, y0, (0.74, 0.70), fam="fold")
        sheet(doc, fr, P, pts, 0.50 - 0.07 * i, L[i], L[min(4, i + 1)], shadow=0.14, blur=fr.l(8) if i == 0 else 0, seed=i)
        if i == 1:
            haze(doc, fr, P, pts, 0.30)
    threads(doc, fr, P, lambda y0: streamline(-0.12, y0, (0.74, 0.70), fam="fold"))
    quiet_accent(doc, fr, P, 0.74 * W, 0.70 * H, 0.2 * H)
    grain(doc, fr, P)


def form_m_gate(doc, fr, P):
    """Signature C (matte): the gate in the flow. Reading: enters by the light NO, the sheets part around the
    round void (the moon gate) and close behind it, landing at the SE."""
    W, H = fr.w, fr.h
    asp = W / H
    matte_backdrop(doc, fr, P)
    c, R, land = (0.58, 0.54), 0.20, (0.80, 0.72)

    def field(x, y):
        ex, ey = 0.86, 0.50
        ln = math.hypot(ex, ey)
        ex, ey = ex / ln, ey / ln
        rx, ry = (x - c[0]) * asp, (y - c[1])
        r2 = rx * rx + ry * ry
        r = math.sqrt(r2) or 1e-3
        dot = ex * rx / r + ey * ry / r
        k = R * R / r2
        vx = ex - k * (2 * dot * rx / r - ex)
        vy = ey - k * (2 * dot * ry / r - ey)
        dx, dy = (land[0] - x) * asp, land[1] - y
        d = math.hypot(dx, dy) or 1
        vx += 0.45 * dx / d
        vy += 0.45 * dy / d
        n = math.hypot(vx, vy) or 1
        return vx / n, vy / n

    L = ladder(P)
    for i, y0 in enumerate((-0.10, 0.08, 0.28, 0.52, 0.76)):
        x, y = -0.12, y0
        pts = [(x, y)]
        for _ in range(260):
            vx, vy = field(x, y)
            x += vx * 0.010 / asp
            y += vy * 0.010
            if math.hypot((x - c[0]) * asp, y - c[1]) < R * 1.04:
                x += (x - c[0]) * 0.04
                y += (y - c[1]) * 0.04
            pts.append((x, y))
            if math.hypot((x - land[0]) * asp, y - land[1]) < 0.04 or x > 1.1 or y > 1.12:
                break
        sheet(doc, fr, P, pts, 0.40 - 0.05 * i, L[i], L[min(4, i + 1)], shadow=0.14, blur=fr.l(8) if i == 0 else 0, seed=i)
        if i == 1:
            haze(doc, fr, P, pts, 0.26)
    cx, cy, Rp = c[0] * W, c[1] * H, R * H
    doc.add(f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(Rp)}" fill="{lin(doc, [(0, L[0], 1), (1, L[1], 1)], (cx - Rp, cy - Rp), (cx + Rp, cy + Rp))}"/>')
    quiet_accent(doc, fr, P, land[0] * W, land[1] * H, 0.2 * H)
    grain(doc, fr, P)


def ladder(P, steps=5):
    """Muted tones for the matte register, all from the base by derive(): value steps close together,
    chroma low; the last one leans to the water hue as the one quiet second colour."""
    night = P["_name"] == "night"
    ks = [-8, -9.5, -11, -12.5, -14][:steps] if night else [17, 14.5, 12, 9.5, 7][:steps]
    cs = [3, 4, 4.5, 5, 5.5]
    out = [K.derive(k, c, K.hue_of("base", K.BASE), K.BASE) for k, c in zip(ks, cs)]
    out[2] = K.derive(ks[2], 4.5, K.hue_of("water", K.BASE), K.BASE)
    return out


def haze(doc, fr, P, pts, thick, opacity=0.35, seed=2):
    """A soft, wide veil of the lightest tone drifting along a path (depth between two sheets)."""
    W, H = fr.w, fr.h
    m = resample([(x * W, y * H) for x, y in pts], 40)
    top, bot = [], []
    for i, (x, y) in enumerate(m):
        q, p0 = m[min(i + 1, len(m) - 1)], m[max(i - 1, 0)]
        dx, dy = q[0] - p0[0], q[1] - p0[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = thick * H * (math.sin(math.pi * (0.1 + 0.8 * i / (len(m) - 1))))
        top.append((x + nx * w / 2, y + ny * w / 2))
        bot.append((x - nx * w / 2, y - ny * w / 2))
    d = f"M{f(top[0][0])} {f(top[0][1])}" + smooth(top) + f"L{f(bot[-1][0])} {f(bot[-1][1])}" + smooth(bot[::-1]) + "Z"
    doc.add(f'<path d="{d}" fill="{P["cloud"]}" opacity="{f(opacity)}" filter="{blurf(doc, fr.l(46))}"/>')


def threads(doc, fr, P, line_fn, n=64, seed=4):
    """Secondary flow: many thin streamlines of the same field, weights from 1 to 4 px, light and shade."""
    rnd = random.Random(seed)
    W, H = fr.w, fr.h
    out = []
    for k in range(n):
        y0 = -0.12 + 1.1 * (k + rnd.random() * 0.8) / n
        pts = line_fn(y0)
        seg = pts[int(len(pts) * rnd.uniform(0, 0.25)): int(len(pts) * rnd.uniform(0.7, 1.0))]
        if len(seg) < 6:
            continue
        ds = "M" + " ".join(f"{f(x * W)} {f(y * H)}" if i == 0 else f"L{f(x * W)} {f(y * H)}" for i, (x, y) in enumerate(seg))
        col = P["lit"] if k % 3 else P["shade"]
        out.append(f'<path d="{ds}" fill="none" stroke="{col}" stroke-width="{f(fr.s * rnd.choice((1.2, 1.8, 2.6, 3.6, 5.0)))}" opacity="{f(rnd.uniform(0.16, 0.5))}" stroke-linecap="round"/>')
    doc.add("".join(out))
