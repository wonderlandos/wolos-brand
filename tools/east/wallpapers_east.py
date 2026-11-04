# SPDX-License-Identifier: GPL-2.0-or-later
"""Two static wallpaper studies (docs/adr/brand-east.md section 10). 3840 x 2160.

  python3 -I design/tools/east/wallpapers_east.py [outdir]   (default design/east/wallpapers)

Shanshui in three planes (far, middle, near: ground, second plane, first plane, in the area
shares 21 : 15 : 6). One light, upper left: it is the entry of the eye. The qi path is the river:
it comes from behind the far ridge near the light, turns twice (no straight run) and lands in a
pool in the lower-right third, where a small lit door stands (the landing). Ridges are juzhe-like
concave slopes, never straight; nothing straight runs into the frame. Weight sits low (mountain
form): the windows of the desktop keep the calm middle. Colours derive from the base violet:
metal sky, water ridges, one earth light (the door) under the 1/7 accent share.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import calculus as K  # noqa: E402
from geom import smooth, f, rrect  # noqa: E402
from colour import from_oklch, oklch  # noqa: E402

W, H = 3840, 2160
L0, C0, H0 = oklch(K.BASE)
EARTH = K.hue_of("earth")
WOOD = K.hue_of("wood")


def ridge(y_base, amp, seed, peaks, x_shift=0.0, steep=1.6):
    """A ridge line: peaks of different heights joined by concave (juzhe-like) slopes."""
    import random
    rnd = random.Random(seed)
    pts = []
    xs = [x_shift + i * W / peaks for i in range(-1, peaks + 2)]
    tops = [(x + rnd.uniform(-0.25, 0.25) * W / peaks, y_base - amp * rnd.uniform(0.25, 1.0)) for x in xs]
    for (x0, y0), (x1, y1) in zip(tops, tops[1:]):
        xm = (x0 + x1) / 2 + rnd.uniform(-0.12, 0.12) * (x1 - x0)
        ym = y_base - amp * 0.18 * rnd.uniform(0.0, 1.0)
        for t in (0.0, 0.35, 0.7):            # concave descent: fast near the peak, slow at the saddle
            u = 1 - (1 - t) ** steep
            pts.append((x0 + (xm - x0) * t, y0 + (ym - y0) * u))
        for t in (0.3, 0.65):
            u = t ** steep
            pts.append((xm + (x1 - xm) * t, ym + (y1 - ym) * u))
    return [(x, y) for x, y in pts if -W * 0.2 < x < W * 1.2]


def plane(pts, top_c, bot_c, gid, defs):
    defs.append(f'<linearGradient id="{gid}" x1="0.2" y1="0" x2="0.6" y2="1"><stop offset="0" stop-color="{top_c}"/>'
                f'<stop offset="1" stop-color="{bot_c}"/></linearGradient>')
    d = f"M{f(pts[0][0])} {f(pts[0][1])}" + smooth(pts) + f"L{f(pts[-1][0])} {H + 10}L{f(pts[0][0])} {H + 10}Z"
    return f'<path d="{d}" fill="url(#{gid})"/>'


def river(defs, colour, glow):
    """The qi path: a ribbon that widens as it comes near (perspective), two turns, a pool."""
    c = [(1260, 1500), (1560, 1580), (1380, 1690), (1820, 1790), (2440, 1850), (2820, 1905)]
    widths = [14, 30, 52, 80, 120, 150]
    left, right = [], []
    for i, (x, y) in enumerate(c):
        a, b = c[max(0, i - 1)], c[min(len(c) - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        nx, ny = -dy / n * widths[i] / 2, dx / n * widths[i] / 2
        left.append((x + nx, y + ny)); right.append((x - nx, y - ny))
    d = f"M{f(left[0][0])} {f(left[0][1])}" + smooth(left) + f"L{f(right[-1][0])} {f(right[-1][1])}" + smooth(right[::-1]) + "Z"
    pool = f'<ellipse cx="2930" cy="1915" rx="280" ry="58" fill="{colour}"/>'
    defs.append(f'<linearGradient id="rv" x1="0" y1="0" x2="1" y2="0.3"><stop offset="0" stop-color="{glow}"/>'
                f'<stop offset="1" stop-color="{colour}"/></linearGradient>')
    return f'<path d="{d}" fill="url(#rv)"/>' + pool


def door(x, y, h, lit, frame):
    w = h * 0.62
    r = w / 2
    d = f"M{f(x - w / 2)} {f(y)}V{f(y - h + r)}A{f(r)} {f(r)} 0 0 1 {f(x + w / 2)} {f(y - h + r)}V{f(y)}Z"
    w2, r2, h2 = w * 0.62, w * 0.31, h * 0.7
    d2 = f"M{f(x - w2 / 2)} {f(y)}V{f(y - h2 + r2)}A{f(r2)} {f(r2)} 0 0 1 {f(x + w2 / 2)} {f(y - h2 + r2)}V{f(y)}Z"
    spill = f'<ellipse cx="{f(x + h * 0.25)}" cy="{f(y + 12)}" rx="{f(h * 0.9)}" ry="{f(h * 0.12)}" fill="{lit}" opacity="0.35"/>'
    return f'<path d="{d}" fill="{frame}"/><path d="{d2}" fill="{lit}"/>' + spill


def study(mode):
    defs, body = [], []
    night = mode == "night"
    if night:
        sky_a, sky_b = from_oklch(0.30, C0 * 4 / 21, H0), from_oklch(0.16, C0 * 2 / 21, H0)
        light = from_oklch(0.95, C0 * 1 / 21, EARTH)
        ridges = [(0.36, 0.06), (0.30, 0.07), (0.24, 0.08)]
        near_b = from_oklch(0.12, C0 * 2 / 21, H0)
    else:
        sky_a, sky_b = from_oklch(0.985, C0 * 1 / 21, EARTH), from_oklch(0.90, C0 * 2.5 / 21, H0)
        light = from_oklch(0.99, C0 * 2 / 21, EARTH)
        ridges = [(0.84, 0.035), (0.72, 0.06), (0.58, 0.085)]
        near_b = from_oklch(0.40, C0 * 7 / 21, H0)
    defs.append(f'<linearGradient id="sky" x1="0.2" y1="0" x2="0.6" y2="1"><stop offset="0" stop-color="{sky_a}"/>'
                f'<stop offset="1" stop-color="{sky_b}"/></linearGradient>')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    # the light: upper left, the entry; a large soft glow, a small disc (sun or moon)
    defs.append(f'<radialGradient id="glow" cx="0.2" cy="0.16" r="0.6"><stop offset="0" stop-color="{light}" stop-opacity="{0.45 if night else 0.9}"/>'
                f'<stop offset="0.5" stop-color="{light}" stop-opacity="{0.08 if night else 0.18}"/><stop offset="1" stop-color="{light}" stop-opacity="0"/></radialGradient>')
    body.append(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
    body.append(f'<circle cx="760" cy="420" r="{110 if night else 130}" fill="{light}" opacity="{0.95 if night else 0.8}"/>')
    # three planes; each lighter on its left (toward the light)
    bases = [1180, 1420, 1640]
    amps = [300, 380, 260]
    for i, ((L, cf), yb, amp) in enumerate(zip(ridges, bases, amps)):
        pts = ridge(yb, amp, seed=11 + i * 7, peaks=4 - (i == 2), x_shift=i * 380)
        top = from_oklch(L + 0.05, C0 * (cf * 21 / 0.23 if False else 4 + 3 * i) / 21, H0 + (0 if i < 2 else -18))
        bot = from_oklch(L - 0.06 - 0.04 * i, C0 * (3 + 3 * i) / 21, H0)
        body.append(plane(pts, top, bot, f"p{i}", defs))

    # the valley floor, the river (qi path), the pool and the lit door (the landing)
    floor_c = from_oklch(ridges[2][0] - 0.12, C0 * 8 / 21, H0)
    body.append(f'<rect y="1640" width="{W}" height="{H - 1640}" fill="{floor_c}" opacity="0"/>')
    water_c = from_oklch(0.80 if not night else 0.42, C0 * 5 / 21, K.hue_of("water"))
    body.append(river(defs, water_c, light))
    body.append(door(2930, 1905, 190, from_oklch(0.88, C0 * 12 / 21, EARTH), from_oklch(ridges[2][0] - 0.25, C0 * 6 / 21, H0)))
    # the near plane: a mountain anchoring the lower left (the weight sits low, opposite the landing)
    near = [(-200, 1760), (200, 1660), (520, 1610), (900, 1700), (1250, 1900), (1500, 2060), (1700, 2200)]
    d = f"M{f(near[0][0])} {f(near[0][1])}" + smooth(near) + f"L-200 {H + 10}Z"
    defs.append(f'<linearGradient id="pn" x1="0.2" y1="0" x2="0.6" y2="1"><stop offset="0" stop-color="{from_oklch(oklch(near_b)[0] + 0.1, C0 * 6 / 21, H0)}"/><stop offset="1" stop-color="{near_b}"/></linearGradient>')
    body.append(f'<path d="{d}" fill="url(#pn)"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<title>east {"moon gate, night" if night else "courtyard, day"}</title>'
            '<!-- SPDX-License-Identifier: LicenseRef-Wonderland-Brand-1.0. (c) 2026 Julia Klee. WolOS east study. -->'
            f'<defs>{"".join(defs)}</defs>{"".join(body)}</svg>\n')


def main(argv):
    out = argv[0] if argv else os.path.join(HERE, "..", "..", "east", "wallpapers")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "east-courtyard-day.svg"), "w").write(study("day"))
    open(os.path.join(out, "east-moon-gate-night.svg"), "w").write(study("night"))
    print("wrote", os.path.normpath(out))


if __name__ == "__main__":
    main(sys.argv[1:])
