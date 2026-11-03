# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright (c) 2026 Julia Klee
"""Stroke to fill, stdlib only.

stroke(d, width, closed=None) -> SVG path data of the *filled* outline of a stroked path
(round joins, round caps).  Paint the result with fill and a non-zero rule; no SVG stroke
attribute is ever needed, so the drawings are fill-only and render identically everywhere.

d may hold absolute M L H V C Q A Z.  Curves are offset with Hermite cubics (value and
slope of the offset curve at the knots), joins and caps are SVG arcs.
"""
import math


def _f(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------- parsing
def _arc_to_cubics(x1, y1, rx, ry, rot, large, sweep, x2, y2):
    if rx == 0 or ry == 0 or (x1, y1) == (x2, y2):
        return [("L", (x1, y1), (x2, y2))]
    phi = math.radians(rot)
    c, s = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = c * dx + s * dy, -s * dx + c * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        k = math.sqrt(lam)
        rx, ry = rx * k, ry * k
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    co = math.sqrt(max(0.0, num / den)) * (-1 if large == sweep else 1)
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = c * cxp - s * cyp + (x1 + x2) / 2
    cy = s * cxp + c * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    if sweep and dt < 0:
        dt += 2 * math.pi
    n = max(1, math.ceil(abs(dt) / (math.pi / 2) - 1e-9))
    step = dt / n
    k = 4 / 3 * math.tan(step / 4)
    out = []
    pt = lambda t: (cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c)
    dv = lambda t: (-rx * math.sin(t) * c - ry * math.cos(t) * s, -rx * math.sin(t) * s + ry * math.cos(t) * c)
    for i in range(n):
        a, b = t1 + i * step, t1 + (i + 1) * step
        p0, p3 = pt(a), pt(b)
        d0, d3 = dv(a), dv(b)
        p0 = (x1, y1) if i == 0 else p0
        p3 = (x2, y2) if i == n - 1 else p3
        out.append(("C", p0, (p0[0] + k * d0[0], p0[1] + k * d0[1]), (p3[0] - k * d3[0], p3[1] - k * d3[1]), p3))
    return out


def parse(d):
    """-> list of (segments, closed).  A segment is ('L', p0, p1) or ('C', p0, c1, c2, p1)."""
    import re
    if re.search(r"[a-df-zA-Z]", re.sub(r"[MLHVCQAZ]", "", d)):
        raise ValueError("outline.parse takes absolute M L H V C Q A Z only: " + d[:40])
    toks = re.findall(r"[MLHVCQAZ]|-?\d*\.?\d+(?:e-?\d+)?", d)
    i, subs, cur, pos, start, cmd = 0, [], None, (0, 0), (0, 0), None

    def num(n):
        nonlocal i
        v = [float(t) for t in toks[i:i + n]]
        i += n
        return v

    while i < len(toks):
        if toks[i] in "MLHVCQAZ" and not toks[i][0].isdigit():
            cmd = toks[i]
            i += 1
            if cmd == "Z":
                if cur is not None:
                    if pos != start:
                        cur.append(("L", pos, start))
                    subs.append((cur, True))
                    cur, pos = None, start
                continue
        if cmd == "M":
            if cur:
                subs.append((cur, False))
            pos = start = tuple(num(2))
            cur = []
            cmd = "L"
        elif cmd == "L":
            p = tuple(num(2)); cur.append(("L", pos, p)); pos = p
        elif cmd == "H":
            p = (num(1)[0], pos[1]); cur.append(("L", pos, p)); pos = p
        elif cmd == "V":
            p = (pos[0], num(1)[0]); cur.append(("L", pos, p)); pos = p
        elif cmd == "C":
            a, b, c2, e, f, g = num(6)
            cur.append(("C", pos, (a, b), (c2, e), (f, g))); pos = (f, g)
        elif cmd == "Q":
            a, b, e, f = num(4)
            c1 = (pos[0] + 2 / 3 * (a - pos[0]), pos[1] + 2 / 3 * (b - pos[1]))
            c2 = (e + 2 / 3 * (a - e), f + 2 / 3 * (b - f))
            cur.append(("C", pos, c1, c2, (e, f))); pos = (e, f)
        elif cmd == "A":
            rx, ry, rot, la, sw, x, y = num(7)
            cur.extend(_arc_to_cubics(pos[0], pos[1], rx, ry, rot, int(la), int(sw), x, y)); pos = (x, y)
        else:
            raise ValueError(f"unsupported path command {cmd!r}")
    if cur:
        subs.append((cur, False))
    return [(s, c) for s, c in subs if s]


# ---------------------------------------------------------------- geometry
def _eval(seg, t):
    if seg[0] == "L":
        (x0, y0), (x1, y1) = seg[1], seg[2]
        return (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t), (x1 - x0, y1 - y0), (0.0, 0.0)
    p0, p1, p2, p3 = seg[1:]
    u = 1 - t
    x = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
    y = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
    dx = 3 * (u * u * (p1[0] - p0[0]) + 2 * u * t * (p2[0] - p1[0]) + t * t * (p3[0] - p2[0]))
    dy = 3 * (u * u * (p1[1] - p0[1]) + 2 * u * t * (p2[1] - p1[1]) + t * t * (p3[1] - p2[1]))
    ax = 6 * (u * (p2[0] - 2 * p1[0] + p0[0]) + t * (p3[0] - 2 * p2[0] + p1[0]))
    ay = 6 * (u * (p2[1] - 2 * p1[1] + p0[1]) + t * (p3[1] - 2 * p2[1] + p1[1]))
    return (x, y), (dx, dy), (ax, ay)


def _tangent(seg, end):
    """Unit tangent at the start (end=False) or end of a segment (handles zero-length handles)."""
    if seg[0] == "L":
        v = (seg[2][0] - seg[1][0], seg[2][1] - seg[1][1])
    else:
        p0, p1, p2, p3 = seg[1:]
        cands = [(p3[0] - p2[0], p3[1] - p2[1]), (p3[0] - p1[0], p3[1] - p1[1]), (p3[0] - p0[0], p3[1] - p0[1])] if end \
            else [(p1[0] - p0[0], p1[1] - p0[1]), (p2[0] - p0[0], p2[1] - p0[1]), (p3[0] - p0[0], p3[1] - p0[1])]
        v = next((c for c in cands if math.hypot(*c) > 1e-9), (1.0, 0.0))
    n = math.hypot(*v) or 1.0
    return (v[0] / n, v[1] / n)


def _reverse(segs):
    out = []
    for s in reversed(segs):
        out.append(("L", s[2], s[1]) if s[0] == "L" else ("C", s[4], s[3], s[2], s[1]))
    return out


def _normal(t):
    return (-t[1], t[0])


def _offset_seg(seg, h):
    """Path commands (after the start point) for seg offset by +h along rot90(tangent)."""
    if seg[0] == "L":
        n = _normal(_tangent(seg, False))
        return [f"L{_f(seg[2][0] + n[0] * h)} {_f(seg[2][1] + n[1] * h)}"]
    # split so that each piece turns by at most ~35 degrees
    a0, a1 = _tangent(seg, False), _tangent(seg, True)
    turn = abs(math.atan2(a0[0] * a1[1] - a0[1] * a1[0], a0[0] * a1[0] + a0[1] * a1[1]))
    chord = math.hypot(seg[4][0] - seg[1][0], seg[4][1] - seg[1][1])
    n = max(2, math.ceil(turn / math.radians(35)) + (1 if chord > 8 * abs(h) else 0))
    cmds = []
    prev = None
    for k in range(n + 1):
        t = k / n
        p, dv, ac = _eval(seg, t)
        sp = math.hypot(*dv)
        if sp < 1e-9:
            dv, sp = _tangent(seg, t > 0.5), 1.0
            ac = (0.0, 0.0)
        nx, ny = -dv[1] / sp, dv[0] / sp
        # d(unit normal)/dt = rot90((a*sp^2 - v*(v.a)) / sp^3)
        va = dv[0] * ac[0] + dv[1] * ac[1]
        qx, qy = (ac[0] * sp * sp - dv[0] * va) / sp ** 3, (ac[1] * sp * sp - dv[1] * va) / sp ** 3
        pt = (p[0] + nx * h, p[1] + ny * h)
        vel = (dv[0] - qy * h, dv[1] + qx * h)      # offset curve velocity per unit t
        if prev is not None:
            dt = 1 / n
            c1 = (prev[0][0] + prev[1][0] * dt / 3, prev[0][1] + prev[1][1] * dt / 3)
            c2 = (pt[0] - vel[0] * dt / 3, pt[1] - vel[1] * dt / 3)
            cmds.append(f"C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(pt[0])} {_f(pt[1])}")
        prev = (pt, vel)
    return cmds


def _start_pt(seg, h):
    n = _normal(_tangent(seg, False))
    return seg[1][0] + n[0] * h, seg[1][1] + n[1] * h


def _join(a, b, h):
    """Commands joining the offset end of segment a to the offset start of b (offset +h)."""
    v = a[-1]
    t1, t2 = _tangent(a, True), _tangent(b, False)
    cross = t1[0] * t2[1] - t1[1] * t2[0]
    dot = t1[0] * t2[0] + t1[1] * t2[1]
    n2 = _normal(t2)
    s = (v[0] + n2[0] * h, v[1] + n2[1] * h)
    if abs(cross) < 2e-3 and dot > 0:
        return [f"L{_f(s[0])} {_f(s[1])}"]
    if cross < 0:   # outer side: round join
        return [f"A{_f(h)} {_f(h)} 0 0 0 {_f(s[0])} {_f(s[1])}"]
    return [f"L{_f(v[0])} {_f(v[1])}", f"L{_f(s[0])} {_f(s[1])}"]     # inner side: through the pivot


def _side(segs, h, closed):
    """One side of the stroke as path commands starting with M (open: no close)."""
    p = _start_pt(segs[0], h)
    out = [f"M{_f(p[0])} {_f(p[1])}"]
    for i, s in enumerate(segs):
        out += _offset_seg(s, h)
        if i + 1 < len(segs):
            out += _join(s, segs[i + 1], h)
        elif closed:
            out += _join(s, segs[0], h)
    return out


def _cap(seg_end, h, butt=False):
    """Round (or butt) cap at the end of a stroke; ends on the opposite offset."""
    v = seg_end[-1]
    n = _normal(_tangent(seg_end, True))
    if butt:
        return [f"L{_f(v[0] - n[0] * h)} {_f(v[1] - n[1] * h)}"]
    return [f"A{_f(h)} {_f(h)} 0 0 0 {_f(v[0] - n[0] * h)} {_f(v[1] - n[1] * h)}"]


def stroke(d, width, closed=None, butt=False):
    h = width / 2
    out = []
    for segs, is_closed in parse(d):
        if closed is not None:
            is_closed = closed
        segs = [s for s in segs if not (s[0] == "L" and s[1] == s[2])]
        if not segs:
            continue
        if is_closed:
            if segs[-1][-1] != segs[0][1]:
                segs.append(("L", segs[-1][-1], segs[0][1]))
            out += _side(segs, h, True) + ["Z"]
            out += _side(_reverse(segs), h, True) + ["Z"]
        else:
            rev = _reverse(segs)
            body = _side(segs, h, False) + _cap(segs[-1], h, butt)
            back = _side(rev, h, False)
            back[0] = "L" + back[0][1:]
            out += body + back + _cap(rev[-1], h, butt) + ["Z"]
    return "".join(out)


# ---------------------------------------------------------------- helpers
def rect_d(x, y, w, h, r=0):
    r = min(r, w / 2, h / 2)
    if r <= 0:
        return f"M{_f(x)} {_f(y)}H{_f(x + w)}V{_f(y + h)}H{_f(x)}Z"
    return (f"M{_f(x + r)} {_f(y)}H{_f(x + w - r)}A{_f(r)} {_f(r)} 0 0 1 {_f(x + w)} {_f(y + r)}V{_f(y + h - r)}"
            f"A{_f(r)} {_f(r)} 0 0 1 {_f(x + w - r)} {_f(y + h)}H{_f(x + r)}A{_f(r)} {_f(r)} 0 0 1 {_f(x)} {_f(y + h - r)}"
            f"V{_f(y + r)}A{_f(r)} {_f(r)} 0 0 1 {_f(x + r)} {_f(y)}Z")


def ellipse_d(cx, cy, rx, ry):
    return (f"M{_f(cx - rx)} {_f(cy)}A{_f(rx)} {_f(ry)} 0 1 1 {_f(cx + rx)} {_f(cy)}"
            f"A{_f(rx)} {_f(ry)} 0 1 1 {_f(cx - rx)} {_f(cy)}Z")


def circle_d(cx, cy, r):
    return ellipse_d(cx, cy, r, r)


def flatten(d, steps=48):
    """Polyline points per subpath, for dashing."""
    out = []
    for segs, closed in parse(d):
        pts = [segs[0][1]]
        for s in segs:
            n = 1 if s[0] == "L" else steps
            pts += [_eval(s, k / n)[0] for k in range(1, n + 1)]
        out.append(pts)
    return out


def dashes(d, on, off, shift=0.0):
    """Cut the first subpath of d into dashes -> list of (x, y) polylines.  Like SVG
    stroke-dasharray "on off" with stroke-dashoffset = shift."""
    pts = flatten(d)[0]
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = cum[-1]
    at = lambda s: next(((a[0] + (b[0] - a[0]) * (s - c0) / (c1 - c0), a[1] + (b[1] - a[1]) * (s - c0) / (c1 - c0))
                         for a, b, c0, c1 in zip(pts, pts[1:], cum, cum[1:]) if c1 > c0 and s <= c1 + 1e-9), pts[-1])
    period = on + off
    out = []
    k = math.floor(shift / period) if shift else 0
    s0 = -shift + k * period
    while s0 < total:
        s1 = s0 + on
        a, b = max(s0, 0.0), min(s1, total)
        if b > a:
            run = [at(a)] + [p for p, c in zip(pts, cum) if a < c < b] + [at(b)]
            out.append(run)
        s0 += period
    return out


def polyline_d(run):
    return "M" + "L".join(f"{_f(x)} {_f(y)}" for x, y in run)
