# SPDX-License-Identifier: GPL-2.0-or-later
"""Measure an original (upstream) icon before it is redrawn in Type A2.

  python3 -I design/tools/brand/measure.py ICON.svg|png [...] [--kind icon] [--json] [--sheet OUT.png]

For each file it prints what the eye takes from the icon, on the 24-fen canvas:
  silhouette  art box in fen, fill ratio of the filled silhouette, whether it sits on a card
              (a rounded square that fills most of its box) or is a free shape
  colours     the dominant colours (k-means in OKLab) with their share and phase (element)
  mass        the centre of visual mass (salience-weighted, score.Px) against the optical centre
              (0.5, 0.47) used by the density rule
  zones       the nine-square (luoshu) salience weights, as score.r_zones sees them
  brand score  the eight rules and the total (score.score_pixels, same as score.py)
The reading (art box, palette, parts) comes from read_icon.read; this tool adds the mass, the
zones and the score, so the original and the A2 redraw are compared on one scale."""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import read_icon as R  # noqa: E402
import score as SC  # noqa: E402


def measure(path, kind="icon", size=256):
    r = R.read(path, size)
    arr = SC.load(path, size)
    p = SC.Px(arr, kind)
    w = p.sal * p.mask
    tot = w.sum() or 1.0
    ys, xs = np.mgrid[0:p.h, 0:p.w]
    centre = (float((w * xs).sum() / tot / p.w), float((w * ys).sum() / tot / p.h))
    zones = np.array(SC._zones(p)).reshape(3, 3)
    x0, y0, x1, y1 = r["box_fen"]
    box_area = (x1 - x0) * (y1 - y0)
    on_card = r["fill"] > 0.86 and abs((x1 - x0) - (y1 - y0)) < 1.5
    s = SC.score_pixels(path, kind)
    s["total"] = SC.total(s)
    return {"file": path, "box_fen": r["box_fen"], "box_area_fen2": round(box_area, 1), "fill": r["fill"],
            "card": bool(on_card), "palette": [(round(a, 3), hx, el) for a, hx, el in r["palette"]],
            "parts": [(round(a, 3), hx, b, c) for a, hx, b, c in r["parts"]],
            "mass_centre": tuple(round(v, 3) for v in centre),
            "mass_offset": round(float(np.hypot(centre[0] - 0.5, (centre[1] - 0.47))), 3),
            "zones": zones.round(3).tolist(), "score": {k: s[k]["score"] for k in SC.RULES}, "total": s["total"]}


def show(m):
    print(f"== {os.path.basename(m['file'])}")
    print(f"silhouette  box {m['box_fen']} fen ({m['box_area_fen2']} fen2), fill {m['fill']}, {'card' if m['card'] else 'free shape'}")
    print("colours     " + ", ".join(f"{hx} {el} {a:.0%}" for a, hx, el in m["palette"]))
    print(f"mass        centre ({m['mass_centre'][0]:.2f}, {m['mass_centre'][1]:.2f}), {m['mass_offset']:.2f} from (0.50, 0.47)")
    print("zones       " + " | ".join(" ".join(f"{v:.2f}" for v in row) for row in m["zones"]))
    for a, hx, b, c in m["parts"][:4]:
        print(f"part        {a:.0%} {hx} box {b} centre {c}")
    print("brand score  " + "  ".join(f"{k} {v:.1f}" for k, v in m["score"].items()))
    print(f"total       {m['total']:.1f}")


def sheet(ms, out):
    """One row per file: the icon at 256/64/32/16, its silhouette with the mass centre, the nine
    zones as a heat grid, the palette and the score."""
    sys.path.insert(0, HERE)
    import board as B
    from PIL import Image, ImageDraw
    rh, W = 300, 1300
    im = Image.new("RGB", (W, 40 + rh * len(ms)), B.BG)
    dr = ImageDraw.Draw(im)
    dr.text((20, 8), "measure: original icon, silhouette + mass centre, nine zones, palette, brand score", font=B.font(18, True), fill=B.INK)
    for i, m in enumerate(ms):
        y = 40 + i * rh
        x = 20
        for sz in (256, 64, 32, 16):
            ic = B.raster(m["file"], sz, sz)
            im.paste(ic, (x, y + 256 - sz), ic)
            x += sz + 16
        r = R.read(m["file"], 256)
        sil = Image.fromarray(np.where(r["mask"], 40, 250).astype("uint8")).convert("RGB")
        sd = ImageDraw.Draw(sil)
        yy, xx = np.nonzero(r["mask"])           # the zones grid is on the drawn area (score._zones)
        bx0, bx1, by0, by1 = xx.min(), xx.max() + 1, yy.min(), yy.max() + 1
        sd.rectangle((bx0, by0, bx1 - 1, by1 - 1), outline=(200, 120, 160))
        for k in (1, 2):
            gx, gy = bx0 + k * (bx1 - bx0) / 3, by0 + k * (by1 - by0) / 3
            sd.line((gx, by0, gx, by1), fill=(200, 120, 160))
            sd.line((bx0, gy, bx1, gy), fill=(200, 120, 160))
        cx, cy = m["mass_centre"][0] * 256, m["mass_centre"][1] * 256
        sd.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(240, 180, 30), outline=(255, 255, 255))
        sd.ellipse((128 - 4, 0.47 * 256 - 4, 128 + 4, 0.47 * 256 + 4), outline=(80, 200, 120), width=2)
        im.paste(sil, (x, y))
        x += 272
        z = np.array(m["zones"])
        for a in range(3):
            for b in range(3):
                v = min(1.0, z[a][b] * 3)
                col = (int(250 - 150 * v), int(250 - 190 * v), int(250 - 40 * v))
                dr.rectangle((x + b * 50, y + a * 50, x + b * 50 + 48, y + a * 50 + 48), fill=col)
                dr.text((x + b * 50 + 8, y + a * 50 + 16), f"{z[a][b]:.2f}", font=B.font(13), fill=B.INK)
        for j, (a, hx, el) in enumerate(m["palette"][:6]):
            rgb = tuple(int(hx[k:k + 2], 16) for k in (1, 3, 5))
            dr.rectangle((x + 160, y + j * 26, x + 184, y + j * 26 + 22), fill=rgb, outline=B.LINE)
            dr.text((x + 190, y + j * 26 + 3), f"{hx} {el} {a:.0%}", font=B.font(13), fill=B.INK)
        ty = y + 160
        dr.text((x, ty), os.path.basename(m["file"]), font=B.font(14, True), fill=B.INK)
        for j, (k, v) in enumerate(m["score"].items()):
            dr.text((x + (j % 4) * 92, ty + 22 + (j // 4) * 20), f"{k} {v:.0f}", font=B.font(13), fill=B.DIM)
        dr.text((x, ty + 70), f"total {m['total']:.1f}   box {m['box_fen']}  fill {m['fill']}", font=B.font(14, True), fill=B.INK)
    im.save(out)


# ---------------------------------------------------------------- keeping the base (lead 07:57Z)
# The redraw keeps the original's own geometry: its shapes are read (SVG) or traced (raster
# silhouette), fitted into the A2 glyph box, and only then restyled. Nothing is eyeballed.
import re  # noqa: E402

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def _affine(t):
    """SVG transform list -> 2x3 matrix (a b c d e f)."""
    M = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", t or ""):
        v = [float(x) for x in re.findall(_NUM, args)]
        if name == "translate":
            m = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            m = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        elif name == "matrix":
            m = tuple(v)
        elif name == "rotate":
            a = np.radians(v[0]); c, s_ = np.cos(a), np.sin(a)
            cx, cy = (v[1], v[2]) if len(v) > 2 else (0, 0)
            m = (c, s_, -s_, c, cx - c * cx + s_ * cy, cy - s_ * cx - c * cy)
        else:
            continue
        M = _mul(M, m)
    return M


def _mul(A, B):
    a, b, c, d, e, f_ = A
    a2, b2, c2, d2, e2, f2 = B
    return (a * a2 + c * b2, b * a2 + d * b2, a * c2 + c * d2, b * c2 + d * d2, a * e2 + c * f2 + e, b * e2 + d * f2 + f_)


def _ap(M, x, y):
    return (M[0] * x + M[2] * y + M[4], M[1] * x + M[3] * y + M[5])


def parse_d(d):
    """Path data -> list of subpaths, each a list of segments ('M', p) ('L', p) ('C', p1, p2, p)
    in absolute coordinates (quadratics raised to cubics; arcs are not supported)."""
    toks = re.findall(r"[MmLlHhVvCcSsQqTtZzAa]|" + _NUM, d)
    i, cmd, cur, start, out, sub, last_c = 0, None, (0.0, 0.0), (0.0, 0.0), [], None, None

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v
    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
            if cmd in "Zz":
                if sub:
                    sub.append(("Z",)); out.append(sub); sub = None
                cur = start
                continue
        rel = cmd.islower()
        C = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if C == "M":
            p = (ox + num(), oy + num())
            if sub:
                out.append(sub)
            sub = [("M", p)]; cur = start = p
            cmd = "l" if rel else "L"
            last_c = None
        elif C == "L":
            p = (ox + num(), oy + num()); sub.append(("L", p)); cur = p; last_c = None
        elif C == "H":
            p = ((ox if rel else 0) + num(), cur[1]); sub.append(("L", p)); cur = p; last_c = None
        elif C == "V":
            p = (cur[0], (oy if rel else 0) + num()); sub.append(("L", p)); cur = p; last_c = None
        elif C == "C":
            p1 = (ox + num(), oy + num()); p2 = (ox + num(), oy + num()); p = (ox + num(), oy + num())
            sub.append(("C", p1, p2, p)); cur = p; last_c = p2
        elif C == "S":
            p1 = (2 * cur[0] - last_c[0], 2 * cur[1] - last_c[1]) if last_c else cur
            p2 = (ox + num(), oy + num()); p = (ox + num(), oy + num())
            sub.append(("C", p1, p2, p)); cur = p; last_c = p2
        elif C == "Q":
            q = (ox + num(), oy + num()); p = (ox + num(), oy + num())
            p1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            p2 = (p[0] + 2 / 3 * (q[0] - p[0]), p[1] + 2 / 3 * (q[1] - p[1]))
            sub.append(("C", p1, p2, p)); cur = p; last_c = None
        else:
            raise ValueError(f"path command {cmd} not supported")
    if sub:
        out.append(sub)
    return out


def _ellipse_d(cx, cy, rx, ry):
    k = 0.5522847
    return (f"M{cx + rx} {cy}C{cx + rx} {cy + k * ry} {cx + k * rx} {cy + ry} {cx} {cy + ry}"
            f"C{cx - k * rx} {cy + ry} {cx - rx} {cy + k * ry} {cx - rx} {cy}"
            f"C{cx - rx} {cy - k * ry} {cx - k * rx} {cy - ry} {cx} {cy - ry}"
            f"C{cx + k * rx} {cy - ry} {cx + rx} {cy - k * ry} {cx + rx} {cy}Z")


def svg_shapes(path):
    """The drawable shapes of a flat SVG (path, ellipse, circle, rect in nested <g> transforms),
    in document order: [{"fill": "#rrggbb", "sub": parse_d segments in canvas px}], plus the
    viewBox. Enough for upstream logos drawn as filled shapes (no strokes, no gradients)."""
    src = open(path, encoding="utf-8").read()
    vb = [float(v) for v in re.findall(_NUM, re.search(r'viewBox="([^"]*)"', src).group(1))]
    stack, shapes = [(1, 0, 0, 1, 0, 0)], []
    for m in re.finditer(r"<(/?)(g|path|ellipse|circle|rect)\b([^>]*?)(/?)>", src, re.S):
        close, tag, attrs, selfc = m.groups()
        if tag == "g":
            if close:
                stack.pop()
            elif not selfc:
                stack.append(_mul(stack[-1], _affine(_attr(attrs, "transform"))))
            continue
        if close:
            continue
        M = _mul(stack[-1], _affine(_attr(attrs, "transform")))
        style = _attr(attrs, "style") or ""
        fill = _attr(attrs, "fill") or (re.search(r"fill:\s*(#[0-9a-fA-F]{3,6}|none)", style) or [None, "#000000"])[1]
        if fill == "none" or "display:none" in style:
            continue
        if tag == "path":
            d = _attr(attrs, "d")
        elif tag in ("ellipse", "circle"):
            g_ = lambda k, dflt=0.0: float(_attr(attrs, k) or dflt)  # noqa: E731
            rx = g_("rx", g_("r")); ry = g_("ry", g_("r"))
            d = _ellipse_d(g_("cx"), g_("cy"), rx, ry)
        else:
            x, y, w, h = (float(_attr(attrs, k) or 0) for k in ("x", "y", "width", "height"))
            d = f"M{x} {y}L{x + w} {y}L{x + w} {y + h}L{x} {y + h}Z"
        subs = [[(seg[0],) + tuple(_ap(M, *p) for p in seg[1:]) for seg in sp] for sp in parse_d(d)]
        shapes.append({"fill": fill.upper(), "sub": subs})
    return shapes, vb


def _attr(attrs, k):
    m = re.search(r'(?<![\w:-])' + k + r'="([^"]*)"', attrs)
    return m.group(1) if m else None


def shapes_box(shapes):
    pts = [p for s in shapes for sp in s["sub"] for seg in sp for p in seg[1:]]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def fit(box, target):
    """Uniform scale + translate that puts `box` (x0 y0 x1 y1) centred into `target` (cx, cy, size):
    the longer side becomes `size`, so the original's own proportions are kept."""
    x0, y0, x1, y1 = box
    cx, cy, size = target
    k = size / max(x1 - x0, y1 - y0)
    return (k, 0, 0, k, cx - k * (x0 + x1) / 2, cy - k * (y0 + y1) / 2)


def to_d(subs, M, X):
    """Segments -> path data, through the matrix M (into fen) and X (fen -> canvas px)."""
    out = []
    for sp in subs:
        for seg in sp:
            if seg[0] == "Z":
                out.append("Z")
                continue
            pts = [_ap(M, *p) for p in seg[1:]]
            out.append(seg[0] + " ".join(f"{X(x):.2f} {X(y):.2f}" for x, y in pts))
    return "".join(out)


def trace(mask, eps=0.6):
    """Outer contour of the largest component of a boolean mask (Moore neighbour tracing),
    simplified by Douglas-Peucker within eps pixels. Returns [(x, y)] in pixels."""
    from scipy import ndimage as nd
    lab, n = nd.label(mask)
    if n == 0:
        return []
    big = 1 + int(np.argmax(nd.sum(np.ones_like(lab), lab, range(1, n + 1))))
    m = nd.binary_fill_holes(lab == big)
    m = np.pad(m, 1)
    ys, xs = np.nonzero(m)
    i0 = np.lexsort((xs, ys))[0]
    start = (int(xs[i0]), int(ys[i0]))
    nb = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    cur, d, pts = start, 6, [start]
    for _ in range(4 * m.size):
        for k in range(8):
            dd = (d + 6 + k) % 8          # start searching from the back-left of the last move
            nx, ny = cur[0] + nb[dd][0], cur[1] + nb[dd][1]
            if m[ny, nx]:
                cur, d = (nx, ny), dd
                break
        if cur == start:
            break
        pts.append(cur)
    pts = [(x - 1, y - 1) for x, y in pts]
    return _dp(pts, eps)


def _dp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0], float), np.array(pts[-1], float)
    P_ = np.array(pts, float)
    ab = b - a
    n = np.hypot(*ab)
    dist = np.abs(np.cross(ab, P_ - a)) / n if n > 0 else np.hypot(*(P_ - a).T)
    i = int(np.argmax(dist))
    if dist[i] > eps:
        return _dp(pts[:i + 1], eps)[:-1] + _dp(pts[i:], eps)
    return [pts[0], pts[-1]]


def main(argv):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--kind", default="icon")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--sheet")
    a = ap.parse_args(argv)
    ms = [measure(f, a.kind) for f in a.files]
    if a.json:
        print(json.dumps(ms, default=str))
    else:
        for m in ms:
            show(m)
    if a.sheet:
        sheet(ms, a.sheet)


if __name__ == "__main__":
    main(sys.argv[1:])
